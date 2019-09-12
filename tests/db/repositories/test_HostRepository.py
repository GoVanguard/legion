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
from unittest.mock import MagicMock, patch

from tests.db.helpers.db_helpers import mock_execute_fetchall, mock_query_with_filter_by, mock_first_by_return_value

exists_query = 'SELECT host.ip FROM hostObj AS host WHERE host.ip == ? OR host.hostname == ?'


def expected_get_hosts_and_ports_query(with_filter: str = "") -> str:
    query = (
        "SELECT hosts.ip,ports.portId,ports.protocol,ports.state,ports.hostId,ports.serviceId,services.name,"
        "services.product,services.version,services.extrainfo,services.fingerprint FROM portObj AS ports "
        "INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
        "LEFT OUTER JOIN serviceObj AS services ON services.id=ports.serviceId "
        "WHERE services.name=?")
    query += with_filter
    return query


class HostRepositoryTest(unittest.TestCase):
    @patch('utilities.stenoLogging.get_logger')
    def setUp(self, get_logger) -> None:
        self.mock_db_adapter = MagicMock()

    def get_hosts_and_ports_test_case(self, filters, service_name, expected_query):
        from db.repositories.HostRepository import HostRepository

        repository = HostRepository(self.mock_db_adapter)
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall(
            [{'name': 'service_name1'}, {'name': 'service_name2'}])
        service_names = repository.get_hosts_and_ports_by_service_name(service_name, filters)

        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, service_name)
        self.assertEqual([{'name': 'service_name1'}, {'name': 'service_name2'}], service_names)

    def test_exists_WhenProvidedAExistingHosts_ReturnsTrue(self):
        from db.repositories.HostRepository import HostRepository
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([['some-ip']])

        host_repository = HostRepository(self.mock_db_adapter)
        self.assertTrue(host_repository.exists("some_host"))
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(exists_query, "some_host", "some_host")

    def test_exists_WhenProvidedANonExistingHosts_ReturnsFalse(self):
        from db.repositories.HostRepository import HostRepository
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([])

        host_repository = HostRepository(self.mock_db_adapter)
        self.assertFalse(host_repository.exists("some_host"))
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(exists_query, "some_host", "some_host")

    def test_get_hosts_InvokedWithNoFilters_ReturnsHosts(self):
        from db.repositories.HostRepository import HostRepository
        from app.auxiliary import Filters
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([['host1'], ['host2']])
        expected_query = "SELECT * FROM hostObj AS hosts WHERE 1=1"
        host_repository = HostRepository(self.mock_db_adapter)
        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        result = host_repository.get_hosts(filters)
        self.assertEqual([['host1'], ['host2']], result)
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query)

    def test_get_hosts_InvokedWithAFewFilters_ReturnsFilteredHosts(self):
        from db.repositories.HostRepository import HostRepository
        from app.auxiliary import Filters
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([['host1'], ['host2']])
        expected_query = ("SELECT * FROM hostObj AS hosts WHERE 1=1"
                          " AND hosts.status != 'down' AND hosts.checked != 'True'")
        host_repository = HostRepository(self.mock_db_adapter)
        filters: Filters = Filters()
        filters.apply(up=True, down=False, checked=False, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        result = host_repository.get_hosts(filters)
        self.assertEqual([['host1'], ['host2']], result)
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query)

    def test_get_host_info_WhenProvidedHostIpAddress_FetchesHostInformation(self):
        from db.database import hostObj
        from db.repositories.HostRepository import HostRepository

        mock_db_session = MagicMock()
        expected_host_info: hostObj = MagicMock()
        self.mock_db_adapter.session.return_value = mock_db_session
        mock_db_session.query.return_value = mock_query_with_filter_by(mock_first_by_return_value(expected_host_info))

        repository = HostRepository(self.mock_db_adapter)
        actual_host_info = repository.get_host_information("127.0.0.1")
        self.assertEqual(actual_host_info, expected_host_info)

    def test_get_hosts_and_ports_InvokedWithNoFilters_FetchesHostsAndPortsMatchingKeywords(self):
        from app.auxiliary import Filters

        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        expected_query = expected_get_hosts_and_ports_query()
        self.get_hosts_and_ports_test_case(filters=filters,
                                           service_name="some_service_name", expected_query=expected_query)

    def test_get_hosts_and_ports_InvokedWithFewFilters_FetchesHostsAndPortsWithFiltersApplied(self):
        from app.auxiliary import Filters

        filters: Filters = Filters()
        filters.apply(up=True, down=False, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=False)
        expected_query = expected_get_hosts_and_ports_query(
            with_filter=" AND hosts.status != 'down' AND ports.protocol != 'udp'")
        self.get_hosts_and_ports_test_case(filters=filters,
                                           service_name="some_service_name", expected_query=expected_query)
