#!/bin/sh
while true
do
		git pull
        echo "running avebot"
        date
        python3.6 avebot.py
        sleep 1
done
