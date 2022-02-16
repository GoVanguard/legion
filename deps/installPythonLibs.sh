#!/bin/bash

source ./deps/detectPython.sh

# Setup Python deps
${PIP3BIN} install -r requirements.txt --upgrade

${PYTHON3BIN} ./deps/primeExploitDb.py
