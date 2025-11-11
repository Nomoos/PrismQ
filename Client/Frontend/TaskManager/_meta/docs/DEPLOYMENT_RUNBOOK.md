# Frontend/TaskManager Deployment Runbook

**Version:** 1.0.0  
**Last Updated:** 2025-11-10  
**Owner:** Worker08 - DevOps & Deployment Specialist

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Staging Deployment](#staging-deployment)
3. [Production Deployment](#production-deployment)
4. [Post-Deployment Verification](#post-deployment-verification)
5. [Rollback Procedures](#rollback-procedures)
6. [Troubleshooting](#troubleshooting)
7. [Emergency Contacts](#emergency-contacts)

## Pre-Deployment Checklist

Before deploying to any environment, ensure all items below are complete:

### Code Quality Checks
- [ ] All unit tests passing (`npm run test`)
- [ ] All E2E tests passing (`npm run test:e2e`)
- [ ] Code coverage > 80% (`npm run test:coverage`)
- [ ] No TypeScript errors (`npm run build`)
- [ ] ESLint checks passing (`npm run lint`)
- [ ] Bundle size within limits (`npm run bundle:check`)

### Documentation
- [ ] CHANGELOG.md updated with changes
- [ ] API integration docs updated (if API changes)
- [ ] README.md reflects current state
- [ ] Breaking changes documented

### Approvals
- [ ] Code review approved
- [ ] Worker10 final review completed (for production)
- [ ] Security scan passed (CodeQL/Sentry checks)
- [ ] Performance tests passed

### Configuration
- [ ] Environment variables reviewed
- [ ] API endpoints verified
- [ ] Feature flags configured appropriately
- [ ] Secrets rotated (if needed)

## Staging Deployment

Staging deployment is used to validate changes before production.

### Environment Details
- **URL:** `https://staging.your-domain.com` (or configured staging URL)
- **Purpose:** Pre-production testing and validation
- **Data:** Test data only
- **API:** Connects to staging backend API

### Step 1: Prepare Environment File

```bash
cd Frontend/TaskManager

# Copy staging environment template
cp .env.staging.example .env

# Edit .env with staging-specific values
# VITE_API_BASE_URL=https://api-staging.your-domain.com
# VITE_APP_ENV=staging
# VITE_ENABLE_DEBUG=true

# Verify configuration
cat .env
```

### Step 2: Build for Staging

```bash
# Clean build (recommended for staging)
./build-and-package.sh --clean

# Or normal build
./build-and-package.sh

# Verify build completed
ls -lh deploy-package/
du -sh deploy-package/
```

**Expected Output:**
- `deploy-package/` directory created
- Total size: 200-500 KB
- Contains: index.html, assets/, .htaccess, deploy scripts

### Step 3: Test Build Locally

Before uploading, test the build locally:

```bash
cd deploy-package
python3 -m http.server 8080

# Or use npm preview
cd ..
npm run preview
```

Open `http://localhost:8080` and verify:
- [ ] App loads without errors
- [ ] All routes accessible
- [ ] Settings page loads
- [ ] API configuration present
- [ ] No console errors

### Step 4: Upload to Staging Server

**Option A: FTP/SFTP Upload**
```bash
# Using SCP
cd Frontend/TaskManager
scp -r deploy-package/* user@staging-server:/path/to/staging/

# Or use FTP client (FileZilla, WinSCP)
# Upload entire deploy-package/ contents
```

**Option B: Automated Deployment (if SSH available)**
```bash
# Upload package
scp deploy-package-latest.tar.gz user@staging-server:/tmp/

# SSH into server
ssh user@staging-server

# Deploy
cd /path/to/staging
php deploy-auto.php --source=/tmp/deploy-package-latest.tar.gz
```

### Step 5: Configure Server (First Time Only)

```bash
# SSH into staging server
ssh user@staging-server
cd /path/to/staging

# Verify .htaccess exists
ls -la .htaccess

# Set correct permissions
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;

# Test Apache rewrite module
apache2ctl -M | grep rewrite
# Should show: rewrite_module (shared)
```

### Step 6: Verify Staging Deployment

```bash
# Test health endpoint
curl https://staging.your-domain.com/health.json

# Should return:
# {
#   "status": "ok",
#   "environment": "staging",
#   "version": "0.1.0",
#   ...
# }

# Test main page
curl -I https://staging.your-domain.com/

# Should return: HTTP/1.1 200 OK
```

**Manual Verification:**
1. Open `https://staging.your-domain.com/`
2. Check browser console for errors
3. Navigate through key pages:
   - [ ] Dashboard
   - [ ] Task List
   - [ ] Task Detail (select a task)
   - [ ] Settings
4. Test API connectivity in Settings
5. Verify SPA routing (refresh on a route, should not 404)

### Step 7: Staging Testing

Perform smoke tests:
- [ ] View available tasks
- [ ] Claim a task
- [ ] Update task status
- [ ] Complete a task
- [ ] Test on mobile device
- [ ] Test API error handling

## Production Deployment

⚠️ **CRITICAL:** Production deployment requires extra care and approvals.

### Prerequisites
- [ ] Staging deployment successful
- [ ] All staging tests passed
- [ ] Worker10 approval obtained
- [ ] Change notification sent to team
- [ ] Rollback plan prepared
- [ ] Monitoring alerts configured

### Deployment Window
- **Preferred:** Low-traffic hours (late evening/early morning)
- **Avoid:** Peak business hours
- **Duration:** 10-15 minutes expected
- **Downtime:** Near-zero (static file replacement)

### Step 1: Prepare Production Environment

```bash
cd Frontend/TaskManager

# Copy production environment template
cp .env.production.example .env

# Edit .env with production values
# VITE_API_BASE_URL=https://api.your-domain.com
# VITE_APP_ENV=production
# VITE_ENABLE_DEBUG=false
# VITE_ENABLE_ANALYTICS=true
# VITE_SENTRY_DSN=your-sentry-dsn

# Verify configuration (ensure no debug/test settings)
cat .env
```

### Step 2: Build for Production

```bash
# Clean build for production
./build-and-package.sh --clean

# Verify build
./test-deployment.sh production

# All tests should pass
```

### Step 3: Create Backup

**CRITICAL:** Always backup current production before deploying.

```bash
# SSH into production server
ssh user@production-server

# Create timestamped backup
cd /path/to/production
BACKUP_DIR="backups/frontend_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r * "$BACKUP_DIR/"

# Verify backup
ls -lh "$BACKUP_DIR"
```

### Step 4: Deploy to Production

```bash
# Upload new build
scp deploy-package-latest.tar.gz user@production-server:/tmp/

# SSH into server
ssh user@production-server
cd /path/to/production

# Deploy with automated script
php deploy-auto.php --source=/tmp/deploy-package-latest.tar.gz
```

**Manual Alternative:**
```bash
# Upload via FTP/SFTP
# Replace files in production directory
# Keep backups/ directory intact
```

### Step 5: Immediate Post-Deployment Checks

**Within 5 minutes of deployment:**

```bash
# 1. Health check
curl https://your-domain.com/health.json

# 2. Main page loads
curl -I https://your-domain.com/

# 3. Check critical paths
curl -I https://your-domain.com/dashboard
curl -I https://your-domain.com/settings

# 4. Monitor server logs
tail -f /var/log/apache2/error.log
# Should see no errors related to our app
```

**Browser Checks:**
1. Open production URL in incognito window
2. Hard refresh (Ctrl+Shift+R)
3. Navigate through app
4. Check browser console
5. Test on mobile device

### Step 6: Monitoring

**First 15 minutes:**
- Monitor Sentry for errors (if configured)
- Check server resource usage
- Monitor API backend logs
- Watch for user reports

**First hour:**
- Review error rates
- Check performance metrics
- Verify user activity normal
- Monitor health endpoint

**First 24 hours:**
- Daily error summary
- Performance comparison
- User feedback review

## Post-Deployment Verification

Use this checklist after any deployment:

### Functional Tests
- [ ] Application loads
- [ ] All routes accessible
- [ ] API connection working
- [ ] Authentication working (if applicable)
- [ ] Core features working:
  - [ ] View tasks
  - [ ] Claim tasks
  - [ ] Update tasks
  - [ ] Complete tasks

### Technical Tests
- [ ] No JavaScript errors in console
- [ ] No 404 errors for assets
- [ ] SPA routing working (no 404 on refresh)
- [ ] Health endpoint responding
- [ ] Gzip compression enabled
- [ ] Cache headers set correctly

### Performance Tests
- [ ] Page load time < 3 seconds
- [ ] Time to Interactive < 5 seconds
- [ ] No memory leaks
- [ ] Bundle size within limits

### Security Tests
- [ ] HTTPS enabled
- [ ] Security headers present
- [ ] No sensitive data in console
- [ ] No exposed API keys

## Rollback Procedures

See [ROLLBACK_PROCEDURES.md](./ROLLBACK_PROCEDURES.md) for detailed rollback steps.

### Quick Rollback (< 5 minutes)

If critical issues detected immediately after deployment:

```bash
# SSH into server
ssh user@production-server
cd /path/to/production

# Find latest backup
ls -lt backups/

# Restore backup
LATEST_BACKUP=$(ls -t backups/ | head -1)
# Remove current deployed files
rm -rf assets/ index.html .htaccess deploy*.php health.*
# Restore from backup
cp -r "backups/$LATEST_BACKUP"/* .

# Verify rollback
curl https://your-domain.com/health.json
```

### When to Rollback

Rollback immediately if:
- ❌ Application doesn't load
- ❌ Critical features broken
- ❌ Security vulnerability introduced
- ❌ Severe performance degradation
- ❌ Database corruption risk
- ❌ Widespread user-reported errors

## Troubleshooting

### Issue: Application Shows Blank Page

**Symptoms:** White screen, no content
**Check:**
1. Browser console for errors
2. Network tab for failed requests
3. Server logs for PHP errors

**Solutions:**
```bash
# Check file permissions
ls -la /path/to/production/

# Verify .htaccess exists
cat .htaccess

# Check Apache error log
tail -f /var/log/apache2/error.log

# Clear browser cache
# Hard refresh (Ctrl+Shift+R)
```

### Issue: 404 on Direct URL Access

**Symptoms:** Refreshing a route returns 404
**Cause:** SPA routing not configured

**Solutions:**
```bash
# Verify .htaccess exists
ls -la .htaccess

# Check mod_rewrite enabled
apache2ctl -M | grep rewrite

# Test .htaccess syntax
apache2ctl configtest

# Check .htaccess content
cat .htaccess
# Should contain RewriteRule for SPA routing
```

### Issue: API Connection Failed

**Symptoms:** "Cannot connect to API" error
**Check:**
1. API backend is running
2. CORS configured correctly
3. Firewall allows connections
4. API URL correct in build

**Solutions:**
```bash
# Test API from server
curl https://api.your-domain.com/health

# Check API URL in deployed build (on server, not local)
grep -r "VITE_API_BASE_URL" assets/

# Note: To check locally before deployment:
# grep -r "VITE_API_BASE_URL" deploy-package/assets/

# Verify CORS headers
curl -H "Origin: https://your-domain.com" \
     -I https://api.your-domain.com/health
# Should include Access-Control-Allow-Origin header
```

### Issue: Slow Performance

**Symptoms:** Page loads slowly, high Time to Interactive

**Check:**
1. Bundle size (`npm run bundle:size`)
2. Server compression enabled
3. Cache headers set
4. Network latency

**Solutions:**
```bash
# Enable gzip compression
# Add to .htaccess:
# <IfModule mod_deflate.c>
#   AddOutputFilterByType DEFLATE text/html text/css application/javascript
# </IfModule>

# Verify compression
curl -H "Accept-Encoding: gzip" -I https://your-domain.com/

# Check cache headers
curl -I https://your-domain.com/assets/index.css
```

### Issue: Health Check Failing

**Symptoms:** /health.json returns error

**Solutions:**
```bash
# Verify file exists
ls -la health.json

# Check file permissions
chmod 644 health.json

# Test local file
cat health.json

# Verify JSON syntax
python3 -c "import json; json.load(open('health.json'))"
```

## Emergency Contacts

### Deployment Issues
- **Primary:** Worker08 - DevOps & Deployment
- **Backup:** Worker01 - Project Coordinator

### Application Issues
- **Frontend:** Worker03 - Vue.js/TypeScript Expert
- **Backend:** Backend Team Lead

### Infrastructure Issues
- **Hosting:** Vedos/Wedos Support
- **Server:** System Administrator

### Communication Channels
- **Urgent:** Direct message/call
- **Normal:** GitHub Issues
- **Updates:** Team chat channel

## Deployment Metrics

Track these metrics for each deployment:

- **Build Time:** < 2 minutes
- **Upload Time:** < 5 minutes
- **Total Deployment Time:** < 15 minutes
- **Downtime:** 0 seconds (zero-downtime deployment)
- **Rollback Time:** < 5 minutes (if needed)
- **Error Rate Increase:** < 1% (acceptable variance)

## Continuous Improvement

After each deployment:
1. Update this runbook with lessons learned
2. Document any new issues encountered
3. Improve automation where possible
4. Review and optimize deployment process
5. Share knowledge with team

---

**Document Version:** 1.0.0  
**Created:** 2025-11-10  
**Owner:** Worker08  
**Review Schedule:** Monthly or after major incidents
