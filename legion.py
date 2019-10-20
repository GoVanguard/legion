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
from app.ProjectManager import ProjectManager
from app.shell.DefaultShell import DefaultShell
from app.tools.nmap.DefaultNmapExporter import DefaultNmapExporter
from db.RepositoryFactory import RepositoryFactory
from ui.eventfilter import MyEventFilter
from utilities.stenoLogging import *

log = get_logger('legion', path="./log/legion-startup.log")
log.setLevel(logging.INFO)

# check for dependencies first (make sure all non-standard dependencies are checked for here)
try:
    from sqlalchemy.orm.scoping import ScopedSession as scoped_session
except ImportError as e:
    log.info(
        "Import failed. SQL Alchemy library not found. If on Ubuntu or similar try: apt-get install python3-sqlalchemy*"
    )
    log.info(e)
    exit(1)

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
except ImportError as e:
    log.info("Import failed. PyQt5 library not found. If on Ubuntu or similar try: agt-get install python3-pyqt5")
    log.info(e)
    exit(1)

try:
    import quamash
    import asyncio
except ImportError as e:
    log.info("Import failed. Quamash or asyncio not found.")
    log.info(e)
    exit(1)

try:
    import sys
    from colorama import init

    init(strip=not sys.stdout.isatty())
    from termcolor import cprint
    from pyfiglet import figlet_format
except ImportError as e:
    log.info("Import failed. One or more of the terminal drawing libraries not found.")
    log.info(e)
    exit(1)

from ui.view import *
from controller.controller import *

# Main application declaration and loop
if __name__ == "__main__":
    cprint(figlet_format('LEGION', font='starwars'), 'yellow', 'on_red', attrs=['bold'])

    app = QApplication(sys.argv)
    loop = quamash.QEventLoop(app)
    asyncio.set_event_loop(loop)

    MainWindow = QtWidgets.QMainWindow()
    app.setWindowIcon(QIcon('./images/icons/Legion-N_128x128.svg'))

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    try:
        qss_file = open('./ui/legion.qss').read()
    except IOError as e:
        log.info(
            "The legion.qss file is missing. Your installation seems to be corrupted. " +
            "Try downloading the latest version.")
        exit(0)

    MainWindow.setStyleSheet(qss_file)

    shell = DefaultShell()

    repositoryFactory = RepositoryFactory(log)
    projectManager = ProjectManager(shell, repositoryFactory, log)
    nmapExporter = DefaultNmapExporter(shell)
    toolCoordinator = ToolCoordinator(shell, nmapExporter)
    # Model prep (logic, db and models)
    logic = Logic(shell, projectManager, toolCoordinator)

    log.info("Creating temporary project at application start...")
    logic.createNewTemporaryProject()

    viewState = ViewState()
    view = View(viewState, ui, MainWindow, shell)  # View prep (gui)
    controller = Controller(view, logic)  # Controller prep (communication between model and view)
    view.qss = qss_file

    myFilter = MyEventFilter(view, MainWindow)  # to capture events
    app.installEventFilter(myFilter)

    # Center the application in screen
    x = app.desktop().screenGeometry().center().x()
    y = app.desktop().screenGeometry().center().y()
    MainWindow.move(x - MainWindow.geometry().width() / 2, y - MainWindow.geometry().height() / 2)

    # Show main window
    MainWindow.show()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    app.deleteLater()
    loop.close()
    sys.exit()
