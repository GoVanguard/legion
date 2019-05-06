#!/usr/bin/python

import sys
import xml.dom.minidom

class CVE:
    name = ''
    product = ''
    version = ''
    url = ''
    source = ''
    severity = ''
    exploitId = ''
    exploit = ''
    exploitUrl = ''

    def __init__(self, cveData):
        self.name = cveData.get('id', 'unknown')
        self.product = cveData.get('product', 'unknown')
        self.version = cveData.get('version', 'unknown')
        self.url = cveData.get('url', 'unknown')
        self.source = cveData.get('source', 'unknown')
        self.severity = cveData.get('severity', 'unknown')
        self.exploitId = cveData.get('exploitId', 'unknown')
        self.exploit = cveData.get('exploit', 'unknown')
        self.exploitUrl = cveData.get('exploitUrl', 'unknown')
