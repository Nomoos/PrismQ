#!/bin/bash
# Deployment Test Script
# Tests deployment package integrity and readiness
#
# Usage:
#   ./test-deployment.sh [staging|production]
#
# This script validates that the deployment package is ready
# to be uploaded to the target environment.

# Don't exit on error for test script
# set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# deploy-package/ is in Frontend/TaskManager/, not in _meta/scripts/
FRONTEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEPLOY_PACKAGE_DIR="$FRONTEND_DIR/deploy-package"
ENVIRONMENT="${1:-staging}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_test() {
    echo -e "\n${BLUE}TEST: $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((TESTS_PASSED++))
    ((TESTS_TOTAL++))
}

print_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((TESTS_FAILED++))
    ((TESTS_TOTAL++))
}

print_info() {
    echo -e "${YELLOW}ℹ INFO${NC}: $1"
}

# Start
print_header "Deployment Package Test Suite"
echo "Environment: $ENVIRONMENT"
echo "Package: $DEPLOY_PACKAGE_DIR"
echo ""

# Test 1: Package Directory Exists
print_test "Package directory exists"
if [[ -d "$DEPLOY_PACKAGE_DIR" ]]; then
    print_pass "deploy-package/ directory exists"
else
    print_fail "deploy-package/ directory not found. Run ./build-and-package.sh first"
    exit 1
fi

# Test 2: Required Files Present
print_test "Required files present"

required_files=(
    "index.html"
    ".htaccess"
    "deploy.php"
)

for file in "${required_files[@]}"; do
    if [[ -f "$DEPLOY_PACKAGE_DIR/$file" ]]; then
        print_pass "$file present"
    else
        print_fail "$file missing"
    fi
done

# Test 3: Assets Directory
print_test "Assets directory structure"

if [[ -d "$DEPLOY_PACKAGE_DIR/assets" ]]; then
    print_pass "assets/ directory exists"
    
    # Check for JavaScript files
    js_count=$(find "$DEPLOY_PACKAGE_DIR/assets" -name "*.js" | wc -l)
    if [[ $js_count -gt 0 ]]; then
        print_pass "Found $js_count JavaScript files"
    else
        print_fail "No JavaScript files found in assets/"
    fi
    
    # Check for CSS files
    css_count=$(find "$DEPLOY_PACKAGE_DIR/assets" -name "*.css" | wc -l)
    if [[ $css_count -gt 0 ]]; then
        print_pass "Found $css_count CSS files"
    else
        print_fail "No CSS files found in assets/"
    fi
else
    print_fail "assets/ directory missing"
fi

# Test 4: index.html Validation
print_test "index.html validation"

if [[ -f "$DEPLOY_PACKAGE_DIR/index.html" ]]; then
    # Check if it's a valid HTML file
    if grep -q "<!DOCTYPE html>" "$DEPLOY_PACKAGE_DIR/index.html"; then
        print_pass "Valid HTML DOCTYPE"
    else
        print_fail "Missing or invalid DOCTYPE"
    fi
    
    # Check for script tags (should have Vite-built scripts)
    if grep -q "<script" "$DEPLOY_PACKAGE_DIR/index.html"; then
        print_pass "Contains script tags"
    else
        print_fail "No script tags found"
    fi
    
    # Check for title
    if grep -q "<title>" "$DEPLOY_PACKAGE_DIR/index.html"; then
        title=$(grep -o "<title>.*</title>" "$DEPLOY_PACKAGE_DIR/index.html" | sed 's/<[^>]*>//g')
        print_pass "Title: '$title'"
    else
        print_fail "No title tag found"
    fi
fi

# Test 5: .htaccess Validation
print_test ".htaccess validation"

if [[ -f "$DEPLOY_PACKAGE_DIR/.htaccess" ]]; then
    # Check for RewriteEngine
    if grep -q "RewriteEngine On" "$DEPLOY_PACKAGE_DIR/.htaccess"; then
        print_pass "RewriteEngine configured"
    else
        print_fail "RewriteEngine not found"
    fi
    
    # Check for SPA routing
    if grep -q "RewriteRule.*index.html" "$DEPLOY_PACKAGE_DIR/.htaccess"; then
        print_pass "SPA routing configured"
    else
        print_fail "SPA routing not configured"
    fi
fi

# Test 6: Bundle Size Check
print_test "Bundle size validation"

if [[ -d "$DEPLOY_PACKAGE_DIR" ]]; then
    total_size=$(du -sk "$DEPLOY_PACKAGE_DIR" | cut -f1)
    total_size_mb=$((total_size / 1024))
    
    if [[ $total_size_mb -lt 1 ]]; then
        print_pass "Total package size: ${total_size}KB (< 1MB)"
    elif [[ $total_size_mb -lt 5 ]]; then
        print_pass "Total package size: ${total_size_mb}MB (acceptable)"
    else
        print_fail "Package size too large: ${total_size_mb}MB (should be < 5MB)"
    fi
    
    # Check individual asset sizes
    if [[ -d "$DEPLOY_PACKAGE_DIR/assets" ]]; then
        for js_file in "$DEPLOY_PACKAGE_DIR/assets"/*.js; do
            if [[ -f "$js_file" ]]; then
                size=$(du -k "$js_file" | cut -f1)
                if [[ $size -gt 500 ]]; then
                    print_info "Large JS file: $(basename "$js_file") - ${size}KB"
                fi
            fi
        done
    fi
fi

# Test 7: Health Check Files
print_test "Health check files"

if [[ -f "$DEPLOY_PACKAGE_DIR/health.json" ]]; then
    print_pass "health.json present"
    
    # Validate JSON syntax
    if command -v python3 &> /dev/null; then
        if python3 -c "import json; json.load(open('$DEPLOY_PACKAGE_DIR/health.json'))" 2>/dev/null; then
            print_pass "health.json is valid JSON"
        else
            print_fail "health.json is invalid JSON"
        fi
    fi
else
    print_info "health.json not found (optional)"
fi

if [[ -f "$DEPLOY_PACKAGE_DIR/health.html" ]]; then
    print_pass "health.html present"
else
    print_info "health.html not found (optional)"
fi

# Test 8: Deployment Scripts
print_test "Deployment scripts"

optional_scripts=(
    "deploy-deploy.php"
    "deploy-auto.php"
)

for script in "${optional_scripts[@]}"; do
    if [[ -f "$DEPLOY_PACKAGE_DIR/$script" ]]; then
        print_pass "$script present"
    else
        print_info "$script not found (optional)"
    fi
done

# Test 9: No Development Files
print_test "No development files included"

dev_patterns=(
    "*.map"
    "*.ts"
    "*.tsx"
    "node_modules"
    ".git"
    ".env"
)

found_dev_files=false
for pattern in "${dev_patterns[@]}"; do
    if find "$DEPLOY_PACKAGE_DIR" -name "$pattern" 2>/dev/null | grep -q .; then
        print_fail "Found development files: $pattern"
        found_dev_files=true
    fi
done

if [[ "$found_dev_files" == false ]]; then
    print_pass "No development files found"
fi

# Test 10: File Permissions Check
print_test "File permissions"

# Check that files are readable
if [[ -r "$DEPLOY_PACKAGE_DIR/index.html" ]]; then
    print_pass "Files are readable"
else
    print_fail "Files not readable"
fi

# Test 11: Environment-Specific Checks
print_test "Environment-specific validation ($ENVIRONMENT)"

if [[ "$ENVIRONMENT" == "staging" ]]; then
    # Check for staging configuration
    if grep -r "staging" "$DEPLOY_PACKAGE_DIR/health.json" 2>/dev/null; then
        print_pass "Staging environment detected in health.json"
    else
        print_info "Staging environment not specified in health.json"
    fi
elif [[ "$ENVIRONMENT" == "production" ]]; then
    # Check for production configuration
    if grep -r "console.log" "$DEPLOY_PACKAGE_DIR/assets"/*.js 2>/dev/null; then
        print_fail "console.log found in production build (should be removed)"
    else
        print_pass "No console.log in production build"
    fi
fi

# Test 12: Local Server Test (Optional)
print_test "Local server test (optional)"

if command -v python3 &> /dev/null; then
    print_info "You can test locally with: cd $DEPLOY_PACKAGE_DIR && python3 -m http.server 8080"
    print_info "Then open: http://localhost:8080"
else
    print_info "Python3 not available for local testing"
fi

# Summary
echo ""
print_header "Test Summary"

echo -e "\nTotal Tests: $TESTS_TOTAL"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "Deployment package is ready!"
    echo ""
    echo "Next steps:"
    echo "  1. Upload deploy-package/ to server"
    echo "  2. Run health check after deployment"
    echo "  3. Test application functionality"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please fix the issues above before deploying."
    echo ""
    exit 1
fi
