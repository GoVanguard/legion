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
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from selenium import webdriver
from PyQt6 import QtCore

from app.logging.legionLog import getAppLogger
from app.http.isHttps import isHttps
from app.timing import getTimestamp

logger = getAppLogger()

class Screenshooter(QtCore.QThread):
    done = QtCore.pyqtSignal(str, str, str, name="done")  # signal sent after each individual screenshot is taken
    log = QtCore.pyqtSignal(str, name="log")

    def __init__(self, timeout):
        QtCore.QThread.__init__(self, parent=None)
        self.queue = []
        self.processing = False
        self.timeout = timeout  # screenshooter timeout (ms)

    def tsLog(self, msg):
        self.log.emit(str(msg))
        logger.info(msg)

    def addToQueue(self, ip, port, url):
        self.queue.append([ip, port, url])

    # this function should be called when the project is saved/saved as as the tool-output folder changes
    def updateOutputFolder(self, screenshotsFolder):
        self.outputfolder = screenshotsFolder

    def run(self):
        while self.processing == True:
            self.sleep(1)  # effectively a semaphore

        self.processing = True

        for i in range(0, len(self.queue)):
            try:
                queueItem = self.queue.pop(0)
                ip = queueItem[0]
                port = queueItem[1]
                url = queueItem[2]
                self.tsLog("------> %s" % str(url))
                outputfile = getTimestamp() + '-screenshot-' + url.replace(':', '-') + '.png'
                #ip = url.split(':')[0]
                #port = url.split(':')[1]

                if isHttps(ip, port):
                    self.save("https://" + url, ip, port, outputfile)
                else:
                    self.save("http://" + url, ip, port, outputfile)

            except Exception as e:
                self.tsLog('Unable to take the screenshot. Error follows.')
                self.tsLog(e)
                continue

        self.processing = False

        if not len(self.queue) == 0:  # if meanwhile queue were added to the queue, start over unless we are in pause mode
            self.run()

    def save(self, url, ip, port, outputfile):
        self.tsLog('Saving screenshot as: ' + str(outputfile))
        driver = webdriver.PhantomJS(executable_path="/usr/bin/phantomjs")
        driver.set_window_size(1280, 1024)
        driver.get(url)
        driver.save_screenshot("{0}/{1}".format(self.outputfolder, outputfile))
        driver.quit()
        self.done.emit(ip, port, outputfile)  # send a signal to add the 'process' to the DB
