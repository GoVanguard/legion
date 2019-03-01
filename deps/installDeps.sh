#!/bin/bash

source ./deps/apt.sh

# Install deps
echo "Checking Apt..."
runAptGetUpdate

echo "Installing deps..."
DEBIAN_FRONTEND="noninteractive" apt-get -yqqq --allow-unauthenticated --force-yes -o DPkg::Options::="--force-overwrite" -o DPkg::Options::="--force-confdef" install nmap finger hydra nikto whatweb nbtscan nfs-common rpcbind smbclient sra-toolkit ldap-utils sslscan rwho medusa x11-apps cutycapt leafpad xvfb imagemagick eog hping3 python-impacket ruby perl
