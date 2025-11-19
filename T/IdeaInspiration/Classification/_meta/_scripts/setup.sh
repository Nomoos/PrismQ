#!/bin/bash
# Setup script for PrismQ.IdeaInspiration.Classification (Linux/Mac - Development Only)

echo "======================================"
echo "PrismQ.IdeaInspiration.Classification"
echo "Setup Script (Development Only)"
echo "======================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/5] Checking Python version..."
python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if [ $? -ne 0 ]; then
    echo "[ERROR] Python 3.8 or higher is required"
    exit 1
fi
echo "[OK] Python version is compatible"

echo ""
echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
    echo "[OK] Virtual environment created"
fi

echo ""
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
fi
echo "[OK] Virtual environment activated"

echo ""
echo "[4/5] Installing package and dependencies..."
pip install -e ".[dev]" --quiet
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install package"
    exit 1
fi
echo "[OK] Package installed"

echo ""
echo "[5/5] Running tests..."
pytest -q
if [ $? -ne 0 ]; then
    echo "[WARNING] Some tests failed, but setup completed"
else
    echo "[OK] All tests passed"
fi

echo ""
echo "======================================"
echo "Setup completed successfully!"
echo "======================================"
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the example:"
echo "  python _meta/examples/example.py"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
