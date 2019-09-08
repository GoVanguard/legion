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
from db.database import Database
from db.filters import apply_port_filters


class PortRepository:
    def __init__(self, db_adapter: Database):
        self.db_adapter = db_adapter

    def get_ports_by_ip_and_protocol(self, host_ip, protocol):
        query = ("SELECT ports.portId FROM portObj AS ports INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
                 "WHERE hosts.ip = ? and ports.protocol = ?")
        return self.db_adapter.metadata.bind.execute(query, str(host_ip), str(protocol)).first()

    def get_port_states_by_host_id(self, host_id):
        query = 'SELECT port.state FROM portObj as port WHERE port.hostId = ?'
        return self.db_adapter.metadata.bind.execute(query, str(host_id)).fetchall()

    def get_ports_and_services_by_host_ip(self, host_ip, filters):
        query = ("SELECT hosts.ip, ports.portId, ports.protocol, ports.state, ports.hostId, ports.serviceId, "
                 "services.name, services.product, services.version, services.extrainfo, services.fingerprint "
                 "FROM portObj AS ports INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
                 "LEFT OUTER JOIN serviceObj AS services ON services.id = ports.serviceId WHERE hosts.ip = ?")
        query += apply_port_filters(filters)
        return self.db_adapter.metadata.bind.execute(query, str(host_ip)).fetchall()
