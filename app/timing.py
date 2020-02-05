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
from datetime import datetime
from functools import wraps
from time import time

from app.logging.legionLog import log

timestampFormats = {
    "HUMAN_FORMAT": "%d %b %Y %H:%M:%S.%f",
    "STANDARD_TIMESTAMP": '%Y%m%d%H%M%S%f'
}


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        tr = te - ts
        log.debug('Function:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, tr))
        return result

    return wrap


def getTimestamp(human: bool = False) -> str:
    timeFormat = timestampFormats["HUMAN_FORMAT"] if human else timestampFormats["STANDARD_TIMESTAMP"]
    return datetime.fromtimestamp(time()).strftime(timeFormat)
