# Deployment Guide - Frontend/TaskManager

Simple guide for building and deploying Frontend/TaskManager to Vedos/Wedos shared hosting.

## Quick Start (3 Steps)

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

This creates `deploy-package/` directory with all files ready to upload.

### Step 2: Upload to Server

**Option A: FTP/SFTP (Recommended)**
1. Open FileZilla or your FTP client
2. Connect to your Vedos/Wedos hosting
3. Navigate to your web root (e.g., `/www/` or `/public_html/`)
4. Upload entire contents of `deploy-package/` directory

**Option B: File Manager**
1. Compress `deploy-package/` to ZIP
2. Login to Vedos/Wedos control panel
3. Use File Manager to upload ZIP
4. Extract ZIP in web root

### Step 3: Configure

1. Open `https://your-domain.com/deploy.php` in browser
2. Click "Run Environment Check"
3. Click "Proceed with Setup"
4. Done! Open `https://your-domain.com/` to use the app

## Detailed Instructions

### Building Locally

The build process:
1. Installs npm dependencies (if needed)
2. Builds production bundle with Vite
3. Copies deployment scripts
4. Creates archive files for easy transfer

**Build Options:**
```bash
# Normal build
./build-and-package.sh

# Clean build (removes node_modules and rebuilds)
./build-and-package.sh --clean
```

**Output:**
- `deploy-package/` - Ready-to-upload directory
- `deploy-package-YYYYMMDD_HHMMSS.tar.gz` - Archive for Linux/Mac
- `deploy-package-YYYYMMDD_HHMMSS.zip` - Archive for Windows
- `deploy-package-latest.tar.gz` - Symlink to latest archive

### Configuring API Connection

The frontend needs to know where your Backend/TaskManager API is.

**Before Building:**
1. Edit `Frontend/TaskManager/.env`:
   ```bash
   VITE_API_BASE_URL=https://your-api-domain.com/api
   VITE_API_KEY=your-api-key-here
   ```
2. Rebuild: `./build-and-package.sh`
3. Re-upload `deploy-package/`

**Note:** Environment variables are baked into the build at compile time. You must rebuild after changing `.env`.

### Deployment Methods

#### Method 1: Manual FTP Upload (Easiest)

1. Build package locally
2. Upload `deploy-package/` contents via FTP
3. Visit `deploy.php` to finish setup

**Pros:** 
- Simple and reliable
- Works with any FTP client
- Full control

**Cons:** 
- Manual process
- Slower for large files

#### Method 2: Automated CLI Deployment (Advanced)

If you have SSH access to your server:

```bash
# On your local machine
./build-and-package.sh

# Transfer to server
scp deploy-package-latest.tar.gz user@server:/path/to/web/

# On server via SSH
cd /path/to/web
php deploy-auto.php --source=deploy-package-latest.tar.gz
```

**Pros:** 
- Fast for updates
- Scriptable/automatable

**Cons:** 
- Requires SSH access
- More complex

#### Method 3: Direct Upload from URL

If your package is hosted somewhere:

```bash
# On server via SSH
php deploy-auto.php --source=https://example.com/package.tar.gz
```

### What Gets Deployed

The `deploy-package/` contains:

```
deploy-package/
├── assets/              # JavaScript, CSS, images
│   ├── index-xxx.js     # Main app bundle (~12KB gzipped)
│   ├── vue-vendor-xxx.js # Vue framework (~38KB gzipped)
│   ├── axios-vendor-xxx.js # HTTP client (~15KB gzipped)
│   └── index-xxx.css    # Styles (~4KB gzipped)
├── index.html           # App entry point
├── deploy.php           # Setup wizard
├── deploy-auto.php      # CLI deployment
├── deploy-deploy.php    # Script downloader
├── .htaccess            # Apache SPA routing
└── README_DEPLOYMENT.txt # Deployment info
```

**Total Size:** ~210KB (71KB gzipped)

### Server Requirements

**Minimum:**
- Web server (Apache, Nginx, etc.)
- PHP 7.4+ (only for deployment scripts, not required for app runtime)
- HTTPS recommended

**For SPA Routing:**
- Apache: mod_rewrite enabled + .htaccess support
- Nginx: Configure try_files directive

**Backend:**
- Backend/TaskManager API must be deployed and accessible
- CORS configured if frontend and backend on different domains

### Apache Configuration (.htaccess)

The `.htaccess` file is automatically included. It enables SPA routing:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```

If Apache doesn't support .htaccess, configure VirtualHost instead.

### Nginx Configuration

If using Nginx, add to your site config:

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### Testing Deployment

**Before uploading:**
```bash
# Build and test locally
./build-and-package.sh
cd deploy-package
python3 -m http.server 8080
# Open http://localhost:8080
```

**After uploading:**
1. Open `https://your-domain.com/`
2. Check browser console for errors
3. Try Settings page to configure API
4. Verify API connection

### Troubleshooting

#### Problem: "API connection failed"

**Solution:**
1. Check Backend/TaskManager is running
2. Verify VITE_API_BASE_URL in `.env`
3. Check CORS settings on backend
4. Check browser console for details

#### Problem: "404 on page refresh"

**Solution:**
1. Ensure .htaccess is uploaded
2. Verify mod_rewrite is enabled
3. Check Apache .htaccess support
4. For Nginx, add try_files directive

#### Problem: "Blank page / white screen"

**Solution:**
1. Check browser console for errors
2. Verify all files uploaded correctly
3. Check file permissions (644 for files, 755 for dirs)
4. Clear browser cache

#### Problem: "Environment variables not working"

**Solution:**
- Environment variables are baked into build
- Edit `.env` then rebuild: `./build-and-package.sh`
- Re-upload entire `deploy-package/`

### Updating Deployment

To deploy an update:

1. Build new package: `./build-and-package.sh`
2. Upload new files (overwrites old ones)
3. Clear browser cache
4. Done!

**Note:** No need to run `deploy.php` again unless .htaccess changed.

### Version Management

Each build creates timestamped archives:
- `deploy-package-20250109_143022.tar.gz`
- `deploy-package-20250109_153415.tar.gz`

Keep old versions for rollback if needed.

### Security Considerations

1. **HTTPS:** Always use HTTPS in production
2. **API Key:** Keep VITE_API_KEY secret (baked into bundle)
3. **Backend Security:** Secure Backend/TaskManager API properly
4. **File Permissions:** Set correct permissions (644/755)
5. **Updates:** Keep dependencies updated regularly

### Performance Tips

1. **Enable compression** on server (gzip/brotli)
2. **Set cache headers** for assets (1 year)
3. **Use CDN** for static assets (optional)
4. **HTTP/2** improves load times
5. **Monitor** with browser DevTools

### Backup Strategy

Before deploying updates:
1. Backup current deployment
2. Test new version locally
3. Deploy to staging first (if available)
4. Deploy to production
5. Keep old version for quick rollback

### Getting Help

- **Documentation:** `Frontend/TaskManager/README.md`
- **API Docs:** `Frontend/TaskManager/docs/API_INTEGRATION.md`
- **Issues:** GitHub Issues
- **Support:** PrismQ Team

## Summary

**Simple Deployment Flow:**
1. `./build-and-package.sh` → Creates deployment package
2. Upload `deploy-package/` → To web server
3. Open `deploy.php` → Configure .htaccess
4. Done! → App is live

**Update Flow:**
1. `./build-and-package.sh` → New build
2. Upload `deploy-package/` → Overwrites old files
3. Done! → Update live

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-09  
**Maintained by:** Worker08 (Deployment Scripts)
