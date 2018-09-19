#!/usr/bin/env python

'''
SPARTA - Network Infrastructure Penetration Testing Tool (http://sparta.secforce.com)
Copyright (c) 2015 SECFORCE (Antonio Quina and Leonidas Stavliotis)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from six import u as unicode

Base = declarative_base()

class process(Base):
    __tablename__ = 'process'
    pid = Column(String, primary_key=True)
    display=Column(String)
    name=Column(String)
    tabtitle=Column(String)
    hostip=Column(String)
    port=Column(String)
    protocol=Column(String)
    command=Column(String)
    starttime=Column(String)
    endtime=Column(String)
    outputfile=Column(String)
    output=relationship("process_output", uselist=False, backref="process")
    status=Column(String)
    closed=Column(String)

    def __init__(self, pid, name, tabtitle, hostip, port, protocol, command, starttime, endtime, outputfile, status, processOutputId):
        self.display='True'
        self.pid=pid
        self.name=name
        self.tabtitle=tabtitle
        self.hostip=hostip
        self.port=port
        self.protocol=protocol
        self.command=command
        self.starttime=starttime
        self.endtime=endtime
        self.outputfile=outputfile
        self.output=processOutputId
        self.status=status
        self.closed='False'

class process_output(Base):
    __tablename__ = 'process_output'
    output=Column(String, primary_key=True)
    process=Column(Integer, ForeignKey('process.pid'))

    def __init__(self):
        self.output=unicode('')

# This class holds various info about an nmap scan
class nmap_session(Base):
    __tablename__ = 'nmap_session'
    filename=Column(String, primary_key=True)
    start_time=Column(String)
    finish_time=Column(String)
    nmap_version=Column(String)
    scan_args=Column(String)
    total_hosts=Column(String)
    up_hosts=Column(String)
    down_hosts=Column(String)

    def __init__(self, filename, start_time, finish_time, nmap_version='', scan_args='', total_hosts='0', up_hosts='0', down_hosts='0'):
        self.filename=filename
        self.start_time=start_time
        self.finish_time=finish_time
        self.nmap_version=nmap_version
        self.scan_args=scan_args
        self.total_hosts=total_hosts
        self.up_hosts=up_hosts
        self.down_hosts=down_hosts


class nmap_os(Base):
    __tablename__ = 'nmap_os'
    name=Column(String, primary_key=True)
    family=Column(String)
    generation=Column(String)
    os_type=Column(String)
    vendor=Column(String)
    accuracy=Column(String)
    host=Column(String, ForeignKey('nmap_host.hostname'))
    
    def __init__(self, name, family, generation, os_type, vendor, accuracy, hostId):
        self.name=name
        self.family=family
        self.generation=generation
        self.os_type=os_type
        self.vendor=vendor
        self.accuracy=accuracy
        self.host=hostId
    
class nmap_port(Base):
    __tablename__ = 'nmap_port'
    port_id=Column(String, primary_key=True)
    protocol=Column(String)
    state=Column(String)
    host=Column(String, ForeignKey('nmap_host.hostname'))
    service=Column(String, ForeignKey('nmap_service.name'))
    script=Column(String, ForeignKey('nmap_script.script_id'))
    
    def __init__(self, port_id, protocol, state, host, service=''):
        self.port_id=port_id
        self.protocol=protocol
        self.state=state
        self.host=host
        self.service=service

class nmap_service(Base):
    __tablename__ = 'nmap_service'
    name=Column(String, primary_key=True)
    product=Column(String)
    version=Column(String)
    extrainfo=Column(String)
    fingerprint=Column(String)
    port=Column(String, ForeignKey('nmap_port.port_id'))
    
    def __init__(self, name='', product='', version='', extrainfo='', fingerprint=''):
        self.name=name
        self.product=product
        self.version=version
        self.extrainfo=extrainfo
        self.fingerprint=fingerprint

class nmap_script(Base):
    __tablename__ = 'nmap_script'
    script_id=Column(String, primary_key=True)
    output=Column(String)
    port=Column(String, ForeignKey('nmap_port.port_id'))
    host=Column(String, ForeignKey('nmap_host.hostname'))
    
    def __init__(self, script_id, output, portId, hostId):
        self.script_id=script_id
        self.output=unicode(output)
        self.port=portId
        self.host=hostId

class nmap_host(Base):
    __tablename__ = 'nmap_host'
    checked=Column(String)
    os_match=Column(String)
    os_accuracy=Column(String)
    ip=Column(String)
    ipv4=Column(String)
    ipv6=Column(String)
    macaddr=Column(String)
    status=Column(String)
    hostname=Column(String, primary_key=True)
    vendor=Column(String)
    uptime=Column(String)
    lastboot=Column(String)
    distance=Column(String)
    state=Column(String)
    count=Column(String)    
    
    # host relationships
    os=Column(String, ForeignKey('nmap_os.name'))
    ports=Column(String, ForeignKey('nmap_port.port_id'))

    def __init__(self, os_match='', os_accuracy='', ip='', ipv4='', ipv6='', macaddr='', status='', hostname='', vendor='', uptime='', lastboot='', distance='', state='', count=''):
        self.checked='False'
        self.os_match=os_match
        self.os_accuracy=os_accuracy
        self.ip=ip
        self.ipv4=ipv4
        self.ipv6=ipv6
        self.macaddr=macaddr
        self.status=status
        self.hostname=hostname
        self.vendor=vendor
        self.uptime=uptime
        self.lastboot=lastboot
        self.distance=distance
        self.state=state
        self.count=count        


class note(Base):
    __tablename__ = 'note'
    host=Column(String, ForeignKey('nmap_host.hostname'))
    text=Column(String, primary_key=True)
    
    def __init__(self, hostId, text):
        self.text=unicode(text)
        self.host=hostId
