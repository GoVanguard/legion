#!/usr/bin/python

__author__ =  'ketchup'
__version__=  '0.1'
__modified_by = 'ketchup'

import sys
import xml.dom.minidom
import parsers.CVE as CVE
from pyExploitDb import PyExploitDb

class Script:
    scriptId = ''
    output = ''

    def __init__(self, ScriptNode):
        if not (ScriptNode is None):
            self.scriptId = ScriptNode.getAttribute('id')
            self.output = ScriptNode.getAttribute('output')

    def getExploitDataFromCves(self, cveSet):
        for cveEntry in cveSet:
            print("CVE Entry: {0}".format(cveEntry))
            cveExploitData = self.pyExploitDb.searchCve(cveEntry(0))
            print("CVE Exploit Data: {0}".format(cveExploitData))

    def processVulnersScriptOutput(self, vulnersOutput):
        output = vulnersOutput.replace('\t\t\t','\t')
        output = output.replace('\t\t','\t')
        output = output.replace('\t',';')
        output = output.replace('\n;','\n')
        output = output.replace(' ','')
        output = output.split('\n')
        output = [entry for entry in output if len(entry) > 1]

        pyExploitDb = PyExploitDb()
        pyExploitDb.debug = False
        pyExploitDb.openFile()

        cpeList = []
        count = 0
        for entry in output:
            if 'cpe' in entry:
                cpeList.append(entry)
                output[count] = 'CPE'
            count = count + 1

        output = ' '.join(output)
        output = output.split('CPE')
        output = [entry for entry in output if len(entry) > 1]

        resultsDict = {}
        counter = 0
        for cpeEntry in cpeList:
            resultCpeData = cpeEntry.split(':')
            resultCpeData = [entry for entry in resultCpeData if len(entry) > 1]
            resultCpeDetails = {}
            resultCpeDetails['type'] = resultCpeData[1]
            resultCpeDetails['source'] = resultCpeData[2]
            resultCpeDetails['product'] = resultCpeData[3]
            resultCpeDetails['version'] = resultCpeData[4]
            resultCves = output[counter]
            resultCves = resultCves.split(' ')
            resultCves = [entry for entry in resultCves if len(entry) > 1]
            resultCvesProcessed = []
            for resultCve in resultCves:
                resultCveDict = {}
                resultCveData = resultCve.split(';')
                resultCveDict['id'] = resultCveData[0]
                resultCveDict['severity'] = resultCveData[1]
                resultCveDict['url'] = resultCveData[2]
                exploitResults = pyExploitDb.searchCve(resultCveData[0])
                print("-----------------{0}".format(exploitResults))
                if exploitResults:
                    resultCveDict['exploitid'] = exploitResults['edbid']
                    resultCveDict['exploit'] = exploitResults['exploit']
                    resultCveDict['exploiturl'] = "https://www.exploit-db.com/exploits/{0}".format(resultCveDict['exploit'])
                resultCvesProcessed.append(resultCveDict)
            resultCpeDetails['cves'] = resultCvesProcessed
            resultsDict[resultCpeData[3]] = resultCpeDetails
            count = count + 1

        return resultsDict 

    def get_cves(self):
        cveOutput = self.output
        cveObjects = []

        if len(cveOutput) > 0:
           cvesResults = self.processVulnersScriptOutput(cveOutput)

           for cpeEntry in cvesResults:
               cpeData = cvesResults[cpeEntry]
               cpeProduct = cpeEntry
               cpeType = cpeData['type']
               cpeVersion = cpeData['version']
               cpeSource = cpeData['source']
               cpeCves = cpeData['cves']
               for cveEntry in cpeCves:
                   cveData = cveEntry
                   cveData['type'] = cpeType
                   cveData['version'] = cpeVersion
                   cveData['source'] = cpeSource
                   cveData['product'] = cpeProduct
                   cveObj = CVE.CVE(cveData)
                   cveObjects.append(cveObj)
           return cveObjects
        return None

if __name__ == '__main__':

    dom = xml.dom.minidom.parse('a-full.xml')

    for scriptNode in dom.getElementsByTagName('script'):
        script = Script(scriptNode)
        log.info(script.scriptId)
        log.info(script.output)
