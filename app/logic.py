#!/usr/bin/env python

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

import ntpath
import shutil

from app.Project import Project
from app.tools.ToolCoordinator import ToolCoordinator
from app.shell.Shell import Shell
from app.tools.nmap.NmapPaths import getNmapOutputFolder
from db.database import *
from ui.ancillaryDialog import *


class Logic:
    def __init__(self, shell: Shell, projectManager, toolCoordinator: ToolCoordinator):
        self.projectManager = projectManager
        self.activeProject: Project = None
        self.toolCoordinator = toolCoordinator
        self.shell = shell

    def createFolderForTool(self, tool):
        if 'nmap' in tool:
            tool = 'nmap'
        path = self.activeProject.properties.runningFolder + '/' + re.sub("[^0-9a-zA-Z]", "", str(tool))
        if not os.path.exists(path):
            os.makedirs(path)

    # this flag is matched to the conf file setting, so that we know if we need
    # to delete the found usernames/passwords wordlists on exit
    def setStoreWordlistsOnExit(self, flag=True):
        self.storeWordlists = flag

    def copyNmapXMLToOutputFolder(self, file):
        outputFolder = self.activeProject.properties.outputFolder
        try:
            path = getNmapOutputFolder(outputFolder)
            ntpath.basename(str(file))
            if not os.path.exists(path):
                os.makedirs(path)

            shutil.copy(str(file), path)  # will overwrite if file already exists
        except:
            log.info('Something went wrong copying the imported XML to the project folder.')
            log.info("Unexpected error: {0}".format(sys.exc_info()[0]))

    def createNewTemporaryProject(self) -> None:
        self.activeProject = self.projectManager.createNewProject(projectType="legion", isTemp=True)

    def openExistingProject(self, filename, projectType="legion") -> None:
        self.activeProject = self.projectManager.openExistingProject(projectName=filename, projectType=projectType)

    def saveProjectAs(self, filename, replace=0, projectType='legion') -> bool:
        self.activeProject = self.projectManager.saveProjectAs(self.activeProject, filename, replace, projectType)
        return True
