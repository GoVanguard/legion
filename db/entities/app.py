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
from sqlalchemy import Column, String, ForeignKey, Integer

from db.database import Base


class appObj(Base):
    __tablename__ = 'appObj'
    name = Column(String)
    id = Column(Integer, primary_key=True)
    product = Column(String)
    version = Column(String)
    extrainfo = Column(String)
    fingerprint = Column(String)
    cpe = Column(String)
    serviceId = Column(String, ForeignKey('serviceObj.id'))

    def __init__(self, name='', product='', version='', extrainfo='', fingerprint='', cpe=''):
        self.name = name
        self.product = product
        self.version = version
        self.extrainfo = extrainfo
        self.fingerprint = fingerprint
        self.cpe = cpe
