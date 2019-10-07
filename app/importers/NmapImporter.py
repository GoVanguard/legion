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
import sys

from PyQt5 import QtCore

from app.actions.updateProgress import AbstractUpdateProgressObservable
from db.entities.host import hostObj
from db.entities.l1script import l1ScriptObj
from db.entities.nmapSession import nmapSessionObj
from db.entities.note import note
from db.entities.os import osObj
from db.entities.port import portObj
from db.entities.service import serviceObj
from db.repositories.HostRepository import HostRepository
from parsers.Parser import Parser
from ui.ancillaryDialog import time


class NmapImporter(QtCore.QThread):
    tick = QtCore.pyqtSignal(int, name="changed")  # New style signal
    done = QtCore.pyqtSignal(name="done")  # New style signal
    schedule = QtCore.pyqtSignal(object, bool, name="schedule")  # New style signal
    log = QtCore.pyqtSignal(str, name="log")

    def __init__(self, updateProgressObservable: AbstractUpdateProgressObservable, hostRepository: HostRepository):
        QtCore.QThread.__init__(self, parent=None)
        self.output = ''
        self.updateProgressObservable = updateProgressObservable
        self.hostRepository = hostRepository

    def tsLog(self, msg):
        self.log.emit(str(msg))

    def setDB(self, db):
        self.db = db

    def setHostRepository(self, hostRepository: HostRepository):
        self.hostRepository = hostRepository

    def setFilename(self, filename):
        self.filename = filename

    def setOutput(self, output):
        self.output = output

    # it is necessary to get the qprocess because we need to send it back to the scheduler when we're done importing
    def run(self):
        try:
            self.updateProgressObservable.start()
            session = self.db.session()
            self.tsLog("Parsing nmap xml file: " + self.filename)
            startTime = time()

            try:
                parser = Parser(self.filename)
            except:
                self.tsLog('Giving up on import due to previous errors.')
                self.tsLog("Unexpected error: {0}".format(sys.exc_info()[0]))
                self.done.emit()
                return

            self.db.dbsemaphore.acquire()  # ensure that while this thread is running, no one else can write to the DB
            s = parser.getSession()  # nmap session info
            if s:
                n = nmapSessionObj(self.filename, s.startTime, s.finish_time, s.nmapVersion, s.scanArgs, s.totalHosts,
                                   s.upHosts, s.downHosts)
                session.add(n)

            allHosts = parser.getAllHosts()
            hostCount = len(allHosts)
            if hostCount == 0:  # to fix a division by zero if we ran nmap on one host
                hostCount = 1
            totalprogress = 0

            self.updateProgressObservable.updateProgress(totalprogress)

            createProgress = 0
            createOsNodesProgress = 0
            createPortsProgress = 0

            for h in allHosts:  # create all the hosts that need to be created
                db_host = self.hostRepository.getHostInformation(h.ip)

                if not db_host:  # if host doesn't exist in DB, create it first
                    hid = hostObj(osMatch='', osAccuracy='', ip=h.ip, ipv4=h.ipv4, ipv6=h.ipv6, macaddr=h.macaddr,
                                  status=h.status, hostname=h.hostname, vendor=h.vendor, uptime=h.uptime,
                                  lastboot=h.lastboot, distance=h.distance, state=h.state, count=h.count)
                    self.tsLog("Adding db_host")
                    session.add(hid)
                    t_note = note(h.ip, 'Added by nmap')
                    session.add(t_note)
                else:
                    self.tsLog("Found db_host already in db")

                createProgress = createProgress + ((100.0 / hostCount) / 5)
                totalprogress = totalprogress + createProgress
                self.updateProgressObservable.updateProgress(int(totalprogress))

            session.commit()

            for h in allHosts:  # create all OS, service and port objects that need to be created
                self.tsLog("Processing h {ip}".format(ip=h.ip))

                db_host = self.hostRepository.getHostInformation(h.ip)
                if db_host:
                    self.tsLog("Found db_host during os/ports/service processing")
                else:
                    self.log("Did not find db_host during os/ports/service processing")

                os_nodes = h.getOs()  # parse and store all the OS nodes
                self.tsLog("    'os_nodes' to process: {os_nodes}".format(os_nodes=str(len(os_nodes))))
                for os in os_nodes:
                    self.tsLog("    Processing os obj {os}".format(os=str(os.name)))
                    db_os = session.query(osObj).filter_by(hostId=db_host.id).filter_by(name=os.name).filter_by(
                        family=os.family).filter_by(generation=os.generation).filter_by(osType=os.osType).filter_by(
                        vendor=os.vendor).first()

                    if not db_os:
                        t_osObj = osObj(os.name, os.family, os.generation, os.osType, os.vendor, os.accuracy,
                                        db_host.id)
                        session.add(t_osObj)

                    createOsNodesProgress = createOsNodesProgress + ((100.0 / hostCount) / 5)
                    totalprogress = totalprogress + createOsNodesProgress
                    self.updateProgressObservable.updateProgress(int(totalprogress))

                session.commit()

                all_ports = h.all_ports()
                self.tsLog("    'ports' to process: {all_ports}".format(all_ports=str(len(all_ports))))
                for p in all_ports:  # parse the ports
                    self.tsLog("        Processing port obj {port}".format(port=str(p.portId)))
                    s = p.getService()

                    if not (s is None):  # check if service already exists to avoid adding duplicates
                        # print("            Found service {service} for port {port}".format(service=str(s.name),port=str(p.portId)))
                        # db_service = session.query(serviceObj).filter_by(name=s.name).filter_by(product=s.product).filter_by(version=s.version).filter_by(extrainfo=s.extrainfo).filter_by(fingerprint=s.fingerprint).first()
                        db_service = session.query(serviceObj).filter_by(name=s.name).first()
                        if not db_service:
                            # print("Did not find service *********** name={0} prod={1} ver={2} extra={3} fing={4}".format(s.name, s.product, s.version, s.extrainfo, s.fingerprint))
                            db_service = serviceObj(s.name, s.product, s.version, s.extrainfo, s.fingerprint)
                            session.add(db_service)
                    # else:
                    # print("FOUND service *************** name={0}".format(db_service.name))

                    else:  # else, there is no service info to parse
                        db_service = None
                        # fetch the port
                    db_port = session.query(portObj).filter_by(hostId=db_host.id).filter_by(portId=p.portId).filter_by(
                        protocol=p.protocol).first()

                    if not db_port:
                        # print("Did not find port *********** portid={0} proto={1}".format(p.portId, p.protocol))
                        if db_service:
                            db_port = portObj(p.portId, p.protocol, p.state, db_host.id, db_service.id)
                        else:
                            db_port = portObj(p.portId, p.protocol, p.state, db_host.id, '')
                        session.add(db_port)
                    # else:
                    # print('FOUND port *************** portid={0}'.format(db_port.portId))
                    createPortsProgress = createPortsProgress + ((100.0 / hostCount) / 5)
                    totalprogress = totalprogress + createPortsProgress
                    self.updateProgressObservable.updateProgress(totalprogress)

            session.commit()

            # totalprogress += progress
            # self.tick.emit(int(totalprogress))

            for h in allHosts:  # create all script objects that need to be created
                db_host = self.hostRepository.getHostInformation(h.ip)

                for p in h.all_ports():
                    for scr in p.getScripts():
                        self.tsLog("        Processing script obj {scr}".format(scr=str(scr)))
                        print("        Processing script obj {scr}".format(scr=str(scr)))
                        db_port = session.query(portObj).filter_by(hostId=db_host.id).filter_by(
                            portId=p.portId).filter_by(protocol=p.protocol).first()
                        db_script = session.query(l1ScriptObj).filter_by(scriptId=scr.scriptId).filter_by(
                            portId=db_port.id).first()

                        if not db_script:  # if this script object doesn't exist, create it
                            t_l1ScriptObj = l1ScriptObj(scr.scriptId, scr.output, db_port.id, db_host.id)
                            self.tsLog("        Adding l1ScriptObj obj {script}".format(script=scr.scriptId))
                            session.add(t_l1ScriptObj)

                for hs in h.getHostScripts():
                    db_script = session.query(l1ScriptObj).filter_by(scriptId=hs.scriptId).filter_by(
                        hostId=db_host.id).first()
                    if not db_script:
                        t_l1ScriptObj = l1ScriptObj(hs.scriptId, hs.output, None, db_host.id)
                        session.add(t_l1ScriptObj)

            session.commit()

            for h in allHosts:  # update everything

                db_host = self.hostRepository.getHostInformation(h.ip)

                if db_host.ipv4 == '' and not h.ipv4 == '':
                    db_host.ipv4 = h.ipv4
                if db_host.ipv6 == '' and not h.ipv6 == '':
                    db_host.ipv6 = h.ipv6
                if db_host.macaddr == '' and not h.macaddr == '':
                    db_host.macaddr = h.macaddr
                if not h.status == '':
                    db_host.status = h.status
                if db_host.hostname == '' and not h.hostname == '':
                    db_host.hostname = h.hostname
                if db_host.vendor == '' and not h.vendor == '':
                    db_host.vendor = h.vendor
                if db_host.uptime == '' and not h.uptime == '':
                    db_host.uptime = h.uptime
                if db_host.lastboot == '' and not h.lastboot == '':
                    db_host.lastboot = h.lastboot
                if db_host.distance == '' and not h.distance == '':
                    db_host.distance = h.distance
                if db_host.state == '' and not h.state == '':
                    db_host.state = h.state
                if db_host.count == '' and not h.count == '':
                    db_host.count = h.count

                session.add(db_host)

                tmp_name = ''
                tmp_accuracy = '0'  # TODO: check if better to convert to int for comparison

                os_nodes = h.getOs()
                for os in os_nodes:
                    db_os = session.query(osObj).filter_by(hostId=db_host.id).filter_by(name=os.name).filter_by(
                        family=os.family).filter_by(generation=os.generation).filter_by(osType=os.osType).filter_by(
                        vendor=os.vendor).first()

                    db_os.osAccuracy = os.accuracy  # update the accuracy

                    if not os.name == '':  # get the most accurate OS match/accuracy to store it in the host table for easier access
                        if os.accuracy > tmp_accuracy:
                            tmp_name = os.name
                            tmp_accuracy = os.accuracy

                if os_nodes:  # if there was operating system info to parse

                    if not tmp_name == '' and not tmp_accuracy == '0':  # update the current host with the most accurate OS match
                        db_host.osMatch = tmp_name
                        db_host.osAccuracy = tmp_accuracy

                session.add(db_host)

                for scr in h.getHostScripts():
                    print("-----------------------Host SCR: {0}".format(scr.scriptId))
                    db_host = self.hostRepository.getHostInformation(h.ip)
                    scrProcessorResults = scr.scriptSelector(db_host)
                    for scrProcessorResult in scrProcessorResults:
                        session.add(scrProcessorResult)

                for scr in h.getScripts():
                    print("-----------------------SCR: {0}".format(scr.scriptId))
                    db_host = self.hostRepository.getHostInformation(h.ip)
                    scrProcessorResults = scr.scriptSelector(db_host)
                    for scrProcessorResult in scrProcessorResults:
                        session.add(scrProcessorResult)

                for p in h.all_ports():
                    s = p.getService()
                    if not (s is None):
                        # db_service = session.query(serviceObj).filter_by(name=s.name).filter_by(product=s.product).filter_by(version=s.version).filter_by(extrainfo=s.extrainfo).filter_by(fingerprint=s.fingerprint).first()
                        db_service = session.query(serviceObj).filter_by(name=s.name).first()
                    else:
                        db_service = None
                        # fetch the port
                    db_port = session.query(portObj).filter_by(hostId=db_host.id).filter_by(portId=p.portId).filter_by(
                        protocol=p.protocol).first()
                    if db_port:
                        # print("************************ Found {0}".format(db_port))

                        if db_port.state != p.state:
                            db_port.state = p.state
                            session.add(db_port)

                        if not (
                                db_service is None) and db_port.serviceId != db_service.id:  # if there is some new service information, update it
                            db_port.serviceId = db_service.id
                            session.add(db_port)

                    for scr in p.getScripts():  # store the script results (note that existing script outputs are also kept)
                        db_script = session.query(l1ScriptObj).filter_by(scriptId=scr.scriptId).filter_by(
                            portId=db_port.id).first()

                        if not scr.output == '' and scr.output is not None:
                            db_script.output = scr.output

                        session.add(db_script)

            self.updateProgressObservable.updateProgress(100)

            session.commit()
            self.db.dbsemaphore.release()  # we are done with the DB
            self.tsLog(f"Finished in {str(time() - startTime)} seconds.")
            self.done.emit()
            self.updateProgressObservable.finished()

            # call the scheduler (if there is no terminal output it means we imported nmap)
            self.schedule.emit(parser, self.output == '')

        except Exception as e:
            self.tsLog('Something went wrong when parsing the nmap file..')
            self.tsLog("Unexpected error: {0}".format(sys.exc_info()[0]))
            self.tsLog(e)
            raise
            self.done.emit()
