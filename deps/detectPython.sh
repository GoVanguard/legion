#!/bin/bash

testForPython=`python --version 2>&1`
testForPython2=`python3 --version 2>&1`
testForPython3=`python3.6 --version 2>&1`
testForPython4=`python3.7 --version 2>&1`

if [[ $testForPython == *"3.6"* ]]; then
    pythonBin='python'
    pythonVersion='3.6'
elif [[ $testForPython == *"3.7"* ]]; then
    pythonBin='python'
    pythonVersion='3.7'
elif [[ $testForPython2 == *"3.6"* ]]; then
    pythonBin='python3'
    pythonVersion='3.6'
elif [[ $testForPython2 == *"3.7"* ]]; then
    pythonBin='python3'
    pythonVersion='3.7'
elif [[ $testForPython3 == *"3.6"* ]] && [[ $testForPython3 != *"not found"* ]]; then
    pythonBin='python3.6'
    pythonVersion='3.6'
elif [[ $testForPython4 == *"3.7"* ]] && [[ $testForPython4 != *"not found"* ]]; then
    pythonBin='python3.7'
    pythonVersion='3.7'
else
    pythonBin='Missing'
fi

testForPip=`pip --version 2>&1`
testForPip2=`pip3 --version 2>&1`
testForPip3=`pip3.6 --version 2>&1`
testForPip4=`pip3.7 --version 2>&1`

if [[ $testForPip == *"3.6"* ]]; then
    pipBin='pip'
    pipVersion=3.6
elif [[ $testForPip == *"3.7"* ]]; then
    pipBin='pip'
    pipVersion='3.7'
elif [[ $testForPip2 == *"3.6"* ]]; then
    pipBin='pip3'
    pipVersion='3.6'
elif [[ $testForPip2 == *"3.7"* ]]; then
    pipBin='pip3'
    pipVersion='3.7'
elif [[ $testForPip3 == *"3.6"* ]] && [[ $testForPip3 != *"not found"* ]]; then
    pipBin='pip3.6'
    pipVersion='3.6'
elif [[ $testForPip4 == *"3.7"* ]] && [[ $testForPip4 != *"not found"* ]]; then
    pipBin='pip3.7'
    pipVersion='3.7'
else
    pipBin='Missing'
fi

if [[ ${pythonVersion} == *"3.7"* ]] && [[ ${pipVersion} != *"3.7"* ]]; then
    case ${pipBin} in
        3.6)
            echo "Found Python 3.7 but no PIP 3.7. Let's try to use Python 3.6 instead, or locate PIP 3.7."
            if [[ $testForPython3 == *"3.6"* ]] && [[ $testForPython3 != *"not found"* ]]; then
                pythonBin='python3.6'
                pythonVersion='3.6'
            elif [[ $testForPython2 == *"3.6"* ]] && [[ $testForPython2 != *"not found"* ]]; then
                pythonBin='python3'
                pythonVersion='3.6'
            elif [[ $testForPython == *"3.6"* ]] && [[ $testForPython != *"not found"* ]]; then
                pythonBin='python'
                pythonVersion='3.6'
            elif [[ $testForPip4 == *"3.7"* ]] && [[ $testForPip4 != *"not found"* ]]; then
                pipBin='pip3.7'
                pipVersion='3.7'
            elif [[ $testForPip2 == *"3.7"* ]] && [[ $testForPip2 != *"not found"* ]]; then
                pipBin='pip3'
                pipVersion='3.7'
            elif [[ $testForPip == *"3.7"* ]] && [[ $testForPip != *"not found"* ]]; then
                pipBin='pip'
                pipVersion='3.7'
            else
                pipBin='Missing'
                echo "Python 3.7 is installed, however PIP 3.7 is not installed and neither is Python 3.6. Please install PIP 3.7."
            fi
            ;;
        3)
            if [[ ${pipBin} != *"3.6"* ]] && [[ ${pipBin} != *"3.7"* ]]; then
                if [[ ${pipVersion} == *"3.6"* ]]; then
                    echo "Found Python 3.7 but PIP 3.6. Let's try to use Python 3.6 instead, or switch to PIP 3.7."
                    if [[ $testForPython3 == *"3.6"* ]] && [[ $testForPython3 != *"not found"* ]]; then
                        pythonBin='python3.6'
                        pythonVersion='3.6'
                    elif [[ $testForPython2 == *"3.6"* ]] && [[ $testForPython2 != *"not found"* ]]; then
                        pythonBin='python3'
                        pythonVersion='3.6'
                    elif [[ $testForPython == *"3.6"* ]] && [[ $testForPython != *"not found"* ]]; then
                        pythonBin='python'
                        pythonVersion='3.6'
                    else
                        echo "Python 3.6 is not installed yet PIP 3.6 is. Let's look for PIP 3.7."
                        if [[ $testForPip4 == *"3.7"* ]] && [[ $testForPip4 != *"not found"* ]]; then
                            pipBin='pip3.7'
                            pipVersion='3.7'
                        elif [[ $testForPip2 == *"3.7"* ]] && [[ $testForPip2 != *"not found"* ]]; then
                            pipBin='pip3'
                            pipVersion='3.7'
                        elif [[ $testForPip == *"3.7"* ]] && [[ $testForPip != *"not found"* ]]; then
                            pipBin='pip'
                            pipVersion='3.7'
                        else
                            echo "PIP 3.7 not found either. Please install PIP 3.7."
                            pipBin='Missing'
                        fi
                    fi 
                else
                    pipBin='Missing'
                    echo "Python 3.7 is installed, but neither PIP 3.7 nor PIP 3.6 were found. Please install PIP 3.7."
                fi
            fi
            ;;
        *)
            if [[ ${pipVersion} == *"3.6"* ]]; then
                echo "Found Python 3.7 but only PIP 3.6 was found. Let's try to use Python 3.6 instead, or switch to PIP 3.7."
                if [[ $testForPython3 == *"3.6"* ]] && [[ $testForPython3 != *"not found"* ]]; then
                    pythonBin='python3.6'
                    pythonVersion='3.6'
                elif [[ $testForPython2 == *"3.6"* ]] && [[ $testForPython2 != *"not found"* ]]; then
                    pythonBin='python3'
                    pythonVersion='3.6'
                elif [[ $testForPython == *"3.6"* ]] && [[ $testForPython != *"not found"* ]]; then
                    pythonBin='python'
                    pythonVersion='3.6'
                else
                    echo "Python 3.6 is not installed yet PIP 3.6 is. Let's look for PIP 3.7."
                    if [[ $testForPip4 == *"3.7"* ]] && [[ $testForPip4 != *"not found"* ]]; then
                        pipBin='pip3.7'
                        pipVersion='3.7'
                    elif [[ $testForPip2 == *"3.7"* ]] && [[ $testForPip2 != *"not found"* ]]; then
                        pipBin='pip3'
                        pipVersion='3.7'
                    elif [[ $testForPip == *"3.7"* ]] && [[ $testForPip != *"not found"* ]]; then
                        pipBin='pip'
                        pipVersion='3.7'
                    else
                        echo "PIP 3.7 not found either. Please install PIP 3.7."
                        pipBin='Missing'
                    fi
                fi 
            else
                pipBin='Missing'
                echo "Python 3.7 is installed, but neither PIP 3.7 nor PIP 3.6 were found. Please install PIP 3.7."
            fi
            ;;
    esac
elif [[ ${pythonVersion} == *"3.6"* ]] && [[ ${pipVersion} != *"3.6"* ]]; then
    case ${pipBin} in
        3.7)
            echo "Found Python 3.6 but not PIP 3.6. Let's look for PIP 3.6 or switch to Python 3.7."
            if [[ $testForPython4 == *"3.7"* ]] && [[ $testForPython4 != *"not found"* ]]; then
                pythonBin='python3.7'
                pythonVersion='3.7'
            elif [[ $testForPython2 == *"3.7"* ]] && [[ $testForPython2 != *"not found"* ]]; then
                pythonBin='python3'
                pythonVersion='3.7'
            elif [[ $testForPython == *"3.7"* ]] && [[ $testForPython != *"not found"* ]]; then
                pythonBin='python3'
                pythonVersion='3.7'
            elif [[ $testForPip3 == *"3.6"* ]] && [[ $testForPip3 != *"not found"* ]]; then
                pipBin='pip3.6'
                pipVersion='3.6'
            elif [[ $testForPip2 == *"3.6"* ]] && [[ $testForPip2 != *"not found"* ]]; then
                pipBin='pip3'
                pipVersion='3.6'
            elif [[ $testForPip == *"3.6"* ]] && [[ $testForPip != *"not found"* ]]; then
                pipBin='pip'
                pipVersion='3.6'
            else
                pipBin='Missing'
                echo "Python 3.6 was found, but PIP 3.6 and Python 3.7 were not found. Please install PIP 3.6."
            fi
            ;;
        3)
            if [[ ${pipBin} != *"3.6"* ]] || [[ ${pipBin} != *"3.7"* ]]; then
                if [[ ${pipVersion} == *"3.7"* ]]; then
                    echo "Found Python 3.6 and PIP 3.7. Let's try to switch to Python 3.7 or PIP 3.6."
                    if [[ $testForPython4 == *"3.7"* ]] && [[ $testForPython4 != *"not found"* ]]; then
                        pythonBin='python3.7'
                        pythonVersion='3.7'
                    elif [[ $testForPython2 == *"3.7"* ]] && [[ $testForPython2 != *"not found"* ]]; then
                        pythonBin='python3'
                        pythonVersion='3.7'
                    elif [[ $testForPython == *"3.7"* ]] && [[ $testForPython != *"not found"* ]]; then
                        pythonBin='python3'
                        pythonVersion='3.7'
                    elif [[ $testForPip3 == *"3.6"* ]] && [[ $testForPip3 != *"not found"* ]]; then
                        pipBin='pip3.6'
                        pipVersion='3.6'
                    elif [[ $testForPip2 == *"3.6"* ]] && [[ $testForPip2 != *"not found"* ]]; then
                        pipBin='pip3'
                        pipVersion='3.6'
                    elif [[ $testForPip == *"3.6"* ]] && [[ $testForPip != *"not found"* ]]; then
                        pipBin='pip'
                        pipVersion='3.6'
                    else
                        pipBin='Missing'
                    fi
                else
                    pipBin='Missing'
                fi
            fi
            ;;
        *)
            if [[ ${pipVersion} == *"3.7"* ]]; then
                echo "Found Python 3.6 and PIP 3.7. Let's try to switch to Python 3.7 or PIP 3.6."
                if [[ $testForPython4 == *"3.7"* ]] && [[ $testForPython4 != *"not found"* ]]; then
                    pythonBin='python3.7'
                    pythonVersion='3.7'
                elif [[ $testForPython2 == *"3.7"* ]] && [[ $testForPython2 != *"not found"* ]]; then
                    pythonBin='python3'
                    pythonVersion='3.7'
                elif [[ $testForPython == *"3.7"* ]] && [[ $testForPython != *"not found"* ]]; then
                    pythonBin='python3'
                    pythonVersion='3.7'
                elif [[ $testForPip3 == *"3.6"* ]] && [[ $testForPip3 != *"not found"* ]]; then
                    pipBin='pip3.6'
                    pipVersion='3.6'
                elif [[ $testForPip2 == *"3.6"* ]] && [[ $testForPip2 != *"not found"* ]]; then
                    pipBin='pip3'
                    pipVersion='3.6'
                elif [[ $testForPip == *"3.6"* ]] && [[ $testForPip != *"not found"* ]]; then
                    pipBin='pip'
                    pipVersion='3.6'
                else
                    pipBin='Missing'
                fi
            else
                pipBin='Missing'
            fi
            ;;
    esac
fi

echo "Python 3 bin is ${pythonBin} ($(which ${pythonBin}))"
echo "Pip 3 bin is ${pipBin} ($(which ${pipBin}))"

PYTHON3BIN=${pythonBin}
export PYTHON3BIN
export PIP3BIN=$(which ${pipBin})
