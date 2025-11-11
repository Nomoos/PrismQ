# Quick Start: What to Do After Upload

**📦 You just uploaded Frontend/TaskManager to shared hosting. Here's what to do next:**

---

## ✅ Which Directory Did You Upload?

### ⚠️ CRITICAL: Use `deploy-package/`, NOT `dist/`

**If you uploaded `dist/`:**
- ❌ Missing deployment scripts
- ❌ Missing `.htaccess` for routing  
- ❌ Missing health check files
- **Action:** Re-upload `deploy-package/` instead

**If you uploaded `deploy-package/`:**
- ✅ Contains everything needed
- ✅ Includes deployment wizard
- ✅ Ready to configure
- **Action:** Continue below

---

## 🚀 3 Quick Steps to Complete Setup

### Step 1: Run Deployment Wizard (2 minutes)

Open in browser:
```
https://your-domain.com/deploy.php
```

Click through:
1. "Run Environment Check" ✓
2. "Proceed with Setup" ✓
3. Done!

**What it does:** Creates `.htaccess` for SPA routing

---

### Step 2: Open Your App (1 minute)

Navigate to:
```
https://your-domain.com/
```

**Expected:** Mobile-first UI loads successfully

**If blank page:** Check browser console (F12) for errors

---

### Step 3: Test Navigation (1 minute)

1. Click between pages (Dashboard, Settings, Tasks)
2. Refresh the page (should NOT show 404)
3. Check API connection status

**If 404 on refresh:** `.htaccess` not working (contact hosting support)

---

## 🔧 Quick Troubleshooting

### Problem: API Not Connecting?

Your `.env` was configured before building:
```env
VITE_API_BASE_URL=https://api.prismq.nomoos.cz/api
VITE_API_KEY=147852369
```

**Check:**
1. Is backend deployed? Test: `curl https://api.prismq.nomoos.cz/api/health`
2. CORS configured? Backend must allow your frontend domain
3. Wrong URL? Rebuild with correct `.env` and re-upload

**Remember:** Environment variables are baked into build. To change them, you must:
```bash
# On your local machine
cd Frontend/TaskManager
nano .env                    # Edit values
./build-and-package.sh       # Rebuild
# Re-upload deploy-package/
```

---

### Problem: 404 on Page Refresh?

**Cause:** `.htaccess` not working

**Fix:**
1. Verify `.htaccess` exists in web root
2. Contact hosting to enable `mod_rewrite` (Apache)
3. Or configure Nginx (see full guide)

---

### Problem: Blank Page?

**Check:**
1. Open browser console (F12)
2. Look for red errors
3. Check Network tab for failed requests
4. Verify all files uploaded correctly

---

## 📚 Full Documentation

Need more details? See:

- **[Post-Deployment Guide](./_meta/docs/POST_DEPLOYMENT_GUIDE.md)** - Comprehensive next steps
- **[Deployment Guide](./_meta/docs/DEPLOYMENT.md)** - Full deployment documentation
- **[Troubleshooting](./_meta/docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[README](./README.md)** - Project overview

---

## ✅ Deployment Complete Checklist

After upload, verify:

- [ ] Used `deploy-package/` (not `dist/`)
- [ ] Ran `deploy.php` wizard
- [ ] App loads at your domain
- [ ] No 404 when refreshing pages
- [ ] API connection status known
- [ ] Tested on mobile device

---

## 🎯 What You Have Now

**Working:**
- ✅ Frontend application deployed
- ✅ Mobile-optimized UI
- ✅ SPA routing configured
- ✅ Sentry error tracking (if configured)

**Still Need:**
- Backend/TaskManager deployed and accessible
- CORS configured on backend
- API connection verified

---

## 📞 Need Help?

**Quick Help:**
- Check [POST_DEPLOYMENT_GUIDE.md](./_meta/docs/POST_DEPLOYMENT_GUIDE.md)
- Browser console (F12) shows errors
- Test API: `curl https://api.prismq.nomoos.cz/api/health`

**Support:**
- GitHub Issues for bugs
- PrismQ Team for assistance
- Hosting support for server issues

---

**🎉 Success Path:**
1. Upload `deploy-package/` ✓
2. Run `deploy.php` ✓
3. Open `https://your-domain.com/` ✓
4. Test functionality ✓
5. Deploy Backend ⏳
6. Configure CORS ⏳
7. Verify API connection ⏳
8. Done! 🎉

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-11
