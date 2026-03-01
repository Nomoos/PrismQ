#!/bin/bash
# Run.sh - PrismQ.T.Script.From.Title.Review.Script
# Refine script from title and review feedback - saves to database
#
# Usage: ./Run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

setup_env() {
    MODULE_DIR="$SCRIPT_DIR/../../../T/Content/From/Title/Review/Script"
    VENV_DIR="$MODULE_DIR/.venv"
    REQUIREMENTS="$MODULE_DIR/requirements.txt"
    VENV_MARKER="$VENV_DIR/pyvenv.cfg"
    
    echo "[INFO] Setting up Python environment..."
    
    if ! command -v python3 &> /dev/null; then
        echo "ERROR: Python3 not found"
        exit 1
    fi
    
    if [ ! -f "$VENV_MARKER" ]; then
        echo "[INFO] Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    source "$VENV_DIR/bin/activate"
    
    if [ -f "$REQUIREMENTS" ] && [ ! -f "$VENV_DIR/.requirements_installed" ]; then
        echo "[INFO] Installing dependencies..."
        pip install -r "$REQUIREMENTS" --quiet
        touch "$VENV_DIR/.requirements_installed"
    fi
    
    echo "[INFO] Environment ready"
}

setup_env

echo "========================================"
echo "PrismQ.T.Script.From.Title.Review.Script - RUN MODE"
echo "========================================"
echo

python3 ../../../T/Content/From/Title/Review/Script/src/script_from_review_workflow.py

if [ $? -ne 0 ]; then
    echo "ERROR: Script execution failed"
    exit 1
fi

echo
echo "Press Enter to continue..."
read
