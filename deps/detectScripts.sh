#!/bin/bash

echo "Checking for additional Sparta scripts..."
curPath=`pwd`

scripts=("smbenum.sh" "snmpbrute.py" "ms08-067_check.py" "rdp-sec-check.pl", "ndr.py", "installDeps.sh", "snmpcheck.rb", "smtp-user-enum.pl")

for script in "${scripts[@]}"; do
  if [ -a "scripts/$script" ]; then
    echo "$script is already installed"
  else
    wget -v -P scripts/ "https://raw.githubusercontent.com/GoVanguard/sparta-scripts/master/$script"
  fi
done

declare -A externalRepos
externalRepos["CloudFail"]="https://github.com/m0rtem/CloudFail.git"

for externalRepo in "${!externalRepos[@]}"; do
  if [ -d "scripts/$externalRepos" ]; then
    echo "$externalRepo is already installed"
  else
    git clone "${externalRepos[$externalRepo]}" scripts/$externalRepo
  fi
done

if [ ! -f ".initialized" ]
  then
    chmod a+x scripts/installDeps.sh
    ./scripts/installDeps.sh
fi

cd ${curPath}
