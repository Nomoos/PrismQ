#!/bin/bash
# Auto-Build and Package Script for Frontend/TaskManager
# Run this script before deployment to create a ready-to-upload package
#
# Usage:
#   ./build-and-package.sh
#   ./build-and-package.sh --clean  (rebuild from scratch)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR"
DIST_DIR="$SCRIPT_DIR/dist"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_step() {
    echo -e "\n${GREEN}➜ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Parse arguments
CLEAN_BUILD=false
if [[ "$1" == "--clean" ]]; then
    CLEAN_BUILD=true
fi

# Start
print_header "Frontend/TaskManager Auto-Build & Package"
echo "Build Date: $(date)"
echo "Working Directory: $FRONTEND_DIR"
echo ""

# Check if we're in the right directory
if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
    print_error "Error: package.json not found. Are you in Frontend/TaskManager directory?"
    exit 1
fi

# Step 1: Clean if requested
if [[ "$CLEAN_BUILD" == true ]]; then
    print_step "Cleaning previous build..."
    rm -rf node_modules dist deploy-package
    print_success "Clean complete"
fi

# Step 2: Install dependencies
print_step "Installing dependencies..."
if [[ ! -d "node_modules" ]]; then
    npm install --legacy-peer-deps
    print_success "Dependencies installed"
else
    print_info "Dependencies already installed (use --clean to reinstall)"
fi

# Step 3: Build production bundle
print_step "Building production bundle..."
npm run build
BUILD_SIZE=$(du -sh dist 2>/dev/null | cut -f1)
print_success "Build complete (Size: $BUILD_SIZE)"

# Step 4: Finalize deployment files in dist/
print_step "Finalizing deployment package in dist/..."

# Create .htaccess from example (if not already there)
if [[ -f "$DIST_DIR/.htaccess.example" ]] && [[ ! -f "$DIST_DIR/.htaccess" ]]; then
    cp "$DIST_DIR/.htaccess.example" "$DIST_DIR/.htaccess"
    print_success "Created .htaccess from example"
else
    print_info ".htaccess already exists or will be created by deploy.php"
fi

print_success "Deployment package ready in dist/ folder"

# Step 5: Create README for deployment
cat > "$DIST_DIR/README_DEPLOYMENT.txt" << EOF
Frontend/TaskManager - Deployment Package
==========================================

Build Date: $(date)
Build Script: npm run build (or build-and-package.sh)
Git Commit: $(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
Git Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "N/A")

Package Contents:
-----------------
- assets/          : Production build files (JS, CSS, images)
- index.html       : Main application entry point
- deploy.php       : Deployment wizard (open in browser)
- deploy-auto.php  : Automated deployment script (CLI)
- deploy-deploy.php: Script downloader
- .htaccess        : Apache SPA routing configuration
- .htaccess.example: Backup/template for .htaccess

Deployment Options:
-------------------

OPTION 1: Upload via FTP/SFTP (Recommended for Vedos/Wedos)
1. Upload all files from dist/ folder to your web root
2. Open https://your-domain.com/deploy.php in browser
3. Follow the deployment wizard

OPTION 2: Manual Setup
1. Upload all files to your web root
2. Ensure .htaccess is in place (for SPA routing)
3. Open https://your-domain.com/ in browser
4. Configure API connection in Settings page

OPTION 3: Automated CLI Deployment (if PHP CLI available)
1. Upload deploy-auto.php to server
2. SSH to server
3. Run: php deploy-auto.php --version=latest

Requirements:
-------------
- Web server with PHP 7.4+ (for deployment scripts only)
- Apache with mod_rewrite (or equivalent for SPA routing)
- Backend/TaskManager API running and accessible
- HTTPS recommended for production

Configuration:
--------------
The application is configured via environment variables at BUILD TIME.
To change API URL or other settings:
1. Edit Frontend/TaskManager/.env
2. Rebuild: npm run build
3. Re-upload dist/

Support:
--------
- Documentation: Frontend/TaskManager/README.md
- Issues: GitHub Issues
- API Docs: Frontend/TaskManager/docs/API_INTEGRATION.md

EOF

print_success "Created deployment README"

# Step 6: Create archive for easy download
print_step "Creating archives..."

cd "$FRONTEND_DIR"

# Create tar.gz (for Linux/Mac)
tar -czf "dist-package-${TIMESTAMP}.tar.gz" -C dist .
TAR_SIZE=$(du -sh "dist-package-${TIMESTAMP}.tar.gz" 2>/dev/null | cut -f1)
print_success "Created dist-package-${TIMESTAMP}.tar.gz ($TAR_SIZE)"

# Create zip (for Windows)
if command -v zip &> /dev/null; then
    cd dist
    zip -r "../dist-package-${TIMESTAMP}.zip" . -q
    cd ..
    ZIP_SIZE=$(du -sh "dist-package-${TIMESTAMP}.zip" 2>/dev/null | cut -f1)
    print_success "Created dist-package-${TIMESTAMP}.zip ($ZIP_SIZE)"
else
    print_info "zip not available, skipping .zip creation"
fi

# Step 7: Create latest symlinks
print_step "Creating convenience links..."
rm -f dist-package-latest.tar.gz dist-package-latest.zip
ln -sf "dist-package-${TIMESTAMP}.tar.gz" dist-package-latest.tar.gz
if [[ -f "dist-package-${TIMESTAMP}.zip" ]]; then
    ln -sf "dist-package-${TIMESTAMP}.zip" dist-package-latest.zip
fi
print_success "Created latest links"

# Summary
print_header "Build Complete!"

echo -e "\n${GREEN}📦 Deployment Package Ready!${NC}\n"
echo "Package Location:"
echo "  Directory: $DIST_DIR"
echo "  Archive:   dist-package-${TIMESTAMP}.tar.gz"
if [[ -f "dist-package-${TIMESTAMP}.zip" ]]; then
    echo "  Archive:   dist-package-${TIMESTAMP}.zip"
fi
echo ""

echo "Next Steps:"
echo "  1. Upload dist/ folder to your web server"
echo "  2. Open deploy.php in browser to complete setup"
echo "  3. Or extract archive: tar -xzf dist-package-${TIMESTAMP}.tar.gz"
echo ""

echo "Quick Commands:"
echo "  View contents:    ls -lh $DIST_DIR"
echo "  Test locally:     cd $DIST_DIR && python3 -m http.server 8080"
echo "  Upload via SCP:   scp -r $DIST_DIR/* user@server:/var/www/html/"
echo ""

print_success "All done! 🎉"
