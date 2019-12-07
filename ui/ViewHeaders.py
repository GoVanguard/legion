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

hostTableHeaders = ["Id", "OS", "Accuracy", "Host", "IPv4", "IPv6", "Mac", "Status", "Hostname", "Vendor", "Uptime",
                    "Lastboot", "Distance", "CheckedHost", "State", "Count", "Closed"]

serviceTableHeaders = ["Host", "Port", "Port", "Protocol", "State", "HostId", "ServiceId", "Name", "Product", "Version",
                       "Extrainfo", "Fingerprint"]

serviceNamesTableHeaders = ["Name"]

scriptsTableHeaders = ["Id", "Script", "Port", "Protocol"]

cvesTableHeaders = ["CVE Id", "CVSS Score", "Product", "Version", "CVE URL", "Source", "ExploitDb ID", "ExploitDb",
                    "ExploitDb URL"]

processTableHeaders = ["Progress", "Display", "Elapsed", "Est. Remaining", "Pid", "Name", "Tool", "Host", "Port",
                       "Protocol", "Command", "Start time", "End time", "OutputFile", "Output", "Status", "Closed"]

toolsTableHeaders = ["Progress", "Display", "Elapsed", "Est. Remaining", "Pid", "Name", "Tool", "Host", "Port",
                     "Protocol", "Command", "Start time", "End time", "OutputFile", "Output", "Status", "Closed"]

toolHostsTableHeaders = ["Progress", "Display", "Elapsed", "Est. Remaining", "Pid", "Name", "Tool", "Host", "Port",
                         "Protocol", "Command", "Start time", "End time", "OutputFile", "Output", "Status", "Closed"]
