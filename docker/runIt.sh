#!/bin/bash

docker pull gvit/legion

if [[ ! -z $1 ]]
then
    export DISPLAY=$1:0.0
    XSOCK=/tmp/.X11-unix
    XAUTH=/tmp/.docker.xauth
    rm /tmp/.docker.xauth* -f
    touch $XAUTH
    xauth add $DISPLAY - `mcookie`
    xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -
    docker run -ti -v $XSOCK -v $XAUTH -e XAUTHORITY=$XAUTH -e DISPLAY=$DISPLAY gvit/legion
else
    docker run -ti -e DISPLAY=$DISPLAY --net=host --security-opt=apparmor:unconfined --security-opt=label:disable gvit/legion
fi
