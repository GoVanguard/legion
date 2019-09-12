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


def build_mock_process(status: str, display: str) -> MagicMock:
    process = MagicMock()
    process.status = status
    process.display = display
    return process


class LogicTest(unittest.TestCase):
    @patch('utilities.stenoLogging.get_logger')
    def setUp(self, get_logger) -> None:
        self.shell = MagicMock()
        self.mock_db_session = MagicMock()

    def test_init_ShouldLoadInitialVariablesSuccessfully(self):
        from app.logic import Logic

        self.shell.get_current_working_directory.return_value = "./some/path/"
        self.shell.create_temporary_directory.side_effect = ["./output/folder", "./running/folder"]
        logic = Logic("test-session", self.mock_db_session, self.shell)

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
        logic = Logic("test-session", self.mock_db_session, self.shell)
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
        logic = Logic("test-session", self.mock_db_session, self.shell)
        logic.istemp = True
        logic.projectname = "project-name"
        logic.runningfolder = "./running/folder"
        logic.outputfolder = "./output/folder"
        logic.removeTemporaryFiles()

        self.shell.remove_file.assert_called_once_with("project-name")
        self.shell.remove_directory.assert_has_calls([mock.call("./output/folder"), mock.call("./running/folder")])

    def test_toggleProcessDisplayStatus_whenResetAllIsTrue_setDisplayToFalseForAllProcessesThatAreNotRunning(
            self):
        from app.logic import Logic
        logic = Logic("test-session", self.mock_db_session, self.shell)

        process1 = build_mock_process(status="Waiting", display="True")
        process2 = build_mock_process(status="Waiting", display="True")
        logic.db = MagicMock()
        logic.db.session.return_value = self.mock_db_session
        mock_query_response = MagicMock()
        mock_filtered_response = MagicMock()
        mock_filtered_response.all.return_value = [process1, process2]
        mock_query_response.filter_by.return_value = mock_filtered_response
        self.mock_db_session.query.return_value = mock_query_response
        logic.toggleProcessDisplayStatus(resetAll=True)

        self.assertEqual("False", process1.display)
        self.assertEqual("False", process2.display)
        self.mock_db_session.add.assert_has_calls([
            mock.call(process1),
            mock.call(process2),
        ])
        logic.db.commit.assert_called_once()

    def test_toggleProcessDisplayStatus_whenResetAllIFalse_setDisplayToFalseForAllProcessesThatAreNotRunningOrWaiting(
            self):
        from app.logic import Logic
        logic = Logic("test-session", self.mock_db_session, self.shell)

        process1 = build_mock_process(status="Random Status", display="True")
        process2 = build_mock_process(status="Another Random Status", display="True")
        process3 = build_mock_process(status="Running", display="True")
        logic.db = MagicMock()
        logic.db.session.return_value = self.mock_db_session
        mock_query_response = MagicMock()
        mock_filtered_response = MagicMock()
        mock_filtered_response.all.return_value = [process1, process2]
        mock_query_response.filter_by.return_value = mock_filtered_response
        self.mock_db_session.query.return_value = mock_query_response
        logic.toggleProcessDisplayStatus()

        self.assertEqual("False", process1.display)
        self.assertEqual("False", process2.display)
        self.assertEqual("True", process3.display)
        self.mock_db_session.add.assert_has_calls([
            mock.call(process1),
            mock.call(process2),
        ])
        logic.db.commit.assert_called_once()
