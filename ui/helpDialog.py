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

import os
from PyQt5.QtGui import *                                               # for filters dialog
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtGui
from app.auxiliary import *                                             # for timestamps
from six import u as unicode
from ui.ancillaryDialog import flipState

class License(QtWidgets.QPlainTextEdit):
    def __init__(self,parent = None):
        super(License, self).__init__(parent)
        self.setReadOnly(True)
        self.setWindowTitle('License')
        self.setGeometry(0, 0, 300, 300)
        self.center()
        self.setPlainText(open('LICENSE','r').read())

    def center(self):
        frameGm = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

class ChangeLog(QtWidgets.QPlainTextEdit):
    def __init__(self, qss, parent = None):
        super(ChangeLog, self).__init__(parent)
        self.setMinimumHeight(240)
        self.setStyleSheet(qss)
        self.setPlainText(open('CHANGELOG.txt','r').read())
        self.setReadOnly(True)

class HelpDialog(QtWidgets.QDialog):
    def __init__(self, name, author, copyright, links, emails, version, build, update, license, desc, smallIcon,
                 bigIcon, qss, parent = None):
        super(HelpDialog, self).__init__(parent)
        self.name = name
        self.author = author
        self.copyright = copyright
        self.links = links
        self.emails = emails
        self.version = version
        self.build = build
        self.update = update
        self.desc = QtWidgets.QLabel(desc)
        self.smallIcon = smallIcon
        self.bigIcon = bigIcon
        self.qss = qss
        self.setWindowTitle("About {0}".format(self.name))
        self.Main = QtWidgets.QVBoxLayout()
        self.frm = QtWidgets.QFormLayout()
        self.setGeometry(0, 0, 350, 400)
        self.center()
        self.Qui_update()
        self.setStyleSheet(self.qss)

    def center(self):
        frameGm = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def Qui_update(self):
        self.logoapp = QtWidgets.QLabel('')
        self.logoapp.setPixmap(QtGui.QPixmap(self.smallIcon).scaled(64,64))
        self.form = QtWidgets.QFormLayout()
        self.form2 = QtWidgets.QVBoxLayout()
        self.form.addRow(self.logoapp,QtWidgets.QLabel('<h2>{0} {1}-{2}</h2>'.format(self.name,
                                                                                     self.version, self.build)))
        self.tabwid = QtWidgets.QTabWidget(self)
        self.TabAbout = QtWidgets.QWidget(self)
        self.TabVersion = QtWidgets.QWidget(self)
        self.TabChangelog = QtWidgets.QWidget(self)
        self.cmdClose = QtWidgets.QPushButton("Close")
        self.cmdClose.setFixedWidth(90)
        self.cmdClose.setIcon(QtGui.QIcon('images/close.png'))
        self.cmdClose.clicked.connect(self.close)

        self.formAbout = QtWidgets.QFormLayout()
        self.formVersion = QtWidgets.QFormLayout()
        self.formChange = QtWidgets.QFormLayout()

        # About section
        self.formAbout.addRow(self.desc)
        self.formAbout.addRow(QtWidgets.QLabel('<br>'))
        self.formAbout.addRow(QtWidgets.QLabel('Last Update:'))
        self.formAbout.addRow(QtWidgets.QLabel(self.update + '<br>'))
        self.formAbout.addRow(QtWidgets.QLabel('Feedback:'))
        for link in self.links:
            self.formAbout.addRow(QtWidgets.QLabel('<a href="{0}">{0}</a>'.format(link)))
        for email in self.emails:
            self.formAbout.addRow(QtWidgets.QLabel(email))
        self.formAbout.addRow(QtWidgets.QLabel('<br>'))
        self.formAbout.addRow(QtWidgets.QLabel(self.copyright + ' ' + self.author))
        self.gnu = QtWidgets.QLabel('<a href="link">License: GNU General Public License Version</a><br>')
        self.gnu.linkActivated.connect(self.link)
        self.formAbout.addRow(self.gnu)
        self.TabAbout.setLayout(self.formAbout)

        # Version Section
        self.formVersion.addRow(QtWidgets.QLabel('<strong>Version: {0}-{1}</strong><br>'.format(self.version,
                                                                                                self.build)))
        self.formVersion.addRow(QtWidgets.QLabel('Using:'))
        import platform
        python_version = platform.python_version()
        self.formVersion.addRow(QtWidgets.QLabel('''
        <ul>
          <li>QTVersion: {0}</li>
          <li>Python: {1}</li>
        </ul>'''.format(QtCore.QT_VERSION_STR,python_version)))
        self.TabVersion.setLayout(self.formVersion)

        # Changelog Section
        self.formChange.addRow(ChangeLog(qss = self.qss))
        self.TabChangelog.setLayout(self.formChange)

        self.tabwid.addTab(self.TabAbout,'About')
        self.tabwid.addTab(self.TabVersion,'Version')
        self.tabwid.addTab(self.TabChangelog,'ChangeLog')
        self.form.addRow(self.tabwid)
        self.form2.addWidget(QtWidgets.QLabel('<br>'))
        self.form2.addWidget(self.cmdClose, alignment = Qt.AlignCenter)
        self.form.addRow(self.form2)
        self.Main.addLayout(self.form)
        self.setLayout(self.Main)

    def link(self):
        self.formLicense = License()
        self.formLicense.show()
