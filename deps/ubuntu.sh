#!/bin/bash
cp *.sh /tmp
cd /tmp
chmod a+x *.sh
./installDeps.sh
test=`python3.6 --version`

if [[ $test != "Python 3.6.6" ]]
then
    echo "Installing python3.6.6..."
    ./installPython36.sh
fi
./installPythonLibs.sh
echo "Installing external binaryies and application dependancies..."
apt-get -qq install finger hydra nikto whatweb nbtscan nfs-common rpcbind smbclient sra-toolkit ldap-utils sslscan rwho medusa x11-apps cutycapt leafpad xvfb gksu -y
echo "Installing Python Libraries..."
./installPythonLibs.sh
