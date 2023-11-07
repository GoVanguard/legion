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

"""
import xml

from app.auxiliary import log
from parsers.Session import Session

if __name__ == '__main__':

    dom = xml.dom.minidom.parse('i.xml')
    dom.getElementsByTagName('finished')[0].getAttribute('timestr')

    MySession = { 'finish_time': dom.getElementsByTagName('finished')[0].getAttribute('timestr'),
                  'nmapVersion' : '4.79', 'scanArgs' : '-sS -sV -A -T4',
                  'startTime' : dom.getElementsByTagName('nmaprun')[0].getAttribute('startstr'),
                  'totalHosts' : '1', 'upHosts' : '1', 'downHosts' : '0' }

    s = Session( MySession )

    log.info('startTime:' + s.startTime)
    log.info('finish_time:' + s.finish_time)
    log.info('nmapVersion:' + s.nmapVersion)
    log.info('nmap_args:' + s.scanArgs)
    log.info('total hosts:' + s.totalHosts)
    log.info('up hosts:' + s.upHosts)
    log.info('down hosts:' + s.downHosts)