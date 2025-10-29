#!/bin/bash
# Test script for PrismQ.IdeaInspiration.Classification (Linux/Mac - Development Only)

echo "======================================"
echo "PrismQ.IdeaInspiration.Classification"
echo "Running Tests"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found"
    echo "Please run setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
fi

# Run tests
echo "Running test suite..."
echo ""
pytest -v --cov=prismq --cov-report=html --cov-report=term

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Some tests failed"
    exit 1
else
    echo ""
    echo "[OK] All tests passed!"
fi

echo ""
echo "Coverage report saved to: htmlcov/index.html"
echo ""
