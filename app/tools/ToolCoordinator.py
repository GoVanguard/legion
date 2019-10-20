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
import ntpath

from app.shell.Shell import Shell
from app.tools.nmap.NmapExporter import NmapExporter
from app.tools.nmap.NmapHelpers import nmapFileExists


def xmlFileExists(shell: Shell, fileName: str) -> bool:
    return fileExists(shell, f"{fileName}.xml")


def textFileExists(shell: Shell, fileName: str) -> bool:
    return fileExists(shell, f"{fileName}.txt")


def fileExists(shell: Shell, fileName) -> bool:
    return shell.directoryOrFileExists(fileName) and shell.isFile(fileName)


class ToolCoordinator:
    def __init__(self, shell: Shell, nmapExporter: NmapExporter):
        self.shell = shell
        self.nmapExporter = nmapExporter

    # this function moves the specified tool output file from the temporary 'running' folder
    # to the 'tool output' folder
    def saveToolOutput(self, projectOutputFolder: str, outputFileName: str) -> None:
        tool = self.__determineToolUsedByOutputFilename(outputFileName)
        toolOutputFolder = f"{projectOutputFolder}/{tool}"
        self.__createToolOutputFolderIfNotExists(toolOutputFolder)
        self.__determineToolOutputFiles(outputFileName, toolOutputFolder)

    def __determineToolOutputFiles(self, outputFileName: str, toolOutputFolder: str):
        # check if the outputFilename exists, if not try .xml and .txt extensions
        # (different tools use different formats)
        if fileExists(self.shell, outputFileName):
            self.shell.move(outputFileName, toolOutputFolder)
        # move all the nmap files (not only the .xml)
        elif nmapFileExists(self.shell, outputFileName):
            self.nmapExporter.exportOutputToHtml(outputFileName, toolOutputFolder)
            self.shell.move(outputFileName + '.xml', toolOutputFolder)
            self.shell.move(outputFileName + '.nmap', toolOutputFolder)
            self.shell.move(outputFileName + '.gnmap', toolOutputFolder)
        elif xmlFileExists(self.shell, outputFileName):
            self.shell.move(outputFileName + '.xml', toolOutputFolder)
        elif textFileExists(self.shell, outputFileName):
            self.shell.move(outputFileName + '.txt', toolOutputFolder)

    @staticmethod
    def __determineToolUsedByOutputFilename(outputFileName) -> str:
        return ntpath.basename(ntpath.dirname(outputFileName))

    def __createToolOutputFolderIfNotExists(self, toolOutputFolder: str) -> None:
        if not self.shell.directoryOrFileExists(toolOutputFolder):
            self.shell.create_directory_recursively(toolOutputFolder)
