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

Author(s): Shane Scott (sscott@gotham-security.com), Dmitriy Dubson (d.dubson@gmail.com)
"""
from db.RepositoryContainer import RepositoryContainer
from db.SqliteDbAdapter import Database
from db.repositories.CVERepository import CVERepository
from db.repositories.HostRepository import HostRepository
from db.repositories.NoteRepository import NoteRepository
from db.repositories.PortRepository import PortRepository
from db.repositories.ProcessRepository import ProcessRepository
from db.repositories.ScriptRepository import ScriptRepository
from db.repositories.ServiceRepository import ServiceRepository


class RepositoryFactory:
    def __init__(self, logger):
        self.logger = logger

    def buildRepositories(self, database: Database) -> RepositoryContainer:
        hostRepository = HostRepository(database)
        processRepository = ProcessRepository(database, self.logger)
        serviceRepository = ServiceRepository(database)
        portRepository: PortRepository = PortRepository(database)
        cveRepository: CVERepository = CVERepository(database)
        noteRepository: NoteRepository = NoteRepository(database, self.logger)
        scriptRepository: ScriptRepository = ScriptRepository(database)
        return RepositoryContainer(serviceRepository, processRepository, hostRepository,
                                   portRepository, cveRepository, noteRepository, scriptRepository)
