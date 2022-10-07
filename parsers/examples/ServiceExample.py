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

"""
import sys
import xml

from app.auxiliary import log
from parsers.Service import Service

if __name__ == '__main__':

    dom = xml.dom.minidom.parse('i.xml')

    service_nodes = dom.getElementsByTagName('service')
    if len(service_nodes) == 0:
        sys.exit()

    node = dom.getElementsByTagName('service')[0]

    s = Service( node )
    log.info(s.name)
    log.info(s.product)
    log.info(s.version)
    log.info(s.extrainfo)
    log.info(s.fingerprint)