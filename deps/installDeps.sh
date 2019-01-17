#!/bin/bash

# Install deps
echo "Installing deps..."
sudo apt-get install -yqq python3 python3-pip python-netlib 2>&1 > /dev/null
