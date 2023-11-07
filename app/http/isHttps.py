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
import ssl


def defaultUserAgent() -> str:
    return "Mozilla/5.0 (X11; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0 Iceweasel/22.0"


def isHttps(ip, port) -> bool:
    from urllib.error import URLError
    try:
        from urllib.request import Request, urlopen
        headers = {"User-Agent": defaultUserAgent()}
        req = Request(f"https://{ip}:{port}", headers=headers)
        urlopen(req, timeout=5).read()
        return True
    except URLError as e:
        reason = str(e.reason)
        print("urlerror" + reason)
        if 'Forbidden' in reason or 'certificate verify failed' in reason:
            return True
        return False
    except ssl.CertificateError:
        print("ssl")
        return True
