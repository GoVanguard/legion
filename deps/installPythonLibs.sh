#!/bin/bash

source ./detectPython.sh

# Setup Python deps
${PIP3BIN} install -r requirements.txt
${PIP3BIN} install sqlalchemy pyqt5 asyncio aiohttp aioredis aiomonitor apscheduler Quamash
${PIP3BIN} install service_identity --upgrade
