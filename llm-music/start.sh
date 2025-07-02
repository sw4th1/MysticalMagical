#!/bin/bash

echo "Starting Ollama server in background..."
# Start Ollama server in the background. Redirect stdout/stderr to files for debugging if needed,
# or just let them go to the console for Docker logs.
ollama serve &

# Give Ollama a few seconds to fully initialize
sleep 5

echo "Starting Python web server..."
# Ensure this path is correct relative to the WORKDIR (/app) in your Dockerfile.
# Given your structure, web_server.py is in src/, so the path is src/web_server.py
python src/web_server.py