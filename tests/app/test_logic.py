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


class LogicTest(unittest.TestCase):
    @patch('utilities.stenoLogging.get_logger')
    @patch('db.repositories.HostRepository')
    def setUp(self, get_logger, hostRepository) -> None:
        self.shell = MagicMock()
        self.hostRepository = hostRepository
        self.mock_db_session = MagicMock()

    def test_init_ShouldLoadInitialVariablesSuccessfully(self):
        from app.logic import Logic

        self.shell.get_current_working_directory.return_value = "./some/path/"
        self.shell.create_temporary_directory.side_effect = ["./output/folder", "./running/folder"]
        logic = Logic("test-session", self.mock_db_session, self.shell, self.hostRepository)

        self.assertEqual("./some/path/", logic.cwd)
        self.assertTrue(logic.istemp)
        self.shell.create_directory_recursively.assert_has_calls([
            mock.call("./output/folder/screenshots"),
            mock.call("./running/folder/nmap"),
            mock.call("./running/folder/hydra"),
            mock.call("./running/folder/dnsmap"),
        ])

    def test_removeTemporaryFiles_whenProjectIsNotTemporaryAndNotStoringWordlists_shouldRemoveWordListsAndRunningFolder(
            self):
        from app.logic import Logic
        logic = Logic("test-session", self.mock_db_session, self.shell, self.hostRepository)
        logic.setStoreWordlistsOnExit(False)
        logic.istemp = False
        logic.runningfolder = "./running/folder"
        logic.usernamesWordlist = MagicMock()
        logic.usernamesWordlist.filename = "UsernamesList.txt"
        logic.passwordsWordlist = MagicMock()
        logic.passwordsWordlist.filename = "PasswordsList.txt"
        logic.removeTemporaryFiles()

        self.shell.remove_file.assert_has_calls([mock.call("UsernamesList.txt"), mock.call("PasswordsList.txt")])
        self.shell.remove_directory.assert_called_once_with("./running/folder")

    def test_removeTemporaryFiles_whenProjectIsTemporary_shouldRemoveProjectAndOutputFolderAndRunningFolder(
            self):
        from app.logic import Logic
        logic = Logic("test-session", self.mock_db_session, self.shell, self.hostRepository)
        logic.istemp = True
        logic.projectname = "project-name"
        logic.runningfolder = "./running/folder"
        logic.outputfolder = "./output/folder"
        logic.removeTemporaryFiles()

        self.shell.remove_file.assert_called_once_with("project-name")
        self.shell.remove_directory.assert_has_calls([mock.call("./output/folder"), mock.call("./running/folder")])
