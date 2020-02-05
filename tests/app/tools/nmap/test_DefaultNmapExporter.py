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
from unittest.mock import MagicMock, patch


class DefaultNmapExporterTest(unittest.TestCase):
    @patch("app.logging.legionLog.log")
    def setUp(self, legionLog) -> None:
        from app.tools.nmap.DefaultNmapExporter import DefaultNmapExporter
        self.mockShell = MagicMock()
        self.log = legionLog
        self.nmapExporter = DefaultNmapExporter(self.mockShell)

    @patch("subprocess.Popen")
    def test_exportOutputToHtml_WhenProvidedFileNameAndOutputFolder_ExportsOutputSuccessfully(self, processOpen):
        exportCommand = f"xsltproc -o some-file.html nmap.xsl some-file.xml"
        self.nmapExporter.exportOutputToHtml("some-file", "some-folder/")
        processOpen.assert_called_once_with(exportCommand, shell=True)
        self.mockShell.move.assert_called_once_with("some-file.html", "some-folder/")

    @patch("subprocess.Popen")
    def test_exportOutputToHtml_WhenExportFailsDueToProcessError_DoesNotMoveAnyFilesToOutputFolder(self, processOpen):
        exportCommand = f"xsltproc -o some-bad-file.html nmap.xsl some-bad-file.xml"
        processOpen.side_effect = Exception("something went wrong")
        self.nmapExporter.exportOutputToHtml("some-bad-file", "some-folder/")
        processOpen.assert_called_once_with(exportCommand, shell=True)
        self.mockShell.move.assert_not_called()
        self.log.error.assert_called()

