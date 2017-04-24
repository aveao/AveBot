#!/bin/sh
while true
do
		git pull
        echo "running avebot"
        date
        python3 avebot.py
        sleep 1
done
