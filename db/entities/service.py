"""
LEGION (https://govanguard.com)
Copyright (c) 2020 GoVanguard

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
from sqlalchemy.orm import relationship

from db.database import Base
from db.entities.app import appObj
from db.entities.cve import cve
from db.entities.port import portObj


class serviceObj(Base):
    __tablename__ = 'serviceObj'
    name = Column(String)
    id = Column(Integer, primary_key=True)
    product = Column(String)
    version = Column(String)
    extrainfo = Column(String)
    fingerprint = Column(String)
    hostId = Column(String, ForeignKey('hostObj.id'))
    port = relationship(portObj)
    cves = relationship(cve)
    application = relationship(appObj)

    def __init__(self, name, host, product='', version='', extrainfo='', fingerprint=''):
        self.name = name
        self.product = product
        self.version = version
        self.extrainfo = extrainfo
        self.fingerprint = fingerprint
        self.hostId = host
