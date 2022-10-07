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
from sqlalchemy import String, Column

from db.database import Base


class nmapSessionObj(Base):
    __tablename__ = 'nmapSessionObj'
    filename = Column(String, primary_key=True)
    startTime = Column(String)
    finish_time = Column(String)
    nmapVersion = Column(String)
    scanArgs = Column(String)
    totalHosts = Column(String)
    upHosts = Column(String)
    downHosts = Column(String)

    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self.startTime = args[0]
        self.finish_time = args[1]
        self.nmapVersion = kwargs.get('nmapVersion') or 'unknown'
        self.scanArgs = kwargs.get('scanArgs') or ''
        self.totalHosts = kwargs.get('total_host') or '0'
        self.upHosts = kwargs.get('upHosts') or '0'
        self.downHosts = kwargs.get('downHosts') or '0'
