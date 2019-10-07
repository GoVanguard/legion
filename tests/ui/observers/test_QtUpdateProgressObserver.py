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
from unittest.mock import patch


class QtUpdateProgressObserverTest(unittest.TestCase):
    @patch("ui.ancillaryDialog.ProgressWidget")
    @patch('utilities.stenoLogging.get_logger')
    def setUp(self, mockProgressWidget, mockLogging) -> None:
        from ui.observers.QtUpdateProgressObserver import QtUpdateProgressObserver
        self.mockProgressWidget = mockProgressWidget
        self.qtUpdateProgressObserver = QtUpdateProgressObserver(self.mockProgressWidget)

    def test_onStart_callsShowOnProgressWidget(self):
        self.qtUpdateProgressObserver.onStart()
        self.mockProgressWidget.show.assert_called_once()

    def test_onFinished_callsHideOnProgressWidget(self):
        self.qtUpdateProgressObserver.onFinished()
        self.mockProgressWidget.hide.assert_called_once()

    def test_onProgressUpdate_callsSetProgressAndShow(self):
        self.qtUpdateProgressObserver.onProgressUpdate(25)
        self.mockProgressWidget.setProgress.assert_called_once_with(25)
        self.mockProgressWidget.show.assert_called_once()
