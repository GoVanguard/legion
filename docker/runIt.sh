#!/bin/bash

if [[ -z $1 ]]
then
    X11HOST=localhost
else
    X11HOST=$1
fi

export DISPLAY=$X11HOST:0.0
docker pull gvit/legion
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
rm /tmp/.docker.xauth* -f
touch $XAUTH
xauth add $DISPLAY - `mcookie`
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -
docker run -ti -v $XSOCK -v $XAUTH -e XAUTHORITY=$XAUTH -e DISPLAY=$DISPLAY gvit/legion
