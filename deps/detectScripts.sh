#!/bin/bash

echo "Checking for additional Sparta scripts..."
curPath=`pwd`

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

if [ -a scripts/installDeps.sh ]
  then
    echo "installDeps.sh is already installed"
else
  wget -v -P scripts/ https://raw.githubusercontent.com/GoVanguard/sparta-scripts/master/installDeps.sh
fi

if [ -a scripts/snmpcheck.rb ]
  then
    echo "snmpcheck.rb is already installed"
else
  wget -v -P scripts/ https://raw.githubusercontent.com/GoVanguard/sparta-scripts/master/snmpcheck.rb
fi

if [ -a scripts/smtp-user-enum.pl ]
  then
    echo "smtp-user-enum.pl is already installed"
else
  wget -v -P scripts/ https://raw.githubusercontent.com/GoVanguard/sparta-scripts/master/smtp-user-enum.pl
fi

if [ -a scripts/CloudFail/cloudfail.py ]
  then
    echo "Cloudfail has been found"
else
  git clone https://github.com/m0rtem/CloudFail.git scripts/CloudFail
fi

if [ -a scripts/AutoSploit/autosploit.py ]
  then
    echo "AutoSploit is already installed"
else
  git clone https://github.com/NullArray/AutoSploit.git scripts/AutoSploit
fi

if [ ! -f ".initialized" ]
  then
    scripts/installDeps.sh
fi

cd ${curPath}
