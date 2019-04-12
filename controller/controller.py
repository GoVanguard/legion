#!/usr/bin/env python

'''
LEGION (https://govanguard.io)
Copyright (c) 2018 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys, os, ntpath, signal, re, subprocess                          # for file operations, to kill processes, for regex, for subprocesses
try:
    import queue
except:
    import Queue as queue
from PyQt5.QtGui import *                                               # for filters dialog
from app.logic import *
from app.auxiliary import *
from app.settings import *

class Controller():

    # initialisations that will happen once - when the program is launched
    @timing
    def __init__(self, view, logic):
        self.name = "LEGION"
        self.version = '0.3.4'
        self.build = '1555077770'
        self.author = 'GoVanguard'
        self.copyright = '2019'
        self.links = ['http://github.com/GoVanguard/legion/issues', 'https://GoVanguard.io/legion']
        self.emails = []

        self.update = '04/12/2019'

        self.license = "GPL v3"
        self.desc = "Legion is a fork of SECFORCE's Sparta, Legion is an open source, easy-to-use, \nsuper-extensible and semi-automated network penetration testing tool that aids in discovery, \nreconnaissance and exploitation of information systems."
        self.smallIcon = './images/icons/Legion-N_128x128.svg'
        self.bigIcon = './images/icons/Legion-N_128x128.svg'

        self.logic = logic
        self.view = view
        self.view.setController(self)
        self.view.startOnce()
        self.view.startConnections()

        self.loadSettings()                                             # creation of context menu actions from settings file and set up of various settings        
        self.initNmapImporter()
        self.initScreenshooter()
        self.initBrowserOpener()
        self.start()                                                    # initialisations (globals, etc)
        self.initTimers()
        self.processTimers = {}
        self.processMeasurements = {}
        
    # initialisations that will happen everytime we create/open a project - can happen several times in the program's lifetime
    def start(self, title='*untitled'):
        self.processes = []                                             # to store all the processes we run (nmaps, niktos, etc)
        self.fastProcessQueue = queue.Queue()                           # to manage fast processes (banner, snmpenum, etc)
        self.fastProcessesRunning = 0                                   # counts the number of fast processes currently running
        self.slowProcessesRunning = 0                                   # counts the number of slow processes currently running
        self.nmapImporter.setDB(self.logic.db)                          # tell nmap importer which db to use
        self.updateOutputFolder()                                       # tell screenshooter where the output folder is
        self.view.start(title)
        
    def initNmapImporter(self):
        self.nmapImporter = NmapImporter()
        self.nmapImporter.done.connect(self.nmapImportFinished)
        self.nmapImporter.schedule.connect(self.scheduler)              # run automated attacks
        self.nmapImporter.log.connect(self.view.ui.LogOutputTextView.append)
    
    def initScreenshooter(self):
        self.screenshooter = Screenshooter(self.settings.general_screenshooter_timeout)         # screenshot taker object (different thread)
        self.screenshooter.done.connect(self.screenshotFinished)
        self.screenshooter.log.connect(self.view.ui.LogOutputTextView.append)

    def initBrowserOpener(self):
        self.browser = BrowserOpener()                                  # browser opener object (different thread)
        self.browser.log.connect(self.view.ui.LogOutputTextView.append)

    def initTimers(self):                                               # these timers are used to prevent from updating the UI several times within a short time period - which freezes the UI
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

    # this function fetches all the settings from the conf file. Among other things it populates the actions lists that will be used in the context menus.
    def loadSettings(self):
        self.settingsFile = AppSettings()
        self.settings = Settings(self.settingsFile)                     # load settings from conf file (create conf file first if necessary)
        self.originalSettings = Settings(self.settingsFile)             # save the original state so that we can know if something has changed when we exit LEGION
        self.logic.setStoreWordlistsOnExit(self.settings.brute_store_cleartext_passwords_on_exit=='True')
        self.view.settingsWidget.setSettings(Settings(self.settingsFile))
        
    def applySettings(self, newSettings):                               # call this function when clicking 'apply' in the settings menu (after validation)
        self.settings = newSettings

    def cancelSettings(self):                                           # called when the user presses cancel in the Settings dialog
        self.view.settingsWidget.setSettings(self.settings)             # resets the dialog's settings to the current application settings to forget any changes made by the user

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
        return self.logic.cwd
        
    def getProjectName(self):
        return self.logic.projectname
        
    def getVersion(self):
        return (self.version + "-" + self.build)
        
    def getRunningFolder(self):
        return self.logic.runningfolder

    def getOutputFolder(self):
        return self.logic.outputfolder
        
    def getUserlistPath(self):
        return self.logic.usernamesWordlist.filename
        
    def getPasslistPath(self):
        return self.logic.passwordsWordlist.filename        
        
    def updateOutputFolder(self):
        self.screenshooter.updateOutputFolder(self.logic.outputfolder+'/screenshots')   # update screenshot folder

    def copyNmapXMLToOutputFolder(self, filename):
        self.logic.copyNmapXMLToOutputFolder(filename)

    def isTempProject(self):
        return self.logic.istemp
        
    def getDB(self):
        return self.logic.db
        
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
        self.view.closeProject()                                        # removes temp folder (if any)
        self.logic.createTemporaryFiles()                               # creates new temp files and folders
        self.start()                                                    # initialisations (globals, etc)

    def openExistingProject(self, filename, projectType='legion'):
        self.view.closeProject()
        self.view.importProgressWidget.reset('Opening project..')
        self.view.importProgressWidget.show()                           # show the progress widget      
        self.logic.openExistingProject(filename, projectType)
        self.start(ntpath.basename(str(self.logic.projectname)))        # initialisations (globals, signals, etc)
        self.view.restoreToolTabs()                                     # restores the tool tabs for each host
        self.view.hostTableClick()                                      # click on first host to restore his host tool tabs
        self.view.importProgressWidget.hide()                           # hide the progress widget

    def saveProject(self, lastHostIdClicked, notes):
        if not lastHostIdClicked == '':
            self.logic.storeNotesInDB(lastHostIdClicked, notes)

    def saveProjectAs(self, filename, replace=0):
        success = self.logic.saveProjectAs(filename, replace)
        if success:
            self.nmapImporter.setDB(self.logic.db)                      # tell nmap importer which db to use
        return success
            
    def closeProject(self):
        self.saveSettings()                                             # backup and save config file, if necessary
        self.screenshooter.terminate()
        self.initScreenshooter()
        self.logic.toggleProcessDisplayStatus(True)
        self.view.updateProcessesTableView()                            # clear process table
        self.logic.removeTemporaryFiles()

    @timing
    def addHosts(self, targetHosts, runHostDiscovery, runStagedNmap, nmapSpeed, scanMode, nmapOptions = []):
        if targetHosts == '':
            log.info('No hosts entered..')
            return

        if scanMode == 'Easy':
            if runStagedNmap:
                self.runStagedNmap(targetHosts, runHostDiscovery)
            elif runHostDiscovery:
                outputfile = self.logic.runningfolder + "/nmap/" + getTimestamp() + '-host-discover'
                command = "nmap -n -sV -O --version-light -T" + str(nmapSpeed) + " " + targetHosts + " -oA "+outputfile
                log.info("Running {command}".format(command=command))
                self.runCommand('nmap', 'nmap (discovery)', targetHosts, '','', command, getTimestamp(True), outputfile, self.view.createNewTabForHost(str(targetHosts), 'nmap (discovery)', True))               
            else:
                outputfile = self.logic.runningfolder + "/nmap/" + getTimestamp() + '-nmap-list'
                command = "nmap -n -sL -T" + str(nmapSpeed) + " " + targetHosts + " -oA " + outputfile
                self.runCommand('nmap', 'nmap (list)', targetHosts, '','', command, getTimestamp(True), outputfile, self.view.createNewTabForHost(str(targetHosts), 'nmap (list)', True))
        elif scanMode == 'Hard':
            outputfile = self.logic.runningfolder + "/nmap/" + getTimestamp() + '-nmap-custom'
            nmapOptionsString = ' '.join(nmapOptions)
            nmapOptionsString = nmapOptionsString + " -T" + str(nmapSpeed)
            command = "nmap " + nmapOptionsString + " " + targetHosts + " -oA " + outputfile
            self.runCommand('nmap', 'nmap (custom ' + nmapOptionsString + ')', targetHosts, '','', command, getTimestamp(True), outputfile, self.view.createNewTabForHost(str(targetHosts), 'nmap (custom ' + nmapOptionsString + ')', True))

    #################### CONTEXT MENUS ####################

    @timing
    def getContextMenuForHost(self, isChecked, showAll=True):           # showAll exists because in some cases we only want to show host tools excluding portscans and 'mark as checked'
        
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
        
        if action.text() == 'Mark as checked' or action.text() == 'Mark as unchecked':
            self.logic.toggleHostCheckStatus(ip)
            self.view.updateInterface()
            return
            
        if action.text() == 'Run nmap (staged)':
            log.info('Purging previous portscan data for ' + str(ip))  # if we are running nmap we need to purge previous portscan results
            if self.logic.getPortsForHostFromDB(ip, 'tcp'):
                self.logic.deleteAllPortsAndScriptsForHostFromDB(hostid, 'tcp')
            if self.logic.getPortsForHostFromDB(ip, 'udp'):
                self.logic.deleteAllPortsAndScriptsForHostFromDB(hostid, 'udp')
            self.view.updateInterface()
            self.runStagedNmap(ip, False)
            return

        if action.text() == 'Rescan':
            log.info('Rescanning host {0}'.format(str(ip)))
            self.runStagedNmap(ip, False)
            return

        if action.text() == 'Purge Results':
            log.info('Purging previous portscan data for host {0}'.format(str(ip)))
            if self.logic.getPortsForHostFromDB(ip, 'tcp'):
                self.logic.deleteAllPortsAndScriptsForHostFromDB(hostid, 'tcp')
            if self.logic.getPortsForHostFromDB(ip, 'udp'):
                self.logic.deleteAllPortsAndScriptsForHostFromDB(hostid, 'udp')
            self.view.updateInterface()
            return

        if action.text() == 'Delete':
            log.info('Purging previous portscan data for host {0}'.format(str(ip)))
            if self.logic.getPortsForHostFromDB(ip, 'tcp'):
                self.logic.deleteAllPortsAndScriptsForHostFromDB(hostid, 'tcp')
            if self.logic.getPortsForHostFromDB(ip, 'udp'):
                self.logic.deleteAllPortsAndScriptsForHostFromDB(hostid, 'udp')
            self.logic.deleteHost(ip)
            self.view.updateInterface()
            return
            
        for i in range(0,len(actions)):
            if action == actions[i]:
                name = self.settings.hostActions[i][1]
                invisibleTab = False
                if 'nmap' in name:                                      # to make sure different nmap scans appear under the same tool name
                    name = 'nmap'
                    invisibleTab = True                 
                                                                        # remove all chars that are not alphanumeric from tool name (used in the outputfile's name)
                outputfile = self.logic.runningfolder+"/"+re.sub("[^0-9a-zA-Z]", "", str(name))+"/"+getTimestamp()+"-"+re.sub("[^0-9a-zA-Z]", "", str(self.settings.hostActions[i][1]))+"-"+ip  
                command = str(self.settings.hostActions[i][2])
                command = command.replace('[IP]', ip).replace('[OUTPUT]', outputfile)
                                                                        # check if same type of nmap scan has already been made and purge results before scanning
                if 'nmap' in command:
                    proto = 'tcp'
                    if '-sU' in command:
                        proto = 'udp'

                    if self.logic.getPortsForHostFromDB(ip, proto):     # if we are running nmap we need to purge previous portscan results (of the same protocol)
                        self.logic.deleteAllPortsAndScriptsForHostFromDB(hostid, proto)

                tabtitle = self.settings.hostActions[i][1]
                self.runCommand(name, tabtitle, ip, '','', command, getTimestamp(True), outputfile, self.view.createNewTabForHost(ip, tabtitle, invisibleTab))
                break

    @timing    
    def getContextMenuForServiceName(self, serviceName='*', menu=None):
        if menu == None:                                                # if no menu was given, create a new one
            menu = QMenu()

        if serviceName == '*' or serviceName in self.settings.general_web_services.split(","):
            menu.addAction("Open in browser")
            menu.addAction("Take screenshot")

        actions = []
        for a in self.settings.portActions:         
            if serviceName is None or serviceName == '*' or serviceName in a[3].split(",") or a[3] == '':   # if the service name exists in the portActions list show the command in the context menu
                actions.append([self.settings.portActions.index(a), menu.addAction(a[0])])  # in actions list write the service and line number that corresponds to it in portActions

        modifiers = QtWidgets.QApplication.keyboardModifiers()              # if the user pressed SHIFT+Right-click show full menu
        if modifiers == QtCore.Qt.ShiftModifier:
            shiftPressed = True
        else:
            shiftPressed = False
        
        return menu, actions, shiftPressed

    @timing
    def handleServiceNameAction(self, targets, actions, action, restoring=True):

        if action.text() == 'Take screenshot':
            for ip in targets:
                url = ip[0]+':'+ip[1]
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
                    tabtitle = self.settings.portActions[srvc_num][1]+" ("+ip[1]+"/"+ip[2]+")"                  
                    outputfile = self.logic.runningfolder+"/"+re.sub("[^0-9a-zA-Z]", "", str(tool))+"/"+getTimestamp()+'-'+tool+"-"+ip[0]+"-"+ip[1]
                                        
                    command = str(self.settings.portActions[srvc_num][2])
                    command = command.replace('[IP]', ip[0]).replace('[PORT]', ip[1]).replace('[OUTPUT]', outputfile)
                    
                    if 'nmap' in command and ip[2] == 'udp':
                        command=command.replace("-sV","-sVU")

                    if 'nmap' in tabtitle:                              # we don't want to show nmap tabs
                        restoring = True

                    self.runCommand(tool, tabtitle, ip[0], ip[1], ip[2], command, getTimestamp(True), outputfile, self.view.createNewTabForHost(ip[0], tabtitle, restoring))
                break

    @timing
    def getContextMenuForPort(self, serviceName='*'):

        menu = QMenu()

        modifiers = QtWidgets.QApplication.keyboardModifiers()              # if the user pressed SHIFT+Right-click show full menu
        if modifiers == QtCore.Qt.ShiftModifier:
            serviceName='*'
        
        terminalActions = []                                            # custom terminal actions from settings file
        for a in self.settings.portTerminalActions:                             # if wildcard or the command is valid for this specific service or if the command is valid for all services
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
                self.view.createNewBruteTab(ip[0], ip[1], ip[3])        # ip[0] is the IP, ip[1] is the port number and ip[3] is the service name
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
        killAction = menu.addAction("Kill")
        clearAction = menu.addAction("Clear")
        return menu
    
    def handleProcessAction(self, selectedProcesses, action):           # selectedProcesses is a list of tuples (pid, status, procId)
        
        if action.text() == 'Kill':
            if self.view.killProcessConfirmation():
                for p in selectedProcesses:
                    if p[1]!="Running":
                        if p[1]=="Waiting":
                            if str(self.logic.getProcessStatusForDBId(p[2])) == 'Running':
                                self.killProcess(self.view.ProcessesTableModel.getProcessPidForId(p[2]), p[2])
                            self.logic.storeProcessCancelStatusInDB(str(p[2]))
                        else:
                            log.info("This process has already been terminated. Skipping.")
                    else:
                        self.killProcess(p[0], p[2])
                self.view.updateProcessesTableView()
            return
                        
        if action.text() == 'Clear':                                    # hide all the processes that are not running
            self.logic.toggleProcessDisplayStatus()
            self.view.updateProcessesTableView()

    #################### LEFT PANEL INTERFACE UPDATE FUNCTIONS ####################

    def isHostInDB(self, host):
        return self.logic.isHostInDB(host)

    def getHostsFromDB(self, filters):
        return self.logic.getHostsFromDB(filters)
        
    def getServiceNamesFromDB(self, filters):
        return self.logic.getServiceNamesFromDB(filters)

    def getProcessStatusForDBId(self, dbId):
        return self.logic.getProcessStatusForDBId(dbId)
    
    def getPidForProcess(self,dbId):
        return self.logic.getPidForProcess(dbId)

    def storeCloseTabStatusInDB(self,pid):
        return self.logic.storeCloseTabStatusInDB(pid)

    def getServiceNameForHostAndPort(self, hostIP, port):
        return self.logic.getServiceNameForHostAndPort(hostIP, port)
                
    #################### RIGHT PANEL INTERFACE UPDATE FUNCTIONS ####################
    
    def getPortsAndServicesForHostFromDB(self, hostIP, filters):
        return self.logic.getPortsAndServicesForHostFromDB(hostIP, filters)

    def getHostsAndPortsForServiceFromDB(self, serviceName, filters):
        return self.logic.getHostsAndPortsForServiceFromDB(serviceName, filters)
        
    def getHostInformation(self, hostIP):
        return self.logic.getHostInformation(hostIP)
        
    def getPortStatesForHost(self, hostid):
        return self.logic.getPortStatesForHost(hostid)

    def getScriptsFromDB(self, hostIP):
        return self.logic.getScriptsFromDB(hostIP)

    def getCvesFromDB(self, hostIP):
        return self.logic.getCvesFromDB(hostIP)

    def getScriptOutputFromDB(self,scriptDBId):
        return self.logic.getScriptOutputFromDB(scriptDBId)

    def getNoteFromDB(self, hostid):
        return self.logic.getNoteFromDB(hostid)

    def getHostsForTool(self, toolname, closed = 'False'):
        return self.logic.getHostsForTool(toolname, closed)
    
    #################### BOTTOM PANEL INTERFACE UPDATE FUNCTIONS ####################       

    def getProcessesFromDB(self, filters, showProcesses = 'noNmap', sort = 'desc', ncol = 'id'):
        return self.logic.getProcessesFromDB(filters, showProcesses, sort, ncol)
                    
    #################### PROCESSES ####################

    def checkProcessQueue(self):
        log.debug('# MAX PROCESSES: ' + str(self.settings.general_max_fast_processes))
        log.debug('# Fast processes running: ' + str(self.fastProcessesRunning))
        log.debug('# Fast processes queued: ' + str(self.fastProcessQueue.qsize()))
        
        if not self.fastProcessQueue.empty():
            self.processTableUiUpdateTimer.start(1000)
            if (self.fastProcessesRunning <= int(self.settings.general_max_fast_processes)):
                next_proc = self.fastProcessQueue.get()
                if not self.logic.isCanceledProcess(str(next_proc.id)):
                    log.debug('Running: '+ str(next_proc.command))
                    next_proc.display.clear()
                    self.processes.append(next_proc)
                    self.fastProcessesRunning += 1
                    # Add Timeout 
                    next_proc.waitForFinished(10)
                    next_proc.start(next_proc.command)
                    self.logic.storeProcessRunningStatusInDB(next_proc.id, next_proc.pid())
                elif not self.fastProcessQueue.empty():
                    log.debug('> next process was canceled, checking queue again..')
                    self.checkProcessQueue()
        #else:
        #    log.info("Halting process panel update timer as all processes are finished.")
        #    self.processTableUiUpdateTimer.stop()
            
    def cancelProcess(self, dbId):
        log.info('Canceling process: ' + str(dbId))
        self.logic.storeProcessCancelStatusInDB(str(dbId))              # mark it as cancelled
        self.updateUITimer.stop()
        self.updateUITimer.start(1500)                                  # update the interface soon

    def killProcess(self, pid, dbId):
        log.info('Killing process: ' + str(pid))
        self.logic.storeProcessKillStatusInDB(str(dbId))                # mark it as killed
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
            self.logic.storeProcessRunningElapsedInDB(qProcess.id, procTime)

        def handleProcUpdate(*vargs):
            procTime = timer.elapsed() / 1000
            self.processMeasurements[qProcess.pid()] = procTime

        name = args[0]
        tabtitle = args[1]
        hostip = args[2]
        port = args[3]
        protocol = args[4]
        command = args[5]
        starttime = args[6]
        outputfile = args[7]
        textbox = args[8]
        timer = QtCore.QTime()
        updateElapsed = QTimer()

        self.logic.createFolderForTool(name)
        qProcess = MyQProcess(name, tabtitle, hostip, port, protocol, command, starttime, outputfile, textbox)
        qProcess.started.connect(timer.start)
        qProcess.finished.connect(handleProcStop)
        updateElapsed.timeout.connect(handleProcUpdate)

        textbox.setProperty('dbId', str(self.logic.addProcessToDB(qProcess)))
        updateElapsed.start(1000)
        self.processTimers[qProcess.id] = updateElapsed
        self.processMeasurements[qProcess.pid()] = 0
        
        log.info('Queuing: ' + str(command))
        self.fastProcessQueue.put(qProcess)

        self.checkProcessQueue()
        
        self.updateUITimer.stop()                                       # update the processes table
        self.updateUITimer.start(900)                                   # while the process is running, when there's output to read, display it in the GUI

        qProcess.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        qProcess.readyReadStandardOutput.connect(lambda: qProcess.display.appendPlainText(str(qProcess.readAllStandardOutput().data().decode('ISO-8859-1'))))

        qProcess.sigHydra.connect(self.handleHydraFindings)
        qProcess.finished.connect(lambda: self.processFinished(qProcess))
        qProcess.error.connect(lambda: self.processCrashed(qProcess))
        log.info("runCommand called for stage {0}".format(str(stage)))

        if stage > 0 and stage < 6:                                     # if this is a staged nmap, launch the next stage
            log.info("runCommand connected for stage {0}".format(str(stage)))
            nextStage = stage + 1
            qProcess.finished.connect(lambda: self.runStagedNmap(str(hostip), discovery = discovery, stage = nextStage, stop = self.logic.isKilledProcess(str(qProcess.id))))

        return qProcess.pid()                                           # return the pid so that we can kill the process if needed

    def runPython(self):
        textbox = self.view.createNewConsole("python")
        name = 'python'
        tabtitle = name
        hostip = '127.0.0.1'
        port = '22'
        protocol = 'tcp'
        command = 'python3 /mnt/c/Users/hackm/OneDrive/Documents/Customers/GVIT/GIT/legion/test.py'
        starttime = getTimestamp(True)
        outputfile = '/tmp/a'
        qProcess = MyQProcess(name, tabtitle, hostip, port, protocol, command, starttime, outputfile, textbox)

        textbox.setProperty('dbId', str(self.logic.addProcessToDB(qProcess)))

        log.info('Queuing: ' + str(command))
        self.fastProcessQueue.put(qProcess)

        self.checkProcessQueue()

        self.updateUI2Timer.stop()                                       # update the processes table
        self.updateUI2Timer.start(900)                                   # while the process is running, when there's output to read, display it in the GUI
        self.updateUITimer.stop()                                       # update the processes table
        self.updateUITimer.start(900)

        qProcess.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        qProcess.readyReadStandardOutput.connect(lambda: qProcess.display.appendPlainText(str(qProcess.readAllStandardOutput().data().decode('ISO-8859-1'))))

        qProcess.sigHydra.connect(self.handleHydraFindings)
        qProcess.finished.connect(lambda: self.processFinished(qProcess))
        qProcess.error.connect(lambda: self.processCrashed(qProcess))

        return qProcess.pid()

    # recursive function used to run nmap in different stages for quick results
    def runStagedNmap(self, targetHosts, discovery = True, stage = 1, stop = False):
        log.info("runStagedNmap called for stage {0}".format(str(stage)))
        if not stop:
            textbox = self.view.createNewTabForHost(str(targetHosts), 'nmap (stage '+str(stage)+')', True)
            outputfile = self.logic.runningfolder+"/nmap/"+getTimestamp()+'-nmapstage'+str(stage)       
            
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
            command += "-T4 -sC "
            if not stage == 1 and not stage == 3:
                command += "-n "                                        # only do DNS resolution on first stage
            if os.geteuid() == 0:                                       # if we are root we can run SYN + UDP scans
                command += "-sSU "
                if stage == 2:
                    command += '-O '                                    # only check for OS once to save time and only if we are root otherwise it fail
            else:
                command += '-sT '

            if stage != 3:
                command += '-p ' + ports + ' ' + targetHosts + ' -oA ' + outputfile
            else:
                command = 'nmap -sV --script=./scripts/nmap/vulners.nse -vvvv ' + targetHosts + ' -oA ' + outputfile
                            
            self.runCommand('nmap','nmap (stage '+str(stage)+')', str(targetHosts), '', '', command, getTimestamp(True), outputfile, textbox, discovery = discovery, stage = stage, stop = stop)

    def nmapImportFinished(self):
        self.updateUI2Timer.stop()
        self.updateUI2Timer.start(800)  
        self.view.displayAddHostsOverlay(False)                         # if nmap import was the first action, we need to hide the overlay (note: we shouldn't need to do this everytime. this can be improved)

    def screenshotFinished(self, ip, port, filename):
        dbId = self.logic.addScreenshotToDB(str(ip),str(port),str(filename))
        imageviewer = self.view.createNewTabForHost(ip, 'screenshot ('+port+'/tcp)', True, '', str(self.logic.outputfolder)+'/screenshots/'+str(filename))
        imageviewer.setProperty('dbId', QVariant(str(dbId)))
        self.view.switchTabClick()                                      # to make sure the screenshot tab appears when it is launched from the host services tab
        self.updateUITimer.stop()                                       # update the processes table
        self.updateUITimer.start(900)

    def processCrashed(self, proc):
        self.logic.storeProcessCrashStatusInDB(str(proc.id))
        log.info('Process {qProcessId} Crashed!'.format(qProcessId=str(proc.id)))
        qProcessOutput = "\n\t" + str(proc.display.toPlainText()).replace('\n','').replace("b'","")
        log.info('Process {qProcessId} Output: {qProcessOutput}'.format(qProcessId=str(proc.id), qProcessOutput=qProcessOutput))

    # this function handles everything after a process ends
    #def processFinished(self, qProcess, crashed=False):
    def processFinished(self, qProcess):
        try:
            if not self.logic.isKilledProcess(str(qProcess.id)):        # if process was not killed
                if not qProcess.outputfile == '':
                    self.logic.moveToolOutput(qProcess.outputfile)      # move tool output from runningfolder to output folder if there was an output file
                
                    if 'nmap' in qProcess.name:                         # if the process was nmap, use the parser to store it
                        if qProcess.exitCode() == 0:                    # if the process finished successfully
                            newoutputfile = qProcess.outputfile.replace(self.logic.runningfolder, self.logic.outputfolder)
                            self.nmapImporter.setFilename(str(newoutputfile)+'.xml')
                            self.nmapImporter.setOutput(str(qProcess.display.toPlainText()))
                            self.nmapImporter.start()
                exitCode = qProcess.exitCode()
                if exitCode != 0 and exitCode != 255:
                    log.info("Process {qProcessId} exited with code {qProcessExitCode}".format(qProcessId=qProcess.id, qProcessExitCode=qProcess.exitCode()))
                    self.processCrashed(qProcess)
                
                log.info("Process {qProcessId} is done!".format(qProcessId=qProcess.id))
 
            
            self.logic.storeProcessOutputInDB(str(qProcess.id), qProcess.display.toPlainText())
            
            if 'hydra' in qProcess.name:                                # find the corresponding widget and tell it to update its UI
                self.view.findFinishedBruteTab(str(self.logic.getPidForProcess(str(qProcess.id))))

            try:
                self.fastProcessesRunning =- 1
                self.checkProcessQueue()
                self.processes.remove(qProcess)
                self.updateUITimer.stop()
                self.updateUITimer.start(1000)                          # update the interface soon
                
            except Exception as e:
                log.info("Process Finished Cleanup Exception {e}".format(e=e))
        except Exception as e:                                                         # fixes bug when receiving finished signal when project is no longer open.
            log.info("Process Finished Exception {e}".format(e=e))
            raise

    def handleHydraFindings(self, bWidget, userlist, passlist):         # when hydra finds valid credentials we need to save them and change the brute tab title to red
        self.view.blinkBruteTab(bWidget)
        for username in userlist:
            self.logic.usernamesWordlist.add(username)
        for password in passlist:
            self.logic.passwordsWordlist.add(password)

    # this function parses nmap's output looking for open ports to run automated attacks on
    def scheduler(self, parser, isNmapImport):
        if isNmapImport and self.settings.general_enable_scheduler_on_import == 'False':
            return
        if self.settings.general_enable_scheduler == 'True':
            log.info('Scheduler started!')
            
            for h in parser.all_hosts():
                for p in h.all_ports():
                    if p.state == 'open':
                        s = p.get_service()
                        if not (s is None):
                            self.runToolsFor(s.name, h.ip, p.portId, p.protocol)
                    
            log.info('-----------------------------------------------')
        log.info('Scheduler ended!')

    def runToolsFor(self, service, ip, port, protocol='tcp'):
        log.info('Running tools for: ' + service + ' on ' + ip + ':' + port)

        if service.endswith("?"):                                       # when nmap is not sure it will append a ?, so we need to remove it
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
                            restoring = False
                            tabtitle = a[1]+" ("+port+"/"+protocol+")"
                            outputfile = self.logic.runningfolder+"/"+re.sub("[^0-9a-zA-Z]", "", str(tool[0]))+"/"+getTimestamp()+'-'+a[1]+"-"+ip+"-"+port
                            command = str(a[2])
                            command = command.replace('[IP]', ip).replace('[PORT]', port).replace('[OUTPUT]', outputfile)
                            log.debug("Running tool command " + str(command))

                            if 'nmap' in tabtitle:                          # we don't want to show nmap tabs
                                restoring = True

                            tab = self.view.ui.HostsTabWidget.tabText(self.view.ui.HostsTabWidget.currentIndex())                       
                            self.runCommand(tool[0], tabtitle, ip, port, protocol, command, getTimestamp(True), outputfile, self.view.createNewTabForHost(ip, tabtitle, not (tab == 'Hosts')))
                            break

