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

Author(s): Shane Scott (sscott@gotham-security.com), Dmitriy Dubson (d.dubson@gmail.com)
"""

from typing import Union

from six import u as unicode

from app.timing import getTimestamp
from sqlalchemy import text
from db.SqliteDbAdapter import Database
from db.entities.process import process
from db.entities.processOutput import process_output


class ProcessRepository:
    def __init__(self, dbAdapter: Database, log):
        self.dbAdapter = dbAdapter
        self.log = log

    # the showProcesses flag is used to ensure we don't display processes in the process table after we have cleared
    # them or when an existing project is opened.
    # to speed up the queries we replace the columns we don't need by zeros (the reason we need all the columns is
    # we are using the same model to display process information everywhere)

    def getProcesses(self, filters, showProcesses: Union[str, bool] = 'noNmap', sort: str = 'desc', ncol: str = 'id'):
        # we do not fetch nmap processes because these are not displayed in the host tool tabs / tools
        session = self.dbAdapter.session()
        if showProcesses == 'noNmap':
            query = text('SELECT "0", "0", "0", process.name, "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0" '
                         'FROM process AS process WHERE process.closed = "False" AND process.name != "nmap" '
                         'GROUP BY process.name')
            result = session.execute(query).fetchall()
        elif not showProcesses:
            query = text('SELECT process.id, process.hostIp, process.tabTitle, process.outputfile, output.output '
                         'FROM process AS process INNER JOIN process_output AS output ON process.id = output.processId '
                         'WHERE process.display = :display AND process.closed = "False" order by process.id desc')
            result = session.execute(query, {'display': str(showProcesses)}).fetchall()
        else:
            query = text('SELECT * FROM process AS process WHERE process.display=:display order by {0} {1}'.format(ncol, sort))
            result = session.execute(query, {'display': str(showProcesses)}).fetchall()
        session.close()
        return result

    def storeProcess(self, proc):
        session = self.dbAdapter.session()
        p_output = process_output()
       
        #p = process(str(proc.processId()), str(proc.name), str(proc.tabTitle),
        p = process(str(proc.processId()), str(proc.name), str(proc.tabTitle),
                    str(proc.hostIp), str(proc.port), str(proc.protocol),
                    unicode(proc.command), proc.startTime, "", str(proc.outputfile),
                    'Waiting', [p_output], 100, 0)

        self.log.info(f"Adding process: {p}")
        session.add(p)
        session.commit()
        proc.id = p.id
        session.close()
        return proc.id

    def storeProcessOutput(self, process_id: str, output: str):
        session = self.dbAdapter.session()
        proc = session.query(process).filter_by(id=process_id).first()

        if not proc:
            session.close()
            return False

        proc_output = session.query(process_output).filter_by(id=process_id).first()
        if proc_output:
            self.log.info("Storing process output into db: {0}".format(str(proc_output)))
            proc_output.output = unicode(output)
            session.add(proc_output)

        proc.endTime = getTimestamp(True)

        if proc.status == "Killed" or proc.status == "Cancelled" or proc.status == "Crashed":
            #session.commit() # Needed?
            session.close()
            return True
        else:
            proc.status = 'Finished'
            session.add(proc)
            session.commit()
        session.close()

    def getStatusByProcessId(self, process_id: str):
        return self.getFieldByProcessId("status", process_id)

    def getPIDByProcessId(self, process_id: str):
        return self.getFieldByProcessId("pid", process_id)

    def isKilledProcess(self, process_id: str) -> bool:
        status = self.getFieldByProcessId("status", process_id)
        return True if status == "Killed" else False

    def isCancelledProcess(self, process_id: str) -> bool:
        status = self.getFieldByProcessId("status", process_id)
        return True if status == "Cancelled" else False

    def getFieldByProcessId(self, field_name: str, process_id: str):
        session = self.dbAdapter.session()
        query = text("SELECT process.{0} FROM process AS process WHERE process.id=:process_id".format(field_name))
        p = session.execute(query, {'process_id': str(process_id)}).fetchall()
        result = p[0][0] if p else -1
        session.close()
        return result

    def getHostsByToolName(self, toolName: str, closed: str = "False"):
        session = self.dbAdapter.session()
        if closed == 'FetchAll':
            query = text('SELECT "0", "0", "0", "0", "0", process.hostIp, process.port, process.protocol, "0", "0", '
                         'process.outputfile, "0", "0", "0" FROM process AS process WHERE process.name=:toolName')
        else:
            query = text('SELECT process.id, "0", "0", "0", "0", "0", "0", process.hostIp, process.port, '
                         'process.protocol, "0", "0", process.outputfile, "0", "0", "0" FROM process AS process '
                         'WHERE process.name=:toolName and process.closed="False"')
        result = session.execute(query, {'toolName': str(toolName)}).fetchall()
        session.close()
        return result

    def storeProcessCrashStatus(self, processId: str):
        session = self.dbAdapter.session()
        proc = session.query(process).filter_by(id=processId).first()
        if proc and not proc.status == 'Killed' and not proc.status == 'Cancelled':
            proc.status = 'Crashed'
            proc.endTime = getTimestamp(True)
            session.add(proc)
            session.commit()
        session.close()

    def storeProcessCancelStatus(self, processId: str):
        session = self.dbAdapter.session()
        proc = session.query(process).filter_by(id=processId).first()
        if proc:
            proc.status = 'Cancelled'
            proc.endTime = getTimestamp(True)
            session.add(proc)
            session.commit()
        session.close()

    def storeProcessKillStatus(self, processId: str):
        session = self.dbAdapter.session()
        proc = session.query(process).filter_by(id=processId).first()
        if proc and not proc.status == 'Finished':
            proc.status = 'Killed'
            proc.endTime = getTimestamp(True)
            session.add(proc)
            session.commit()
        session.close()

    def storeProcessRunningStatus(self, processId: str, pid):
        session = self.dbAdapter.session()
        proc = session.query(process).filter_by(id=processId).first()
        if proc:
            proc.status = 'Running'
            proc.pid = str(pid)
            session.add(proc)
            session.commit()
        session.close()

    def storeProcessRunningElapsedTime(self, processId: str, elapsed):
        session = self.dbAdapter.session()
        proc = session.query(process).filter_by(id=processId).first()
        if proc:
            proc.elapsed = elapsed
            session.add(proc)
            session.commit()

    def storeCloseStatus(self, processId):
        session = self.dbAdapter.session()
        proc = session.query(process).filter_by(id=processId).first()
        if proc:
            proc.closed = 'True'
            session.add(proc)
            session.commit()
        session.close()

    def storeScreenshot(self, ip: str, port: str, filename: str):
        session = self.dbAdapter.session()
        p = process(0, "screenshooter", "screenshot (" + str(port) + "/tcp)", str(ip), str(port), "tcp", "",
                    getTimestamp(True), getTimestamp(True), str(filename), "Finished", [process_output()], 2, 0)
        if p:
            session.add(p)
            session.commit()
            pD = p.id
            session.close()
        return pD

    def toggleProcessDisplayStatus(self, resetAll=False):
        session = self.dbAdapter.session()
        proc = session.query(process).filter_by(display='True').all()
        for p in proc:
            session.add(self.toggleProcessStatusField(p, resetAll))
        session.commit()
        session.close()

    @staticmethod
    def toggleProcessStatusField(p, reset_all):
        not_running = p.status != 'Running'
        not_waiting = p.status != 'Waiting'

        if (reset_all and not_running) or (not_running and not_waiting):
            p.display = 'False'

        return p
