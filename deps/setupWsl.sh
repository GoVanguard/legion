#!/bin/bash

# Setup linked Windows NMAP
if [ -f "/usr/bin/nmap" ]
then
    nmapBinCheck=$(cat /usr/bin/nmap | grep -c "nmap.exe")
else
    nmapBinCheck=1
fi

if [ ! -f "/sbin/nmap" ] | [ ${nmapBinCheck} -eq 0 ]
then
    echo "Installing Link to Windows NMAP..."
    today=$(date +%s)
    mv /usr/bin/nmap /usr/bin/nmap_lin_${today}
    cp ./deps/nmap-wsl.sh /sbin/nmap
    chmod a+x /sbin/nmap
    if [ ! -f "/sbin/nmap" ]
    then
        ln -s /sbin/nmap /usr/bin/nmap
    fi
else
    echo "Link to Windows NMAP already exists; skipping."
fi
