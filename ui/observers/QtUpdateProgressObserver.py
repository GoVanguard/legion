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

Author(s): Dmitriy Dubson (d.dubson@gmail.com)
"""
from app.actions.updateProgress.AbstractUpdateProgressObserver import AbstractUpdateProgressObserver
from ui.ancillaryDialog import ProgressWidget


class QtUpdateProgressObserver(AbstractUpdateProgressObserver):
    def __init__(self, progressWidget: ProgressWidget):
        self.progressWidget = progressWidget

    def onStart(self) -> None:
        self.progressWidget.show()

    def onFinished(self) -> None:
        self.progressWidget.hide()

    def onProgressUpdate(self, progress: int) -> None:
        self.progressWidget.setProgress(progress)
        self.progressWidget.show()
