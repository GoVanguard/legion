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

Author(s): Dmitriy Dubson (d.dubson@gmail.com)
"""
import unittest
from unittest import mock
from unittest.mock import MagicMock, Mock, patch

from PyQt5.QtCore import QEvent, Qt, QObject
from PyQt5.QtWidgets import QApplication

from ui.eventfilter import MyEventFilter


class MyEventFilterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_view = MagicMock()
        self.mock_main_window = MagicMock()
        self.mock_event = MagicMock()
        self.mock_receiver = MagicMock()

    def test_eventFilter_whenKeyPressedIsClose_InvokesAppExit(self):
        event_filter = MyEventFilter(self.mock_view, self.mock_main_window)
        self.mock_event.type = Mock(return_value=QEvent.Close)

        result = event_filter.eventFilter(self.mock_main_window, self.mock_event)
        self.assertTrue(result)
        self.mock_event.ignore.assert_called_once()
        self.mock_view.appExit.assert_called_once()

    @patch('PyQt5.QtWidgets.QTableView')
    @patch('PyQt5.QtWidgets.QAbstractItemView')
    @patch('PyQt5.QtCore.QModelIndex')
    def test_eventFilter_whenKeyDownPressed_SelectsNextRowAndEmitsClickEvent(
            self, hosts_table_view, selection_model, selected_row):
        self.mock_view.ui.HostsTableView = hosts_table_view
        event_filter = MyEventFilter(self.mock_view, self.mock_main_window)
        self.simulateKeyPress(Qt.Key_Down)
        self.mock_receiver = hosts_table_view
        selected_row.row = Mock(return_value=0)
        selection_model.selectedRows = Mock(return_value=[selected_row])
        self.mock_receiver.selectionModel = Mock(return_value=selection_model)

        result = event_filter.eventFilter(self.mock_receiver, self.mock_event)
        self.assertTrue(result)
        self.mock_receiver.selectRow.assert_called_once_with(1)
        self.mock_receiver.clicked.emit.assert_called_with(selected_row)

    @patch('PyQt5.QtWidgets.QTableView')
    @patch('PyQt5.QtWidgets.QAbstractItemView')
    @patch('PyQt5.QtCore.QModelIndex')
    def test_eventFilter_whenKeyUpPressed_SelectsPreviousRowAndEmitsClickEvent(
            self, hosts_table_view, selection_model, selected_row):
        self.mock_view.ui.HostsTableView = hosts_table_view
        event_filter = MyEventFilter(self.mock_view, self.mock_main_window)
        self.simulateKeyPress(Qt.Key_Up)
        self.mock_receiver = hosts_table_view
        selected_row.row = Mock(return_value=1)
        selection_model.selectedRows = Mock(return_value=[selected_row])
        self.mock_receiver.selectionModel = Mock(return_value=selection_model)

        result = event_filter.eventFilter(self.mock_receiver, self.mock_event)
        self.assertTrue(result)
        self.mock_receiver.selectRow.assert_called_once_with(0)
        self.mock_receiver.clicked.emit.assert_called_with(selected_row)

    @patch('PyQt5.QtWidgets.QTableView')
    @patch('PyQt5.QtWidgets.QAbstractItemView')
    @patch('PyQt5.QtCore.QModelIndex')
    @patch('PyQt5.QtGui.QClipboard')
    def test_eventFilter_whenKeyCPressed_SelectsPreviousRowAndEmitsClickEvent(
            self, hosts_table_view, selection_model, selected_row, mock_clipboard):
        expected_data = MagicMock()
        expected_data.toString = Mock(return_value="some clipboard data")
        control_modifier = mock.patch.object(QApplication, 'keyboardModifiers', return_value=Qt.ControlModifier)
        clipboard = mock.patch.object(QApplication, 'clipboard', return_value=mock_clipboard)

        self.mock_view.ui.HostsTableView = hosts_table_view
        event_filter = MyEventFilter(self.mock_view, self.mock_main_window)
        self.simulateKeyPress(Qt.Key_C)
        self.mock_receiver = hosts_table_view
        selected_row.data = Mock(return_value=expected_data)
        selection_model.currentIndex = Mock(return_value=selected_row)
        self.mock_receiver.selectionModel = Mock(return_value=selection_model)

        with control_modifier, clipboard:
            result = event_filter.eventFilter(self.mock_receiver, self.mock_event)
            self.assertTrue(result)
            mock_clipboard.setText.assert_called_once_with("some clipboard data")

    def test_eventFilter_onDefaultAction_CallsParentEventFilter(self):
        event_filter = MyEventFilter(self.mock_view, self.mock_main_window)
        result = event_filter.eventFilter(QObject(), QEvent(QEvent.Scroll))
        self.assertFalse(result)

    def simulateKeyPress(self, key_event):
        self.mock_event.type = Mock(return_value=QEvent.KeyPress)
        self.mock_event.key = Mock(return_value=key_event)
