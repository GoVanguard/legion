#!/usr/bin/python
from app.logging.legionLog import log

__author__ =  'yunshu(wustyunshu@hotmail.com)'
__version__=  '0.2'

import sys
import xml.dom.minidom

class Session:
    def __init__( self, SessionHT ):
        self.startTime = SessionHT.get('startTime', '')
        self.finish_time = SessionHT.get('finish_time', '')
        self.nmapVersion = SessionHT.get('nmapVersion', '')
        self.scanArgs = SessionHT.get('scanArgs', '')
        self.totalHosts = SessionHT.get('totalHosts', '')
        self.upHosts = SessionHT.get('upHosts', '')
        self.downHosts = SessionHT.get('downHosts', '')

if __name__ == '__main__':

    dom = xml.dom.minidom.parse('i.xml')
    dom.getElementsByTagName('finished')[0].getAttribute('timestr')

    MySession = { 'finish_time': dom.getElementsByTagName('finished')[0].getAttribute('timestr'),
                  'nmapVersion' : '4.79', 'scanArgs' : '-sS -sV -A -T4',
                  'startTime' : dom.getElementsByTagName('nmaprun')[0].getAttribute('startstr'),
                  'totalHosts' : '1', 'upHosts' : '1', 'downHosts' : '0' }

    s = Session( MySession )

    log.info('startTime:' + s.startTime)
    log.info('finish_time:' + s.finish_time)
    log.info('nmapVersion:' + s.nmapVersion)
    log.info('nmap_args:' + s.scanArgs)
    log.info('total hosts:' + s.totalHosts)
    log.info('up hosts:' + s.upHosts)
    log.info('down hosts:' + s.downHosts)
