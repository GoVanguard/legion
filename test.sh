#!/bin/bash

unameOutput=`uname -a`
releaseOutput=`cat /etc/os-release`
releaseName="?"
releaseVersion="?"
wslEnv=""

# Detect WSL and enable XForwaridng to Xming
if [[ $unameOutput == *"Microsoft"* ]]
then
    export DISPLAY=localhost:0.0
    wslEnv="on WSL"
fi

if [ ! -f ".initialized" ] | [ -f ".justcloned" ]
then
    if [[ $releaseOutput == *"Ubuntu"* ]]
    then
        releaseName="Ubuntu"
        if [[ $releaseOutput == *"16."* ]]
        then
            releaseVersion="16"
        elif [[ $releaseOutput == *"18."* ]]
        then
            releaseVersion="18"
        fi
    elif [[ $releaseOutput == *"Kali"* ]]
    then
        releaseName="Kali"
        if [[ $releaseOutput == *"2018"* ]]
        then
            releaseVersion="2018"
        elif [[ $releaseOutput == *"2016."* ]]
        then
            releaseVersion="2016"
        fi
    else
        releaseName="something unsupported"
    fi
    echo "Detected ${releaseName} ${releaseVersion} ${wslEnv}"
fi
