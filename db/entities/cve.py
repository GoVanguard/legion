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
from sqlalchemy import String, Column, Integer, ForeignKey

from db.database import Base


class cve(Base):
    __tablename__ = 'cve'
    name = Column(String)
    id = Column(Integer, primary_key=True)
    url = Column(String)
    product = Column(String)
    severity = Column(String)
    source = Column(String)
    version = Column(String)
    exploitId = Column(Integer)
    exploit = Column(String)
    exploitUrl = Column(String)
    serviceId = Column(String, ForeignKey('serviceObj.id'))
    hostId = Column(String, ForeignKey('hostObj.id'))

    def __init__(self, name, url, product, hostId, severity='', source='', version='', exploitId=0, exploit='',
                 exploitUrl=''):
        self.url = url
        self.name = name
        self.product = product
        self.severity = severity
        self.source = source
        self.version = version
        self.exploitId = exploitId
        self.exploit = exploit
        self.exploitUrl = exploitUrl
        self.hostId = hostId
