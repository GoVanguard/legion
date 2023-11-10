"""
LEGION (https://govanguard.io)
Copyright (c) 2019 GoVanguard

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

from PyQt6.QtCore import QSemaphore
import time
from random import randint

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from app.logging.legionLog import getDbLogger


class Database:
    def __init__(self, dbfilename):
        from db.database import Base
        self.log = getDbLogger()
        self.base = Base
        try:
            self.establishSqliteConnection(dbfilename)
        except Exception as e:
            self.log.error('Could not create SQLite database. Please try again.')
            self.log.info(e)

    def openDB(self, dbfilename):
        try:
            self.establishSqliteConnection(dbfilename)
        except:
            self.log.error('Could not open SQLite database file. Is the file corrupted?')

    def establishSqliteConnection(self, dbFileName: str):
        self.name = dbFileName
        self.dbsemaphore = QSemaphore(1)  # to control concurrent write access to db
        self.engine = create_engine(
            'sqlite:///{dbFileName}'.format(dbFileName=dbFileName))
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.session.configure(bind=self.engine, autoflush=False)
        self.metadata = self.base.metadata
        self.metadata.create_all(self.engine)
        self.metadata.echo = True
        self.metadata.bind = self.engine
        self.log.info(f"Established SQLite connection on file '{dbFileName}'")

    def commit(self):
        self.dbsemaphore.acquire()
        self.log.debug("DB lock acquired")
        try:
            session = self.session()
            rnd = float(randint(1, 99)) / 1000.00
            self.log.debug("Waiting {0}s before commit...".format(str(rnd)))
            time.sleep(rnd)
            session.commit()
        except Exception as e:
            self.log.error("DB Commit issue")
            self.log.error(str(e))
            try:
                rnd = float(randint(1, 99)) / 100.00
                time.sleep(rnd)
                self.log.debug("Waiting {0}s before commit...".format(str(rnd)))
                session.commit()
            except Exception as e:
                self.log.error("DB Commit issue on retry")
                self.log.error(str(e))
                pass
        self.dbsemaphore.release()
        self.log.debug("DB lock released")
