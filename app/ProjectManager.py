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
import ntpath
import os
import sys
from typing import Tuple

from app.Project import Project, ProjectProperties
from app.tools.ToolCoordinator import fileExists
from app.auxiliary import Wordlist, getTempFolder
from app.shell.Shell import Shell
from app.tools.nmap.NmapPaths import getNmapRunningFolder
from db.RepositoryFactory import RepositoryFactory
from db.SqliteDbAdapter import Database

tempDirectory = getTempFolder()


class ProjectManager:
    def __init__(self, shell: Shell, repositoryFactory: RepositoryFactory, logger):
        self.shell = shell
        self.repositoryFactory = repositoryFactory
        self.logger = logger

    def createNewProject(self, projectType: str, isTemp: bool) -> Project:
        database = self.__createDatabase()
        workingDirectory = self.shell.get_current_working_directory()

        # to store tool output of finished processes
        outputFolder = self.shell.create_temporary_directory(prefix="legion-", suffix="-tool-output",
                                                             directory=tempDirectory)

        # to store tool output of running processes
        runningFolder = self.shell.create_temporary_directory(prefix="legion-", suffix="-running", directory=tempDirectory)

        self.shell.create_directory_recursively(f"{outputFolder}/screenshots")  # to store screenshots
        self.shell.create_directory_recursively(getNmapRunningFolder(runningFolder))  # to store nmap output
        self.shell.create_directory_recursively(f"{runningFolder}/hydra")  # to store hydra output
        self.shell.create_directory_recursively(f"{runningFolder}/dnsmap")  # to store dnsmap output

        (usernameWordList, passwordWordList) = self.__createUsernameAndPasswordWordLists(outputFolder)
        repositoryContainer = self.repositoryFactory.buildRepositories(database)

        projectName = database.name
        projectProperties = ProjectProperties(
            projectName, workingDirectory, projectType, isTemp, outputFolder, runningFolder, usernameWordList,
            passwordWordList, storeWordListsOnExit=True
        )
        return Project(projectProperties, repositoryContainer, database)

    def openExistingProject(self, projectName: str, projectType: str = "legion") -> Project:
        self.logger.info(f"Opening existing project: {projectName}...")
        database = self.__createDatabase(projectName)
        workingDirectory = f"{ntpath.dirname(projectName)}/"
        outputFolder, _ = self.__determineOutputFolder(projectName, projectType)
        runningFolder = self.shell.create_temporary_directory(suffix="-running", prefix=projectType + '-',
                                                              directory=tempDirectory)
        (usernameWordList, passwordWordList) = self.__createUsernameAndPasswordWordLists(outputFolder)
        projectProperties = ProjectProperties(
            projectName=projectName, workingDirectory=workingDirectory, projectType=projectType, isTemporary=False,
            outputFolder=outputFolder, runningFolder=runningFolder, usernamesWordList=usernameWordList,
            passwordWordList=passwordWordList, storeWordListsOnExit=True
        )
        repositoryContainer = self.repositoryFactory.buildRepositories(database)
        return Project(projectProperties, repositoryContainer, database)

    def closeProject(self, project: Project) -> None:
        self.logger.info(f"Closing project {project.properties.projectName}...")
        # if current project is not temporary & delete wordlists if necessary
        projectProperties = project.properties
        try:
            if not projectProperties.isTemporary:
                if not projectProperties.storeWordListsOnExit:
                    self.logger.info('Removing wordlist files.')
                    self.shell.remove_file(projectProperties.usernamesWordList.filename)
                    self.shell.remove_file(projectProperties.passwordWordList.filename)
            else:
                self.logger.info('Removing temporary files and folders...')
                self.shell.remove_file(projectProperties.projectName)
                self.shell.remove_directory(projectProperties.outputFolder)

            self.logger.info('Removing running folder at close...')
            self.shell.remove_directory(projectProperties.runningFolder)
        except:
            self.logger.info('Something went wrong removing temporary files and folders..')
            self.logger.info("Unexpected error: {0}".format(sys.exc_info()[0]))

    # this function copies the current project files and folder to a new location
    # if the replace flag is set to 1, it overwrites the destination file and folder
    def saveProjectAs(self, project: Project, fileName: str, replace=0, projectType="legion") -> Project:
        self.logger.info(f"Saving project {project.properties.projectName}...")
        toolOutputFolder, normalizedFileName = self.__determineOutputFolder(fileName, projectType)

        # check if filename already exists (skip the check if we want to replace the file)
        if replace == 0 and fileExists(self.shell, normalizedFileName):
            return

        self.shell.copy(source=project.properties.projectName, destination=normalizedFileName)
        os.system('cp -r "' + project.properties.outputFolder + '/." "' + toolOutputFolder + '"')

        if project.properties.isTemporary:
            self.shell.remove_file(project.properties.projectName)
            self.shell.remove_directory(project.properties.outputFolder)

        self.logger.info(f"Project saved as {normalizedFileName}.")
        return self.openExistingProject(normalizedFileName, projectType)

    def __createDatabase(self, projectName: str = None) -> Database:
        if projectName:
            return Database(projectName)

        databaseFile = self.shell.create_named_temporary_file(suffix=".legion", prefix="legion-", directory=tempDirectory,
                                                              delete_on_close=False)  # to store the db file
        return Database(databaseFile.name)

    @staticmethod
    def setStoreWordListsOnExit(project: Project, storeWordListsOnExit: bool) -> None:
        projectProperties = ProjectProperties(
            projectName=project.properties.projectName, workingDirectory=project.properties.workingDirectory,
            projectType=project.properties.projectType, isTemporary=project.properties.isTemporary,
            outputFolder=project.properties.outputFolder, runningFolder=project.properties.runningFolder,
            usernamesWordList=project.properties.usernamesWordList,
            passwordWordList=project.properties.passwordWordList, storeWordListsOnExit=storeWordListsOnExit
        )
        project.properties = projectProperties

    @staticmethod
    def __determineOutputFolder(projectName: str, projectType: str) -> Tuple[str, str]:
        nameOffset = len(projectType) + 1
        if not projectName.endswith(projectType):
            # use the same name as the file for the folder (without the extension)
            return f"{projectName}-tool-output", f"{projectName}.{projectType}"
        else:
            return f"{projectName[:-nameOffset]}-tool-output", projectName

    @staticmethod
    def __createUsernameAndPasswordWordLists(outputFolder: str) -> Tuple[Wordlist, Wordlist]:
        usernamesWordlist = Wordlist(f"{outputFolder}/legion-usernames.txt")  # to store found usernames
        passwordWordlist = Wordlist(f"{outputFolder}/legion-passwords.txt")  # to store found passwords
        return usernamesWordlist, passwordWordlist
