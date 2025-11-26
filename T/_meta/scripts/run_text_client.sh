#!/bin/bash
# Quick run script for PrismQ.T Interactive Text Client
# 
# Usage:
#   ./run_text_client.sh          # Start interactive client
#   ./run_text_client.sh --demo   # Start with demo data
#   ./run_text_client.sh --check  # Check module availability

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    PrismQ.T - Interactive Text Client                        ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python availability
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "Error: Python is not installed or not in PATH"
        exit 1
    fi
else
    PYTHON_CMD="python3"
fi

# Run the interactive client
cd "$SCRIPT_DIR"
PYTHONPATH="${SCRIPT_DIR}/../../../:${PYTHONPATH}" $PYTHON_CMD run_text_client.py "$@"
