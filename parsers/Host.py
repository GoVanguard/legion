#!/usr/bin/python

__author__ =  'yunshu(wustyunshu@hotmail.com)'
__version__=  '0.2'
__modified_by = 'ketchup'

import parsers.Service as Service
import parsers.Script as Script
import parsers.OS as OS
import parsers.Port as Port

class Host:
    ipv4 = ''
    ipv6 = ''
    macaddr = ''
    status = 'none'
    hostname = ''
    vendor = ''
    uptime = ''
    lastboot = ''
    distance = 0
    state = ''
    count = ''

    def __init__( self, HostNode ):
        self.hostNode = HostNode
        self.status = HostNode.getElementsByTagName('status')[0].getAttribute('state')
        for e in HostNode.getElementsByTagName('address'):
            if e.getAttribute('addrtype') == 'ipv4':
                self.ipv4 = e.getAttribute('addr')
            elif e.getAttribute('addrtype') == 'ipv6':
                self.ipv6 = e.getAttribute('addr')
            elif e.getAttribute('addrtype') == 'mac':
                self.macaddr = e.getAttribute('addr')
                self.vendor = e.getAttribute('vendor')
        #self.ip = HostNode.getElementsByTagName('address')[0].getAttribute('addr');
        self.ip = self.ipv4 # for compatibility with the original library
        if len(HostNode.getElementsByTagName('hostname')) > 0:
            self.hostname = HostNode.getElementsByTagName('hostname')[0].getAttribute('name')
        if len(HostNode.getElementsByTagName('uptime')) > 0:
            self.uptime = HostNode.getElementsByTagName('uptime')[0].getAttribute('seconds')
            self.lastboot = HostNode.getElementsByTagName('uptime')[0].getAttribute('lastboot')
        if len(HostNode.getElementsByTagName('distance')) > 0:
            self.distance = int(HostNode.getElementsByTagName('distance')[0].getAttribute('value'))
        if len(HostNode.getElementsByTagName('extraports')) > 0:
            self.state = HostNode.getElementsByTagName('extraports')[0].getAttribute('state')
            self.count = HostNode.getElementsByTagName('extraports')[0].getAttribute('count')

    def getOs(self):
        oss = []

        for osNode in self.hostNode.getElementsByTagName('osclass'):
            os = OS.OS(osNode)
            oss.append(os)

        for osNode in self.hostNode.getElementsByTagName('osmatch'):
            os = OS.OS(osNode)
            oss.append(os)

        return oss

    def all_ports( self ):
        
        ports = []

        for portNode in self.hostNode.getElementsByTagName('port'):
            p = Port.Port(portNode)
            ports.append(p)

        return ports

    def getPorts( self, protocol, state ):
        '''get a list of ports which is in the special state'''

        open_ports = []

        for portNode in self.hostNode.getElementsByTagName('port'):
            if portNode.getAttribute('protocol') == protocol and portNode.getElementsByTagName('state')[0]\
                    .getAttribute('state') == state:
                open_ports.append( portNode.getAttribute('portid') )

        return open_ports

    def getScripts( self ):

        scripts = []

        for scriptNode in self.hostNode.getElementsByTagName('script'):
            scr = Script.Script(scriptNode)
            scr.hostId = self.ipv4
            scripts.append(scr)

        return scripts

    def getHostScripts( self ):

        scripts = []
        for hostscriptNode in self.hostNode.getElementsByTagName('hostscript'):
            for scriptNode in hostscriptNode.getElementsByTagName('script'):
                scr = Script.Script(scriptNode)
                scripts.append(scr)

        return scripts

    def getService( self, protocol, port ):
        '''return a Service object'''

        for portNode in self.hostNode.getElementsByTagName('port'):
            if portNode.getAttribute('protocol') == protocol and portNode.getAttribute('portid') == port and \
                    len(portNode.getElementsByTagName('service')) > 0:
                service_node = portNode.getElementsByTagName('service')[0]
                service = Service.Service( service_node )
                return service
        return None
