#!/bin/bash

source ./deps/apt.sh

# Install deps
## Disabled temporrily - Doesn't always detect apt-get update incomplete
 echo "Checking Apt..."
# runAptGetUpdate
apt-get update -m

echo "Installing deps..."
DEBIAN_FRONTEND="noninteractive" apt-get -yqqqm --allow-unauthenticated --force-yes -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install nmap finger hydra nikto nbtscan nfs-common rpcbind smbclient sra-toolkit ldap-utils sslscan rwho x11-apps cutycapt leafpad xvfb imagemagick eog hping3 sqlmap theharvester wapiti libqt5core5a python-pip ruby perl urlscan git xsltproc

DEBIAN_FRONTEND="noninteractive" apt-get -yqqqm --allow-unauthenticated --force-yes -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install dnsmap
DEBIAN_FRONTEND="noninteractive" apt-get -yqqqm --allow-unauthenticated --force-yes -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install wapiti
DEBIAN_FRONTEND="noninteractive" apt-get -yqqqm --allow-unauthenticated --force-yes -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install python-impacket
DEBIAN_FRONTEND="noninteractive" apt-get -yqqqm --allow-unauthenticated --force-yes -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install whatweb
DEBIAN_FRONTEND="noninteractive" apt-get -yqqqm --allow-unauthenticated --force-yes -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install medusa
