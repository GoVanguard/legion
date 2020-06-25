#!/bin/bash

echo "Building local branch"
docker build -f ./docker/Dockerfile.local -t legion:local . --no-cache
