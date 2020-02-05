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
from sqlalchemy import Integer, Column, String, ForeignKey

from db.database import Base


class osObj(Base):
    __tablename__ = 'osObj'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    family = Column(String)
    generation = Column(String)
    osType = Column(String)
    vendor = Column(String)
    accuracy = Column(String)
    hostId = Column(String, ForeignKey('hostObj.id'))

    def __init__(self, name, *args):
        self.name = name
        self.family = args[0]
        self.generation = args[1]
        self.osType = args[2]
        self.vendor = args[3]
        self.accuracy = args[4]
        self.hostId = args[5]
