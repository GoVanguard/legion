#!/usr/bin/python

import sys
import xml.dom.minidom

class CPE:
    extrainfo = ''
    name = ''
    product = ''
    fingerprint = ''
    version = ''

    def __init__( self, CPE ):
        self.name = None 

#<port protocol="tcp" portid="135"><state state="open" reason="syn-ack" reason_ttl="128"/><service name="msrpc" product="Microsoft Windows RPC" ostype="Windows" method="probed" conf="10"><cpe>cpe:/o:microsoft:windows</cpe></service></port>

if __name__ == '__main__':

    dom = xml.dom.minidom.parse('i.xml')

    cpes = dom.getElementsByTagName('cpe')
    print(cpes)
    if len(cpes) == 0:
        sys.exit()

    node = dom.getElementsByTagName('service')[0]

    #s = CPE( node )
    #log.info(s.name)
    #log.info(s.product)
    #log.info(s.version)
    #log.info(s.extrainfo)
    #log.info(s.fingerprint)
