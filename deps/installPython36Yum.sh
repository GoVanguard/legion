#!/bin/bash

source ./deps/yum.sh
source ./deps/detectPython.sh

releaseOutput=`cat /etc/os-release`


if [[ ${PYTHON3BIN} == "Missing" ]] | [[ ${PIP3BIN} == "Missing" ]] | [[ -z "${PYTHON3BIN}" ]] | [[ -z "${PIP3BIN}" ]]
then
    echo "Installing python3.6 from YUM..."
    echo "Checking Yum..."
    runYumGetUpdate
    echo "Install Python3.6 and Pip3.6 from YUM..."
	if [[ ${releaseOutput} == *"CentOS"* ]]
	then
		yum install -y rh-python36
		scl enable rh-python36 bash
		yum groupinstall 'Development Tools'
	else
		yum install -y python36
	fi
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
