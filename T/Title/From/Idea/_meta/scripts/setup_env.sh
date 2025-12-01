#!/bin/bash
# setup_env.sh - Setup Python Virtual Environment for PrismQ.T.Title.From.Idea
# This script creates and activates a virtual environment for the module
#
# Virtual environment location: T/Title/From/Idea/.venv
# Dependencies: T/Title/From/Idea/requirements.txt (if exists)
#
# Usage:
#   source ./setup_env.sh
#
# Note: Must be sourced (not executed) to activate the virtual environment in your shell

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$MODULE_DIR/.venv"
REQUIREMENTS="$MODULE_DIR/requirements.txt"
ENV_FILE="$MODULE_DIR/.env"
VENV_MARKER="$VENV_DIR/pyvenv.cfg"

echo ""
echo "========================================"
echo "PrismQ - Python Environment Setup"
echo "========================================"
echo ""

# Check Python availability
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python is not installed or not in PATH"
    echo ""
    echo "Please install Python from https://www.python.org/downloads/"
    return 1 2>/dev/null || exit 1
fi

# Show Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "[INFO] Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ -f "$VENV_MARKER" ]; then
    echo "[INFO] Virtual environment found: $VENV_DIR"
    echo "[INFO] Using existing virtual environment"
else
    echo "[INFO] Virtual environment not found"
    echo "[INFO] Creating virtual environment at: $VENV_DIR"
    echo ""
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        echo ""
        echo "Please ensure you have the 'venv' module installed."
        echo "On some systems, you may need to install it separately:"
        echo "  - Ubuntu/Debian: sudo apt install python3-venv"
        echo "  - macOS: Should be included with Python installation"
        return 1 2>/dev/null || exit 1
    fi
    echo "[SUCCESS] Virtual environment created"
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    return 1 2>/dev/null || exit 1
fi

# Show activated Python path
PYTHON_PATH=$(which python)
echo "[INFO] Using Python: $PYTHON_PATH"

# Check if requirements need to be installed (only if requirements.txt exists)
REQUIREMENTS_MARKER="$VENV_DIR/.requirements_installed"
if [ -f "$REQUIREMENTS" ] && [ ! -f "$REQUIREMENTS_MARKER" ]; then
    echo "[INFO] Installing dependencies from requirements.txt..."
    pip install -r "$REQUIREMENTS" --quiet
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        return 1 2>/dev/null || exit 1
    fi
    # Create marker file
    date > "$REQUIREMENTS_MARKER"
    echo "[SUCCESS] Dependencies installed"
elif [ -f "$REQUIREMENTS_MARKER" ]; then
    echo "[INFO] Dependencies already installed"
else
    echo "[INFO] No requirements.txt found - using system packages"
fi

# Create .env file if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    echo "[INFO] Creating .env file at: $ENV_FILE"
    cat > "$ENV_FILE" << 'EOF'
# PrismQ.T.Title.From.Idea Environment Configuration
# Created automatically on first run

# Working directory (auto-detected)
# WORKING_DIRECTORY=

# Database configuration
# DATABASE_URL=sqlite:///db.s3db
EOF
    echo "[SUCCESS] .env file created"
else
    echo "[INFO] .env file exists: $ENV_FILE"
fi

echo ""
echo "========================================"
echo "Environment Setup Complete"
echo "========================================"
echo "  Virtual Environment: $VENV_DIR"
echo "  Python: $PYTHON_PATH"
echo "  Requirements: $REQUIREMENTS"
echo "  Config: $ENV_FILE"
echo "========================================"
echo ""

# Export variables for use in calling scripts
export PRISMQ_VENV="$VENV_DIR"
export PRISMQ_PYTHON="$PYTHON_PATH"
