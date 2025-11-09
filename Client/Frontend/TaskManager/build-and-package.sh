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
DEPLOY_PACKAGE_DIR="$SCRIPT_DIR/deploy-package"
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

# Step 4: Create deployment package
print_step "Creating deployment package..."

# Remove old package
rm -rf "$DEPLOY_PACKAGE_DIR"
mkdir -p "$DEPLOY_PACKAGE_DIR"

# Copy built files
cp -r dist/* "$DEPLOY_PACKAGE_DIR/"
print_info "Copied dist/ files"

# Copy deployment scripts
cp deploy.php "$DEPLOY_PACKAGE_DIR/"
cp deploy-auto.php "$DEPLOY_PACKAGE_DIR/"
cp public/deploy-deploy.php "$DEPLOY_PACKAGE_DIR/"
cp public/.htaccess.example "$DEPLOY_PACKAGE_DIR/"
print_info "Copied deployment scripts"

# Create .htaccess from example
if [[ -f "$DEPLOY_PACKAGE_DIR/.htaccess.example" ]]; then
    cp "$DEPLOY_PACKAGE_DIR/.htaccess.example" "$DEPLOY_PACKAGE_DIR/.htaccess"
    print_info "Created .htaccess from example"
fi

# Step 5: Create README for deployment
cat > "$DEPLOY_PACKAGE_DIR/README_DEPLOYMENT.txt" << EOF
Frontend/TaskManager - Deployment Package
==========================================

Build Date: $(date)
Build Script: build-and-package.sh
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
1. Upload entire contents of this directory to your web root
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
3. Re-upload deploy-package/

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
tar -czf "deploy-package-${TIMESTAMP}.tar.gz" -C deploy-package .
TAR_SIZE=$(du -sh "deploy-package-${TIMESTAMP}.tar.gz" 2>/dev/null | cut -f1)
print_success "Created deploy-package-${TIMESTAMP}.tar.gz ($TAR_SIZE)"

# Create zip (for Windows)
if command -v zip &> /dev/null; then
    cd deploy-package
    zip -r "../deploy-package-${TIMESTAMP}.zip" . -q
    cd ..
    ZIP_SIZE=$(du -sh "deploy-package-${TIMESTAMP}.zip" 2>/dev/null | cut -f1)
    print_success "Created deploy-package-${TIMESTAMP}.zip ($ZIP_SIZE)"
else
    print_info "zip not available, skipping .zip creation"
fi

# Step 7: Create latest symlinks
print_step "Creating convenience links..."
rm -f deploy-package-latest.tar.gz deploy-package-latest.zip
ln -sf "deploy-package-${TIMESTAMP}.tar.gz" deploy-package-latest.tar.gz
if [[ -f "deploy-package-${TIMESTAMP}.zip" ]]; then
    ln -sf "deploy-package-${TIMESTAMP}.zip" deploy-package-latest.zip
fi
print_success "Created latest links"

# Summary
print_header "Build Complete!"

echo -e "\n${GREEN}📦 Deployment Package Ready!${NC}\n"
echo "Package Location:"
echo "  Directory: $DEPLOY_PACKAGE_DIR"
echo "  Archive:   deploy-package-${TIMESTAMP}.tar.gz"
if [[ -f "deploy-package-${TIMESTAMP}.zip" ]]; then
    echo "  Archive:   deploy-package-${TIMESTAMP}.zip"
fi
echo ""

echo "Next Steps:"
echo "  1. Upload deploy-package/ to your web server"
echo "  2. Open deploy.php in browser to complete setup"
echo "  3. Or extract archive: tar -xzf deploy-package-${TIMESTAMP}.tar.gz"
echo ""

echo "Quick Commands:"
echo "  View contents:    ls -lh $DEPLOY_PACKAGE_DIR"
echo "  Test locally:     cd $DEPLOY_PACKAGE_DIR && python3 -m http.server 8080"
echo "  Upload via SCP:   scp -r $DEPLOY_PACKAGE_DIR/* user@server:/var/www/html/"
echo ""

print_success "All done! 🎉"
