#!/bin/bash
# Install deps
echo "Updating Apt database..."
sudo apt-get update
sudo apt-get install -yqq build-essential libreadline-gplv2-dev libncursesw5-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev python3-dev libssl1.0-dev libjpeg62-turbo-dev libxml2-dev libxslt1-dev python-dev libnetfilter-queue-dev qt4-qmake libqt4-dev libsqlite3-dev zlib1g-dev
sudo apt-get install -yqq python-netlib 
