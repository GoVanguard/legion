#!/bin/bash

source ./deps/apt.sh

# Install deps
## Disabled temporrily - Doesn't always detect apt-get update incomplete
 echo "Checking Apt..."
# runAptGetUpdate
apt-get update -m

echo "Installing deps..."
DEBIAN_FRONTEND="noninteractive" apt-get -yqqq --allow-unauthenticated --force-yes -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install nmap finger hydra nikto whatweb nbtscan nfs-common rpcbind smbclient sra-toolkit ldap-utils sslscan rwho medusa x11-apps cutycapt leafpad xvfb imagemagick eog hping3 sqlmap wapiti libqt5core5a python-pip python-impacket ruby perl dnsmap urlscan git
