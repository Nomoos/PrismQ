#!/bin/bash

# Release Readiness Check Script
# Validates that the project is ready for release
# Run from project root: ./_meta/_scripts/check-release-readiness.sh

set -e

echo "========================================="
echo "Release Readiness Check"
echo "========================================="
echo ""

ERRORS=0
WARNINGS=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error
error() {
    echo -e "${RED}✗${NC} $1"
    ERRORS=$((ERRORS + 1))
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

echo "1. Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    warning "Uncommitted changes found"
    git status --short
else
    success "Working directory clean"
fi
echo ""

echo "2. Checking version consistency..."
ROOT_VERSION=$(cat VERSION 2>/dev/null || echo "NOT_FOUND")
FRONTEND_VERSION=$(grep '"version":' Frontend/package.json | head -1 | sed 's/.*"version": "\(.*\)".*/\1/' 2>/dev/null || echo "NOT_FOUND")

echo "   Root VERSION: $ROOT_VERSION"
echo "   Frontend version: $FRONTEND_VERSION"

if [ "$ROOT_VERSION" = "NOT_FOUND" ]; then
    error "VERSION file not found"
elif [ "$ROOT_VERSION" != "$FRONTEND_VERSION" ]; then
    warning "Version mismatch: root=$ROOT_VERSION, frontend=$FRONTEND_VERSION"
else
    success "Version consistent: $ROOT_VERSION"
fi
echo ""

echo "3. Checking required files..."
REQUIRED_FILES=(
    "README.md"
    "RELEASE.md"
    "VERSION"
    "Frontend/package.json"
    "Backend/TaskManager/composer.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "$file exists"
    else
        error "$file missing"
    fi
done
echo ""

echo "4. Checking Frontend dependencies..."
cd Frontend
if [ ! -d "node_modules" ]; then
    warning "Frontend dependencies not installed"
    echo "   Run: cd Frontend && npm install"
else
    success "Frontend dependencies installed"
fi
cd ..
echo ""

echo "5. Running Frontend tests..."
cd Frontend
if [ ! -d "node_modules" ]; then
    warning "Frontend tests skipped (dependencies not installed)"
elif npm test -- --run > /tmp/frontend-test.log 2>&1; then
    success "Frontend tests passed"
else
    error "Frontend tests failed"
    echo "   See /tmp/frontend-test.log for details"
fi
cd ..
echo ""

echo "6. Running Frontend linter..."
cd Frontend
if [ ! -d "node_modules" ]; then
    warning "Frontend linter skipped (dependencies not installed)"
elif npm run lint > /tmp/frontend-lint.log 2>&1; then
    success "Frontend linter passed"
else
    warning "Frontend linter found issues"
    echo "   See /tmp/frontend-lint.log for details"
fi
cd ..
echo ""

echo "7. Checking Frontend build..."
cd Frontend
if [ ! -d "node_modules" ]; then
    warning "Frontend build skipped (dependencies not installed)"
elif npm run build > /tmp/frontend-build.log 2>&1; then
    success "Frontend build succeeded"
else
    error "Frontend build failed"
    echo "   See /tmp/frontend-build.log for details"
fi
cd ..
echo ""

echo "8. Running Backend TaskManager tests..."
cd Backend/TaskManager
if [ -f "tests/test.php" ]; then
    if php tests/test.php > /tmp/backend-test.log 2>&1; then
        success "Backend tests passed"
    else
        error "Backend tests failed"
        echo "   See /tmp/backend-test.log for details"
    fi
else
    warning "Backend test file not found"
fi
cd ../..
echo ""

echo "9. Validating composer.json..."
cd Backend/TaskManager
if composer validate --strict > /tmp/composer-validate.log 2>&1; then
    success "composer.json valid"
else
    warning "composer.json validation failed"
    echo "   See /tmp/composer-validate.log for details"
fi
cd ../..
echo ""

echo "10. Checking documentation..."
DOC_FILES=(
    "_meta/docs/SETUP.md"
    "_meta/docs/USER_GUIDE.md"
    "Backend/TaskManager/_meta/docs/API_REFERENCE.md"
)

for doc in "${DOC_FILES[@]}"; do
    if [ -f "$doc" ]; then
        success "$doc exists"
    else
        warning "$doc missing"
    fi
done
echo ""

echo "========================================="
echo "Summary"
echo "========================================="
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}✗ FAILED${NC}: $ERRORS error(s) found"
    echo "Please fix errors before creating a release"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ PASSED WITH WARNINGS${NC}: $WARNINGS warning(s) found"
    echo "Consider addressing warnings before release"
    exit 0
else
    echo -e "${GREEN}✓ PASSED${NC}: Ready for release!"
    exit 0
fi
