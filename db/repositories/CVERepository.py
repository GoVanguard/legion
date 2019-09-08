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


class CVERepository:
    def __init__(self, db_adapter: Database):
        self.db_adapter = db_adapter

    def get_cves_by_host_ip(self, host_ip):
        query = ('SELECT cves.name, cves.severity, cves.product, cves.version, cves.url, cves.source, '
                 'cves.exploitId, cves.exploit, cves.exploitUrl FROM cve AS cves '
                 'INNER JOIN hostObj AS hosts ON hosts.id = cves.hostId '
                 'WHERE hosts.ip = ?')
        return self.db_adapter.metadata.bind.execute(query, str(host_ip)).fetchall()
