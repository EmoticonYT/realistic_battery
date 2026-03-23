#!/bin/bash

echo "Starting Realistic Battery"

read -p "Please install Python3 before running this script. If you get any cannot find "python3" or module not found "pip" errors, you may need to install Python or Pip Press enter to continue..." pressentertocontinuevariablenotimportantdontcaredidntasklollmaostfuidc

prevdir="$PWD"

cd /tmp

rm -rf realisticbattery

mkdir -p /tmp/realisticbattery

cd realisticbattery

curl -LO "https://raw.githubusercontent.com/EmoticonYT/realistic_battery/refs/heads/main/realisticbattery/realistic_battery.py"

curl -LO "https://raw.githubusercontent.com/EmoticonYT/realistic_battery/refs/heads/main/realisticbattery/Realistic%20Battery.spec"

curl -LO "https://raw.githubusercontent.com/EmoticonYT/realistic_battery/refs/heads/main/realisticbattery/requirements.txt"

python3 -m pip install -r requirements.txt --break-system-packages

python3 realistic_battery.py --gui

PYPID=$!

echo "Running Now!"

wait $PYPID; echo "Thanks for using Realistic Battery!"; exit' INT
