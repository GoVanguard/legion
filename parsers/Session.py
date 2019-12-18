#!/usr/bin/python
from app.logging.legionLog import log

__author__ =  'yunshu(wustyunshu@hotmail.com)'
__version__=  '0.2'

class Session:
    def __init__( self, SessionHT ):
        self.startTime = SessionHT.get('startTime', '')
        self.finish_time = SessionHT.get('finish_time', '')
        self.nmapVersion = SessionHT.get('nmapVersion', '')
        self.scanArgs = SessionHT.get('scanArgs', '')
        self.totalHosts = SessionHT.get('totalHosts', '')
        self.upHosts = SessionHT.get('upHosts', '')
        self.downHosts = SessionHT.get('downHosts', '')

