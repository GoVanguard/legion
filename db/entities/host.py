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
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from db.database import Base
from db.entities.cve import cve
from db.entities.os import osObj
from db.entities.port import portObj


class hostObj(Base):
    __tablename__ = 'hostObj'
    # State
    state = Column(String)
    count = Column(String)
    checked = Column(String)

    # OS
    osMatch = Column(String)
    osAccuracy = Column(String)
    vendor = Column(String)
    uptime = Column(String)
    lastboot = Column(String)

    # Network
    isp = Column(String)
    asn = Column(String)
    ip = Column(String)
    ipv4 = Column(String)
    ipv6 = Column(String)
    macaddr = Column(String)
    status = Column(String)
    hostname = Column(String)

    # ID
    hostId = Column(String)
    id = Column(Integer, primary_key=True)

    # Location
    city = Column(String)
    countryCode = Column(String)
    postalCode = Column(String)
    longitude = Column(String)
    latitude = Column(String)
    distance = Column(String)

    # host relationships
    os = relationship(osObj)
    ports = relationship(portObj)
    cves = relationship(cve)

    def __init__(self, **kwargs):
        self.checked = kwargs.get('checked') or 'False'
        self.osMatch = kwargs.get('osMatch') or 'unknown'
        self.osAccuracy = kwargs.get('osAccuracy') or 'NaN'
        self.ip = kwargs.get('ip') or 'unknown'
        self.ipv4 = kwargs.get('ipv4') or 'unknown'
        self.ipv6 = kwargs.get('ipv6') or 'unknown'
        self.macaddr = kwargs.get('macaddr') or 'unknown'
        self.status = kwargs.get('status') or 'unknown'
        self.hostname = kwargs.get('hostname') or 'unknown'
        self.hostId = kwargs.get('hostname') or 'unknown'
        self.vendor = kwargs.get('vendor') or 'unknown'
        self.uptime = kwargs.get('uptime') or 'unknown'
        self.lastboot = kwargs.get('lastboot') or 'unknown'
        self.distance = kwargs.get('distance') or 'unknown'
        self.state = kwargs.get('state') or 'unknown'
        self.count = kwargs.get('count') or 'unknown'
        self.city = kwargs.get('city') or 'unknown'
        self.countryCode = kwargs.get('countryCode') or 'unknown'
        self.postalCode = kwargs.get('postalCode') or 'unknown'
        self.longitude = kwargs.get('longitude') or 'unknown'
        self.latitude = kwargs.get('latitude') or 'unknown'
        self.isp = kwargs.get('isp') or 'unknown'
        self.asn = kwargs.get('asn') or 'unknown'
