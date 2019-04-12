#!/usr/bin/env python

'''
LEGION (https://govanguard.io)
Copyright (c) 2018 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys, os, ntpath, signal, re                                      # for file operations, to kill processes and for regex

from PyQt5.QtCore import *                                              # for filters dialog
from PyQt5 import QtCore
from PyQt5 import QtWidgets, QtGui, QtCore

from ui.gui import *
from ui.dialogs import *
from ui.settingsDialog import *
from ui.configDialog import *
from ui.helpDialog import *
from ui.addHostDialog import *
from ui.ancillaryDialog import *
from app.hostmodels import *
from app.servicemodels import *
from app.scriptmodels import *
from app.cvemodels import *
from app.processmodels import *
from app.auxiliary import *
import time #temp
from six import u as unicode

# this class handles everything gui-related
class View(QtCore.QObject):
    tick = QtCore.pyqtSignal(int, name="changed")                       # signal used to update the progress bar
    
    def __init__(self, ui, ui_mainwindow):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.ui_mainwindow = ui_mainwindow                              # TODO: retrieve window dimensions/location from settings

        self.bottomWindowSize = 100
        self.leftPanelSize = 300

        self.ui.splitter_2.setSizes([250, self.bottomWindowSize])                           # set better default size for bottom panel
        self.qss = None
        self.processesTableViewSort = 'desc'
        self.processesTableViewSortColumn = 'status'
        self.toolsTableViewSort = 'desc'
        self.toolsTableViewSortColumn = 'id'

    def setController(self, controller):                                # the view needs access to controller methods to link gui actions with real actions
        self.controller = controller

    def startOnce(self):
        self.fixedTabsCount = self.ui.ServicesTabWidget.count()         # the number of fixed host tabs (services, scripts, information, notes)
        self.hostInfoWidget = HostInformationWidget(self.ui.InformationTab)
        self.filterdialog = FiltersDialog(self.ui.centralwidget)
        self.importProgressWidget = ProgressWidget('Importing nmap..', self.ui.centralwidget)
        self.adddialog = AddHostsDialog(self.ui.centralwidget)      
        self.settingsWidget = AddSettingsDialog(self.ui.centralwidget)
        self.helpDialog = HelpDialog(self.controller.name, self.controller.author, self.controller.copyright, self.controller.links, self.controller.emails, self.controller.version, self.controller.build, self.controller.update, self.controller.license, self.controller.desc, self.controller.smallIcon, self.controller.bigIcon, qss = self.qss, parent = self.ui.centralwidget)
        self.configDialog = ConfigDialog(controller = self.controller, qss = self.qss, parent = self.ui.centralwidget)

        self.ui.HostsTableView.setSelectionMode(1)                      # disable multiple selection
        self.ui.ServiceNamesTableView.setSelectionMode(1)
        self.ui.CvesTableView.setSelectionMode(1)
        self.ui.ToolsTableView.setSelectionMode(1)
        self.ui.ScriptsTableView.setSelectionMode(1)        
        self.ui.ToolHostsTableView.setSelectionMode(1)

    # initialisations (globals, etc)
    def start(self, title='*untitled'):
        self.dirty = False                                              # to know if the project has been saved
        self.firstSave = True                                           # to know if we should use the save as dialog (should probably be False until we add/import a host)
        self.hostTabs = dict()                                          # to keep track of which tabs should be displayed for each host
        self.bruteTabCount = 1                                          # to keep track of the numbering of the bruteforce tabs (incremented when a new tab is added)
        
        self.filters = Filters()                                        # to choose what to display in each panel

        self.ui.keywordTextInput.setText('')                            # clear keyword filter

        self.lastHostIdClicked = ''                                     # TODO: check if we can get rid of this one.
        self.ip_clicked = ''                                            # useful when updating interfaces (serves as memory)
        self.service_clicked = ''                                       # useful when updating interfaces (serves as memory)
        self.tool_clicked = ''                                          # useful when updating interfaces (serves as memory)
        self.script_clicked = ''                                        # useful when updating interfaces (serves as memory)
        self.tool_host_clicked = ''                                     # useful when updating interfaces (serves as memory)
        self.lazy_update_hosts = False                                  # these variables indicate that the corresponding table needs to be updated.
        self.lazy_update_services = False                               # 'lazy' means we only update a table at the last possible minute - before the user needs to see it
        self.lazy_update_tools = False
        self.menuVisible = False                                        # to know if a context menu is showing (important to avoid disrupting the user)
        self.ProcessesTableModel = None                                 # fixes bug when sorting processes for the first time
        self.ToolsTableModel = None
        self.setupProcessesTableView()
        self.setupToolsTableView()

        self.setMainWindowTitle(title)
        self.ui.statusbar.showMessage('Starting up..', msecs=1000)

        self.initTables()                                               # initialise all tables

        self.updateInterface()
        self.restoreToolTabWidget(True)                                 # True means we want to show the original textedit
        self.updateScriptsOutputView('')                                # update the script output panel (right) 
        self.updateToolHostsTableView('')
        self.ui.MainTabWidget.setCurrentIndex(0)                        # display scan tab by default
        self.ui.HostsTabWidget.setCurrentIndex(0)                       # display Hosts tab by default
        self.ui.ServicesTabWidget.setCurrentIndex(0)                    # display Services tab by default
        self.ui.BottomTabWidget.setCurrentIndex(0)                      # display Log tab by default
        self.ui.BruteTabWidget.setTabsClosable(True)                    # sets all tabs as closable in bruteforcer

        self.ui.ServicesTabWidget.setTabsClosable(True)                 # hide the close button (cross) from the fixed tabs

        self.ui.ServicesTabWidget.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.ui.ServicesTabWidget.tabBar().setTabButton(1, QTabBar.RightSide, None)
        self.ui.ServicesTabWidget.tabBar().setTabButton(2, QTabBar.RightSide, None)
        self.ui.ServicesTabWidget.tabBar().setTabButton(3, QTabBar.RightSide, None)
        self.ui.ServicesTabWidget.tabBar().setTabButton(4, QTabBar.RightSide, None)

        self.resetBruteTabs()                                           # clear brute tabs (if any) and create default brute tab
        self.displayToolPanel(False)
        self.displayScreenshots(False)
        self.displayAddHostsOverlay(True)                               # displays an overlay over the hosttableview saying 'click here to add host(s) to scope'

    def startConnections(self):                                         # signal initialisations (signals/slots, actions, etc)
        ### MENU ACTIONS ###
        self.connectCreateNewProject()
        self.connectOpenExistingProject()
        self.connectSaveProject()
        self.connectSaveProjectAs()
        self.connectAddHosts()
        self.connectImportNmap()
        #self.connectSettings()
        self.connectHelp()      
        self.connectConfig()
        self.connectAppExit()
        ### TABLE ACTIONS ###
        self.connectAddHostsOverlayClick()
        self.connectHostTableClick()        
        self.connectServiceNamesTableClick()
        self.connectToolsTableClick()
        self.connectScriptTableClick()
        self.connectToolHostsClick()
        self.connectAdvancedFilterClick()
        self.connectAddHostClick()
        self.connectSwitchTabClick()                                    # to detect changing tabs (on left panel)
        self.connectSwitchMainTabClick()                                # to detect changing top level tabs
        self.connectTableDoubleClick()                                  # for double clicking on host (it redirects to the host view)
        self.connectProcessTableHeaderResize()
        ### CONTEXT MENUS ###
        self.connectHostsTableContextMenu()
        self.connectServiceNamesTableContextMenu()
        self.connectServicesTableContextMenu()
        self.connectToolHostsTableContextMenu()
        self.connectProcessesTableContextMenu()
        self.connectScreenshotContextMenu()
        ### OTHER ###
        self.ui.NotesTextEdit.textChanged.connect(self.setDirty)
        self.ui.FilterApplyButton.clicked.connect(self.updateFilterKeywords)
        self.ui.ServicesTabWidget.tabCloseRequested.connect(self.closeHostToolTab)
        self.ui.BruteTabWidget.tabCloseRequested.connect(self.closeBruteTab)
        self.ui.keywordTextInput.returnPressed.connect(self.ui.FilterApplyButton.click)
        self.filterdialog.applyButton.clicked.connect(self.updateFilter)
        #self.settingsWidget.applyButton.clicked.connect(self.applySettings)
        #self.settingsWidget.cmdCancelButton.clicked.connect(self.cancelSettings)
        #self.settingsWidget.applyButton.clicked.connect(self.controller.applySettings(self.settingsWidget.settings))
        self.tick.connect(self.importProgressWidget.setProgress)        # slot used to update the progress bar

    #################### AUXILIARY ####################

    def initTables(self):                                               # this function prepares the default settings for each table
        # hosts table (left)
        headers = ["Id", "OS", "Accuracy", "Host", "IPv4", "IPv6", "Mac", "Status", "Hostname", "Vendor", "Uptime", "Lastboot", "Distance", "CheckedHost", "State", "Count", "Padding"]
        setTableProperties(self.ui.HostsTableView, len(headers), [0, 2, 4, 5, 6, 7, 8, 9, 10 , 11, 12, 13, 14, 15, 16])
        self.ui.HostsTableView.horizontalHeader().resizeSection(1, 30)

        # service names table (left)
        headers = ["Name"]
        setTableProperties(self.ui.ServiceNamesTableView, len(headers))

        # cves table (right)
        headers = ["Id", "Severity", "Product", "Version", "URL", "Source"]
        setTableProperties(self.ui.CvesTableView, len(headers))
        self.ui.CvesTableView.setSortingEnabled(True)

        # tools table (left)
        headers = ["Progress", "Display", "Pid", "Tool", "Tool", "Host", "Port", "Protocol", "Command", "Start time", "OutputFile", "Output", "Status"]
        setTableProperties(self.ui.ToolsTableView, len(headers), [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])

        # service table (right)
        headers = ["Host", "Port", "Port", "Protocol", "State", "HostId", "ServiceId", "Name", "Product", "Version", "Extrainfo", "Fingerprint"]
        setTableProperties(self.ui.ServicesTableView, len(headers), [0, 1, 5, 6, 8, 10, 11])      

        # ports by service (right)
        headers = ["Host", "Port", "Port", "Protocol", "State", "HostId", "ServiceId", "Name", "Product", "Version", "Extrainfo", "Fingerprint"]
        setTableProperties(self.ui.ServicesTableView, len(headers), [2, 5, 6, 8, 10, 11])
        self.ui.ServicesTableView.horizontalHeader().resizeSection(0, 130)       # resize IP 

        # scripts table (right)
        headers = ["Id", "Script", "Port", "Protocol"]
        setTableProperties(self.ui.ScriptsTableView, len(headers), [0, 3])

        # tool hosts table (right)
        headers = ["Progress", "Display", "Pid", "Name", "Action", "Target", "Port", "Protocol", "Command", "Start time", "OutputFile", "Output", "Status"]
        setTableProperties(self.ui.ToolHostsTableView, len(headers), [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12])
        self.ui.ToolHostsTableView.horizontalHeader().resizeSection(5,150)      # default width for Host column
    
        # process table
        headers = ["Progress", "Elapsed", "Est. Remaining", "Display", "Pid", "Name", "Tool", "Host", "Port", "Protocol", "Command", "Start time", "OutputFile", "Output", "Status"]
        setTableProperties(self.ui.ProcessesTableView, len(headers), [1, 2, 3, 4, 5, 8, 9, 10, 13, 14, 16])
        self.ui.ProcessesTableView.setSortingEnabled(True)

    def setMainWindowTitle(self, title):
        self.ui_mainwindow.setWindowTitle(str(title))

    def yesNoDialog(self, message, title):
        dialog = QtWidgets.QMessageBox.question(self.ui.centralwidget, title, message, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        return dialog
        
    def setDirty(self, status=True):                                    # this function is called for example when the user edits notes
        self.dirty = status     
        title = ''
        
        if self.dirty:
            title = '*'
        if self.controller.isTempProject():
            title += 'untitled'
        else:
            title += ntpath.basename(str(self.controller.getProjectName()))
        
        self.setMainWindowTitle(self.controller.name + ' ' + self.controller.getVersion() + ' - ' + title + ' - ' + self.controller.getCWD())
        
    #################### ACTIONS ####################

    def connectProcessTableHeaderResize(self):
        self.ui.ProcessesTableView.horizontalHeader().sectionResized.connect(self.saveProcessHeaderWidth)

    def saveProcessHeaderWidth(self, index, oldSize, newSize):
        columnWidths = self.controller.getSettings().gui_process_tab_column_widths.split(',')
        difference = abs(int(columnWidths[index]) - newSize)
        if difference >= 5:
            columnWidths[index] = str(newSize)
            self.controller.settings.gui_process_tab_column_widths = ','.join(columnWidths)
            self.controller.applySettings(self.controller.settings)

    def dealWithRunningProcesses(self, exiting=False):
        if len(self.controller.getRunningProcesses()) > 0:
            message = "There are still processes running. If you continue, every process will be terminated. Are you sure you want to continue?"
            reply = self.yesNoDialog(message, 'Confirm')
                    
            if not reply == QtWidgets.QMessageBox.Yes:
                return False
            self.controller.killRunningProcesses()
        
        elif exiting:
            return self.confirmExit()
        
        return True

    def dealWithCurrentProject(self, exiting=False):                    # returns True if we can proceed with: creating/opening a project or exiting
        if self.dirty:                                                  # if there are unsaved changes, show save dialog first
            if not self.saveOrDiscard():                                # if the user canceled, stop
                return False
        
        return self.dealWithRunningProcesses(exiting)                   # deal with running processes

    def confirmExit(self):          
        message = "Are you sure to exit the program?"
        reply = self.yesNoDialog(message, 'Confirm')
        return (reply == QtWidgets.QMessageBox.Yes)

    def killProcessConfirmation(self):
        message = "Are you sure you want to kill the selected processes?"
        reply = self.yesNoDialog(message, 'Confirm')
        if reply == QtWidgets.QMessageBox.Yes:
            return True
        return False

    def connectCreateNewProject(self):
        self.ui.actionNew.triggered.connect(self.createNewProject)

    def createNewProject(self):
        if self.dealWithCurrentProject():
            log.info('Creating new project..')
            self.controller.createNewProject()

    def connectOpenExistingProject(self):
        self.ui.actionOpen.triggered.connect(self.openExistingProject)

    def openExistingProject(self):      
        if self.dealWithCurrentProject():
            filename = QtWidgets.QFileDialog.getOpenFileName(self.ui.centralwidget, 'Open project', self.controller.getCWD(), filter='Legion session (*.legion);; Sparta session (*.sprt)')[0]
        
            if not filename == '':                                      # check for permissions
                if not os.access(filename, os.R_OK) or not os.access(filename, os.W_OK):
                    log.info('Insufficient permissions to open this file.')
                    reply = QtWidgets.QMessageBox.warning(self.ui.centralwidget, 'Warning', "You don't have the necessary permissions on this file.", "Ok")
                    return

                if '.legion' in str(filename):
                    projectType = 'legion'
                elif '.sprt' in str(filename):
                    projectType = 'sparta'
                                
                self.controller.openExistingProject(filename, projectType)
                self.firstSave = False                                  # overwrite this variable because we are opening an existing file
                self.displayAddHostsOverlay(False)                      # do not show the overlay because the hosttableview is already populated
            else:
                log.info('No file chosen..')

    def connectSaveProject(self):
        self.ui.actionSave.triggered.connect(self.saveProject)
    
    def saveProject(self):
        self.ui.statusbar.showMessage('Saving..')
        if self.firstSave:
            self.saveProjectAs()
        else:
            log.info('Saving project..')
            self.controller.saveProject(self.lastHostIdClicked, self.ui.NotesTextEdit.toPlainText())

            self.setDirty(False)
            self.ui.statusbar.showMessage('Saved!', msecs=1000)
            log.info('Saved!')

    def connectSaveProjectAs(self):
        self.ui.actionSaveAs.triggered.connect(self.saveProjectAs)

    def saveProjectAs(self):
        self.ui.statusbar.showMessage('Saving..')
        log.info('Saving project..')

        self.controller.saveProject(self.lastHostIdClicked, self.ui.NotesTextEdit.toPlainText())        

        filename = QtWidgets.QFileDialog.getSaveFileName(self.ui.centralwidget, 'Save project as', self.controller.getCWD(), filter='Legion session (*.legion)', options=QtWidgets.QFileDialog.DontConfirmOverwrite)[0]
            
        while not filename =='':
            if not os.access(ntpath.dirname(str(filename)), os.R_OK) or not os.access(ntpath.dirname(str(filename)), os.W_OK):
                log.info('Insufficient permissions on this folder.')
                reply = QtWidgets.QMessageBox.warning(self.ui.centralwidget, 'Warning', "You don't have the necessary permissions on this folder.")
                
            else:
                if self.controller.saveProjectAs(filename):
                    break
                    
                if not str(filename).endswith('.legion'):
                    filename = str(filename) + '.legion'
                msgBox = QtWidgets.QMessageBox()
                reply = msgBox.question(self.ui.centralwidget, 'Confirm', "A file named \""+ntpath.basename(str(filename))+"\" already exists.  Do you want to replace it?", "Abort", "Replace", "", 0)
            
                if reply == 1:
                    self.controller.saveProjectAs(filename, 1)          # replace
                    break

            filename = QtWidgets.QFileDialog.getSaveFileName(self.ui.centralwidget, 'Save project as', '.', filter='Legion session (*.legion)', options=QtWidgets.QFileDialog.DontConfirmOverwrite)[0]

        if not filename == '':          
            self.setDirty(False)
            self.firstSave = False
            self.ui.statusbar.showMessage('Saved!', msecs=1000)
            self.controller.updateOutputFolder()
            log.info('Saved!')
        else:
            log.info('No file chosen..')

    def saveOrDiscard(self):
        reply = QtWidgets.QMessageBox.question(self.ui.centralwidget, 'Confirm', "The project has been modified. Do you want to save your changes?", QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Save)
        
        if reply == QtWidgets.QMessageBox.Save:
            self.saveProject()
            return True
        elif reply == QtWidgets.QMessageBox.Discard:
            return True
        else:
            return False                                                # the user cancelled
            
    def closeProject(self):
        self.ui.statusbar.showMessage('Closing project..', msecs=1000)
        self.controller.closeProject()
        self.removeToolTabs()                                           # to make them disappear from the UI
                
    def connectAddHosts(self):
        self.ui.actionAddHosts.triggered.connect(self.connectAddHostsDialog)
        
    def connectAddHostsDialog(self):
        self.adddialog.cmdAddButton.setDefault(True)   
        self.adddialog.txtHostList.setFocus(True)
        self.adddialog.validationLabel.hide()
        self.adddialog.spacer.changeSize(15, 15)
        self.adddialog.show()
        self.adddialog.cmdAddButton.clicked.connect(self.callAddHosts)
        self.adddialog.cmdCancelButton.clicked.connect(self.adddialog.close)
        
    def callAddHosts(self):
        hostListStr = str(self.adddialog.txtHostList.toPlainText()).replace(';',' ')
        nmapOptions = []
        scanMode = 'Unset'

        if validateNmapInput(hostListStr):
            self.adddialog.close()
            hostList = []
            splitTypes = [';', ' ', '\n']

            for splitType in splitTypes:
                hostListStr = hostListStr.replace(splitType, ';')

            hostList = hostListStr.split(';')
            hostList = [hostEntry for hostEntry in hostList if len(hostEntry) > 0]

            hostAddOptionControls = [self.adddialog.rdoScanOptTcpConnect, self.adddialog.rdoScanOptSynStealth, self.adddialog.rdoScanOptFin, self.adddialog.rdoScanOptNull, self.adddialog.rdoScanOptXmas, self.adddialog.rdoScanOptPingTcp, self.adddialog.rdoScanOptPingUdp, self.adddialog.rdoScanOptPingDisable, self.adddialog.rdoScanOptPingRegular, self.adddialog.rdoScanOptPingSyn, self.adddialog.rdoScanOptPingAck, self.adddialog.rdoScanOptPingTimeStamp, self.adddialog.rdoScanOptPingNetmask, self.adddialog.chkScanOptFragmentation]
            nmapOptions = []

            if self.adddialog.rdoModeOptEasy.isChecked():
                scanMode = 'Easy'
            else:
                scanMode = 'Hard'
                for hostAddOptionControl in hostAddOptionControls:
                    if hostAddOptionControl.isChecked():
                       nmapOptionValue = str(hostAddOptionControl.toolTip())
                       nmapOptionValueSplit = nmapOptionValue.split('[')
                       if len(nmapOptionValueSplit) > 1:
                           nmapOptionValue = nmapOptionValueSplit[1].replace(']','')
                           nmapOptions.append(nmapOptionValue)
                nmapOptions.append(str(self.adddialog.txtCustomOptList.text()))
            for hostListEntry in hostList:
                self.controller.addHosts(targetHosts = hostListEntry, runHostDiscovery = self.adddialog.chkDiscovery.isChecked(), runStagedNmap = self.adddialog.chkNmapStaging.isChecked(), nmapSpeed = self.adddialog.sldScanTimingSlider.value(), scanMode = scanMode, nmapOptions = nmapOptions)
            self.adddialog.cmdAddButton.clicked.disconnect()                   # disconnect all the signals from that button
        else:       
            self.adddialog.spacer.changeSize(0,0)
            self.adddialog.validationLabel.show()
            self.adddialog.cmdAddButton.clicked.disconnect()                   # disconnect all the signals from that button
            self.adddialog.cmdAddButton.clicked.connect(self.callAddHosts)

    ###
    
    def connectImportNmap(self):
        self.ui.actionImportNmap.triggered.connect(self.importNmap)

    def importNmap(self):
        self.ui.statusbar.showMessage('Importing nmap xml..', msecs=1000)
        filename = QtWidgets.QFileDialog.getOpenFileName(self.ui.centralwidget, 'Choose nmap file', self.controller.getCWD(), filter='XML file (*.xml)')[0]
        log.info('Importing nmap xml from {0}...'.format(str(filename))) 
        if not filename == '':
            if not os.access(filename, os.R_OK):                        # check for read permissions on the xml file
                log.info('Insufficient permissions to read this file.')
                reply = QtWidgets.QMessageBox.warning(self.ui.centralwidget, 'Warning', "You don't have the necessary permissions to read this file.", "Ok")
                return

            self.importProgressWidget.reset('Importing nmap..') 
            self.importProgressWidget.setProgress(5)
            self.importProgressWidget.show()
            self.controller.nmapImporter.setFilename(str(filename))
            self.controller.nmapImporter.start()
            self.controller.copyNmapXMLToOutputFolder(str(filename))
            self.importProgressWidget.show()
            
        else:
            log.info('No file chosen..')

    def connectSettings(self):
        self.ui.actionSettings.triggered.connect(self.showSettingsWidget)

    def showSettingsWidget(self):
        self.settingsWidget.resetTabIndexes()
        self.settingsWidget.show()

    def applySettings(self):
        if self.settingsWidget.applySettings():
            self.controller.applySettings(self.settingsWidget.settings)
            self.settingsWidget.hide()

    def cancelSettings(self):
        log.info('DEBUG: cancel button pressed')                            # LEO: we can use this later to test ESC button once implemented.
        self.settingsWidget.hide()
        self.controller.cancelSettings()

    def connectHelp(self):
        self.ui.actionHelp.triggered.connect(self.helpDialog.show)

    def connectConfig(self):
        self.ui.actionConfig.triggered.connect(self.configDialog.show)

    def connectAppExit(self):
        self.ui.actionExit.triggered.connect(self.appExit)  

    def appExit(self):
        if self.dealWithCurrentProject(True):                           # the parameter indicates that we are exiting the application
            self.closeProject()
            log.info('Exiting application..')
            sys.exit(0)

    ### TABLE ACTIONS ###

    def connectAddHostsOverlayClick(self):
        self.ui.addHostsOverlay.selectionChanged.connect(self.connectAddHostsDialog)

    def connectHostTableClick(self):
        self.ui.HostsTableView.clicked.connect(self.hostTableClick)

    # TODO: review - especially what tab is selected when coming from another host
    def hostTableClick(self):
        if self.ui.HostsTableView.selectionModel().selectedRows():      # get the IP address of the selected host (if any)
            row = self.ui.HostsTableView.selectionModel().selectedRows()[len(self.ui.HostsTableView.selectionModel().selectedRows())-1].row()
            ip = self.HostsTableModel.getHostIPForRow(row)
            self.ip_clicked = ip
            save = self.ui.ServicesTabWidget.currentIndex()
            self.removeToolTabs()
            self.restoreToolTabsForHost(self.ip_clicked)
            self.ui.ServicesTabWidget.setCurrentIndex(save)             # display services tab if we are coming from a dynamic tab (non-fixed)
            self.updateRightPanel(self.ip_clicked)
        else:
            self.removeToolTabs()               
            self.updateRightPanel('')

    ###
    
    def connectServiceNamesTableClick(self):
        self.ui.ServiceNamesTableView.clicked.connect(self.serviceNamesTableClick)
        
    def serviceNamesTableClick(self):
        if self.ui.ServiceNamesTableView.selectionModel().selectedRows():
            row = self.ui.ServiceNamesTableView.selectionModel().selectedRows()[len(self.ui.ServiceNamesTableView.selectionModel().selectedRows())-1].row()
            self.service_clicked = self.ServiceNamesTableModel.getServiceNameForRow(row)
            self.updatePortsByServiceTableView(self.service_clicked)
        
    ###
    
    def connectToolsTableClick(self):
        self.ui.ToolsTableView.clicked.connect(self.toolsTableClick)
        
    def toolsTableClick(self):
        if self.ui.ToolsTableView.selectionModel().selectedRows():
            row = self.ui.ToolsTableView.selectionModel().selectedRows()[len(self.ui.ToolsTableView.selectionModel().selectedRows())-1].row()
            self.tool_clicked = self.ToolsTableModel.getToolNameForRow(row)
            self.updateToolHostsTableView(self.tool_clicked)
            self.displayScreenshots(self.tool_clicked == 'screenshooter')   # if we clicked on the screenshooter we need to display the screenshot widget

        # update the updateToolHostsTableView when the user closes all the host tabs
        # TODO: this doesn't seem right
        else:
            self.updateToolHostsTableView('')
            self.ui.DisplayWidgetLayout.addWidget(self.ui.toolOutputTextView)
            
    ###
    
    def connectScriptTableClick(self):
        self.ui.ScriptsTableView.clicked.connect(self.scriptTableClick)
        
    def scriptTableClick(self):
        if self.ui.ScriptsTableView.selectionModel().selectedRows():
            row = self.ui.ScriptsTableView.selectionModel().selectedRows()[len(self.ui.ScriptsTableView.selectionModel().selectedRows())-1].row()
            self.script_clicked = self.ScriptsTableModel.getScriptDBIdForRow(row)
            self.updateScriptsOutputView(self.script_clicked)
                
    ###

    def connectToolHostsClick(self):
        self.ui.ToolHostsTableView.clicked.connect(self.toolHostsClick)

    # TODO: review / duplicate code
    def toolHostsClick(self):
        if self.ui.ToolHostsTableView.selectionModel().selectedRows():
            row = self.ui.ToolHostsTableView.selectionModel().selectedRows()[len(self.ui.ToolHostsTableView.selectionModel().selectedRows())-1].row()
            self.tool_host_clicked = self.ToolHostsTableModel.getProcessIdForRow(row)
            ip = self.ToolHostsTableModel.getIpForRow(row)
            
            if self.tool_clicked == 'screenshooter':
                filename = self.ToolHostsTableModel.getOutputfileForRow(row)
                self.ui.ScreenshotWidget.open(str(self.controller.getOutputFolder())+'/screenshots/'+str(filename))
            
            else:
                self.restoreToolTabWidget()                             # restore the tool output textview now showing in the tools display panel to its original host tool tab
                
                if self.ui.DisplayWidget.findChild(QtWidgets.QPlainTextEdit):   # remove the tool output currently in the tools display panel (if any)
                    self.ui.DisplayWidget.findChild(QtWidgets.QPlainTextEdit).setParent(None)

                tabs = []                                               # fetch tab list for this host (if any)
                if str(ip) in self.hostTabs:
                    tabs = self.hostTabs[str(ip)]
                
                for tab in tabs:                                        # place the tool output textview in the tools display panel
                    if tab.findChild(QtWidgets.QPlainTextEdit) and str(tab.findChild(QtWidgets.QPlainTextEdit).property('dbId')) == str(self.tool_host_clicked):
                        self.ui.DisplayWidgetLayout.addWidget(tab.findChild(QtWidgets.QPlainTextEdit))
                        break

    ###

    def connectAddHostClick(self):
        self.ui.AddHostButton.clicked.connect(self.connectAddHostsDialog)

    def connectAdvancedFilterClick(self):
        self.ui.FilterAdvancedButton.clicked.connect(self.advancedFilterClick)

    def advancedFilterClick(self, current):
        self.filterdialog.setCurrentFilters(self.filters.getFilters())  # to make sure we don't show filters than have been clicked but cancelled
        self.filterdialog.show()

    def updateFilter(self):
        f = self.filterdialog.getFilters()
        self.filters.apply(f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8])
        self.ui.keywordTextInput.setText(" ".join(f[8]))
        self.updateInterface()

    def updateFilterKeywords(self):
        self.filters.setKeywords(unicode(self.ui.keywordTextInput.text()).split())
        self.updateInterface()

    ###
    
    def connectTableDoubleClick(self):
        self.ui.ServicesTableView.doubleClicked.connect(self.tableDoubleClick)
        self.ui.ToolHostsTableView.doubleClicked.connect(self.tableDoubleClick)

    def tableDoubleClick(self):
        tab = self.ui.HostsTabWidget.tabText(self.ui.HostsTabWidget.currentIndex())

        if tab == 'Services':
            row = self.ui.ServicesTableView.selectionModel().selectedRows()[len(self.ui.ServicesTableView.selectionModel().selectedRows())-1].row()
            ## Missing
            ip = self.PortsByServiceTableModel.getIpForRow(row)
        elif tab == 'Tools':
            row = self.ui.ToolHostsTableView.selectionModel().selectedRows()[len(self.ui.ToolHostsTableView.selectionModel().selectedRows())-1].row()
            ## Missing
            ip = self.ToolHostsTableModel.getIpForRow(row)
        else:
            return

        hostrow = self.HostsTableModel.getRowForIp(ip)
        if hostrow is not None:
            self.ui.HostsTabWidget.setCurrentIndex(0)
            self.ui.HostsTableView.selectRow(hostrow)
            self.hostTableClick()
    
    ###
    
    def connectSwitchTabClick(self):
        self.ui.HostsTabWidget.currentChanged.connect(self.switchTabClick)

    def switchTabClick(self):
        if self.ServiceNamesTableModel:                                 # fixes bug when switching tabs at start-up 
            selectedTab = self.ui.HostsTabWidget.tabText(self.ui.HostsTabWidget.currentIndex())
        
            if selectedTab == 'Hosts':
                self.ui.ServicesTabWidget.insertTab(1,self.ui.ScriptsTab,("Scripts"))
                self.ui.ServicesTabWidget.insertTab(2,self.ui.InformationTab,("Information"))
                self.ui.ServicesTabWidget.insertTab(3,self.ui.CvesRightTab,("CVEs"))
                self.ui.ServicesTabWidget.insertTab(4,self.ui.NotesTab,("Notes"))
                self.ui.ServicesTabWidget.tabBar().setTabButton(0, QTabBar.RightSide, None)
                self.ui.ServicesTabWidget.tabBar().setTabButton(1, QTabBar.RightSide, None)
                self.ui.ServicesTabWidget.tabBar().setTabButton(2, QTabBar.RightSide, None)
                self.ui.ServicesTabWidget.tabBar().setTabButton(3, QTabBar.RightSide, None)
                self.ui.ServicesTabWidget.tabBar().setTabButton(4, QTabBar.RightSide, None)

                self.restoreToolTabWidget()
                ###
                if self.lazy_update_hosts == True:
                    self.updateHostsTableView()
                ###
                self.hostTableClick()       
                    
            elif selectedTab == 'Services':
                self.ui.ServicesTabWidget.setCurrentIndex(0)                
                self.removeToolTabs(0)                                  # remove the tool tabs
                self.controller.saveProject(self.lastHostIdClicked, self.ui.NotesTextEdit.toPlainText())
                if self.lazy_update_services == True:
                    self.updateServiceNamesTableView()
                self.serviceNamesTableClick()

            #elif  selectedTab == 'CVEs':
            #    self.ui.ServicesTabWidget.setCurrentIndex(0)
            #    self.removeToolTabs(0)                                  # remove the tool tabs
            #    self.controller.saveProject(self.lastHostIdClicked, self.ui.NotesTextEdit.toPlainText())
            #    if self.lazy_update_services == True:
            #        self.updateServiceNamesTableView()
            #    self.serviceNamesTableClick()
                
            elif selectedTab == 'Tools':
                self.updateToolsTableView()

            self.displayToolPanel(selectedTab == 'Tools')               # display tool panel if we are in tools tab, hide it otherwise
    
    ###

    def connectSwitchMainTabClick(self):
        self.ui.MainTabWidget.currentChanged.connect(self.switchMainTabClick)

    def switchMainTabClick(self):
        selectedTab = self.ui.MainTabWidget.tabText(self.ui.MainTabWidget.currentIndex())
        
        if selectedTab == 'Scan':
            self.switchTabClick()
        
        elif selectedTab == 'Brute':
            self.ui.BruteTabWidget.currentWidget().runButton.setFocus()
            self.restoreToolTabWidget()
        
        self.ui.MainTabWidget.tabBar().setTabTextColor(1, QtGui.QColor())       # in case the Brute tab was red because hydra found stuff, change it back to black

    ###
    def setVisible(self):                                               # indicates that a context menu is showing so that the ui doesn't get updated disrupting the user
        self.menuVisible = True

    def setInvisible(self):                                             # indicates that a context menu has now closed and any pending ui updates can take place now
        self.menuVisible = False
    ###
    
    def connectHostsTableContextMenu(self):
        self.ui.HostsTableView.customContextMenuRequested.connect(self.contextMenuHostsTableView)

    def contextMenuHostsTableView(self, pos):
        if len(self.ui.HostsTableView.selectionModel().selectedRows()) > 0:
            row = self.ui.HostsTableView.selectionModel().selectedRows()[len(self.ui.HostsTableView.selectionModel().selectedRows())-1].row()
            self.ip_clicked = self.HostsTableModel.getHostIPForRow(row) # because when we right click on a different host, we need to select it
            self.ui.HostsTableView.selectRow(row)                       # select host when right-clicked
            self.hostTableClick()           
            
            menu, actions = self.controller.getContextMenuForHost(str(self.HostsTableModel.getHostCheckStatusForRow(row)))          
            menu.aboutToShow.connect(self.setVisible)
            menu.aboutToHide.connect(self.setInvisible)
            hostid = self.HostsTableModel.getHostIdForRow(row)
            action = menu.exec_(self.ui.HostsTableView.viewport().mapToGlobal(pos))

            if action:
                self.controller.handleHostAction(self.ip_clicked, hostid, actions, action)
    
    ###

    def connectServiceNamesTableContextMenu(self):
        self.ui.ServiceNamesTableView.customContextMenuRequested.connect(self.contextMenuServiceNamesTableView)

    def contextMenuServiceNamesTableView(self, pos):
        if len(self.ui.ServiceNamesTableView.selectionModel().selectedRows()) > 0:
            row = self.ui.ServiceNamesTableView.selectionModel().selectedRows()[len(self.ui.ServiceNamesTableView.selectionModel().selectedRows())-1].row()
            self.service_clicked = self.ServiceNamesTableModel.getServiceNameForRow(row)
            self.ui.ServiceNamesTableView.selectRow(row)                # select service when right-clicked
            self.serviceNamesTableClick()

            menu, actions, shiftPressed = self.controller.getContextMenuForServiceName(self.service_clicked)
            menu.aboutToShow.connect(self.setVisible)
            menu.aboutToHide.connect(self.setInvisible)
            action = menu.exec_(self.ui.ServiceNamesTableView.viewport().mapToGlobal(pos))

            if action:                                                                  
                self.serviceNamesTableClick()                           # because we will need to populate the right-side panel in order to select those rows
                                                                        # we must only fetch the targets on which we haven't run the tool yet               
                tool = None
                for i in range(0,len(actions)):                         # fetch the tool name
                    if action == actions[i][1]:
                        srvc_num = actions[i][0]
                        tool = self.controller.getSettings().portActions[srvc_num][1]
                        break

                if action.text() == 'Take screenshot':
                    tool = 'screenshooter'
                        
                targets = []                                            # get (IP,port,protocol) combinations for this service
                for row in range(self.PortsByServiceTableModel.rowCount("")):
                    targets.append([self.PortsByServiceTableModel.getIpForRow(row), self.PortsByServiceTableModel.getPortForRow(row), self.PortsByServiceTableModel.getProtocolForRow(row)])

                if shiftPressed:                                        # if the user pressed SHIFT+Right-click, ignore the rule of only running the tool on targets on which we haven't ran it yet
                    tool=None

                if tool:
                    hosts=self.controller.getHostsForTool(tool, 'FetchAll') # fetch the hosts that we already ran the tool on
                    oldTargets = []
                    for i in range(0,len(hosts)):
                        oldTargets.append([hosts[i][5], hosts[i][6], hosts[i][7]])
                        
                    for host in oldTargets:                             # remove from the targets the hosts:ports we have already run the tool on
                        if host in targets:
                            targets.remove(host)
                
                self.controller.handleServiceNameAction(targets, actions, action)

    ###
    
    def connectToolHostsTableContextMenu(self):
        self.ui.ToolHostsTableView.customContextMenuRequested.connect(self.contextToolHostsTableContextMenu)

    def contextToolHostsTableContextMenu(self, pos):
        if len(self.ui.ToolHostsTableView.selectionModel().selectedRows()) > 0:
            
            row = self.ui.ToolHostsTableView.selectionModel().selectedRows()[len(self.ui.ToolHostsTableView.selectionModel().selectedRows())-1].row()
            ip = self.ToolHostsTableModel.getIpForRow(row)
            port = self.ToolHostsTableModel.getPortForRow(row)
            
            if port:
                serviceName = self.controller.getServiceNameForHostAndPort(ip, port)[0]

                menu, actions, terminalActions = self.controller.getContextMenuForPort(str(serviceName))
                menu.aboutToShow.connect(self.setVisible)
                menu.aboutToHide.connect(self.setInvisible)
     
                                                                        # this can handle multiple host selection if we apply it in the future
                targets = []                                            # get (IP,port,protocol,serviceName) combinations for each selected row                                 # context menu when the left services tab is selected
                for row in self.ui.ToolHostsTableView.selectionModel().selectedRows():
                    targets.append([self.ToolHostsTableModel.getIpForRow(row.row()),self.ToolHostsTableModel.getPortForRow(row.row()),self.ToolHostsTableModel.getProtocolForRow(row.row()),self.controller.getServiceNameForHostAndPort(self.ToolHostsTableModel.getIpForRow(row.row()), self.ToolHostsTableModel.getPortForRow(row.row()))[0]])
                    restore = True

                action = menu.exec_(self.ui.ToolHostsTableView.viewport().mapToGlobal(pos))
     
                if action:                  
                    self.controller.handlePortAction(targets, actions, terminalActions, action, restore)    
            
            else:                                                       # in case there was no port, we show the host menu (without the portscan / mark as checked)
                menu, actions = self.controller.getContextMenuForHost(str(self.HostsTableModel.getHostCheckStatusForRow(self.HostsTableModel.getRowForIp(ip))), False)
                menu.aboutToShow.connect(self.setVisible)
                menu.aboutToHide.connect(self.setInvisible)
                hostid = self.HostsTableModel.getHostIdForRow(self.HostsTableModel.getRowForIp(ip))

                action = menu.exec_(self.ui.ToolHostsTableView.viewport().mapToGlobal(pos))

                if action:
                    self.controller.handleHostAction(self.ip_clicked, hostid, actions, action)              
    
    ###

    def connectServicesTableContextMenu(self):
        self.ui.ServicesTableView.customContextMenuRequested.connect(self.contextMenuServicesTableView)

    def contextMenuServicesTableView(self, pos):                        # this function is longer because there are two cases we are in the services table
        if len(self.ui.ServicesTableView.selectionModel().selectedRows()) > 0:
            
            if len(self.ui.ServicesTableView.selectionModel().selectedRows()) == 1:     # if there is only one row selected, get service name
                row = self.ui.ServicesTableView.selectionModel().selectedRows()[len(self.ui.ServicesTableView.selectionModel().selectedRows())-1].row()
                
                if self.ui.ServicesTableView.isColumnHidden(0):         # if we are in the services tab of the hosts view
                    serviceName = self.ServicesTableModel.getServiceNameForRow(row)
                else:                                                   # if we are in the services tab of the services view
                    serviceName = self.PortsByServiceTableModel.getServiceNameForRow(row)
                    
            else:
                serviceName = '*'                                       # otherwise show full menu
                
            menu, actions, terminalActions = self.controller.getContextMenuForPort(serviceName)         
            menu.aboutToShow.connect(self.setVisible)
            menu.aboutToHide.connect(self.setInvisible)

            targets = []                                                # get (IP,port,protocol,serviceName) combinations for each selected row
            if self.ui.ServicesTableView.isColumnHidden(0):
                for row in self.ui.ServicesTableView.selectionModel().selectedRows():
                    targets.append([self.ServicesTableModel.getIpForRow(row.row()),self.ServicesTableModel.getPortForRow(row.row()),self.ServicesTableModel.getProtocolForRow(row.row()),self.ServicesTableModel.getServiceNameForRow(row.row())])
                    restore = False
            
            else:                                                       # context menu when the left services tab is selected
                for row in self.ui.ServicesTableView.selectionModel().selectedRows():
                    targets.append([self.PortsByServiceTableModel.getIpForRow(row.row()),self.PortsByServiceTableModel.getPortForRow(row.row()),self.PortsByServiceTableModel.getProtocolForRow(row.row()),self.PortsByServiceTableModel.getServiceNameForRow(row.row())])
                    restore = True

            action = menu.exec_(self.ui.ServicesTableView.viewport().mapToGlobal(pos))

            if action:                  
                self.controller.handlePortAction(targets, actions, terminalActions, action, restore)
    
    ###

    def connectProcessesTableContextMenu(self):
        self.ui.ProcessesTableView.customContextMenuRequested.connect(self.contextMenuProcessesTableView)

    def contextMenuProcessesTableView(self, pos):
        if self.ui.ProcessesTableView.selectionModel() and self.ui.ProcessesTableView.selectionModel().selectedRows():
    
            menu = self.controller.getContextMenuForProcess()
            menu.aboutToShow.connect(self.setVisible)
            menu.aboutToHide.connect(self.setInvisible)

            selectedProcesses = []                                  # list of tuples (pid, status, procId)
            for row in self.ui.ProcessesTableView.selectionModel().selectedRows():
                pid = self.ProcessesTableModel.getProcessPidForRow(row.row())
                selectedProcesses.append([int(pid), self.ProcessesTableModel.getProcessStatusForRow(row.row()), self.ProcessesTableModel.getProcessIdForRow(row.row())])

            action = menu.exec_(self.ui.ProcessesTableView.viewport().mapToGlobal(pos))

            if action:                                      
                self.controller.handleProcessAction(selectedProcesses, action)

    ###
    
    def connectScreenshotContextMenu(self):
        self.ui.ScreenshotWidget.scrollArea.customContextMenuRequested.connect(self.contextMenuScreenshot)

    def contextMenuScreenshot(self, pos):
        menu = QMenu()

        zoomInAction = menu.addAction("Zoom in (25%)")
        zoomOutAction = menu.addAction("Zoom out (25%)")
        fitToWindowAction = menu.addAction("Fit to window")
        normalSizeAction = menu.addAction("Original size")

        menu.aboutToShow.connect(self.setVisible)
        menu.aboutToHide.connect(self.setInvisible)
        
        action = menu.exec_(self.ui.ScreenshotWidget.scrollArea.viewport().mapToGlobal(pos))

        if action == zoomInAction:
            self.ui.ScreenshotWidget.zoomIn()
        elif action == zoomOutAction:
            self.ui.ScreenshotWidget.zoomOut()
        elif action == fitToWindowAction:
            self.ui.ScreenshotWidget.fitToWindow()
        elif action == normalSizeAction:
            self.ui.ScreenshotWidget.normalSize()
            
    #################### LEFT PANEL INTERFACE UPDATE FUNCTIONS ####################

    def updateHostsTableView(self): 
        headers = ["Id", "OS", "Accuracy", "Host", "IPv4", "IPv6", "Mac", "Status", "Hostname", "Vendor", "Uptime", "Lastboot", "Distance", "CheckedHost", "State", "Count", "Padding"]
        self.HostsTableModel = HostsTableModel(self.controller.getHostsFromDB(self.filters), headers)
        self.ui.HostsTableView.setModel(self.HostsTableModel)

        self.lazy_update_hosts = False                                  # to indicate that it doesn't need to be updated anymore

        for i in [0,2,4,5,6,7,8,9,10,11,12,13,14,15,16]:                   # hide some columns
            self.ui.HostsTableView.setColumnHidden(i, True)

        self.ui.HostsTableView.horizontalHeader().resizeSection(1,30)
        self.HostsTableModel.sort(3, Qt.DescendingOrder)

        ips = []                                                        # ensure that there is always something selected
        for row in range(self.HostsTableModel.rowCount("")):
            ips.append(self.HostsTableModel.getHostIPForRow(row))

        if self.ip_clicked in ips:                                      # the ip we previously clicked may not be visible anymore (eg: due to filters)
            row = self.HostsTableModel.getRowForIp(self.ip_clicked)
        else:
            row = 0                                                     # or select the first row
            
        if not row == None:
            self.ui.HostsTableView.selectRow(row)
            self.hostTableClick()

    def updateServiceNamesTableView(self):
        headers = ["Name"]
        self.ServiceNamesTableModel = ServiceNamesTableModel(self.controller.getServiceNamesFromDB(self.filters), headers)
        self.ui.ServiceNamesTableView.setModel(self.ServiceNamesTableModel)

        self.lazy_update_services = False                               # to indicate that it doesn't need to be updated anymore

        services = []                                                   # ensure that there is always something selected
        for row in range(self.ServiceNamesTableModel.rowCount("")):
            services.append(self.ServiceNamesTableModel.getServiceNameForRow(row))
        
        if self.service_clicked in services:                            # the service we previously clicked may not be visible anymore (eg: due to filters)
            row = self.ServiceNamesTableModel.getRowForServiceName(self.service_clicked)
        else:
            row = 0                                                     # or select the first row
            
        if not row == None:
            self.ui.ServiceNamesTableView.selectRow(row)
            self.serviceNamesTableClick()

    def setupToolsTableView(self):
        headers = ["Progress", "Display", "Elapsed", "Est. Remaining", "Pid", "Name", "Tool", "Host", "Port", "Protocol", "Command", "Start time", "End time", "OutputFile", "Output", "Status", "Closed"]
        self.ToolsTableModel = ProcessesTableModel(self,self.controller.getProcessesFromDB(self.filters, showProcesses = 'noNmap', sort = self.toolsTableViewSort, ncol = self.toolsTableViewSortColumn), headers)
        self.ui.ToolsTableView.setModel(self.ToolsTableModel)

    def updateToolsTableView(self):
        if self.ui.MainTabWidget.tabText(self.ui.MainTabWidget.currentIndex()) == 'Scan' and self.ui.HostsTabWidget.tabText(self.ui.HostsTabWidget.currentIndex()) == 'Tools':
            headers = ["Progress", "Display", "Elapsed", "Est. Remaining", "Pid", "Name", "Tool", "Host", "Port", "Protocol", "Command", "Start time", "End time", "OutputFile", "Output", "Status", "Closed"]
            self.ToolsTableModel.setDataList(self.controller.getProcessesFromDB(self.filters, showProcesses = 'noNmap', sort = self.toolsTableViewSort, ncol = self.toolsTableViewSortColumn))
            self.ui.ToolsTableView.repaint()
            self.ui.ToolsTableView.update()

            self.lazy_update_tools = False                              # to indicate that it doesn't need to be updated anymore

            # Hides columns we don't want to see
            for i in [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]:                # hide some columns
                self.ui.ToolsTableView.setColumnHidden(i, True)
                    
            tools = []                                                  # ensure that there is always something selected
            for row in range(self.ToolsTableModel.rowCount("")):
                tools.append(self.ToolsTableModel.getToolNameForRow(row))

            if self.tool_clicked in tools:                              # the tool we previously clicked may not be visible anymore (eg: due to filters)
                row = self.ToolsTableModel.getRowForToolName(self.tool_clicked)
            else:
                row = 0                                                 # or select the first row
                
            if not row == None:
                self.ui.ToolsTableView.selectRow(row)
                self.toolsTableClick()
        
    #################### RIGHT PANEL INTERFACE UPDATE FUNCTIONS ####################
    
    def updateServiceTableView(self, hostIP):
        headers = ["Host", "Port", "Port", "Protocol", "State", "HostId", "ServiceId", "Name", "Product", "Version", "Extrainfo", "Fingerprint"]
        self.ServicesTableModel = ServicesTableModel(self.controller.getPortsAndServicesForHostFromDB(hostIP, self.filters), headers)
        self.ui.ServicesTableView.setModel(self.ServicesTableModel)

        for i in range(0, len(headers)):                                # reset all the hidden columns
                self.ui.ServicesTableView.setColumnHidden(i, False)

        for i in [0,1,5,6,8,10,11]:                                     # hide some columns
            self.ui.ServicesTableView.setColumnHidden(i, True)      
        
        self.ServicesTableModel.sort(2, Qt.DescendingOrder)             # sort by port by default (override default)

    def updatePortsByServiceTableView(self, serviceName):
        headers = ["Host", "Port", "Port", "Protocol", "State", "HostId", "ServiceId", "Name", "Product", "Version", "Extrainfo", "Fingerprint"]
        self.PortsByServiceTableModel = ServicesTableModel(self.controller.getHostsAndPortsForServiceFromDB(serviceName, self.filters), headers)
        self.ui.ServicesTableView.setModel(self.PortsByServiceTableModel)

        for i in range(0, len(headers)):                                # reset all the hidden columns
                self.ui.ServicesTableView.setColumnHidden(i, False)

        for i in [2,5,6,7,8,10,11]:                                     # hide some columns
            self.ui.ServicesTableView.setColumnHidden(i, True)              
        
        self.ui.ServicesTableView.horizontalHeader().resizeSection(0,165)   # resize IP
        self.ui.ServicesTableView.horizontalHeader().resizeSection(1,65)    # resize port
        self.ui.ServicesTableView.horizontalHeader().resizeSection(3,100)   # resize protocol
        self.PortsByServiceTableModel.sort(0, Qt.DescendingOrder)           # sort by IP by default (override default)

    def updateInformationView(self, hostIP):

        if hostIP:
            host = self.controller.getHostInformation(hostIP)
            
            if host:                    
                states = self.controller.getPortStatesForHost(host.id)
                counterOpen = counterClosed = counterFiltered = 0

                for s in states:
                    if s[0] == 'open':
                        counterOpen+=1
                    elif s[0] == 'closed':
                        counterClosed+=1
                    else:
                        counterFiltered+=1
                
                if host.state == 'closed':                              # check the extra ports
                    counterClosed = 65535 - counterOpen - counterFiltered
                else:
                    counterFiltered = 65535 - counterOpen - counterClosed

                self.hostInfoWidget.updateFields(status=host.status, openPorts=counterOpen, closedPorts=counterClosed, filteredPorts=counterFiltered, ipv4=host.ipv4, ipv6=host.ipv6, macaddr=host.macaddr, osMatch=host.os_match, osAccuracy=host.os_accuracy)

    def updateScriptsView(self, hostIP):
        headers = ["Id", "Script", "Port", "Protocol"]
        self.ScriptsTableModel = ScriptsTableModel(self,self.controller.getScriptsFromDB(hostIP), headers)
        self.ui.ScriptsTableView.setModel(self.ScriptsTableModel)

        for i in [0,3]:                                                 # hide some columns
            self.ui.ScriptsTableView.setColumnHidden(i, True)
    
        scripts = []                                                    # ensure that there is always something selected
        for row in range(self.ScriptsTableModel.rowCount("")):
            scripts.append(self.ScriptsTableModel.getScriptDBIdForRow(row))

        if self.script_clicked in scripts:                              # the script we previously clicked may not be visible anymore (eg: due to filters)
            row = self.ScriptsTableModel.getRowForDBId(self.script_clicked)

        else:
            row = 0                                                     # or select the first row
            
        if not row == None:
            self.ui.ScriptsTableView.selectRow(row)
            self.scriptTableClick()

    def updateCvesByHostView(self, hostIP):
        headers = ["ID", "CVSS Score", "Product", "Version", "URL", "Source"]
        cves = self.controller.getCvesFromDB(hostIP)
        self.CvesTableModel = CvesTableModel(self,self.controller.getCvesFromDB(hostIP), headers)

        self.ui.CvesTableView.horizontalHeader().resizeSection(0,175)
        self.ui.CvesTableView.horizontalHeader().resizeSection(2,175)
        self.ui.CvesTableView.horizontalHeader().resizeSection(4,225)

        self.ui.CvesTableView.setModel(self.CvesTableModel)
        self.ui.CvesTableView.repaint()
        self.ui.CvesTableView.update()

    def updateScriptsOutputView(self, scriptId):
        self.ui.ScriptsOutputTextEdit.clear()
        lines = self.controller.getScriptOutputFromDB(scriptId)
        for l in lines:
            self.ui.ScriptsOutputTextEdit.insertPlainText(l.output.rstrip())

    # TODO: check if this hack can be improved because we are calling setDirty more than we need
    def updateNotesView(self, hostid):
        self.lastHostIdClicked = str(hostid)
        note = self.controller.getNoteFromDB(hostid)
        
        saved_dirty = self.dirty                                        # save the status so we can restore it after we update the note panel
        self.ui.NotesTextEdit.clear()                                   # clear the text box from the previous notes
            
        if note:
            self.ui.NotesTextEdit.insertPlainText(note.text)
        
        if saved_dirty == False:
            self.setDirty(False)

    def updateToolHostsTableView(self, toolname):
        headers = ["Progress", "Display", "Elapsed", "Est. Remaining", "Pid", "Name", "Tool", "Host", "Port", "Protocol", "Command", "Start time", "End time", "OutputFile", "Output", "Status", "Closed"]
        self.ToolHostsTableModel = ProcessesTableModel(self, self.controller.getHostsForTool(toolname), headers)
        self.ui.ToolHostsTableView.setModel(self.ToolHostsTableModel)

        for i in [0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15]:                         # hide some columns
            self.ui.ToolHostsTableView.setColumnHidden(i, True)
        
        self.ui.ToolHostsTableView.horizontalHeader().resizeSection(7, 150)  # default width for Host column

        ids = []                                                        # ensure that there is always something selected
        for row in range(self.ToolHostsTableModel.rowCount("")):
            ids.append(self.ToolHostsTableModel.getProcessIdForRow(row))

        if self.tool_host_clicked in ids:                               # the host we previously clicked may not be visible anymore (eg: due to filters)
            row = self.ToolHostsTableModel.getRowForDBId(self.tool_host_clicked)

        else:
            row = 0                                                     # or select the first row

        if not row == None and self.ui.HostsTabWidget.tabText(self.ui.HostsTabWidget.currentIndex()) == 'Tools':
            self.ui.ToolHostsTableView.selectRow(row)
            self.toolHostsClick()


    def updateRightPanel(self, hostIP):
        self.updateServiceTableView(hostIP)
        self.updateScriptsView(hostIP)
        self.updateCvesByHostView(hostIP)
        self.updateInformationView(hostIP)                              # populate host info tab
        self.controller.saveProject(self.lastHostIdClicked, self.ui.NotesTextEdit.toPlainText())

        if hostIP:
            self.updateNotesView(self.HostsTableModel.getHostIdForRow(self.HostsTableModel.getRowForIp(hostIP)))
        else:
            self.updateNotesView('')        
            
    def displayToolPanel(self, display=False):
        size = self.ui.splitter.parentWidget().width() - self.leftPanelSize - 24       # note: 24 is a fixed value
        if display:
            self.ui.ServicesTabWidget.hide()
            self.ui.splitter_3.show()
            self.ui.splitter.setSizes([self.leftPanelSize, 0, size])                     # reset hoststableview width
            
            if self.tool_clicked == 'screenshooter':
                self.displayScreenshots(True)
            else:
                self.displayScreenshots(False)
                #self.ui.splitter_3.setSizes([275,size-275,0])          # reset middle panel width      

        else:
            self.ui.splitter_3.hide()
            self.ui.ServicesTabWidget.show()
            self.ui.splitter.setSizes([self.leftPanelSize, size, 0])

    def displayScreenshots(self, display=False):
        size = self.ui.splitter.parentWidget().width() - self.leftPanelSize - 24       # note: 24 is a fixed value

        if display:
            self.ui.DisplayWidget.hide()
            self.ui.ScreenshotWidget.scrollArea.show()
            self.ui.splitter_3.setSizes([275, 0, size - 275])               # reset middle panel width  

        else:
            self.ui.ScreenshotWidget.scrollArea.hide()
            self.ui.DisplayWidget.show()
            self.ui.splitter_3.setSizes([275, size - 275, 0])               # reset middle panel width  

    def displayAddHostsOverlay(self, display=False):
        if display:
            self.ui.addHostsOverlay.show()
            self.ui.HostsTableView.hide()
        else:
            self.ui.addHostsOverlay.hide()
            self.ui.HostsTableView.show()
            
    #################### BOTTOM PANEL INTERFACE UPDATE FUNCTIONS ####################       

    def setupProcessesTableView(self):
        headers = ["Progress", "Display", "Elapsed", "Est. Remaining", "Pid", "Name", "Tool", "Host", "Port", "Protocol", "Command", "Start time", "End time", "OutputFile", "Output", "Status", "Closed"]
        self.ProcessesTableModel = ProcessesTableModel(self,self.controller.getProcessesFromDB(self.filters, showProcesses = True, sort = self.processesTableViewSort, ncol = self.processesTableViewSortColumn), headers)
        self.ui.ProcessesTableView.setModel(self.ProcessesTableModel)
        self.ProcessesTableModel.sort(15, Qt.DescendingOrder)
        
    def updateProcessesTableView(self):
        headers = ["Progress", "Display", "Elapsed", "Est. Remaining", "Pid", "Name", "Tool", "Host", "Port", "Protocol", "Command", "Start time", "End time", "OutputFile", "Output", "Status", "Closed"]
        self.ProcessesTableModel.setDataList(self.controller.getProcessesFromDB(self.filters, showProcesses = True, sort = self.processesTableViewSort, ncol = self.processesTableViewSortColumn))
        self.ui.ProcessesTableView.repaint()
        self.ui.ProcessesTableView.update()

        # load the column widths from settings to persist widths between sessions
        columnWidths = self.controller.getSettings().gui_process_tab_column_widths.split(',')
        header = self.ui.ProcessesTableView.horizontalHeader()
        for index, width in enumerate(columnWidths):
            header.resizeSection(index, int(width))

        #Hides columns we don't want to see
        showDetail = self.controller.settings.gui_process_tab_detail
        if showDetail ==  True:
            columnsToHide = [1, 5, 8, 9, 12, 14, 16]
        else:
            columnsToHide = [1, 5, 8, 9, 10, 11, 12, 13, 14, 16]
        for i in columnsToHide:
            self.ui.ProcessesTableView.setColumnHidden(i, True)
        
        # Force size of progress animation    
        self.ui.ProcessesTableView.horizontalHeader().resizeSection(0, 125)
        self.ui.ProcessesTableView.horizontalHeader().resizeSection(15, 125)

        # Update animations
        self.updateProcessesIcon()

    def updateProcessesIcon(self):
        if self.ProcessesTableModel:
            for row in range(len(self.ProcessesTableModel.getProcesses())):
                status = self.ProcessesTableModel.getProcesses()[row].status
                
                directStatus = {'Waiting':'waiting', 'Running':'running', 'Finished':'finished', 'Crashed':'killed'}
                defaultStatus = 'killed'

                processIconName = directStatus.get(status) or defaultStatus
                processIcon = './images/{processIconName}.gif'.format(processIconName=processIconName)

                self.runningWidget = ImagePlayer(processIcon)
                self.ui.ProcessesTableView.setIndexWidget(self.ui.ProcessesTableView.model().index(row,0), self.runningWidget)

    #################### GLOBAL INTERFACE UPDATE FUNCTION ####################
    
    # TODO: when nmap file is imported select last IP clicked (or first row if none)
    def updateInterface(self):
        self.ui_mainwindow.show()
        
        if self.ui.HostsTabWidget.tabText(self.ui.HostsTabWidget.currentIndex()) == 'Hosts':
            self.updateHostsTableView()
            self.lazy_update_services = True
            self.lazy_update_tools = True
            
        if self.ui.HostsTabWidget.tabText(self.ui.HostsTabWidget.currentIndex()) == 'Services':
            self.updateServiceNamesTableView()
            self.lazy_update_hosts = True
            self.lazy_update_tools = True           
            
        if self.ui.HostsTabWidget.tabText(self.ui.HostsTabWidget.currentIndex()) == 'Tools':        
            self.updateToolsTableView()
            self.lazy_update_hosts = True
            self.lazy_update_services = True
        
    #################### TOOL TABS ####################

    # this function creates a new tool tab for a given host
    # TODO: refactor/review, especially the restoring part. we should not check if toolname=nmap everywhere in the code
    # ..maybe we should do it here. rethink
    def createNewTabForHost(self, ip, tabtitle, restoring=False, content='', filename=''):
    
        if 'screenshot' in str(tabtitle):       # TODO: use regex otherwise tools with 'screenshot' in the name are screwed.    
            tempWidget = ImageViewer()
            tempWidget.setObjectName(str(tabtitle))
            tempWidget.open(str(filename))
            tempTextView = tempWidget.scrollArea
            tempTextView.setObjectName(str(tabtitle))
        else:
            tempWidget = QtWidgets.QWidget()
            tempWidget.setObjectName(str(tabtitle))
            tempTextView = QtWidgets.QPlainTextEdit(tempWidget)
            tempTextView.setReadOnly(True)
            if self.controller.getSettings().general_tool_output_black_background == 'True':
                p = tempTextView.palette()
                p.setColor(QtGui.QPalette.Base, Qt.black)               # black background
                p.setColor(QtGui.QPalette.Text, Qt.white)               # white font
                tempTextView.setPalette(p)
                tempTextView.setStyleSheet("QMenu { color:black;}")     #font-size:18px; width: 150px; color:red; left: 20px;}"); # set the menu font color: black
            tempLayout = QtWidgets.QHBoxLayout(tempWidget)
            tempLayout.addWidget(tempTextView)
        
            if not content == '':                                       # if there is any content to display
                tempTextView.appendPlainText(content)

        if restoring == False:                                          # if restoring tabs (after opening a project) don't show the tab in the ui
            tabindex = self.ui.ServicesTabWidget.addTab(tempWidget, str(tabtitle))
    
        hosttabs = []                                                   # fetch tab list for this host (if any)
        if str(ip) in self.hostTabs:
            hosttabs = self.hostTabs[str(ip)]
        
        if 'screenshot' in str(tabtitle):
            hosttabs.append(tempWidget.scrollArea)                      # add the new tab to the list
        else:
            hosttabs.append(tempWidget)                                 # add the new tab to the list
        
        self.hostTabs.update({str(ip):hosttabs})

        return tempTextView


    def createNewConsole(self, tabtitle, content='Hello\n', filename=''):

        tempWidget = QtWidgets.QWidget()
        tempWidget.setObjectName(str(tabtitle))
        tempTextView = QtWidgets.QPlainTextEdit(tempWidget)
        tempTextView.setReadOnly(True)
        if self.controller.getSettings().general_tool_output_black_background == 'True':
            p = tempTextView.palette()
            p.setColor(QtGui.QPalette.Base, Qt.black)               # black background
            p.setColor(QtGui.QPalette.Text, Qt.white)               # white font
            tempTextView.setPalette(p)
            tempTextView.setStyleSheet("QMenu { color:black;}")     #font-size:18px; width: 150px; color:red; left: 20px;}"); # set the menu font color: black
        tempLayout = QtWidgets.QHBoxLayout(tempWidget)
        tempLayout.addWidget(tempTextView)
        self.ui.PythonTabLayout.addWidget(tempWidget)

        if not content == '':                                       # if there is any content to display
            tempTextView.appendPlainText(content)


        return tempTextView

    def closeHostToolTab(self, index):      
        currentTabIndex = self.ui.ServicesTabWidget.currentIndex()      # remember the currently selected tab
        self.ui.ServicesTabWidget.setCurrentIndex(index)                # select the tab for which the cross button was clicked

        currentWidget = self.ui.ServicesTabWidget.currentWidget()
        if 'screenshot' in str(self.ui.ServicesTabWidget.currentWidget().objectName()):
            dbId = int(currentWidget.property('dbId'))
        else:       
            dbId = int(currentWidget.findChild(QtWidgets.QPlainTextEdit).property('dbId'))
        
        pid = int(self.controller.getPidForProcess(dbId))               # the process ID (=os)

        if str(self.controller.getProcessStatusForDBId(dbId)) == 'Running':
            message = "This process is still running. Are you sure you want to kill it?"
            reply = self.yesNoDialog(message, 'Confirm')
            if reply == QtWidgets.QMessageBox.Yes:
                self.controller.killProcess(pid, dbId)
            else:
                return
        
        # TODO: duplicate code      
        if str(self.controller.getProcessStatusForDBId(dbId)) == 'Waiting':
            message = "This process is waiting to start. Are you sure you want to cancel it?"
            reply = self.yesNoDialog(message, 'Confirm')
            if reply == QtWidgets.QMessageBox.Yes:
                self.controller.cancelProcess(dbId)
            else:
                return

        # remove tab from host tabs list
        hosttabs = []
        for ip in self.hostTabs.keys():
            if self.ui.ServicesTabWidget.currentWidget() in self.hostTabs[ip]:
                hosttabs = self.hostTabs[ip]
                hosttabs.remove(self.ui.ServicesTabWidget.currentWidget())
                self.hostTabs.update({ip:hosttabs})
                break

        self.controller.storeCloseTabStatusInDB(dbId)                   # update the closed status in the db - getting the dbid 
        self.ui.ServicesTabWidget.removeTab(index)                      # remove the tab
        
        if currentTabIndex >= self.ui.ServicesTabWidget.currentIndex():     # select the initially selected tab
            self.ui.ServicesTabWidget.setCurrentIndex(currentTabIndex - 1)  # all the tab indexes shift if we remove a tab index smaller than the current tab index
        else:
            self.ui.ServicesTabWidget.setCurrentIndex(currentTabIndex)  

    # this function removes tabs that were created when running tools (starting from the end to avoid index problems)
    def removeToolTabs(self, position=-1):
        if position == -1:
            position = self.fixedTabsCount-1        
        for i in range(self.ui.ServicesTabWidget.count()-1, position, -1):
            self.ui.ServicesTabWidget.removeTab(i)

    # this function restores the tool tabs based on the DB content (should be called when opening an existing project).
    def restoreToolTabs(self):
        tools = self.controller.getProcessesFromDB(self.filters, showProcesses = False) # false means we are fetching processes with display flag=False, which is the case for every process once a project is closed.
        nbr = len(tools)                                                # show a progress bar because this could take long
        if nbr==0:                                          
            nbr=1
        progress = 100.0 / nbr
        totalprogress = 0
        self.tick.emit(int(totalprogress))

        for t in tools:
            if not t.tabtitle == '':
                if 'screenshot' in str(t.tabtitle):
                    imageviewer = self.createNewTabForHost(t.hostip, t.tabtitle, True, '', str(self.controller.getOutputFolder())+'/screenshots/'+str(t.outputfile))
                    imageviewer.setObjectName(str(t.tabtitle))
                    imageviewer.setProperty('dbId', str(t.id))
                else:
                    self.createNewTabForHost(t.hostip, t.tabtitle, True, t.output).setProperty('dbId', str(t.id))     # True means we are restoring tabs. Set the widget's object name to the DB id of the process

            totalprogress += progress                                   # update the progress bar
            self.tick.emit(int(totalprogress))
        
    def restoreToolTabsForHost(self, ip):
        if (self.hostTabs) and (ip in self.hostTabs):
            tabs = self.hostTabs[ip]    # use the ip as a key to retrieve its list of tooltabs
            for tab in tabs:
                # do not display hydra and nmap tabs when restoring for that host
                if not 'hydra' in tab.objectName() and not 'nmap' in tab.objectName():                  
                    tabindex = self.ui.ServicesTabWidget.addTab(tab, tab.objectName())

    # this function restores the textview widget (now in the tools display widget) to its original tool tab (under the correct host)
    def restoreToolTabWidget(self, clear=False):
        if self.ui.DisplayWidget.findChild(QtWidgets.QPlainTextEdit) == self.ui.toolOutputTextView:
            return
        
        for host in self.hostTabs.keys():
            hosttabs = self.hostTabs[host]
            for tab in hosttabs:
                if not 'screenshot' in str(tab.objectName()) and not tab.findChild(QtWidgets.QPlainTextEdit):
                    tab.layout().addWidget(self.ui.DisplayWidget.findChild(QtWidgets.QPlainTextEdit))
                    break

        if clear:
            if self.ui.DisplayWidget.findChild(QtWidgets.QPlainTextEdit):   # remove the tool output currently in the tools display panel
                self.ui.DisplayWidget.findChild(QtWidgets.QPlainTextEdit).setParent(None)
                
            self.ui.DisplayWidgetLayout.addWidget(self.ui.toolOutputTextView)

    #################### BRUTE TABS ####################
    
    def createNewBruteTab(self, ip, port, service): 
        self.ui.statusbar.showMessage('Sending to Brute: '+ip+':'+port+' ('+service+')', msecs=1000)
        bWidget = BruteWidget(ip, port, service, self.controller.getSettings())
        bWidget.runButton.clicked.connect(lambda: self.callHydra(bWidget))
        self.ui.BruteTabWidget.addTab(bWidget, str(self.bruteTabCount)) 
        self.bruteTabCount += 1                                                     # update tab count
        self.ui.BruteTabWidget.setCurrentIndex(self.ui.BruteTabWidget.count()-1)    # show the last added tab in the brute widget

    def closeBruteTab(self, index):
        currentTabIndex = self.ui.BruteTabWidget.currentIndex()         # remember the currently selected tab       
        self.ui.BruteTabWidget.setCurrentIndex(index)                   # select the tab for which the cross button was clicked
        
        if not self.ui.BruteTabWidget.currentWidget().pid == -1:        # if process is running
            if self.ProcessesTableModel.getProcessStatusForPid(self.ui.BruteTabWidget.currentWidget().pid)=="Running":
                message = "This process is still running. Are you sure you want to kill it?"
                reply = self.yesNoDialog(message, 'Confirm')
                if reply == QtWidgets.QMessageBox.Yes:
                    self.killBruteProcess(self.ui.BruteTabWidget.currentWidget())
                else:
                    return
    
        dbIdString = self.ui.BruteTabWidget.currentWidget().display.property('dbId')
        if dbIdString:
            if not dbIdString == '':
                self.controller.storeCloseTabStatusInDB(int(dbIdString))

        self.ui.BruteTabWidget.removeTab(index)                         # remove the tab
        
        if currentTabIndex >= self.ui.BruteTabWidget.currentIndex():    # select the initially selected tab
            self.ui.BruteTabWidget.setCurrentIndex(currentTabIndex - 1) # all the tab indexes shift if we remove a tab index smaller than the current tab index
        else:
            self.ui.BruteTabWidget.setCurrentIndex(currentTabIndex)
            
        if self.ui.BruteTabWidget.count() == 0:                         # if the last tab was removed, add default tab
            self.createNewBruteTab('127.0.0.1', '22', 'ssh')

    def resetBruteTabs(self):
        count = self.ui.BruteTabWidget.count()
        for i in range(0, count):
            self.ui.BruteTabWidget.removeTab(count -i -1)
        self.createNewBruteTab('127.0.0.1', '22', 'ssh')

    # TODO: show udp in tabtitle when udp service
    def callHydra(self, bWidget):
        if validateNmapInput(bWidget.ipTextinput.text()) and validateNmapInput(bWidget.portTextinput.text()) and validateCredentials(bWidget.usersTextinput.text()) and validateCredentials(bWidget.passwordsTextinput.text()):
                                                                        # check if host is already in scope
            if not self.controller.isHostInDB(bWidget.ipTextinput.text()):
                message = "This host is not in scope. Add it to scope and continue?"
                reply = self.yesNoDialog(message, 'Confirm')
                if reply == QtWidgets.QMessageBox.No:
                    return
                else:
                    log.info('Adding host to scope here!!')
                    self.controller.addHosts(str(bWidget.ipTextinput.text()).replace(';',' '), False, False, "unset", "unset")
            
            bWidget.validationLabel.hide()
            bWidget.toggleRunButton()
            bWidget.resetDisplay()                                      # fixes tab bug
            
            hydraCommand = bWidget.buildHydraCommand(self.controller.getRunningFolder(), self.controller.getUserlistPath(), self.controller.getPasslistPath())      
            bWidget.setObjectName(str("hydra"+" ("+bWidget.getPort()+"/tcp)"))
            
            hosttabs = []                                               # add widget to host tabs (needed to be able to move the widget between brute/tools tabs)
            if str(bWidget.ip) in self.hostTabs:
                hosttabs = self.hostTabs[str(bWidget.ip)]
                
            hosttabs.append(bWidget)
            self.hostTabs.update({str(bWidget.ip):hosttabs})
            
            bWidget.pid = self.controller.runCommand("hydra", bWidget.objectName(), bWidget.ip, bWidget.getPort(), 'tcp', unicode(hydraCommand), getTimestamp(True), bWidget.outputfile, bWidget.display)
            bWidget.runButton.clicked.disconnect()
            bWidget.runButton.clicked.connect(lambda: self.killBruteProcess(bWidget))
            
        else:
            bWidget.validationLabel.show()
        
    def killBruteProcess(self, bWidget):
        dbId = str(bWidget.display.property('dbId'))
        status = self.controller.getProcessStatusForDBId(dbId)
        if status == "Running":                                         # check if we need to kill or cancel
            self.controller.killProcess(self.controller.getPidForProcess(dbId), dbId)
            
        elif status == "Waiting":
            self.controller.cancelProcess(dbId)
        self.bruteProcessFinished(bWidget)
        
    def bruteProcessFinished(self, bWidget):
        bWidget.toggleRunButton()
        bWidget.pid = -1
        
        # disassociate textview from bWidget (create new textview for bWidget) and replace it with a new host tab
        self.createNewTabForHost(str(bWidget.ip), str(bWidget.objectName()), restoring=True, content=unicode(bWidget.display.toPlainText())).setProperty('dbId', str(bWidget.display.property('dbId')))
        
        hosttabs = []                                                   # go through host tabs and find the correct bWidget
        if str(bWidget.ip) in self.hostTabs:
            hosttabs = self.hostTabs[str(bWidget.ip)]

        if hosttabs.count(bWidget) > 1:
            hosttabs.remove(bWidget)
        
        self.hostTabs.update({str(bWidget.ip):hosttabs})

        bWidget.runButton.clicked.disconnect()
        bWidget.runButton.clicked.connect(lambda: self.callHydra(bWidget))

    def findFinishedBruteTab(self, pid):
        for i in range(0, self.ui.BruteTabWidget.count()):
            if str(self.ui.BruteTabWidget.widget(i).pid) == pid:
                self.bruteProcessFinished(self.ui.BruteTabWidget.widget(i))
                return

    def blinkBruteTab(self, bWidget):
        self.ui.MainTabWidget.tabBar().setTabTextColor(1, QtGui.QColor('red'))
        for i in range(0, self.ui.BruteTabWidget.count()):
            if self.ui.BruteTabWidget.widget(i) == bWidget:
                self.ui.BruteTabWidget.tabBar().setTabTextColor(i, QtGui.QColor('red'))
                return
