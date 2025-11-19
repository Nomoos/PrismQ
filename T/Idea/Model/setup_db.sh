#!/bin/bash
# Setup script for Idea database (Linux/macOS)

set -e

echo "=========================================="
echo "PrismQ.Idea.Model - Database Setup"
echo "=========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Current directory: $(pwd)"
echo ""

# Check Python version
if command -v python3.10 &> /dev/null; then
    PYTHON_CMD=python3.10
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    echo "Error: Python 3 not found!"
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# Setup database
echo "Setting up Idea database..."
$PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
from src.idea_db import setup_database

print('Creating database schema...')
db = setup_database('idea.db')
print(f'✓ Database created: idea.db')
print(f'✓ Tables created: ideas, idea_inspirations')
print(f'✓ Indexes created for performance')
db.close()
print('✓ Setup complete!')
"

echo ""
echo "=========================================="
echo "Database setup successful!"
echo "Database file: idea.db"
echo "=========================================="
