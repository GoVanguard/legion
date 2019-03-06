#!/bin/bash

chmod a+x ./deps/*.sh

./deps/installDeps.sh
./deps/installPython36.sh

source ./deps/detectPython.sh

echo "Installing Python Libraries..."
./deps/installPythonLibs.sh

echo "WSL Setup..."
./deps/setupWsl.sh

echo "renameat2() work around for libQt5Core.so.5 and cutycapt"
strip --remove-section=.note.ABI-tag  /usr/lib/x86_64-linux-gnu/libQt5Core.so.5
