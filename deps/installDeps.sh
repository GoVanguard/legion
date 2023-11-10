#!/bin/bash

source ./deps/apt.sh

# Install deps
## Disabled temporrily - Doesn't always detect apt-get update incomplete
 echo "Checking Apt..."
# runAptGetUpdate
apt-get update -m

echo "Installing deps..."
export DEBIAN_FRONTEND="noninteractive"
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install sra-toolkit sslscan
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install nmap finger hydra nikto nbtscan nfs-common rpcbind smbclient ldap-utils rwho x11-apps cutycapt featherpad xvfb imagemagick eog hping3 sqlmap libqt5core5a python3-pip ruby perl urlscan git xsltproc hping3
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install libgl1-mesa-glx libegl-mesa0 libegl1 libxcb-cursor0 libxcb-icccm4 python3-xvfbwrapper python3-selenium phantomjs libxcb-image0  libxcb-keysyms1  libxcb-render-util0  libxcb-xkb1 libxkbcommon-x11-0
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install dnsmap
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install wapiti
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install python3-impacket
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install whatweb
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install medusa
#apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install postgresql postgresql-server-dev-all
