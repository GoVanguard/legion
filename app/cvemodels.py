#!/usr/bin/env python

'''
LEGION (https://govanguard.io)
Copyright (c) 2018 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
from PyQt5 import QtWidgets, QtGui, QtCore
from app.auxiliary import *                                                 # for bubble sort

class CvesTableModel(QtCore.QAbstractTableModel):
    
    def __init__(self, controller, cves = [[]], headers = [], parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__headers = headers
        self.__cves = cves
        self.__controller = controller
        
    def setCves(self, cves):
        self.__cves = cves
        
    def getCves(self):
        return self.__cves

    def rowCount(self, parent):
        return len(self.__cves)

    def columnCount(self, parent):
        if not len(self.__cves) is 0:
            return len(self.__cves[0])
        return 0

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:            
            if orientation == QtCore.Qt.Horizontal:                
                if section < len(self.__headers):
                    return self.__headers[section]
                else:
                    return "not implemented"
                
    def data(self, index, role):                                        # this method takes care of how the information is displayed

        if role == QtCore.Qt.DisplayRole:                               # how to display each cell
            value = ''
            row = index.row()
            column = index.column()
            if column == 0:
                value = self.__cves[row]['name']
            elif column == 1:
                value = self.__cves[row]['severity']
            elif column == 2:
                value = self.__cves[row]['product']
            elif column == 3:
                value = self.__cves[row]['version']
            elif column == 4:
                value = self.__cves[row]['url']
            elif column == 5:
                value = self.__cves[row]['source']
            return value
                    

    def sort(self, Ncol, order):
        self.layoutAboutToBeChanged.emit()
        array=[]
        
        if Ncol == 0:            
            for i in range(len(self.__cves)):
                array.append(self.__cves[i]['name'])
        elif Ncol == 1:
            for i in range(len(self.__cves)):
                array.append(self.__cves[i]['severity'])
        elif Ncol == 2:
            for i in range(len(self.__cves)):
                array.append(self.__cves[i]['product'])
        elif Ncol == 3:
            for i in range(len(self.__cves)):
                array.append(self.__cves[i]['version'])
        elif Ncol == 4:
            for i in range(len(self.__cves)):
                array.append(self.__cves[i]['url'])
        elif Ncol == 5:
            for i in range(len(self.__cves)):
                array.append(self.__cves[i]['source'])

        sortArrayWithArray(array, self.__cves)                       # sort the services based on the values in the array

        if order == Qt.AscendingOrder:                                  # reverse if needed
            self.__cves.reverse()
            
        self.layoutChanged.emit()

    def flags(self, index):                                             # method that allows views to know how to treat each item, eg: if it should be enabled, editable, selectable etc
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    ### getter functions ###

    def getCveDBIdForRow(self, row):
        return self.__cves[row]['name']
    
    def getRowForDBId(self, id):
        for i in range(len(self.__cves)):
            if self.__cves[i]['name'] == id:
                return i
