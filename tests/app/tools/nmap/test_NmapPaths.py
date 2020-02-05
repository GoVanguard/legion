import unittest

from app.tools.nmap.NmapPaths import getNmapRunningFolder, getNmapOutputFolder


class NmapPathsTest(unittest.TestCase):
    def test_getNmapRunningFolder_ReturnsProperNmapPathWithinAnActiveProject(self):
        self.assertEqual(getNmapRunningFolder("some-folder"), "some-folder/nmap")

    def test_getNmapOutputFolder_ReturnsProperNmapPathWithinAnActiveProject(self):
        self.assertEqual(getNmapOutputFolder("some-folder"), "some-folder/nmap")
