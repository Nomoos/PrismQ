#!/bin/bash
# PrismQ Client - Installation Validation Script
# Checks the state of the Client implementation

set -e

echo "🔍 PrismQ Client - Installation Check"
echo "======================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
ISSUES_FOUND=0

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    local status=$1
    local message=$2
    
    if [ "$status" = "ok" ]; then
        echo -e "${GREEN}✅${NC} $message"
    elif [ "$status" = "warn" ]; then
        echo -e "${YELLOW}⚠️${NC}  $message"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${RED}❌${NC} $message"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
}

# Check Python
echo "📦 Checking Prerequisites..."
echo "----------------------------"

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_status "ok" "Python 3 installed: $PYTHON_VERSION"
else
    print_status "fail" "Python 3 not found"
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status "ok" "Node.js installed: $NODE_VERSION"
else
    print_status "fail" "Node.js not found"
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_status "ok" "npm installed: $NPM_VERSION"
else
    print_status "fail" "npm not found"
fi

echo ""
echo "🔧 Checking Backend..."
echo "----------------------"

# Check if in correct directory
if [ ! -f "Backend/requirements.txt" ]; then
    echo "❌ Error: Must run from Client directory"
    echo "   cd /path/to/PrismQ.IdeaInspiration/Client"
    exit 1
fi

# Check Backend dependencies
cd Backend

if [ -d "src" ]; then
    print_status "ok" "Backend source directory exists"
else
    print_status "fail" "Backend source directory not found"
fi

# Try to import main modules
if python3 -c "import fastapi, uvicorn, pydantic" 2>/dev/null; then
    print_status "ok" "Backend dependencies installed"
else
    print_status "warn" "Backend dependencies not installed (run: pip install -r requirements.txt)"
fi

# Check if tests can be discovered
if [ -d "../_meta/tests/Backend" ]; then
    TEST_COUNT=$(find ../_meta/tests/Backend -name "test_*.py" | wc -l)
    print_status "ok" "Backend tests found: $TEST_COUNT test files"
else
    print_status "warn" "Backend test directory not found"
fi

cd ..

echo ""
echo "🎨 Checking Frontend..."
echo "-----------------------"

cd Frontend

if [ -d "src" ]; then
    print_status "ok" "Frontend source directory exists"
else
    print_status "fail" "Frontend source directory not found"
fi

if [ -d "node_modules" ]; then
    print_status "ok" "Frontend dependencies installed"
else
    print_status "warn" "Frontend dependencies not installed (run: npm install)"
fi

# Check if Vue components exist
VUE_COMPONENTS=$(find src/components -name "*.vue" 2>/dev/null | wc -l)
if [ "$VUE_COMPONENTS" -gt 0 ]; then
    print_status "ok" "Vue components found: $VUE_COMPONENTS components"
else
    print_status "warn" "No Vue components found"
fi

cd ..

echo ""
echo "📝 Checking Documentation..."
echo "----------------------------"

if [ -f "CLIENT_STATUS_REPORT.md" ]; then
    print_status "ok" "Client status report exists"
else
    print_status "warn" "Client status report not found"
fi

if [ -f "README.md" ]; then
    print_status "ok" "README.md exists"
else
    print_status "warn" "README.md not found"
fi

if [ -f "_meta/doc/README.md" ]; then
    print_status "ok" "Documentation directory exists"
else
    print_status "warn" "Documentation directory not found"
fi

echo ""
echo "🏗️  Checking Implementation Status..."
echo "--------------------------------------"

# Count completed issues
# Note: Issue number patterns are hardcoded based on current Phase 0 web client issues (#101-112)
# Update these patterns if issue numbering scheme changes
DONE_ISSUES=$(find ../_meta/issues/done -name "10[1-7]-*.md" 2>/dev/null | wc -l)
NEW_ISSUES=$(find ../_meta/issues/new -name "10[8-9]-*.md" -o -name "11[0-2]-*.md" 2>/dev/null | wc -l)

if [ "$DONE_ISSUES" -eq 7 ]; then
    print_status "ok" "Phase 1-2 complete: 7 issues done"
else
    print_status "warn" "Phase 1-2 status: $DONE_ISSUES/7 issues done"
fi

if [ "$NEW_ISSUES" -eq 5 ]; then
    print_status "ok" "Phase 3-4 pending: 5 issues remaining"
else
    print_status "warn" "Phase 3-4 status: $NEW_ISSUES/5 issues pending"
fi

echo ""
echo "======================================"

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "To run the application:"
    echo "  Backend:  cd Backend && uvicorn src.main:app --reload"
    echo "  Frontend: cd Frontend && npm run dev"
    echo ""
    echo "To run tests:"
    echo "  Backend:  cd Backend && pytest ../_meta/tests/Backend/ -v"
    echo "  Frontend: cd Frontend && npm test"
    exit 0
else
    echo -e "${YELLOW}⚠️  Found $ISSUES_FOUND issues${NC}"
    echo ""
    echo "See CLIENT_STATUS_REPORT.md for details"
    echo ""
    echo "To install dependencies:"
    echo "  Backend:  cd Backend && pip install -r requirements.txt"
    echo "  Frontend: cd Frontend && npm install"
    exit 1
fi
