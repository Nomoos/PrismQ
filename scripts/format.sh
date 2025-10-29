#!/bin/bash
# PrismQ Module Format Script for Linux/Unix
# Target: Linux with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
# Python scripts are optimized for Windows but will work on Linux too

set -e  # Exit on error

echo "====================================="
echo "PrismQ Module Format"
echo "====================================="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run setup.sh first."
    if [ -t 0 ]; then
        read -p "Press Enter to continue..."
    fi
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
set +e  # Temporarily allow errors for source command
source venv/bin/activate
ACTIVATE_STATUS=$?
set -e  # Re-enable exit on error

if [ $ACTIVATE_STATUS -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo
echo "Formatting code with Ruff (PEP 8)..."
echo

# Run ruff format
ruff format .

echo
echo "====================================="
echo "Formatting Complete!"
echo "====================================="
echo "Code has been formatted according to PEP 8."
echo

# Skip interactive prompt if not running in a terminal
if [ -t 0 ]; then
    read -p "Press Enter to continue..."
fi
