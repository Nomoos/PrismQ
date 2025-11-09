# TaskManager Deployment Guide

**Version**: 0.1.0  
**Last Updated**: 2025-11-09  
**Target Audience**: DevOps, System Administrators

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Local Deployment](#local-deployment)
4. [Production Deployment](#production-deployment)
5. [Vedos/Wedos Deployment](#vedoswedos-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Troubleshooting](#troubleshooting)
8. [Production Checklist](#production-checklist)

---

## Introduction

### About This Guide

This guide covers deployment of the Frontend/TaskManager application to various environments, with a focus on Vedos/Wedos hosting which is the primary deployment target.

### Deployment Options

1. **Local Development**: For testing and development
2. **Vedos/Wedos Hosting**: Primary production deployment
3. **Generic Web Server**: Apache, Nginx, or other static hosting

### Architecture

Frontend/TaskManager is a **Single Page Application (SPA)** that:
- Consists of static files (HTML, CSS, JavaScript)
- Requires client-side routing support
- Connects to Backend/TaskManager API
- Has no server-side rendering

---

## Prerequisites

### Development Machine

- **Node.js**: 18.0.0 or higher
- **npm**: 9.0.0 or higher
- **Git**: For source control

### Production Server

- **Web Server**: Apache 2.4+ or Nginx 1.18+
- **PHP**: 7.4+ (for deployment scripts)
- **HTTPS**: SSL certificate recommended
- **Domain**: Configured and pointing to server

### Access Requirements

- FTP/SFTP credentials for file upload
- SSH access (optional, for advanced setup)
- Domain DNS configuration access

---

## Local Deployment

### Development Server

For local development with hot reload:

```bash
cd Frontend/TaskManager
npm install
npm run dev
```

Access at: `http://localhost:5173`

### Local Production Build

To test production build locally:

```bash
# Build
npm run build

# Preview
npm run preview
```

Access at: `http://localhost:4173`

### Local with Backend

To test with local Backend/TaskManager:

1. Start Backend/TaskManager:
   ```bash
   cd Backend/TaskManager
   npm start
   ```

2. Configure Frontend environment (`.env`):
   ```env
   VITE_API_BASE_URL=http://localhost:8080
   VITE_API_KEY=your-local-api-key
   ```

3. Start Frontend:
   ```bash
   npm run dev
   ```

---

## Production Deployment

### Build Process

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Set Environment Variables**
   
   Create `.env.production`:
   ```env
   VITE_API_BASE_URL=https://api.yourdomain.com
   VITE_API_KEY=production-api-key
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

4. **Verify Build**
   ```bash
   # Check output
   ls -la dist/
   
   # Check bundle size
   npm run bundle:size
   ```

### Build Output

The `dist/` directory contains:

```
dist/
├── assets/
│   ├── index-[hash].js      # Main application bundle
│   ├── vendor-[hash].js     # Third-party libraries
│   └── index-[hash].css     # Compiled styles
├── index.html               # Entry point
└── favicon.ico              # Icon
```

### Deployment Methods

#### Method 1: FTP/SFTP Upload

1. Build locally (see above)
2. Connect to server via FTP/SFTP
3. Upload contents of `dist/` to web root
4. Configure web server (see below)

#### Method 2: Git Deploy (Advanced)

```bash
# On server
git clone <repo-url> /var/www/taskmanager
cd /var/www/taskmanager/Frontend/TaskManager
npm install
npm run build

# Serve dist/ directory
```

#### Method 3: CI/CD Pipeline

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install and Build
        run: |
          cd Frontend/TaskManager
          npm install
          npm run build
      
      - name: Deploy to Server
        uses: SamKirkland/FTP-Deploy-Action@4.3.0
        with:
          server: ${{ secrets.FTP_SERVER }}
          username: ${{ secrets.FTP_USERNAME }}
          password: ${{ secrets.FTP_PASSWORD }}
          local-dir: ./Frontend/TaskManager/dist/
```

---

## Vedos/Wedos Deployment

### Overview

Vedos/Wedos is a Czech hosting provider. This section provides step-by-step instructions for deploying to Vedos/Wedos hosting.

### Step 1: Prepare Build

On your local machine:

```bash
cd Frontend/TaskManager

# Install dependencies
npm install

# Create production environment file
cat > .env.production << EOF
VITE_API_BASE_URL=https://your-domain.cz/api
VITE_API_KEY=your-production-api-key
EOF

# Build for production
npm run build

# Verify build
ls -la dist/
```

### Step 2: Prepare Deployment Files

The repository includes deployment scripts:

- `deploy-deploy.php` - Deployment wizard launcher
- `deploy.php` - Main deployment script
- `.htaccess` - Apache configuration for SPA routing

These files handle:
- File uploads
- Environment configuration
- Health checks
- Deployment verification

### Step 3: Upload Files via FTP

1. **Connect to Vedos/Wedos FTP**:
   - Host: `ftp.yourdomain.cz`
   - Port: 21
   - Username: Your FTP username
   - Password: Your FTP password

2. **Create Directory Structure**:
   ```
   /www/
   └── taskmanager/
       ├── (upload dist/ contents here)
       ├── deploy-deploy.php
       └── deploy.php
   ```

3. **Upload Built Files**:
   - Upload all contents of `dist/` to `/www/taskmanager/`
   - Upload `deploy-deploy.php` to `/www/taskmanager/`
   - Upload `deploy.php` to `/www/taskmanager/`

### Step 4: Configure Apache

Create or update `.htaccess` in `/www/taskmanager/`:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /taskmanager/
  
  # Redirect to HTTPS (recommended)
  RewriteCond %{HTTPS} off
  RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
  
  # Handle SPA routing
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /taskmanager/index.html [L]
</IfModule>

# Security headers
<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set X-Frame-Options "SAMEORIGIN"
  Header set X-XSS-Protection "1; mode=block"
  
  # CORS (if needed)
  Header set Access-Control-Allow-Origin "https://your-api-domain.cz"
  Header set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
  Header set Access-Control-Allow-Headers "Content-Type, Authorization"
</IfModule>

# Compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript
</IfModule>

# Browser caching
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 0 seconds"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
</IfModule>
```

### Step 5: Run Deployment Wizard

1. **Access Deployment Wizard**:
   ```
   https://yourdomain.cz/taskmanager/deploy-deploy.php
   ```

2. **Follow Wizard Steps**:
   - Verify files uploaded
   - Configure environment variables
   - Test API connection
   - Run health check
   - Complete deployment

3. **Delete Deployment Scripts** (after successful deployment):
   ```
   # For security, remove these files
   rm deploy-deploy.php
   rm deploy.php
   ```

### Step 6: Verify Deployment

1. **Access Application**:
   ```
   https://yourdomain.cz/taskmanager/
   ```

2. **Check Health**:
   - Task List should load
   - Tasks should be fetchable from API
   - Navigation should work
   - No console errors

3. **Test Functionality**:
   - Configure Worker ID in Settings
   - View task details
   - Claim a task
   - Complete a task

### Step 7: Configure Domain (Optional)

If deploying to root domain or subdomain:

1. **In Vedos/Wedos Control Panel**:
   - Go to Domain Management
   - Point domain to `/www/taskmanager/`
   - Update SSL certificate

2. **Update `.htaccess`**:
   ```apache
   RewriteBase /
   RewriteRule . /index.html [L]
   ```

3. **Update Environment**:
   - Rebuild with correct base URL
   - Re-upload files

---

## Environment Configuration

### Environment Variables

Create `.env.production` before building:

```env
# API Configuration
VITE_API_BASE_URL=https://api.yourdomain.cz
VITE_API_KEY=your-production-api-key

# Application Configuration
VITE_APP_TITLE=TaskManager
VITE_APP_VERSION=0.1.0

# Feature Flags (optional)
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=false
```

### Runtime Configuration

For configuration that can't be embedded at build time, use the Settings view:

- **API Base URL**: Configurable in UI
- **API Key**: Configurable in UI (stored in localStorage)
- **Worker ID**: Configurable in UI (stored in localStorage)

### CORS Configuration

If Frontend and Backend are on different domains:

1. **Backend Configuration** (in Backend/TaskManager):
   ```javascript
   // Enable CORS
   app.use(cors({
     origin: 'https://frontend.yourdomain.cz',
     credentials: true
   }))
   ```

2. **Frontend Configuration**:
   - Already configured in Axios client
   - No additional changes needed

---

## Troubleshooting

### Issue: 404 Error on Refresh

**Symptom**: Direct navigation to `/tasks/123` returns 404

**Cause**: Server not configured for SPA routing

**Solution**: 
1. Ensure `.htaccess` is uploaded
2. Verify `mod_rewrite` is enabled on server
3. Check `RewriteBase` matches deployment path

### Issue: Blank Page After Deployment

**Symptom**: White screen, no content

**Cause**: JavaScript errors, wrong base path

**Solution**:
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify build was successful
4. Check `base` in `vite.config.ts` matches deployment path

### Issue: API Connection Failed

**Symptom**: "Failed to fetch tasks" error

**Cause**: Wrong API URL or CORS issue

**Solution**:
1. Go to Settings
2. Verify API Base URL is correct
3. Test API URL in browser: `https://api.yourdomain.cz/health`
4. Check CORS configuration on backend
5. Verify API key is correct

### Issue: Assets Not Loading

**Symptom**: Missing styles or JavaScript

**Cause**: Wrong asset paths

**Solution**:
1. Check browser network tab
2. Verify base path in build configuration
3. Rebuild if necessary
4. Re-upload files

### Issue: Slow Loading

**Symptom**: Application takes > 5 seconds to load

**Cause**: Large bundle, slow network

**Solution**:
1. Check bundle size: `npm run bundle:check`
2. Verify code splitting is working
3. Enable compression in `.htaccess`
4. Check server response times
5. Use CDN if available

---

## Production Checklist

### Pre-Deployment

- [ ] All tests passing (`npm run test`)
- [ ] No linting errors (`npm run lint`)
- [ ] TypeScript compiles without errors (`npm run build`)
- [ ] Bundle size < 500KB (`npm run bundle:check`)
- [ ] Environment variables configured
- [ ] API connection tested
- [ ] HTTPS certificate ready
- [ ] Backup existing deployment (if updating)

### During Deployment

- [ ] Build production bundle (`npm run build`)
- [ ] Verify build output (`ls -la dist/`)
- [ ] Upload files to server
- [ ] Configure `.htaccess`
- [ ] Run deployment wizard (if applicable)
- [ ] Verify file permissions
- [ ] Test basic navigation

### Post-Deployment

- [ ] Application loads successfully
- [ ] No console errors
- [ ] All routes accessible
- [ ] API connection working
- [ ] Task claiming works
- [ ] Task completion works
- [ ] Mobile responsive (test on device)
- [ ] Cross-browser compatibility
- [ ] Performance acceptable (Lighthouse > 90)
- [ ] Remove deployment scripts (`deploy-deploy.php`, `deploy.php`)

### Security

- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] No API keys in client code
- [ ] CORS properly configured
- [ ] No sensitive data exposed
- [ ] Deployment scripts removed

### Monitoring

- [ ] Error tracking configured (optional)
- [ ] Analytics configured (optional)
- [ ] Performance monitoring (optional)
- [ ] Health check endpoint working

---

## Rollback Procedure

If deployment fails or issues arise:

### Quick Rollback

1. **Restore Previous Version**:
   - Re-upload previous `dist/` files
   - Or restore from backup

2. **Verify**:
   - Test application
   - Check for errors
   - Confirm functionality

### Full Rollback

1. **Revert Git Commit**:
   ```bash
   git revert HEAD
   git push
   ```

2. **Rebuild Previous Version**:
   ```bash
   git checkout <previous-commit>
   npm install
   npm run build
   ```

3. **Re-deploy**:
   - Upload files
   - Verify

---

## Continuous Deployment

### Automated Deployment

For automatic deployment on git push:

1. **Set up CI/CD** (GitHub Actions, GitLab CI)
2. **Configure secrets** (FTP credentials, API keys)
3. **Create workflow** (see CI/CD Pipeline section above)
4. **Test workflow**
5. **Monitor deployments**

### Deployment Monitoring

After deployment:
- Monitor error logs
- Check performance metrics
- Review user feedback
- Track API errors
- Monitor bundle size over time

---

## Additional Resources

### Vedos/Wedos Documentation

- [Vedos Hosting Guide](https://www.vedos.cz/)
- [FTP Configuration](https://www.vedos.cz/podpora/)
- [SSL Certificates](https://www.vedos.cz/ssl/)

### General Resources

- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [Vue SPA Deployment](https://router.vuejs.org/guide/essentials/history-mode.html)
- [Apache mod_rewrite](https://httpd.apache.org/docs/current/mod/mod_rewrite.html)

---

## Support

For deployment issues:

1. **Check Troubleshooting Section** above
2. **Review Server Logs**
3. **Check Browser Console**
4. **Contact Hosting Support** (Vedos/Wedos)
5. **Contact Development Team**

---

**Last Updated**: 2025-11-09  
**Version**: 0.1.0
