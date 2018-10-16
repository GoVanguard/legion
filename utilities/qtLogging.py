import sys
from PyQt5.QtGui import *                                               # for filters dialog
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtGui
from PyQt5 import QtCore, QtGui
import logging

class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        #self.widget.setReadOnly(True)    
        #self.sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #self.sizePolicy.setHorizontalStretch(1)
        #self.sizePolicy.setVerticalStretch(1)
        #self.widget.setSizePolicy(self.sizePolicy)
        #self.widget.setGeometry(0, 0, 200, 400)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)    
