#!/usr/bin/env python
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
import shutil

from app.ProjectManager import ProjectManager
from app.logging.legionLog import getStartupLogger, getDbLogger
from app.shell.DefaultShell import DefaultShell
from app.tools.nmap.DefaultNmapExporter import DefaultNmapExporter
from db.RepositoryFactory import RepositoryFactory
from ui.eventfilter import MyEventFilter
from ui.ViewState import ViewState
from ui.gui import *
from ui.gui import Ui_MainWindow

startupLog = getStartupLogger()

# check for dependencies first (make sure all non-standard dependencies are checked for here)
try:
    from sqlalchemy.orm.scoping import ScopedSession as scoped_session
except ImportError as e:
    startupLog.error(
        "Import failed. SQL Alchemy library not found. If on Ubuntu or similar try: apt-get install python3-sqlalchemy*"
    )
    startupLog.error(e)
    exit(1)

try:
    from PyQt6 import QtWidgets, QtGui, QtCore
    from PyQt6.QtCore import QCoreApplication
except ImportError as e:
    startupLog.error("Import failed. PyQt6 library not found. If on Ubuntu or similar try: "
                     "apt-get install python3-pyqt5")
    startupLog.error(e)
    exit(1)

try:
    import qasync
    import asyncio
except ImportError as e:
    startupLog.error("Import failed. Quamash or asyncio not found.")
    startupLog.error(e)
    exit(1)

try:
    import sys
    from colorama import init

    init(strip=not sys.stdout.isatty())
    from termcolor import cprint
    from pyfiglet import figlet_format
except ImportError as e:
    startupLog.error("Import failed. One or more of the terminal drawing libraries not found.")
    startupLog.error(e)
    exit(1)

import os

#if not os.path.isdir(os.path.expanduser("~/.local/share/legion/tmp")):
#    os.makedirs(os.path.expanduser("~/.local/share/legion/tmp"))

if not os.path.isdir(os.path.expanduser("~/.local/share/legion/backup")):
    os.makedirs(os.path.expanduser("~/.local/share/legion/backup"))

if not os.path.exists(os.path.expanduser('~/.local/share/legion/legion.conf')):
    shutil.copy('./legion.conf', os.path.expanduser('~/.local/share/legion/legion.conf'))

# Check Nmap version is not 7.92- it segfaults under zsh constantly
import subprocess
checkNmapVersion = subprocess.check_output(['nmap', '-version'])

# Quite upgrade of pyExploitDb
upgradeExploitDb = os.system('pip install pyExploitDb --upgrade > /dev/null 2>&1')

from ui.view import *
from controller.controller import *

# Main application declaration and loop
if __name__ == "__main__":
    cprint(figlet_format('LEGION'), 'yellow', 'on_red', attrs=['bold'])

    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    MainWindow = QtWidgets.QMainWindow()
    Screen = QGuiApplication.primaryScreen()
    app.setWindowIcon(QIcon('./images/icons/Legion-N_128x128.svg'))

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # Possibly unneeded
    #try:
    #    qss_file = open('./ui/legion.qss').read()
    #except IOError:
    #    startupLog.error(
    #        "The legion.qss file is missing. Your installation seems to be corrupted. " +
    #        "Try downloading the latest version.")
    #    exit(0)

    if os.geteuid()!=0:
        startupLog.error("Legion must run as root for raw socket access. Please start legion using sudo.")
        notice=QMessageBox()
        notice.setIcon(QMessageBox.Icon.Critical)
        notice.setText("Legion must run as root for raw socket access. Please start legion using sudo.")
        notice.exec()
        exit(1)

    if '7.92' in checkNmapVersion.decode():
        startupLog.error("Cannot continue. NMAP version is 7.92, which has problems segfaulting under zsh.")
        startupLog.error("Please follow the instructions at https://github.com/GoVanguard/legion/ to resolve.")
        notice=QMessageBox()
        notice.setIcon(QMessageBox.Icon.Critical)
        notice.setText("Cannot continue. The installed NMAP version is 7.92, which has segfaults under zsh.\nPlease follow the instructions at https://github.com/GoVanguard/legion/ to resolve.")
        notice.exec_()
        exit(1)

    # Possibly unneeded
    #MainWindow.setStyleSheet(qss_file)

    shell = DefaultShell()

    dbLog = getDbLogger()
    appLogger = getAppLogger()

    repositoryFactory = RepositoryFactory(dbLog)
    projectManager = ProjectManager(shell, repositoryFactory, appLogger)
    nmapExporter = DefaultNmapExporter(shell, appLogger)
    toolCoordinator = ToolCoordinator(shell, nmapExporter)

    # Model prep (logic, db and models)
    logic = Logic(shell, projectManager, toolCoordinator)

    startupLog.info("Creating temporary project at application start...")
    logic.createNewTemporaryProject()

    viewState = ViewState()
    view = View(viewState, ui, MainWindow, shell, app, loop)  # View prep (gui)
    controller = Controller(view, logic)  # Controller prep (communication between model and view)

    # Possibly unneeded
    #view.qss = qss_file

    myFilter = MyEventFilter(view, MainWindow)  # to capture events
    app.installEventFilter(myFilter)

    # Center the application in screen
    screenCenter = Screen.availableGeometry().center()
    MainWindow.move(screenCenter - MainWindow.rect().center())

    # Show main window
    #MainWindow.showMaximized()

    startupLog.info("Legion started successfully.")
    try:
        sys.exit(loop.run_forever())
    except KeyboardInterrupt:
        pass

    #app.deleteLater()
    #app.quit()
    #loop.close()
    #sys.exit()
