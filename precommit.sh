#!/bin/bash

# Update last update in controller
sed -i -r "s/update\": .*?/update\": '`date '+%m\/%d\/%Y'`',/g" ./app/ApplicationInfo.py
sed -i -r "s/build\": .*?/build\": '`date '+%s'`',/g" ./app/ApplicationInfo.py

# Clear logs

echo "" > ./log/legion.log
echo "" > ./log/legion-db.log
echo "" > ./log/legion-startup.log

# Prep hidden files
rm -f .initialized
touch .justcloned

# Clear tmp
rm -Rf ./tmp/*

# Clear all pyc and pyc
find . -name \*.pyc -delete
find . -name \*.pyo -delete

# Remove cloned scripts
rm -Rf ./scripts/CloudFail/

# Removed backups
rm -Rf ./backup/*.conf

find . -type f -exec sed -i 's/Copyright (c) 2020 GoVanguard/Copyright (c) 2022 GoVanguard/' {} \;
