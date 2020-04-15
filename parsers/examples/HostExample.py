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

"""
import sys

import xml

from app.logging.legionLog import getAppLogger
from parsers.Host import Host

log = getAppLogger()

if __name__ == '__main__':

    dom = xml.dom.minidom.parse('/tmp/test_pwn01.xml')
    hostNodes = dom.getElementsByTagName('host')

    if len(hostNodes) == 0:
        sys.exit( )

    hostNode = dom.getElementsByTagName('host')[0]

    h = Host( hostNode )
    log.info('host status: ' + h.status)
    log.info('host ip: ' + h.ip)

    for port in h.getPorts( 'tcp', 'open' ):
        log.info(port + " is open")

    log.info("script output:")
    for scr in h.getScripts():
        log.info("script id:" + scr.scriptId)
        log.info("Output:")
        log.info(scr.output)

    log.info("service of tcp port 80:")
    s = h.getService( 'tcp', '80' )
    if s is None:
        log.info("\tno service")

    else:
        log.info("\t" + s.name)
        log.info("\t" + s.product)
        log.info("\t" + s.version)
        log.info("\t" + s.extrainfo)
        log.info("\t" + s.fingerprint)