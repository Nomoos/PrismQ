# Post-Deployment Guide - Frontend/TaskManager

**What to do after uploading Frontend/TaskManager to shared hosting**

---

## ❓ Which Directory to Upload?

**⚠️ IMPORTANT:** Upload `deploy-package/`, NOT `dist/`!

### The Difference:
- **`dist/`** - Raw Vite build output (created by `npm run build`)
  - Contains only: `index.html`, `assets/` folder
  - Missing deployment scripts
  - ❌ **DO NOT upload this directory**

- **`deploy-package/`** - Complete deployment package (created by `build-and-package.sh`)
  - Contains everything from `dist/` folder
  - Plus: `deploy.php`, `deploy-auto.php`, `.htaccess`, health check files
  - ✅ **Upload this directory**

### Why?
The `build-and-package.sh` script does this:
1. Runs `npm run build` → creates `dist/`
2. Copies `dist/*` to `deploy-package/`
3. Adds deployment scripts and Apache configuration
4. Creates ready-to-upload package

---

## ✅ You're Here: Files Uploaded Successfully

Great! You've uploaded the files and configured your `.env`. Now follow these steps:

---

## 🚀 Step-by-Step Post-Deployment

### Step 1: Verify Upload ✓

Open your browser and check these files are accessible:

```
https://your-domain.com/index.html        → Should show the app
https://your-domain.com/deploy.php        → Deployment wizard
https://your-domain.com/assets/           → Should list JS/CSS files
```

If you see "404 Not Found" or "File not found":
- Check FTP/SFTP upload completed successfully
- Verify files are in the correct directory (web root)
- Check file permissions (644 for files, 755 for directories)

---

### Step 2: Run Deployment Wizard

1. **Open deployment wizard in browser:**
   ```
   https://your-domain.com/deploy.php
   ```

2. **Click "Run Environment Check"**
   - Verifies PHP version (7.4+ required)
   - Checks write permissions
   - Checks mod_rewrite (for Apache)

3. **Click "Proceed with Setup"**
   - Creates `.htaccess` from `.htaccess.example`
   - Configures SPA routing for Vue.js
   - Displays success message

4. **Done!** The deployment wizard sets up your environment.

---

### Step 3: Open the Application

1. **Navigate to your domain:**
   ```
   https://your-domain.com/
   ```

2. **What to expect:**
   - Mobile-first UI should load
   - You'll see the task management interface
   - Initially, API connection may show as disconnected

---

### Step 4: Configure API Connection

Your `.env` file was configured before building, so API settings are already embedded in the JavaScript bundle:

```bash
VITE_API_BASE_URL=https://api.prismq.nomoos.cz/api
VITE_API_KEY=147852369
```

**Important:** Environment variables are baked into the build at compile time. You cannot change them without rebuilding.

#### To verify API connection:

1. Open browser console (F12)
2. Look for API connection attempts
3. Check for CORS errors or authentication issues

#### If API is not connecting:

**Option A: Backend is not deployed yet**
- Deploy Backend/TaskManager first
- See: `Backend/TaskManager/README.md`

**Option B: CORS issues**
- Configure CORS on backend to allow your frontend domain
- Update backend `.htaccess` or PHP CORS headers

**Option C: Wrong API URL**
- Edit `Frontend/TaskManager/.env`
- Rebuild: `./build-and-package.sh`
- Re-upload `deploy-package/`

---

### Step 5: Test the Application

#### Basic functionality tests:

1. **Navigate between pages:**
   - Dashboard → Should load without 404
   - Settings → Should show API configuration
   - Tasks → Should load (may be empty if backend not connected)

2. **Refresh the page:**
   - Should NOT show 404 error
   - If you see 404, check Step 2 (`.htaccess` configuration)

3. **Check browser console:**
   - Open DevTools (F12) → Console tab
   - Look for errors (red messages)
   - Network tab → Check API requests

4. **Test on mobile device:**
   - App is mobile-first
   - Should work well on smartphones
   - Test touch interactions

---

### Step 6: Verify Error Tracking (Optional)

If you configured Sentry in `.env`:

```bash
VITE_SENTRY_DSN=https://b9da0c3962c8a8c4dae5af2233d02134@o4510346023731200.ingest.de.sentry.io/4510346034282576
VITE_SENTRY_ENVIRONMENT=production
VITE_SENTRY_ENABLED=true
```

1. **Check Sentry dashboard:**
   - Login to [sentry.io](https://sentry.io)
   - Navigate to your project
   - Should see "Frontend/TaskManager" initialization event

2. **Test error reporting:**
   - Open browser console
   - Trigger a test error (optional)
   - Verify it appears in Sentry dashboard

---

## 🔧 Common Issues & Solutions

### Issue 1: "404 Not Found" when refreshing pages

**Symptoms:**
- App works on initial load
- Clicking links works
- Refreshing page shows 404

**Cause:** `.htaccess` not configured or mod_rewrite not enabled

**Solution:**
```bash
# On server via SSH or FTP client
1. Verify .htaccess exists in web root
2. Check .htaccess contains RewriteEngine rules
3. Contact hosting support to enable mod_rewrite
4. For Nginx, configure try_files (see below)
```

**Nginx users:** Add to site config:
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

---

### Issue 2: "Blank page" or "White screen"

**Symptoms:**
- Page loads but shows nothing
- No visible errors

**Cause:** JavaScript errors or missing files

**Solution:**
```bash
1. Open browser console (F12)
2. Check for red error messages
3. Check Network tab for failed requests (red status)
4. Verify all files uploaded correctly:
   - index.html
   - assets/ folder with .js and .css files
5. Clear browser cache (Ctrl+Shift+R)
```

---

### Issue 3: "API Connection Failed"

**Symptoms:**
- App loads but shows "API disconnected"
- Tasks don't load
- Network errors in console

**Cause:** Backend not accessible or CORS issues

**Solution:**
```bash
1. Check backend is deployed and running:
   curl https://api.prismq.nomoos.cz/api/health

2. Test CORS from frontend domain:
   curl -H "Origin: https://your-domain.com" \
        -I https://api.prismq.nomoos.cz/api/health
   
   Should include header:
   Access-Control-Allow-Origin: https://your-domain.com

3. If CORS missing, configure backend:
   - Edit Backend/TaskManager/.htaccess
   - Add CORS headers for your frontend domain
   - Or update backend CORS configuration

4. If API URL wrong:
   - Edit Frontend/TaskManager/.env
   - Rebuild: ./build-and-package.sh
   - Re-upload deploy-package/
```

---

### Issue 4: "Environment variables not working"

**Symptoms:**
- Changed `.env` but app still uses old values
- API URL pointing to wrong server

**Cause:** Environment variables are baked into JavaScript at build time

**Solution:**
```bash
# Environment variables are NOT runtime configurable
# They are embedded in JavaScript during build

1. Edit Frontend/TaskManager/.env with new values
2. Rebuild the package:
   cd Frontend/TaskManager
   ./build-and-package.sh
3. Re-upload entire deploy-package/ folder
4. Clear browser cache
5. Refresh application
```

---

### Issue 5: "File permissions error"

**Symptoms:**
- 403 Forbidden errors
- Cannot access files

**Cause:** Wrong file permissions on server

**Solution:**
```bash
# Via SSH
cd /path/to/web/root
find . -type f -exec chmod 644 {} \;  # Files
find . -type d -exec chmod 755 {} \;  # Directories

# Via FTP client (FileZilla, etc.)
# Select all files → Right-click → File permissions
# Files: 644
# Directories: 755
```

---

## 🏥 Health Checks

Verify deployment is healthy:

### Quick Health Check:
```bash
curl https://your-domain.com/health.json
```

Expected response:
```json
{
  "status": "ok",
  "service": "frontend-taskmanager",
  "timestamp": "2025-11-11T12:00:00Z"
}
```

### Full Health Check:
```bash
# Test main page
curl -I https://your-domain.com/

# Test assets load
curl -I https://your-domain.com/assets/

# Test API connection from frontend
# (Check browser DevTools → Network tab)
```

---

## 📊 Verify Performance

After deployment, check performance:

### 1. Lighthouse (Chrome DevTools)
```bash
1. Open Chrome DevTools (F12)
2. Navigate to "Lighthouse" tab
3. Click "Analyze page load"
4. Should score 90+ in all categories
```

### 2. Page Load Speed
```bash
# Open browser DevTools → Network tab
# Reload page (Ctrl+R)
# Check load time in bottom status bar
# Target: < 3 seconds on 3G connection
```

### 3. Bundle Size
```bash
# Check in DevTools → Network tab
# Look at transferred sizes:
# - Main JS: ~14KB (gzipped)
# - Vue vendor: ~38KB (gzipped)
# - CSS: ~5KB (gzipped)
# Total: < 100KB (gzipped)
```

---

## 🔄 Updating the Deployment

When you need to make changes:

### 1. Update Code
```bash
cd Frontend/TaskManager
# Edit source files in src/
```

### 2. Update Configuration (if needed)
```bash
# Edit .env with new values
nano .env
```

### 3. Rebuild Package
```bash
./build-and-package.sh
```

### 4. Upload New Package
```bash
# Via FTP/SFTP:
# Upload entire deploy-package/ folder
# Overwrite existing files

# Via SCP:
scp -r deploy-package/* user@server:/var/www/html/

# Via deploy-auto.php (if SSH available):
scp deploy-package-latest.tar.gz user@server:/tmp/
ssh user@server
php deploy-auto.php --source=/tmp/deploy-package-latest.tar.gz
```

### 5. Clear Browser Cache
```bash
# Users must clear cache to see updates
# Press: Ctrl+Shift+R (hard reload)
```

**Note:** No need to run `deploy.php` again unless `.htaccess` changed.

---

## 🎯 What's Next?

### 1. Deploy Backend (if not done yet)
```bash
# See Backend/TaskManager deployment guide
cd Backend/TaskManager
# Follow Backend/TaskManager/README.md
```

### 2. Set Up Monitoring
```bash
# Configure Sentry alerts
# Set up uptime monitoring (UptimeRobot, etc.)
# Monitor API health checks
```

### 3. Configure HTTPS
```bash
# Use Let's Encrypt (free SSL)
# Or use hosting provider's SSL
# Ensure both frontend and backend use HTTPS
```

### 4. Optimize Performance
```bash
# Enable gzip compression on server
# Set cache headers for assets
# Configure CDN (optional)
```

### 5. User Testing
```bash
# Test on real mobile devices
# Verify all features work
# Check different browsers
# Test API integration end-to-end
```

---

## 📞 Getting Help

### Documentation:
- **Frontend Guide:** `Frontend/TaskManager/README.md`
- **Backend Guide:** `Backend/TaskManager/README.md`
- **API Reference:** `Backend/TaskManager/_meta/docs/api/API_REFERENCE.md`
- **Deployment Runbook:** `Frontend/TaskManager/_meta/docs/DEPLOYMENT_RUNBOOK.md`

### Troubleshooting:
- **Check logs:** Browser console (F12), server error logs
- **Test API:** Use curl or Postman to test backend endpoints
- **Verify CORS:** Check API response headers
- **File issues:** Check file permissions and paths

### Support:
- **GitHub Issues:** Report bugs or ask questions
- **PrismQ Team:** Contact for assistance
- **Hosting Support:** Contact Vedos/Wedos for server issues

---

## ✅ Deployment Checklist

After deployment, verify:

- [ ] Files uploaded to correct directory
- [ ] `deploy.php` wizard completed
- [ ] `.htaccess` configured (SPA routing works)
- [ ] Application loads at `https://your-domain.com/`
- [ ] No 404 errors when refreshing pages
- [ ] Browser console shows no critical errors
- [ ] API connection working (or understood why not)
- [ ] Sentry error tracking active (if configured)
- [ ] Mobile testing completed
- [ ] Performance acceptable (< 3s load time)
- [ ] HTTPS enabled
- [ ] Health check endpoints responding

---

## 🎉 Success!

Your Frontend/TaskManager is now deployed and running!

**Next Steps:**
1. Test thoroughly on different devices
2. Monitor Sentry for any errors
3. Configure API connection if needed
4. Share with users

**Bookmark this URL:**
```
https://your-domain.com/
```

---

**Version:** 1.0.0  
**Created:** 2025-11-11  
**Last Updated:** 2025-11-11  
**Maintained by:** DevOps & Documentation Team
