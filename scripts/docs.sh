#!/bin/bash
# PrismQ Module Documentation Build Script for Linux/Unix
# Target: Linux with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
# Python scripts are optimized for Windows but will work on Linux too

set -e  # Exit on error

echo "====================================="
echo "PrismQ Module Documentation"
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
echo "Building documentation with Sphinx..."
echo

# Install Sphinx if not already installed
echo "Checking for Sphinx..."
python -c "import sphinx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Sphinx and dependencies..."
    pip install sphinx sphinx-rtd-theme
fi

# Clean previous builds
echo "Cleaning previous documentation builds..."
if [ -d "doc/build" ]; then
    rm -rf doc/build
fi

# Build HTML documentation
echo "Building HTML documentation..."
sphinx-build -b html doc/source doc/build

echo
echo "====================================="
echo "Documentation Build Complete!"
echo "====================================="
echo
echo "Documentation available at:"
echo "  doc/build/index.html"
echo

# Only offer browser opening if running in a terminal
if [ -t 0 ]; then
    echo "To view in browser:"
    echo "  xdg-open doc/build/index.html"
    echo
    
    # Optional: Open in browser automatically
    read -p "Open documentation in browser? (y/n): " OPEN_BROWSER
    if [[ "$OPEN_BROWSER" =~ ^[Yy]$ ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open doc/build/index.html
        elif command -v open &> /dev/null; then
            open doc/build/index.html
        else
            echo "Could not find a command to open the browser."
            echo "Please open doc/build/index.html manually."
        fi
    fi
    
    read -p "Press Enter to continue..."
fi
