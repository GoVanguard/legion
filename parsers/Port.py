#!/usr/bin/python

__author__ =  'SECFORCE'
__version__=  '0.1'

import parsers.Service as Service
import parsers.Script as Script

class Port:
    portId = ''
    protocol= ''
    state=''

    def __init__(self, PortNode):
        if not (PortNode is None):
            self.portNode = PortNode
            self.portId = PortNode.getAttribute('portid')
            self.protocol = PortNode.getAttribute('protocol')
            self.state = PortNode.getElementsByTagName('state')[0].getAttribute('state')

    def getService(self):

        service_node = self.portNode.getElementsByTagName('service')
        
        if len(service_node) > 0:
           return Service.Service(service_node[0])

        return None

   # def get_cpe(self):

   #     cpes = []
   #     cpe = self.portNode.getElementsByTagName('cpe')
   #     print(cpe)

   #     if len(cpe) > 0:
   #        return CPE.CPE(cpe[0])

   #     return None

    def getScripts(self):

        scripts = [ ]

        for scriptNode in self.portNode.getElementsByTagName('script'):
            scr = Script.Script(scriptNode)
            scripts.append(scr)

        return scripts
