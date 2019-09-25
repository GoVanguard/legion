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
from sqlalchemy import Column, Integer, String, ForeignKey

from db.database import Base
from six import u as unicode


class l2ScriptObj(Base):
    __tablename__ = 'l2ScriptObj'
    scriptId = Column(String)
    id = Column(Integer, primary_key=True)
    output = Column(String)
    portId = Column(String, ForeignKey('portObj.id'))
    hostId = Column(String, ForeignKey('hostObj.id'))

    def __init__(self, scriptId, output, portId, hostId):
        self.scriptId = scriptId
        self.output = unicode(output)
        self.portId = portId
        self.hostId = hostId
