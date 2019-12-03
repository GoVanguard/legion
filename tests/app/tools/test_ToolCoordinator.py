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
from unittest.mock import MagicMock, patch


class ToolCoordinatorTest(unittest.TestCase):
    @patch("app.tools.nmap.NmapHelpers.nmapFileExists")
    def setUp(self, nmapFileExists) -> None:
        from app.tools.ToolCoordinator import ToolCoordinator
        self.mockShell = MagicMock()
        self.mockNmapExporter = MagicMock()
        self.nmapFileExists = nmapFileExists
        self.outputFolder = "some-output-folder"
        self.toolCoordinator = ToolCoordinator(self.mockShell, self.mockNmapExporter)

    @patch("ntpath.basename")
    def test_saveToolOutput_WhenGivenProjectOutputFolderAndNmapFileNameToSaveOutputIn_SavesOutputSuccessfully(self,
                                                                                                              basename):
        fileName = "some-output-nmap-file"

        basename.return_value = "nmap"
        self.mockShell.directoryOrFileExists.side_effect = [True, False, True, True, True]
        self.nmapFileExists.return_value = True

        self.toolCoordinator.saveToolOutput(self.outputFolder, fileName)
        self.mockNmapExporter.exportOutputToHtml.assert_called_once_with("some-output-nmap-file",
                                                                         "some-output-folder/nmap")
        self.mockShell.move.assert_has_calls([
            mock.call("some-output-nmap-file.xml", "some-output-folder/nmap"),
            mock.call("some-output-nmap-file.nmap", "some-output-folder/nmap"),
            mock.call("some-output-nmap-file.gnmap", "some-output-folder/nmap"),
        ])

    @patch("ntpath.basename")
    def test_saveToolOutput_WhenGivenProjectOutputDirAndGenericFileNameToSaveOutputIn_SavesOutputSuccessfully(self,
                                                                                                              basename):
        fileName = "some-output-file"
        basename.return_value = "some-tool"
        self.mockShell.directoryOrFileExists.side_effect = [False, True]
        self.mockShell.isFile.return_value = True

        self.toolCoordinator.saveToolOutput(self.outputFolder, fileName)
        self.mockShell.move.assert_called_once_with("some-output-file", "some-output-folder/some-tool")

    @patch("ntpath.basename")
    def test_saveToolOutput_WhenGivenProjectOutputFolderAndXmlFileNameToSaveOutputIn_SavesOutputSuccessfully(self,
                                                                                                             basename):
        fileName = "some-output-xml-file"
        basename.return_value = "some-tool"
        self.mockShell.directoryOrFileExists.side_effect = [False, False, False, True]
        self.mockShell.isFile.return_value = True

        self.toolCoordinator.saveToolOutput(self.outputFolder, fileName)
        self.mockShell.move.assert_called_once_with("some-output-xml-file.xml", "some-output-folder/some-tool")

    @patch("ntpath.basename")
    def test_saveToolOutput_WhenGivenProjectOutputFolderAndTxtFileNameToSaveOutputIn_SavesOutputSuccessfully(self,
                                                                                                             basename):
        fileName = "some-output-txt-file"
        basename.return_value = "some-tool"
        self.mockShell.directoryOrFileExists.side_effect = [False, False, False, False, True]
        self.mockShell.isFile.return_value = True

        self.toolCoordinator.saveToolOutput(self.outputFolder, fileName)
        self.mockShell.move.assert_called_once_with("some-output-txt-file.txt", "some-output-folder/some-tool")
