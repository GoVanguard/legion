"""
LEGION (https://govanguard.com)
Copyright (c) 2022 GoVanguard

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
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from db.database import Base


class process(Base):
    __tablename__ = 'process'
    pid = Column(String)
    id = Column(Integer, primary_key = True)
    display = Column(String)
    name = Column(String)
    tabTitle = Column(String)
    hostIp = Column(String)
    port = Column(String)
    protocol = Column(String)
    command = Column(String)
    startTime = Column(String)
    endTime = Column(String)
    estimatedRemaining = Column(Integer)
    elapsed = Column(Integer)
    outputfile = Column(String)
    output = relationship("process_output")
    status = Column(String)
    closed = Column(String)

    def __init__(self, pid, *args):
        self.display = 'True'
        self.pid = pid
        self.name = args[0]
        self.tabTitle = args[1]
        self.hostIp = args[2]
        self.port = args[3]
        self.protocol = args[4]
        self.command = args[5]
        self.startTime = args[6]
        self.endTime = args[7]
        self.outputfile = args[8]
        self.output = args[10]
        self.status = args[9]
        self.closed = 'False'
        self.estimatedRemaining = args[11]
        self.elapsed = args[12]