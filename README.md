LEGION 0.2.1 (https://govanguard.io)
==

## Authors:
Shane Scott

## About legion
Based on Sparta by SECFORCE, legion is an information security tool that utilizes other effective tools as plugins, such as Nmap, netcat, Nikto, THC Hydra, smbenum, snmpcheck, dirbuster, and much more, and presents all of this information in a nice GUI. Now includes process monitoring to kill any hanging processes.

legion is written in Python 3, has been ported from PyQt4 to PyQt5, and no longer uses Elixir. 

Tested on Ubuntu, Parrot Security OS, and Windows Subsystem for Linux.

<img src="https://raw.githubusercontent.com/GoVanguard/legion/master/legion.png" width="500"></img>

## Installation
```
git clone https://github.com/GoVanguard/legion.git
```

## Recommended Python Version
legion supports Python 3.5+.

## Dependencies
* Ubuntu or variant or WSL (Windows Subsystem for Linux)
* Python 3.5+
* PyQT5
* SQLAlchemy
* six
* hydra
* nmap

## Usage
Run startLegion start script to launch legion. You may first have to grant yourself the permission to execute the script, which can either be done by right clicking it and selecting Properties and enabling Execute permissions, or:
```
chmod +x startLegion.sh
```

Then run startLegion:
```
./startLegion.sh
```
Note: Deps will be installed automatically.

## License
legion is licensed under the GNU General Public License v3.0.

## Credits
SECFORCE (Sparta)
