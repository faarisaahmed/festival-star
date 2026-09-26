#!/bin/bash
# waits for the render to finish, then assembles the movie
cd "$(dirname "$0")/.."
while pgrep -f render_all.sh > /dev/null; do sleep 60; done
python3 scripts/assemble.py > logs/assemble.log 2>&1
