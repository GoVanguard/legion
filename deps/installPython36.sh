#!/bin/bash

source ./deps/apt.sh
source ./deps/detectPython.sh

if [[ ${PYTHON3BIN} == "Missing" ]] | [[ ${PIP3BIN} == "Missing" ]] | [[ -z "${PYTHON3BIN}" ]] | [[ -z "${PIP3BIN}" ]]
then
    echo "Installing python 3.6 or 3.7 from APT..."
    echo "Checking Apt..."
    runAptGetUpdate
    echo "Install Python 3.6 or 3.7 and Pip 3.6 or 3.7 from APT..."
    apt-get install -yqqqq python3 python3-pip
else
    if [[ ${PYTHON3BIN} == *"3.7"* ]]; then
        echo "Python 3.7 found!"
    elif [[ ${PYTHON3BIN} == *"3.6"* ]]; then
        echo "Python 3.6 found!"
    elif [[ ${PYTHON3BIN} == *"3.8"* ]]; then
        echo "Python 3.8 found!"
    fi
    if [[ ${PIP3BIN} == *"3.7"* ]]; then
        echo "Pip 3.7 found!"
    elif [[ ${PIP3BIN} == *"3.6"* ]]; then
        echo "Pip 3.6 found!"
    elif [[ ${PIP3BIN} == *"3.8"* ]]; then
        echo "Pip 3.8 found!"
    fi
        
    echo "Python3: ${PYTHON3BIN}"
    echo "PIP3: ${PIP3BIN}"
    exit 0
fi

source ./deps/detectPython.sh

if [[ ${PYTHON3BIN} == "Missing" ]] | [[ ${PIP3BIN} == "Missing" ]] | [[ -z "${PYTHON3BIN}" ]] | [[ -z "${PIP3BIN}" ]]
then
    echo "Installing python3.6 from source..."
    sudo ./deps/buildPython36.sh
else
    echo "Python 3.6 or newer found!"
    echo "Python3: ${PYTHON3BIN}"
    echo "PIP3: ${PIP3BIN}"
    exit 0
fi

source ./deps/detectPython.sh

if [[ ${PYTHON3BIN} == "Missing" ]] | [[ ${PIP3BIN} == "Missing" ]] | [[ -z "${PYTHON3BIN}" ]] | [[ -z "${PIP3BIN}" ]]
then
    echo "Everything went wrong trying to get python 3.6 or newer setup. Please do this manually."
    echo "Python3: ${PYTHON3BIN}"
    echo "PIP3: ${PIP3BIN}"
    exit 1
else
    echo "Python 3.6 or newer found!"
    echo "Python3: ${PYTHON3BIN}"
    echo "PIP3: ${PIP3BIN}"
    exit 0
fi
