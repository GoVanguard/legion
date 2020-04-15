"""
LEGION (https://govanguard.com)
Copyright (c) 2020 GoVanguard

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
import unittest
from unittest.mock import MagicMock, patch

from db.repositories.NoteRepository import NoteRepository
from tests.db.helpers.db_helpers import mockQueryWithFilterBy, mockFirstByReturnValue


class NoteRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        from db.entities.note import note
        self.mockDbAdapter = MagicMock()
        self.mockDbSession = MagicMock()
        self.someNote: note = MagicMock()
        self.mockLog = MagicMock()
        self.noteRepository: NoteRepository = NoteRepository(self.mockDbAdapter, self.mockLog)

    def test_getNoteByHostId_WhenProvidedHostId_ReturnsNote(self):
        self.mockDbAdapter.session.return_value = self.mockDbSession
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(mockFirstByReturnValue("some-note"))

        note = self.noteRepository.getNoteByHostId("some-host-id")
        self.assertEqual("some-note", note)

    def test_storeNotes_WhenProvidedHostIdAndNoteAndNoteAlreadyExists_UpdatesNote(self):
        self.mockDbAdapter.session.return_value = self.mockDbSession
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(mockFirstByReturnValue(self.someNote))
        self.noteRepository.storeNotes("some-host-id", "some-note")
        self.mockDbSession.add.assert_called_once_with(self.someNote)
        self.mockDbAdapter.commit.assert_called_once()

    def test_storeNotes_WhenProvidedHostIdAndNoteAndNoteDoesNotExist_SavesNewNote(self):
        self.mockDbAdapter.session.return_value = self.mockDbSession
        self.mockDbSession.query.return_value = mockQueryWithFilterBy(mockFirstByReturnValue(None))
        self.noteRepository.storeNotes("some-host-id", "some-note")
        self.mockDbSession.add.assert_called_once()
        self.mockDbAdapter.commit.assert_called_once()
