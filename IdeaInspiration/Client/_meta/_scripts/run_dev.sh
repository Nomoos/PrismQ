#!/bin/bash

# PrismQ Web Client Backend - Development Server

echo "Starting PrismQ Web Client Backend in development mode..."
echo ""
echo "Server will run on http://127.0.0.1:8000"
echo "API docs available at http://127.0.0.1:8000/docs"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run uvicorn with auto-reload using custom runner
python -m src.uvicorn_runner
