#!/bin/bash

strip --remove-section=.note.ABI-tag /usr/local/lib/python3.8/dist-packages/PyQt6/Qt6/lib/libQt6Core.so.6
strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5
