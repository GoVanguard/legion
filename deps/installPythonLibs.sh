#!/bin/bash

source ./deps/detectPython.sh

# Setup Python deps
${PIP3BIN} install -r requirements.txt --upgrade
${PIP3BIN} install service-identity --upgrade
