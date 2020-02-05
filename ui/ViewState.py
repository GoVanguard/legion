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
from app.auxiliary import Filters


# Defines the state of the UI at any given moment
# Defaults are the initial state of the UI
class ViewState:
    # Indicator if any changes have happened since last save (default: False [no changes])
    dirty: bool = False
    # Indicator if 'Save As..' dialog should be used (default: True)
    firstSave = True
    # Indicator of which tabs should be displayed for each host (default: empty dictionary)
    hostTabs = dict()
    # Indicator of the numbering of the bruteforce tabs, incremented when a new tab is added (default: 1)
    bruteTabCount = 1
    # to choose what to display in each panel (default: base filters)
    filters = Filters()
    # Indicator of which host was clicked last (default: None)
    lastHostIdClicked = ''
    # Indicator of which IP Address was clicked on last (default: None)
    ip_clicked = ''
    # Indicator of which Service was clicked on last (default: None)
    service_clicked = ''
    # Indicator of which Tool was clicked on last (default: None)
    tool_clicked = ''
    # Indicator of which script was clicked on last (default: None)
    script_clicked = ''
    # Indicator of which tool host was clicked on last (default: None)
    tool_host_clicked = ''
    # these variables indicate that the corresponding table needs to be updated.
    # 'lazy' means we only update a table at the last possible minute - before the user needs to see it
    lazy_update_hosts = False
    lazy_update_services = False
    lazy_update_tools = False
    # Indicator if a context menu is showing (important to avoid disrupting the user) (default: False)
    menuVisible = False

