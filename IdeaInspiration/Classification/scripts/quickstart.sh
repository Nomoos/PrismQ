#!/bin/bash
# Quickstart script for PrismQ.IdeaInspiration.Classification (Linux/Mac - Development Only)

echo "======================================"
echo "PrismQ.IdeaInspiration.Classification"
echo "Quickstart - Running Example"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found"
    echo "Please run setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
fi

# Run example
echo "Running classification example..."
echo ""
python example.py

echo ""
echo "======================================"
echo "Example completed!"
echo "======================================"
echo ""
