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
from app.auxiliary import log
from parsers.Parser import Parser

if __name__ == '__main__':
    parser = Parser('a-full.xml')

    log.info('\nscan session:')
    session = parser.getSession()
    log.info("\tstart time:\t" + session.startTime)
    log.info("\tstop time:\t" + session.finish_time)
    log.info("\tnmap version:\t" + session.nmapVersion)
    log.info("\tnmap args:\t" + session.scanArgs)
    log.info("\ttotal hosts:\t" + session.totalHosts)
    log.info("\tup hosts:\t" + session.upHosts)
    log.info("\tdown hosts:\t" + session.downHosts)

    for h in parser.getAllHosts():

        log.info('host ' + h.ip + ' is ' + h.status)

        for port in h.getPorts('tcp', 'open'):
            print(port)
            log.info("\t---------------------------------------------------")
            log.info("\tservice of tcp port " + port + ":")
            s = h.getService('tcp', port)

            if s == None:
                log.info("\t\tno service")

            else:
                log.info("\t\t" + s.name)
                log.info("\t\t" + s.product)
                log.info("\t\t" + s.version)
                log.info("\t\t" + s.extrainfo)
                log.info("\t\t" + s.fingerprint)

            log.info("\tscript output:")
            sc = port.getScripts()

            if sc == None:
                log.info("\t\tno scripts")

            else:
                for scr in sc:
                    log.info("Script ID: " + scr.scriptId)
                    log.info("Output: ")
                    log.info(scr.output)

            log.info("\t---------------------------------------------------")