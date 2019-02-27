#!/bin/bash

source ./deps/apt.sh

# Install deps
echo "Checking Apt..."
runAptGetUpdate

echo "Installing deps..."
apt-get -yqqq install nmap finger hydra nikto whatweb nbtscan nfs-common rpcbind smbclient sra-toolkit ldap-utils sslscan rwho medusa x11-apps cutycapt leafpad xvfb imagemagick eog hping3 -y
