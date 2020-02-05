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
from unittest import mock
from unittest.mock import MagicMock, patch

from app.Project import Project


class ProjectManagerTest(unittest.TestCase):
    @patch('utilities.stenoLogging.get_logger')
    @patch('db.repositories.HostRepository')
    @patch('app.auxiliary.Wordlist')
    @patch('db.database.Database')
    def setUp(self, getLogger, hostRepository, wordlist, database) -> None:
        from app.ProjectManager import ProjectManager
        self.mockShell = MagicMock()
        self.mockRepositoryFactory = MagicMock()
        self.project = MagicMock()
        self.mockDatabase = database
        self.projectManager = ProjectManager(self.mockShell, self.mockRepositoryFactory, getLogger)

    def test_createNewProject_WhenProvidedProjectDetails_ReturnsANewProject(self):
        projectType = "legion"
        isTemporary = True
        self.mockDatabase.name = "newTemporaryProject"
        self.mockShell.get_current_working_directory.return_value = "workingDir/"
        self.mockShell.create_temporary_directory.side_effect = ["/outputFolder", "/runningFolder"]

        project = self.projectManager.createNewProject(projectType, isTemporary)
        self.mockShell.create_named_temporary_file.assert_called_once_with(
            suffix=".legion", prefix="legion-", directory="./tmp/", delete_on_close=False
        )
        self.mockShell.create_temporary_directory.assert_has_calls([
            mock.call(prefix="legion-", suffix="-tool-output", directory="./tmp/"),
            mock.call(prefix="legion-", suffix="-running", directory="./tmp/"),
        ])
        self.mockShell.create_directory_recursively.assert_has_calls([
            mock.call("/outputFolder/screenshots"),
            mock.call("/runningFolder/nmap"),
            mock.call("/runningFolder/hydra"),
            mock.call("/runningFolder/dnsmap"),
        ])
        self.assertIsNotNone(project.properties.projectName)
        self.assertEqual(project.properties.projectType, "legion")
        self.assertEqual(project.properties.workingDirectory, "workingDir/")
        self.assertEqual(project.properties.isTemporary, True)
        self.assertEqual(project.properties.outputFolder, "/outputFolder")
        self.assertEqual(project.properties.runningFolder, "/runningFolder")
        self.assertEqual(project.properties.storeWordListsOnExit, True)
        self.mockRepositoryFactory.buildRepositories.assert_called_once_with(mock.ANY)

    def test_closeProject_WhenProvidedAnOpenTemporaryProject_ClosesTheProject(self):
        self.project.properties.isTemporary = True
        self.project.properties.storeWordListsOnExit = True
        self.project.properties.projectName = "project-name"
        self.project.properties.runningFolder = "./running/folder"
        self.project.properties.outputFolder = "./output/folder"

        self.projectManager.closeProject(self.project)
        self.mockShell.remove_file.assert_called_once_with("project-name")
        self.mockShell.remove_directory.assert_has_calls([mock.call("./output/folder"), mock.call("./running/folder")])

    def test_closeProject_WhenProvidedAnOpenNonTemporaryProject_ClosesTheProject(self):
        self.project.properties.isTemporary = False
        self.project.properties.storeWordListsOnExit = False
        self.project.properties.runningFolder = "./running/folder"
        self.project.properties.usernamesWordList = MagicMock()
        self.project.properties.usernamesWordList.filename = "UsernamesList.txt"
        self.project.properties.passwordWordList = MagicMock()
        self.project.properties.passwordWordList.filename = "PasswordsList.txt"

        self.projectManager.closeProject(self.project)
        self.mockShell.remove_file.assert_has_calls([mock.call("UsernamesList.txt"), mock.call("PasswordsList.txt")])
        self.mockShell.remove_directory.assert_called_once_with("./running/folder")

    def test_openExistingProject_WhenProvidedProjectNameAndType_OpensAnExistingProjectSuccessfully(self):
        from app.Project import Project

        projectName = "some-existing-project"
        self.mockShell.create_temporary_directory.return_value = "/running/folder"
        openedExistingProject: Project = self.projectManager.openExistingProject(projectName, "legion")
        self.assertFalse(openedExistingProject.properties.isTemporary)
        self.assertEqual(openedExistingProject.properties.projectName, "some-existing-project")
        self.assertEqual(openedExistingProject.properties.workingDirectory, "/")
        self.assertEqual(openedExistingProject.properties.projectType, "legion")
        self.assertFalse(openedExistingProject.properties.isTemporary)
        self.assertEqual(openedExistingProject.properties.outputFolder, "some-existing-project-tool-output")
        self.assertEqual(openedExistingProject.properties.runningFolder, "/running/folder")
        self.assertIsNotNone(openedExistingProject.properties.usernamesWordList)
        self.assertIsNotNone(openedExistingProject.properties.passwordWordList)
        self.assertTrue(openedExistingProject.properties.storeWordListsOnExit)
        self.mockShell.create_temporary_directory.assert_called_once_with(suffix="-running", prefix="legion-",
                                                                          directory="./tmp/")
        self.mockRepositoryFactory.buildRepositories.assert_called_once()

    @patch('os.system')
    def test_saveProjectAs_WhenProvidedAnActiveTemporaryProjectAndASaveFileName_SavesProjectSuccessfully(self,
                                                                                                         osSystem):
        expectedFileName = "my-test-project"
        self.project.properties.projectName = "some-running-temporary-project"
        self.project.properties.outputFolder = "some-temporary-output-folder"
        self.project.properties.isTemporary = True
        self.mockShell.directoryOrFileExists.return_value = False

        savedProject: Project = self.projectManager.saveProjectAs(self.project, expectedFileName, replace=1,
                                                                  projectType="legion")
        self.mockShell.copy.assert_called_once_with(source="some-running-temporary-project",
                                                    destination="my-test-project.legion")
        osSystem.assert_called_once()
        self.mockShell.remove_file.assert_called_once_with("some-running-temporary-project")
        self.mockShell.remove_directory.assert_called_once_with("some-temporary-output-folder")
        self.assertEqual(savedProject.properties.projectName, "my-test-project.legion")
        self.assertEqual(savedProject.properties.projectType, "legion")

    @patch('os.system')
    def test_saveProjectAs_WhenReplaceFlagIsFalse_DoesNotSaveProject(self, osSystem):
        self.projectManager.saveProjectAs(self.project, "some-project-that-cannot-be-replaced", replace=0,
                                          projectType="legion")
        self.mockShell.copy.assert_not_called()
        osSystem.assert_not_called()
