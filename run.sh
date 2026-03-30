#!/bin/bash
cd ~/src/get_polly_data/
## === LOAD ENVIRONMENT FROM .env ===
#export $(grep -v '^#' .env | xargs)

# === START FASTAPI USING GUNICORN ===
/lacroshome/cloudnetpy/venv/get_api_env/bin/gunicorn main:app \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5052

