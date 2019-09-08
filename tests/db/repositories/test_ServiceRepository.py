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

from tests.db.helpers.db_helpers import mock_execute_fetchall, mock_first_by_return_value, mock_query_with_filter_by


class ServiceRepositoryTest(unittest.TestCase):
    @patch('utilities.stenoLogging.get_logger')
    def setUp(self, get_logger) -> None:
        self.mock_db_adapter = MagicMock()

    def get_service_names_test_case(self, filters, expected_query):
        from db.repositories.ServiceRepository import ServiceRepository

        repository = ServiceRepository(self.mock_db_adapter)

        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall(
            [{'name': 'service_name1'}, {'name': 'service_name2'}])
        service_names = repository.get_service_names(filters)

        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query)
        self.assertEqual([{'name': 'service_name1'}, {'name': 'service_name2'}], service_names)

    def test_get_service_names_InvokedWithNoFilters_FetchesAllServiceNames(self):
        from app.auxiliary import Filters

        expected_query = query = ("SELECT DISTINCT service.name FROM serviceObj as service "
                                  "INNER JOIN portObj as ports "
                                  "INNER JOIN hostObj AS hosts "
                                  "ON hosts.id = ports.hostId AND service.id=ports.serviceId WHERE 1=1 "
                                  "ORDER BY service.name ASC")
        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        self.get_service_names_test_case(filters=filters, expected_query=expected_query)

    def test_get_service_names_InvokedWithFewFilters_FetchesAllServiceNamesWithFiltersApplied(self):
        from app.auxiliary import Filters

        expected_query = ("SELECT DISTINCT service.name FROM serviceObj as service "
                          "INNER JOIN portObj as ports "
                          "INNER JOIN hostObj AS hosts "
                          "ON hosts.id = ports.hostId AND service.id=ports.serviceId WHERE 1=1 "
                          "AND hosts.status != 'down' AND ports.protocol != 'udp' "
                          "ORDER BY service.name ASC")
        filters: Filters = Filters()
        filters.apply(up=True, down=False, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=False)
        self.get_service_names_test_case(filters=filters, expected_query=expected_query)

    def test_get_service_names_by_host_ip_and_port_WhenProvidedWithHostIpAndPort_ReturnsServiceNames(self):
        from db.repositories.ServiceRepository import ServiceRepository
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_first_by_return_value(
            [['service-name1'], ['service-name2']])

        expected_query = ("SELECT services.name FROM serviceObj AS services "
                          "INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
                          "INNER JOIN portObj AS ports ON services.id=ports.serviceId "
                          "WHERE hosts.ip=? and ports.portId = ?")
        service_repository = ServiceRepository(self.mock_db_adapter)
        result = service_repository.get_service_names_by_host_ip_and_port("some_host", "1234")
        self.assertEqual([['service-name1'], ['service-name2']], result)
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_host", "1234")
