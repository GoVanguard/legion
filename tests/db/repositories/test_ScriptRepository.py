import unittest
from unittest.mock import MagicMock

from tests.db.helpers.db_helpers import mockExecuteFetchAll


class ScriptRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        from db.repositories.ScriptRepository import ScriptRepository
        self.mockDbAdapter = MagicMock()
        self.scriptRepository = ScriptRepository(self.mockDbAdapter)

    def test_getScriptsByHostIP_WhenProvidedAHostIP_ReturnsAllScripts(self):
        expectedQuery = ("SELECT host.id, host.scriptId, port.portId, port.protocol FROM l1ScriptObj AS host "
                         "INNER JOIN hostObj AS hosts ON hosts.id = host.hostId "
                         "LEFT OUTER JOIN portObj AS port ON port.id = host.portId WHERE hosts.ip=?")
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll(
            [['some-script1'], ['some-script2']])
        scripts = self.scriptRepository.getScriptsByHostIP("some-host-ip")
        self.assertEqual([['some-script1'], ['some-script2']], scripts)
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some-host-ip")

    def test_getScriptOutputById_WhenProvidedAScriptId_ReturnsScriptOutput(self):
        expectedQuery = "SELECT script.output FROM l1ScriptObj as script WHERE script.id = ?"
        self.mockDbAdapter.metadata.bind.execute.return_value = mockExecuteFetchAll(
            [['some-script-output1'], ['some-script-output2']])

        scripts = self.scriptRepository.getScriptOutputById("some-id")
        self.assertEqual([['some-script-output1'], ['some-script-output2']], scripts)
        self.mockDbAdapter.metadata.bind.execute.assert_called_once_with(expectedQuery, "some-id")
