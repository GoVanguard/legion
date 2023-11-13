#!/bin/bash

checkWsl() {
# Check if WSL is in use
if grep -q Microsoft /proc/version; then
    if grep -q Microsoft-standard /proc/version; then
        ip addr show eth0 | grep -q "172\. "
        if [ $? -eq 0 ]; then
            echo "WSL 2 detected. You are using a bridged network configuration."
            echo "Verify your network configuration and %userprofile%\\.wslconfig."
            echo "Make sure XMing is running. Check the XMing long."
            echo "When you start XMing, make sure access control is turned off unless you've setup a cookie."
            echo "Ultimately the Xorg port cannot be reached or being rejected."
            exit 1
        else
            echo "WSL 2 detected. You are using a NAT-only network configuration."
            echo "You cannot reach Xming on the Windows desktop easily this way. Please switch to a bridged network configuration."
            echo "See https://learn.microsoft.com/en-us/windows/wsl/wsl-config and https://blog.alexbal.com/2022/01/26/12/."
            echo "Ultimately the Xorg port cannot be reached or being rejected."
            exit 1
        fi
    else
        echo "WSL 1 detected. Verify your network configuration and /etc/wsl.conf."
        echo "Make sure XMing is running. Check the XMing long."
        echo "When you start XMing, make sure access control is turned off unless you've setup a cookie."
        echo "Ultimately the Xorg port cannot be reached or being rejected."
        exit 1
    fi
fi
}

# Check if DISPLAY variable is set
if [ -z "$DISPLAY" ]; then
    echo "DISPLAY variable is not set. Please export the DISPLAY variable and try again."
    exit 1
fi

# Extract the host and port from the DISPLAY variable
xorgHost=$(echo $DISPLAY | sed 's/:.*//')

# Check if the Xorg port is open
nc -zv $xorgHost 6000 &> /dev/null
if [ $? -ne 0 ]; then
    echo "Cannot reach the X server at $xorgHost:6000. Please check your X server configuration and verify your DISPLAY variable has been exported correctly."
    checkWsl
    exit 1
fi

echo "X server is reachable. You're good to go!"
