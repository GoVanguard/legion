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
    echo "Python 3.6 or 3.7 found!"
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
    echo "Python 3.6 or 3.7 found!"
    echo "Python3: ${PYTHON3BIN}"
    echo "PIP3: ${PIP3BIN}"
    exit 0
fi

source ./deps/detectPython.sh

if [[ ${PYTHON3BIN} == "Missing" ]] | [[ ${PIP3BIN} == "Missing" ]] | [[ -z "${PYTHON3BIN}" ]] | [[ -z "${PIP3BIN}" ]]
then
    echo "Everything went wrong trying to get python 3.6 or 3.7 setup. Please do this manually."
    echo "Python3: ${PYTHON3BIN}"
    echo "PIP3: ${PIP3BIN}"
    exit 1
else
    echo "Python 3.6 or 3.7 found!"
    echo "Python3: ${PYTHON3BIN}"
    echo "PIP3: ${PIP3BIN}"
    exit 0
fi
