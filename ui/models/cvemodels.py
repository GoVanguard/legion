#!/usr/bin/env python

"""
LEGION (https://govanguard.com)
Copyright (c) 2022 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
    version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
    details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <http://www.gnu.org/licenses/>.
"""

import re
from typing import Dict

from PyQt5 import QtWidgets, QtGui, QtCore

from app.ModelHelpers import resolveHeaders, itemInteractive
from app.auxiliary import *                                                 # for bubble sort

class CvesTableModel(QtCore.QAbstractTableModel):
    def __init__(self, controller, cves = [[]], headers = [], parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__headers = headers
        self.__cves = cves
        self.__controller = controller
        self.columnMapping = {
            0: "name",
            1: "severity",
            2: "product",
            3: "version",
            4: "url",
            5: "source",
            6: "exploitId",
            7: "exploit",
            8: "exploitUrl"
        }
        
    def setCves(self, cves):
        self.__cves = cves
        
    def getCves(self):
        return self.__cves

    def rowCount(self, parent):
        return len(self.__cves)

    def columnCount(self, parent):
        if len(self.__cves) != 0:
            return len(self.__cves[0])
        return 0

    def headerData(self, section, orientation, role):
        return resolveHeaders(role, orientation, section, self.__headers)
                
    def data(self, index, role):  # this method takes care of how the information is displayed
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:  # how to display each cell
            row = index.row()
            column = index.column()
            return self.__cves[row][self.columnMapping[column]]

    def sort(self, Ncol, order):
        self.layoutAboutToBeChanged.emit()

        array = []
        for i in range(len(self.__cves)):
            array.append(self.__cves[i][self.columnMapping[Ncol]])

        sortArrayWithArray(array, self.__cves)  # sort the services based on the values in the array

        if order == Qt.AscendingOrder:                                  # reverse if needed
            self.__cves.reverse()
            
        self.layoutChanged.emit()

    # method that allows views to know how to treat each item, eg: if it should be enabled, editable, selectable etc
    def flags(self, index):
        return itemInteractive()

    ### getter functions ###

    def getCveDBIdForRow(self, row):
        return self.__cves[row]['name']

    def getCveForRow(self, row):
        return self.__cves[row]
    
    def getRowForDBId(self, id):
        for i in range(len(self.__cves)):
            if self.__cves[i]['name'] == id:
                return i
