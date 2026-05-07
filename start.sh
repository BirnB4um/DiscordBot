#!/bin/bash
echo "starting..."

cd src
/usr/local/bin/python launcher.py

tail -f /dev/null