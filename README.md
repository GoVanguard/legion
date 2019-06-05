![alt tag](https://github.com/GoVanguard/legion/blob/master/images/LegionBanner.png)
[![Build Status](https://travis-ci.com/GoVanguard/legion.svg?branch=master)](https://travis-ci.com/GoVanguard/legion)
[![Known Vulnerabilities](https://snyk.io/test/github/GoVanguard/legion/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/GoVanguard/legion?targetFile=requirements.txt)
[![Maintainability](https://api.codeclimate.com/v1/badges/4e33e52aab8f49cdcd02/maintainability)](https://codeclimate.com/github/GoVanguard/legion/maintainability)
[![Analytics](https://ga-beacon-gvit.appspot.com/UA-126307374-3/legion/readme)](https://github.com/GoVanguard/legion)



## ABOUT
Legion, a fork of SECFORCE's Sparta, is an open source, easy-to-use, super-extensible and semi-automated network penetration testing framework that aids in discovery, reconnaissance and exploitation of information systems. 
[Legion](https://govanguard.io/legion) is developed and maintained by [GoVanguard](https://govanguard.io). More information about Legion, including the [roadmap](https://govanguard.io/legion), can be found on it's project page at [https://GoVanguard.io/legion](https://govanguard.io/legion).

### FEATURES
* Automatic recon and scanning with NMAP, whataweb, nikto, Vulners, Hydra, SMBenum, dirbuster, sslyzer, webslayer and more (with almost 100 auto-scheduled scripts)
* Easy to use graphical interface with rich context menus and panels that allow pentesters to quickly find and exploit attack vectors on hosts
* Modular functionality allows users to easily customize Legion and automatically call their own scripts/tools
* Highly customizable stage scanning for ninja-like IPS evasion
* Automatic detection of CPEs (Common Platform Enumeration) and CVEs (Common Vulnerabilities and Exposures)
* Ties CVEs to Exploits as detailed in Exploit-Database
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
It is preferable to use the docker image over a traditional installation. This is because of all the dependancy requirements and the complications that occur in environments which differ from a clean, non-default installation.

### DOCKER METHOD
------
Assumes Docker and Xauthority are installed.

Linux with local X11:
 - Within Terminal:
   ```
   git clone https://github.com/GoVanguard/legion.git
   cd legion/docker
   sudo chmod +x runIt.sh
   sudo ./runIt.sh
   ```

Linux with Remote X11:
 - Replace X.X.X.X with the IP of the remote running X11.
 - Within Terminal:
   ```
   git clone https://github.com/GoVanguard/legion.git
   cd legion/docker
   sudo chmod +x runIt.sh
   sudo ./runIt.sh X.X.X.X
   ```

Windows under WSL using Xming:
 - Replace X.X.X.X with the IP with which Xming has registered itself.
   - Right click Xming in system tray -> View log and see IP next to "XdmcpRegisterConnection: newAddress"
 - Within Terminal:
   ```
   git clone https://github.com/GoVanguard/legion.git
   cd legion/docker
   sudo chmod +x runIt.sh
   sudo ./runIt.sh X.X.X.X
   ```

Windows using Xming without WSL:
 - Why? Don't do this. :)

OSX using Glas:
 - Not yet in runIt.sh script.
 - Possible to setup using socat. See instructions here: https://kartoza.com/en/blog/how-to-run-a-linux-gui-application-on-osx-using-docker/

### TRADITIONAL METHOD
 - Please use the docker image where possible! It's becoming very difficult to support all the various platforms and their own quirks
 - Assumes Ubuntu, Kali or Parrot Linux is being used with Python 3.6 installed.
 - Within Terminal:
   ```
   git clone https://github.com/GoVanguard/legion.git
   cd legion
   sudo chmod +x startLegion.sh
   sudo ./startLegion.sh
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
