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

class ScriptRepository:
    def __init__(self, dbAdapter: Database):
        self.dbAdapter = dbAdapter

    def getScriptsByHostIP(self, hostIP):
        session = self.dbAdapter.session()
        query = text("SELECT host.id, host.scriptId, port.portId, port.protocol FROM l1ScriptObj AS host "
                     "INNER JOIN hostObj AS hosts ON hosts.id = host.hostId "
                     "LEFT OUTER JOIN portObj AS port ON port.id = host.portId WHERE hosts.ip=:hostIP")
        result = session.execute(query, {'hostIP': str(hostIP)}).fetchall()
        session.close()
        return result

    def getScriptOutputById(self, scriptDBId):
        session = self.dbAdapter.session()
        query = text("SELECT script.output FROM l1ScriptObj as script WHERE script.id = :scriptDBId")
        result = session.execute(query, {'scriptDBId': str(scriptDBId)}).fetchall()
        session.close()
        return result
