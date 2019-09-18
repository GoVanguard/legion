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

Author(s): Dmitriy Dubson (d.dubson@gmail.com)
"""
import unittest
from unittest.mock import patch, MagicMock

from tests.db.helpers.db_helpers import mockExecuteFetchAll


class CVERepositoryTest(unittest.TestCase):
    @patch('utilities.stenoLogging.get_logger')
    def setUp(self, get_logger) -> None:
        self.mock_db_adapter = MagicMock()

    def test_getCVEsByHostIP_WhenProvidedAHostIp_ReturnsCVEs(self):
        from db.repositories.CVERepository import CVERepository
        self.mock_db_adapter.metadata.bind.execute.return_value = mockExecuteFetchAll([['cve1'], ['cve2']])
        expected_query = ("SELECT cves.name, cves.severity, cves.product, cves.version, cves.url, cves.source, "
                          "cves.exploitId, cves.exploit, cves.exploitUrl FROM cve AS cves "
                          "INNER JOIN hostObj AS hosts ON hosts.id = cves.hostId "
                          "WHERE hosts.ip = ?")
        cveRepository = CVERepository(self.mock_db_adapter)
        result = cveRepository.getCVEsByHostIP("some_host")
        self.assertEqual([['cve1'], ['cve2']], result)
        self.mock_db_adapter.metadata.bind.execute.assert_called_once_with(expected_query, "some_host")
