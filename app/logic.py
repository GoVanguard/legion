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
import tempfile

from app.shell.Shell import Shell
from db.database import *
from db.repositories.CVERepository import CVERepository
from db.repositories.HostRepository import HostRepository
from db.repositories.NoteRepository import NoteRepository
from db.repositories.PortRepository import PortRepository
from db.repositories.ProcessRepository import ProcessRepository
from db.repositories.ScriptRepository import ScriptRepository
from db.repositories.ServiceRepository import ServiceRepository
from ui.ancillaryDialog import *


class Logic:
    def __init__(self, project_name: str, db: Database, shell: Shell, hostRepository: HostRepository):
        self.shell = shell
        self.db = db
        self.cwd = shell.get_current_working_directory()
        self.projectname = project_name
        self.createTemporaryFiles()  # creates temporary files/folders used by SPARTA
        log.info(project_name)
        self.reinitialize(db)

    def reinitialize(self, db: Database):
        self.serviceRepository: ServiceRepository = ServiceRepository(db)
        self.processRepository: ProcessRepository = ProcessRepository(db, log)
        self.hostRepository: HostRepository = HostRepository(db)
        self.portRepository: PortRepository = PortRepository(db)
        self.cveRepository: CVERepository = CVERepository(db)
        self.noteRepository: NoteRepository = NoteRepository(db, log)
        self.scriptRepository: ScriptRepository = ScriptRepository(db)

    def createTemporaryFiles(self):
        try:
            log.info('Creating temporary files..')
            self.istemp = True                                          # indicates that file is temporary and can be deleted if user exits without saving
            log.info(self.cwd)

            self.outputfolder = self.shell.create_temporary_directory(
                prefix="legion-", suffix="-tool-output", directory="./tmp/")  # to store tool output of finished processes
            self.runningfolder = self.shell.create_temporary_directory(
                prefix="legion-", suffix="-running", directory="./tmp/")  # to store tool output of running processes

            self.shell.create_directory_recursively(f"{self.outputfolder}/screenshots")  # to store screenshots
            self.shell.create_directory_recursively(f"{self.runningfolder}/nmap")  # to store nmap output
            self.shell.create_directory_recursively(f"{self.runningfolder}/hydra")  # to store hydra output
            self.shell.create_directory_recursively(f"{self.runningfolder}/dnsmap")  # to store dnsmap output

            self.usernamesWordlist = Wordlist(self.outputfolder + '/legion-usernames.txt')  # to store found usernames
            self.passwordsWordlist = Wordlist(self.outputfolder + '/legion-passwords.txt')  # to store found passwords
        except:
            log.info('Something went wrong creating the temporary files..')
            log.info("Unexpected error: {0}".format(sys.exc_info()[0]))

    def removeTemporaryFiles(self):
        log.info('Removing temporary files and folders..')
        try:
            # if current project is not temporary & delete wordlists if necessary
            if not self.istemp and not self.storeWordlists:
                log.info('Removing wordlist files.')
                self.shell.remove_file(self.usernamesWordlist.filename)
                self.shell.remove_file(self.passwordsWordlist.filename)
            else:
                self.shell.remove_file(self.projectname)
                self.shell.remove_directory(self.outputfolder)

            self.shell.remove_directory(self.runningfolder)
        except:
            log.info('Something went wrong removing temporary files and folders..')
            log.info("Unexpected error: {0}".format(sys.exc_info()[0]))

    def createFolderForTool(self, tool):
        if 'nmap' in tool:
            tool = 'nmap'
        path = self.runningfolder+'/'+re.sub("[^0-9a-zA-Z]", "", str(tool))
        if not os.path.exists(path):
            os.makedirs(path)

    # this flag is matched to the conf file setting, so that we know if we need to delete the found usernames/passwords wordlists on exit
    def setStoreWordlistsOnExit(self, flag=True):
        self.storeWordlists = flag

    # this function moves the specified tool output file from the temporary 'running' folder to the 'tool output' folder
    def moveToolOutput(self, outputFilename):
        try:
            # first create the tool folder if it doesn't already exist
            tool = ntpath.basename(ntpath.dirname(str(outputFilename)))
            path = self.outputfolder+'/'+str(tool)
            if not os.path.exists(str(path)):
                os.makedirs(str(path))

            # check if the outputFilename exists, if not try .xml and .txt extensions (different tools use different formats)
            if os.path.exists(str(outputFilename)) and os.path.isfile(str(outputFilename)):
                shutil.move(str(outputFilename), str(path))
            # move all the nmap files (not only the .xml)
            elif os.path.exists(str(outputFilename)+'.xml') and os.path.exists(str(outputFilename)+'.nmap') and os.path.exists(str(outputFilename)+'.gnmap') and os.path.isfile(str(outputFilename)+'.xml') and os.path.isfile(str(outputFilename)+'.nmap') and os.path.isfile(str(outputFilename)+'.gnmap'):
                try:
                    exportNmapToHTML(str(outputFilename))
                    shutil.move(str(outputFilename)+'.html', str(path))
                except:
                    pass

                shutil.move(str(outputFilename)+'.xml', str(path))
                shutil.move(str(outputFilename)+'.nmap', str(path))
                shutil.move(str(outputFilename)+'.gnmap', str(path))
            elif os.path.exists(str(outputFilename)+'.xml') and os.path.isfile(str(outputFilename)+'.xml'):
                shutil.move(str(outputFilename)+'.xml', str(path))
            elif os.path.exists(str(outputFilename)+'.txt') and os.path.isfile(str(outputFilename)+'.txt'):
                shutil.move(str(outputFilename)+'.txt', str(path))                          
        except:
            log.info('Something went wrong moving the tool output file..')
            log.info("Unexpected error: {0}".format(sys.exc_info()[0]))

    def copyNmapXMLToOutputFolder(self, file):
        try:
            path = self.outputfolder+"/nmap"
            filename = ntpath.basename(str(file))
            if not os.path.exists(str(path)):
                os.makedirs(str(path))

            shutil.copy(str(file), str(path))   # will overwrite if file already exists
        except:
            log.info('Something went wrong copying the imported XML to the project folder.')
            log.info("Unexpected error: {0}".format(sys.exc_info()[0]))

    def openExistingProject(self, filename, projectType="legion"):
        try:
            log.info('Opening project..')
            self.istemp = False                                         # indicate the file is NOT temporary and should NOT be deleted later
            
            self.projectname = str(filename)                            # set the new projectname and outputfolder vars
            nameOffset = len(projectType) + 1
            if not str(filename).endswith(projectType):         
                self.outputfolder = str(filename)+'-tool-output'        # use the same name as the file for the folder (without the extension)
            else:
                self.outputfolder = str(filename)[:-nameOffset]+'-tool-output'

            self.usernamesWordlist = Wordlist(self.outputfolder + '/' + projectType + '-usernames.txt')          # to store found usernames
            self.passwordsWordlist = Wordlist(self.outputfolder + '/' + projectType + '-passwords.txt')          # to store found passwords          
            
            self.runningfolder = tempfile.mkdtemp(suffix = "-running", prefix = projectType + '-')               # to store tool output of running processes
            self.db = Database(self.projectname)                        # use the new db
            self.reinitialize(self.db)
            self.cwd = ntpath.dirname(str(self.projectname))+'/'        # update cwd so it appears nicely in the window title
        
        except:
            log.info('Something went wrong while opening the project..')
            log.info("Unexpected error: {0}".format(sys.exc_info()[0]))
        
    # this function copies the current project files and folder to a new location
    # if the replace flag is set to 1, it overwrites the destination file and folder
    def saveProjectAs(self, filename, replace=0, projectType = 'legion'):
        try:
            # the folder name must be : filename-tool-output (without the .legion extension)
            nameOffset = len(projectType) + 1
            if not str(filename).endswith(projectType):
                foldername = str(filename)+'-tool-output'
                filename = str(filename) + '.legion'
            else:
                foldername = filename[:-nameOffset]+'-tool-output'

            # check if filename already exists (skip the check if we want to replace the file)
            if replace == 0 and os.path.exists(str(filename)) and os.path.isfile(str(filename)):
                return False

            shutil.copyfile(self.projectname, str(filename))
            os.system('cp -r "'+self.outputfolder+'/." "'+str(foldername)+'"')
            
            if self.istemp:                                             # we can remove the temp file/folder if it was temporary
                log.info('Removing temporary files and folders..')
                os.remove(self.projectname)
                shutil.rmtree(self.outputfolder)

            self.db.openDB(str(filename))                               # inform the DB to use the new file
            self.cwd = ntpath.dirname(str(filename))+'/'                # update cwd so it appears nicely in the window title
            self.projectname = str(filename)
            self.outputfolder = str(foldername)

            self.usernamesWordlist = Wordlist(self.outputfolder + '/legion-usernames.txt')          # to store found usernames
            self.passwordsWordlist = Wordlist(self.outputfolder + '/legion-passwords.txt')          # to store found passwords  
            
            self.istemp = False                                         # indicate that file is NOT temporary anymore and should NOT be deleted later
            return True

        except:
            log.info('Something went wrong while saving the project..')
            log.info("Unexpected error: {0}".format(sys.exc_info()[0]))
            return False
