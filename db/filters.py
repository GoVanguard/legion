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
from db.validation import sanitise


def applyFilters(filters):
    query_filter = ""
    query_filter += applyHostsFilters(filters)
    query_filter += applyPortFilters(filters)
    return query_filter


def applyHostsFilters(filters):
    query_filter = ""
    if not filters.down:
        query_filter += " AND hosts.status != 'down'"
    if not filters.up:
        query_filter += " AND hosts.status != 'up'"
    if not filters.checked:
        query_filter += " AND hosts.checked != 'True'"
    for word in filters.keywords:
        query_filter += (f" AND (hosts.ip LIKE '%{sanitise(word)}%'"
                         f" OR hosts.osMatch LIKE '%{sanitise(word)}%'"
                         f" OR hosts.hostname LIKE '%{sanitise(word)}%')")
    return query_filter


def applyPortFilters(filters):
    query_filter = ""
    if not filters.portopen:
        query_filter += " AND ports.state != 'open' AND ports.state != 'open|filtered'"
    if not filters.portclosed:
        query_filter += " AND ports.state != 'closed'"
    if not filters.portfiltered:
        query_filter += " AND ports.state != 'filtered' AND ports.state != 'open|filtered'"
    if not filters.tcp:
        query_filter += " AND ports.protocol != 'tcp'"
    if not filters.udp:
        query_filter += " AND ports.protocol != 'udp'"
    return query_filter
