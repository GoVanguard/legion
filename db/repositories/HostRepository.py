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
from db.database import Database
from db.entities.host import hostObj
from db.filters import applyFilters, applyHostsFilters


class HostRepository:
    def __init__(self, dbAdapter: Database):
        self.dbAdapter = dbAdapter

    def exists(self, host: str):
        query = 'SELECT host.ip FROM hostObj AS host WHERE host.ip == ? OR host.hostname == ?'
        result = self.dbAdapter.metadata.bind.execute(query, str(host), str(host)).fetchall()
        return True if result else False

    def getHosts(self, filters):
        query = 'SELECT * FROM hostObj AS hosts WHERE 1=1'
        query += applyHostsFilters(filters)
        return self.dbAdapter.metadata.bind.execute(query).fetchall()

    def getHostsAndPortsByServiceName(self, service_name, filters: Filters):
        query = ("SELECT hosts.ip,ports.portId,ports.protocol,ports.state,ports.hostId,ports.serviceId,"
                 "services.name,services.product,services.version,services.extrainfo,services.fingerprint "
                 "FROM portObj AS ports " +
                 "INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId " +
                 "LEFT OUTER JOIN serviceObj AS services ON services.id=ports.serviceId " +
                 "WHERE services.name=?")
        query += applyFilters(filters)
        return self.dbAdapter.metadata.bind.execute(query, str(service_name)).fetchall()

    def getHostInformation(self, host_ip_address: str):
        session = self.dbAdapter.session()
        return session.query(hostObj).filter_by(ip=str(host_ip_address)).first()

    def deleteHost(self, hostIP):
        session = self.dbAdapter.session()
        h = session.query(hostObj).filter_by(ip=str(hostIP)).first()
        session.delete(h)
        session.commit()

    def toggleHostCheckStatus(self, ipAddress):
        session = self.dbAdapter.session()
        host = session.query(hostObj).filter_by(ip=ipAddress).first()
        if host:
            if host.checked == 'False':
                host.checked = 'True'
            else:
                host.checked = 'False'
            session.add(host)
            self.dbAdapter.commit()
