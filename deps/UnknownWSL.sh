#!/bin/bash

chmod a+x ./deps/*.sh

./deps/installDeps.sh
./deps/installPython36.sh

source ./deps/detectPython.sh

echo "Installing Python Libraries..."
./deps/installPythonLibs.sh

echo "WSL Setup..."
./deps/setupWsl.sh
