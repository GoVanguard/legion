#!/bin/bash

source ./deps/apt.sh
source ./deps/detectPython.sh

if [[ ${PYTHON3BIN} == "Missing" ]] | [[ ${PIP3BIN} == "Missing" ]] | [[ -z "${PYTHON3BIN}" ]] | [[ -z "${PIP3BIN}" ]]
then
    echo "Installing python3.6 from APT..."
    echo "Checking Apt..."
    runAptGetUpdate
    echo "Install Python3.6 and Pip3.6 from APT..."
    apt-get install -yqqqq python3 python3-pip
else
    echo "Python3.6 found!"
    echo "Python 3.6: ${PYTHON3BIN}"
    echo "PIP 3.6: ${PIP3BIN}"
    exit 0
fi

source ./deps/detectPython.sh

if [[ ${PYTHON3BIN} == "Missing" ]] | [[ ${PIP3BIN} == "Missing" ]] | [[ -z "${PYTHON3BIN}" ]] | [[ -z "${PIP3BIN}" ]]
then
    echo "Installing python3.6 from source..."
    sudo ./deps/buildPython36.sh
else
    echo "Python3.6 found!"
    echo "Python 3.6: ${PYTHON3BIN}"
    echo "PIP 3.6: ${PIP3BIN}"
    exit 0
fi

source ./deps/detectPython.sh

if [[ ${PYTHON3BIN} == "Missing" ]] | [[ ${PIP3BIN} == "Missing" ]] | [[ -z "${PYTHON3BIN}" ]] | [[ -z "${PIP3BIN}" ]]
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
