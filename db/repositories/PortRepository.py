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
from db.entities.l1script import l1ScriptObj
from db.entities.port import portObj
from db.filters import applyPortFilters


class PortRepository:
    def __init__(self, dbAdapter: Database):
        self.dbAdapter = dbAdapter

    def getPortsByIPAndProtocol(self, host_ip, protocol):
        query = ("SELECT ports.portId FROM portObj AS ports INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
                 "WHERE hosts.ip = ? and ports.protocol = ?")
        return self.dbAdapter.metadata.bind.execute(query, str(host_ip), str(protocol)).first()

    def getPortStatesByHostId(self, host_id):
        query = 'SELECT port.state FROM portObj as port WHERE port.hostId = ?'
        return self.dbAdapter.metadata.bind.execute(query, str(host_id)).fetchall()

    def getPortsAndServicesByHostIP(self, host_ip, filters):
        query = ("SELECT hosts.ip, ports.portId, ports.protocol, ports.state, ports.hostId, ports.serviceId, "
                 "services.name, services.product, services.version, services.extrainfo, services.fingerprint "
                 "FROM portObj AS ports INNER JOIN hostObj AS hosts ON hosts.id = ports.hostId "
                 "LEFT OUTER JOIN serviceObj AS services ON services.id = ports.serviceId WHERE hosts.ip = ?")
        query += applyPortFilters(filters)
        return self.dbAdapter.metadata.bind.execute(query, str(host_ip)).fetchall()

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
