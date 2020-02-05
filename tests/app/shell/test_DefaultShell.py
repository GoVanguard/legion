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

Author(s): Dmitriy Dubson (d.dubson@gmail.com)
"""
import unittest
import os.path


class DefaultShellTest(unittest.TestCase):
    def setUp(self) -> None:
        from app.shell.DefaultShell import DefaultShell
        self.shell = DefaultShell()

    def test_isDirectory_whenProvidedADirectory_ReturnsTrue(self):
        os.path.isdir = lambda name: True
        self.assertTrue(self.shell.isDirectory("some-directory"))

    def test_isDirectory_whenProvidedAFile_ReturnsFalse(self):
        os.path.isdir = lambda name: False
        self.assertFalse(self.shell.isDirectory("some-file"))

    def test_isFile_whenProvidedAFile_ReturnsTrue(self):
        os.path.isfile = lambda name: True
        self.assertTrue(self.shell.isFile("some-file"))

    def test_isFile_whenProvidedAFile_ReturnsFalse(self):
        os.path.isfile = lambda name: False
        self.assertFalse(self.shell.isFile("some-directory"))
