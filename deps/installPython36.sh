#!/bin/bash

source ./detectPython.sh

if [[ ${PYTHON3BIN} == "Missing" ]] | [[ ${PIP3BIN} == "Missing" ]]
then
    echo "Installing python3.6 from APT..."
    echo "Updating Apt database..."
    sudo apt-get update -yqq 2>&1 > /dev/null
    echo "Install Python3.6 and Pip3.6 from APT..."
    sudo apt-get install -yqq python3 python3-pip python-netlib 2>&1 > /dev/null
else
    echo "Python3.6 found!"
    echo "Python 3.6: ${PYTHON3BIN}"
    echo "PIP 3.6: ${PIP3BIN}"
    exit 0
fi

source ./detectPython.sh

if [[ ${PYTHON3BIN} == "Missing" ]] | [[ ${PIP3BIN} == "Missing" ]]
then
    echo "Installing python3.6 from source..."
    sudo ./buildPython36.sh
else
    echo "Python3.6 found!"
    echo "Python 3.6: ${PYTHON3BIN}"
    echo "PIP 3.6: ${PIP3BIN}"
    exit 0
fi

source ./detectPython.sh

if [[ ${PYTHON3BIN} == "Missing" ]] | [[ ${PIP3BIN} == "Missing" ]]
then
    echo "Everything went wrong trying to get python3.6 setup. Please do this manually."
    echo "Python 3.6: ${PYTHON3BIN}"
    echo "PIP 3.6: ${PIP3BIN}"
    exit 1
else
    echo "Python3.6 found!"
    echo "Python 3.6: ${PYTHON3BIN}"
    echo "PIP 3.6: ${PIP3BIN}"
    exit 0
fi
