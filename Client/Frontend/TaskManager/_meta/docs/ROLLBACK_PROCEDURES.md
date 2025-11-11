# Rollback Procedures - Frontend/TaskManager

**Version:** 1.0.0  
**Last Updated:** 2025-11-10  
**Owner:** Worker08 - DevOps & Deployment Specialist

## Overview

This document outlines procedures for rolling back a deployment of Frontend/TaskManager when issues are encountered in staging or production.

## Table of Contents

1. [When to Rollback](#when-to-rollback)
2. [Rollback Decision Matrix](#rollback-decision-matrix)
3. [Quick Rollback Guide](#quick-rollback-guide)
4. [Detailed Rollback Procedures](#detailed-rollback-procedures)
5. [Post-Rollback Actions](#post-rollback-actions)
6. [Prevention Strategies](#prevention-strategies)

## When to Rollback

### Critical Issues (Immediate Rollback Required)

Rollback **immediately** if any of these occur:

- ❌ **Application won't load** - Blank page or critical error
- ❌ **Data loss risk** - User data being corrupted or lost
- ❌ **Security breach** - Vulnerability exposed or exploited
- ❌ **Complete feature failure** - Core functionality broken
- ❌ **Performance collapse** - Application unusable due to performance
- ❌ **Backend incompatibility** - Can't communicate with API
- ❌ **Widespread user impact** - > 50% of users affected

### Major Issues (Rollback Recommended)

Consider rollback within 30 minutes if:

- ⚠️ **Significant bug** - Important feature broken
- ⚠️ **Performance degradation** - 50%+ slower than before
- ⚠️ **High error rate** - Errors spiking in monitoring
- ⚠️ **User complaints** - Multiple users reporting problems
- ⚠️ **Mobile incompatibility** - Not working on mobile devices
- ⚠️ **API timeout issues** - Backend communication failing

### Minor Issues (Fix Forward Preferred)

These typically don't require rollback:

- ✓ **UI glitches** - Visual issues that don't block functionality
- ✓ **Single feature bug** - One non-critical feature affected
- ✓ **Minor performance** - Slight performance decrease
- ✓ **Edge case bugs** - Rare scenarios affected
- ✓ **Cosmetic issues** - Styling problems

**For minor issues:** Deploy a fix forward rather than rolling back.

## Rollback Decision Matrix

```
┌─────────────────────────────────────────────────────────────┐
│ Severity  │ User Impact  │ Time to Fix  │ Action           │
├───────────┼──────────────┼──────────────┼──────────────────┤
│ Critical  │ >50%        │ Any          │ ROLLBACK NOW     │
│ Critical  │ <50%        │ >1 hour      │ ROLLBACK NOW     │
│ Major     │ >25%        │ >30 min      │ ROLLBACK         │
│ Major     │ <25%        │ <30 min      │ FIX FORWARD      │
│ Minor     │ Any         │ Any          │ FIX FORWARD      │
└─────────────────────────────────────────────────────────────┘
```

**Decision Time:** Make rollback decision within **5 minutes** of issue detection.

## Quick Rollback Guide

### Prerequisites
- Backup exists (created during deployment)
- Server access available
- Rollback authority granted

### 5-Minute Rollback Procedure

```bash
# 1. SSH into server
ssh user@production-server

# 2. Navigate to deployment directory
cd /path/to/production

# 3. Find latest backup
ls -lt backups/ | head -5

# 4. Identify backup to restore
# Format: frontend_YYYYMMDD_HHMMSS
BACKUP="backups/frontend_20251110_143022"  # Replace with actual

# 5. Create safety backup of current (problematic) version
SAFETY_BACKUP="backups/rollback_safety_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SAFETY_BACKUP"
# Note: Deployed files (from deploy-package/) are in root, not dist/
cp -r assets/ index.html .htaccess deploy*.php health.* "$SAFETY_BACKUP/" 2>/dev/null

# 6. Remove current deployment
rm -rf assets/ index.html .htaccess deploy*.php health.*

# 7. Restore from backup
cp -r "$BACKUP"/* .

# 8. Verify restoration
ls -la index.html
cat health.json | grep version

# 9. Test health endpoint
curl http://localhost/health.json
# or
curl https://your-domain.com/health.json

# 10. Verify in browser
# Open production URL and test critical paths
```

**Expected Time:** 3-5 minutes

## Detailed Rollback Procedures

### Pre-Rollback Checklist

Before initiating rollback:

- [ ] **Confirm issue severity** - Meets rollback criteria
- [ ] **Check backup exists** - Verify backup from deployment
- [ ] **Notify team** - Alert team of rollback action
- [ ] **Document issue** - Note what went wrong
- [ ] **Get approval** - If time permits, get authorization

### Step-by-Step Rollback

#### Step 1: Prepare for Rollback

```bash
# SSH into affected server
ssh user@production-server

# Navigate to deployment directory
cd /path/to/production

# List available backups
ls -lth backups/

# Output should show:
# frontend_20251110_143022/  (most recent deployment)
# frontend_20251110_120000/  (previous deployment)
# frontend_20251109_180000/  (older deployment)
```

#### Step 2: Identify Correct Backup

```bash
# Check backup dates and times
ls -lth backups/

# Verify backup contents
ls -la backups/frontend_20251110_120000/

# Should contain:
# - index.html
# - assets/
# - .htaccess
# - deploy scripts
# - health.json

# Check version in backup
cat backups/frontend_20251110_120000/health.json
```

#### Step 3: Create Safety Backup

```bash
# Backup current (problematic) version for investigation
SAFETY_DIR="backups/rollback_safety_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SAFETY_DIR"

# Copy current deployed files (from previous deploy-package/)
cp -r assets/ "$SAFETY_DIR/assets/" 2>/dev/null || true
cp index.html .htaccess health.json deploy*.php "$SAFETY_DIR/" 2>/dev/null || true

# Verify safety backup
ls -la "$SAFETY_DIR"
```

#### Step 4: Stop Traffic (Optional)

For major issues, consider temporary maintenance mode:

```bash
# Create maintenance page (optional)
cat > maintenance.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Maintenance</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>🔧 Maintenance in Progress</h1>
    <p>We're making improvements. Back shortly!</p>
</body>
</html>
EOF

# Redirect to maintenance (Apache .htaccess)
# Only if needed for major issues
```

#### Step 5: Perform Rollback

```bash
# Remove problematic deployment
rm -rf assets/ index.html .htaccess deploy*.php health.*

# Note: Keep backups/ directory

# Restore from backup
BACKUP_DIR="backups/frontend_20251110_120000"
cp -r "$BACKUP_DIR"/* .

# Restore specific files if selective rollback needed
# cp "$BACKUP_DIR/index.html" .
# cp -r "$BACKUP_DIR/assets" .
# cp -r "$BACKUP_DIR/dist" .
```

#### Step 6: Verify File Integrity

```bash
# Check files restored correctly
ls -la

# Verify index.html
head -20 index.html
# Should show valid HTML with DOCTYPE

# Check assets directory
ls -la assets/
# Should contain .js and .css files

# Verify .htaccess
cat .htaccess
# Should contain SPA routing rules

# Check file permissions
find . -type f -name "*.html" -exec ls -l {} \;
find . -type f -name "*.js" -exec ls -l {} \;
```

#### Step 7: Test Locally on Server

```bash
# Test health endpoint
curl http://localhost/health.json

# Should return valid JSON:
# {"status":"ok","version":"0.1.0",...}

# Test main page
curl -I http://localhost/

# Should return: HTTP/1.1 200 OK

# Check for errors in Apache log
tail -50 /var/log/apache2/error.log
# Should not show errors related to our app
```

#### Step 8: Verify Publicly

```bash
# From your local machine or another server:

# Test health endpoint
curl https://your-domain.com/health.json

# Test main page loads
curl -I https://your-domain.com/

# Test SPA routing
curl -I https://your-domain.com/dashboard
```

**Manual Browser Verification:**
1. Open production URL in incognito window
2. Hard refresh (Ctrl+Shift+R) to clear cache
3. Navigate through critical paths:
   - [ ] Dashboard loads
   - [ ] Task list shows
   - [ ] Can view task details
   - [ ] Settings page accessible
4. Check browser console for errors
5. Test on mobile device
6. Verify SPA routing (refresh on route)

#### Step 9: Monitor Post-Rollback

```bash
# Monitor server logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# Watch for:
# - Normal request patterns
# - No 404s or 500s
# - No JavaScript errors
# - No unusual traffic
```

**Monitoring Checklist:**
- [ ] No increase in error rate
- [ ] Response times normal
- [ ] No user complaints
- [ ] Health check passing
- [ ] All routes accessible

### Rollback Verification Matrix

| Check | Expected | How to Verify |
|-------|----------|---------------|
| App loads | 200 OK | `curl -I https://your-domain.com/` |
| Health check | Valid JSON | `curl https://your-domain.com/health.json` |
| SPA routing | No 404 | Refresh on /dashboard route |
| Assets load | No 404s | Check browser Network tab |
| API works | Connects | Test in Settings page |
| No errors | Clean console | Check browser Console |
| Mobile works | Responsive | Test on phone |
| Performance | Fast load | Check Core Web Vitals |

## Post-Rollback Actions

### Immediate Actions (Within 15 minutes)

1. **Notify Team**
   ```
   Subject: ROLLBACK COMPLETED - Frontend/TaskManager
   
   Rollback completed successfully.
   
   - Environment: Production
   - Previous version: v0.2.0 (problematic)
   - Rolled back to: v0.1.0
   - Reason: [brief description]
   - Impact: [user impact]
   - Status: Application stable
   
   Investigation ongoing. Update to follow.
   ```

2. **Update Status**
   - Update status page (if applicable)
   - Post in team chat
   - Notify affected users (if needed)

3. **Begin Investigation**
   - Collect logs from problematic deployment
   - Capture error reports
   - Document what went wrong
   - Preserve safety backup for analysis

### Short-Term Actions (Within 24 hours)

1. **Root Cause Analysis**
   - Investigate what caused the issue
   - Review deployment logs
   - Check build artifacts
   - Analyze error reports
   - Identify what was missed in testing

2. **Create Bug Report**
   ```markdown
   # Deployment Failure Report - YYYY-MM-DD
   
   ## Issue
   [Description of what went wrong]
   
   ## Impact
   - Users affected: [number/percentage]
   - Duration: [time problem existed]
   - Severity: [Critical/Major/Minor]
   
   ## Timeline
   - HH:MM - Deployed version X.X.X
   - HH:MM - Issue detected
   - HH:MM - Rollback initiated
   - HH:MM - Rollback completed
   - HH:MM - Service restored
   
   ## Root Cause
   [What caused the issue]
   
   ## Fix
   [What needs to be done to fix]
   
   ## Prevention
   [How to prevent this in the future]
   ```

3. **Plan Fix**
   - Create fix branch
   - Write tests for the issue
   - Implement fix
   - Test thoroughly
   - Schedule new deployment

### Long-Term Actions (Within 1 week)

1. **Process Improvement**
   - Update deployment checklist
   - Add new tests if gap found
   - Improve monitoring
   - Enhance documentation
   - Review deployment process

2. **Update Documentation**
   - Update this rollback guide
   - Document lessons learned
   - Share with team
   - Update deployment runbook

3. **Team Review**
   - Post-mortem meeting
   - Discuss what went wrong
   - Identify improvements
   - Update procedures
   - Share knowledge

## Rollback Scenarios

### Scenario 1: Blank Page After Deployment

**Symptoms:**
- White screen
- No content loads
- Console shows "Cannot read property of undefined"

**Cause:** Likely build error or missing assets

**Rollback Priority:** 🔴 CRITICAL - Immediate

**Procedure:**
```bash
# Quick rollback using latest backup
ssh user@server
cd /path/to/production
BACKUP=$(ls -t backups/ | head -1)
rm -rf dist assets index.html
cp -r "backups/$BACKUP"/* .
curl http://localhost/health.json
```

### Scenario 2: API Connection Failures

**Symptoms:**
- "Cannot connect to API" errors
- API calls failing
- 500 errors from backend

**Cause:** Wrong API URL in build or CORS issue

**Rollback Priority:** 🟠 MAJOR - Within 15 minutes

**Procedure:**
```bash
# Verify it's a frontend issue first
curl https://api.your-domain.com/health
# If API is working, it's a frontend build issue

# Rollback
ssh user@server
cd /path/to/production
# Follow standard rollback procedure
```

### Scenario 3: Performance Degradation

**Symptoms:**
- Slow page loads (>10 seconds)
- High memory usage
- Browser freezing

**Cause:** Bundle size issue, memory leak, or inefficient code

**Rollback Priority:** 🟠 MAJOR - Within 30 minutes

**Procedure:**
```bash
# Confirm degradation is from new deployment
# Check bundle size
ls -lh assets/*.js

# If significantly larger (>2x), rollback
# Follow standard rollback procedure
```

### Scenario 4: Mobile Incompatibility

**Symptoms:**
- Works on desktop, broken on mobile
- Touch events not working
- Mobile layout broken

**Cause:** CSS or JavaScript mobile-specific bug

**Rollback Priority:** 🟡 MODERATE - Within 1 hour

**Consider:** If desktop works, may fix forward with mobile-only fix

**Procedure:**
- Assess user impact (% mobile users)
- If >25% mobile users, rollback
- If <25%, consider fixing forward

## Prevention Strategies

### Before Deployment

1. **Comprehensive Testing**
   - Run full test suite
   - Test on multiple browsers
   - Test on mobile devices
   - Test with backend API
   - Perform load testing

2. **Staging Validation**
   - Always deploy to staging first
   - Test all critical paths
   - Leave staging running 24 hours
   - Get QA approval

3. **Build Verification**
   - Check bundle sizes
   - Verify source maps
   - Test built files locally
   - Run automated tests on build

4. **Deployment Checklist**
   - Use pre-deployment checklist
   - Verify backups exist
   - Confirm rollback plan
   - Have team available

### During Deployment

1. **Gradual Rollout** (if possible)
   - Deploy to subset of servers
   - Monitor initial batch
   - Gradually increase
   - Full rollout only if stable

2. **Active Monitoring**
   - Watch deployment in real-time
   - Monitor error rates
   - Check health endpoints
   - Watch user reports

3. **Quick Verification**
   - Test immediately after deploy
   - Verify critical paths
   - Check on multiple devices
   - Monitor for 15 minutes minimum

### After Deployment

1. **Extended Monitoring**
   - Monitor for first hour
   - Check daily for first week
   - Review error trends
   - Track performance metrics

2. **User Feedback**
   - Monitor support channels
   - Check user reports
   - Review analytics
   - Act on issues quickly

3. **Documentation**
   - Document any issues
   - Update runbooks
   - Share lessons learned
   - Improve processes

## Rollback Metrics

Track these metrics for each rollback:

- **Time to Decision:** < 5 minutes (how long to decide to rollback)
- **Time to Rollback:** < 5 minutes (actual rollback time)
- **Total Downtime:** < 10 minutes (total impact time)
- **Recovery Verification:** < 5 minutes (confirming recovery)

**Total incident time:** < 25 minutes from detection to full recovery

## Emergency Contacts

### Rollback Authority
- **Primary:** Worker08 - DevOps & Deployment
- **Backup:** Worker01 - Project Coordinator
- **Escalation:** Technical Lead

### Support Team
- **Frontend Issues:** Worker03 - Vue.js Expert
- **Backend Issues:** Backend Team Lead
- **Infrastructure:** System Administrator

### Communication
- **Urgent:** Direct call/message
- **Updates:** Team chat + email
- **Status:** Status page (if available)

---

**Document Version:** 1.0.0  
**Created:** 2025-11-10  
**Owner:** Worker08  
**Review Schedule:** After each rollback or quarterly
