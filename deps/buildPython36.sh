#!/bin/bash
cd /tmp

# Install deps
echo "Updating Apt database..."
sudo apt-get update -yqq 2>&1 > /dev/null
sudo apt-get install -yqq build-essential libreadline-gplv2-dev libncursesw5-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev python3-dev libssl1.0-dev libjpeg62-turbo-dev libxml2-dev libxslt1-dev python-dev libnetfilter-queue-dev qt4-qmake libqt4-dev libsqlite3-dev zlib1g-dev 2>&1 > /dev/null

# Setup Python3.6
wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tgz
tar xzf Python-3.6.6.tgz
cd Python-3.6.6/
./configure --enable-optimizations --enable-ipv6 --with-ensurepip=install
sudo make altinstall
