#!/usr/bin/env python

'''
LEGION (https://govanguard.io)
Copyright (c) 2018 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
from PyQt5.QtGui import *                                               # for filters dialog
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtGui
from app.auxiliary import *                                             # for timestamps
from six import u as unicode
from ui.ancillaryDialog import flipState

# dialog shown when the user selects "Add host(s)" from the menu
class AddHostsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupLayout()
        
    def setupLayout(self):
        self.setModal(True)
        self.setWindowTitle('Add host(s) to scan seperated by semicolons')
        self.setFixedSize(700, 700)

        self.formLayout = QtWidgets.QVBoxLayout()
        
        self.lblHost = QtWidgets.QLabel(self)
        self.lblHost.setText('IP(s), Range(s), and Host(s)')
        self.txtHostList = QtWidgets.QPlainTextEdit(self)

        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.lblHost)
        self.hlayout.addWidget(self.txtHostList)        
        
        self.lblHostExample = QtWidgets.QLabel(self)
        self.lblHostExample.setText('Ex: 192.168.1.0/24; 10.10.10.10-20; 1.2.3.4; bing.com')
        self.font = QtGui.QFont('Calibri', 10)
        self.lblHostExample.setFont(self.font)
        self.lblHostExample.setAlignment(Qt.AlignRight)
        self.spacer = QSpacerItem(15,15)

        self.validationLabel = QtWidgets.QLabel(self)
        self.validationLabel.setText('Invalid input. Please try again!')
        self.validationLabel.setStyleSheet('QLabel { color: red }')

        self.spacer2 = QSpacerItem(5,5)

        # Mode
        self.grpMode = QtWidgets.QGroupBox()
        self.grpModeWidgets = QtWidgets.QHBoxLayout()
        self.grpMode.setTitle('Mode Selection')
        self.rdoModeOptEasy = QtWidgets.QRadioButton(self)
        self.rdoModeOptEasy.setText('Easy')
        self.rdoModeOptEasy.setToolTip('Easy mode [--lame]')
        self.rdoModeOptHard = QtWidgets.QRadioButton(self)
        self.rdoModeOptHard.setText('Hard')
        self.rdoModeOptHard.setToolTip('Hard mode')
        self.grpModeWidgets.addWidget(self.rdoModeOptEasy)
        self.grpModeWidgets.addWidget(self.rdoModeOptHard)
        self.grpMode.setLayout(self.grpModeWidgets)
        self.rdoModeOptEasy.toggle()

        # Easy mode options
        self.grpEasyMode = QtWidgets.QGroupBox()
        self.grpEasyModeWidgets = QtWidgets.QHBoxLayout()
        self.grpEasyMode.setTitle('Easy Mode Options')
        self.chkDiscovery = QtWidgets.QCheckBox(self)
        self.chkDiscovery.setText('Run nmap host discovery')
        self.chkDiscovery.setToolTip('Typical host discovery options')
        self.chkDiscovery.toggle()
        self.chkNmapStaging = QtWidgets.QCheckBox(self)
        self.chkNmapStaging.setText('Run staged nmap scan')
        self.chkNmapStaging.setToolTip('Scan ports in stages with typical options')
        self.chkNmapStaging.toggle()
        self.grpEasyModeWidgets.addWidget(self.chkDiscovery)
        self.grpEasyModeWidgets.addWidget(self.chkNmapStaging)
        self.grpEasyMode.setLayout(self.grpEasyModeWidgets)
        self.grpEasyMode.setEnabled(True)

        self.spacer3 = QSpacerItem(5,5)

        # Timing and performance options
        self.grpScanTiming = QtWidgets.QGroupBox()
        self.grpScanTimingWidgets = QtWidgets.QVBoxLayout()
        self.grpScanTimingControlWidgets = QtWidgets.QHBoxLayout()
        self.grpScanTimingLabelWidgets = QtWidgets.QHBoxLayout()
        self.grpScanTiming.setTitle('Timing and Performance Options')
        self.grpScanTimingSpacer = QSpacerItem(5,5)
        self.lblScanTimingLabel0 = QtWidgets.QLabel()
        self.lblScanTimingLabel1 = QtWidgets.QLabel()
        self.lblScanTimingLabel2 = QtWidgets.QLabel()
        self.lblScanTimingLabel3 = QtWidgets.QLabel()
        self.lblScanTimingLabel4 = QtWidgets.QLabel()
        self.lblScanTimingLabel5 = QtWidgets.QLabel()
        self.lblScanTimingLabel0.setText("Paranoid")
        self.lblScanTimingLabel0.setToolTip('Serialize every scan operation with a 5 minute wait between each. Useful for evading IDS detection [-T0]')
        self.lblScanTimingLabel1.setText("Sneaky")
        self.lblScanTimingLabel1.setToolTip('Serialize every scan operation with a 15 second wait between each. Useful for evading IDS detection [-T1]')
        self.lblScanTimingLabel2.setText("Polite")
        self.lblScanTimingLabel2.setToolTip('Serialize every scan operation with a 0.4 second wait between each. Useful for evading IDS detection [-T2]')
        self.lblScanTimingLabel3.setText("Normal")
        self.lblScanTimingLabel3.setToolTip('NMAP defaults including parallelization [-T3]')
        self.lblScanTimingLabel4.setText("Aggressive")
        self.lblScanTimingLabel4.setToolTip('Sets the following options: --max-rtt-timeout 1250ms --min-rtt-timeout 100ms --initial-rtt-timeout 500ms --max-retries 6 with a 10ms delay between operations [-T4]')
        self.lblScanTimingLabel5.setText("Insane")
        self.lblScanTimingLabel5.setToolTip('Sets the following options: --max-rtt-timeout 300ms --min-rtt-timeout 50ms --initial-rtt-timeout 250ms --max-retries 2 --host-timeout 15m --script-timeout 10m with a 5ms delay between operations [-T5]')
        self.sldScanTimingSlider = QtWidgets.QSlider(Qt.Horizontal)
        self.sldScanTimingSlider.setRange(0, 5)
        self.sldScanTimingSlider.setSingleStep(1)
        self.sldScanTimingSlider.setValue(4)
        self.grpScanTimingControlWidgets.addWidget(self.sldScanTimingSlider)
        self.grpScanTimingControlWidgets.addItem(self.grpScanTimingSpacer)
        self.grpScanTimingLabelWidgets.addWidget(self.lblScanTimingLabel0)
        self.grpScanTimingLabelWidgets.addWidget(self.lblScanTimingLabel1)
        self.grpScanTimingLabelWidgets.addWidget(self.lblScanTimingLabel2)
        self.grpScanTimingLabelWidgets.addWidget(self.lblScanTimingLabel3)
        self.grpScanTimingLabelWidgets.addWidget(self.lblScanTimingLabel4)
        self.grpScanTimingLabelWidgets.addWidget(self.lblScanTimingLabel5)
        self.grpScanTimingLabelWidgets.setSpacing(45)
        self.grpScanTimingWidgets.addLayout(self.grpScanTimingControlWidgets)
        self.grpScanTimingWidgets.addLayout(self.grpScanTimingLabelWidgets)
        self.grpScanTiming.setLayout(self.grpScanTimingWidgets)

        self.spacer3_5 = QSpacerItem(5,5)

        # Port scan options
        self.rdoScanOptTcpConnect = QtWidgets.QRadioButton(self)
        self.rdoScanOptTcpConnect.setText('TCP')
        self.rdoScanOptTcpConnect.setToolTip('TCP connect() scanning [-sT]')
        self.rdoScanOptSynStealth = QtWidgets.QRadioButton(self)
        self.rdoScanOptSynStealth.setText('Stealth SYN')
        self.rdoScanOptSynStealth.setToolTip('SYN scanning (also known as half-open, or stealth scanning) [-sS]')
        self.rdoScanOptFin = QtWidgets.QRadioButton(self)
        self.rdoScanOptFin.setText('FIN')
        self.rdoScanOptFin.setToolTip('FIN scanning sends a packet with only the FIN flag set [-sF]')
        self.rdoScanOptNull = QtWidgets.QRadioButton(self)
        self.rdoScanOptNull.setText('NULL')
        self.rdoScanOptNull.setToolTip('Null scanning sends a packet with no flags switched on [-sN]')
        self.rdoScanOptXmas = QtWidgets.QRadioButton(self)
        self.rdoScanOptXmas.setText('Xmas')
        self.rdoScanOptXmas.setToolTip('Xmas Tree scanning sets the FIN, URG and PUSH flags [-sX]')
        self.rdoScanOptPingTcp = QtWidgets.QRadioButton(self)
        self.rdoScanOptPingTcp.setText('TCP Ping')
        self.rdoScanOptPingTcp.setToolTip('TCP Ping scanning sends either a SYN or an ACK packet to any port (80 is the default) on the remote system [-sP]')
        self.rdoScanOptPingUdp = QtWidgets.QRadioButton(self)
        self.rdoScanOptPingUdp.setText('UDP Ping')
        self.rdoScanOptPingUdp.setToolTip('UDP Ping scanning sends 0-byte UDP packets to each target port on the victim. Receipt of an ICMP Port Unreachable message signifies the port is closed, otherwise it is assumed open [-sU]')

        # Fragmentation option
        self.chkScanOptFragmentation = QtWidgets.QCheckBox(self)
        self.chkScanOptFragmentation.setText('Fragment')
        self.chkScanOptFragmentation.toggle()

        # Port scan options
        self.grpScanOpt = QtWidgets.QGroupBox()
        self.grpScanOptWidgets = QtWidgets.QHBoxLayout()
        self.grpScanOpt.setTitle('Port Scan Options')
        self.grpScanOptWidgets.addWidget(self.rdoScanOptTcpConnect)
        self.grpScanOptWidgets.addWidget(self.rdoScanOptSynStealth)
        self.grpScanOptWidgets.addWidget(self.rdoScanOptFin)
        self.grpScanOptWidgets.addWidget(self.rdoScanOptNull)
        self.grpScanOptWidgets.addWidget(self.rdoScanOptXmas)
        self.grpScanOptWidgets.addWidget(self.rdoScanOptPingTcp)
        self.grpScanOptWidgets.addWidget(self.rdoScanOptPingUdp)
        self.grpScanOptWidgets.addWidget(self.chkScanOptFragmentation)
        self.grpScanOpt.setLayout(self.grpScanOptWidgets)
        self.rdoScanOptSynStealth.toggle()
        self.grpScanOpt.setEnabled(False)

        self.spacer4 = QSpacerItem(5,5)

        self.rdoScanOptPingDisable = QtWidgets.QRadioButton(self)
        self.rdoScanOptPingDisable.setText('Disable')
        self.rdoScanOptPingDisable.setToolTip('Disable Ping entirely [-P0 | -Pn]')
        self.rdoScanOptPingDefault = QtWidgets.QRadioButton(self)
        self.rdoScanOptPingDefault.setText('Default')
        self.rdoScanOptPingDefault.setToolTip('ICMP Echo Request and TCP ping, with ACK packets [-PB]')
        self.rdoScanOptPingRegular = QtWidgets.QRadioButton(self)
        self.rdoScanOptPingRegular.setText('ICMP')
        self.rdoScanOptPingRegular.setToolTip('Standard ICMP Echo Request [-PE]')
        self.rdoScanOptPingSyn = QtWidgets.QRadioButton(self)
        self.rdoScanOptPingSyn.setText('TCP SYN')
        self.rdoScanOptPingSyn.setToolTip('TCP Ping that sends SYN packets instead of ACK packets [-PT -PS]')
        self.rdoScanOptPingAck = QtWidgets.QRadioButton(self)
        self.rdoScanOptPingAck.setText('TCP ACK')
        self.rdoScanOptPingAck.setToolTip('TCP Ping that sends SYN packets instead of ACK packets [-PT]')
        self.rdoScanOptPingTimeStamp = QtWidgets.QRadioButton(self)
        self.rdoScanOptPingTimeStamp.setText('Timestamp')
        self.rdoScanOptPingTimeStamp.setToolTip('ICMP Timestamp Request [-PP]')
        self.rdoScanOptPingNetmask = QtWidgets.QRadioButton(self)
        self.rdoScanOptPingNetmask.setText('Netmask')
        self.rdoScanOptPingNetmask.setToolTip('ICMP Netmask Request [-PM]')
        
        self.grpScanOptPing = QtWidgets.QGroupBox()
        self.grpScanOptPingWidgets = QtWidgets.QHBoxLayout()
        self.grpScanOptPing.setTitle('Host Discovery Options')
        self.grpScanOptPingWidgets.addWidget(self.rdoScanOptPingDisable)
        self.grpScanOptPingWidgets.addWidget(self.rdoScanOptPingDefault)
        self.grpScanOptPingWidgets.addWidget(self.rdoScanOptPingRegular)
        self.grpScanOptPingWidgets.addWidget(self.rdoScanOptPingSyn)
        self.grpScanOptPingWidgets.addWidget(self.rdoScanOptPingAck)
        self.grpScanOptPingWidgets.addWidget(self.rdoScanOptPingTimeStamp)
        self.grpScanOptPingWidgets.addWidget(self.rdoScanOptPingNetmask)
        self.grpScanOptPing.setLayout(self.grpScanOptPingWidgets)
        self.rdoScanOptPingSyn.toggle()
        self.grpScanOptPing.setEnabled(False)

        self.spacer6 = QSpacerItem(5,5)

        # Custom scan options
        self.scanOptCustomGroup = QtWidgets.QGroupBox()
        self.scanOptCustomGroupWidgets = QtWidgets.QHBoxLayout()
        self.scanOptCustomGroup.setTitle('Custom Options')
        self.lblCustomOpt = QtWidgets.QLabel(self)
        self.lblCustomOpt.setText('Additional arguments')
        self.txtCustomOptList = QtWidgets.QLineEdit(self)
        self.txtCustomOptList.setText("-sV -O")
        self.scanOptCustomGroupWidgets.addWidget(self.lblCustomOpt)
        self.scanOptCustomGroupWidgets.addWidget(self.txtCustomOptList)
        self.scanOptCustomGroup.setLayout(self.scanOptCustomGroupWidgets)
        self.scanOptCustomGroup.setEnabled(False)

        self.cmdAddButton = QPushButton('Submit', self)
        self.cmdAddButton.setMaximumSize(160, 70)
        self.cmdCancelButton = QPushButton('Cancel', self)
        self.cmdCancelButton.setMaximumSize(110, 30)
        self.cmdAddButton.setDefault(True)
        self.hlayout2 = QtWidgets.QHBoxLayout()
        self.hlayout2.addWidget(self.cmdAddButton)
        self.hlayout2.addWidget(self.cmdCancelButton)
        self.formLayout.addLayout(self.hlayout)
        self.formLayout.addWidget(self.lblHostExample)

        self.formLayout.addWidget(self.validationLabel)
        self.validationLabel.hide()

        self.formLayout.addWidget(self.grpMode)
        self.formLayout.addItem(self.spacer)
        self.formLayout.addWidget(self.grpEasyMode)
        self.formLayout.addItem(self.spacer2)
        self.formLayout.addWidget(self.grpScanTiming)
        self.formLayout.addItem(self.spacer3_5)
        self.formLayout.addWidget(self.grpScanOpt)
        self.formLayout.addItem(self.spacer3)
        self.formLayout.addWidget(self.grpScanOptPing)
        self.formLayout.addItem(self.spacer6)
        self.formLayout.addWidget(self.scanOptCustomGroup)
        self.formLayout.addItem(self.spacer4)
        self.formLayout.addLayout(self.hlayout2)
        self.setLayout(self.formLayout)


        easyModeControls = [self.grpEasyMode]
        hardModeControls = [self.grpScanOpt, self.grpScanOptPing, self.scanOptCustomGroup]

        self.rdoModeOptHard.clicked.connect(lambda: flipState(targetState = self.rdoModeOptHard.isChecked(), widgetsToFlipOn = hardModeControls, widgetsToFlipOff = easyModeControls))
        self.rdoModeOptEasy.clicked.connect(lambda: flipState(targetState = self.rdoModeOptEasy.isChecked(), widgetsToFlipOn = easyModeControls, widgetsToFlipOff = hardModeControls))
