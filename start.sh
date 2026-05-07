#!/bin/bash

echo "🚀 Starting DeuceVerify Bot + FastAPI..."

# Start FastAPI with Uvicorn (using Railway's $PORT)
uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 2 &

# Start Telegram Bot
python -m bot.main &

# Wait for any process to exit
wait -n

# Exit with the status of whichever process failed first
exit $?