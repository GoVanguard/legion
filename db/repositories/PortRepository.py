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

from sqlalchemy import text
from db.SqliteDbAdapter import Database
from db.entities.l1script import l1ScriptObj
from db.entities.port import portObj
from db.filters import applyPortFilters


class PortRepository:
    def __init__(self, dbAdapter: Database):
        self.dbAdapter = dbAdapter

    def getPortsByIPAndProtocol(self, host_ip, protocol):
        session = self.dbAdapter.session()
        query = text("SELECT ports.portId FROM portObj AS ports INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
                     "WHERE hosts.ip = :host_ip and ports.protocol = :protocol")
        result = session.execute(query, {'host_ip': str(host_ip), 'protocol': str(protocol)}).first()
        session.close()
        return result

    def getPortStatesByHostId(self, host_id):
        session = self.dbAdapter.session()
        query = text('SELECT port.state FROM portObj as port WHERE port.hostId = :host_id')
        result = session.execute(query, {'host_id': str(host_id)}).fetchall()
        session.close()
        return result

    def getPortsAndServicesByHostIP(self, host_ip, filters):
        session = self.dbAdapter.session()
        query = ("SELECT hosts.ip, ports.portId, ports.protocol, ports.state, ports.hostId, ports.serviceId, "
                 "services.name, services.product, services.version, services.extrainfo, services.fingerprint "
                 "FROM portObj AS ports INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
                 "LEFT OUTER JOIN serviceObj AS services ON services.id = ports.serviceId WHERE hosts.ip = :host_ip")
        query += applyPortFilters(filters)
        query = text(query)
        result = session.execute(query, {'host_ip': str(host_ip)}).fetchall()
        session.close()
        return result

    # used to delete all port/script data related to a host - to overwrite portscan info with the latest scan
    def deleteAllPortsAndScriptsByHostId(self, hostID, protocol):
        session = self.dbAdapter.session()
        ports_for_host = session.query(portObj)\
            .filter(portObj.hostId == hostID)\
            .filter(portObj.protocol == str(protocol)).all()

        for p in ports_for_host:
            scripts_for_ports = session.query(l1ScriptObj).filter(l1ScriptObj.portId == p.id).all()
            for s in scripts_for_ports:
                session.delete(s)
        for p in ports_for_host:
            session.delete(p)
        session.commit()
        session.close()
