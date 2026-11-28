#!/bin/bash
curl -s -o /dev/null http://localhost:8765/index.html || { (nohup python3 -m http.server 8765 --directory /home/claude/kokugo-app >/dev/null 2>&1 &); sleep 1; }
python3 -u /home/claude/regress/run.py "$@"
