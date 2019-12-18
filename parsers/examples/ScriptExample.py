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
"""
import xml

from app.auxiliary import log
from parsers.Script import Script

if __name__ == '__main__':

    dom = xml.dom.minidom.parse('a-full.xml')

    for scriptNode in dom.getElementsByTagName('script'):
        script = Script(scriptNode)
        log.info(script.scriptId)
        log.info(script.output)
