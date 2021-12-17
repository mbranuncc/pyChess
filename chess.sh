#!/bin/bash
#TODO: Update to kill app process at conclusion of script

python3 app.py &
sleep 1
python3 visuals.py &
