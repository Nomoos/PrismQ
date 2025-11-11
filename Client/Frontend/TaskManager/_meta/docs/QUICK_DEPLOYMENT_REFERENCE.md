# Quick Deployment Reference

**Quick reference for deploying Frontend/TaskManager to staging and production**

---

## 🚀 Quick Deploy to Staging

```bash
# 1. Setup
cd Frontend/TaskManager
cp .env.staging .env

# 2. Build & Package
./build-and-package.sh

# 3. Verify
./test-deployment.sh staging

# 4. Deploy
scp deploy-package-latest.tar.gz user@staging-server:/tmp/
ssh user@staging-server
cd /path/to/staging
php deploy-auto.php --source=/tmp/deploy-package-latest.tar.gz

# 5. Verify
curl https://staging.your-domain.com/health.json
```

**Time:** ~10 minutes

---

## 🎯 Quick Deploy to Production

```bash
# 1. Setup
cd Frontend/TaskManager
cp .env.production .env

# 2. Build & Package
./build-and-package.sh

# 3. Verify
./test-deployment.sh production

# 4. Backup (on server)
ssh user@production-server
cd /path/to/production
BACKUP="backups/frontend_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP"
# Backup deployed files (from previous deploy-package/)
cp -r assets/ index.html .htaccess deploy*.php health.* "$BACKUP/" 2>/dev/null || true

# 5. Deploy
# From local:
scp deploy-package-latest.tar.gz user@production-server:/tmp/
# On server:
php deploy-auto.php --source=/tmp/deploy-package-latest.tar.gz

# 6. Verify
curl https://your-domain.com/health.json
```

**Time:** ~15 minutes

---

## 🔄 Quick Rollback

```bash
# On server
ssh user@server
cd /path/to/deployment
BACKUP=$(ls -t backups/ | head -1)
# Remove current deployed files
rm -rf assets/ index.html .htaccess deploy*.php health.*
# Restore from backup
cp -r "backups/$BACKUP"/* .
curl http://localhost/health.json
```

**Time:** ~3 minutes

---

## ✅ Pre-Deployment Checklist

- [ ] Tests passing (`npm run test`)
- [ ] Build works (`npm run build`)
- [ ] Code reviewed
- [ ] Environment file configured
- [ ] Backup plan ready

---

## 🏥 Health Check URLs

**Staging:**
- Health JSON: `https://staging.your-domain.com/health.json`
- Health Page: `https://staging.your-domain.com/health.html`

**Production:**
- Health JSON: `https://your-domain.com/health.json`
- Health Page: `https://your-domain.com/health.html`

---

## 📊 Key Metrics

**Bundle Sizes:**
- Main JS: ~14KB (gzipped)
- Vue vendor: ~38KB (gzipped)
- Axios vendor: ~15KB (gzipped)
- Total CSS: ~5KB (gzipped)

**Performance:**
- Page load: < 3s
- Time to Interactive: < 5s
- Bundle total: < 100KB (gzipped)

---

## 🐛 Quick Troubleshooting

**Blank page?**
```bash
# Check console errors, verify API URL
cat .env | grep VITE_API_BASE_URL
```

**404 on refresh?**
```bash
# Verify .htaccess
cat .htaccess | grep RewriteEngine
```

**API not connecting?**
```bash
# Test API
curl https://api.your-domain.com/health
# Check CORS
curl -H "Origin: https://your-domain.com" -I https://api.your-domain.com/health
```

**Slow performance?**
```bash
# Check compression
curl -H "Accept-Encoding: gzip" -I https://your-domain.com/
# Should show Content-Encoding: gzip
```

---

## 📚 Full Documentation

- **Deployment Runbook:** `docs/DEPLOYMENT_RUNBOOK.md`
- **Rollback Guide:** `docs/ROLLBACK_PROCEDURES.md`
- **Monitoring Setup:** `docs/MONITORING_SETUP.md`
- **Staging Checklist:** `docs/STAGING_DEPLOYMENT_CHECKLIST.md`

---

## 🆘 Emergency Contacts

**Deployment Issues:** Worker08  
**Frontend Issues:** Worker03  
**Backend Issues:** Backend Team  
**Server Issues:** System Admin  

---

## 📝 Quick Commands

```bash
# Build
npm run build

# Test locally
npm run preview

# Package
./build-and-package.sh

# Verify package
./test-deployment.sh staging

# Upload
scp -r deploy-package/* user@server:/var/www/html/

# SSH
ssh user@server

# Check logs
tail -f /var/log/apache2/error.log

# Health check
curl https://your-domain.com/health.json
```

---

**Last Updated:** 2025-11-10  
**Version:** 1.0.0
