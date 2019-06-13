from pyShodan import PyShodan

class PyShodanScript():
    def __init__(self):
        self.dbHost = None
        self.session = None

    def setDbHost(self, dbHost):
        self.dbHost = dbHost

    def setSession(self, session):
        self.session = session

    def run(self):
        print('Running PyShodan Class')
        if self.dbHost:
            pyShodanObj = PyShodan()
            pyShodanObj.apiKey = "SNYEkE0gdwNu9BRURVDjWPXePCquXqht"
            pyShodanObj.createSession()
            pyShodanResults = pyShodanObj.searchIp(self.dbHost.ipv4, allData = True)
            if type(pyShodanResults) == type(dict()):
                if pyShodanResults:
                    self.dbHost.latitude = pyShodanResults.get('latitude', 'unknown')
                    self.dbHost.longitude = pyShodanResults.get('longitude', 'unknown')
                    self.dbHost.asn = pyShodanResults.get('asn', 'unknown')
                    self.dbHost.ips = pyShodanResults.get('isp', 'unknown')
                    self.dbHost.city = pyShodanResults.get('city', 'unknown')
                    self.dbHost.countryCode = pyShodanResults.get('country_code', 'unknown')
                    self.session.add(self.dbHost)

if __name__ == "__main__":
    pass
