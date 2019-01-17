#!/bin/bash

source ./deps/detectPython.sh

cp ./deps/*.sh /tmp
cp ./requirements.txt /tmp -f
cd /tmp
chmod a+x *.sh

./installDeps.sh
./installPython36.sh

echo "Installing external binaryies and application dependancies..."
apt-get -yqqq install finger hydra nikto whatweb nbtscan nfs-common rpcbind smbclient sra-toolkit ldap-utils sslscan rwho medusa x11-apps cutycapt leafpad xvfb -y

echo "Installing Python Libraries..."
./installPythonLibs.sh
