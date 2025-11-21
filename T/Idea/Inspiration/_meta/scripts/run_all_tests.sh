#!/bin/bash
# Run all tests across core modules with coverage

set -e  # Exit on error

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    PrismQ.IdeaInspiration - Test Runner                      ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

run_module_tests() {
    local module=$1
    local test_dir=$2
    local cov_src=$3
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Testing: $module"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    cd "$REPO_ROOT/$module"
    
    if [ ! -d "$test_dir" ]; then
        echo -e "${YELLOW}⚠ No tests directory found${NC}"
        return
    fi
    
    PYTHONPATH=.:$PYTHONPATH python -m pytest "$test_dir" \
        --cov="$cov_src" \
        --cov-report=term \
        --cov-report=html:htmlcov \
        -v --tb=short 2>&1 | tee test_output.log
    
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Tests passed${NC}"
    else
        echo -e "${RED}✗ Tests failed${NC}"
    fi
    
    echo ""
    cd "$REPO_ROOT"
    return $exit_code
}

# Track overall status
overall_status=0

# Run tests for each module
run_module_tests "Scoring" "_meta/tests" "src" || overall_status=1
run_module_tests "Classification" "_meta/tests" "prismq" || overall_status=1
run_module_tests "Model" "tests" "idea_inspiration" || overall_status=1
run_module_tests "ConfigLoad" "tests" "." || overall_status=1

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                              Test Summary                                    ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

if [ $overall_status -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Coverage reports available at:"
    echo "  - Scoring/htmlcov/index.html"
    echo "  - Classification/htmlcov/index.html"
    echo "  - Model/htmlcov/index.html"
    echo "  - ConfigLoad/htmlcov/index.html"
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Check individual module logs for details."
fi

echo ""
echo "For detailed coverage analysis, run:"
echo "  python _meta/scripts/analyze_coverage.py"

exit $overall_status
