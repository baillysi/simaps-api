#!/bin/bash
gunicorn -w 4 "wsmain.app:app" -b 0.0.0.0:8080 -t 0
