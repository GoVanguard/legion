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
from app.auxiliary import getTimestamp
from db.database import *
from six import u as unicode


class ProcessRepository:
    def __init__(self, db_adapter: Database, log):
        self.db_adapter = db_adapter
        self.log = log

    def store_process_output(self, process_id: str, output: str):
        session = self.db_adapter.session()
        proc = session.query(process).filter_by(id=process_id).first()

        if not proc:
            return False

        proc_output = session.query(process_output).filter_by(id=process_id).first()
        if proc_output:
            self.log.info("Storing process output into db: {0}".format(str(proc_output)))
            proc_output.output = unicode(output)
            session.add(proc_output)

        proc.endTime = getTimestamp(True)

        if proc.status == "Killed" or proc.status == "Cancelled" or proc.status == "Crashed":
            self.db_adapter.commit()
            return True
        else:
            proc.status = 'Finished'
            session.add(proc)
            self.db_adapter.commit()

    def get_status_by_process_id(self, process_id: str):
        return self.get_field_by_process_id("status", process_id)

    def get_pid_by_process_id(self, process_id: str):
        return self.get_field_by_process_id("pid", process_id)

    def is_killed_process(self, process_id: str) -> bool:
        status = self.get_field_by_process_id("status", process_id)
        return True if status == "Killed" else False

    def is_cancelled_process(self, process_id: str) -> bool:
        status = self.get_field_by_process_id("status", process_id)
        return True if status == "Cancelled" else False

    def get_field_by_process_id(self, field_name: str, process_id: str):
        query = f"SELECT process.{field_name} FROM process AS process WHERE process.id=?"
        p = self.db_adapter.metadata.bind.execute(query, str(process_id)).fetchall()
        return p[0][0] if p else -1
