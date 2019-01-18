#!/bin/bash

source ./deps/detectPython.sh

# Setup Python deps
${PIP3BIN} install -r requirements.txt
${PIP3BIN} install service_identity --upgrade
