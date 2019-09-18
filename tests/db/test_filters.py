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
from unittest.mock import patch


class FiltersTest(unittest.TestCase):
    @patch('utilities.stenoLogging.get_logger')
    def setUp(self, get_logger) -> None:
        return

    def test_applyFilters_InvokedWithNoFilters_ReturnsEmptyString(self):
        from app.auxiliary import Filters
        from db.filters import applyFilters

        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        result = applyFilters(filters)
        self.assertEqual("", result)

    def test_applyFilters_InvokedWithHostDownFilter_ReturnsQueryFilterWithHostsDown(self):
        from app.auxiliary import Filters
        from db.filters import applyFilters

        filters: Filters = Filters()
        filters.apply(up=True, down=False, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        result = applyFilters(filters)
        self.assertEqual(" AND hosts.status != 'down'", result)

    def test_applyFilters_InvokedWithHostUpFilter_ReturnsQueryFilterWithHostsUp(self):
        from app.auxiliary import Filters
        from db.filters import applyFilters

        filters: Filters = Filters()
        filters.apply(up=False, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        result = applyFilters(filters)
        self.assertEqual(" AND hosts.status != 'up'", result)

    def test_applyFilters_InvokedWithHostCheckedFilter_ReturnsQueryFilterWithHostsChecked(self):
        from app.auxiliary import Filters
        from db.filters import applyFilters

        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=False, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        result = applyFilters(filters)
        self.assertEqual(" AND hosts.checked != 'True'", result)

    def test_applyFilters_InvokedWithPortOpenFilter_ReturnsQueryFilterWithPortOpen(self):
        from app.auxiliary import Filters
        from db.filters import applyFilters

        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=False, portfiltered=True, portclosed=True,
                      tcp=True, udp=True)
        result = applyFilters(filters)
        self.assertEqual(" AND ports.state != 'open' AND ports.state != 'open|filtered'", result)

    def test_applyFilters_InvokedWithPortClosedFilter_ReturnsQueryFilterWithPortClosed(self):
        from app.auxiliary import Filters
        from db.filters import applyFilters

        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=False,
                      tcp=True, udp=True)
        result = applyFilters(filters)
        self.assertEqual(" AND ports.state != 'closed'", result)

    def test_applyFilters_InvokedWithPortFilteredFilter_ReturnsQueryFilterWithPortFiltered(self):
        from app.auxiliary import Filters
        from db.filters import applyFilters

        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=False, portclosed=True,
                      tcp=True, udp=True)
        result = applyFilters(filters)
        self.assertEqual(" AND ports.state != 'filtered' AND ports.state != 'open|filtered'", result)

    def test_applyFilters_InvokedWithTcpProtocolFilter_ReturnsQueryFilterWithTcp(self):
        from app.auxiliary import Filters
        from db.filters import applyFilters

        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=False, udp=True)
        result = applyFilters(filters)
        self.assertEqual(" AND ports.protocol != 'tcp'", result)

    def test_applyFilters_InvokedWithUdpProtocolFilter_ReturnsQueryFilterWithUdp(self):
        from app.auxiliary import Filters
        from db.filters import applyFilters

        filters: Filters = Filters()
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=False)
        result = applyFilters(filters)
        self.assertEqual(" AND ports.protocol != 'udp'", result)

    def test_applyFilters_InvokedWithKeywordsFilter_ReturnsQueryFilterWithKeywords(self):
        from app.auxiliary import Filters
        from db.filters import applyFilters

        filters: Filters = Filters()
        keyword = "some-keyword"
        filters.apply(up=True, down=True, checked=True, portopen=True, portfiltered=True, portclosed=True,
                      tcp=True, udp=True, keywords=[keyword])
        result = applyFilters(filters)
        self.assertEqual(" AND (hosts.ip LIKE '%some-keyword%' OR hosts.osMatch LIKE '%some-keyword%'"
                         " OR hosts.hostname LIKE '%some-keyword%')", result)
