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
from datetime import datetime
from time import time
from unittest.mock import patch

from app.timing import getTimestamp


class TimingTest(unittest.TestCase):
    @patch('utilities.stenoLogging.get_logger')
    def test_getTimestamp_WhenInvokedWithNoParameters_ReturnsStandardFormattedTimestamp(self, getLogger):
        expectedStandardTimestampFormat = "%Y%m%d%H%M%S%f"
        currentTime = datetime.fromtimestamp(time())
        self.assertEqual(getTimestamp()[:-3], currentTime.strftime(expectedStandardTimestampFormat)[:-3])

    @patch('utilities.stenoLogging.get_logger')
    def test_getTimestamp_WhenInvokedWithHumanParameter_ReturnsHumanFormattedTimestamp(self, getLogger):
        expectedHumanTimestampFormat = "%d %b %Y %H:%M:%S.%f"
        currentTime = datetime.fromtimestamp(time())
        self.assertEqual(getTimestamp(human=True)[:-3], currentTime.strftime(expectedHumanTimestampFormat)[:-3])
