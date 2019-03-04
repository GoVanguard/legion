#!/bin/bash

source ./deps/yum.sh

# Install deps
echo "Checking Yum..."
runYumGetUpdate

echo "Installing deps..."
yum install -y epel-release centos-release-scl python36-pip python36-devel nmap finger hydra nikto rpcbind sslscan rwho medusa CutyCapt eog hping3 python-sqlalchemy.x86_64 PyQt4 rh-python36-python-sqlalchemy.x86_64 python-impacket ruby perl
