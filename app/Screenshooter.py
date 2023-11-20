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

import os

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from PyQt6 import QtCore

from app.logging.legionLog import getAppLogger
from app.http.isHttps import isHttps
from app.timing import getTimestamp
from app.auxiliary import isKali

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
                outputfile = getTimestamp() + '-screenshot-' + url.replace(':', '-') + '.png'
                self.save(url, ip, port, outputfile)

            except Exception as e:
                self.tsLog('Unable to take the screenshot. Error follows.')
                self.tsLog(e)
                continue

        self.processing = False

        if not len(self.queue) == 0:  # if meanwhile queue were added to the queue, start over unless we are in pause mode
            self.run()

    def save(self, url, ip, port, outputfile):
        # Handle single node URI case by pivot to IP
        if len(str(url).split('.')) == 1:
            url = '{0}:{1}'.format(str(ip), str(port))

        if isHttps(ip, port):
            url = 'https://{0}'.format(url)
        else:
            url = 'http://{0}'.format(url)

        self.tsLog('Taking Screenshot of: {0}'.format(str(url)))

        # Use eyewitness under Kali. Use webdriver is not Kali. Once eyewitness is more boradly available, the conter case can be eliminated.
        if isKali():
            import tempfile
            import subprocess

            tmpOutputfolder = tempfile.mkdtemp(dir=self.outputfolder)
            command = ('xvfb-run --server-args="-screen 0:0, 1024x768x24" /usr/bin/eyewitness --single "{url}/"'
                       ' --no-prompt -d "{outputfolder}"') \
                      .format(url=url, outputfolder=tmpOutputfolder)
            p = subprocess.Popen(command, shell=True)
            p.wait()  # wait for command to finish
            fileName = os.listdir(tmpOutputfolder + '/screens/')[0]
            outputfile = tmpOutputfolder.removeprefix(self.outputfolder) + '/screens/' + fileName
        else:
            from selenium import webdriver

            driver = webdriver.PhantomJS(executable_path='/usr/bin/phantomjs')
            driver.set_window_size(1280, 1024)
            driver.get(url)
            driver.save_screenshot('{0}/{1}'.format(self.outputfolder, outputfile))
            driver.quit()
        self.tsLog('Saving screenshot as: {0}'.format(str(outputfile)))
        self.done.emit(ip, port, outputfile)  # send a signal to add the 'process' to the DB
