#!/bin/bash

source ./deps/apt.sh

# Install deps
echo "Checking Apt..."
runAptGetUpdate

echo "Installing deps..."
sudo apt-get install -yqq python-netlib 2>&1 > /dev/null
