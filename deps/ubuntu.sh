#!/bin/bash
echo "Updating Apt database..."
apt-get -qq update
echo "Installing python dependancies..."
apt-get -qq install python3-pyqt5 python3-pyqt4 python3-pyside.qtwebkit python3-sqlalchemy* -y
echo "Installing external binaryies and application dependancies..."
apt-get -qq install finger hydra nikto whatweb nbtscan nfs-common rpcbind smbclient sra-toolkit ldap-utils sslscan rwho medusa x11-apps cutycapt leafpad -y
