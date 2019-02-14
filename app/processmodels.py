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

class ProcessesTableModel(QtCore.QAbstractTableModel):
    
    def __init__(self, controller, processes = [[]], headers = [], parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__headers = headers
        self.__processes = processes
        self.__controller = controller
        
    def setProcesses(self, processes):
        self.__processes = processes
        
    def getProcesses(self):
        return self.__processes

    def rowCount(self, parent):
        return len(self.__processes)

    def columnCount(self, parent):
        if not len(self.__processes) is 0:
            return len(self.__processes[0])
        return 0

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            
            if orientation == QtCore.Qt.Horizontal:
                
                if section < len(self.__headers):
                    return self.__headers[section]
                else:
                    return "not implemented"

    def data(self, index, role):                                        # this method takes care of how the information is displayed
        if role != QtCore.Qt.DisplayRole:                               # how to display each cell      
            return

        value = ''
        row = index.row()
        column = index.column()
        processColumns = {0:'progress', 1:'display',  2:'elapsed', 3:'estimatedremaining', 4:'pid', 5:'name', 6:'tabtitle', 7:'hostip', 8:'port', 9:'protocol', 10:'command', 11:'starttime', 12:'endtime', 13:'outputfile', 14:'output', 15:'status', 16:'closed'}
        try:
            if column == 0:
                value = ''
            elif column == 2:
                pid = int(self.__processes[row]['pid'])
                elapsed = round(self.__controller.controller.processMeasurements.get(pid, 0), 2)
                value = "{0:.2f}{1}".format(float(elapsed), "s")
            elif column == 3:
                status = str(self.__processes[row]['status'])
                if status == "Finished" or status == "Crashed" or status == "Killed":
                    estimatedRemaining = 0
                else:
                    pid = int(self.__processes[row]['pid'])
                    elapsed = round(self.__controller.controller.processMeasurements.get(pid, 0), 2)
                    estimatedRemaining = int(self.__processes[row]['estimatedremaining']) - float(elapsed)
                value = "{0:.2f}{1}".format(float(estimatedRemaining), "s") if estimatedRemaining >= 0 else 'Unknown'
            elif column == 5 or column == 6:
                if not self.__processes[row]['tabtitle'] == '':
                    value = self.__processes[row]['tabtitle']
                else:
                    value = self.__processes[row]['name']
            elif column == 8:
                if not self.__processes[row]['port'] == '' and not self.__processes[row]['protocol'] == '':
                    value = self.__processes[row]['port'] + '/' + self.__processes[row]['protocol']
                else:
                    value = self.__processes[row]['port']
            elif column == 16:
                value = ""
            else:
                value = self.__processes[row][processColumns.get(int(column))]
        except Exception as e:
            print(str(self.__processes[row]))
            print(str(e))
        return value            

    def sort(self, Ncol, order):
        self.layoutAboutToBeChanged.emit()
        array=[]

        sortColumns = {5:'name', 6:'tabtitle', 11:'starttime', 12:'endtime'}
        field = sortColumns.get(int(Ncol)) or 'status'

        if Ncol == 7:
            for i in range(len(self.__processes)):
                array.append(IP2Int(self.__processes[i]['hostip']))

        elif Ncol == 8:
            for i in range(len(self.__processes)):
                if self.__processes[i]['port'] == '':
                    return
                else:
                    array.append(int(self.__processes[i]['port']))
        else:
            for i in range(len(self.__processes)):
                array.append(self.__processes[i][field])
        
        sortArrayWithArray(array, self.__processes)                     # sort the services based on the values in the array

        if order == Qt.AscendingOrder:                                  # reverse if needed
            self.__processes.reverse()
            self.__controller.processesTableViewSort = 'desc'
        else:
            self.__controller.processesTableViewSort = 'asc'

        self.__controller.processesTableViewSortColumn = field

        ## Extra?
        #self.__controller.updateProcessesIcon()                         # to make sure the progress GIF is displayed in the right place
        self.layoutChanged.emit()

    def flags(self, index):                                             # method that allows views to know how to treat each item, eg: if it should be enabled, editable, selectable etc
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setDataList(self, processes):
        self.__processes = processes
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    ### getter functions ###

    def getProcessPidForRow(self, row):
        return self.__processes[row]['pid']
        
    def getProcessPidForId(self, dbId):
        for i in range(len(self.__processes)):
            if str(self.__processes[i]['id']) == str(dbId):
                return self.__processes[i]['pid']   

    def getProcessStatusForRow(self, row):
        return self.__processes[row]['status']

    def getProcessStatusForPid(self, pid):
        for i in range(len(self.__processes)):
            if str(self.__processes[i]['pid']) == str(pid):
                return self.__processes[i]['status']
                
    def getProcessStatusForId(self, dbId):
        for i in range(len(self.__processes)):
            if str(self.__processes[i]['id']) == str(dbId):
                return self.__processes[i]['status']

    def getProcessIdForRow(self, row):
        return self.__processes[row]['id']
        
    def getToolNameForRow(self, row):
        return self.__processes[row]['name']
        
    def getRowForToolName(self, toolname):
        for i in range(len(self.__processes)):
            if self.__processes[i]['name'] == toolname:
                return i

    def getRowForDBId(self, dbid):  # new
        for i in range(len(self.__processes)):
            if self.__processes[i]['id'] == dbid:
                return i

    def getIpForRow(self, row):
        return self.__processes[row]['hostip']

    def getPortForRow(self, row):
        return self.__processes[row]['port']

    def getProtocolForRow(self, row):
        return self.__processes[row]['protocol']
        
    def getOutputfileForRow(self, row):
        return self.__processes[row]['outputfile']      
