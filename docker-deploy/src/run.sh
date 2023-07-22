#!/bin/bash
echo 'server start...'
#taskset -c 0 python3 server.py
#taskset -c 0-1 python3 server.py
taskset -c 0-3 python3 server.py
while true; do continue; done
