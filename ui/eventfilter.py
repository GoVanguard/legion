"""
LEGION (https://govanguard.com)
Copyright (c) 2022 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
    version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
    details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <http://www.gnu.org/licenses/>.
"""
from PyQt5.QtCore import QObject, QEvent, Qt
from PyQt5.QtWidgets import QApplication


# This class is used to catch events such as arrow key presses or close window (X)
class MyEventFilter(QObject):
    def __init__(self, view, main_window):
        super().__init__()
        self.view = view
        self.main_window = main_window
        self.hosts_table_views = {
            view.ui.HostsTableView,
            view.ui.ServiceNamesTableView,
            view.ui.ToolsTableView,
            view.ui.ToolHostsTableView,
            view.ui.ScriptsTableView,
            view.ui.ServicesTableView,
            view.settingsWidget.toolForHostsTableWidget,
            view.settingsWidget.toolForServiceTableWidget,
            view.settingsWidget.toolForTerminalTableWidget,
        }

    def eventFilter(self, receiver, event):
        # catch up/down arrow key presses in hosts table
        if event.type() == QEvent.KeyPress and receiver in self.hosts_table_views:
            return self.filterKeyPressInHostsTableView(event.key(), receiver)
        elif event.type() == QEvent.Close and receiver == self.main_window:
            event.ignore()
            self.view.appExit()
            return True
        else:
            parent = super(MyEventFilter, self)
            return parent.eventFilter(receiver, event)  # normal event processing

    def filterKeyPressInHostsTableView(self, key, receiver):
        if not receiver.selectionModel().selectedRows():
            return True

        index = receiver.selectionModel().selectedRows()[0].row()

        if key == Qt.Key_Down:
            new_index = index + 1
            receiver.selectRow(new_index)
            receiver.clicked.emit(receiver.selectionModel().selectedRows()[0])
        elif key == Qt.Key_Up:
            new_index = index - 1
            receiver.selectRow(new_index)
            receiver.clicked.emit(receiver.selectionModel().selectedRows()[0])
        elif QApplication.keyboardModifiers() == Qt.ControlModifier and key == Qt.Key_C:
            selected = receiver.selectionModel().currentIndex()
            clipboard = QApplication.clipboard()
            clipboard.setText(selected.data().toString())
        return True
