#!/usr/bin/env python
"""
LEGION (https://gotham-security.com)
Copyright (c) 2023 Gotham Security

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
    version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
    details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtGui import QColor

from ui.dialogs import *                                                # for the screenshots (image viewer)
from ui.ancillaryDialog import *
from utilities.qtLogging import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))    # do not change this name
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))

        self.MainTabWidget = QtWidgets.QTabWidget(self.splitter_2)
        self.MainTabWidget.setObjectName(_fromUtf8("MainTabWidget"))
        self.ScanTab = QtWidgets.QWidget()
        self.ScanTab.setObjectName(_fromUtf8("ScanTab"))
        self.gridLayout_2 = QtWidgets.QGridLayout(self.ScanTab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.splitter = QtWidgets.QSplitter(self.ScanTab)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
    
        # size policies
        self.sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        # this specifies that the widget will keep its width when the window is resized
        self.sizePolicy.setHorizontalStretch(0)
        self.sizePolicy.setVerticalStretch(0)
        
        self.sizePolicy2 = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        # this specifies that the widget will expand its width when the window is resized
        self.sizePolicy2.setHorizontalStretch(1)
        self.sizePolicy2.setVerticalStretch(0)
        
        self.setupLeftPanel()
        self.setupRightPanel()
        self.setupMainTabs()
        self.setupBottomPanel()
        self.setupBottom2Panel()
        
        self.gridLayout.addWidget(self.splitter_2, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.setupMenuBar(MainWindow)
        self.retranslateUi(MainWindow)
        self.setDefaultIndexes()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setWindowState(QtCore.Qt.WindowState.WindowMaximized)

    def setupLeftPanel(self):
        self.HostsTabWidget = QtWidgets.QTabWidget(self.splitter)
        self.sizePolicy.setHeightForWidth(self.HostsTabWidget.sizePolicy().hasHeightForWidth())
        self.HostsTabWidget.setSizePolicy(self.sizePolicy2)
        self.HostsTabWidget.setObjectName(_fromUtf8("HostsTabWidget"))

        self.HostsTab = QtWidgets.QWidget()
        self.HostsTab.setObjectName(_fromUtf8("HostsTab"))
        self.keywordTextInput = QtWidgets.QLineEdit()
        self.keywordTextInput.setToolTip('Enter keywords and click apply to filter view')

        self.FilterApplyButton = QtWidgets.QToolButton()
        self.searchIcon = QtGui.QIcon()
        self.searchIcon.addPixmap(QtGui.QPixmap(_fromUtf8("./images/search.png")), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.FilterApplyButton.setIconSize(QtCore.QSize(19, 19))
        self.FilterApplyButton.setIcon(self.searchIcon)
        self.FilterApplyButton.setToolTip('Apply filters to view')

        self.FilterAdvancedButton = QtWidgets.QToolButton()
        self.advancedIcon = QtGui.QIcon()
        self.advancedIcon.addPixmap(QtGui.QPixmap(_fromUtf8("./images/advanced.png")),
                                    QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.FilterAdvancedButton.setIconSize(QtCore.QSize(19, 19))
        self.FilterAdvancedButton.setIcon(self.advancedIcon)
        self.FilterAdvancedButton.setToolTip('Choose advanced filters')

        self.AddHostButton = QtWidgets.QToolButton()
        self.addIcon = QtGui.QIcon()
        self.addIcon.addPixmap(QtGui.QPixmap(_fromUtf8("./images/add.png")), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.AddHostButton.setIconSize(QtCore.QSize(19, 19))
        self.AddHostButton.setIcon(self.addIcon)
        self.AddHostButton.setToolTip('Add host')

        self.vlayout = QtWidgets.QVBoxLayout(self.HostsTab)
        self.vlayout.setObjectName(_fromUtf8("vlayout"))
        self.HostsTableView = QtWidgets.QTableView(self.HostsTab)
        self.HostsTableView.setObjectName(_fromUtf8("HostsTableView"))
        self.vlayout.addWidget(self.HostsTableView)

        # the overlay widget that appears over the hosttableview
        self.addHostsOverlay = QtWidgets.QTextEdit(self.HostsTab)
        self.addHostsOverlay.setObjectName(_fromUtf8("addHostsOverlay"))
        self.addHostsOverlay.setText('Click here to add host(s) to scope')
        self.addHostsOverlay.setReadOnly(True)
        self.addHostsOverlay.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)

        ###
        self.addHostsOverlay.setFont(QtGui.QFont('Calibri', 12))
        self.addHostsOverlay.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)
        ###
        
        self.vlayout.addWidget(self.addHostsOverlay)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.keywordTextInput)
        self.hlayout.addWidget(self.FilterApplyButton)
        self.hlayout.addWidget(self.FilterAdvancedButton)
        self.hlayout.addWidget(self.AddHostButton)
        self.vlayout.addLayout(self.hlayout)
        self.HostsTabWidget.addTab(self.HostsTab, _fromUtf8(""))

        self.ServicesLeftTab = QtWidgets.QWidget()
        self.ServicesLeftTab.setObjectName(_fromUtf8("ServicesLeftTab"))
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.ServicesLeftTab)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.ServiceNamesTableView = QtWidgets.QTableView(self.ServicesLeftTab)
        self.ServiceNamesTableView.setObjectName(_fromUtf8("ServiceNamesTableView"))
        self.horizontalLayout_2.addWidget(self.ServiceNamesTableView)
        self.HostsTabWidget.addTab(self.ServicesLeftTab, _fromUtf8(""))

        self.ToolsTab = QtWidgets.QWidget()
        self.ToolsTab.setObjectName(_fromUtf8("ToolsTab"))
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.ToolsTab)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.ToolsTableView = QtWidgets.QTableView(self.ToolsTab)
        self.ToolsTableView.setObjectName(_fromUtf8("ToolsTableView"))
        self.horizontalLayout_3.addWidget(self.ToolsTableView)
        self.HostsTabWidget.addTab(self.ToolsTab, _fromUtf8(""))

        # Disabled for now
        #self.CvesLeftTab = QtWidgets.QWidget()
        #self.CvesLeftTab.setObjectName(_fromUtf8("CvesLeftTab"))
        #self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.CvesLeftTab)
        #self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        #self.CvesTableView = QtWidgets.QTableView(self.CvesLeftTab)
        #self.CvesTableView.setObjectName(_fromUtf8("CvesTableView"))
        #self.horizontalLayout_8.addWidget(self.CvesTableView)
        #self.HostsTabWidget.addTab(self.CvesLeftTab, _fromUtf8(""))

    def setupRightPanel(self):
        self.ServicesTabWidget = QtWidgets.QTabWidget()
        self.ServicesTabWidget.setEnabled(True)
        self.sizePolicy2.setHeightForWidth(self.ServicesTabWidget.sizePolicy().hasHeightForWidth())
        self.ServicesTabWidget.setSizePolicy(self.sizePolicy2)
        self.ServicesTabWidget.setObjectName(_fromUtf8("ServicesTabWidget"))
        self.splitter.addWidget(self.ServicesTabWidget)

        ###

        self.splitter_3 = QtWidgets.QSplitter()
        self.splitter_3.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter_3.setObjectName(_fromUtf8("splitter_3"))
        # this makes the tools tab stay the same width when resizing the window
        self.splitter_3.setSizePolicy(self.sizePolicy2)
        
        ###
        
        self.ToolHostsWidget = QtWidgets.QWidget()
        self.ToolHostsWidget.setObjectName(_fromUtf8("ToolHostsTab"))
        self.ToolHostsLayout = QtWidgets.QVBoxLayout(self.ToolHostsWidget)
        self.ToolHostsLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ToolHostsTableView = QtWidgets.QTableView(self.ToolHostsWidget)
        self.ToolHostsTableView.setObjectName(_fromUtf8("ServicesTableView"))
        self.ToolHostsLayout.addWidget(self.ToolHostsTableView)
        self.splitter_3.addWidget(self.ToolHostsWidget)
        
        self.DisplayWidget = QtWidgets.QWidget()
        self.DisplayWidget.setObjectName('ToolOutput')
        self.DisplayWidget.setSizePolicy(self.sizePolicy2)
        ### ?
        #self.toolOutputTextView = QtWidgets.QTextEdit(self.DisplayWidget)
        self.toolOutputTextView = QtWidgets.QPlainTextEdit(self.DisplayWidget)
        self.toolOutputTextView.setReadOnly(True)
        self.DisplayWidgetLayout = QtWidgets.QHBoxLayout(self.DisplayWidget)
        self.DisplayWidgetLayout.addWidget(self.toolOutputTextView)
        self.splitter_3.addWidget(self.DisplayWidget)

        self.ScreenshotWidget = ImageViewer()
        self.ScreenshotWidget.setObjectName('Screenshot')
        self.ScreenshotWidget.scrollArea.setSizePolicy(self.sizePolicy2)
        self.ScreenshotWidget.scrollArea.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.splitter_3.addWidget(self.ScreenshotWidget.scrollArea)

        self.splitter.addWidget(self.splitter_3)

        ###
        
        self.ServicesRightTab = QtWidgets.QWidget()
        self.ServicesRightTab.setObjectName(_fromUtf8("ServicesRightTab"))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.ServicesRightTab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ServicesTableView = QtWidgets.QTableView(self.ServicesRightTab)
        self.ServicesTableView.setObjectName(_fromUtf8("ServicesTableView"))
        self.verticalLayout.addWidget(self.ServicesTableView)
        self.ServicesTabWidget.addTab(self.ServicesRightTab, _fromUtf8(""))

        self.CvesRightTab = QtWidgets.QWidget()
        self.CvesRightTab.setObjectName(_fromUtf8("CvesRightTab"))
        self.verticalLayout_1 = QtWidgets.QVBoxLayout(self.CvesRightTab)
        self.verticalLayout_1.setObjectName(_fromUtf8("verticalLayout_1"))
        self.CvesTableView = QtWidgets.QTableView(self.CvesRightTab)
        self.CvesTableView.setObjectName(_fromUtf8("CvesTableView"))
        self.verticalLayout_1.addWidget(self.CvesTableView)
        self.ServicesTabWidget.addTab(self.CvesRightTab, _fromUtf8(""))
        
        self.ScriptsTab = QtWidgets.QWidget()
        self.ScriptsTab.setObjectName(_fromUtf8("ScriptsTab"))
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.ScriptsTab)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
                
        self.splitter_4 = QtWidgets.QSplitter(self.ScriptsTab)
        self.splitter_4.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.splitter_4.setObjectName(_fromUtf8("splitter_4"))
        
        self.ScriptsTableView = QtWidgets.QTableView()
        self.ScriptsTableView.setObjectName(_fromUtf8("ScriptsTableView"))
        self.splitter_4.addWidget(self.ScriptsTableView)
        
        self.ScriptsOutputTextEdit = QtWidgets.QPlainTextEdit()
        self.ScriptsOutputTextEdit.setObjectName(_fromUtf8("ScriptsOutputTextEdit"))
        self.ScriptsOutputTextEdit.setReadOnly(True)
        self.splitter_4.addWidget(self.ScriptsOutputTextEdit)
        self.horizontalLayout_6.addWidget(self.splitter_4)
        self.ServicesTabWidget.addTab(self.ScriptsTab, _fromUtf8(""))
        
        self.InformationTab = QtWidgets.QWidget()
        self.InformationTab.setObjectName(_fromUtf8("InformationTab"))
        self.ServicesTabWidget.addTab(self.InformationTab, _fromUtf8(""))
        
        self.NotesTab = QtWidgets.QWidget()
        self.NotesTab.setObjectName(_fromUtf8("NotesTab"))
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.NotesTab)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.NotesTextEdit = QtWidgets.QPlainTextEdit(self.NotesTab)
        self.NotesTextEdit.setObjectName(_fromUtf8("NotesTextEdit"))
        self.horizontalLayout_4.addWidget(self.NotesTextEdit)
        self.ServicesTabWidget.addTab(self.NotesTab, _fromUtf8(""))

    def setupMainTabs(self):
        self.gridLayout_2.addWidget(self.splitter, 0, 0, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gridLayout_2.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.MainTabWidget.addTab(self.ScanTab, _fromUtf8(""))
        
        self.BruteTab = QtWidgets.QWidget()
        self.BruteTab.setObjectName(_fromUtf8("BruteTab"))
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.BruteTab)
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.BruteTabWidget = QtWidgets.QTabWidget(self.BruteTab)
        self.BruteTabWidget.setObjectName(_fromUtf8("BruteTabWidget"))
        self.horizontalLayout_7.addWidget(self.BruteTabWidget)
        self.MainTabWidget.addTab(self.BruteTab, _fromUtf8(""))

    def setupBottomPanel(self):
        self.BottomTabWidget = QtWidgets.QTabWidget(self.splitter_2)
        self.BottomTabWidget.setSizeIncrement(QtCore.QSize(0, 0))
        self.BottomTabWidget.setBaseSize(QtCore.QSize(0, 0))
        self.BottomTabWidget.setObjectName(_fromUtf8("BottomTabWidget"))

        # Process Tab
        self.ProcessTab = QtWidgets.QWidget()
        self.ProcessTab.setObjectName(_fromUtf8("ProcessesTab"))
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.ProcessTab)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.ProcessesTableView = QtWidgets.QTableView(self.ProcessTab)
        self.ProcessesTableView.setObjectName(_fromUtf8("ProcessesTableView"))
        self.horizontalLayout_5.addWidget(self.ProcessesTableView)
        self.BottomTabWidget.addTab(self.ProcessTab, _fromUtf8(""))

    def setupBottom2Panel(self):
        # Log Tab
        self.LogTab = QtWidgets.QWidget()
        self.LogTab.setObjectName(_fromUtf8("LogTab"))
        self.LogTabLayout = QtWidgets.QHBoxLayout(self.LogTab)
        self.LogTabLayout.setObjectName(_fromUtf8("LogTabLayout"))
        self.LogOutputTextView = QPlainTextEditLogger(self.LogTab)
        self.LogOutputTextView.widget.setObjectName(_fromUtf8("LogOutputTextView"))
        self.LogOutputTextView.widget.setReadOnly(True)
        self.LogTabLayout.addWidget(self.LogOutputTextView.widget)
        self.BottomTabWidget.addTab(self.LogTab, _fromUtf8(""))
        log.addHandler(self.LogOutputTextView)

        # Python Tab - Disabled until next release
        #self.PythonTab = QtWidgets.QWidget()
        #self.PythonTab.setObjectName(_fromUtf8("PythonTab"))
        #self.PythonOutputTextView = QtWidgets.QPlainTextEdit(self.PythonTab)
        #self.PythonOutputTextView.setReadOnly(False)
        #self.PythonTabLayout = QtWidgets.QHBoxLayout(self.PythonTab)
        #self.PythonTabLayout.addWidget(self.PythonOutputTextView)
        #self.BottomTabWidget.addTab(self.PythonTab, _fromUtf8(""))

    def setupMenuBar(self, MainWindow):
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1010, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        #self.menuSettings = QtWidgets.QMenu(self.menubar)
        #self.menuSettings.setObjectName(_fromUtf8("menuSettings"))
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionImportNmap = QtGui.QAction(MainWindow)
        self.actionImportNmap.setObjectName(_fromUtf8("actionImportNmap"))
        self.actionSaveAs = QtGui.QAction(MainWindow)
        self.actionSaveAs.setObjectName(_fromUtf8("actionSaveAs"))
        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        self.actionAddHosts = QtGui.QAction(MainWindow)
        self.actionAddHosts.setObjectName(_fromUtf8("actionAddHosts"))
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionAddHosts)
        self.menuFile.addAction(self.actionImportNmap)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        #self.menubar.addAction(self.menuSettings.menuAction())
        #self.actionSettings = QtGui.QAction(MainWindow)
        #self.actionSettings.setObjectName(_fromUtf8("getSettingsMenu"))
        #self.menuSettings.addAction(self.actionSettings)

        self.actionHelp = QtGui.QAction(MainWindow)
        self.actionHelp.setObjectName(_fromUtf8("getHelp"))
        self.menuHelp.addAction(self.actionHelp)
        self.menubar.addAction(self.menuHelp.menuAction())

        self.actionConfig = QtGui.QAction(MainWindow)
        self.actionConfig.setObjectName(_fromUtf8("config"))
        self.menuHelp.addAction(self.actionConfig)
        self.menubar.addAction(self.menuHelp.menuAction())

    def setDefaultIndexes(self):
        self.MainTabWidget.setCurrentIndex(1)
        self.HostsTabWidget.setCurrentIndex(1)
        self.ServicesTabWidget.setCurrentIndex(1)
        self.BruteTabWidget.setCurrentIndex(1)
        self.BottomTabWidget.setCurrentIndex(0)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "LEGION", None))
        self.HostsTabWidget.setTabText(self.HostsTabWidget.indexOf(self.HostsTab),
                                       QtWidgets.QApplication.translate("MainWindow", "Hosts", None))
        self.HostsTabWidget.setTabText(self.HostsTabWidget.indexOf(self.ServicesLeftTab),
                                       QtWidgets.QApplication.translate("MainWindow", "Services", None))
        #self.HostsTabWidget.setTabText(self.HostsTabWidget.indexOf(self.CvesLeftTab),
        # QtWidgets.QApplication.translate("MainWindow", "CVEs", None))
        self.HostsTabWidget.setTabText(self.HostsTabWidget.indexOf(self.ToolsTab),
                                       QtWidgets.QApplication.translate("MainWindow", "Tools", None))
        self.ServicesTabWidget.setTabText(self.ServicesTabWidget.indexOf(self.ServicesRightTab),
                                          QtWidgets.QApplication.translate("MainWindow", "Services", None))
        self.ServicesTabWidget.setTabText(self.ServicesTabWidget.indexOf(self.CvesRightTab),
                                          QtWidgets.QApplication.translate("MainWindow", "CVEs", None))
        self.ServicesTabWidget.setTabText(self.ServicesTabWidget.indexOf(self.ScriptsTab),
                                          QtWidgets.QApplication.translate("MainWindow", "Scripts", None))
        self.ServicesTabWidget.setTabText(self.ServicesTabWidget.indexOf(self.InformationTab),
                                          QtWidgets.QApplication.translate("MainWindow", "Information", None))
        self.ServicesTabWidget.setTabText(self.ServicesTabWidget.indexOf(self.NotesTab),
                                          QtWidgets.QApplication.translate("MainWindow", "Notes", None))
        self.MainTabWidget.setTabText(self.MainTabWidget.indexOf(self.ScanTab),
                                      QtWidgets.QApplication.translate("MainWindow", "Scan", None))
        self.MainTabWidget.setTabText(self.MainTabWidget.indexOf(self.BruteTab),
                                      QtWidgets.QApplication.translate("MainWindow", "Brute", None))
        self.BottomTabWidget.setTabText(self.BottomTabWidget.indexOf(self.ProcessTab),
                                        QtWidgets.QApplication.translate("MainWindow", "Processes", None))
        self.BottomTabWidget.setTabText(self.BottomTabWidget.indexOf(self.LogTab),
                                        QtWidgets.QApplication.translate("MainWindow", "Log", None))
        # self.BottomTabWidget.setTabText(self.BottomTabWidget.indexOf(self.PythonTab),
        # QtWidgets.QApplication.translate("MainWindow", "Python", None)) - Disabled until future release
        self.menuFile.setTitle(QtWidgets.QApplication.translate("MainWindow", "File", None))
        #self.menuSettings.setTitle(QtWidgets.QApplication.translate("MainWindow", "Settings", None))
        self.menuHelp.setTitle(QtWidgets.QApplication.translate("MainWindow", "Help", None))
        self.actionExit.setText(QtWidgets.QApplication.translate("MainWindow", "Exit", None))
        self.actionExit.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Exit the application", None))
        self.actionExit.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Q", None))
        self.actionOpen.setText(QtWidgets.QApplication.translate("MainWindow", "Open", None))
        self.actionOpen.setToolTip(QtWidgets.QApplication.translate("MainWindow",
                                                                    "Open an existing project file", None))
        self.actionOpen.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+O", None))
        self.actionSave.setText(QtWidgets.QApplication.translate("MainWindow", "Save", None))
        self.actionSave.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Save the current project", None))
        self.actionSave.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+S", None))
        self.actionImportNmap.setText(QtWidgets.QApplication.translate("MainWindow", "Import nmap", None))
        self.actionImportNmap.setToolTip(QtWidgets.QApplication.translate("MainWindow",
                                                                          "Import an nmap xml file", None))
        self.actionImportNmap.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+I", None))
        self.actionSaveAs.setText(QtWidgets.QApplication.translate("MainWindow", "Save As", None))
        self.actionNew.setText(QtWidgets.QApplication.translate("MainWindow", "New", None))
        self.actionNew.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+N", None))
        self.actionAddHosts.setText(QtWidgets.QApplication.translate("MainWindow", "Add host(s) to scope", None))
        self.actionAddHosts.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+H", None))
        #self.actionSettings.setText(QtWidgets.QApplication.translate("MainWindow", "Preferences", None))
        self.actionHelp.setText(QtWidgets.QApplication.translate("MainWindow", "Help", None))
        self.actionHelp.setShortcut(QtWidgets.QApplication.translate("MainWindow", "F1", None))
        self.actionConfig.setText(QtWidgets.QApplication.translate("MainWindow", "Config", None))
        self.actionConfig.setShortcut(QtWidgets.QApplication.translate("MainWindow", "F2", None))
