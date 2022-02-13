#!/bin/bash

chmod a+x ./deps/*.sh

./deps/installDeps.sh

# Install dnsmap manually as Ubuntu versions earlier than 20.04 do not have dnsmap available in primary distro repositories.
curl -q -O http://archive.ubuntu.com/ubuntu/pool/universe/d/dnsmap/dnsmap_0.35-3_amd64.deb -o dnsmap_0.35-3_amd64.deb && \
  sudo dpkg -i dnsmap_0.35-3_amd64.deb && \
  rm dnsmap_0.35-3_amd64.deb

./deps/installPython36.sh

source ./deps/detectPython.sh

echo "Installing Python Libraries..."
./deps/installPythonLibs.sh

echo "WSL Setup..."
./deps/setupWsl.sh
