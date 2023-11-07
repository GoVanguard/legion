"""
LEGION (https://gotham-security.com)
Copyright (c) 2023 Gotham Security

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
    version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
    details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <http://www.gnu.org/licenses/>.

Author(s): Shane Scott (sscott@gotham-security.com), Dmitriy Dubson (d.dubson@gmail.com)
"""
import unittest
from os.path import dirname, join
from typing import Optional

from parsers.Host import Host
from parsers.OS import OS
from parsers.Parser import Parser, parseNmapReport, MalformedXmlDocumentException
from parsers.Port import Port
from parsers.Session import Session


def givenAnXmlFile(xmlFile: str) -> Parser:
    return parseNmapReport(join(dirname(__file__), xmlFile))


class ParserTest(unittest.TestCase):
    def test_parseNmapReport_givenAValidXml_ReturnsAValidParser(self):
        self.assertIsNotNone(givenAnXmlFile("nmap-fixtures/valid-nmap-report.xml"))

    def test_parseNmapReport_givenAnInvalidXml_RaisesException(self):
        with self.assertRaises(MalformedXmlDocumentException):
            givenAnXmlFile("nmap-fixtures/malformed-nmap-report.xml")

    def test_parser_givenValidXmlWithHosts_ReturnsServicesParsed(self):
        parser = givenAnXmlFile("nmap-fixtures/valid-nmap-report.xml")
        hosts = list(parser.getAllHosts())
        self.assertEqual(1, len(hosts))

        allPorts: [Port] = hosts[0].all_ports()
        allServiceNames: [str] = list(map(lambda port: port.getService().name, allPorts))
        allServiceVersions: [str] = list(map(lambda port: port.getService().version, allPorts))
        allServiceFingerprints: [str] = list(map(lambda port: port.getService().fingerprint, allPorts))
        allServiceProducts: [str] = list(map(lambda port: port.getService().product, allPorts))
        allServiceExtraInfos: [str] = list(map(lambda port: port.getService().extrainfo, allPorts))
        self.assertEqual(['domain', 'http', 'netbios-ssn', 'https', 'msft'], allServiceNames)
        self.assertEqual(['0.0', '0.0', '0.0', '1.0', '0.0'], allServiceVersions)
        self.assertEqual(['p1', 'p2', 'p3', 'p4', 'p5'], allServiceFingerprints)
        self.assertEqual(['table', 'table', 'table', 'table', 'table'], allServiceProducts)
        self.assertEqual(['exinfo', 'exinfo', 'exinfo', 'exinfo', 'exinfo'], allServiceExtraInfos)

    def test_parser_givenAValidXmlWithIpAddresses_ReturnsAllIpAddresses(self):
        parser = givenAnXmlFile("nmap-fixtures/valid-nmap-report.xml")
        self.assertEqual(['192.168.1.1'], parser.getAllIps())

    def test_parser_givenAValidXmlWithIpAddressesAndFilterByStatus_ReturnsAllIpAddresses(self):
        parser = givenAnXmlFile("nmap-fixtures/valid-nmap-report.xml")
        self.assertEqual(['192.168.1.1'], parser.getAllIps('up'))

    def test_parser_givenAValidXmlWithIpAddressesAndFilterByStatusWithNoResults_ReturnsAnEmptyList(self):
        parser = givenAnXmlFile("nmap-fixtures/valid-nmap-report.xml")
        self.assertEqual([], parser.getAllIps('down'))

    def test_parser_givenAValidXmlWithHosts_ReturnsHostByIpAddress(self):
        parser = givenAnXmlFile("nmap-fixtures/valid-nmap-report.xml")
        host: Optional[Host.Host] = parser.getHost("192.168.1.1")
        self.assertIsNotNone(host)

        self.assertEqual("192.168.1.1", host.ip)
        self.assertEqual("192.168.1.1", host.ipv4)
        self.assertEqual("up", host.status)
        self.assertEqual("coolhost", host.hostname)
        self.assertEqual("closed", host.state)

        ports: [Port.Port] = host.all_ports()
        allPortIds: [str] = list(map(lambda port: port.portId, ports))
        allPortProtocols: [str] = list(map(lambda port: port.protocol, ports))
        allPortStates: [str] = list(map(lambda port: port.state, ports))
        self.assertEqual(['53', '80', '139', '443', '445'], allPortIds)
        self.assertEqual(['tcp', 'tcp', 'tcp', 'tcp', 'tcp'], allPortProtocols)
        self.assertEqual(['open', 'open', 'open', 'open', 'open'], allPortStates)

        self.assertEqual(1, len(host.getOs()))
        operatingSystem: OS = host.getOs()[0]
        self.assertEqual("macos", operatingSystem.name)
        self.assertEqual("darwin", operatingSystem.family)
        self.assertEqual("x64", operatingSystem.osType)
        self.assertEqual("5", operatingSystem.generation)
        self.assertEqual("apple", operatingSystem.vendor)
        self.assertEqual("98%", operatingSystem.accuracy)

    def test_parser_givenAValidXmlButInvalidHostIp_ReturnsNone(self):
        parser = givenAnXmlFile("nmap-fixtures/valid-nmap-report.xml")
        self.assertIsNone(parser.getHost("192.168.1.2"))

    def test_parser_givenAValidXml_ReturnsSessionInfo(self):
        parser = givenAnXmlFile("nmap-fixtures/valid-nmap-report.xml")
        session: Session.Session = parser.getSession()
        self.assertEqual("Wed Apr 15 20:34:59 2020", session.finish_time)
        self.assertEqual("7.80", session.nmapVersion)
        self.assertEqual("nmap -oX output.xml --stylesheet nmap.xsl -vv -p1-1024 -sT 192.168.1.1", session.scanArgs)
        self.assertEqual("Wed Apr 15 20:34:59 2020", session.startTime)
        self.assertEqual("1", session.totalHosts)
        self.assertEqual("1", session.upHosts)
        self.assertEqual("0", session.downHosts)
