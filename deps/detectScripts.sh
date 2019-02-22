#!/bin/bash

echo "Checking for additional Sparta scripts..."
echo $(pwd)
if [ -a scripts/smbenum.sh ]
  then
    echo "smbenum.sh is already installed"
else
  wget -v -P scripts/ https://raw.githubusercontent.com/GoVanguard/sparta-scripts/master/smbenum.sh
fi

if [ -a scripts/snmpbrute.py ]
  then
    echo "snmpbrute.py is already installed"
else
  wget -v -P scripts/ https://raw.githubusercontent.com/GoVanguard/sparta-scripts/master/snmpbrute.py
fi

if [ -a scripts/ms08-067_check.py ]
  then
    echo "ms08-067_check.py is already installed"
else
  wget -v -P scripts/ https://raw.githubusercontent.com/GoVanguard/sparta-scripts/master/ms08-067_check.py
fi

if [ -a scripts/rdp-sec-check.pl ]
  then
    echo "rdp-sec-check.pl is already installed"
else
  wget -v -P scripts/ https://raw.githubusercontent.com/GoVanguard/sparta-scripts/master/rdp-sec-check.pl
fi

if [ -a scripts/ndr.py ]
  then
    echo "ndr.py is already installed"
else
  wget -v -P scripts/ https://raw.githubusercontent.com/GoVanguard/sparta-scripts/master/ndr.py  
fi
