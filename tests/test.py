try:
    from sqlalchemy.orm.scoping import ScopedSession as scoped_session
    print("SQL Alchemy library OK")
except ImportError:
    print("Import failed. SQL Alchemy library not found.")
    exit(1)

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
    print("PyQt5 library OK.")
except ImportError:
    print("Import failed. PyQt5 library not found.")
    exit(1)

try:
    import quamash
    import asyncio
    print("Quamash and asyncio libraries OK.")
except ImportError:
    print("Import failed. quamash or asyncio not found.")
    exit(1)

try:
    from app.logic import *
    from ui.gui import *
    from ui.view import *
    from controller.controller import *
    print("Legion class imports OK.")
except ImportError:
    print("Import failed. One or more modules failed to import correctly.")
    exit(1)
