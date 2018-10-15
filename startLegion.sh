#!/bin/bash

unameOutput=`uname -a`

# Detect WSL and enable XForwaridng to Xming
if [[ $unameOutput == *"Microsoft"* ]]
then
    export DISPLAY=localhost:0.0
fi

if [ ! -f ".initialized" ] | [ -f ".justcloned" ]
then
    releaseOutput=`cat /etc/*release*` # | grep -i 'ubuntu' | wc -l
    echo "First run here (or you did a pull to update). Let's try to automatically install all the dependancies..."
    if [ ! -d "tmp" ]
    then
        mkdir tmp
    fi
    if [[ $unameOutput == *"Microsoft"* ]]
    then
        echo "Detected WSL (Windows Subsystem for Linux)"
        if [[ $releaseOutput == *"Ubuntu"* ]]
        then
            echo "Detected Ubuntu on WSL"
            ./deps/ubuntu-wsl.sh
            touch .initialized
            rm .justcloned -f
        else
            echo "Not Ubuntu. Install deps manually for now"
            touch .initialized
            rm .justcloned -f
            exit 0
        fi
    else
        echo "Detected Linux"
        if [[ $releaseOutput == *"Ubuntu"* ]]
        then
            echo "Detected Ubuntu"
            ./deps/ubuntu.sh
            touch .initialized
            rm .justcloned -f
        elif [[ $releaseOutput == *"Parrot"* ]]
        then
            ./deps/ubuntu.sh
            touch .initialized
            rm .justcloned -f
        else
            echo "Not Ubuntu. Install deps manually for now"
            touch .initialized
            rm .justcloned -f
            exit 0
        fi
    fi
fi

gksu python3 legion.py
