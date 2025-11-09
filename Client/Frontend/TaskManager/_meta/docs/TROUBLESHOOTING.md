# Frontend/TaskManager - Troubleshooting Guide

**Version**: 1.0  
**Last Updated**: 2025-11-09  
**Audience**: All Users

---

## Common Issues

### Application Won't Load

**Symptoms**: Blank page, loading spinner indefinitely

**Solutions**:
1. **Check browser console** for JavaScript errors
2. **Clear browser cache**: Ctrl+Shift+Del (Windows) or Cmd+Shift+Del (Mac)
3. **Hard reload**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
4. **Check API connection** in Settings
5. **Try different browser**
6. **Verify server is running**

---

### Tasks Not Loading

**Symptoms**: "Loading tasks..." message persists, or error shown

**Solutions**:
1. **Check API URL** in Settings - must be correct and accessible
2. **Test API directly**: Visit `https://your-api-url/health` in browser
3. **Check CORS settings** on backend - must allow your frontend domain
4. **Verify API key** if authentication is enabled
5. **Check network connection**
6. **Check browser console** for specific error messages

---

### Can't Claim Tasks

**Symptoms**: Claim button doesn't work or shows error

**Solutions**:
1. **Check task status** - only "pending" tasks can be claimed
2. **Verify worker initialized** - go to Worker Dashboard and initialize
3. **Check API response** in browser console Network tab
4. **Verify backend is running** and database is accessible
5. **Check for race conditions** - task might have been claimed by another worker

---

### Progress Not Updating

**Symptoms**: Progress slider doesn't save changes

**Solutions**:
1. **Check task status** - must be "claimed" to update progress
2. **Verify claimed by your worker** - check worker ID matches
3. **Check network connection**
4. **Look for API errors** in console
5. **Refresh page** to see if update actually saved

---

### Routes Not Working (404 Errors)

**Symptoms**: Direct URL navigation shows 404, refresh on route shows error

**Solutions**:
1. **Check .htaccess file** exists and is configured correctly
2. **Verify mod_rewrite enabled** on Apache server
3. **Check RewriteBase** in .htaccess matches your deployment path
4. **Contact hosting support** if mod_rewrite is disabled

**Example .htaccess**:
```apache
RewriteEngine On
RewriteBase /taskmanager/
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^ index.html [L]
```

---

### Styling Broken

**Symptoms**: Unstyled page, missing CSS

**Solutions**:
1. **Check browser console** for 404 errors on CSS files
2. **Verify all files uploaded** after deployment
3. **Clear browser cache**
4. **Check file permissions** - CSS files must be readable (644)
5. **Verify base path** in vite.config.ts matches deployment

---

### Worker ID Resets

**Symptoms**: Worker ID disappears after reload

**Solutions**:
1. **Check browser localStorage** is enabled
2. **Not in incognito mode** - private browsing doesn't persist data
3. **Check browser settings** - cookies/site data must be allowed
4. **Use HTTPS** - some browsers restrict localStorage on HTTP

---

### Slow Performance

**Symptoms**: App loads slowly, laggy interactions

**Solutions**:
1. **Check network speed** - app optimized for 3G but works best on WiFi
2. **Close other tabs** - free up browser memory
3. **Use modern browser** - Chrome 90+, Firefox 88+, Safari 14+
4. **Check bundle size** - should be ~155KB JavaScript
5. **Enable compression** on server (.htaccess mod_deflate)
6. **Clear browser cache** - old cached files might conflict

---

## Error Messages

### "Failed to fetch tasks"

**Cause**: API request failed

**Solutions**:
1. Verify API is running
2. Check API URL in Settings
3. Test API health endpoint
4. Check CORS configuration
5. Verify network connection

---

### "No pending tasks available"

**Cause**: No tasks in "pending" status to claim

**Solutions**:
1. Create new tasks via API
2. Check filter - might be viewing wrong status
3. Wait for existing claimed tasks to timeout
4. Check database for pending tasks

---

### "Unauthorized"

**Cause**: Invalid or missing API key

**Solutions**:
1. Check API key in .env file
2. Rebuild app after changing .env
3. Verify API key with backend admin
4. Check API key not expired

---

### "CORS Error"

**Cause**: Backend not allowing requests from frontend domain

**Solutions**:
1. Configure CORS on backend
2. Add frontend domain to allowed origins
3. Example PHP backend:
   ```php
   header('Access-Control-Allow-Origin: https://your-frontend-domain.com');
   header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
   header('Access-Control-Allow-Headers: Content-Type, Authorization');
   ```

---

## Browser-Specific Issues

### Chrome

**Issue**: Service Worker conflicts
**Solution**: 
1. Open DevTools > Application > Service Workers
2. Unregister any old service workers
3. Hard reload

### Safari

**Issue**: LocalStorage not persisting
**Solution**:
1. Settings > Safari > Prevent Cross-Site Tracking (disable)
2. Settings > Safari > Block All Cookies (disable)

### Firefox

**Issue**: Tracking protection blocking requests
**Solution**:
1. Click shield icon in address bar
2. Disable tracking protection for this site

---

## Mobile Issues

### Touch Targets Too Small

**Solution**: App uses 44x44px minimum touch targets. If buttons seem small:
1. Check browser zoom level
2. Report specific button as issue

### Bottom Navigation Not Visible

**Solution**:
1. Scroll to bottom of page
2. Check browser chrome (address bar) isn't overlapping
3. Report if issue persists

### Horizontal Scrolling

**Solution**:
1. This shouldn't happen - report as bug
2. Temporary fix: zoom out, then zoom back in

---

## Development Issues

### Build Fails

**Solutions**:
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Check Node.js version (must be 18+)
4. Check for TypeScript errors: `npm run type-check`

### TypeScript Errors

**Solutions**:
1. Run `npm run type-check`
2. Fix reported errors
3. Ensure `tsconfig.json` is correct
4. Restart TypeScript server in editor

### Vite Build Warnings

**Solutions**:
1. Check bundle size - might need code splitting
2. Review dynamic imports
3. Check for circular dependencies

---

## Getting Help

If issues persist:

1. **Check documentation**:
   - USER_GUIDE.md
   - DEVELOPER_GUIDE.md
   - DEPLOYMENT_GUIDE.md

2. **Check browser console**:
   - Copy error messages
   - Note network requests that fail

3. **Gather information**:
   - Browser and version
   - Device type
   - Steps to reproduce
   - Error messages
   - Screenshots

4. **Contact support**:
   - Include all gathered information
   - Mention troubleshooting steps already tried

---

## Diagnostic Commands

### Check API Health

```bash
curl https://your-api-url/health
```

Expected response:
```json
{"status":"ok"}
```

### Test CORS

```bash
curl -H "Origin: https://your-frontend-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-api-url/tasks
```

Should return CORS headers in response.

### Check Server Logs

SSH to server and check logs:
```bash
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
```

---

**Document Owner**: Worker06 (Documentation Specialist)  
**Last Updated**: 2025-11-09  
**Version**: 1.0  
**Status**: ✅ Complete
