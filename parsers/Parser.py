#!/usr/bin/python

'''this module used to parse nmap xml report'''
__author__ =  'yunshu(wustyunshu@hotmail.com)'
__version__=  '0.2'
__modified_by = 'ketchup'
__modified_by = 'SECFORCE'

import sys
import pprint
import logging
import parsers.Session as Session
import parsers.Host as Host
import parsers.Script as Script
import xml.dom.minidom
from six import u as unicode

class Parser:

    '''Parser class, parse a xml format nmap report'''
    def __init__( self, xml_input):
        '''constructor function, need a xml file name as the argument'''
        try:
            self.__dom = xml.dom.minidom.parse(xml_input)
            self.__session = None
            self.__hosts = { }
            for hostNode in self.__dom.getElementsByTagName('host'):
                __host =  Host.Host(hostNode)
                self.__hosts[__host.ip] = __host
        except Exception as ex:
            log.info("Parser error! Invalid nmap file!")
            #logging.error(ex)
            raise

    def getSession( self ):
        '''get this scans information, return a Session object'''
        run_node = self.__dom.getElementsByTagName('nmaprun')[0]
        hosts_node = self.__dom.getElementsByTagName('hosts')[0]

        finish_time = self.__dom.getElementsByTagName('finished')[0].getAttribute('timestr')

        nmapVersion = run_node.getAttribute('version')
        startTime =  run_node.getAttribute('startstr')
        scanArgs = run_node.getAttribute('args')

        totalHosts = hosts_node.getAttribute('total')
        upHosts = hosts_node.getAttribute('up')
        downHosts = hosts_node.getAttribute('down')

        MySession = { 'finish_time': finish_time,
                        'nmapVersion' : nmapVersion,
                        'scanArgs' : scanArgs,
                        'startTime' : startTime,
                        'totalHosts' : totalHosts,
                        'upHosts' : upHosts,
                        'downHosts' : downHosts }

        self.__session = Session.Session( MySession )

        return self.__session

    def getHost( self, ipaddr ):

        '''get a Host object by ip address'''

        return self.__hosts.get(ipaddr)

    def getAllHosts( self, status = '' ):

        '''get a list of Host object'''

        if( status == '' ):
            return self.__hosts.values( )

        else:
            __tmp_hosts = [ ]

            for __host in self.__hosts.values( ):

                if __host.status == status:
                    __tmp_hosts.append( __host )

            return __tmp_hosts

    def getAllIps( self, status = '' ):

        '''get a list of ip address'''
        __tmp_ips = [ ]

        if( status == '' ):
            for __host in self.__hosts.values( ):

                __tmp_ips.append( __host.ip )

        else:
            for __host in self.__hosts.values( ):

                if __host.status == status:
                    __tmp_ips.append( __host.ip )

        return __tmp_ips

if __name__ == '__main__':

    parser = Parser( 'a-full.xml' )

    log.info('\nscan session:')
    session = parser.getSession()
    log.info("\tstart time:\t" + session.startTime)
    log.info("\tstop time:\t" + session.finish_time)
    log.info("\tnmap version:\t" + session.nmapVersion)
    log.info("\tnmap args:\t" + session.scanArgs)
    log.info("\ttotal hosts:\t" + session.totalHosts)
    log.info("\tup hosts:\t" + session.upHosts)
    log.info("\tdown hosts:\t" + session.downHosts)

    for h in parser.getAllHosts():

        log.info('host ' +h.ip + ' is ' + h.status)

        for port in h.getPorts( 'tcp', 'open' ):
            print(port)
            log.info("\t---------------------------------------------------")
            log.info("\tservice of tcp port " + port + ":")
            s = h.getService( 'tcp', port )

            if s == None:
                log.info("\t\tno service")

            else:
                log.info("\t\t" + s.name)
                log.info("\t\t" + s.product)
                log.info("\t\t" + s.version)
                log.info("\t\t" + s.extrainfo)
                log.info("\t\t" + s.fingerprint)

            log.info("\tscript output:")
            sc = port.getScripts()
            
            if sc == None:
                log.info("\t\tno scripts")
            
            else:
                for scr in sc:
                    log.info("Script ID: " + scr.scriptId)
                    log.info("Output: ")
                    log.info(scr.output)

            log.info("\t---------------------------------------------------")
