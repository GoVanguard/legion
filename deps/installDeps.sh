#!/bin/bash

source ./deps/apt.sh

# Install deps
## Disabled temporarily - Doesn't always detect apt-get update incomplete
echo "Checking Apt..."
# runAptGetUpdate
apt-get update -m

echo "Installing deps..."
export DEBIAN_FRONTEND="noninteractive"
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install curl nmap finger hydra nikto nbtscan nfs-common rpcbind smbclient sra-toolkit ldap-utils sslscan rwho x11-apps cutycapt leafpad xvfb imagemagick eog hping3 sqlmap libqt5core5a python-pip ruby perl urlscan git xsltproc
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install libgl1-mesa-glx
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install dnsmap
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install wapiti
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install python-impacket
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install whatweb
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install medusa
apt-get -yqqqm --allow-unauthenticated -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install postgresql postgresql-server-dev-all
