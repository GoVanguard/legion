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
    tabTitle = Column(String)
    hostIp = Column(String)
    port = Column(String)
    protocol = Column(String)
    command = Column(String)
    startTime = Column(String)
    endTime = Column(String)
    estimatedRemaining = Column(Integer)
    elapsed = Column(Integer)
    outputfile = Column(String)
    output = relationship("process_output")
    status = Column(String)
    closed = Column(String)

    def __init__(self, pid, *args):
        self.display = 'True'
        self.pid = pid
        self.name = args[0]
        self.tabTitle = args[1]
        self.hostIp = args[2]
        self.port = args[3]
        self.protocol = args[4]
        self.command = args[5]
        self.startTime = args[6]
        self.endTime = args[7]
        self.outputfile = args[8]
        self.output = args[10]
        self.status = args[9]
        self.closed = 'False'
        self.estimatedRemaining = args[11]
        self.elapsed = args[12]

# This class holds various info about an nmap scan
class nmapSessionObj(Base):
    __tablename__ = 'nmapSessionObj'
    filename = Column(String, primary_key = True)
    startTime = Column(String)
    finish_time = Column(String)
    nmapVersion = Column(String)
    scanArgs = Column(String)
    totalHosts = Column(String)
    upHosts = Column(String)
    downHosts = Column(String)

    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self.startTime = args[0]
        self.finish_time = args[1]
        self.nmapVersion = kwargs.get('nmapVersion') or 'unknown'
        self.scanArgs = kwargs.get('scanArgs') or ''
        self.totalHosts = kwargs.get('total_host') or '0'
        self.upHosts = kwargs.get('upHosts') or '0'
        self.downHosts = kwargs.get('downHosts') or '0'


class osObj(Base):
    __tablename__ = 'osObj'
    id = Column(Integer, primary_key = True)
    name = Column(String)
    family = Column(String)
    generation = Column(String)
    osType = Column(String)
    vendor = Column(String)
    accuracy = Column(String)
    hostId = Column(String, ForeignKey('hostObj.id'))

    def __init__(self, name, *args):
        self.name = name
        self.family = args[0]
        self.generation = args[1]
        self.osType = args[2]
        self.vendor = args[3]
        self.accuracy = args[4]
        self.hostId = args[5]

class portObj(Base):
    __tablename__ = 'portObj'
    portId = Column(String)
    id = Column(Integer, primary_key = True)
    protocol = Column(String)
    state = Column(String)
    hostId = Column(String, ForeignKey('hostObj.id'))
    serviceId = Column(String, ForeignKey('serviceObj.id'))
    scriptId = Column(String, ForeignKey('l1ScriptObj.id'))

    def __init__(self, portId, protocol, state, host, service = ''):
        self.portId = portId
        self.protocol = protocol
        self.state = state
        self.serviceId = service
        self.hostId = host

class cve(Base):
    __tablename__ = 'cve'
    name = Column(String)
    id = Column(Integer, primary_key = True)
    url = Column(String)
    product = Column(String)
    severity = Column(String)
    source = Column(String)
    version = Column(String)
    exploitId = Column(Integer)
    exploit = Column(String)
    exploitUrl = Column(String)
    serviceId = Column(String, ForeignKey('serviceObj.id'))
    hostId = Column(String, ForeignKey('hostObj.id'))

    def __init__(self, name, url, product, hostId, severity = '', source = '', version = '', exploitId = 0, exploit = '', exploitUrl = ''):
        self.url = url
        self.name = name
        self.product = product
        self.severity = severity
        self.source = source
        self.version = version
        self.exploitId = exploitId
        self.exploit = exploit
        self.exploitUrl = exploitUrl
        self.hostId = hostId

class appObj(Base):
    __tablename__ = 'appObj'
    name = Column(String)
    id = Column(Integer, primary_key = True)
    product = Column(String)
    version = Column(String)
    extrainfo = Column(String)
    fingerprint = Column(String)
    cpe = Column(String)
    serviceId = Column(String, ForeignKey('serviceObj.id'))

    def __init__(self, name = '', product = '', version = '', extrainfo = '', fingerprint = '', cpe = ''):
        self.name = name
        self.product = product
        self.version = version
        self.extrainfo = extrainfo
        self.fingerprint = fingerprint
        self.cpe = cpe

class serviceObj(Base):
    __tablename__ = 'serviceObj'
    name = Column(String)
    id = Column(Integer, primary_key = True)
    product = Column(String)
    version = Column(String)
    extrainfo = Column(String)
    fingerprint = Column(String)
    port = relationship(portObj)
    cves = relationship(cve)
    application = relationship(appObj)

    def __init__(self, name = '', product = '', version = '', extrainfo = '', fingerprint = ''):
        self.name = name
        self.product = product
        self.version = version
        self.extrainfo = extrainfo
        self.fingerprint = fingerprint

class l1ScriptObj(Base):
    __tablename__ = 'l1ScriptObj'
    scriptId = Column(String)
    id = Column(Integer, primary_key = True)
    output = Column(String)
    portId = Column(String, ForeignKey('portObj.id'))
    hostId = Column(String, ForeignKey('hostObj.id'))

    def __init__(self, scriptId, output, portId, hostId):
        self.scriptId = scriptId
        self.output = unicode(output)
        self.portId = portId
        self.hostId = hostId

class l2ScriptObj(Base):
    __tablename__ = 'l2ScriptObj'
    scriptId = Column(String)
    id = Column(Integer, primary_key = True)
    output = Column(String)
    portId = Column(String, ForeignKey('portObj.id'))
    hostId = Column(String, ForeignKey('hostObj.id'))

    def __init__(self, scriptId, output, portId, hostId):
        self.scriptId = scriptId
        self.output = unicode(output)
        self.portId = portId
        self.hostId = hostId


class hostObj(Base):
    __tablename__ = 'hostObj'
    # State
    state = Column(String)
    count = Column(String)
    checked = Column(String)

    # OS
    osMatch = Column(String)
    osAccuracy = Column(String)
    vendor = Column(String)
    uptime = Column(String)
    lastboot = Column(String)

    # Network
    isp = Column(String)
    asn = Column(String)
    ip = Column(String)
    ipv4 = Column(String)
    ipv6 = Column(String)
    macaddr = Column(String)
    status = Column(String)
    hostname = Column(String)

    # ID
    hostId = Column(String)
    id = Column(Integer, primary_key = True)
    count = Column(String)

    # Location
    city = Column(String)
    countryCode = Column(String)
    postalCode = Column(String)
    longitude = Column(String)
    latitude = Column(String)
    distance = Column(String)

    # Network
    isp = Column(String)
    asn = Column(String)

    # host relationships
    os = relationship(osObj)
    ports = relationship(portObj)
    cves = relationship(cve)

    def __init__(self, **kwargs):
        self.checked = kwargs.get('checked') or 'False'
        self.osMatch = kwargs.get('osMatch') or 'unknown'
        self.osAccuracy = kwargs.get('osAccuracy') or 'NaN'
        self.ip = kwargs.get('ip') or 'unknown'
        self.ipv4 = kwargs.get('ipv4') or 'unknown'
        self.ipv6 = kwargs.get('ipv6') or 'unknown'
        self.macaddr = kwargs.get('macaddr') or 'unknown'
        self.status = kwargs.get('status') or 'unknown'
        self.hostname = kwargs.get('hostname') or 'unknown'
        self.hostId = kwargs.get('hostname') or 'unknown'
        self.vendor = kwargs.get('vendor') or 'unknown'
        self.uptime = kwargs.get('uptime') or 'unknown'
        self.lastboot = kwargs.get('lastboot') or 'unknown'
        self.distance = kwargs.get('distance') or 'unknown'
        self.state = kwargs.get('state') or 'unknown'
        self.count = kwargs.get('count') or 'unknown'
        self.city = kwargs.get('city') or 'unknown'
        self.countryCode = kwargs.get('countryCode') or 'unknown'
        self.postalCode = kwargs.get('postalCode') or 'unknown'
        self.longitude = kwargs.get('longitude') or 'unknown'
        self.latitude = kwargs.get('latitude') or 'unknown'
        self.isp = kwargs.get('isp') or 'unknown'
        self.asn = kwargs.get('asn') or 'unknown'



class note(Base):
    __tablename__ = 'note'
    hostId = Column(Integer, ForeignKey('hostObj.id'))
    id = Column(Integer, primary_key = True)
    text = Column(String)

    def __init__(self, hostId, text):
        self.text = unicode(text)
        self.hostId = hostId

class process_output(Base):
    __tablename__ = 'process_output'
    processId = Column(Integer, ForeignKey('process.id'))
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
        log.info("DB lock acquired")
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
