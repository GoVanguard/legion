#!/bin/bash

if [ ! -f "/mnt/c/Program Files (x86)/Nmap/nmap.exe" ]
then
    echo "Install Windows NMAP for NMAP support in WSL. Linux NMAP will not work."
    exit 1
fi

"/mnt/c/Program Files (x86)/Nmap/nmap.exe" "$@"
