#!/usr/bin/env python
"""
LEGION (https://govanguard.com)
Copyright (c) 2020 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
    version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
    details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <http://www.gnu.org/licenses/>.

"""

import signal  # for file operations, to kill processes, for regex, for subprocesses
import subprocess

from app.ApplicationInfo import applicationInfo
from app.Screenshooter import Screenshooter
from app.actions.updateProgress.UpdateProgressObservable import UpdateProgressObservable
from app.importers.NmapImporter import NmapImporter
from app.importers.PythonImporter import PythonImporter
from app.tools.nmap.NmapPaths import getNmapRunningFolder
from ui.observers.QtUpdateProgressObserver import QtUpdateProgressObserver

try:
    import queue
except:
    import Queue as queue
from app.logic import *
from app.settings import *

log = getAppLogger()

class Controller:

    # initialisations that will happen once - when the program is launched
    @timing
    def __init__(self, view, logic):
        self.logic = logic
        self.view = view
        self.view.setController(self)
        self.view.startOnce()
        self.view.startConnections()

        self.loadSettings()  # creation of context menu actions from settings file and set up of various settings
        updateProgressObservable = UpdateProgressObservable()
        updateProgressObserver = QtUpdateProgressObserver(self.view.importProgressWidget)
        updateProgressObservable.attach(updateProgressObserver)

        self.initNmapImporter(updateProgressObservable)
        self.initPythonImporter()
        self.initScreenshooter()
        self.initBrowserOpener()
        self.start()                                                    # initialisations (globals, etc)
        self.initTimers()
        self.processTimers = {}
        self.processMeasurements = {}

    # initialisations that will happen everytime we create/open a project - can happen several times in the
    # program's lifetime
    def start(self, title='*untitled'):
        self.processes = []                    # to store all the processes we run (nmaps, niktos, etc)
        self.fastProcessQueue = queue.Queue()  # to manage fast processes (banner, snmpenum, etc)
        self.fastProcessesRunning = 0          # counts the number of fast processes currently running
        self.slowProcessesRunning = 0          # counts the number of slow processes currently running
        activeProject = self.logic.activeProject
        self.nmapImporter.setDB(activeProject.database)  # tell nmap importer which db to use
        self.nmapImporter.setHostRepository(activeProject.repositoryContainer.hostRepository)
        self.pythonImporter.setDB(activeProject.database)
        self.updateOutputFolder()                                       # tell screenshooter where the output folder is
        self.view.start(title)

    def initNmapImporter(self, updateProgressObservable: UpdateProgressObservable):
        self.nmapImporter = NmapImporter(updateProgressObservable,
                                         self.logic.activeProject.repositoryContainer.hostRepository)
        self.nmapImporter.done.connect(self.importFinished)
        self.nmapImporter.schedule.connect(self.scheduler)              # run automated attacks
        self.nmapImporter.log.connect(self.view.ui.LogOutputTextView.append)

    def initPythonImporter(self):
        self.pythonImporter = PythonImporter()
        self.pythonImporter.done.connect(self.importFinished)
        self.pythonImporter.schedule.connect(self.scheduler)              # run automated attacks
        self.pythonImporter.log.connect(self.view.ui.LogOutputTextView.append)

    def initScreenshooter(self):
        # screenshot taker object (different thread)
        self.screenshooter = Screenshooter(self.settings.general_screenshooter_timeout)
        self.screenshooter.done.connect(self.screenshotFinished)
        self.screenshooter.log.connect(self.view.ui.LogOutputTextView.append)

    def initBrowserOpener(self):
        self.browser = BrowserOpener()                                  # browser opener object (different thread)
        self.browser.log.connect(self.view.ui.LogOutputTextView.append)

    # these timers are used to prevent from updating the UI several times within a short time period -
    # which freezes the UI
    def initTimers(self):
        self.updateUITimer = QTimer()
        self.updateUITimer.setSingleShot(True)
        self.updateUITimer.timeout.connect(self.view.updateProcessesTableView)
        self.updateUITimer.timeout.connect(self.view.updateToolsTableView)

        self.updateUI2Timer = QTimer()
        self.updateUI2Timer.setSingleShot(True)
        self.updateUI2Timer.timeout.connect(self.view.updateInterface)

        self.processTableUiUpdateTimer = QTimer()
        self.processTableUiUpdateTimer.timeout.connect(self.view.updateProcessesTableView)
        # Update only when queue > 0
        self.processTableUiUpdateTimer.start(1000) # Faster than this doesn't make anything smoother

    # this function fetches all the settings from the conf file. Among other things it populates the actions lists
    # that will be used in the context menus.
    def loadSettings(self):
        self.settingsFile = AppSettings()
        # load settings from conf file (create conf file first if necessary)
        self.settings = Settings(self.settingsFile)
        # save the original state so that we can know if something has changed when we exit LEGION
        self.originalSettings = Settings(self.settingsFile)
        self.logic.projectManager.setStoreWordListsOnExit(self.logic.activeProject,
            self.settings.brute_store_cleartext_passwords_on_exit == 'True')
        self.view.settingsWidget.setSettings(Settings(self.settingsFile))

    # call this function when clicking 'apply' in the settings menu (after validation)
    def applySettings(self, newSettings):
        self.settings = newSettings

    def cancelSettings(self):  # called when the user presses cancel in the Settings dialog
        # resets the dialog's settings to the current application settings to forget any changes made by the user
        self.view.settingsWidget.setSettings(self.settings)

    @timing
    def saveSettings(self, saveBackup = True):
        if not self.settings == self.originalSettings:
            log.info('Settings have been changed.')
            self.settingsFile.backupAndSave(self.settings, saveBackup)
        else:
            log.info('Settings have NOT been changed.')

    def getSettings(self):
        return self.settings

    #################### AUXILIARY ####################

    def getCWD(self):
        return self.logic.activeProject.properties.workingDirectory

    def getProjectName(self):
        return self.logic.activeProject.properties.projectName

    def getRunningFolder(self):
        return self.logic.activeProject.properties.runningFolder

    def getOutputFolder(self):
        return self.logic.activeProject.properties.outputFolder

    def getUserlistPath(self):
        return self.logic.activeProject.properties.usernamesWordList.filename

    def getPasslistPath(self):
        return self.logic.activeProject.properties.passwordWordList.filename

    def updateOutputFolder(self):
        self.screenshooter.updateOutputFolder(
            self.logic.activeProject.properties.outputFolder + '/screenshots')  # update screenshot folder

    def copyNmapXMLToOutputFolder(self, filename):
        self.logic.copyNmapXMLToOutputFolder(filename)

    def isTempProject(self):
        return self.logic.activeProject.properties.isTemporary

    def getDB(self):
        return self.logic.activeProject.database

    def getRunningProcesses(self):
        return self.processes

    def getHostActions(self):
        return self.settings.hostActions

    def getPortActions(self):
        return self.settings.portActions

    def getPortTerminalActions(self):
        return self.settings.portTerminalActions

    #################### ACTIONS ####################

    def createNewProject(self):
        self.view.closeProject()  # removes temp folder (if any)
        self.logic.createNewTemporaryProject()
        self.start()  # initialisations (globals, etc)

    def openExistingProject(self, filename, projectType='legion'):
        self.view.closeProject()
        self.view.importProgressWidget.reset('Opening project..')
        self.view.importProgressWidget.show()                           # show the progress widget
        self.logic.openExistingProject(filename, projectType)
        # initialisations (globals, signals, etc)
        self.start(ntpath.basename(self.logic.activeProject.properties.projectName))
        self.view.restoreToolTabs()                                     # restores the tool tabs for each host
        self.view.hostTableClick()                                 # click on first host to restore his host tool tabs
        self.view.importProgressWidget.hide()                           # hide the progress widget

    def saveProject(self, lastHostIdClicked, notes):
        if not lastHostIdClicked == '':
            self.logic.activeProject.repositoryContainer.noteRepository.storeNotes(lastHostIdClicked, notes)

    def saveProjectAs(self, filename, replace=0):
        success = self.logic.saveProjectAs(filename, replace)
        if success:
            self.nmapImporter.setDB(self.logic.activeProject.database)   # tell nmap importer which db to use
        return success

    def closeProject(self):
        self.saveSettings()                                             # backup and save config file, if necessary
        self.screenshooter.terminate()
        self.initScreenshooter()
        self.logic.activeProject.repositoryContainer.processRepository.toggleProcessDisplayStatus(True)
        self.view.updateProcessesTableView()                            # clear process table
        self.logic.projectManager.closeProject(self.logic.activeProject)

    @timing
    def addHosts(self, targetHosts, runHostDiscovery, runStagedNmap, nmapSpeed, scanMode, nmapOptions = []):
        if targetHosts == '':
            log.info('No hosts entered..')
            return

        runningFolder = self.logic.activeProject.properties.runningFolder
        if scanMode == 'Easy':
            if runStagedNmap:
                self.runStagedNmap(targetHosts, runHostDiscovery)
            elif runHostDiscovery:
                outputfile = getNmapRunningFolder(runningFolder) + "/" + getTimestamp() + '-host-discover'
                command = f"nmap -n -sV -O --version-light -T{str(nmapSpeed)} {targetHosts} -oA {outputfile}"
                log.info("Running {command}".format(command=command))
                self.runCommand('nmap', 'nmap (discovery)', targetHosts, '', '', command, getTimestamp(True),
                                outputfile, self.view.createNewTabForHost(str(targetHosts), 'nmap (discovery)', True))
            else:
                outputfile = getNmapRunningFolder(runningFolder) + "/" + getTimestamp() + '-nmap-list'
                command = "nmap -n -sL -T" + str(nmapSpeed) + " " + targetHosts + " -oA " + outputfile
                self.runCommand('nmap', 'nmap (list)', targetHosts, '', '', command, getTimestamp(True),
                                outputfile,
                                self.view.createNewTabForHost(str(targetHosts), 'nmap (list)', True))
        elif scanMode == 'Hard':
            outputfile = getNmapRunningFolder(runningFolder) + "/" + getTimestamp() + '-nmap-custom'
            nmapOptionsString = ' '.join(nmapOptions)
            nmapOptionsString = nmapOptionsString + " -T" + str(nmapSpeed)
            command = "nmap " + nmapOptionsString + " " + targetHosts + " -oA " + outputfile
            self.runCommand('nmap', 'nmap (custom ' + nmapOptionsString + ')', targetHosts, '', '', command,
                            getTimestamp(True), outputfile,
                            self.view.createNewTabForHost(
                                str(targetHosts), 'nmap (custom ' + nmapOptionsString + ')',
                                                          True))

    #################### CONTEXT MENUS ####################

    # showAll exists because in some cases we only want to show host tools excluding portscans and 'mark as checked'
    @timing
    def getContextMenuForHost(self, isChecked, showAll=True):
        menu = QMenu()
        self.nmapSubMenu = QMenu('Portscan')
        actions = []

        for a in self.settings.hostActions:
            if "nmap" in a[1] or "unicornscan" in a[1]:
                actions.append(self.nmapSubMenu.addAction(a[0]))
            else:
                actions.append(menu.addAction(a[0]))

        if showAll:
            actions.append(self.nmapSubMenu.addAction("Run nmap (staged)"))

            menu.addMenu(self.nmapSubMenu)
            menu.addSeparator()

            if isChecked == 'True':
                menu.addAction('Mark as unchecked')
            else:
                menu.addAction('Mark as checked')
            menu.addAction('Rescan')
            menu.addAction('Purge Results')
            menu.addAction('Delete')

        return menu, actions

    @timing
    def handleHostAction(self, ip, hostid, actions, action):
        repositoryContainer = self.logic.activeProject.repositoryContainer

        if action.text() == 'Mark as checked' or action.text() == 'Mark as unchecked':
            repositoryContainer.hostRepository.toggleHostCheckStatus(ip)
            self.view.updateInterface()
            return

        if action.text() == 'Run nmap (staged)':
            # if we are running nmap we need to purge previous portscan results
            log.info('Purging previous portscan data for ' + str(ip))
            if repositoryContainer.portRepository.getPortsByIPAndProtocol(ip, 'tcp'):
                repositoryContainer.portRepository.deleteAllPortsAndScriptsByHostId(hostid, 'tcp')
            if repositoryContainer.portRepository.getPortsByIPAndProtocol(ip, 'udp'):
                repositoryContainer.portRepository.deleteAllPortsAndScriptsByHostId(hostid, 'udp')
            self.view.updateInterface()
            self.runStagedNmap(ip, False)
            return

        if action.text() == 'Rescan':
            log.info('Rescanning host {0}'.format(str(ip)))
            self.runStagedNmap(ip, False)
            return

        if action.text() == 'Purge Results':
            log.info('Purging previous portscan data for host {0}'.format(str(ip)))
            if repositoryContainer.portRepository.getPortsByIPAndProtocol(ip, 'tcp'):
                repositoryContainer.portRepository.deleteAllPortsAndScriptsByHostId(hostid, 'tcp')
            if repositoryContainer.portRepository.getPortsByIPAndProtocol(ip, 'udp'):
                repositoryContainer.portRepository.deleteAllPortsAndScriptsByHostId(hostid, 'udp')
            self.view.updateInterface()
            return

        if action.text() == 'Delete':
            log.info('Purging previous portscan data for host {0}'.format(str(ip)))
            if repositoryContainer.portRepository.getPortsByIPAndProtocol(ip, 'tcp'):
                repositoryContainer.portRepository.deleteAllPortsAndScriptsByHostId(hostid, 'tcp')
            if repositoryContainer.portRepository.getPortsByIPAndProtocol(ip, 'udp'):
                repositoryContainer.portRepository.deleteAllPortsAndScriptsByHostId(hostid, 'udp')
            self.logic.activeProject.repositoryContainer.hostRepository.deleteHost(ip)
            self.view.updateInterface()
            return

        for i in range(0,len(actions)):
            if action == actions[i]:
                name = self.settings.hostActions[i][1]
                invisibleTab = False
                # to make sure different nmap scans appear under the same tool name
                if 'nmap' in name:
                    name = 'nmap'
                    invisibleTab = True
                elif 'python-script' in name:
                    invisibleTab = True
                # remove all chars that are not alphanumeric from tool name (used in the outputfile's name)
                outputfile = self.logic.activeProject.properties.runningFolder + "/" + \
                             re.sub("[^0-9a-zA-Z]", "", str(name)) + "/" + getTimestamp() + "-" + \
                             re.sub("[^0-9a-zA-Z]", "", str(self.settings.hostActions[i][1])) + "-" + ip
                command = str(self.settings.hostActions[i][2])
                command = command.replace('[IP]', ip).replace('[OUTPUT]', outputfile)

                # check if same type of nmap scan has already been made and purge results before scanning
                if 'nmap' in command:
                    proto = 'tcp'
                    if '-sU' in command:
                        proto = 'udp'
                    # if we are running nmap we need to purge previous portscan results (of the same protocol)
                    if repositoryContainer.portRepository.getPortsByIPAndProtocol(ip, proto):
                        repositoryContainer.portRepository.deleteAllPortsAndScriptsByHostId(hostid, proto)

                tabTitle = self.settings.hostActions[i][1]
                self.runCommand(name, tabTitle, ip, '', '', command, getTimestamp(True), outputfile,
                                self.view.createNewTabForHost(ip, tabTitle, invisibleTab))
                break

    @timing
    def getContextMenuForServiceName(self, serviceName='*', menu=None):
        if menu == None:  # if no menu was given, create a new one
            menu = QMenu()

        if serviceName == '*' or serviceName in self.settings.general_web_services.split(","):
            menu.addAction("Open in browser")
            menu.addAction("Take screenshot")

        actions = []
        for a in self.settings.portActions:
            # if the service name exists in the portActions list show the command in the context menu
            if serviceName is None or serviceName == '*' or serviceName in a[3].split(",") or a[3] == '':
                # in actions list write the service and line number that corresponds to it in portActions
                actions.append([self.settings.portActions.index(a), menu.addAction(a[0])])

        # if the user pressed SHIFT+Right-click show full menu
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            shiftPressed = True
        else:
            shiftPressed = False

        return menu, actions, shiftPressed

    @timing
    def handleServiceNameAction(self, targets, actions, action, restoring=True):

        if action.text() == 'Take screenshot':
            for ip in targets:
                url = ip[0] + ':' + ip[1]
                self.screenshooter.addToQueue(url)
            self.screenshooter.start()
            return

        elif action.text() == 'Open in browser':
            for ip in targets:
                url = ip[0]+':'+ip[1]
                self.browser.addToQueue(url)
            self.browser.start()
            return

        for i in range(0,len(actions)):
            if action == actions[i][1]:
                srvc_num = actions[i][0]
                for ip in targets:
                    tool = self.settings.portActions[srvc_num][1]
                    tabTitle = self.settings.portActions[srvc_num][1]+" ("+ip[1]+"/"+ip[2]+")"
                    outputfile = self.logic.activeProject.properties.runningFolder + "/" + \
                                 re.sub("[^0-9a-zA-Z]", "", str(tool)) + \
                                 "/" + getTimestamp() + '-' + tool + "-" + ip[0] + "-" + ip[1]

                    command = str(self.settings.portActions[srvc_num][2])
                    command = command.replace('[IP]', ip[0]).replace('[PORT]', ip[1]).replace('[OUTPUT]', outputfile)

                    if 'nmap' in command and ip[2] == 'udp':
                        command = command.replace("-sV", "-sVU")

                    if 'nmap' in tabTitle:                              # we don't want to show nmap tabs
                        restoring = True
                    elif 'python-script' in tabTitle:                              # we don't want to show nmap tabs
                        restoring = True

                    self.runCommand(tool, tabTitle, ip[0], ip[1], ip[2], command, getTimestamp(True), outputfile,
                                    self.view.createNewTabForHost(ip[0], tabTitle, restoring))
                break

    @timing
    def getContextMenuForPort(self, serviceName='*'):

        menu = QMenu()

        modifiers = QtWidgets.QApplication.keyboardModifiers()  # if the user pressed SHIFT+Right-click show full menu
        if modifiers == QtCore.Qt.ShiftModifier:
            serviceName='*'

        terminalActions = []  # custom terminal actions from settings file
        # if wildcard or the command is valid for this specific service or if the command is valid for all services
        for a in self.settings.portTerminalActions:
            if serviceName is None or serviceName == '*' or serviceName in a[3].split(",") or a[3] == '':
                terminalActions.append([self.settings.portTerminalActions.index(a), menu.addAction(a[0])])

        menu.addSeparator()
        menu.addAction("Send to Brute")
        menu.addSeparator()  # dummy is there because we don't need the third return value
        menu, actions, dummy = self.getContextMenuForServiceName(serviceName, menu)
        menu.addSeparator()
        menu.addAction("Run custom command")

        return menu, actions, terminalActions

    @timing
    def handlePortAction(self, targets, *args):
        actions = args[0]
        terminalActions = args[1]
        action = args[2]
        restoring = args[3]

        if action.text() == 'Send to Brute':
            for ip in targets:
                # ip[0] is the IP, ip[1] is the port number and ip[3] is the service name
                self.view.createNewBruteTab(ip[0], ip[1], ip[3])
            return

        if action.text() == 'Run custom command':
            log.info('custom command')
            return

        terminal = self.settings.general_default_terminal               # handle terminal actions
        for i in range(0,len(terminalActions)):
            if action == terminalActions[i][1]:
                srvc_num = terminalActions[i][0]
                for ip in targets:
                    command = str(self.settings.portTerminalActions[srvc_num][2])
                    command = command.replace('[IP]', ip[0]).replace('[PORT]', ip[1])
                    subprocess.Popen(terminal+" -e 'bash -c \""+command+"; exec bash\"'", shell=True)
                return

        self.handleServiceNameAction(targets, actions, action, restoring)

    def getContextMenuForProcess(self):
        menu = QMenu()
        menu.addAction("Kill")
        menu.addAction("Clear")
        return menu

    # selectedProcesses is a list of tuples (pid, status, procId)
    def handleProcessAction(self, selectedProcesses, action):
        if action.text() == 'Kill':
            if self.view.killProcessConfirmation():
                for p in selectedProcesses:
                    if p[1] != "Running":
                        if p[1] == "Waiting":
                            if str(self.logic.activeProject.repositoryContainer.processRepository.getStatusByProcessId(
                                    p[2])) == 'Running':
                                self.killProcess(self.view.ProcessesTableModel.getProcessPidForId(p[2]), p[2])
                            self.logic.activeProject.repositoryContainer.processRepository.storeProcessCancelStatus(
                                str(p[2]))
                        else:
                            log.info("This process has already been terminated. Skipping.")
                    else:
                        self.killProcess(p[0], p[2])
                self.view.updateProcessesTableView()
            return

        if action.text() == 'Clear':  # hide all the processes that are not running
            self.logic.activeProject.repositoryContainer.processRepository.toggleProcessDisplayStatus()
            self.view.updateProcessesTableView()

    #################### LEFT PANEL INTERFACE UPDATE FUNCTIONS ####################

    def isHostInDB(self, host):
        return self.logic.activeProject.repositoryContainer.hostRepository.exists(host)

    def getHostsFromDB(self, filters):
        return self.logic.activeProject.repositoryContainer.hostRepository.getHosts(filters)

    def getServiceNamesFromDB(self, filters):
        return self.logic.activeProject.repositoryContainer.serviceRepository.getServiceNames(filters)

    def getProcessStatusForDBId(self, dbId):
        return self.logic.activeProject.repositoryContainer.processRepository.getStatusByProcessId(dbId)

    def getPidForProcess(self, dbId):
        return self.logic.activeProject.repositoryContainer.processRepository.getPIDByProcessId(dbId)

    def storeCloseTabStatusInDB(self, pid):
        return self.logic.activeProject.repositoryContainer.processRepository.storeCloseStatus(pid)

    def getServiceNameForHostAndPort(self, hostIP, port):
        return self.logic.activeProject.repositoryContainer.serviceRepository.getServiceNamesByHostIPAndPort(hostIP,
                                                                                                             port)

    #################### RIGHT PANEL INTERFACE UPDATE FUNCTIONS ####################

    def getPortsAndServicesForHostFromDB(self, hostIP, filters):
        return self.logic.activeProject.repositoryContainer.portRepository.getPortsAndServicesByHostIP(hostIP, filters)

    def getHostsAndPortsForServiceFromDB(self, serviceName, filters):
        return self.logic.activeProject.repositoryContainer.hostRepository.getHostsAndPortsByServiceName(serviceName,
                                                                                                         filters)

    def getHostInformation(self, hostIP):
        return self.logic.activeProject.repositoryContainer.hostRepository.getHostInformation(hostIP)

    def getPortStatesForHost(self, hostid):
        return self.logic.activeProject.repositoryContainer.portRepository.getPortStatesByHostId(hostid)

    def getScriptsFromDB(self, hostIP):
        return self.logic.activeProject.repositoryContainer.scriptRepository.getScriptsByHostIP(hostIP)

    def getCvesFromDB(self, hostIP):
        return self.logic.activeProject.repositoryContainer.cveRepository.getCVEsByHostIP(hostIP)

    def getScriptOutputFromDB(self, scriptDBId):
        return self.logic.activeProject.repositoryContainer.scriptRepository.getScriptOutputById(scriptDBId)

    def getNoteFromDB(self, hostid):
        return self.logic.activeProject.repositoryContainer.noteRepository.getNoteByHostId(hostid)

    def getHostsForTool(self, toolName, closed='False'):
        return self.logic.activeProject.repositoryContainer.processRepository.getHostsByToolName(toolName, closed)

    #################### BOTTOM PANEL INTERFACE UPDATE FUNCTIONS ####################

    def getProcessesFromDB(self, filters, showProcesses='noNmap', sort='desc', ncol='id'):
        return self.logic.activeProject.repositoryContainer.processRepository.getProcesses(filters, showProcesses, sort,
                                                                                           ncol)

    #################### PROCESSES ####################

    def checkProcessQueue(self):
        log.debug('# MAX PROCESSES: ' + str(self.settings.general_max_fast_processes))
        log.debug('# Fast processes running: ' + str(self.fastProcessesRunning))
        log.debug('# Fast processes queued: ' + str(self.fastProcessQueue.qsize()))

        if not self.fastProcessQueue.empty():
            self.processTableUiUpdateTimer.start(1000)
            if (self.fastProcessesRunning <= int(self.settings.general_max_fast_processes)):
                next_proc = self.fastProcessQueue.get()
                if not self.logic.activeProject.repositoryContainer.processRepository.isCancelledProcess(
                        str(next_proc.id)):
                    log.debug('Running: ' + str(next_proc.command))
                    next_proc.display.clear()
                    self.processes.append(next_proc)
                    self.fastProcessesRunning += 1
                    # Add Timeout
                    next_proc.waitForFinished(10)
                    next_proc.start(next_proc.command)
                    self.logic.activeProject.repositoryContainer.processRepository.storeProcessRunningStatus(
                        next_proc.id, next_proc.pid())
                elif not self.fastProcessQueue.empty():
                    log.debug('> next process was canceled, checking queue again..')
                    self.checkProcessQueue()
        #else:
        #    log.info("Halting process panel update timer as all processes are finished.")
        #    self.processTableUiUpdateTimer.stop()

    def cancelProcess(self, dbId):
        log.info('Canceling process: ' + str(dbId))
        self.logic.activeProject.repositoryContainer.processRepository.storeProcessCancelStatus(
            str(dbId))  # mark it as cancelled
        self.updateUITimer.stop()
        self.updateUITimer.start(1500)                                  # update the interface soon

    def killProcess(self, pid, dbId):
        log.info('Killing process: ' + str(pid))
        self.logic.activeProject.repositoryContainer.processRepository.storeProcessKillStatus(str(dbId))
        try:
            os.kill(int(pid), signal.SIGTERM)
        except OSError:
            log.info('This process has already been terminated.')
        except:
            log.info("Unexpected error:", sys.exc_info()[0])

    def killRunningProcesses(self):
        log.info('Killing running processes!')
        for p in self.processes:
            p.finished.disconnect()                 # experimental
            self.killProcess(int(p.pid()), p.id)

    # this function creates a new process, runs the command and takes care of displaying the ouput. returns the PID
    # the last 3 parameters are only used when the command is a staged nmap
    def runCommand(self, *args, discovery=True, stage=0, stop=False):
        def handleProcStop(*vargs):
            updateElapsed.stop()
            self.processTimers[qProcess.id] = None
            procTime = timer.elapsed() / 1000
            qProcess.elapsed = procTime
            self.logic.activeProject.repositoryContainer.processRepository.storeProcessRunningElapsedTime(qProcess.id,
                                                                                                          procTime)

        def handleProcUpdate(*vargs):
            procTime = timer.elapsed() / 1000
            self.processMeasurements[qProcess.pid()] = procTime

        name = args[0]
        tabTitle = args[1]
        hostIp = args[2]
        port = args[3]
        protocol = args[4]
        command = args[5]
        startTime = args[6]
        outputfile = args[7]
        textbox = args[8]
        timer = QtCore.QTime()
        updateElapsed = QTimer()

        self.logic.createFolderForTool(name)
        qProcess = MyQProcess(name, tabTitle, hostIp, port, protocol, command, startTime, outputfile, textbox)
        qProcess.started.connect(timer.start)
        qProcess.finished.connect(handleProcStop)
        updateElapsed.timeout.connect(handleProcUpdate)

        processRepository = self.logic.activeProject.repositoryContainer.processRepository
        textbox.setProperty('dbId', str(processRepository.storeProcess(qProcess)))
        updateElapsed.start(1000)
        self.processTimers[qProcess.id] = updateElapsed
        self.processMeasurements[qProcess.pid()] = 0

        log.info('Queuing: ' + str(command))
        self.fastProcessQueue.put(qProcess)

        self.checkProcessQueue()

        # update the processes table
        self.updateUITimer.stop()
        # while the process is running, when there's output to read, display it in the GUI
        self.updateUITimer.start(900)

        qProcess.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        qProcess.readyReadStandardOutput.connect(lambda: qProcess.display.appendPlainText(
            str(qProcess.readAllStandardOutput().data().decode('ISO-8859-1'))))

        qProcess.sigHydra.connect(self.handleHydraFindings)
        qProcess.finished.connect(lambda: self.processFinished(qProcess))
        qProcess.error.connect(lambda: self.processCrashed(qProcess))
        log.info("runCommand called for stage {0}".format(str(stage)))

        if stage > 0 and stage < 6:  # if this is a staged nmap, launch the next stage
            log.info("runCommand connected for stage {0}".format(str(stage)))
            nextStage = stage + 1
            qProcess.finished.connect(
                lambda: self.runStagedNmap(str(hostIp), discovery=discovery, stage=nextStage,
                                           stop=processRepository.isKilledProcess(str(qProcess.id))))

        return qProcess.pid()  # return the pid so that we can kill the process if needed

    def runPython(self):
        textbox = self.view.createNewConsole("python")
        name = 'python'
        tabTitle = name
        hostIp = '127.0.0.1'
        port = '22'
        protocol = 'tcp'
        command = 'python3 /mnt/c/Users/hackm/OneDrive/Documents/Customers/GVIT/GIT/legion/test.py'
        startTime = getTimestamp(True)
        outputfile = '/tmp/a'
        qProcess = MyQProcess(name, tabTitle, hostIp, port, protocol, command, startTime, outputfile, textbox)

        processRepository = self.logic.activeProject.repositoryContainer.processRepository
        textbox.setProperty('dbId', str(processRepository.storeProcess(qProcess)))

        log.info('Queuing: ' + str(command))
        self.fastProcessQueue.put(qProcess)

        self.checkProcessQueue()

        self.updateUI2Timer.stop()   # update the processes table
        # while the process is running, when there's output to read, display it in the GUI
        self.updateUI2Timer.start(900)
        self.updateUITimer.stop()   # update the processes table
        self.updateUITimer.start(900)

        qProcess.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        qProcess.readyReadStandardOutput.connect(lambda: qProcess.display.appendPlainText(
            str(qProcess.readAllStandardOutput().data().decode('ISO-8859-1'))))

        qProcess.sigHydra.connect(self.handleHydraFindings)
        qProcess.finished.connect(lambda: self.processFinished(qProcess))
        qProcess.error.connect(lambda: self.processCrashed(qProcess))

        return qProcess.pid()

    # recursive function used to run nmap in different stages for quick results
    def runStagedNmap(self, targetHosts, discovery = True, stage = 1, stop = False):
        log.info("runStagedNmap called for stage {0}".format(str(stage)))
        runningFolder = self.logic.activeProject.properties.runningFolder
        if not stop:
            textbox = self.view.createNewTabForHost(str(targetHosts), 'nmap (stage ' + str(stage) + ')', True)
            outputfile = getNmapRunningFolder(runningFolder) + "/" + getTimestamp() + '-nmapstage' + str(stage)

            if stage == 1:                                              # webservers/proxies
                ports = self.settings.tools_nmap_stage1_ports
            elif stage == 2:                                            # juicy stuff that we could enumerate + db
                ports = self.settings.tools_nmap_stage2_ports
            elif stage == 4:                                            # bruteforceable protocols + portmapper + nfs
                ports = self.settings.tools_nmap_stage4_ports
            elif stage == 5:                                            # first 30000 ports except ones above
                ports = self.settings.tools_nmap_stage5_ports
            else:                                                       # last 35535 ports
                ports = self.settings.tools_nmap_stage6_ports
            command = "nmap "
            if not discovery:                                           # is it with/without host discovery?
                command += "-Pn "
            command += "-T4 -sV "
            if not stage == 1 and not stage == 3:
                command += "-n "                                        # only do DNS resolution on first stage
            if os.geteuid() == 0:                                       # if we are root we can run SYN + UDP scans
                command += "-sSU "
                if stage == 2:
                    command += '-O '  # only check for OS once to save time and only if we are root otherwise it fail
            else:
                command += '-sT '

            if stage != 3:
                command += '-p ' + ports + ' ' + targetHosts + ' -oA ' + outputfile
            else:
                command = 'nmap -sV --script=./scripts/nmap/vulners.nse -vvvv ' + targetHosts + ' -oA ' + outputfile

            self.runCommand('nmap', 'nmap (stage ' + str(stage) + ')', str(targetHosts), '', '', command,
                            getTimestamp(True), outputfile, textbox, discovery=discovery, stage=stage, stop=stop)

    def importFinished(self):
        self.updateUI2Timer.stop()
        self.updateUI2Timer.start(800)
        # if nmap import was the first action, we need to hide the overlay (note: we shouldn't need to do this
        # every time. this can be improved)
        self.view.displayAddHostsOverlay(False)

    def screenshotFinished(self, ip, port, filename):
        outputFolder = self.logic.activeProject.properties.outputFolder
        dbId = self.logic.activeProject.repositoryContainer.processRepository.storeScreenshot(str(ip), str(port),
                                                                                              str(filename))
        imageviewer = self.view.createNewTabForHost(ip, 'screenshot (' + port + '/tcp)', True, '',
                                                    str(outputFolder) + '/screenshots/' + str(filename))
        imageviewer.setProperty('dbId', QVariant(str(dbId)))
        # to make sure the screenshot tab appears when it is launched from the host services tab
        self.view.switchTabClick()
        self.updateUITimer.stop()  # update the processes table
        self.updateUITimer.start(900)

    def processCrashed(self, proc):
        processRepository = self.logic.activeProject.repositoryContainer.processRepository
        processRepository.storeProcessCrashStatus(str(proc.id))
        log.info('Process {qProcessId} Crashed!'.format(qProcessId=str(proc.id)))
        qProcessOutput = "\n\t" + str(proc.display.toPlainText()).replace('\n', '').replace("b'", "")
        # self.view.closeHostToolTab(self, index))
        self.view.findFinishedServiceTab(str(processRepository.getPIDByProcessId(str(proc.id))))
        log.info('Process {qProcessId} Output: {qProcessOutput}'.format(qProcessId=str(proc.id),
                                                                        qProcessOutput=qProcessOutput))

    # this function handles everything after a process ends
    # def processFinished(self, qProcess, crashed=False):
    def processFinished(self, qProcess):
        processRepository = self.logic.activeProject.repositoryContainer.processRepository
        try:
            if not processRepository.isKilledProcess(
                    str(qProcess.id)):  # if process was not killed
                if not qProcess.outputfile == '':
                    # move tool output from runningfolder to output folder if there was an output file
                    self.logic.toolCoordinator.saveToolOutput(self.logic.activeProject.properties.outputFolder,
                                                          qProcess.outputfile)
                    print(qProcess.command)
                    if 'nmap' in qProcess.command: # if the process was nmap, use the parser to store it
                        if qProcess.exitCode() == 0:                    # if the process finished successfully
                            newoutputfile = qProcess.outputfile.replace(
                                self.logic.activeProject.properties.runningFolder,
                                self.logic.activeProject.properties.outputFolder)
                            self.nmapImporter.setFilename(str(newoutputfile) + '.xml')
                            self.nmapImporter.setOutput(str(qProcess.display.toPlainText()))
                            self.nmapImporter.start()
                    elif 'PythonScript' in qProcess.command:
                        pythonScript = str(qProcess.command).split(' ')[2]
                        print('PythonImporter running for script: {0}'.format(pythonScript))
                        if qProcess.exitCode() == 0:                    # if the process finished successfully
                            self.pythonImporter.setOutput(str(qProcess.display.toPlainText()))
                            self.pythonImporter.setHostIp(str(qProcess.hostIp))
                            self.pythonImporter.setPythonScript(pythonScript)
                            self.pythonImporter.start()
                exitCode = qProcess.exitCode()
                if exitCode != 0 and exitCode != 255:
                    log.info("Process {qProcessId} exited with code {qProcessExitCode}"
                             .format(qProcessId=qProcess.id, qProcessExitCode=qProcess.exitCode()))
                    self.processCrashed(qProcess)

                log.info("Process {qProcessId} is done!".format(qProcessId=qProcess.id))

            processRepository.storeProcessOutput(str(qProcess.id), qProcess.display.toPlainText())

            if 'hydra' in qProcess.name:  # find the corresponding widget and tell it to update its UI
                self.view.findFinishedBruteTab(str(processRepository.getPIDByProcessId(str(qProcess.id))))

            try:
                self.fastProcessesRunning =- 1
                self.checkProcessQueue()
                self.processes.remove(qProcess)
                self.updateUITimer.stop()
                self.updateUITimer.start(1000)  # update the interface soon
            except Exception as e:
                log.info("Process Finished Cleanup Exception {e}".format(e=e))
        except Exception as e:  # fixes bug when receiving finished signal when project is no longer open.
            log.info("Process Finished Exception {e}".format(e=e))
            raise

    # when hydra finds valid credentials we need to save them and change the brute tab title to red
    def handleHydraFindings(self, bWidget, userlist, passlist):
        self.view.blinkBruteTab(bWidget)
        for username in userlist:
            self.logic.activeProject.properties.usernamesWordList.add(username)
        for password in passlist:
            self.logic.activeProject.properties.passwordWordList.add(password)

    # this function parses nmap's output looking for open ports to run automated attacks on
    def scheduler(self, parser, isNmapImport):
        if isNmapImport and self.settings.general_enable_scheduler_on_import == 'False':
            return
        if self.settings.general_enable_scheduler == 'True':
            log.info('Scheduler started!')

            for h in parser.getAllHosts():
                for p in h.all_ports():
                    if p.state == 'open':
                        s = p.getService()
                        if not (s is None):
                            self.runToolsFor(s.name, h.ip, p.portId, p.protocol)

            log.info('-----------------------------------------------')
        log.info('Scheduler ended!')

    def runToolsFor(self, service, ip, port, protocol='tcp'):
        log.info('Running tools for: ' + service + ' on ' + ip + ':' + port)

        if service.endswith("?"):  # when nmap is not sure it will append a ?, so we need to remove it
            service=service[:-1]

        for tool in self.settings.automatedAttacks:
            if service in tool[1].split(",") and protocol==tool[2]:
                if tool[0] == "screenshooter":
                    url = ip+':'+port
                    self.screenshooter.addToQueue(url)
                    self.screenshooter.start()

                else:
                    for a in self.settings.portActions:
                        if tool[0] == a[1]:
                            tabTitle = a[1] + " (" + port + "/" + protocol + ")"
                            outputfile = self.logic.activeProject.properties.runningFolder + "/" + \
                                         re.sub("[^0-9a-zA-Z]", "", str(tool[0])) + \
                                         "/" + getTimestamp() + '-' + a[1] + "-" + ip + "-" + port
                            command = str(a[2])
                            command = command.replace('[IP]', ip).replace('[PORT]', port)\
                                .replace('[OUTPUT]',
                                                                                                  outputfile)
                            log.debug("Running tool command " + str(command))

                            tab = self.view.ui.HostsTabWidget.tabText(self.view.ui.HostsTabWidget.currentIndex())
                            self.runCommand(tool[0], tabTitle, ip, port, protocol, command,
                                            getTimestamp(True),
                                            outputfile,
                                            self.view.createNewTabForHost(ip, tabTitle, not (tab == 'Hosts')))
                            break
