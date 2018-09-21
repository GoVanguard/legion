#!/bin/bash
./deps/ubuntu.sh

# Setup linked Windows NMAP

if [ ! -f "/sbin/nmap" ]
then
    echo "Installing Link to Windows NMAP..."
    mv /usr/bin/nmap /usr/bin/nmap_lin
    cp ./deps/nmap-wsl.sh /sbin/nmap
    chmod a+x /sbin/nmap
    ln -s /sbin/nmap /usr/bin/nmap
else
    echo "Link to Windows NMAP already exists; skipping."
fi
