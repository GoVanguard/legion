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

Author(s): Shane Scott (sscott@gotham-security.com), Dmitriy Dubson (d.dubson@gmail.com)
"""
import unittest

from app.actions.updateProgress.AbstractUpdateProgressObserver import AbstractUpdateProgressObserver
from app.actions.updateProgress.UpdateProgressObservable import UpdateProgressObservable


class MockObserver(AbstractUpdateProgressObserver):
    started = False
    finished = False
    progress = 0

    def onProgressUpdate(self, progress) -> None:
        self.progress = progress

    def onStart(self) -> None:
        self.started = True

    def onFinished(self) -> None:
        self.finished = True


class UpdateProgressObservableTest(unittest.TestCase):
    def setUp(self) -> None:
        self.updateProgressObservable = UpdateProgressObservable()
        self.someObserver = MockObserver()
        self.anotherObserver = MockObserver()
        self.updateProgressObservable.attach(self.someObserver)
        self.updateProgressObservable.attach(self.anotherObserver)

    def test_start_notifiesAllObservers(self):
        self.assertFalse(self.someObserver.started)
        self.assertFalse(self.anotherObserver.started)
        self.updateProgressObservable.start()
        self.assertTrue(self.someObserver.started)
        self.assertTrue(self.anotherObserver.started)

    def test_finished_notifiesAllObservers(self):
        self.assertFalse(self.someObserver.finished)
        self.assertFalse(self.anotherObserver.finished)
        self.updateProgressObservable.finished()
        self.assertTrue(self.someObserver.finished)
        self.assertTrue(self.anotherObserver.finished)

    def test_updateProgress_notifiesAllObservers(self):
        self.assertEqual(0, self.someObserver.progress)
        self.assertEqual(0, self.anotherObserver.progress)
        self.updateProgressObservable.updateProgress(25)
        self.assertEqual(25, self.someObserver.progress)
        self.assertEqual(25, self.anotherObserver.progress)
