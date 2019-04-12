#!/bin/bash

unameOutput=`uname -a`
releaseOutput=`cat /etc/os-release`
releaseName="?"
releaseVersion="?"
wslEnv=""

# Detect WSL and enable XForwaridng to Xming
if [[ ${unameOutput} == *"Microsoft"* ]]
then
    export DISPLAY=localhost:0.0
    wslEnv="WSL"
fi

# Figure Linux Version
if [[ ${releaseOutput} == *"Ubuntu"* ]]
then
    releaseName="Ubuntu"
    if [[ ${releaseOutput} == *"16."* ]]
    then
        releaseVersion="16"
    elif [[ ${releaseOutput} == *"18."* ]]
    then
        releaseVersion="18"
    fi
elif [[ ${releaseOutput} == *"Kali"* ]]
then
    releaseName="Kali"
    if [[ ${releaseOutput} == *"2019"* ]]
    then
        releaseVersion="2019"
    elif [[ ${releaseOutput} == *"2018"* ]]
    then
        releaseVersion="2018"
    elif [[ ${releaseOutput} == *"2016"* ]]
    then
        releaseVersion="2016"
    fi
elif [[ ${releaseOutput} == *"Parrot"* ]]
then
    releaseName="Parrot"
    if [[ ${releaseOutput} == *"4.5"* ]]
    then
        releaseVersion="4.5"
    elif [[ ${releaseOutput} == *"4.6"* ]]
    then
        releaseVersion="4.6"
    fi
else
    releaseName="Unknown"
    releaseVersion=""
fi

echo "Detected ${releaseName} ${releaseVersion} ${wslEnv}"
depInstaller="${releaseName}-${releaseVersion}${wslEnv}.sh"

export DEPINSTALLER=${depInstaller}
export OS_RELEASE=${releaseName}
export OS_RELEASE_VERSION=${releaseVersion}
export ISWSL=${wslEnv}
