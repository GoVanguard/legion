#!/bin/bash
export DISPLAY=localhost:0.0

if [ ! -f ".initialized" ]
then
    unameOutput=`uname -a`
    releaseOutput=`cat /etc/*release*` # | grep -i 'ubuntu' | wc -l
    echo "First run here. Let's try to automatically install all the dependancies..."
    mkdir tmp
    if [[ $unameOutput == *"Microsoft"* ]]
    then
        echo "Detected WSL (Windows Subsystem for Linux)"
        if [[ $releaseOutput == *"Ubuntu"* ]]
        then
            echo "Detected Ubuntu on WSL"
            ./deps/ubuntu-wsl.sh
            touch .initialized
        else
            echo "Not Ubuntu. Install deps manually for now"
            touch .initialized
            exit 0
        fi
    else
        echo "Detected Linux"
        if [[ $releaseOutput == *"Ubuntu"* ]]
        then
            echo "Detected Ubuntu"
            ./deps/ubuntu.sh
            touch .initialized
        else
            echo "Not Ubuntu. Install deps manually for now"
            touch .initialized
            exit 0
        fi
    fi
fi

python3 legion.py
