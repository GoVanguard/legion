#!/bin/bash

source ./deps/yum.sh

# Install deps
echo "Checking Yum..."
runYumGetUpdate

echo "Please install the following deps: centos-release-scl nmap finger hydra nikto whatweb nbtscan nfs-common rpcbind smbclient sra-toolkit ldap-utils sslscan rwho medusa x11-apps cutycapt leafpad xvfb imagemagick eog hping3 python-impacket ruby perl"
