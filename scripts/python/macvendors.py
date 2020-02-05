import requests
import json

class macvendorsScript():
    def __init__(self):
        self.dbHost = None
        self.session = None

    def setDbHost(self, dbHost):
        self.dbHost = dbHost

    def setSession(self, session):
        self.session = session

    def run(self):
        print('Running MacVendors class')
        url = "https://api.macvendors.com/" + str(self.dbHost.macaddr)
        if self.dbHost:
            r = requests.get(url)
            result = str(r.text)
            if type(result) == type(str()):
                if result:
                    self.dbHost.vendor = result
                    print('The vendor is: ' + result)
                    self.session.add(self.dbHost)

if __name__ == "__main__":
    pass
