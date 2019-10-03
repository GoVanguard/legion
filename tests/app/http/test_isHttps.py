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


class isHttpsTest(unittest.TestCase):
    def test_isHttps_GivenAnIpAddrAndPortThatIsHttps_ReturnsTrue(self):
        with patch("urllib.request.urlopen") as urlopen, patch("urllib.request.Request") as Request:
            expectedUserAgent = 'Mozilla/5.0 (X11; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0 Iceweasel/22.0'
            from app.http.isHttps import isHttps
            mockOpenedUrl = MagicMock()
            Request.return_value = MagicMock()
            urlopen.return_value.read.return_value = mockOpenedUrl
            self.assertTrue(isHttps("some-ip", "8080"))
            Request.assert_called_with("https://some-ip:8080", headers={"User-Agent": expectedUserAgent})
