# Staging Deployment Checklist

**Version:** 1.0.0  
**Last Updated:** 2025-11-10  
**Owner:** Worker08 - DevOps & Deployment Specialist

## Purpose

This checklist ensures consistent, error-free staging deployments. Follow each step in order and verify completion before proceeding.

---

## Pre-Deployment Phase

### Code Readiness
- [ ] All code changes committed to feature branch
- [ ] Branch merged/rebased with latest main/develop
- [ ] No merge conflicts
- [ ] Code review completed and approved
- [ ] All CI/CD checks passing

### Testing
- [ ] All unit tests passing (`npm run test`)
- [ ] Test coverage ≥ 80% (`npm run test:coverage`)
- [ ] E2E tests passing (`npm run test:e2e`)
- [ ] Linting checks passed (`npm run lint`)
- [ ] No TypeScript errors (`npm run build`)
- [ ] Bundle size within limits (`npm run bundle:check`)

### Documentation
- [ ] CHANGELOG.md updated with changes
- [ ] Breaking changes documented (if any)
- [ ] API changes documented (if applicable)
- [ ] README.md updated (if needed)

### Configuration Review
- [ ] `.env.staging` reviewed and updated
- [ ] API URLs correct for staging environment
- [ ] Debug flags enabled appropriately
- [ ] Feature flags configured for staging
- [ ] No production secrets in staging config

---

## Build Phase

### Environment Setup
- [ ] Navigate to project directory
  ```bash
  cd Frontend/TaskManager
  ```

- [ ] Ensure dependencies are up to date
  ```bash
  npm install
  ```

- [ ] Copy staging environment file
  ```bash
  cp .env.staging .env
  ```

- [ ] Verify environment variables
  ```bash
  cat .env | grep -E "VITE_APP_ENV|VITE_API_BASE_URL"
  ```
  - Should show: `VITE_APP_ENV=staging`
  - Should show correct staging API URL

### Build Execution
- [ ] Run production build
  ```bash
  npm run build
  ```
  - This creates the `dist/` directory with Vite build output

- [ ] Verify build completed successfully
  - No TypeScript errors
  - No build warnings (critical)
  - Build time < 5 minutes

- [ ] Check build output
  ```bash
  ls -lh dist/
  du -sh dist/
  ```
  - `dist/` directory exists
  - Total size < 500KB
  - Contains `index.html`, `assets/`, etc.

### Build Verification
- [ ] Test built files locally (using dist/)
  ```bash
  npm run preview
  ```

- [ ] Open `http://localhost:4173` in browser
  - [ ] App loads without errors
  - [ ] No console errors
  - [ ] Can navigate to all routes
  - [ ] Settings page accessible

- [ ] Verify environment in browser console
  ```javascript
  // Should show staging API URL
  ```

### Package Creation
- [ ] Create deployment package
  ```bash
  ./build-and-package.sh
  ```
  - This copies `dist/*` to `deploy-package/`
  - Adds deployment scripts and configurations
  - Creates compressed archives

- [ ] Verify deployment package created
  ```bash
  ls -lh deploy-package/
  ```
  - Contains all files from `dist/`
  - Contains `deploy.php`, `deploy-auto.php`
  - Contains `.htaccess` configuration
  - Contains `README_DEPLOYMENT.txt`
  - `deploy-package-*.tar.gz` created
  - `deploy-package-latest.tar.gz` symlink exists

- [ ] Run deployment tests (on deploy-package/)
  ```bash
  cd _meta/scripts
  ./test-deployment.sh staging
  ```
  - All tests should pass
  - No critical errors

---

## Deployment Phase

### Pre-Deployment Backup
- [ ] SSH into staging server
  ```bash
  ssh user@staging-server
  ```

- [ ] Navigate to deployment directory
  ```bash
  cd /path/to/staging
  ```

- [ ] Create backup of current deployment
  ```bash
  BACKUP_DIR="backups/frontend_$(date +%Y%m%d_%H%M%S)"
  mkdir -p "$BACKUP_DIR"
  # Note: Server has deployed files (from previous deploy-package/)
  cp -r assets/ index.html .htaccess health.json deploy*.php "$BACKUP_DIR/" 2>/dev/null || true
  ls -lh "$BACKUP_DIR"
  ```

- [ ] Verify backup created successfully
  - Backup directory exists
  - Contains files from current deployment

### File Upload

**Option A: Automated Upload (if SSH available)**
- [ ] Upload package to server
  ```bash
  # From local machine
  scp deploy-package-latest.tar.gz user@staging-server:/tmp/
  ```

- [ ] Deploy package
  ```bash
  # On server
  cd /path/to/staging
  php deploy-auto.php --source=/tmp/deploy-package-latest.tar.gz
  ```

**Option B: Manual FTP Upload**
- [ ] Open FTP client (FileZilla, WinSCP, etc.)
- [ ] Connect to staging server
- [ ] Navigate to staging directory
- [ ] Upload entire contents of `deploy-package/`
- [ ] Verify all files uploaded successfully
  - index.html
  - assets/ directory
  - .htaccess
  - health.json
  - deploy scripts

### Post-Upload Configuration
- [ ] Verify file permissions
  ```bash
  # On server
  find . -type f -exec chmod 644 {} \;
  find . -type d -exec chmod 755 {} \;
  ```

- [ ] Verify .htaccess exists and is correct
  ```bash
  cat .htaccess | grep "RewriteEngine On"
  ```

- [ ] Verify health.json exists
  ```bash
  cat health.json | head -5
  ```

---

## Verification Phase

### Server-Side Checks
- [ ] Test health endpoint locally on server
  ```bash
  curl http://localhost/health.json
  ```
  - Should return valid JSON
  - Status should be "ok"
  - Environment should be "staging"

- [ ] Test main page
  ```bash
  curl -I http://localhost/
  ```
  - Should return HTTP 200 OK

- [ ] Check Apache error logs
  ```bash
  tail -50 /var/log/apache2/error.log
  ```
  - No new errors related to our app

### Public URL Checks
- [ ] Test health endpoint publicly
  ```bash
  # From local machine or any external location
  curl https://staging.your-domain.com/health.json
  ```
  - Returns valid JSON
  - Status: "ok"
  - Environment: "staging"
  - Version correct

- [ ] Test main page publicly
  ```bash
  curl -I https://staging.your-domain.com/
  ```
  - Returns HTTP 200 OK
  - Content-Type: text/html

- [ ] Test health page
  - Open `https://staging.your-domain.com/health.html`
  - All checks should show ✓ OK
  - Status should be "All Systems Operational"

### Browser Testing
- [ ] Open staging URL in browser (incognito)
  ```
  https://staging.your-domain.com/
  ```

- [ ] Verify app loads
  - No blank page
  - No loading spinner stuck
  - UI displays correctly

- [ ] Check browser console
  - No JavaScript errors
  - No 404 errors for assets
  - API URL correct (check network tab)

- [ ] Test navigation
  - [ ] Dashboard loads
  - [ ] Task List loads
  - [ ] Can open task details
  - [ ] Settings page loads

- [ ] Test SPA routing
  - [ ] Navigate to `/dashboard`
  - [ ] Refresh page (Ctrl+R or F5)
  - [ ] Should not get 404
  - [ ] Page should reload correctly

- [ ] Test on mobile device
  - [ ] Open on phone/tablet
  - [ ] App is responsive
  - [ ] Touch interactions work
  - [ ] No layout issues

### Functional Testing
- [ ] Test API connectivity
  - Open Settings page
  - Configure API connection
  - Test connection
  - Should connect to staging API

- [ ] Test core workflows
  - [ ] View task list
  - [ ] Filter tasks
  - [ ] Select a task
  - [ ] View task details
  - [ ] Test any new features

- [ ] Test error handling
  - Try invalid API URL
  - Verify error message displays
  - Verify app doesn't crash

### Performance Checks
- [ ] Measure page load time
  - Open DevTools Network tab
  - Hard refresh (Ctrl+Shift+R)
  - Load time should be < 3 seconds

- [ ] Check bundle sizes on server
  ```bash
  # On server (deployed files are in assets/)
  ls -lh assets/*.js
  ```
  - Main bundle < 15KB (gzipped)
  - Vue vendor < 40KB (gzipped)
  - Total JS < 100KB (gzipped)

- [ ] Verify compression
  ```bash
  curl -H "Accept-Encoding: gzip" -I https://staging.your-domain.com/assets/index.css
  ```
  - Should include `Content-Encoding: gzip`

---

## Post-Deployment Phase

### Monitoring Setup
- [ ] Verify health check endpoint is accessible
  ```bash
  curl https://staging.your-domain.com/health.json
  ```

- [ ] Add to uptime monitoring (if not already)
  - UptimeRobot / Pingdom / StatusCake
  - Monitor: `/health.json`
  - Interval: 5 minutes
  - Alert on failure

- [ ] Configure Sentry (if using)
  - Verify DSN is set for staging
  - Check Sentry dashboard for events
  - Verify source maps uploaded (if applicable)

### Documentation
- [ ] Update deployment log
  ```
  Date: YYYY-MM-DD HH:MM
  Environment: Staging
  Version: X.X.X
  Deployed By: [Your Name]
  Changes: [Brief description]
  Status: Success
  ```

- [ ] Update team on deployment
  - Post in team chat
  - Email stakeholders (if needed)
  - Update project board/tracker

- [ ] Document any issues encountered
  - Note any problems
  - Solutions applied
  - Lessons learned

### Cleanup
- [ ] Clean up local files
  ```bash
  # Keep deploy-package for reference, but can remove if needed
  # rm -rf deploy-package/
  ```

- [ ] Remove .env file (don't commit)
  ```bash
  rm .env
  git status  # Verify .env not staged
  ```

- [ ] Clean up server temp files
  ```bash
  # On server
  rm /tmp/deploy-package-*.tar.gz
  ```

---

## Rollback Checklist (If Needed)

If critical issues are found:

- [ ] Identify issue severity
  - Critical? → Immediate rollback
  - Major? → Rollback within 15 min
  - Minor? → Fix forward

- [ ] Execute rollback (if needed)
  ```bash
  # On server
  cd /path/to/staging
  LATEST_BACKUP=$(ls -t backups/ | head -1)
  # Remove current deployed files
  rm -rf assets/ index.html .htaccess deploy*.php health.*
  # Restore from backup
  cp -r "backups/$LATEST_BACKUP"/* .
  ```

- [ ] Verify rollback
  ```bash
  curl https://staging.your-domain.com/health.json
  ```

- [ ] Notify team of rollback
  - Post in team chat
  - Document reason
  - Create issue for bug

See [ROLLBACK_PROCEDURES.md](./ROLLBACK_PROCEDURES.md) for detailed rollback guide.

---

## Extended Monitoring (First 24 Hours)

### First Hour
- [ ] Check every 15 minutes
  - Health endpoint responding
  - No error spikes
  - Performance normal

### First Day
- [ ] Check twice
  - Morning check
  - Evening check
  - Review any user reports

### After 24 Hours
- [ ] Review metrics
  - Error rates
  - Performance
  - User activity

- [ ] Collect feedback
  - Team testing results
  - User reports
  - Monitoring data

- [ ] Decision point
  - [ ] Proceed to production (if all good)
  - [ ] Fix issues and re-deploy
  - [ ] Rollback and investigate

---

## Sign-Off

Deployment to staging completed and verified by:

- **Deployed By:** ___________________________
- **Date/Time:** ___________________________
- **Version:** ___________________________
- **Status:** [ ] Success  [ ] Success with issues  [ ] Failed
- **Notes:** _____________________________________________
  _______________________________________________________

---

## Quick Reference

**Staging URL:** `https://staging.your-domain.com`  
**Health Check:** `https://staging.your-domain.com/health.json`  
**Health Page:** `https://staging.your-domain.com/health.html`  
**SSH:** `ssh user@staging-server`  
**Deployment Path:** `/path/to/staging`  

**Emergency Rollback:**
```bash
ssh user@staging-server
cd /path/to/staging
BACKUP=$(ls -t backups/ | head -1)
rm -rf dist/ assets/ index.html
cp -r "backups/$BACKUP"/* .
```

---

**Document Version:** 1.0.0  
**Created:** 2025-11-10  
**Owner:** Worker08  
**Review:** After each deployment
