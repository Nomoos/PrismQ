#!/bin/bash
# PrismQ Module Setup Script for Linux
# Note: Windows is the primary target platform. This script provides limited Linux support for development only.
# macOS is not supported.

set -e

echo "====================================="
echo "PrismQ Module Setup"
echo "====================================="
echo

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "Python found!"
echo

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
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
