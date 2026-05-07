#!/bin/bash

echo "Starting Telegram Bot and Flask API..."

# Start the bot in the background
python -m bot.main &

# Start the Flask API (important: bind to $PORT)
python -m api.main &

# Wait for any process to exit
wait -n

# Exit with status of the process that exited first
exit $?