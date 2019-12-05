"""
LEGION (https://govanguard.io)
Copyright (c) 2018 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
    version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
    details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <http://www.gnu.org/licenses/>.
"""
import subprocess

from PyQt5 import QtCore

from app.http.isHttps import isHttps
from app.timing import getTimestamp


class Screenshooter(QtCore.QThread):
    done = QtCore.pyqtSignal(str, str, str, name="done")  # signal sent after each individual screenshot is taken
    log = QtCore.pyqtSignal(str, name="log")

    def __init__(self, timeout):
        QtCore.QThread.__init__(self, parent=None)
        self.urls = []
        self.processing = False
        self.timeout = timeout  # screenshooter timeout (ms)

    def tsLog(self, msg):
        self.log.emit(str(msg))

    def addToQueue(self, url):
        self.urls.append(url)

    # this function should be called when the project is saved/saved as as the tool-output folder changes
    def updateOutputFolder(self, screenshotsFolder):
        self.outputfolder = screenshotsFolder

    def run(self):

        while self.processing == True:
            self.sleep(1)  # effectively a semaphore

        self.processing = True

        for i in range(0, len(self.urls)):
            try:
                url = self.urls.pop(0)
                outputfile = getTimestamp() + '-screenshot-' + url.replace(':', '-') + '.png'
                ip = url.split(':')[0]
                port = url.split(':')[1]

                if isHttps(ip, port):
                    self.save("https://" + url, ip, port, outputfile)
                else:
                    self.save("http://" + url, ip, port, outputfile)

            except Exception as e:
                self.tsLog('Unable to take the screenshot. Moving on..')
                self.tsLog(e)
                continue

        self.processing = False

        if not len(self.urls) == 0:  # if meanwhile urls were added to the queue, start over unless we are in pause mode
            self.run()

        self.tsLog('Finished.')

    def save(self, url, ip, port, outputfile):
        self.tsLog('Saving screenshot as: ' + str(outputfile))
        command = 'xvfb-run --server-args="-screen 0:0, 1024x768x24" /usr/bin/cutycapt --url="{url}/"' + \
                  ' --max-wait=5000 --out="{outputfolder}/{outputfile}"' \
                      .format(url=url, outputfolder=self.outputfolder, outputfile=outputfile)
        p = subprocess.Popen(command, shell=True)
        p.wait()  # wait for command to finish
        self.done.emit(ip, port, outputfile)  # send a signal to add the 'process' to the DB
