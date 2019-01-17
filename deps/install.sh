#!/bin/bash
cp *.sh /tmp
cd /tmp
chmod a+x *.sh
./installDeps.sh
./installPython36.sh
./installPythonLibs.sh
