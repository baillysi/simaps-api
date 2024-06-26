#!/bin/bash
gunicorn -w 4 "wsmain.deploy:app" -b 0.0.0.0:8080 -t 0
