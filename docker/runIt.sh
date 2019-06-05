#!/bin/bash

if [[ ! -z $1 ]]
then
    export DISPLAY=$1:0.0
fi

docker pull gvit/legion
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
rm /tmp/.docker.xauth* -f
touch $XAUTH
xauth add $DISPLAY - `mcookie`
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -
docker run -ti -v $XSOCK -v $XAUTH -e XAUTHORITY=$XAUTH -e DISPLAY=$DISPLAY gvit/legion
