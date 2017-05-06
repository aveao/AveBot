#!/bin/sh
echo -n "" >> banlist
echo -n "" >> modslist
echo -n "" >> privlist
while true
do
		git pull
        echo "Running AveBot. Current time: $(date)"
        python3 avebot.py
        sleep 1
done
