#!/bin/bash
releaseTag=`git branch | grep "*" | awk '{print $2}'`
docker build -t legion:${releaseTag} . --no-cache
