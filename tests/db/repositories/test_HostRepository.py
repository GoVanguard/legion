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
from unittest.mock import MagicMock, patch

from tests.db.helpers.db_helpers import mockExecuteFetchAll, mockQueryWithFilterBy, mockFirstByReturnValue

existsQuery = 'SELECT host.ip FROM hostObj AS host WHERE host.ip == ? OR host.hostname == ?'


def expectedGetHostsAndPortsQuery(with_filter: str = "") -> str:
    query = (
        "SELECT hosts.ip,ports.portId,ports.protocol,ports.state,ports.hostId,ports.serviceId,services.name,"
        "services.product,services.version,services.extrainfo,services.fingerprint FROM portObj AS ports "
        "INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
        "LEFT OUTER JOIN serviceObj AS services ON services.id=ports.serviceId "
        "WHERE services.name=?")
    query += with_filter
    return query


class HostRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        from db.repositories.HostRepository import HostRepository
        self.mockDbAdapter = MagicMock()
        self.mockDbSession = MagicMock()
        self.mockProcess = MagicMock()
        self.mockDbAdapter.session.return_value = self.mockDbSession
        self.hostRepository = HostRepository(self.mockDbAdapter)

    def getHostsAndPortsTestCase(self, filters, service_name, expectedQuery):
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll(
            [{'name': 'service_name1'}, {'name': 'service_name2'}])
        service_names = self.hostRepository.getHostsAndPortsByServiceName(service_name, filters)

        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, service_name)
        self.assertEqual([{'name': 'service_name1'}, {'name': 'service_name2'}], service_names)

    def test_exists_WhenProvidedAExistingHosts_ReturnsTrue(self):
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([['some-ip']])
        self.assertTrue(self.hostRepository.exists("some_host"))
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(existsQuery, "some_host", "some_host")

    def test_exists_WhenProvidedANonExistingHosts_ReturnsFalse(self):
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([])

        self.assertFalse(self.hostRepository.exists("some_host"))
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(existsQuery, "some_host", "some_host")

    def test_getHosts_InvokedWithNoFilters_ReturnsHosts(self):
        from app.auxiliary import Filters
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([['host1'], ['host2']])
        expectedQuery = "SELECT * FROM hostObj AS hosts WHERE 1=1"
        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        result = self.hostRepository.getHosts(filters)
        self.assertEqual([['host1'], ['host2']], result)
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery)

    def test_getHosts_InvokedWithAFewFilters_ReturnsFilteredHosts(self):
        from app.auxiliary import Filters
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll([['host1'], ['host2']])
        expectedQuery = ("SELECT * FROM hostObj AS hosts WHERE 1=1"
                         " AND hosts.status != 'down' AND hosts.checked != 'True'")
        filters: Filters = Filters()
        filters.apply(up=True, down=False, checked=False, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        result = self.hostRepository.getHosts(filters)
        self.assertEqual([['host1'], ['host2']], result)
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery)

    def test_getHostInfo_WhenProvidedHostIpAddress_FetchesHostInformation(self):
        from db.entities.host import hostObj

        expected_host_info: hostObj = MagicMock()
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(mockFirstByReturnValue(expected_host_info))

        actual_host_info = self.hostRepository.getHostInformation("127.0.0.1")
        self.assertEqual(actual_host_info, expected_host_info)

    def test_getHostsAndPorts_InvokedWithNoFilters_FetchesHostsAndPortsMatchingKeywords(self):
        from app.auxiliary import Filters

        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        expectedQuery = expectedGetHostsAndPortsQuery()
        self.getHostsAndPortsTestCase(filters=filters,
                                      service_name="some_service_name", expectedQuery=expectedQuery)

    def test_getHostsAndPorts_InvokedWithFewFilters_FetchesHostsAndPortsWithFiltersApplied(self):
        from app.auxiliary import Filters

        filters: Filters = Filters()
        filters.apply(up=True, down=False, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=False)
        expectedQuery = expectedGetHostsAndPortsQuery(
            with_filter=" AND hosts.status != 'down' AND ports.protocol != 'udp'")
        self.getHostsAndPortsTestCase(filters=filters,
                                      service_name="some_service_name", expectedQuery=expectedQuery)

    def test_deleteHost_InvokedWithAHostId_DeletesProcess(self):
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(mockFirstByReturnValue(self.mockProcess))

        self.hostRepository.deleteHost("some-host-id")
        self.mockDbSession.delete.assert_called_once_with(self.mockProcess)
        self.mockDbSession.commit.assert_called_once()

    def test_toggleHostCheckStatus_WhenHostIsSetToTrue_TogglesToFalse(self):
        self.mockProcess.checked = 'True'
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(mockFirstByReturnValue(self.mockProcess))
        self.hostRepository.toggleHostCheckStatus("some-ip-address")
        self.assertEqual('False', self.mockProcess.checked)
        self.mockDbSession.add.assert_called_once_with(self.mockProcess)
        self.mockDbAdapter.commit.assert_called_once()

    def test_toggleHostCheckStatus_WhenHostIsSetToFalse_TogglesToTrue(self):
        self.mockProcess.checked = 'False'
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(mockFirstByReturnValue(self.mockProcess))
        self.hostRepository.toggleHostCheckStatus("some-ip-address")
        self.assertEqual('True', self.mockProcess.checked)
        self.mockDbSession.add.assert_called_once_with(self.mockProcess)
        self.mockDbAdapter.commit.assert_called_once()
