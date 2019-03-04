#!/bin/bash

source ./deps/yum.sh

# Install deps
echo "Checking Yum..."
runYumGetUpdate

echo "Installing deps..."
yum install -y epel-release centos-release-scl git python36-pip python36-devel nmap finger hydra nikto rpcbind sslscan rwho medusa CutyCapt eog hping3 python-sqlalchemy.x86_64 PyQt4 rh-python36-python-sqlalchemy.x86_64 python-impacket ruby perl nfs-utils samba-client openldap

if [ -a /usr/bin/whatweb ]
  then
    echo "whatweb is already installed"
else
  git clone https://github.com/urbanadventurer/WhatWeb.git ../scripts/whatweb
  cd ../scripts/whatweb
  make
  cd ../../deps/
fi

if [ -a /usr/bin/nbtscan ]
  then
    echo "nbtscan is already installed"
else
  wget -v -P ../scripts/ http://www.inetcat.org/software/nbtscan_1.5.1.tar.gz --header "Referer: http://www.inetcat.org/software/nbtscan.html" --header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0"
  cd ../scripts
  tar -xvf nbtscan_1.5.1.tar.gz
  cd nbtscan-1.5.1a
  make
  cd ../
  rm nbtscan_1.5.1.tar.gz
  cd ../deps
fi

if [ -a /usr/bin/test-sra ]
  then
    echo "sra-toolkit is already installed"
else
  wget -v -P ../scripts/ https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/2.9.4-1/sratoolkit.2.9.4-1-centos_linux64.tar.gz
  cd ../scripts
  tar -xvf sratoolkit.current-centos_linux64.tar.gz
  cd sratoolkit.2.9.4-1-centos_linux64
  cd ../
  
  rm sratoolkit.current-centos_linux64.tar.gz
  cd ../deps
fi 