#!/bin/bash

# Update last update in controller
sed -i -r "s/self.update = '.*?'/self.update = \'`date '+%m\/%d\/%Y'\'`/g" ./controller/controller.py
sed -i -r "s/self.build = '.*?'/self.build = \'`date '+%s'\'`/g" ./controller/controller.py

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
