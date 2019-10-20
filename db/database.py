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
from utilities.stenoLogging import *

log = get_logger('legion', path="./log/legion-db.log", console=False)
log.setLevel(logging.INFO)

from PyQt5.QtCore import QSemaphore
import time
from random import randint

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Database:
    def __init__(self, dbfilename):
        try:
            self.establishSqliteConnection(dbfilename)
        except Exception as e:
            log.info('Could not create database. Please try again.')
            log.info(e)

    def openDB(self, dbfilename):
        try:
            self.establishSqliteConnection(dbfilename)
        except:
            log.info('Could not open database file. Is the file corrupted?')

    def establishSqliteConnection(self, dbFileName: str):
        self.name = dbFileName
        self.dbsemaphore = QSemaphore(1)  # to control concurrent write access to db
        self.engine = create_engine(
            'sqlite:///{dbFileName}'.format(dbFileName=dbFileName))
        self.session = scoped_session(sessionmaker())
        self.session.configure(bind=self.engine, autoflush=False)
        self.metadata = Base.metadata
        self.metadata.create_all(self.engine)
        self.metadata.echo = True
        self.metadata.bind = self.engine

    def commit(self):
        self.dbsemaphore.acquire()
        log.debug("DB lock acquired")
        try:
            session = self.session()
            rnd = float(randint(1, 99)) / 100.00
            log.debug("Waiting {0}s before commit...".format(str(rnd)))
            time.sleep(rnd)
            session.commit()
        except Exception as e:
            log.error("DB Commit issue")
            log.error(str(e))
            try:
                rnd = float(randint(1, 99)) / 100.00
                time.sleep(rnd)
                log.debug("Waiting {0}s before commit...".format(str(rnd)))
                session.commit()
            except Exception as e:
                log.error("DB Commit issue on retry")
                log.error(str(e))
                pass
        self.dbsemaphore.release()
        log.debug("DB lock released")
