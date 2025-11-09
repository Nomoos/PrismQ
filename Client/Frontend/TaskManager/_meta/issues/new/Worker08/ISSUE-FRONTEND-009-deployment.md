# ISSUE-FRONTEND-009: Deployment Automation

## Status
🔴 NOT STARTED

## Component
Frontend (Deployment)

## Type
DevOps / Deployment

## Priority
High

## Assigned To
Worker08 - DevOps & Deployment Specialist

## Description
Create automated deployment scripts for deploying Frontend to Vedos shared hosting, following the pattern established by Backend/TaskManager deployment.

## Problem Statement
The Frontend needs Vedos-compatible deployment that:
- Works on shared hosting without Node.js
- Deploys pre-built static files
- Configures SPA routing (.htaccess)
- Validates installation
- Handles environment configuration
- Provides simple upload and deploy process

## Solution
Implement deployment automation including:
1. PHP deployment script (`deploy.php`)
2. Deployment loader (`deploy-deploy.php`)
3. Environment configuration
4. .htaccess for SPA routing
5. Build process optimization
6. Post-deployment validation

## Deliverables

### Deployment Scripts
- [ ] `deploy-deploy.php` - Initial deployment loader
- [ ] `deploy.php` - Main deployment script
- [ ] `.htaccess` - Apache SPA routing configuration
- [ ] `build.sh` - Local build script
- [ ] Deployment documentation

### Build Configuration
- [ ] Vite production build config
- [ ] Environment variable handling
- [ ] Asset optimization
- [ ] Source map configuration
- [ ] Bundle analysis

### Environment Configuration
- [ ] `.env.example` template
- [ ] API URL configuration
- [ ] Environment-specific builds
- [ ] Configuration validation

### Validation & Testing
- [ ] Deployment health check
- [ ] File integrity verification
- [ ] Configuration validation
- [ ] SPA routing test

## Acceptance Criteria
- [ ] deploy-deploy.php created and tested
- [ ] deploy.php created and tested
- [ ] .htaccess for SPA routing working
- [ ] Build process optimized
- [ ] Environment configuration working
- [ ] Deployment tested on Vedos
- [ ] Rollback procedure documented
- [ ] Deployment guide complete

## Dependencies
- ISSUE-FRONTEND-005 (Performance) - Build optimization
- ISSUE-FRONTEND-004 (Core Components) - App to deploy
- Backend/TaskManager - API endpoint

## Related Issues
- Backend/TaskManager deployment (reference pattern)
- ISSUE-FRONTEND-010 (Review) - Pre-deployment review

## Deployment Architecture

### Vedos Hosting Requirements
- **Web Server**: Apache 2.4+
- **PHP**: 7.4+ (for deployment scripts only)
- **Modules**: mod_rewrite (for SPA routing)
- **Storage**: ~10-20 MB for app + assets
- **No Requirements**: Node.js, npm (build happens locally)

### Deployment Process
1. **Local Build**: Run `npm run build` locally
2. **Upload Loader**: Upload `deploy-deploy.php` to Vedos
3. **Execute Loader**: Access via browser to download deploy.php
4. **Run Deployment**: deploy.php downloads built files from GitHub
5. **Configure**: Set environment variables
6. **Validate**: Health check and routing test
7. **Complete**: Remove deployment scripts

## Deployment Scripts

### deploy-deploy.php
**Purpose**: Minimal bootstrap script  
**Size**: < 5KB  
**Function**: Downloads deploy.php from GitHub

```php
<?php
/**
 * Frontend Deployment Loader
 * 
 * Upload this single file to start deployment.
 * Access via browser: https://yourdomain.com/deploy-deploy.php
 */

// Download deploy.php from GitHub
// Execute deployment wizard
```

**Features**:
- Minimal dependencies
- Downloads latest deploy.php
- Validates checksum
- Launches deployment wizard

### deploy.php
**Purpose**: Main deployment script  
**Size**: ~30-40KB  
**Function**: Complete deployment automation

```php
<?php
/**
 * Frontend Deployment Script
 * 
 * Downloads built frontend files from GitHub and deploys to server.
 */

// Similar to Backend/TaskManager/deploy.php but for frontend
```

**Features**:
- Download built dist/ files from GitHub release
- Extract static files (HTML, CSS, JS, assets)
- Create .htaccess for SPA routing
- Configure environment (.env)
- Validate deployment
- Health check
- Rollback on failure

**Deployment Steps**:
1. Environment validation
2. Backup existing files (if any)
3. Download release archive
4. Extract static files
5. Create/update .htaccess
6. Configure environment
7. Validate routing
8. Test API connectivity
9. Success confirmation
10. Cleanup deployment scripts

### .htaccess
**Purpose**: Apache configuration for SPA routing

```apache
# Frontend SPA Routing
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  
  # Don't rewrite files or directories
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  
  # Rewrite everything else to index.html
  RewriteRule . /index.html [L]
</IfModule>

# Security Headers
<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set X-Frame-Options "DENY"
  Header set X-XSS-Protection "1; mode=block"
</IfModule>

# Compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript
</IfModule>

# Caching
<IfModule mod_expires.c>
  ExpiresActive On
  
  # HTML (no cache)
  ExpiresByType text/html "access plus 0 seconds"
  
  # Assets (1 year)
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType application/font-woff2 "access plus 1 year"
</IfModule>
```

## Build Process

### Production Build
```bash
# Build for production
npm run build

# Output: dist/
# - index.html
# - assets/
#   - *.js (code-split chunks)
#   - *.css (extracted styles)
#   - images/
#   - fonts/
```

### Build Optimization
- **Code Splitting**: Vendor chunks, route-based chunks
- **Tree Shaking**: Remove unused code
- **Minification**: Terser for JS, cssnano for CSS
- **Asset Optimization**: Image compression, font subsetting
- **Source Maps**: External (production.map.js)
- **Bundle Analysis**: Visualize bundle size

### Vite Configuration
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'ui': ['@headlessui/vue'] // if used
        }
      }
    },
    chunkSizeWarningLimit: 600
  }
});
```

## Environment Configuration

### .env.example
```env
# Frontend Environment Configuration

# API Configuration
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_API_KEY=your-api-key-here

# App Configuration
VITE_APP_NAME=PrismQ TaskManager
VITE_APP_ENV=production

# Feature Flags
VITE_ENABLE_OFFLINE=false
VITE_ENABLE_PWA=false
```

### Runtime Configuration
- Environment variables injected at build time (VITE_*)
- No runtime environment variable access (static build)
- Configuration must be determined at build time
- API URL configurable via .env

## Validation & Testing

### Health Check
Create `health.html` or check endpoint:
```javascript
// Check if app loads
// Check if SPA routing works
// Check if API is reachable
```

### Deployment Checklist
- [ ] Files uploaded successfully
- [ ] .htaccess working (mod_rewrite enabled)
- [ ] index.html loads
- [ ] SPA routing works (/tasks, /workers redirect to index.html)
- [ ] Static assets load (CSS, JS, images)
- [ ] API connectivity works
- [ ] Environment variables correct
- [ ] No console errors
- [ ] Mobile viewport correct

### Rollback Procedure
1. Keep backup of previous deployment
2. On failure, restore from backup
3. Revert .htaccess if needed
4. Restore .env configuration
5. Clear browser cache
6. Retest

## GitHub Release Integration

### Release Workflow
1. Developer runs `npm run build` locally
2. Commit dist/ files to GitHub (or create release artifact)
3. Tag release (e.g., v1.0.0)
4. deploy.php downloads from release tag
5. Extracts and deploys static files

**Alternative**: Use GitHub Actions to build and attach dist.zip to release

## Security Considerations

### Deployment Script Security
- API key authentication (similar to Backend)
- Checksum validation for downloads
- File permission checks
- Input validation
- SQL injection N/A (no database)

### .htaccess Security
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: enabled
- Disable directory listing
- Restrict access to sensitive files

### Production Build
- Remove source maps in production (optional)
- Minify all code
- No console.log statements
- No development dependencies

## Performance Optimization

### Build Output Targets
- **Initial Bundle**: < 500KB (gzipped)
- **Vendor Chunk**: < 300KB
- **App Chunk**: < 200KB
- **Route Chunks**: < 100KB each

### Optimization Techniques
- Code splitting by route
- Lazy loading components
- Tree shaking
- Image optimization (WebP)
- Font subsetting
- Preload critical assets
- Prefetch route chunks

## Documentation

### Deployment Guide
- [ ] Step-by-step deployment instructions
- [ ] Environment configuration guide
- [ ] Troubleshooting common issues
- [ ] Rollback procedures
- [ ] Updating deployed app

### Developer Guide
- [ ] Local build instructions
- [ ] Environment setup
- [ ] Build optimization tips
- [ ] Testing deployment locally

## Timeline
- **Start**: After ISSUE-FRONTEND-005 (Performance)
- **Duration**: 1 week
- **Target**: Week 4

## Success Criteria
- ✅ deploy-deploy.php working
- ✅ deploy.php working
- ✅ .htaccess SPA routing working
- ✅ Successfully deployed to Vedos
- ✅ Health check passing
- ✅ API connectivity working
- ✅ Rollback procedure tested
- ✅ Documentation complete

## Reference
- Backend/TaskManager/deploy.php - Deployment pattern
- Backend/TaskManager/deploy-deploy.php - Loader pattern

---

**Created By**: Worker01 (Project Manager)  
**Date**: 2025-11-09  
**Assigned To**: Worker08 (DevOps & Deployment)  
**Status**: 🔴 NOT STARTED  
**Priority**: High
