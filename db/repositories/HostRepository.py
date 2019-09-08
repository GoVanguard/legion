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
from app.auxiliary import Filters
from db.database import Database, hostObj
from db.filters import apply_filters, apply_hosts_filters


class HostRepository:
    def __init__(self, db_adapter: Database):
        self.db_adapter = db_adapter

    def exists(self, host: str):
        query = 'SELECT host.ip FROM hostObj AS host WHERE host.ip == ? OR host.hostname == ?'
        result = self.db_adapter.metadata.bind.execute(query, str(host), str(host)).fetchall()
        return True if result else False

    def get_hosts(self, filters):
        query = 'SELECT * FROM hostObj AS hosts WHERE 1=1'
        query += apply_hosts_filters(filters)
        return self.db_adapter.metadata.bind.execute(query).fetchall()

    def get_hosts_and_ports_by_service_name(self, service_name, filters: Filters):
        query = ("SELECT hosts.ip,ports.portId,ports.protocol,ports.state,ports.hostId,ports.serviceId,"
                 "services.name,services.product,services.version,services.extrainfo,services.fingerprint "
                 "FROM portObj AS ports " +
                 "INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId " +
                 "LEFT OUTER JOIN serviceObj AS services ON services.id=ports.serviceId " +
                 "WHERE services.name=?")
        query += apply_filters(filters)
        return self.db_adapter.metadata.bind.execute(query, str(service_name)).fetchall()

    def get_host_information(self, host_ip_address: str):
        session = self.db_adapter.session()
        return session.query(hostObj).filter_by(ip=str(host_ip_address)).first()
