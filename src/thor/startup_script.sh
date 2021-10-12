#!/bin/bash

# start scheduler
poetry run python src/thor/time/scheduler.py &

# start web server
poetry run gunicorn thor.main:app -b 0.0.0.0:6565 -k uvicorn.workers.UvicornWorker --reload
