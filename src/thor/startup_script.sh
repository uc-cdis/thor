#!/bin/bash

# start scheduler
$HOME/.poetry/bin/poetry run python /time/scheduler.py &

# start web server
$HOME/.poetry/bin/poetry run gunicorn thor.main:app -b 0.0.0.0:6565 -k uvicorn.workers.UvicornWorker --reload
