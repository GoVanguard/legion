#!/bin/bash

source ./deps/yum.sh

releaseOutput=`cat /etc/os-release`

# Install deps
echo "Checking Yum..."
runYumGetUpdate

echo "Installing deps..."

if [[ ${releaseOutput} == *"CentOS"* ]]
	then
		yum install -y epel-release centos-release-scl git python36-pip python36-devel nmap finger hydra nikto rpcbind sslscan rwho medusa CutyCapt eog hping3 python-sqlalchemy.x86_64 PyQt4 rh-python36-python-sqlalchemy.x86_64 python-impacket ruby perl nfs-utils samba-client openldap xorg-x11-apps xorg-x11-server-Xvfb
elif [[ ${releaseOutput} == *"Fedora"* ]]
	then
		dnf install -y git python-sqlalchemy python3-sqlalchemy nmap finger hydra nikto rpcbind sslscan rwho medusa CutyCapt eog hping3 PyQt4 python-impacket ruby perl nfs-utils samba-client openldap xorg-x11-apps xorg-x11-server-Xvfb
else
	yum install -y git python36-pip python36-devel nmap finger hydra nikto rpcbind sslscan rwho medusa CutyCapt eog hping3 python-sqlalchemy.x86_64 PyQt4 rh-python36-python-sqlalchemy.x86_64 python-impacket ruby perl nfs-utils samba-client openldap xorg-x11-apps xorg-x11-server-Xvfb
fi 

if [ -a /usr/bin/whatweb ]
  then
    echo "whatweb is already installed"
else
  git clone https://github.com/urbanadventurer/WhatWeb.git scripts/whatweb
  cd scripts/whatweb
  make
  cd ../../
fi

if [ -a /usr/bin/nbtscan ]
  then
    echo "nbtscan is already installed"
else
  wget -v -P scripts/ http://www.inetcat.org/software/nbtscan_1.5.1.tar.gz --header "Referer: http://www.inetcat.org/software/nbtscan.html" --header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0"
  cd scripts
  tar -xvf nbtscan_1.5.1.tar.gz
  cd nbtscan-1.5.1a
  make
  cd ../
  rm nbtscan_1.5.1.tar.gz
  cd ../
fi

if [ -a /usr/bin/test-sra ]
  then
    echo "sra-toolkit is already installed"
else
  wget -v -P scripts/ https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/2.9.4-1/sratoolkit.2.9.4-1-centos_linux64.tar.gz
  cd scripts
  tar -xvf sratoolkit.current-centos_linux64.tar.gz
  cd sratoolkit.2.9.4-1-centos_linux64
  cd ../
  rm sratoolkit.current-centos_linux64.tar.gz
  cd ../deps
fi

if [ -a /usr/bin/leafpad ]
  then
    echo "Leafpad is already installed"
else
  wget -v -P scripts/ http://savannah.nongnu.org/download/leafpad/leafpad-0.8.17.tar.gz
  cd scripts
  tar -xvf leafpad-0.8.17.tar.gz
  cd leafpad-0.8.17
  ./configure
  make
  make install-strip
  cd ../
  rm leafpad-0.8.17.tar.gz
  cd ../
fi 

if [ -a /usr/bin/imagemagick ]
  then
    echo "ImageMagick is already installed"
else
  wget -v "ftp://ftp.imagemagick.org/pub/ImageMagick/linux/CentOS/x86_64/ImageMagick-7.0.8-32.x86_64.rpm"
  wget -v "ftp://ftp.imagemagick.org/pub/ImageMagick/linux/CentOS/x86_64/ImageMagick-libs-7.0.8-32.x86_64.rpm"
  rpm -Uvh ImageMagick-7.0.8-32.x86_64.rpm
  rpm -Uvh ImageMagick-libs-7.0.8-32.x86_64.rpm
  rm ImageMagick-7.0.8-32.x86_64.rpm
  rm ImageMagick-libs-7.0.8-32.x86_64.rpm
fi 