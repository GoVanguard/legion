![alt tag](https://github.com/GoVanguard/legion/blob/master/images/LegionBanner.png)
[![Build Status](https://travis-ci.com/GoVanguard/legion.svg?branch=master)](https://travis-ci.com/GoVanguard/legion)
[![Known Vulnerabilities](https://snyk.io/test/github/GoVanguard/legion/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/GoVanguard/legion?targetFile=requirements.txt)
[![Maintainability](https://api.codeclimate.com/v1/badges/4e33e52aab8f49cdcd02/maintainability)](https://codeclimate.com/github/GoVanguard/legion/maintainability)
[![Analytics](https://ga-beacon-gvit.appspot.com/UA-126307374-3/govanguard/legion)](https://github.com/GoVanguard/legion)



## ABOUT
Legion, a fork of SECFORCE's Sparta, is an open source, easy-to-use, super-extensible and semi-automated network penetration testing tool that aids in discovery, reconnaissance and exploitation of information systems. 
[Legion](https://govanguard.io/legion) is developed and maintained by [GoVanguard](https://govanguard.io). More information about Legion, including the [product roadmap](https://govanguard.io/legion), can be found on it's product page at [https://GoVanguard.io/legion](https://govanguard.io/legion).

### FEATURES
* Automatic recon and scanning with NMAP, whataweb, nikto, Vulners, Hydra, SMBenum, dirbuster, sslyzer, webslayer and more (with almost 100 auto-scheduled scripts)
* Easy to use graphical interface with rich context menus and panels that allow pentesters to quickly find and exploit attack vectors on hosts
* Modular functionality allows users to easily customize Legion and automatically call their own scripts/tools
* Highly customizable stage scanning for ninja-like IPS evasion
* Automatic detection of CPEs (Common Platform Enumeration) and CVEs (Common Vulnerabilities and Exposures)
* Realtime autosaving of project results and tasks

### NOTABLE CHANGES FROM SPARTA
* Refactored from Python 2.7 to Python 3.6 and the elimination of depreciated and unmaintained libraries
* Upgraded to PyQT5, increased responsiveness, less buggy, more intuitive GUI that includes features like:
   * Task completion estimates
   * 1-Click scan lists of ips, hostnames and CIDR subnets
   * Ability to purge results, rescan hosts and delete hosts
   * Granual NMAP scanning options
* Support for hostname resolution and scanning of vhosts/sni hosts
* Revise process queuing and execution routines for increased app reliability and performance
* Simplification of installation with dependency resolution and installation routines
* Realtime project autosaving so in the event some goes wrong, you will not loose any progress!
* Docker container deployment option
* Supported by a highly active development team

### GIF DEMO 
![](https://govanguard.io/wp-content/uploads/2019/02/LegionDemo.gif)

## INSTALLATION

### TRADITIONAL METHOD
Assumes Ubuntu, Kali or Parrot Linux is being used with Python 3.6 installed.
Other dependencies should automatically be installed. Within Terminal:
```
git clone https://github.com/GoVanguard/legion.git
cd legion
sudo chmod +x startLegion.sh
sudo ./startLegion.sh
```
### DOCKER METHOD
------
Assumes Docker and Xauthority are installed. Within Terminal:
```
git clone https://github.com/GoVanguard/legion.git
cd legion/docker
sudo chmod +x runIt.sh
sudo ./runIt.sh
```

## LICENSE
Legion is licensed under the GNU General Public License v3.0. Take a look at the [LICENSE](https://github.com/GoVanguard/legion/blob/master/LICENSE) for more information.

## ATTRIBUTION
* Refactored Python 3.6+ codebase, added feature set and ongoing development of Legion is credited to [GoVanguard](https://govanguard.io)
* The initial Sparta Python 2.7 codebase and application design is credited SECFORCE.
* Several additional PortActions, PortTerminalActions and SchedulerSettings are credited to batmancrew.
* The nmap XML output parsing engine was largely based on code by yunshu, modified by ketchup and modified SECFORCE.
* ms08-067_check script used by smbenum.sh is credited to Bernardo Damele A.G.
* Legion relies heavily on nmap, hydra, python, PyQt, SQLAlchemy and many other tools and technologies so we would like to thank all of the people involved in the creation of those.
