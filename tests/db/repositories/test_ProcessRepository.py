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

from tests.db.helpers.db_helpers import mock_execute_fetchall, mock_first_by_side_effect, mock_first_by_return_value, \
    mock_query_with_filter_by


class ProcessRepositoryTest(unittest.TestCase):
    @patch('utilities.stenoLogging.get_logger')
    def setUp(self, get_logger) -> None:
        self.mock_db_adapter = MagicMock()
        self.mock_logger = MagicMock()

    def test_store_process_output_WhenProvidedExistingProcessIdAndOutput_StoresProcessOutput(self):
        from db.repositories.ProcessRepository import ProcessRepository
        from db.database import process, process_output

        expected_process: process = MagicMock()
        process.status = 'Running'
        expected_process_output: process_output = MagicMock()
        mock_db_session = MagicMock()
        self.mock_db_adapter.session.return_value = mock_db_session
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_first_by_side_effect([expected_process, expected_process_output])
        mock_db_session.query.return_value = mock_query

        process_repository = ProcessRepository(self.mock_db_adapter, self.mock_logger)
        process_repository.store_process_output("some_process_id", "this is some cool output")

        mock_db_session.add.assert_has_calls([
            mock.call(expected_process_output),
            mock.call(expected_process)
        ])
        self.mock_db_adapter.commit.assert_called_once()

    def test_store_process_output_WhenProvidedProcessIdDoesNotExist_DoesNotPerformAnyUpdate(self):
        from db.repositories.ProcessRepository import ProcessRepository

        mock_db_session = MagicMock()
        self.mock_db_adapter.session.return_value = mock_db_session
        mock_db_session.query.return_value = mock_query_with_filter_by(mock_first_by_return_value(False))

        process_repository = ProcessRepository(self.mock_db_adapter, self.mock_logger)
        process_repository.store_process_output("some_non_existant_process_id", "this is some cool output")

        mock_db_session.add.assert_not_called()
        self.mock_db_adapter.commit.assert_not_called()

    def test_store_process_output_WhenProvidedExistingProcessIdAndOutputButProcKilled_StoresOutputButStatusNotUpdated(
            self):
        self.when_process_does_not_finish_gracefully("Killed")

    def test_store_process_output_WhenProvidedExistingProcessIdAndOutputButProcCancelled_StoresOutputButStatusNotUpdated(
            self):
        self.when_process_does_not_finish_gracefully("Cancelled")

    def test_store_process_output_WhenProvidedExistingProcessIdAndOutputButProcCrashed_StoresOutputButStatusNotUpdated(
            self):
        self.when_process_does_not_finish_gracefully("Crashed")

    def test_get_status_by_process_id_WhenGivenProcId_FetchesProcessStatus(self):
        from db.repositories.ProcessRepository import ProcessRepository

        expected_query = 'SELECT process.status FROM process AS process WHERE process.id=?'
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([['Running']])

        process_repository = ProcessRepository(self.mock_db_adapter, self.mock_logger)
        actual_status = process_repository.get_status_by_process_id("some_process_id")

        self.assertEqual(actual_status, 'Running')
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_process_id")

    def test_get_status_by_process_id_WhenProcIdDoesNotExist_ReturnsNegativeOne(self):
        from db.repositories.ProcessRepository import ProcessRepository

        expected_query = 'SELECT process.status FROM process AS process WHERE process.id=?'
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall(False)

        process_repository = ProcessRepository(self.mock_db_adapter, self.mock_logger)
        actual_status = process_repository.get_status_by_process_id("some_process_id")

        self.assertEqual(actual_status, -1)
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_process_id")

    def test_get_pid_by_process_id_WhenGivenProcId_FetchesProcessId(self):
        from db.repositories.ProcessRepository import ProcessRepository

        expected_query = 'SELECT process.pid FROM process AS process WHERE process.id=?'
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([['1234']])

        process_repository = ProcessRepository(self.mock_db_adapter, self.mock_logger)
        actual_status = process_repository.get_pid_by_process_id("some_process_id")

        self.assertEqual(actual_status, '1234')
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_process_id")

    def test_get_pid_by_process_id_WhenProcIdDoesNotExist_ReturnsNegativeOne(self):
        from db.repositories.ProcessRepository import ProcessRepository

        expected_query = 'SELECT process.pid FROM process AS process WHERE process.id=?'
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall(False)

        process_repository = ProcessRepository(self.mock_db_adapter, self.mock_logger)
        actual_status = process_repository.get_pid_by_process_id("some_process_id")

        self.assertEqual(actual_status, -1)
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_process_id")

    def test_is_killed_process_WhenProvidedKilledProcessId_ReturnsTrue(self):
        from db.repositories.ProcessRepository import ProcessRepository

        expected_query = "SELECT process.status FROM process AS process WHERE process.id=?"
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([["Killed"]])

        process_repository = ProcessRepository(self.mock_db_adapter, self.mock_logger)

        self.assertTrue(process_repository.is_killed_process("some_process_id"))
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_process_id")

    def test_is_killed_process_WhenProvidedNonKilledProcessId_ReturnsFalse(self):
        from db.repositories.ProcessRepository import ProcessRepository

        expected_query = "SELECT process.status FROM process AS process WHERE process.id=?"
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([["Running"]])

        process_repository = ProcessRepository(self.mock_db_adapter, self.mock_logger)

        self.assertFalse(process_repository.is_killed_process("some_process_id"))
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_process_id")

    def test_is_cancelled_process_WhenProvidedCancelledProcessId_ReturnsTrue(self):
        from db.repositories.ProcessRepository import ProcessRepository

        expected_query = "SELECT process.status FROM process AS process WHERE process.id=?"
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([["Cancelled"]])

        process_repository = ProcessRepository(self.mock_db_adapter, self.mock_logger)

        self.assertTrue(process_repository.is_cancelled_process("some_process_id"))
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_process_id")

    def test_is_cancelled_process_WhenProvidedNonCancelledProcessId_ReturnsFalse(self):
        from db.repositories.ProcessRepository import ProcessRepository

        expected_query = "SELECT process.status FROM process AS process WHERE process.id=?"
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([["Running"]])

        process_repository = ProcessRepository(self.mock_db_adapter, self.mock_logger)

        self.assertFalse(process_repository.is_cancelled_process("some_process_id"))
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_process_id")

    def when_process_does_not_finish_gracefully(self, process_status: str):
        from db.repositories.ProcessRepository import ProcessRepository
        from db.database import process, process_output

        expected_process: process = MagicMock()
        expected_process.status = process_status
        expected_process_output: process_output = MagicMock()
        mock_db_session = MagicMock()
        self.mock_db_adapter.session.return_value = mock_db_session
        mock_db_session.query.return_value = mock_query_with_filter_by(
            mock_first_by_side_effect([expected_process, expected_process_output]))

        process_repository = ProcessRepository(self.mock_db_adapter, self.mock_logger)
        process_repository.store_process_output("some_process_id", "this is some cool output")

        mock_db_session.add.assert_called_once_with(expected_process_output)
        self.mock_db_adapter.commit.assert_called_once()
