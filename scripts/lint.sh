#!/bin/bash
# PrismQ Module Lint Script for Linux/Unix
# Target: Linux with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
# Python scripts are optimized for Windows but will work on Linux too

set -e  # Exit on error

echo "====================================="
echo "PrismQ Module Lint"
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
echo "Running code quality checks..."
echo

# Run ruff check (PEP 8, PEP 257 linting)
echo "Running Ruff linting (PEP 8, PEP 257)..."
set +e  # Allow ruff to fail, we'll handle it
ruff check .
RUFF_STATUS=$?
set -e

if [ $RUFF_STATUS -ne 0 ]; then
    echo
    echo "====================================="
    echo "Linting failed!"
    echo "====================================="
    echo
    echo "To auto-fix issues, run:"
    echo "  ruff check --fix ."
    echo
    if [ -t 0 ]; then
        read -p "Press Enter to continue..."
    fi
    exit 1
fi

echo
echo "Running MyPy type checking (PEP 484, 526, 544)..."
mypy src/

echo
echo "====================================="
echo "Linting Complete!"
echo "====================================="
echo "All code quality checks passed."
echo

# Skip interactive prompt if not running in a terminal
if [ -t 0 ]; then
    read -p "Press Enter to continue..."
fi
