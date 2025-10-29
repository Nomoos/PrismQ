#!/bin/bash
# Database Setup Script for PrismQ Model Repositories
# This script sets up the database in the nearest PrismQ directory
# Use this file if your repository is a Model type

set -e

echo "====================================="
echo "PrismQ Database Setup"
echo "====================================="
echo ""

# Get the script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Set default Python executable
PYTHON_EXEC="python3"

# Check if Python executable exists
if ! command -v "$PYTHON_EXEC" &> /dev/null; then
    echo ""
    echo "[ERROR] Python executable '$PYTHON_EXEC' not found."
    echo "[ERROR] Please install Python 3.14 or higher and try again."
    exit 1
fi

echo "[INFO] Using Python: $PYTHON_EXEC"
$PYTHON_EXEC --version
echo ""

# Use Python to set up configuration and get working directory
echo "[INFO] Setting up configuration..."
USER_WORK_DIR=$($PYTHON_EXEC -c "import sys; sys.path.insert(0, 'src'); from config import Config; config = Config(interactive=True); print(config.working_directory)")

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to set up configuration."
    exit 1
fi

echo "[INFO] Working directory: $USER_WORK_DIR"
echo ""

# Create the database path
DB_PATH="$USER_WORK_DIR/db.s3db"
echo "[INFO] Database will be created at: $DB_PATH"
echo ""

# Check if database already exists
if [ -f "$DB_PATH" ]; then
    echo "[WARNING] Database file already exists: $DB_PATH"
    
    # For non-interactive mode (CI), skip confirmation
    if [ -t 0 ]; then
        # Interactive mode
        read -p "Do you want to recreate it? (Y/N): " OVERWRITE
        if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
            echo "[INFO] Keeping existing database."
            echo "[INFO] Setup completed."
            exit 0
        fi
    else
        # Non-interactive mode (CI)
        echo "[INFO] Non-interactive mode: Keeping existing database."
        exit 0
    fi
    
    echo "[INFO] Removing existing database..."
    rm "$DB_PATH"
fi

# Create database using Python
echo "[INFO] Creating database..."
$PYTHON_EXEC -c "import sqlite3; import sys; sys.path.insert(0, 'src'); conn = sqlite3.connect('$DB_PATH'); print('[SUCCESS] Database created successfully'); conn.close()"

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create database."
    exit 1
fi

echo ""
echo "====================================="
echo "Setup completed successfully!"
echo "====================================="
echo ""
echo "Database location: $DB_PATH"
echo "Working directory: $USER_WORK_DIR"
echo ""
echo "You can now use this database with your PrismQ module."
echo ""
