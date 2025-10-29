#!/bin/bash
# PrismQ Module Setup Script for Linux/Unix
# Target: Linux with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
# Python scripts are optimized for Windows but will work on Linux too

set -e  # Exit on error

echo "====================================="
echo "PrismQ Module Setup"
echo "====================================="
echo

# Set default Python executable
PYTHON_EXEC="python3"

# Read PYTHON_EXECUTABLE from .env if it exists
if [ -f ".env" ]; then
    # Use grep and sed for robust parsing, handle comments and spaces
    PYTHON_EXEC_FROM_ENV=$(grep -E "^PYTHON_EXECUTABLE=" .env | sed 's/^PYTHON_EXECUTABLE=//' | tr -d '"' | tr -d "'" | xargs || echo "")
    if [ -n "$PYTHON_EXEC_FROM_ENV" ]; then
        PYTHON_EXEC="$PYTHON_EXEC_FROM_ENV"
    fi
fi

# Check Python installation
if ! command -v "$PYTHON_EXEC" &> /dev/null; then
    echo "ERROR: Python executable '$PYTHON_EXEC' is not found or not working"
    echo "Please install Python 3.14 or higher or update PYTHON_EXECUTABLE in .env"
    exit 1
fi

echo "Python found: $PYTHON_EXEC"
echo

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    "$PYTHON_EXEC" -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
echo

# Activate virtual environment and install dependencies
echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo
echo "To run the module:"
echo "  python -m src.main"
echo

# Skip interactive prompt if not running in a terminal
if [ -t 0 ]; then
    read -p "Press Enter to continue..."
fi
