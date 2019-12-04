#!/usr/bin/env python

"""
LEGION (https://govanguard.io)
Copyright (c) 2018 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
    version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
    details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <http://www.gnu.org/licenses/>.
"""

import os
from PyQt5.QtGui import *                                               # for filters dialog
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtGui
from app.auxiliary import *                                             # for timestamps
from six import u as unicode

from app.timing import getTimestamp


class BruteWidget(QtWidgets.QWidget):
    
    def __init__(self, ip, port, service, settings, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ip = ip
        self.port = port
        self.service = service

        ##
        #self.hydraServices = hydraServices
        #self.hydraNoUsernameServices = hydraNoUsernameServices
        #self.hydraNoPasswordServices = hydraNoPasswordServices
        #self.bruteSettings = bruteSettings
        #self.generalSettings = generalSettings
        ##

        self.settings = settings
        self.pid = -1                                                   # will store hydra's pid so we can kill it
        self.setupLayout()
        
        self.browseUsersButton.clicked.connect(lambda: self.wordlistDialog())
        self.browsePasswordsButton.clicked.connect(lambda: self.wordlistDialog('Choose password list'))
        self.usersTextinput.textEdited.connect(self.singleUserRadio.toggle)
        self.passwordsTextinput.textEdited.connect(self.singlePassRadio.toggle)
        self.userlistTextinput.textEdited.connect(self.userListRadio.toggle)
        self.passlistTextinput.textEdited.connect(self.passListRadio.toggle)
        self.checkAddMoreOptions.stateChanged.connect(self.showMoreOptions)     
        
    def setupLayoutHlayout(self):
        hydraServiceConversion = {'login': 'rlogin', 'ms-sql-s': 'mssql', 'ms-wbt-server': 'rdp',
                                  'netbios-ssn': 'smb', 'netbios-ns': 'smb', 'microsoft-ds': 'smb',
                                  'postgresql': 'postgres', 'vmware-auth': 'vmauthd"'}
        # sometimes nmap service name is different from hydra service name
        if self.service is None:
            self.service = ''
        elif str(self.service) in hydraServiceConversion:
            self.service = hydraServiceConversion.get(str(self.service))

        self.label1 = QtWidgets.QLabel()
        self.label1.setText('IP')
        self.label1.setAlignment(Qt.AlignLeft)
        self.label1.setAlignment(Qt.AlignVCenter)
        self.ipTextinput = QtWidgets.QLineEdit()
        self.ipTextinput.setText(str(self.ip))
        self.ipTextinput.setFixedWidth(125)
        
        self.label2 = QtWidgets.QLabel()
        self.label2.setText('Port')
        self.label2.setAlignment(Qt.AlignLeft)
        self.label2.setAlignment(Qt.AlignVCenter)
        self.portTextinput = QtWidgets.QLineEdit()
        self.portTextinput.setText(str(self.port))
        self.portTextinput.setFixedWidth(60)
        
        self.label3 = QtWidgets.QLabel()
        self.label3.setText('Service')
        self.label3.setAlignment(Qt.AlignLeft)
        self.label3.setAlignment(Qt.AlignVCenter)
        self.serviceComboBox = QtWidgets.QComboBox()
        self.serviceComboBox.insertItems(0, self.settings.brute_services.split(","))
        self.serviceComboBox.setStyleSheet("QComboBox { combobox-popup: 0; }");
        self.serviceComboBox.currentIndexChanged.connect(self.checkSelectedService)
        
        # autoselect service from combo box
        for i in range(len(self.settings.brute_services.split(","))):
            if str(self.service) in self.settings.brute_services.split(",")[i]:
                self.serviceComboBox.setCurrentIndex(i)
                break

#       self.labelPath = QtWidgets.QLineEdit()  # this is the extra input field to insert the path to brute force
#       self.labelPath.setFixedWidth(800)
#       self.labelPath.setText('/')

        self.runButton = QPushButton('Run')
        self.runButton.setMaximumSize(110, 30)
        self.runButton.setDefault(True) # new
        
        ###
        self.validationLabel = QtWidgets.QLabel(self)
        self.validationLabel.setText('Invalid input. Please try again!')
        self.validationLabel.setStyleSheet('QLabel { color: red }')
        ###

        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.label1)
        self.hlayout.addWidget(self.ipTextinput)
        self.hlayout.addWidget(self.label2)
        self.hlayout.addWidget(self.portTextinput)  
        self.hlayout.addWidget(self.label3)
        self.hlayout.addWidget(self.serviceComboBox)
        self.hlayout.addWidget(self.runButton)
        ###
        self.hlayout.addWidget(self.validationLabel)
        self.validationLabel.hide()
        ###
        self.hlayout.addStretch()

        return self.hlayout

    def setupLayoutHlayout2(self):
        self.singleUserRadio = QtWidgets.QRadioButton()
        self.label4 = QtWidgets.QLabel()
        self.label4.setText('Username')
        self.label4.setFixedWidth(70)
        self.usersTextinput = QtWidgets.QLineEdit()
        self.usersTextinput.setFixedWidth(125)
        self.usersTextinput.setText(self.settings.brute_default_username)
        self.userListRadio = QtWidgets.QRadioButton()
        self.label5 = QtWidgets.QLabel()
        self.label5.setText('Username list')
        self.label5.setFixedWidth(90)
        self.userlistTextinput = QtWidgets.QLineEdit()
        self.userlistTextinput.setFixedWidth(125)
        self.browseUsersButton = QPushButton('Browse')
        self.browseUsersButton.setMaximumSize(80, 30)
        
        self.foundUsersRadio = QtWidgets.QRadioButton()
        self.label9 = QtWidgets.QLabel()
        self.label9.setText('Found usernames')
        self.label9.setFixedWidth(117)      
        
        self.userGroup = QtWidgets.QButtonGroup()
        self.userGroup.addButton(self.singleUserRadio)
        self.userGroup.addButton(self.userListRadio)
        self.userGroup.addButton(self.foundUsersRadio)
        self.foundUsersRadio.toggle()

        self.warningLabel = QtWidgets.QLabel()
        self.warningLabel.setText('*Note: when using form-based services from the Service menu, ' +
                                  'select the "Additional Options" checkbox and add the proper arguments' +
                                  ' for the webpage form. See Hydra documentation for extra help when' +
                                  ' targeting HTTP/HTTPS forms.')
        self.warningLabel.setWordWrap(True)
        self.warningLabel.setAlignment(Qt.AlignRight)
        self.warningLabel.setStyleSheet('QLabel { color: red }')

        self.hlayout2 = QtWidgets.QHBoxLayout()
        self.hlayout2.addWidget(self.singleUserRadio)
        self.hlayout2.addWidget(self.label4)
        self.hlayout2.addWidget(self.usersTextinput)
        self.hlayout2.addWidget(self.userListRadio)
        self.hlayout2.addWidget(self.label5)
        self.hlayout2.addWidget(self.userlistTextinput)
        self.hlayout2.addWidget(self.browseUsersButton)
        self.hlayout2.addWidget(self.foundUsersRadio)
        self.hlayout2.addWidget(self.label9)
        self.hlayout2.addWidget(self.warningLabel)
        self.warningLabel.hide()
        self.hlayout2.addStretch()

        return self.hlayout2

    def checkSelectedService(self):
        self.service = str(self.serviceComboBox.currentText())
        if 'form' in str(self.service):
            self.warningLabel.show()
        #else: This clause would produce an interesting logic error and crash
            #self.warningLabel.hide()

    def setupLayoutHlayout3(self):        
        #add usernames wordlist
        self.singlePassRadio = QtWidgets.QRadioButton()
        self.label6 = QtWidgets.QLabel()
        self.label6.setText('Password')
        self.label6.setFixedWidth(70)
        self.passwordsTextinput = QtWidgets.QLineEdit()
        self.passwordsTextinput.setFixedWidth(125)
        self.passwordsTextinput.setText(self.settings.brute_default_password)
        self.passListRadio = QtWidgets.QRadioButton()
        self.label7 = QtWidgets.QLabel()
        self.label7.setText('Password list')
        self.label7.setFixedWidth(90)
        self.passlistTextinput = QtWidgets.QLineEdit()
        self.passlistTextinput.setFixedWidth(125)
        self.browsePasswordsButton = QPushButton('Browse')
        self.browsePasswordsButton.setMaximumSize(80, 30)
        
        self.foundPasswordsRadio = QtWidgets.QRadioButton()
        self.label10 = QtWidgets.QLabel()
        self.label10.setText('Found passwords')
        self.label10.setFixedWidth(115) 
        
        self.passGroup = QtWidgets.QButtonGroup()
        self.passGroup.addButton(self.singlePassRadio)
        self.passGroup.addButton(self.passListRadio)
        self.passGroup.addButton(self.foundPasswordsRadio)
        self.foundPasswordsRadio.toggle()

        self.label8 = QtWidgets.QLabel()
        self.label8.setText('Threads')
        self.label8.setFixedWidth(60)
        self.threadOptions = []
        for i in range(1, 129):
            self.threadOptions.append(str(i))
        self.threadsComboBox = QtWidgets.QComboBox()
        self.threadsComboBox.insertItems(0, self.threadOptions)
        self.threadsComboBox.setMinimumContentsLength(3)
        self.threadsComboBox.setMaxVisibleItems(3)
        self.threadsComboBox.setStyleSheet("QComboBox { combobox-popup: 0; }");
        self.threadsComboBox.setCurrentIndex(15)    
    
        self.hlayout3 = QtWidgets.QHBoxLayout()
        self.hlayout3.addWidget(self.singlePassRadio)
        self.hlayout3.addWidget(self.label6)
        self.hlayout3.addWidget(self.passwordsTextinput)
        self.hlayout3.addWidget(self.passListRadio)
        self.hlayout3.addWidget(self.label7)
        self.hlayout3.addWidget(self.passlistTextinput)
        self.hlayout3.addWidget(self.browsePasswordsButton)
        self.hlayout3.addWidget(self.foundPasswordsRadio)
        self.hlayout3.addWidget(self.label10)
        self.hlayout3.addStretch()
        self.hlayout3.addWidget(self.label8)
        self.hlayout3.addWidget(self.threadsComboBox)
        #self.hlayout3.addStretch()

        return self.hlayout3

    def setupLayoutHlayout4(self):
        #label6.setText('Try blank password')
        self.checkBlankPass = QtWidgets.QCheckBox()
        self.checkBlankPass.setText('Try blank password')
        self.checkBlankPass.toggle()
        #add 'try blank password'
        #label7.setText('Try login as password')
        self.checkLoginAsPass = QtWidgets.QCheckBox()
        self.checkLoginAsPass.setText('Try login as password')
        self.checkLoginAsPass.toggle()
        #add 'try login as password'
        #label8.setText('Loop around users')
        self.checkLoopUsers = QtWidgets.QCheckBox()
        self.checkLoopUsers.setText('Loop around users')
        self.checkLoopUsers.toggle()
        #add 'loop around users'
        #label9.setText('Exit on first valid')
        self.checkExitOnValid = QtWidgets.QCheckBox()
        self.checkExitOnValid.setText('Exit on first valid')
        self.checkExitOnValid.toggle()
        #add 'exit after first valid combination is found'
        self.checkVerbose = QtWidgets.QCheckBox()
        self.checkVerbose.setText('Verbose')        

        self.checkAddMoreOptions = QtWidgets.QCheckBox()
        self.checkAddMoreOptions.setText('Additional Options')
        
        self.hlayout4 = QtWidgets.QHBoxLayout()
        self.hlayout4.addWidget(self.checkBlankPass)
        self.hlayout4.addWidget(self.checkLoginAsPass)
        self.hlayout4.addWidget(self.checkLoopUsers)
        self.hlayout4.addWidget(self.checkExitOnValid)
        self.hlayout4.addWidget(self.checkVerbose)
        self.hlayout4.addWidget(self.checkAddMoreOptions)
        self.hlayout4.addStretch()

        return self.hlayout4

    def setupLayout(self):
        ###
        self.labelPath = QtWidgets.QLineEdit()  # this is the extra input field to insert the path to brute force
        self.labelPath.setFixedWidth(800)
        self.labelPath.setText('-m "/login/login.html:username=^USER^&password=^PASS^&Login=Login:failed"')
        ###

        self.layoutAddOptions = QtWidgets.QHBoxLayout()
        self.layoutAddOptions.addWidget(self.labelPath)
        self.labelPath.hide()
        self.layoutAddOptions.addStretch()
        
        self.display = QtWidgets.QPlainTextEdit()
        self.display.setReadOnly(True)
        if self.settings.general_tool_output_black_background == 'True':
            #self.display.setStyleSheet("background: rgb(0,0,0)")       # black background
            #self.display.setTextColor(QtGui.QColor('white'))           # white font
            p = self.display.palette()
            p.setColor(QtGui.QPalette.Base, Qt.black)                   # black background
            p.setColor(QtGui.QPalette.Text, Qt.white)                   # white font
            self.display.setPalette(p)
            # font-size:18px; width: 150px; color:red; left: 20px;}"); # set the menu font color: black
            self.display.setStyleSheet("QMenu { color:black;}")
        
        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.addLayout(self.setupLayoutHlayout())
        self.vlayout.addLayout(self.setupLayoutHlayout4())
        self.vlayout.addLayout(self.layoutAddOptions)
        self.vlayout.addLayout(self.setupLayoutHlayout2())
        self.vlayout.addLayout(self.setupLayoutHlayout3())
        self.vlayout.addWidget(self.display)
        self.setLayout(self.vlayout)

    # TODO: need to check all the methods that need an additional input field and add them here
#   def showMoreOptions(self, text):
#       if str(text) == "http-head":        
#           self.labelPath.show()
#       else:
#           self.labelPath.hide()
            
    def showMoreOptions(self):
        if self.checkAddMoreOptions.isChecked():
            self.labelPath.show()
        else:
            self.labelPath.hide()

    def wordlistDialog(self, title='Choose username list'):
    
        if title == 'Choose username list':
            filename = QtWidgets.QFileDialog.getOpenFileName(self, title, self.settings.brute_username_wordlist_path)
            self.userlistTextinput.setText(str(filename[0]))
            self.userListRadio.toggle()
        else:
            filename = QtWidgets.QFileDialog.getOpenFileName(self, title, self.settings.brute_password_wordlist_path)
            self.passlistTextinput.setText(str(filename[0]))
            self.passListRadio.toggle()

    def buildHydraCommand(self, runningfolder, userlistPath, passlistPath):
        
        self.ip = self.ipTextinput.text()
        self.port = self.portTextinput.text()
        self.service = str(self.serviceComboBox.currentText())
        self.command = "hydra " + str(self.ip) + " -s " + self.port + " -o "
        self.outputfile = runningfolder + "/hydra/" + getTimestamp() + \
                          "-" + str(self.ip) + "-" + self.port + "-" + self.service + ".txt"
        self.command += "\"" + self.outputfile + "\""

        if 'form' not in str(self.service):
            self.warningLabel.hide()
        
        if not self.service in self.settings.brute_no_username_services.split(","):
            if self.singleUserRadio.isChecked():
                self.command += " -l " + self.usersTextinput.text()
            elif self.foundUsersRadio.isChecked():
                self.command += " -L \"" + userlistPath+"\""
            else:
                self.command += " -L \"" + self.userlistTextinput.text()+"\""
                
        if not self.service in self.settings.brute_no_password_services.split(","):
            if self.singlePassRadio.isChecked():
                escaped_password = self.passwordsTextinput.text().replace('"', '\"\"\"')
                self.command += " -p \"" + escaped_password + "\""

            elif self.foundPasswordsRadio.isChecked():
                self.command += " -P \"" + passlistPath + "\""
            else:
                self.command += " -P \"" + self.passlistTextinput.text() + "\""

        if self.checkBlankPass.isChecked():
            self.command += " -e n"
            if self.checkLoginAsPass.isChecked():
                self.command += "s"
                
        elif self.checkLoginAsPass.isChecked():
                self.command += " -e s"
                
        if self.checkLoopUsers.isChecked():
            self.command += " -u"
        
        if self.checkExitOnValid.isChecked():
            self.command += " -f"

        if self.checkVerbose.isChecked():
            self.command += " -V"
            
        self.command += " -t " + str(self.threadsComboBox.currentText())
            
        self.command += " " + self.service

#       if self.labelPath.isVisible():  # append the additional field's content, if it was visible
        if self.checkAddMoreOptions.isChecked():
            self.command += " "+str(self.labelPath.text())              # TODO: sanitise this?

        #command = "echo "+escaped_password+" > /tmp/hydra-sub.txt"
        #os.system(unicode(command))
        return self.command
        
    def getPort(self):
        return self.port
        
    def toggleRunButton(self):
        if self.runButton.text() == 'Run':
            self.runButton.setText('Stop')
        else:
            self.runButton.setText('Run')

    # used to be able to display the tool output in both the Brute tab and the tool display panel
    def resetDisplay(self):
        self.display.setParent(None)
        self.display = QtWidgets.QPlainTextEdit()
        self.display.setReadOnly(True)
        if self.settings.general_tool_output_black_background == 'True':
            #self.display.setStyleSheet("background: rgb(0,0,0)")       # black background
            #self.display.setTextColor(QtGui.QColor('white'))           # white font
            p = self.display.palette()
            p.setColor(QtGui.QPalette.Base, Qt.black)                   # black background
            p.setColor(QtGui.QPalette.Text, Qt.white)                   # white font
            self.display.setPalette(p)
            # font-size:18px; width: 150px; color:red; left: 20px;}"); # set the menu font color: black
            self.display.setStyleSheet("QMenu { color:black;}")
        self.vlayout.addWidget(self.display)

# dialog displayed when the user clicks on the advanced filters button      
class FiltersDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupLayout()
        self.applyButton.clicked.connect(self.close)
        self.cancelButton.clicked.connect(self.close)

    def setupLayout(self):
        self.setModal(True)
        self.setWindowTitle('Filters')
        self.setFixedSize(640, 200)
        
        hostsBox = QGroupBox("Host Filters")        
        self.hostsUp = QCheckBox("Show up hosts")
        self.hostsUp.toggle()
        self.hostsDown = QCheckBox("Show down hosts")
        self.hostsChecked = QCheckBox("Show checked hosts")
        self.hostsChecked.toggle()
        hostLayout = QVBoxLayout()
        hostLayout.addWidget(self.hostsUp)
        hostLayout.addWidget(self.hostsDown)
        hostLayout.addWidget(self.hostsChecked)
        hostsBox.setLayout(hostLayout)
        
        portsBox = QGroupBox("Port Filters")
        self.portsOpen = QCheckBox("Show open ports")
        self.portsOpen.toggle()
        self.portsFiltered = QCheckBox("Show filtered ports")
        self.portsClosed = QCheckBox("Show closed ports")
        self.portsTcp = QCheckBox("Show tcp")
        self.portsTcp.toggle()
        self.portsUdp = QCheckBox("Show udp")
        self.portsUdp.toggle()
        servicesLayout = QVBoxLayout()
        servicesLayout.addWidget(self.portsOpen)
        servicesLayout.addWidget(self.portsFiltered)
        servicesLayout.addWidget(self.portsClosed)
        servicesLayout.addWidget(self.portsTcp)
        servicesLayout.addWidget(self.portsUdp)
        portsBox.setLayout(servicesLayout)
        
        keywordSearchBox = QGroupBox("Keyword Filters")
        self.hostKeywordText = QLineEdit()
        keywordLayout = QVBoxLayout()
        keywordLayout.addWidget(self.hostKeywordText)
        keywordSearchBox.setLayout(keywordLayout)
        
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(hostsBox)
        hlayout.addWidget(portsBox)
        hlayout.addWidget(keywordSearchBox)
        
        buttonLayout = QtWidgets.QHBoxLayout()
        self.applyButton = QPushButton('Apply', self)
        self.applyButton.setMaximumSize(110, 30)
        self.cancelButton = QPushButton('Cancel', self)
        self.cancelButton.setMaximumSize(110, 30)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.applyButton)
            
        layout = QVBoxLayout()      
        layout.addLayout(hlayout)
        layout.addLayout(buttonLayout)  
        self.setLayout(layout)
        
    def getFilters(self):
        #return [self.hostsUp.isChecked(), self.hostsDown.isChecked(), self.hostsChecked.isChecked(),
        # self.portsOpen.isChecked(), self.portsFiltered.isChecked(), self.portsClosed.isChecked(),
        # self.portsTcp.isChecked(), self.portsUdp.isChecked(), str(self.hostKeywordText.text()).split()]
        return [self.hostsUp.isChecked(), self.hostsDown.isChecked(), self.hostsChecked.isChecked(),
                self.portsOpen.isChecked(), self.portsFiltered.isChecked(), self.portsClosed.isChecked(),
                self.portsTcp.isChecked(), self.portsUdp.isChecked(), unicode(self.hostKeywordText.text()).split()]

    def setCurrentFilters(self, filters):
        if not self.hostsUp.isChecked() == filters[0]:
            self.hostsUp.toggle()
            
        if not self.hostsDown.isChecked() == filters[1]:
            self.hostsDown.toggle()
            
        if not self.hostsChecked.isChecked() == filters[2]:
            self.hostsChecked.toggle()
            
        if not self.portsOpen.isChecked() == filters[3]:
            self.portsOpen.toggle()
            
        if not self.portsFiltered.isChecked() == filters[4]:
            self.portsFiltered.toggle()
            
        if not self.portsClosed.isChecked() == filters[5]:
            self.portsClosed.toggle()
            
        if not self.portsTcp.isChecked() == filters[6]:
            self.portsTcp.toggle()
            
        if not self.portsUdp.isChecked() == filters[7]:
            self.portsUdp.toggle()
        
        self.hostKeywordText.setText(" ".join(filters[8]))
        
        
    def setKeywords(self, keywords):
        self.hostKeywordText.setText(keywords)

# widget in which the host information is shown
class HostInformationWidget(QtWidgets.QWidget):
    
    def __init__(self, informationTab, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.informationTab = informationTab
        self.setupLayout()
        self.updateFields()     # set default values
        
    def setupLayout(self):
        self.HostStatusLabel = QtWidgets.QLabel()

        self.HostStateLabel = QtWidgets.QLabel()
        self.HostStateText = QtWidgets.QLabel()
        self.HostStateLayout = QtWidgets.QHBoxLayout()
        self.HostStateLayout.addSpacing(20)
        self.HostStateLayout.addWidget(self.HostStateLabel)
        self.HostStateLayout.addWidget(self.HostStateText)
        self.HostStateLayout.addStretch()
        
        self.OpenPortsLabel = QtWidgets.QLabel()
        self.OpenPortsText = QtWidgets.QLabel()
        self.OpenPortsLayout = QtWidgets.QHBoxLayout()
        self.OpenPortsLayout.addSpacing(20)
        self.OpenPortsLayout.addWidget(self.OpenPortsLabel)
        self.OpenPortsLayout.addWidget(self.OpenPortsText)
        self.OpenPortsLayout.addStretch()
        
        self.ClosedPortsLabel = QtWidgets.QLabel()
        self.ClosedPortsText = QtWidgets.QLabel()
        self.ClosedPortsLayout = QtWidgets.QHBoxLayout()
        self.ClosedPortsLayout.addSpacing(20)
        self.ClosedPortsLayout.addWidget(self.ClosedPortsLabel)
        self.ClosedPortsLayout.addWidget(self.ClosedPortsText)
        self.ClosedPortsLayout.addStretch() 
        
        self.FilteredPortsLabel = QtWidgets.QLabel()
        self.FilteredPortsText = QtWidgets.QLabel()
        self.FilteredPortsLayout = QtWidgets.QHBoxLayout()
        self.FilteredPortsLayout.addSpacing(20)
        self.FilteredPortsLayout.addWidget(self.FilteredPortsLabel)
        self.FilteredPortsLayout.addWidget(self.FilteredPortsText)
        self.FilteredPortsLayout.addStretch()   
        ###################
        self.AddressLabel = QtWidgets.QLabel()
        
        self.IP4Label = QtWidgets.QLabel()
        self.IP4Text = QtWidgets.QLabel()
        self.IP4Layout = QtWidgets.QHBoxLayout()
        self.IP4Layout.addSpacing(20)
        self.IP4Layout.addWidget(self.IP4Label)
        self.IP4Layout.addWidget(self.IP4Text)
        self.IP4Layout.addStretch()
        
        self.IP6Label = QtWidgets.QLabel()
        self.IP6Text = QtWidgets.QLabel()
        self.IP6Layout = QtWidgets.QHBoxLayout()
        self.IP6Layout.addSpacing(20)
        self.IP6Layout.addWidget(self.IP6Label)
        self.IP6Layout.addWidget(self.IP6Text)
        self.IP6Layout.addStretch()
        
        self.MacLabel = QtWidgets.QLabel()
        self.MacText = QtWidgets.QLabel()
        self.MacLayout = QtWidgets.QHBoxLayout()
        self.MacLayout.addSpacing(20)
        self.MacLayout.addWidget(self.MacLabel)
        self.MacLayout.addWidget(self.MacText)
        self.MacLayout.addStretch()

        self.AsnLabel = QtWidgets.QLabel()
        self.AsnText = QtWidgets.QLabel()
        self.AsnLayout = QtWidgets.QHBoxLayout()
        self.AsnLayout.addSpacing(20)
        self.AsnLayout.addWidget(self.AsnLabel)
        self.AsnLayout.addWidget(self.AsnText)
        self.AsnLayout.addStretch()

        self.IspLabel = QtWidgets.QLabel()
        self.IspText = QtWidgets.QLabel()
        self.IspLayout = QtWidgets.QHBoxLayout()
        self.IspLayout.addSpacing(20)
        self.IspLayout.addWidget(self.IspLabel)
        self.IspLayout.addWidget(self.IspText)
        self.IspLayout.addStretch()
        
        self.dummyLabel = QtWidgets.QLabel()
        self.dummyText = QtWidgets.QLabel()
        self.dummyLayout = QtWidgets.QHBoxLayout()
        self.dummyLayout.addSpacing(20)
        self.dummyLayout.addWidget(self.dummyLabel)
        self.dummyLayout.addWidget(self.dummyText)
        self.dummyLayout.addStretch()
        #########       
        self.OSLabel = QtWidgets.QLabel()
        
        self.OSNameLabel = QtWidgets.QLabel()
        self.OSNameText = QtWidgets.QLabel()
        self.OSNameLayout = QtWidgets.QHBoxLayout()
        self.OSNameLayout.addSpacing(20)
        self.OSNameLayout.addWidget(self.OSNameLabel)
        self.OSNameLayout.addWidget(self.OSNameText)
        self.OSNameLayout.addStretch()
        
        self.OSAccuracyLabel = QtWidgets.QLabel()
        self.OSAccuracyText = QtWidgets.QLabel()
        self.OSAccuracyLayout = QtWidgets.QHBoxLayout()
        self.OSAccuracyLayout.addSpacing(20)
        self.OSAccuracyLayout.addWidget(self.OSAccuracyLabel)
        self.OSAccuracyLayout.addWidget(self.OSAccuracyText)
        self.OSAccuracyLayout.addStretch()
        
        font = QtGui.QFont('Calibri', 12)        # in each different section
        font.setBold(True)
        self.HostStatusLabel.setText('Host Status')
        self.HostStatusLabel.setFont(font)
        self.HostStateLabel.setText("State:")
        self.OpenPortsLabel.setText('Open Ports:')
        self.ClosedPortsLabel.setText('Closed Ports:')
        self.FilteredPortsLabel.setText('Filtered Ports:')
        self.AddressLabel.setText('Addresses')
        self.AddressLabel.setFont(font)
        self.IP4Label.setText('IPv4:')
        self.IP6Label.setText('IPv6:')
        self.MacLabel.setText('MAC:')
        self.AsnLabel.setText('ASN:')
        self.IspLabel.setText('ISP:')
        self.OSLabel.setText('Operating System')
        self.OSLabel.setFont(font)
        self.OSNameLabel.setText('Name:')
        self.OSAccuracyLabel.setText('Accuracy:')
        #########
        self.vlayout_1 = QtWidgets.QVBoxLayout()
        self.vlayout_2 = QtWidgets.QVBoxLayout()
        self.vlayout_3 = QtWidgets.QVBoxLayout()
        self.hlayout_1 = QtWidgets.QHBoxLayout()
        
        self.vlayout_1.addWidget(self.HostStatusLabel)
        self.vlayout_1.addLayout(self.HostStateLayout)
        self.vlayout_1.addLayout(self.OpenPortsLayout)
        self.vlayout_1.addLayout(self.ClosedPortsLayout)
        self.vlayout_1.addLayout(self.FilteredPortsLayout)
        
        self.vlayout_2.addWidget(self.AddressLabel)
        self.vlayout_2.addLayout(self.IP4Layout)
        self.vlayout_2.addLayout(self.IP6Layout)
        self.vlayout_2.addLayout(self.MacLayout)
        self.vlayout_2.addLayout(self.AsnLayout)
        self.vlayout_2.addLayout(self.IspLayout)
        self.vlayout_2.addLayout(self.dummyLayout)
        
        self.hlayout_1.addLayout(self.vlayout_1)
        self.hlayout_1.addSpacing(20)
        self.hlayout_1.addLayout(self.vlayout_2)
        
        self.vlayout_3.addWidget(self.OSLabel)
        self.vlayout_3.addLayout(self.OSNameLayout)
        self.vlayout_3.addLayout(self.OSAccuracyLayout)
        self.vlayout_3.addStretch()
        
        self.vlayout_4 = QtWidgets.QVBoxLayout()
        self.vlayout_4.addLayout(self.hlayout_1)
        self.vlayout_4.addSpacing(10)
        self.vlayout_4.addLayout(self.vlayout_3)
        
        self.hlayout_4 = QtWidgets.QHBoxLayout(self.informationTab)
        self.hlayout_4.addLayout(self.vlayout_4)
        self.hlayout_4.insertStretch(-1,1)
        self.hlayout_4.addStretch()
                
    def updateFields(self, **kwargs):
        self.HostStateText.setText(kwargs.get('status') or 'unknown')
        self.OpenPortsText.setText(str(kwargs.get('openPorts') or 0))
        self.ClosedPortsText.setText(str(kwargs.get('closedPorts') or 0))
        self.FilteredPortsText.setText(str(kwargs.get('filteredPorts') or 0))
        self.IP4Text.setText(kwargs.get('ipv4') or 'unknown')
        self.IP6Text.setText(kwargs.get('ipv6') or 'unknown')
        self.MacText.setText(kwargs.get('macaddr') or 'unknown')
        self.AsnText.setText(kwargs.get('asn') or 'unknown')
        self.IspText.setText(kwargs.get('isp') or 'unknown')
        self.OSNameText.setText(kwargs.get('osMatch') or 'unknown')
        self.OSAccuracyText.setText(kwargs.get('osAccuracy') or 'unknown')
