#!/usr/bin/env python

'''
LEGION (https://govanguard.io)
Copyright (c) 2018 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

# check for dependencies first (make sure all non-standard dependencies are checked for here)
try:
    from sqlalchemy.orm.scoping import ScopedSession as scoped_session
    #import elixir
except ImportError as e:
    log.info("Import failed. SQL Alchemy library not found. If on Ubuntu or similar try: apt-get install python3-sqlalchemy*")
    exit(1)
    
try:
    from PyQt5 import QtWidgets, QtGui, QtCore
except ImportError as e:
    log.info("Import failed. PyQt4 library not found. If on Ubuntu or similar try: agt-get install python3-pyqt4")
    log.info(e)
    exit(1)

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
except ImportError as e:
    try:
        #from PySide import QtWebKit
        pass
    except ImportError:
        log.info("Import failed. QtWebKit library not found. If on Ubuntu or similar try: agt-get install python3-pyside.qtwebkit")
        exit(1)
    
from app.logic import *
from ui.gui import *
from ui.view import *
from controller.controller import *
import quamash
import asyncio

# this class is used to catch events such as arrow key presses or close window (X)
class MyEventFilter(QObject):
    
    def eventFilter(self, receiver, event):
        # catch up/down arrow key presses in hoststable
        if(event.type() == QEvent.KeyPress and (receiver == view.ui.HostsTableView or receiver == view.ui.ServiceNamesTableView or receiver == view.ui.ToolsTableView or receiver == view.ui.ToolHostsTableView or receiver == view.ui.ScriptsTableView or receiver == view.ui.ServicesTableView or receiver == view.settingsWidget.toolForHostsTableWidget or receiver == view.settingsWidget.toolForServiceTableWidget or receiver == view.settingsWidget.toolForTerminalTableWidget)):
            key = event.key()
            if not receiver.selectionModel().selectedRows():
                return True
            index = receiver.selectionModel().selectedRows()[0].row()
            
            if key == QtCore.Qt.Key_Down:
                newindex = index + 1
                receiver.selectRow(newindex)
                receiver.clicked.emit(receiver.selectionModel().selectedRows()[0])

            elif key == QtCore.Qt.Key_Up:
                newindex = index - 1
                receiver.selectRow(newindex)
                receiver.clicked.emit(receiver.selectionModel().selectedRows()[0])

            elif QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier and key == QtCore.Qt.Key_C:    
                selected = receiver.selectionModel().currentIndex()
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(selected.data().toString())

            return True
            
        elif(event.type() == QEvent.Close and receiver == MainWindow):
            event.ignore()
            view.appExit()
            return True
            
        else:      
            return super(MyEventFilter,self).eventFilter(receiver, event)   # normal event processing


if __name__ == "__main__":

    app = QApplication(sys.argv)
    #loop = quamash.QEventLoop(app)
    #asyncio.set_event_loop(loop)

    #with loop:
    myFilter = MyEventFilter()                      # to capture events
    app.installEventFilter(myFilter)
    MainWindow = QtWidgets.QMainWindow()
    app.setWindowIcon(QIcon('./images/icons/legion_medium.svg'))

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    try:
        qss_file = open('./ui/legion.qss').read()
    except IOError as e:
        log.info("The legion.qss file is missing. Your installation seems to be corrupted. Try downloading the latest version.")
        exit(0)

    MainWindow.setStyleSheet(qss_file)

    logic = Logic()                                 # Model prep (logic, db and models)
    view = View(ui, MainWindow)                     # View prep (gui)
    controller = Controller(view, logic)            # Controller prep (communication between model and view)

    MainWindow.show()
        #log.addHandler(ui.LogOutputTextView)

        #loop.run_forever()
    sys.exit(app.exec_())
