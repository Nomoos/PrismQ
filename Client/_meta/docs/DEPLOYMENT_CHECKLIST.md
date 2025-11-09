# Production Deployment Checklist

## Overview

This checklist ensures safe and successful deployment to production. Complete all items before deploying.

**Project**: PrismQ Client  
**Coordinator**: Worker01 (Project Manager)  
**Status**: Phase 4 - Release Management

---

## Pre-Deployment Checklist

### Code Quality ✓

- [ ] All tests pass locally
  ```bash
  cd Frontend && npm test
  cd Backend/TaskManager && php tests/test.php
  ```
- [ ] Code linting passes
  ```bash
  cd Frontend && npm run lint
  ```
- [ ] Build succeeds without warnings
  ```bash
  cd Frontend && npm run build
  ```
- [ ] No critical or high-severity bugs in backlog
- [ ] Code review completed (if applicable)
- [ ] Security vulnerabilities addressed

### Documentation ✓

- [ ] README.md up to date
- [ ] API documentation current
- [ ] Setup guide verified
- [ ] User guide reflects latest features
- [ ] Known issues documented
- [ ] Migration guide prepared (if breaking changes)

### Version Management ✓

- [ ] VERSION file updated
- [ ] Frontend package.json version updated
- [ ] Backend composer.json version updated
- [ ] All versions are consistent
  ```bash
  ./_meta/_scripts/sync-versions.sh
  ```
- [ ] CHANGELOG.md updated with release notes
- [ ] Git tag created for release

### Testing ✓

- [ ] Unit tests: All passing
- [ ] Integration tests: All passing  
- [ ] Manual smoke tests completed
- [ ] Browser compatibility verified (Chrome, Firefox, Safari)
- [ ] Mobile responsiveness checked
- [ ] API endpoints tested manually
- [ ] Error handling verified

### Dependencies ✓

- [ ] All npm dependencies audited
  ```bash
  cd Frontend && npm audit
  ```
- [ ] No critical security vulnerabilities
- [ ] Composer dependencies validated
  ```bash
  cd Backend/TaskManager && composer validate
  ```
- [ ] Dependency versions locked (package-lock.json, composer.lock)

### Configuration ✓

- [ ] Environment variables documented
- [ ] Production config reviewed
- [ ] API endpoints configured correctly
- [ ] Database connection settings verified
- [ ] CORS settings appropriate for production
- [ ] Security headers configured

### Backup & Rollback ✓

- [ ] Current production state backed up
- [ ] Rollback procedure documented
- [ ] Previous version tag identified
- [ ] Rollback tested in staging (if available)
- [ ] Data migration rollback plan (if applicable)

---

## Deployment Process

### Step 1: Final Verification

```bash
# Run comprehensive readiness check
./_meta/_scripts/check-release-readiness.sh
```

Expected: All checks pass ✓

### Step 2: Create Release

```bash
# Prepare release (updates versions, creates tag)
./_meta/_scripts/prepare-release.sh 1.0.0

# Push to repository
git push origin main
git push origin v1.0.0
```

### Step 3: Build Production Assets

```bash
# Build frontend
cd Frontend
npm ci                    # Clean install dependencies
npm run build            # Build production assets
cd ..

# Verify build output
ls -la Frontend/dist/
```

### Step 4: Deploy Backend

```bash
# Backend deployment (TaskManager)
cd Backend/TaskManager

# IMPORTANT: Update deploy script first (recommended)
# This ensures you have the latest version with all fixes
php deploy-deploy.php     # Downloads latest deploy.php from GitHub

# Then run the deployment
php deploy.php            # Follow the interactive prompts

# OR for manual setup:
# Install dependencies
composer install --no-dev --optimize-autoloader

# Verify deployment
php -l api/*.php         # Syntax check
```

**Note**: The `deploy-deploy.php` script ensures `deploy.php` is always up-to-date by downloading it from the GitHub repository. This is recommended before each deployment to get the latest bug fixes and improvements.

### Step 5: Deploy Frontend

```bash
# Copy dist folder to web server
# Example (adjust for your hosting):
rsync -avz Frontend/dist/ user@server:/var/www/html/

# Or using FTP/SFTP
# Upload Frontend/dist/* to web root
```

### Step 6: Post-Deployment Verification

```bash
# Test endpoints
curl https://your-domain.com/api/health
curl https://your-domain.com/

# Check error logs
tail -f /var/log/nginx/error.log
tail -f Backend/TaskManager/logs/app.log
```

---

## Post-Deployment Checklist

### Immediate Verification (0-2 hours) ✓

- [ ] Website loads successfully
- [ ] API health check returns OK
- [ ] Login/authentication works
- [ ] Main features operational
- [ ] No JavaScript errors in browser console
- [ ] No PHP errors in logs
- [ ] Database connections working
- [ ] Task queue functioning

### Monitoring (2-24 hours) ✓

- [ ] Monitor error logs for new issues
- [ ] Check response times/performance
- [ ] Verify task completion rates
- [ ] Monitor user reports/feedback
- [ ] Check database query performance
- [ ] Monitor memory usage
- [ ] Check disk space

### Documentation ✓

- [ ] Deployment documented in changelog
- [ ] GitHub release created
- [ ] Release notes published
- [ ] Team notified of deployment
- [ ] Users notified (if applicable)

---

## Rollback Procedure

If critical issues are discovered:

### Immediate Rollback (< 1 hour)

```bash
# 1. Identify previous stable version
git tag -l "v*" --sort=-v:refname | head -n 2

# 2. Checkout previous version
git checkout v0.9.0  # Replace with actual previous version

# 3. Rebuild and redeploy
cd Frontend && npm run build
# Deploy dist/ folder

# 4. Document rollback
echo "Rolled back to v0.9.0 due to [issue]" >> ROLLBACK_LOG.md
```

### Planned Rollback (> 1 hour)

1. Assess issue severity and impact
2. Determine if hotfix is feasible
3. If not, execute rollback procedure above
4. Plan and test fix
5. Schedule new deployment

---

## Production Environment Requirements

### Server Requirements

**Frontend:**
- Node.js 18+ (for build only)
- Static file hosting (nginx, Apache)
- HTTPS enabled

**Backend:**
- PHP 8.0+
- MySQL 5.7+ or MariaDB 10.2+
- Apache with mod_rewrite
- PDO extensions enabled

### Performance Targets

- Page load time: < 3 seconds
- API response time: < 200ms average
- Task processing: < 1 second per task
- Uptime: 99.9%

### Security Requirements

- HTTPS enabled (SSL/TLS certificate)
- Security headers configured
- SQL injection protection verified
- XSS protection enabled
- CSRF tokens implemented (if applicable)
- Rate limiting configured

---

## Monitoring & Alerts

### Key Metrics to Monitor

1. **Application Health**
   - Error rate
   - Response time
   - Request throughput

2. **Database**
   - Connection pool usage
   - Query performance
   - Disk usage

3. **Task Queue**
   - Queue depth
   - Task completion rate
   - Failed task count

4. **Infrastructure**
   - CPU usage
   - Memory usage
   - Disk I/O

### Alert Thresholds

- Error rate > 5%: Warning
- Response time > 1s: Warning
- Response time > 5s: Critical
- Queue depth > 1000: Warning
- Failed tasks > 10%: Critical

---

## Success Criteria

A deployment is considered successful when:

- ✓ Zero critical bugs in first 48 hours
- ✓ Performance metrics meet or exceed targets
- ✓ No rollback required
- ✓ Error rate < 1%
- ✓ User feedback neutral or positive

---

## Emergency Contacts

**Project Manager (Worker01)**: [Contact info]  
**Technical Lead**: [Contact info]  
**DevOps**: [Contact info]  
**On-Call**: [Contact info]

---

## Deployment History

| Version | Date | Deployed By | Status | Notes |
|---------|------|-------------|--------|-------|
| 0.1.0 | 2024-11-XX | Worker01 | ✓ Success | Initial deployment |
| 1.0.0 | TBD | Worker01 | Pending | First production release |

---

**Last Updated**: 2024-11-09  
**Maintained By**: Worker01 (Project Manager)  
**Next Review**: After each deployment
