"""
LEGION (https://govanguard.com)
Copyright (c) 2019 GoVanguard

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
    version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
    details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <http://www.gnu.org/licenses/>.

Author(s): Dmitriy Dubson (d.dubson@gmail.com)
"""
from PyQt5 import QtCore


def resolveHeaders(role, orientation, section, headers):
    if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
        if section < len(headers):
            return headers[section]
        else:
            return "not implemented in view model"


def itemInteractive() -> QtCore.Qt.ItemFlag:
    return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable


def itemSelectable() -> QtCore.Qt.ItemFlag:
    return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
