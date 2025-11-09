# Quick Deployment Guide - FTP Workflow

**For building locally and deploying via FTP to Vedos/Wedos**

## Prerequisites

- Node.js 18+ installed locally
- FTP client (FileZilla recommended)
- Vedos/Wedos hosting credentials

## Step-by-Step Deployment

### 1️⃣ Build Locally

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

**Output:** Creates `deploy-package/` folder with all files ready to upload

### 2️⃣ Upload via FTP

**Using FileZilla:**

1. Open FileZilla
2. Connect to your Vedos/Wedos hosting:
   - Host: `ftp.your-domain.com` (or provided by Vedos)
   - Username: Your FTP username
   - Password: Your FTP password
   - Port: 21 (or 22 for SFTP)

3. Navigate to web root on server:
   - Usually `/www/` or `/public_html/`
   - Or specific subdirectory like `/www/taskmanager/`

4. Upload entire contents of `deploy-package/` folder:
   - Drag and drop from left (local) to right (server)
   - Upload ALL files and folders
   - Ensure binary mode for .gz/.zip files

**Files to upload:**
```
deploy-package/
├── assets/          → Upload folder with all JS/CSS
├── index.html       → Upload file
├── deploy.php       → Upload file
├── deploy-auto.php  → Upload file
├── deploy-deploy.php→ Upload file
├── .htaccess        → Upload file (important!)
└── README_DEPLOYMENT.txt → Optional
```

### 3️⃣ Configure on Server

1. Open browser: `https://your-domain.com/deploy.php`
2. Click "Run Environment Check"
3. Click "Proceed with Setup" 
4. Done! ✅

### 4️⃣ Test Application

1. Open: `https://your-domain.com/`
2. Go to Settings page
3. Configure API connection if needed
4. Test task management features

## Updating Deployment

When you need to update:

```bash
# 1. Build new version locally
./build-and-package.sh

# 2. Upload deploy-package/ via FTP (overwrites old files)
#    Use FileZilla to upload

# 3. Clear browser cache
#    Ctrl+Shift+Delete or Ctrl+F5

# 4. Done! Update is live
```

**Note:** No need to run deploy.php again unless .htaccess changed.

## Configuration

### Before First Build

Edit `Frontend/TaskManager/.env`:
```bash
VITE_API_BASE_URL=https://your-api-domain.com/api
VITE_API_KEY=your-api-key-here
```

Then build and upload.

**Important:** Environment variables are baked into the build. After changing .env, you must rebuild and re-upload.

## Troubleshooting

### ❌ "404 on page refresh"
- Ensure `.htaccess` is uploaded
- Check if server supports .htaccess
- Verify mod_rewrite is enabled on server

### ❌ "Blank page / white screen"
- Open browser console (F12) for errors
- Verify all files uploaded correctly
- Check API URL in .env is correct

### ❌ "API connection failed"
- Check Backend/TaskManager is running
- Verify VITE_API_BASE_URL in .env
- Check CORS settings on backend

### ❌ "Permission denied"
- Set file permissions: 644 for files, 755 for folders
- Use FileZilla's chmod feature

## FTP Client Settings (FileZilla)

**Transfer Settings:**
- Transfer Type: Auto
- Default local directory: `Frontend/TaskManager/deploy-package/`
- Default remote directory: `/www/` or `/public_html/`

**Advanced:**
- Use passive mode: Yes (if behind firewall)
- Maximum connections: 2-3
- Enable compression if available

## File Structure on Server

After upload, server should have:

```
/www/  (or /public_html/)
├── assets/
│   ├── index-xxx.js
│   ├── vue-vendor-xxx.js
│   ├── axios-vendor-xxx.js
│   └── index-xxx.css
├── index.html
├── deploy.php
├── deploy-auto.php
├── deploy-deploy.php
└── .htaccess
```

## Quick Commands Reference

```bash
# Build package
./build-and-package.sh           # Linux/Mac
build-and-package.bat           # Windows

# Clean rebuild
./build-and-package.sh --clean  # Linux/Mac
build-and-package.bat clean     # Windows

# Test build locally before upload
cd deploy-package
python3 -m http.server 8080     # Linux/Mac
# Open http://localhost:8080

# Check package contents
ls -lh deploy-package/          # Linux/Mac
dir deploy-package\             # Windows
```

## Checklist

**Before First Deployment:**
- [ ] Configure .env with API URL
- [ ] Build package locally
- [ ] Test build locally (optional)
- [ ] Upload via FTP
- [ ] Run deploy.php setup
- [ ] Test application

**For Updates:**
- [ ] Build new package
- [ ] Upload via FTP (overwrites)
- [ ] Clear browser cache
- [ ] Test update

## Support

- **Build Issues:** Check Node.js version (18+)
- **Upload Issues:** Verify FTP credentials
- **Runtime Issues:** Check browser console (F12)
- **API Issues:** Verify backend is running

---

**Deployment Method:** Local Build + FTP Upload  
**Hosting:** Vedos/Wedos Shared Hosting  
**Build Time:** ~4 seconds  
**Upload Size:** ~210KB (71KB gzipped)  
**Update Time:** ~2 minutes total
