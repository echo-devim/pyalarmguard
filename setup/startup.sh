#! /bin/bash

export PULSE_RUNTIME_PATH=/run/user/1000/pulse/

# cleanup photo directory from photos older than 30 days
find /opt/data/photos -type f -mtime +30 -delete

# Init pi session
ssh pi@localhost "cd /opt/pyalarmguard/ && python3 main.py"




