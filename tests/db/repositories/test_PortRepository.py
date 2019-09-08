"""
LEGION (https://govanguard.io)
Copyright (c) 2018-2019 GoVanguard

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
from unittest.mock import patch, MagicMock

from tests.db.helpers.db_helpers import mock_first_by_return_value, mock_execute_fetchall


class PortRepositoryTest(unittest.TestCase):
    @patch('utilities.stenoLogging.get_logger')
    def setUp(self, get_logger) -> None:
        self.mock_db_adapter = MagicMock()

    def test_get_ports_by_ip_and_protocol_ReturnsPorts(self):
        from db.repositories.PortRepository import PortRepository

        expected_query = ("SELECT ports.portId FROM portObj AS ports "
                          "INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
                          "WHERE hosts.ip = ? and ports.protocol = ?")
        repository = PortRepository(self.mock_db_adapter)
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_first_by_return_value(
            [['port-id1'], ['port-id2']])
        ports = repository.get_ports_by_ip_and_protocol("some_host_ip", "tcp")

        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_host_ip", "tcp")
        self.assertEqual([['port-id1'], ['port-id2']], ports)

    def test_get_port_states_by_host_id_ReturnsPortsStates(self):
        from db.repositories.PortRepository import PortRepository

        expected_query = 'SELECT port.state FROM portObj as port WHERE port.hostId = ?'
        repository = PortRepository(self.mock_db_adapter)
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall(
            [['port-state1'], ['port-state2']])
        port_states = repository.get_port_states_by_host_id("some_host_id")

        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_host_id")
        self.assertEqual([['port-state1'], ['port-state2']], port_states)

    def test_get_ports_and_services_by_host_ip_InvokedWithNoFilters_ReturnsPortsAndServices(self):
        from db.repositories.PortRepository import PortRepository
        from app.auxiliary import Filters

        expected_query = ("SELECT hosts.ip, ports.portId, ports.protocol, ports.state, ports.hostId, ports.serviceId, "
                          "services.name, services.product, services.version, services.extrainfo, services.fingerprint "
                          "FROM portObj AS ports INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
                          "LEFT OUTER JOIN serviceObj AS services ON services.id = ports.serviceId "
                          "WHERE hosts.ip = ?")
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([['ip1'], ['ip2']])
        repository = PortRepository(self.mock_db_adapter)

        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        results = repository.get_ports_and_services_by_host_ip("some_host_ip", filters)

        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_host_ip")
        self.assertEqual([['ip1'], ['ip2']], results)

    def test_get_ports_and_services_by_host_ip_InvokedWithFewFilters_ReturnsPortsAndServices(self):
        from db.repositories.PortRepository import PortRepository
        from app.auxiliary import Filters

        expected_query = ("SELECT hosts.ip, ports.portId, ports.protocol, ports.state, ports.hostId, ports.serviceId, "
                          "services.name, services.product, services.version, services.extrainfo, services.fingerprint "
                          "FROM portObj AS ports INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
                          "LEFT OUTER JOIN serviceObj AS services ON services.id = ports.serviceId "
                          "WHERE hosts.ip = ? AND ports.protocol != 'tcp' AND ports.protocol != 'udp'")
        self.mock_db_adapter.metadata.bind.execute.return_value = mock_execute_fetchall([['ip1'], ['ip2']])
        repository = PortRepository(self.mock_db_adapter)

        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=False, udp=False)
        results = repository.get_ports_and_services_by_host_ip("some_host_ip", filters)

        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_host_ip")
        self.assertEqual([['ip1'], ['ip2']], results)
