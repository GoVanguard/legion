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

from tests.db.helpers.db_helpers import mockExecuteFetchAll, mockFirstBySideEffect, mockFirstByReturnValue, \
    mockQueryWithFilterBy


def build_mock_process(status: str, display: str) -> MagicMock:
    process = MagicMock()
    process.status = status
    process.display = display
    return process


class ProcessRepositoryTest(unittest.TestCase):
    @patch('utilities.stenoLogging.get_logger')
    def setUp(self, get_logger) -> None:
        from db.repositories.ProcessRepository import ProcessRepository
        self.mockProcess = MagicMock()
        self.mockDbSession = MagicMock()
        self.mockDbAdapter = MagicMock()
        self.mockLogger = MagicMock()
        self.mockFilters = MagicMock()
        self.mockDbAdapter.session.return_value = self.mockDbSession
        self.processRepository = ProcessRepository(self.mockDbAdapter, self.mockLogger)

    def test_getProcesses_WhenProvidedShowProcessesWithNoNmapFlag_ReturnsProcesses(self):
        expectedQuery = ('SELECT "0", "0", "0", process.name, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0" '
                         'FROM process AS process WHERE process.closed = "False" AND process.name != "nmap" '
                         'GROUP BY process.name')
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll(
            [['some-process'], ['some-process2']])
        processes = self.processRepository.getProcesses(self.mockFilters, showProcesses='noNmap')
        self.assertEqual(processes, [['some-process'], ['some-process2']])
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery)

    def test_getProcesses_WhenProvidedShowProcessesWithFlagFalse_ReturnsProcesses(self):
        expectedQuery = ('SELECT process.id, process.hostIp, process.tabTitle, process.outputfile, output.output '
                         'FROM process AS process INNER JOIN process_output AS output ON process.id = output.processId '
                         'WHERE process.display = ? AND process.closed = "False" order by process.id desc')
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll(
            [['some-process'], ['some-process2']])
        processes = self.processRepository.getProcesses(self.mockFilters, showProcesses='False')
        self.assertEqual(processes, [['some-process'], ['some-process2']])
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, 'False')

    def test_getProcesses_WhenProvidedShowProcessesWithNoFlag_ReturnsProcesses(self):
        expectedQuery = "SELECT * FROM process AS process WHERE process.display=? order by id asc"
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll(
            [['some-process'], ['some-process2']])
        processes = self.processRepository.getProcesses(self.mockFilters, "True", sort='asc', ncol='id')
        self.assertEqual(processes, [['some-process'], ['some-process2']])
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, 'True')

    def test_storeProcess_WhenProvidedAProcess_StoreProcess(self):
        processId = self.processRepository.storeProcess(self.mockProcess)

        self.mockDbSession.add.assert_called_once()
        self.mockDbAdapter.commit.assert_called_once()

    def test_storeProcessOutput_WhenProvidedExistingProcessIdAndOutput_StoresProcessOutput(self):
        from db.entities.process import process
        from db.entities.processOutput import process_output

        expected_process: process = MagicMock()
        process.status = 'Running'
        expected_process_output: process_output = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mockFirstBySideEffect([expected_process, expected_process_output])
        self.mockDbSession.query.return_value = mock_query

        self.processRepository.storeProcessOutput("some_process_id", "this is some cool output")

        self.mockDbSession.add.assert_has_calls([
            mock.call(expected_process_output),
            mock.call(expected_process)
        ])
        self.mockDbAdapter.commit.assert_called_once()

    def test_storeProcessOutput_WhenProvidedProcessIdDoesNotExist_DoesNotPerformAnyUpdate(self):
        self.mockDbAdapter.session.return_value = self.mockDbSession
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(mockFirstByReturnValue(False))

        self.processRepository.storeProcessOutput("some_non_existent_process_id", "this is some cool output")

        self.mockDbSession.add.assert_not_called()
        self.mockDbAdapter.commit.assert_not_called()

    def test_storeProcessOutput_WhenProvidedExistingProcessIdAndOutputButProcKilled_StoresOutputButStatusNotUpdated(
            self):
        self.whenProcessDoesNotFinishGracefully("Killed")

    def test_storeProcessOutput_WhenProvidedExistingProcessIdAndOutputButProcCancelled_StoresOutputButStatusNotUpdated(
            self):
        self.whenProcessDoesNotFinishGracefully("Cancelled")

    def test_storeProcessOutput_WhenProvidedExistingProcessIdAndOutputButProcCrashed_StoresOutputButStatusNotUpdated(
            self):
        self.whenProcessDoesNotFinishGracefully("Crashed")

    def test_getStatusByProcessId_WhenGivenProcId_FetchesProcessStatus(self):
        expectedQuery = 'SELECT process.status FROM process AS process WHERE process.id=?'
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([['Running']])

        actual_status = self.processRepository.getStatusByProcessId("some_process_id")

        self.assertEqual(actual_status, 'Running')
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some_process_id")

    def test_getStatusByProcessId_WhenProcIdDoesNotExist_ReturnsNegativeOne(self):
        expectedQuery = 'SELECT process.status FROM process AS process WHERE process.id=?'
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll(False)

        actual_status = self.processRepository.getStatusByProcessId("some_process_id")

        self.assertEqual(actual_status, -1)
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some_process_id")

    def test_getPIDByProcessId_WhenGivenProcId_FetchesProcessId(self):
        expectedQuery = 'SELECT process.pid FROM process AS process WHERE process.id=?'
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([['1234']])

        actual_status = self.processRepository.getPIDByProcessId("some_process_id")

        self.assertEqual(actual_status, '1234')
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some_process_id")

    def test_getPIDByProcessId_WhenProcIdDoesNotExist_ReturnsNegativeOne(self):
        expectedQuery = 'SELECT process.pid FROM process AS process WHERE process.id=?'
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll(False)

        actual_status = self.processRepository.getPIDByProcessId("some_process_id")

        self.assertEqual(actual_status, -1)
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some_process_id")

    def test_isKilledProcess_WhenProvidedKilledProcessId_ReturnsTrue(self):
        expectedQuery = "SELECT process.status FROM process AS process WHERE process.id=?"
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([["Killed"]])

        self.assertTrue(self.processRepository.isKilledProcess("some_process_id"))
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some_process_id")

    def test_isKilledProcess_WhenProvidedNonKilledProcessId_ReturnsFalse(self):
        expectedQuery = "SELECT process.status FROM process AS process WHERE process.id=?"
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([["Running"]])

        self.assertFalse(self.processRepository.isKilledProcess("some_process_id"))
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some_process_id")

    def test_isCancelledProcess_WhenProvidedCancelledProcessId_ReturnsTrue(self):
        expectedQuery = "SELECT process.status FROM process AS process WHERE process.id=?"
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([["Cancelled"]])

        self.assertTrue(self.processRepository.isCancelledProcess("some_process_id"))
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some_process_id")

    def test_isCancelledProcess_WhenProvidedNonCancelledProcessId_ReturnsFalse(self):
        expectedQuery = "SELECT process.status FROM process AS process WHERE process.id=?"
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([["Running"]])

        self.assertFalse(self.processRepository.isCancelledProcess("some_process_id"))
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some_process_id")

    def test_storeProcessCrashStatus_WhenProvidedProcessId_StoresProcessCrashStatus(self):
        self.mockProcessStatusAndReturnSingle("Running")
        self.processRepository.storeProcessCrashStatus("some-process-id")
        self.assertProcessStatusUpdatedTo("Crashed")

    def test_storeProcessCancelledStatus_WhenProvidedProcessId_StoresProcessCancelledStatus(self):
        self.mockProcessStatusAndReturnSingle("Running")
        self.processRepository.storeProcessCancelStatus("some-process-id")
        self.assertProcessStatusUpdatedTo("Cancelled")

    def test_storeProcessRunningStatus_WhenProvidedProcessId_StoresProcessRunningStatus(self):
        self.mockProcessStatusAndReturnSingle("Waiting")
        self.processRepository.storeProcessRunningStatus("some-process-id", "3123")
        self.assertProcessStatusUpdatedTo("Running")

    def test_storeProcessKillStatus_WhenProvidedProcessId_StoresProcessKillStatus(self):
        self.mockProcessStatusAndReturnSingle("Running")
        self.processRepository.storeProcessKillStatus("some-process-id")
        self.assertProcessStatusUpdatedTo("Killed")

    def test_storeProcessRunningElapsedTime_WhenProvidedProcessId_StoresProcessRunningElapsedTime(self):
        self.mockProcess.elapsed = "some-time"
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(mockFirstByReturnValue(self.mockProcess))

        self.processRepository.storeProcessRunningElapsedTime("some-process-id", "another-time")
        self.assertEqual("another-time", self.mockProcess.elapsed)
        self.mockDbSession.add.assert_called_once_with(self.mockProcess)
        self.mockDbAdapter.commit.assert_called_once()

    def test_getHostsByToolName_WhenProvidedToolNameAndClosedFalse_StoresProcessRunningElapsedTime(self):
        expectedQuery = ('SELECT process.id, "0", "0", "0", "0", "0", "0", process.hostIp, process.port, '
                         'process.protocol, "0", "0", process.outputfile, "0", "0", "0" FROM process AS process '
                         'WHERE process.name=? and process.closed="False"')
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([["some-host1"], ["some-host2"]])

        hosts = self.processRepository.getHostsByToolName("some-toolname", "False")
        self.assertEqual([["some-host1"], ["some-host2"]], hosts)
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some-toolname")

    def test_getHostsByToolName_WhenProvidedToolNameAndClosedAsFetchAll_StoresProcessRunningElapsedTime(self):
        expectedQuery = ('SELECT "0", "0", "0", "0", "0", process.hostIp, process.port, process.protocol, "0", "0", '
                         'process.outputfile, "0", "0", "0" FROM process AS process WHERE process.name=?')
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([["some-host1"], ["some-host2"]])

        hosts = self.processRepository.getHostsByToolName("some-toolname", "FetchAll")
        self.assertEqual([["some-host1"], ["some-host2"]], hosts)
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some-toolname")

    def test_storeCloseStatus_WhenProvidedProcessId_StoresCloseStatus(self):
        self.mockProcess.closed = 'False'
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(mockFirstByReturnValue(self.mockProcess))
        self.processRepository.storeCloseStatus("some-process-id")

        self.assertEqual('True', self.mockProcess.closed)
        self.mockDbSession.add.assert_called_once_with(self.mockProcess)
        self.mockDbAdapter.commit.assert_called_once()

    def test_storeScreenshot_WhenProvidedIPAndPortAndFileName_StoresScreenshot(self):
        processId = self.processRepository.storeScreenshot("some-ip", "some-port", "some-filename")

        self.mockDbSession.add.assert_called_once()
        self.mockDbSession.commit.assert_called_once()

    def test_toggleProcessDisplayStatus_whenResetAllIsTrue_setDisplayToFalseForAllProcessesThatAreNotRunning(
            self):
        process1 = build_mock_process(status="Waiting", display="True")
        process2 = build_mock_process(status="Waiting", display="True")
        mock_query_response = MagicMock()
        mock_filtered_response = MagicMock()
        mock_filtered_response.all.return_value = [process1, process2]
        mock_query_response.filter_by.return_value = mock_filtered_response
        self.mockDbSession.query.return_value = mock_query_response
        self.processRepository.toggleProcessDisplayStatus(resetAll=True)

        self.assertEqual("False", process1.display)
        self.assertEqual("False", process2.display)
        self.mockDbSession.add.assert_has_calls([
            mock.call(process1),
            mock.call(process2),
        ])
        self.mockDbAdapter.commit.assert_called_once()

    def test_toggleProcessDisplayStatus_whenResetAllIFalse_setDisplayToFalseForAllProcessesThatAreNotRunningOrWaiting(
            self):
        process1 = build_mock_process(status="Random Status", display="True")
        process2 = build_mock_process(status="Another Random Status", display="True")
        process3 = build_mock_process(status="Running", display="True")
        mock_query_response = MagicMock()
        mock_filtered_response = MagicMock()
        mock_filtered_response.all.return_value = [process1, process2]
        mock_query_response.filter_by.return_value = mock_filtered_response
        self.mockDbSession.query.return_value = mock_query_response
        self.processRepository.toggleProcessDisplayStatus()

        self.assertEqual("False", process1.display)
        self.assertEqual("False", process2.display)
        self.assertEqual("True", process3.display)
        self.mockDbSession.add.assert_has_calls([
            mock.call(process1),
            mock.call(process2),
        ])
        self.mockDbAdapter.commit.assert_called_once()

    def mockProcessStatusAndReturnSingle(self, processStatus: str):
        self.mockProcess.status = processStatus
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(mockFirstByReturnValue(self.mockProcess))

    def assertProcessStatusUpdatedTo(self, expected_status: str):
        self.assertEqual(expected_status, self.mockProcess.status)
        self.mockDbSession.add.assert_called_once_with(self.mockProcess)
        self.mockDbAdapter.commit.assert_called_once()

    def whenProcessDoesNotFinishGracefully(self, process_status: str):
        from db.entities.process import process
        from db.entities.processOutput import process_output

        expected_process: process = MagicMock()
        expected_process.status = process_status
        expected_process_output: process_output = MagicMock()
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(
            mockFirstBySideEffect([expected_process, expected_process_output]))

        self.processRepository.storeProcessOutput("some_process_id", "this is some cool output")

        self.mockDbSession.add.assert_called_once_with(expected_process_output)
        self.mockDbAdapter.commit.assert_called_once()
