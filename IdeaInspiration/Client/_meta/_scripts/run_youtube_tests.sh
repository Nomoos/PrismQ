#!/bin/bash
# PrismQ Backend - YouTube Channel Download Tests Runner
# Run this script to execute YouTube integration tests

set -e  # Exit on error

echo ""
echo "======================================"
echo "  YouTube Channel Download Tests"
echo "======================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Navigate to Backend directory
BACKEND_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/Backend"
cd "$BACKEND_DIR"

echo "Working directory: $PWD"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✓ Virtual environment found"
    
    # Check if already activated
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "✓ Virtual environment already activated: $VIRTUAL_ENV"
    else
        echo "  Activating virtual environment..."
        source venv/bin/activate
        echo "✓ Virtual environment activated: $VIRTUAL_ENV"
    fi
else
    echo "⚠ Virtual environment not found at Backend/venv"
    echo "  Creating virtual environment..."
    
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
fi

echo ""
echo "Checking test dependencies..."

# Function to check if Python package is installed
check_package() {
    python3 -c "import $1" 2>/dev/null
    return $?
}

# Check dependencies
MISSING_DEPS=""

if ! check_package pytest; then
    echo "⚠ pytest not installed"
    MISSING_DEPS="$MISSING_DEPS pytest"
else
    echo "✓ pytest installed"
fi

if ! check_package httpx; then
    echo "⚠ httpx not installed"
    MISSING_DEPS="$MISSING_DEPS httpx"
else
    echo "✓ httpx installed"
fi

if ! check_package pytest_asyncio; then
    echo "⚠ pytest-asyncio not installed"
    MISSING_DEPS="$MISSING_DEPS pytest-asyncio"
else
    echo "✓ pytest-asyncio installed"
fi

# Install missing dependencies
if [ -n "$MISSING_DEPS" ]; then
    echo ""
    echo "Installing missing test dependencies..."
    pip install $MISSING_DEPS
    
    if [ $? -ne 0 ]; then
        echo "✗ Failed to install test dependencies"
        echo "  Please install manually: pip install pytest pytest-asyncio httpx"
        exit 1
    fi
    echo "✓ Test dependencies installed"
fi

# Check for yt-dlp (optional)
echo ""
if check_package yt_dlp; then
    echo "✓ yt-dlp installed (tests will download real data)"
else
    echo "⚠ yt-dlp not installed (tests will run but won't download real data)"
    echo "  To install: pip install yt-dlp"
fi

echo ""
echo "======================================"
echo "  Validating Test Structure"
echo "======================================"
echo ""

# Run validation script
VALIDATION_SCRIPT="_meta/tests/integration/validate_youtube_tests.py"
if [ -f "$VALIDATION_SCRIPT" ]; then
    python3 "$VALIDATION_SCRIPT"
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "✗ Test validation failed"
        echo "  Please check the test files"
        exit 1
    fi
else
    echo "⚠ Validation script not found, skipping..."
fi

echo ""
echo "======================================"
echo "🚀 Running YouTube Tests"
echo "======================================"
echo ""

# Check if a specific test was requested
TEST_NAME="$1"

if [ -n "$TEST_NAME" ]; then
    echo "Running test: $TEST_NAME"
    echo ""
    
    # Map short names to full test names
    case "$TEST_NAME" in
        workflow)
            FULL_TEST_NAME="test_youtube_channel_download_workflow"
            ;;
        error)
            FULL_TEST_NAME="test_youtube_channel_download_error_handling"
            ;;
        streaming)
            FULL_TEST_NAME="test_youtube_channel_log_streaming"
            ;;
        config)
            FULL_TEST_NAME="test_youtube_channel_configuration_persistence"
            ;;
        *)
            FULL_TEST_NAME="$TEST_NAME"
            ;;
    esac
    
    TEST_PATH="_meta/tests/integration/test_youtube_channel_download.py::$FULL_TEST_NAME"
else
    echo "Running all YouTube tests..."
    echo ""
    TEST_PATH="_meta/tests/integration/test_youtube_channel_download.py"
fi

# Run the tests with verbose output
python3 -m pytest "$TEST_PATH" -v -s --tb=short --color=yes

# Store exit code
TEST_EXIT_CODE=$?

echo ""
echo "======================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "⚠ Tests completed with exit code: $TEST_EXIT_CODE"
    echo ""
    echo "Note: Some tests may fail if yt-dlp is not installed."
    echo "This is expected behavior."
fi

echo "======================================"
echo ""

# Show next steps
echo "Next steps:"
echo "  • Review the test output above"
echo "  • Check logs for detailed execution information"
echo "  • Read README_YOUTUBE_TESTS.md for more information"
echo ""

exit $TEST_EXIT_CODE
