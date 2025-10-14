#!/bin/bash
# PrismQ Module Setup Script for Linux
# Note: Windows is the primary target platform. This script provides limited Linux support for development only.
# macOS is not supported.

set -e

echo "====================================="
echo "PrismQ Module Setup"
echo "====================================="
echo

# Set default Python executable
PYTHON_EXEC="python3"

# Read PYTHON_EXECUTABLE from .env if it exists
if [ -f ".env" ]; then
    if grep -q "^PYTHON_EXECUTABLE=" .env; then
        PYTHON_EXEC=$(grep "^PYTHON_EXECUTABLE=" .env | cut -d '=' -f 2)
    fi
fi

# Check Python installation
if ! command -v "$PYTHON_EXEC" &> /dev/null; then
    echo "ERROR: Python executable '$PYTHON_EXEC' is not found"
    echo "Please install Python 3.10 or higher or update PYTHON_EXECUTABLE in .env"
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
