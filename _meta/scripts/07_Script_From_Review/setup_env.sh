#!/bin/bash
# setup_env.sh - Setup Python Virtual Environment for PrismQ.T.Script.From.Title.Review.Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_DIR="$(cd "$SCRIPT_DIR/../../../T/Script/From/Title/Review/Script" && pwd)"
VENV_DIR="$MODULE_DIR/.venv"
REQUIREMENTS="$MODULE_DIR/requirements.txt"
ENV_FILE="$MODULE_DIR/.env"
VENV_MARKER="$VENV_DIR/pyvenv.cfg"

echo ""
echo "========================================"
echo "PrismQ - Python Environment Setup"
echo "========================================"
echo ""

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python is not installed or not in PATH"
    return 1 2>/dev/null || exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "[INFO] Python version: $PYTHON_VERSION"

if [ -f "$VENV_MARKER" ]; then
    echo "[INFO] Virtual environment found: $VENV_DIR"
else
    echo "[INFO] Creating virtual environment at: $VENV_DIR"
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        return 1 2>/dev/null || exit 1
    fi
    echo "[SUCCESS] Virtual environment created"
fi

echo "[INFO] Activating virtual environment..."
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    return 1 2>/dev/null || exit 1
fi

PYTHON_PATH=$(which python)
echo "[INFO] Using Python: $PYTHON_PATH"

REQUIREMENTS_MARKER="$VENV_DIR/.requirements_installed"
if [ ! -f "$REQUIREMENTS_MARKER" ]; then
    if [ -f "$REQUIREMENTS" ]; then
        echo "[INFO] Installing dependencies..."
        pip install -r "$REQUIREMENTS" --quiet
        if [ $? -ne 0 ]; then
            echo "[ERROR] Failed to install dependencies"
            return 1 2>/dev/null || exit 1
        fi
        date > "$REQUIREMENTS_MARKER"
        echo "[SUCCESS] Dependencies installed"
    else
        echo "[INFO] No requirements.txt found"
        date > "$REQUIREMENTS_MARKER"
    fi
else
    echo "[INFO] Dependencies already installed"
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "[INFO] Creating .env file at: $ENV_FILE"
    cat > "$ENV_FILE" << 'EOF'
# PrismQ.T.Script.From.Title.Review.Script Environment Configuration
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
echo "========================================"
echo ""

export PRISMQ_VENV="$VENV_DIR"
export PRISMQ_PYTHON="$PYTHON_PATH"
