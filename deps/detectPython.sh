#!/bin/bash

testForPython=`python --version 2>&1`
testForPython2=`python3 --version 2>&1`
testForPython3=`python3.6 --version 2>&1`
testForPython37=`python3.7 --version 2>&1`
releaseOutput=`cat /etc/os-release`

if [[ ${releaseOutput} == *"Fedora"* ]]
	then
		if [[ $testForPython == *"3.7"* ]]; then
			pythonBin='python'
		elif [[ $testForPython2 == *"3.7"* ]]; then
			pythonBin='python3'
		elif [[ $testForPython3 == *"3.7"* ]] && [[ $testForPython3 != *"not found"* ]]; then
			pythonBin='python3.7'
		else
			pythonBin='Missing'
		fi

if [[ $testForPython == *"3.6"* ]]; then
    pythonBin='python'
elif [[ $testForPython2 == *"3.6"* ]]; then
    pythonBin='python3'
elif [[ $testForPython3 == *"3.6"* ]] && [[ $testForPython3 != *"not found"* ]]; then
    pythonBin='python3.6'
else
    pythonBin='Missing'
fi

#echo "Python 3.6 bin is ${pythonBin} ($(which ${pythonBin}))"

testForPip=`pip --version 2>&1`
testForPip2=`pip3 --version 2>&1`
testForPip3=`pip3.6 --version 2>&1`

if [[ $testForPip == *"3.6"* ]]; then
    pipBin='pip'
elif [[ $testForPip2 == *"3.6"* ]]; then
    pipBin='pip3'
elif [[ $testForPip3 == *"3.6"* ]] && [[ $testForPip3 != *"not found"* ]]; then
    pipBin='pip3.6'
else
    pipBin='Missing'
fi

#echo "Pip 3.6 bin is ${pipBin} ($(which ${pipBin}))"

export PYTHON3BIN=$(which ${pythonBin})
export PIP3BIN=$(which ${pipBin})
