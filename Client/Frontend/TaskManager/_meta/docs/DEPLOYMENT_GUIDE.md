# Deployment Guide - Frontend/TaskManager

**Version:** 1.0.0  
**Last Updated:** 2025-11-11  
**Target Platform:** Vedos/Wedos Shared Hosting

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Deployment Process](#detailed-deployment-process)
5. [Environment Configuration](#environment-configuration)
6. [Deployment Methods](#deployment-methods)
7. [Verification & Testing](#verification--testing)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Procedures](#rollback-procedures)
10. [Advanced Topics](#advanced-topics)

## Overview

This guide provides comprehensive instructions for deploying the Frontend/TaskManager application to production and staging environments. The application is designed for deployment on Vedos/Wedos shared hosting but can be deployed to any web server with static file hosting capabilities.

### What Gets Deployed

The deployment package contains:
- **Static Assets**: JavaScript bundles, CSS, images
- **Entry Point**: index.html (SPA entry)
- **Deployment Scripts**: PHP-based deployment utilities
- **Server Configuration**: .htaccess for Apache SPA routing

**Bundle Characteristics:**
- Total Size: ~236KB (71KB gzipped)
- Load Time: 1.5-2.1s on 3G
- Lighthouse Score: 99-100/100

### Architecture

Frontend/TaskManager is a **static single-page application (SPA)** that:
- Runs entirely in the browser
- Requires no server-side runtime (except for deployment scripts)
- Connects to Backend/TaskManager REST API
- Uses Vue Router for client-side routing

## Prerequisites

### Development Environment

**Required:**
- Node.js 18.0.0 or higher
- npm 9.0.0 or higher
- Git (for version control)

**Optional but Recommended:**
- FTP/SFTP client (FileZilla, WinSCP)
- SSH access to server (for automated deployments)

### Server Requirements

**Minimum:**
- Web server (Apache 2.4+, Nginx 1.18+)
- PHP 7.4+ (only for deployment scripts, not app runtime)
- HTTPS enabled (strongly recommended)
- 50MB disk space

**For Apache SPA Routing:**
- mod_rewrite enabled
- .htaccess support enabled (AllowOverride All)

**For Nginx SPA Routing:**
- Configure try_files directive in server block

### Backend Dependencies

- Backend/TaskManager API must be deployed and operational
- API endpoint must be accessible from frontend domain
- CORS configured if frontend/backend on different domains

### Access Requirements

**For FTP Deployment:**
- FTP/SFTP credentials
- Write access to web root directory

**For SSH Deployment:**
- SSH credentials
- Shell access to web root
- PHP CLI available

## Quick Start

Follow these three steps for a basic deployment:

### Step 1: Build the Package

**On Windows:**
```cmd
cd Frontend\TaskManager
build-and-package.bat
```

**On Linux/Mac:**
```bash
cd Frontend/TaskManager
./build-and-package.sh
```

This creates `deploy-package/` directory with all deployment files.

### Step 2: Upload to Server

**Via FTP/SFTP:**
1. Connect to your hosting server
2. Navigate to web root (e.g., `/www/` or `/public_html/`)
3. Upload entire contents of `deploy-package/` directory
4. Ensure proper file permissions (644 for files, 755 for directories)

**Via Control Panel:**
1. Compress `deploy-package/` to ZIP
2. Login to hosting control panel
3. Upload ZIP via File Manager
4. Extract in web root

### Step 3: Configure & Verify

1. Open `https://your-domain.com/deploy.php` in browser
2. Click "Run Environment Check"
3. Review system requirements
4. Click "Proceed with Setup"
5. Open `https://your-domain.com/` to verify deployment

## Detailed Deployment Process

### Phase 1: Pre-Deployment

#### 1.1 Code Quality Verification

Run all checks before building:

```bash
cd Frontend/TaskManager

# Type checking
npm run build

# Linting
npm run lint

# Unit tests
npm test

# E2E tests
npm run test:e2e

# Bundle size check
npm run bundle:check
```

**Quality Gates:**
- ✅ TypeScript: 0 errors
- ✅ ESLint: All checks passing
- ✅ Tests: >96% pass rate
- ✅ Bundle: <500KB
- ✅ Coverage: >80%

#### 1.2 Environment Preparation

Create and configure `.env` file:

```bash
# Copy template
cp .env.production.example .env

# Edit with production values
nano .env
```

**Required Variables:**
```bash
# API Configuration
VITE_API_BASE_URL=https://api.your-domain.com/api
VITE_API_KEY=your-production-api-key

# Application Settings
VITE_APP_ENV=production
VITE_APP_NAME=TaskManager
```

**Optional but Recommended:**
```bash
# Sentry Error Tracking
VITE_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
VITE_SENTRY_ENVIRONMENT=production
VITE_SENTRY_ENABLED=true

# Debug Settings
VITE_ENABLE_DEBUG=false
VITE_ENABLE_CONSOLE_LOGS=false
```

#### 1.3 Documentation Review

Verify documentation is current:
- [ ] CHANGELOG.md updated
- [ ] Version number incremented
- [ ] Breaking changes documented
- [ ] API changes documented

### Phase 2: Build Process

#### 2.1 Standard Build

```bash
cd Frontend/TaskManager
./build-and-package.sh
```

**Process Steps:**
1. Validates Node.js/npm versions
2. Installs/updates dependencies
3. Runs TypeScript compilation
4. Builds production bundle with Vite
5. Copies deployment scripts
6. Creates timestamped archives

**Output Files:**
```
deploy-package/                           # Ready-to-upload directory
deploy-package-YYYYMMDD_HHMMSS.tar.gz    # Linux/Mac archive
deploy-package-YYYYMMDD_HHMMSS.zip       # Windows archive
deploy-package-latest.tar.gz             # Symlink to latest
```

#### 2.2 Clean Build

For critical deployments or after dependency changes:

```bash
./build-and-package.sh --clean
```

This removes `node_modules/` and rebuilds from scratch.

#### 2.3 Build Verification

Test the build locally before uploading:

```bash
cd deploy-package
python3 -m http.server 8080
```

Open http://localhost:8080 and verify:
- [ ] App loads without errors
- [ ] All routes work correctly
- [ ] API connection configurable
- [ ] No console errors
- [ ] Mobile responsive

### Phase 3: Deployment

#### 3.1 Staging Deployment

Always deploy to staging first:

```bash
# Use staging environment
cp .env.staging.example .env
# Edit .env with staging values

# Build for staging
./build-and-package.sh

# Upload to staging server
# (Use Method 1, 2, or 3 below)
```

**Staging Verification:**
1. Functional testing
2. API integration testing
3. Performance testing
4. Accessibility testing
5. Cross-browser testing

#### 3.2 Production Deployment

Only deploy to production after staging validation:

```bash
# Use production environment
cp .env.production.example .env
# Edit .env with production values

# Build for production
./build-and-package.sh

# Upload to production server
# (Use Method 1, 2, or 3 below)
```

### Phase 4: Post-Deployment

#### 4.1 Immediate Verification

Within 5 minutes of deployment:

```bash
# Test critical paths
curl -I https://your-domain.com/
curl -I https://your-domain.com/api/health

# Check error logs
tail -f /var/log/apache2/error.log
```

Browser checks:
- [ ] Home page loads
- [ ] API connection works
- [ ] Authentication works
- [ ] No console errors
- [ ] No 404 errors

#### 4.2 Monitoring Setup

Configure monitoring:
- Set up Sentry error tracking
- Configure uptime monitoring
- Set up performance monitoring
- Enable analytics (if applicable)

**See:** [MONITORING_SETUP.md](./MONITORING_SETUP.md) for details.

## Environment Configuration

### Environment Variables

Environment variables are **compiled into the build** at build time. You must rebuild after changing any variable.

#### Core Variables

```bash
# API Configuration (Required)
VITE_API_BASE_URL=https://api.example.com/api
VITE_API_KEY=your-api-key-here

# Application Configuration (Required)
VITE_APP_ENV=production
VITE_APP_NAME=TaskManager
```

#### Error Tracking (Recommended)

```bash
# Sentry Configuration
VITE_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
VITE_SENTRY_ENVIRONMENT=production
VITE_SENTRY_ENABLED=true
VITE_SENTRY_TRACES_SAMPLE_RATE=0.1
VITE_SENTRY_REPLAYS_SESSION_SAMPLE_RATE=0.1
```

**Free Tier:** 5,000 errors/month

**See:** [SENTRY_SETUP.md](./SENTRY_SETUP.md) for complete Sentry configuration.

#### Debug Settings

```bash
# Only enable in development/staging
VITE_ENABLE_DEBUG=false
VITE_ENABLE_CONSOLE_LOGS=false
```

### Environment Templates

The repository includes three environment templates:

1. **`.env.example`** - Development environment
2. **`.env.staging.example`** - Staging environment
3. **`.env.production.example`** - Production environment

Copy the appropriate template and customize for your needs.

## Deployment Methods

### Method 1: FTP/SFTP Upload (Recommended)

**Best for:** Initial deployments, manual deployments, shared hosting

**Steps:**

1. Build the package locally:
   ```bash
   ./build-and-package.sh
   ```

2. Connect via FTP/SFTP:
   ```bash
   # Using lftp (Linux)
   lftp -u username,password sftp://your-server.com
   
   # Or use FileZilla GUI client
   ```

3. Upload files:
   ```bash
   cd /www/your-site/
   mput -r deploy-package/*
   ```

4. Set permissions:
   ```bash
   # Files: 644
   chmod -R 644 *
   
   # Directories: 755
   chmod -R 755 */
   
   # PHP scripts: 755
   chmod 755 *.php
   ```

5. Configure via browser:
   - Open `https://your-domain.com/deploy.php`
   - Follow setup wizard

**Pros:**
- Simple and reliable
- Works everywhere
- Good for initial setup
- Visual feedback

**Cons:**
- Manual process
- Slower for large files
- No automation

### Method 2: SSH/SCP Upload (Fast)

**Best for:** Regular updates, automated deployments, SSH access available

**Steps:**

1. Build and transfer:
   ```bash
   ./build-and-package.sh
   scp deploy-package-latest.tar.gz user@server:/tmp/
   ```

2. Deploy on server:
   ```bash
   ssh user@server
   cd /www/your-site/
   php deploy-auto.php --source=/tmp/deploy-package-latest.tar.gz
   ```

3. Verify:
   ```bash
   curl -I https://your-domain.com/
   ```

**Pros:**
- Fast deployment
- Scriptable/automatable
- Atomic updates
- Less bandwidth usage

**Cons:**
- Requires SSH access
- More technical
- Command-line only

### Method 3: URL-Based Deployment (Advanced)

**Best for:** CI/CD pipelines, remote deployments, automated workflows

**Steps:**

1. Host the package:
   ```bash
   # Upload to temporary server/CDN
   ./build-and-package.sh
   scp deploy-package-latest.tar.gz cdn.example.com:/public/
   ```

2. Deploy from URL:
   ```bash
   ssh user@server
   cd /www/your-site/
   php deploy-auto.php --source=https://cdn.example.com/public/deploy-package-latest.tar.gz
   ```

**Pros:**
- CI/CD friendly
- Remote deployment
- No direct upload needed
- Repeatable

**Cons:**
- Requires hosting setup
- More complex
- Security considerations

### Method 4: Control Panel Upload

**Best for:** Vedos/Wedos users, GUI preference, no FTP client

**Steps:**

1. Create ZIP archive:
   ```bash
   ./build-and-package.sh
   cd ..
   zip -r frontend-deploy.zip deploy-package/*
   ```

2. Upload via control panel:
   - Login to Vedos/Wedos panel
   - Navigate to File Manager
   - Upload `frontend-deploy.zip`
   - Extract in web root

3. Configure:
   - Open `https://your-domain.com/deploy.php`
   - Follow wizard

**Pros:**
- No additional tools needed
- Familiar interface
- Easy for beginners

**Cons:**
- File size limits (typically 100MB)
- Slower than FTP
- Less automation potential

## Verification & Testing

### Post-Deployment Checklist

#### 1. Application Health

```bash
# Check HTTP status
curl -I https://your-domain.com/

# Expected: HTTP/2 200
# Expected: content-type: text/html
```

#### 2. API Connectivity

```bash
# Test API endpoint
curl https://your-domain.com/api/health

# Or from browser console
fetch('/api/health').then(r => r.json()).then(console.log)
```

#### 3. Frontend Functionality

Manual testing:
- [ ] Home page loads
- [ ] Navigation works
- [ ] Task list displays
- [ ] Task creation works
- [ ] Task detail view works
- [ ] Settings page accessible
- [ ] Mobile responsive
- [ ] No console errors

#### 4. Performance Testing

```bash
# Lighthouse test
npm run lighthouse

# Expected scores:
# Performance: >90
# Accessibility: >90
# Best Practices: >90
# SEO: >90
```

#### 5. Cross-Browser Testing

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

#### 6. Error Tracking

Verify Sentry is receiving events:
1. Trigger a test error
2. Check Sentry dashboard
3. Verify error appears
4. Check source maps are working

**See:** [SENTRY_TESTING.md](./SENTRY_TESTING.md)

### Load Testing

For production deployments:

```bash
# Simple load test
ab -n 1000 -c 10 https://your-domain.com/

# Expected:
# Requests per second: >100
# Time per request: <100ms
# Failed requests: 0
```

### Security Testing

```bash
# Check HTTPS
curl -I https://your-domain.com/ | grep -i "strict-transport"

# Check headers
curl -I https://your-domain.com/ | grep -i "x-frame-options"
curl -I https://your-domain.com/ | grep -i "x-content-type"
```

## Troubleshooting

### Common Issues

#### Issue: White Screen / Blank Page

**Symptoms:**
- Page loads but shows nothing
- No errors in browser console

**Causes:**
1. Incorrect base URL in build
2. Missing .htaccess
3. API not accessible

**Solutions:**
```bash
# Check browser console for errors
# Open DevTools → Console

# Verify .htaccess exists
ls -la .htaccess

# Check API connectivity
curl https://your-api-url.com/api/health

# Rebuild with correct API URL
# Edit .env → VITE_API_BASE_URL
./build-and-package.sh
# Re-upload
```

#### Issue: 404 on Page Refresh

**Symptoms:**
- Direct navigation works
- Page refresh returns 404
- Deep links return 404

**Causes:**
- SPA routing not configured
- .htaccess missing/not working
- mod_rewrite not enabled

**Solutions:**

For Apache:
```bash
# Verify .htaccess exists and is uploaded
cat .htaccess

# Content should include:
# RewriteEngine On
# RewriteRule . /index.html [L]

# Check if mod_rewrite is enabled
# Contact hosting support if needed
```

For Nginx:
```nginx
# Add to server block
location / {
    try_files $uri $uri/ /index.html;
}
```

#### Issue: API Connection Failed

**Symptoms:**
- "Failed to fetch" errors
- API requests fail
- CORS errors

**Causes:**
1. Wrong API URL in build
2. CORS not configured
3. API not running
4. Network/firewall issues

**Solutions:**
```bash
# Test API directly
curl https://your-api-url.com/api/health

# Check CORS headers
curl -I -H "Origin: https://your-domain.com" \
  https://your-api-url.com/api/health

# Rebuild with correct API URL
# Edit .env → VITE_API_BASE_URL=https://correct-url.com/api
./build-and-package.sh

# Configure CORS on backend
# Add your frontend domain to allowed origins
```

#### Issue: Bundle Too Large

**Symptoms:**
- Slow initial load
- Large file sizes
- Poor performance

**Solutions:**
```bash
# Analyze bundle
npm run build:analyze

# Check bundle size
npm run bundle:check

# Review imported libraries
# Remove unused dependencies
# Use dynamic imports for large components

# Rebuild
./build-and-package.sh
```

#### Issue: Deployment Script Errors

**Symptoms:**
- deploy.php shows errors
- PHP errors in logs

**Solutions:**
```bash
# Check PHP version
php -v
# Required: PHP 7.4+

# Check file permissions
ls -la deploy.php
# Should be: -rwxr-xr-x (755)

# Check PHP error log
tail -f /var/log/php_errors.log

# Test PHP is working
echo "<?php phpinfo(); ?>" > test.php
# Open https://your-domain.com/test.php
# Delete test.php after verification
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Edit .env
VITE_ENABLE_DEBUG=true
VITE_ENABLE_CONSOLE_LOGS=true

# Rebuild
./build-and-package.sh

# Re-upload
```

This enables:
- Verbose console logging
- API request/response logging
- Performance metrics logging
- Error details

**Remember:** Disable debug mode in production after troubleshooting.

### Getting Help

If issues persist:

1. Check documentation:
   - [QUICK_START.md](./QUICK_START.md)
   - [API_INTEGRATION.md](./API_INTEGRATION.md)
   - [DEPLOYMENT_RUNBOOK.md](./DEPLOYMENT_RUNBOOK.md)

2. Check logs:
   - Browser console (F12)
   - Server error logs
   - Sentry error dashboard

3. Contact support:
   - Check issue tracker
   - Review similar issues
   - Create new issue with details

## Rollback Procedures

### Emergency Rollback

If deployment causes critical issues:

**Quick Rollback (FTP):**
1. Keep previous version in `backup/` directory
2. Delete current files
3. Upload previous version
4. Verify site is working

**Quick Rollback (SSH):**
```bash
ssh user@server
cd /www/your-site/

# Restore from backup
cp -r backup/previous-version/* .

# Or re-deploy previous package
php deploy-auto.php --source=backup/deploy-package-previous.tar.gz

# Verify
curl -I https://your-domain.com/
```

### Rollback Best Practices

1. **Keep Backups:**
   ```bash
   # Before each deployment
   ssh user@server
   cd /www/your-site/
   tar -czf backup/$(date +%Y%m%d_%H%M%S).tar.gz .
   ```

2. **Test Rollback:**
   - Test rollback procedure in staging
   - Document rollback steps
   - Keep rollback scripts ready

3. **Monitor After Rollback:**
   - Verify functionality
   - Check error logs
   - Monitor user reports

**See:** [ROLLBACK_PROCEDURES.md](./ROLLBACK_PROCEDURES.md) for detailed procedures.

## Advanced Topics

### CI/CD Integration

#### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Build and Package
        run: |
          cd Frontend/TaskManager
          npm ci
          ./build-and-package.sh
      
      - name: Deploy via SSH
        run: |
          cd Frontend/TaskManager
          scp deploy-package-latest.tar.gz ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }}:/tmp/
          ssh ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} "cd /www/site && php deploy-auto.php --source=/tmp/deploy-package-latest.tar.gz"
```

### Multi-Environment Deployment

Manage multiple environments:

```bash
# environments/
├── .env.dev
├── .env.staging
├── .env.production
└── deploy-config.json

# Build for specific environment
./build-and-package.sh --env=staging
./build-and-package.sh --env=production
```

### Blue-Green Deployment

For zero-downtime deployments:

```bash
# Deploy to green environment
cd /www/site-green/
php deploy-auto.php --source=new-version.tar.gz

# Test green environment
curl https://green.your-domain.com/

# Switch traffic to green
# (Update load balancer or DNS)

# Keep blue as backup for rollback
```

### CDN Integration

Serve static assets from CDN:

1. Upload assets to CDN:
   ```bash
   # After building with build-and-package.sh
   cd deploy-package
   aws s3 sync assets/ s3://your-cdn-bucket/assets/
   ```

2. Configure CDN URL in build:
   ```bash
   # .env
   VITE_CDN_URL=https://cdn.your-domain.com
   ```

3. Update deployment to skip assets upload

### Performance Optimization

**Enable Compression:**
```apache
# .htaccess
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css text/javascript application/javascript
</IfModule>
```

**Enable Caching:**
```apache
# .htaccess
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
</IfModule>
```

**See:** [PERFORMANCE.md](./PERFORMANCE.md) for detailed optimization guide.

## Related Documentation

### Essential Reading
- **[Quick Start Guide](./QUICK_START.md)** - Fast deployment overview
- **[Deployment Runbook](./DEPLOYMENT_RUNBOOK.md)** - Operational procedures
- **[Rollback Procedures](./ROLLBACK_PROCEDURES.md)** - Emergency rollback guide

### Configuration & Setup
- **[API Integration](./API_INTEGRATION.md)** - Backend API configuration
- **[Sentry Setup](./SENTRY_SETUP.md)** - Error tracking setup
- **[Monitoring Setup](./MONITORING_SETUP.md)** - Production monitoring

### Reference Guides
- **[Quick Deployment Reference](./QUICK_DEPLOYMENT_REFERENCE.md)** - Command cheatsheet
- **[Staging Deployment Checklist](./STAGING_DEPLOYMENT_CHECKLIST.md)** - Staging procedures
- **[Performance Guide](./PERFORMANCE.md)** - Performance optimization
- **[Security Guide](./SECURITY.md)** - Security best practices

### Testing & Quality
- **[Testing Guide](./TESTING.md)** - Test procedures
- **[Sentry Testing](./SENTRY_TESTING.md)** - Error tracking testing

## Appendix

### File Structure Reference

```
deploy-package/
├── assets/                    # Static assets
│   ├── index-[hash].js       # Main application bundle
│   ├── vue-vendor-[hash].js  # Vue framework
│   ├── axios-vendor-[hash].js # HTTP client
│   └── index-[hash].css      # Styles
├── index.html                # SPA entry point
├── .htaccess                 # Apache configuration
├── deploy.php                # GUI deployment wizard
├── deploy-auto.php           # CLI deployment tool
├── deploy-deploy.php         # Legacy deployment script
└── README_DEPLOYMENT.txt     # Deployment instructions
```

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-11 | Initial comprehensive deployment guide |

### Glossary

- **SPA**: Single Page Application
- **SSR**: Server-Side Rendering (not used in this project)
- **CDN**: Content Delivery Network
- **CORS**: Cross-Origin Resource Sharing
- **FTP**: File Transfer Protocol
- **SSH**: Secure Shell
- **CLI**: Command Line Interface
- **GUI**: Graphical User Interface

---

**Author:** Worker08 - DevOps & Deployment Specialist  
**Review:** Worker10 - Senior Review Master  
**Status:** Production Ready  
**Last Updated:** 2025-11-11
