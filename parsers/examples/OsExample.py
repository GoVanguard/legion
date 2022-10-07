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
import xml

from app.auxiliary import log
from parsers.OS import OS

if __name__ == '__main__':
    dom = xml.dom.minidom.parse('test.xml')
    osclass = dom.getElementsByTagName('osclass')[0]
    osmatch = dom.getElementsByTagName('osmatch')[0]

    os = OS(osclass)
    log.info(os.name)
    log.info(os.family)
    log.info(os.generation)
    log.info(os.osType)
    log.info(os.vendor)
    log.info(str(os.accuracy))

    os = OS(osmatch)
    log.info(os.name)
    log.info(os.family)
    log.info(os.generation)
    log.info(os.osType)
    log.info(os.vendor)
    log.info(str(os.accuracy))