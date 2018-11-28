#!/bin/bash
cd /tmp

# Setup Python3.5
wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tgz
tar xzf Python-3.6.6.tgz
cd Python-3.6.6/
./configure --enable-optimizations --enable-ipv6 --with-ensurepip=install
sudo make altinstall
