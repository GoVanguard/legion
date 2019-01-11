#!/bin/bash
# Setup Python deps

testForPip=`pip --version`

if [[ $testForPip == *"3.6"* ]]; then
    pipBin='pip'
else
    pipBin='pip3.6'
fi

$pipBin -r requirements.txt
$pipBin install sqlalchemy pyqt5 asyncio aiohttp aioredis aiomonitor apscheduler Quamash
$pipBin install service_identity --upgrade
