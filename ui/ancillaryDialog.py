#!/usr/bin/env python

'''
LEGION (https://govanguard.io)
Copyright (c) 2018 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
from PyQt5.QtGui import *                                               # for filters dialog
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtGui
from app.auxiliary import *                                             # for timestamps
from six import u as unicode

def flipState(targetState, widgetsToFlipOn, widgetsToFlipOff):
    for widgetToFlipOn in widgetsToFlipOn:
        widgetToFlipOn.setEnabled(targetState)
    for widgetToFlipOff in widgetsToFlipOff:
        widgetToFlipOff.setEnabled(not targetState)

# Progress bar primative
class ProgressWidget(QtWidgets.QDialog):
    def __init__(self, text, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.text = text
        self.setWindowTitle(text)
        self.setupLayout()

    def setupLayout(self):
        self.setWindowModality(True)
        vbox = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel('')
        self.progressBar = QtWidgets.QProgressBar()
        vbox.addWidget(self.label)
        vbox.addWidget(self.progressBar)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def setProgress(self, progress):
        self.progressBar.setValue(progress)

    def setText(self, text):
        self.text = text
        self.setWindowTitle(text)
        
    def reset(self, text):
        self.text = text
        self.setWindowTitle(text)
        self.setProgress(0)

# Image display primative
class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.scaleFactor = 0.0

        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)

    def open(self, fileName):
        if fileName:
            image = QtGui.QImage(fileName)
            if image.isNull():
                QtWidgets.QMessageBox.information(self, "Image Viewer","Cannot load %s." % fileName)
                return

            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
            self.scaleFactor = 1.0                
            self.fitToWindow()

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.fitToWindow(False)
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self, fit=True):
        self.scrollArea.setWidgetResizable(fit)

    def scaleImage(self, factor):
        self.fitToWindow(False)
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)))

# Gif and supported video display primative
class ImagePlayer(QtWidgets.QWidget):
    def __init__(self, filename, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.movie = QtGui.QMovie(filename)
        self.movie_screen = QtWidgets.QLabel()
        self.movie_screen.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.movie_screen)
        self.setLayout(main_layout)
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.movie.setSpeed(100)
        self.movie_screen.setMovie(self.movie)
        self.movie.start()
        self.show()
