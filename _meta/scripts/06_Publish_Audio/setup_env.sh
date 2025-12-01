#!/bin/bash
# setup_env.sh - Setup Python Virtual Environment for PrismQ Publish Audio Modules
# This script provides environment setup for Audio Publishing modules
#
# Usage:
#   source ./setup_env.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

echo ""
echo "[INFO] Publish Audio module environment ready"
echo ""

export PRISMQ_PYTHON="$PYTHON_CMD"
