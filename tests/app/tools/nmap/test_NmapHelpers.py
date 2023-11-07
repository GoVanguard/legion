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
from unittest.mock import MagicMock

from app.tools.nmap.NmapHelpers import nmapFileExists


class NmapHelpersTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mockShell = MagicMock()

    def test_nmapFileExists_WhenNecessaryNmapFilesExistOnFilesystem_ReturnsTrue(self):
        def makeAllNecessaryNmapFilesExist():
            self.mockShell.directoryOrFileExists.side_effect = [True, True, True]
            self.mockShell.isFile.side_effect = [True, True, True]

        makeAllNecessaryNmapFilesExist()
        self.assertTrue(nmapFileExists(self.mockShell, "some-nmap-session"))

    def test_nmapFileExists_WhenAtLeastOneNmapFileDoesNotExist_ReturnsFalse(self):
        def makeAtLeastOneNmapFileNotPresent():
            self.mockShell.directoryOrFileExists.side_effect = [True, True, True]
            self.mockShell.isFile.side_effect = [True, True, False]

        makeAtLeastOneNmapFileNotPresent()
        self.assertFalse(nmapFileExists(self.mockShell, "some-nmap-session"))
