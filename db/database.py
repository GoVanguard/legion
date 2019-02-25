#!/usr/bin/env python

'''
LEGION (https://govanguard.io)
Copyright (c) 2018 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from utilities.stenoLogging import *
log = get_logger('legion', path="./log/legion-db.log", console=False)
log.setLevel(logging.INFO)

from PyQt5.QtCore import QSemaphore
import time
from random import randint

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, create_engine, Table
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import SingletonThreadPool

from six import u as unicode
 
Base = declarative_base()

class process(Base):
    __tablename__ = 'process'
    pid = Column(String)
    id = Column(Integer, primary_key = True)
    display = Column(String)
    name = Column(String)
    tabtitle = Column(String)
    hostip = Column(String)
    port = Column(String)
    protocol = Column(String)
    command = Column(String)
    starttime = Column(String)
    endtime = Column(String)
    estimatedremaining = Column(Integer)
    elapsed = Column(Integer)
    outputfile = Column(String)
    output = relationship("process_output") #, uselist = False, backref = "process")
    status = Column(String)
    closed = Column(String)

    def __init__(self, pid, *args):
        self.display = 'True'
        self.pid = pid
        self.name = args[0]
        self.tabtitle = args[1]
        self.hostip = args[2]
        self.port = args[3]
        self.protocol = args[4]
        self.command = args[5]
        self.starttime = args[6]
        self.endtime = args[7]
        self.outputfile = args[8]
        self.output = args[10]
        self.status = args[9]
        self.closed = 'False'
        self.estimatedremaining = args[11]
        self.elapsed = args[12]

# This class holds various info about an nmap scan
class nmap_session(Base):
    __tablename__ = 'nmap_session'
    filename = Column(String, primary_key = True)
    start_time = Column(String)
    finish_time = Column(String)
    nmap_version = Column(String)
    scan_args = Column(String)
    total_hosts = Column(String)
    up_hosts = Column(String)
    down_hosts = Column(String)

    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self.start_time = args[0]
        self.finish_time = args[1]
        self.nmap_version = kwargs.get('nmap_version') or 'unknown'
        self.scan_args = kwargs.get('scan_args') or ''
        self.total_hosts = kwargs.get('total_host') or '0'
        self.up_hosts = kwargs.get('up_hosts') or '0'
        self.down_hosts = kwargs.get('down_hosts') or '0'


class nmap_os(Base):
    __tablename__ = 'nmap_os'
    id = Column(Integer, primary_key = True)
    name = Column(String)
    family = Column(String)
    generation = Column(String)
    os_type = Column(String)
    vendor = Column(String)
    accuracy = Column(String)
    host_id = Column(String, ForeignKey('nmap_host.id'))

    def __init__(self, name, *args):
        self.name = name
        self.family = args[0]
        self.generation = args[1]
        self.os_type = args[2]
        self.vendor = args[3]
        self.accuracy = args[4]
        self.host_id = args[5]

class nmap_port(Base):
    __tablename__ = 'nmap_port'
    port_id = Column(String)
    id = Column(Integer, primary_key = True)
    protocol = Column(String)
    state = Column(String)
    host_id = Column(String, ForeignKey('nmap_host.id'))
    service_id = Column(String, ForeignKey('nmap_service.id'))
    script_id = Column(String, ForeignKey('nmap_script.id'))

    def __init__(self, port_id, protocol, state, host, service = ''):
        self.port_id = port_id
        self.protocol = protocol
        self.state = state
        self.service_id = service
        self.host_id = host

class cve(Base):
    __tablename__ = 'cve'
    name = Column(String)
    id = Column(Integer, primary_key = True)
    url = Column(String)
    name = Column(String)
    criteria = Column(String)
    fingerprint = Column(String)
    service_id = Column(String, ForeignKey('nmap_service.id'))
    host_id = Column(String, ForeignKey('nmap_host.id'))

    def __init__(self, url = '', name = '', criteria = '', fingerprint = ''):
        self.url = url
        self.name = name
        self.criteria = criteria
        self.fingerprint = fingerprint

class nmap_service(Base):
    __tablename__ = 'nmap_service'
    name = Column(String)
    id = Column(Integer, primary_key = True)
    product = Column(String)
    version = Column(String)
    extrainfo = Column(String)
    fingerprint = Column(String)
    port = relationship(nmap_port)
    cves = relationship(cve)

    def __init__(self, name = '', product = '', version = '', extrainfo = '', fingerprint = ''):
        self.name = name
        self.product = product
        self.version = version
        self.extrainfo = extrainfo
        self.fingerprint = fingerprint

class nmap_script(Base):
    __tablename__ = 'nmap_script'
    script_id = Column(String)
    id = Column(Integer, primary_key = True)
    output = Column(String)
    port_id = Column(String, ForeignKey('nmap_port.id'))
    host_id = Column(String, ForeignKey('nmap_host.id'))

    def __init__(self, script_id, output, portId, hostId):
        self.script_id = script_id
        self.output = unicode(output)
        self.port_id = portId
        self.host_id = hostId

class nmap_host(Base):
    __tablename__ = 'nmap_host'
    checked = Column(String)
    os_match = Column(String)
    os_accuracy = Column(String)
    ip = Column(String)
    ipv4 = Column(String)
    ipv6 = Column(String)
    macaddr = Column(String)
    status = Column(String)
    hostname = Column(String)
    host_id = Column(String)
    id = Column(Integer, primary_key = True)
    vendor = Column(String)
    uptime = Column(String)
    lastboot = Column(String)
    distance = Column(String)
    state = Column(String)
    count = Column(String)

    # host relationships
    os = relationship(nmap_os)
    ports = relationship(nmap_port)
    cves = relationship(cve)

    def __init__(self, **kwargs):
        self.checked = kwargs.get('checked') or 'False'
        self.os_match = kwargs.get('os_match') or 'unknown'
        self.os_accuracy = kwargs.get('os_accuracy') or 'NaN'
        self.ip = kwargs.get('ip') or 'unknown'
        self.ipv4 = kwargs.get('ipv4') or 'unknown'
        self.ipv6 = kwargs.get('ipv6') or 'unknown'
        self.macaddr = kwargs.get('macaddr') or 'unknown'
        self.status = kwargs.get('status') or 'unknown'
        self.hostname = kwargs.get('hostname') or 'unknown'
        self.host_id = kwargs.get('hostname') or 'unknown'
        self.vendor = kwargs.get('vendor') or 'unknown'
        self.uptime = kwargs.get('uptime') or 'unknown'
        self.lastboot = kwargs.get('lastboot') or 'unknown'
        self.distance = kwargs.get('distance') or 'unknown'
        self.state = kwargs.get('state') or 'unknown'
        self.count = kwargs.get('count') or 'unknown'


class note(Base):
    __tablename__ = 'note'
    host_id = Column(Integer, ForeignKey('nmap_host.id'))
    id = Column(Integer, primary_key = True)
    text = Column(String)

    def __init__(self, hostId, text):
        self.text = unicode(text)
        self.host_id = hostId

class process_output(Base):
    __tablename__ = 'process_output'
    process_id = Column(Integer, ForeignKey('process.id'))
    id = Column(Integer, primary_key = True)
    output = Column(String)

    def __init__(self):
        self.output = unicode('')


class Database:
    def __init__(self, dbfilename):
        try:
            self.name = dbfilename
            self.dbsemaphore = QSemaphore(1)                            # to control concurrent write access to db
            self.engine = create_engine('sqlite:///{dbFileName}'.format(dbFileName = dbfilename)) #, poolclass=SingletonThreadPool)
            self.session = scoped_session(sessionmaker())
            self.session.configure(bind = self.engine, autoflush=False)
            self.metadata = Base.metadata
            self.metadata.create_all(self.engine)
            self.metadata.echo = True
            self.metadata.bind = self.engine
        except Exception as e:
            log.info('Could not create database. Please try again.')
            log.info(e)

    def openDB(self, dbfilename):
        try:
            self.name = dbfilename
            self.dbsemaphore = QSemaphore(1)                            # to control concurrent write access to db
            self.engine = create_engine('sqlite:///{dbFileName}'.format(dbFileName = dbfilename)) #, poolclass=SingletonThreadPool)
            self.session = scoped_session(sessionmaker())
            self.session.configure(bind = self.engine, autoflush=False)
            self.metadata = Base.metadata
            self.metadata.create_all(self.engine)
            self.metadata.echo = True
            self.metadata.bind = self.engine
        except:
            log.info('Could not open database file. Is the file corrupted?')

    def commit(self):
        self.dbsemaphore.acquire()
        log.info("DB lock aquired")
        try:
            session = self.session()
            rnd = float(randint(1,99)) / 100.00
            log.info("Waiting {0}s before commit...".format(str(rnd)))
            time.sleep(rnd)
            session.commit()
        except Exception as e:
            log.error("DB Commit issue")
            log.error(str(e))
            try:
                rnd = float(randint(1,99)) / 100.00
                time.sleep(rnd)
                log.info("Waiting {0}s before commit...".format(str(rnd)))
                session.commit()
            except Exception as e:
                log.error("DB Commit issue on retry")
                log.error(str(e))
                pass
        self.dbsemaphore.release()
        log.info("DB lock released")


if __name__ == "__main__":

    db = Database('myDatabase')
