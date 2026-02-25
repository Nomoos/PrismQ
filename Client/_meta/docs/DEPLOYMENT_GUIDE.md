# PrismQ Client - Deployment Guide

**Version**: 1.0.0  
**Last Updated**: 2025-11-11  
**Status**: Production Ready

---

## Overview

This is the central deployment guide for PrismQ Client, covering both the **Backend/TaskManager** (PHP REST API) and **Frontend/TaskManager** (Vue 3 web interface). This guide provides a high-level overview and links to detailed deployment documentation for each component.

### Production Deployments

**Live Production URLs:**
- **Backend API**: https://api.prismq.nomoos.cz
- **Frontend UI**: https://prismq.nomoos.cz

### Project Structure

```
PrismQ.Client/
├── Backend/TaskManager/     # PHP REST API for task queue management
└── Frontend/TaskManager/    # Vue 3 web interface
```

### Deployment Strategy

PrismQ Client uses a **modular deployment approach**:
- **Backend** and **Frontend** can be deployed independently
- Optimized for **shared hosting** (e.g., cPanel, Plesk)
- Support for both **manual** and **automated** deployment
- **Zero-downtime** updates possible
- Built-in deployment scripts for easy setup

---

## Quick Start

### 1. Backend Deployment (5 minutes)

Deploy the PHP REST API to handle task queue operations:

```bash
# Upload deploy.php from Backend/TaskManager/src/ to your server
# Visit: https://your-domain.com/deploy.php
# Follow the interactive setup wizard
```

**Production Example**: https://api.prismq.nomoos.cz

**See**: [Backend Deployment Guide](../Backend/TaskManager/_meta/docs/deployment/DEPLOYMENT_GUIDE.md)

### 2. Frontend Deployment (5 minutes)

Build and deploy the Vue 3 web interface:

```bash
# On your local machine
cd Frontend/TaskManager
./build-and-package.sh

# Upload deploy-package/ to your web server
# Visit: https://your-domain.com/deploy.php
# Complete the setup
```

**Production Example**: https://prismq.nomoos.cz

**See**: [Frontend Deployment Guide](../Frontend/TaskManager/_meta/docs/DEPLOYMENT.md)

---

## Deployment Options

### Option 1: Shared Hosting (Recommended for Most Users)

**Best for**: Small to medium deployments, cost-effective hosting

- **Backend**: PHP 8.0+ with MySQL
- **Frontend**: Static file hosting with Apache/Nginx
- **Cost**: $5-20/month
- **Complexity**: Low - uses web-based deployment wizards

**Guides**:
- [Backend on Shared Hosting](../Backend/TaskManager/_meta/docs/deployment/DEPLOYMENT_GUIDE.md)
- [Frontend on Shared Hosting](../Frontend/TaskManager/_meta/docs/DEPLOYMENT.md)

### Option 2: VPS / Cloud Hosting

**Best for**: Larger deployments, custom configurations

- **Backend**: Docker container or direct PHP deployment
- **Frontend**: Static hosting or Docker
- **Cost**: $10-100/month
- **Complexity**: Medium - requires server administration

**Research**: [Deployment Platform Research](./docs/archive/DEPLOYMENT_RESEARCH.md)

### Option 3: Platform-as-a-Service (PaaS)

**Best for**: Auto-scaling, managed infrastructure

Supported platforms:
- **Render.com** - Full-stack, Docker support
- **Railway.app** - Modern DX, automatic Dockerfile detection
- **Vercel** (Frontend) + Render/Railway (Backend)
- **Heroku** - Established platform

**Research**: [Deployment Platform Research](./docs/archive/DEPLOYMENT_RESEARCH.md)

---

## Prerequisites

### Backend Requirements

**Server**:
- PHP 8.0 or higher
- MySQL 5.7+ or MariaDB 10.2+
- Apache with mod_rewrite (or Nginx)

**PHP Extensions**:
- PDO
- PDO_MySQL
- JSON
- cURL
- mbstring

**Access**:
- FTP/SFTP or SSH access
- MySQL database and user

### Frontend Requirements

**Build Environment** (local):
- Node.js 18+ and npm
- Git (for cloning repository)

**Deployment Server**:
- Web server (Apache, Nginx)
- Static file hosting
- HTTPS recommended

**Backend Dependency**:
- Backend/TaskManager API must be deployed and accessible

---

## Deployment Process

### Phase 1: Pre-Deployment

**Checklist**: [Deployment Checklist](./docs/operations/DEPLOYMENT_CHECKLIST.md)

- [ ] Review system requirements
- [ ] Backup existing data (if updating)
- [ ] Test in staging environment (if available)
- [ ] Update configuration files
- [ ] Verify dependencies and versions
- [ ] Run security checks

### Phase 2: Backend Deployment

**Step 1: Environment Check**
```bash
# Upload check_setup.php from Backend/TaskManager/src/ and run
php check_setup.php
```

**Step 2: Deploy Backend**
```bash
# Option A: Web-based (recommended)
# Upload deploy.php from Backend/TaskManager/src/
# Visit: https://your-domain.com/deploy.php

# Option B: Command-line
php deploy.php
```

**Step 3: Verify Backend**
```bash
curl https://your-domain.com/api/health
# Expected: {"success":true,"message":"TaskManager API is healthy"}
```

**Production Example**:
```bash
curl https://api.prismq.nomoos.cz/api/health
```

**Detailed Guide**: [Backend Deployment Guide](../Backend/TaskManager/_meta/docs/deployment/DEPLOYMENT_GUIDE.md)

### Phase 3: Frontend Deployment

**Step 1: Configure Environment**
```bash
# Edit Frontend/TaskManager/.env
VITE_API_BASE_URL=https://your-domain.com/api
VITE_API_KEY=your-api-key-here
```

**Production Example**:
```bash
# Production configuration
VITE_API_BASE_URL=https://api.prismq.nomoos.cz/api
VITE_API_KEY=your-production-api-key
```

**Step 2: Build Package**
```bash
cd Frontend/TaskManager
./build-and-package.sh
```

**Step 3: Upload Files**
- Upload `deploy-package/` contents to web server
- Visit `https://your-domain.com/deploy.php`
- Complete setup wizard

**Step 4: Verify Frontend**
- Open `https://your-domain.com/`
- Check browser console for errors
- Test API connection via Settings page

**Detailed Guide**: [Frontend Deployment Guide](../Frontend/TaskManager/_meta/docs/DEPLOYMENT.md)

### Phase 4: Post-Deployment

**Immediate Verification**:
- [ ] Website loads successfully
- [ ] API health check returns OK
- [ ] Login/authentication works (if applicable)
- [ ] Main features operational
- [ ] No console errors
- [ ] Database connections working

**Monitoring** (first 24 hours):
- [ ] Monitor error logs
- [ ] Check response times
- [ ] Verify task completion rates
- [ ] Monitor user feedback

**Documentation**: [Deployment Checklist](./docs/operations/DEPLOYMENT_CHECKLIST.md)

---

## Deployment Scripts

### Backend Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `check_setup.php` | Environment validation | Web browser or CLI |
| `deploy.php` | Main deployment script | Web browser or CLI |
| `deploy-deploy.php` | Update deployment script | Ensures latest version |

**Location**: `Backend/TaskManager/src/`

### Frontend Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `build-and-package.sh` | Build production bundle | Local machine (Linux/Mac) |
| `build-and-package.bat` | Build production bundle | Local machine (Windows) |
| `deploy.php` | Setup wizard | Web browser |
| `deploy-auto.php` | Automated CLI deployment | SSH/Command line |

**Location**: `Frontend/TaskManager/`

---

## Configuration

### Backend Configuration

**Database Settings**:
```php
// config/config.php (auto-generated by deploy.php)
'database' => [
    'host' => 'localhost',
    'name' => 'taskmanager',
    'user' => 'db_user',
    'password' => 'secure_password'
]
```

**API Settings**:
- API endpoints defined in database (`api_endpoints` table)
- CORS configuration in `api/index.php`
- Task types registered via API

### Frontend Configuration

**Environment Variables** (build-time):
```bash
# Frontend/TaskManager/.env
VITE_API_BASE_URL=https://your-domain.com/api
VITE_API_KEY=your-api-key-here

# Optional: Sentry error tracking
VITE_SENTRY_DSN=https://your-dsn@sentry.io/project-id
VITE_SENTRY_ENVIRONMENT=production
VITE_SENTRY_ENABLED=true
```

**Note**: Environment variables are baked into the build. Rebuild after changes.

**Configuration Guide**: [Configuration Documentation](./docs/development/CONFIGURATION.md)

---

## Verification & Testing

### Backend Verification

**Health Check**:
```bash
curl https://your-domain.com/api/health
```

**API Documentation**:
```
https://your-domain.com/api/docs/
```

**Test Endpoints**:
```bash
# List task types
curl https://your-domain.com/api/task-types

# Register new task type
curl -X POST https://your-domain.com/api/task-types/register \
  -H "Content-Type: application/json" \
  -d '{"name":"TestTask","version":"1.0.0","param_schema":{}}'
```

### Frontend Verification

**Access Application**:
```
https://your-domain.com/
```

**Check Browser Console**:
- No JavaScript errors
- Successful API connections
- Proper resource loading

**Test Features**:
- Navigation works
- API communication functional
- Task management operational

### End-to-End Testing

**Create and Process Task**:
1. Register task type via API
2. Create task via frontend
3. Verify task in database
4. Process task with worker
5. Check task completion

---

## Troubleshooting

### Common Backend Issues

**Error: "Database connection failed"**
- Verify database credentials in `config/config.php`
- Check database exists and user has permissions
- Ensure MySQL service is running

**Error: "500 Internal Server Error"**
- Check Apache error logs
- Verify file permissions (644 for files, 755 for directories)
- Ensure mod_rewrite is enabled

**Error: "API endpoint not found"**
- Check .htaccess is uploaded
- Verify mod_rewrite is enabled
- Check URL routing configuration

### Common Frontend Issues

**Error: "API connection failed"**
- Verify Backend is running
- Check VITE_API_BASE_URL in build
- Verify CORS settings on backend

**Error: "404 on page refresh"**
- Ensure .htaccess is uploaded
- Verify mod_rewrite is enabled
- For Nginx, add try_files directive

**Error: "Blank page / white screen"**
- Check browser console for errors
- Verify all files uploaded correctly
- Clear browser cache

**Detailed Troubleshooting**: 
- [Backend Deployment Guide](../Backend/TaskManager/_meta/docs/deployment/DEPLOYMENT_GUIDE.md#troubleshooting)
- [Frontend Deployment Guide](../Frontend/TaskManager/_meta/docs/DEPLOYMENT.md#troubleshooting)

---

## Updates & Maintenance

### Updating Backend

```bash
# Upload latest deploy-deploy.php from Backend/TaskManager/src/
# Download latest deploy.php
php deploy-deploy.php

# Run deployment
php deploy.php
# Choose "Skip database setup" if DB is already configured
```

**Note**: All deployment scripts are located in `Backend/TaskManager/src/` in the repository.

### Updating Frontend

```bash
# Build new package
cd Frontend/TaskManager
./build-and-package.sh

# Upload deploy-package/ contents
# Overwrites old files, no need to run deploy.php again
```

### Rollback Procedure

**If issues occur**:

1. **Identify previous stable version**:
   ```bash
   git tag -l "v*" --sort=-v:refname | head -n 2
   ```

2. **Checkout previous version**:
   ```bash
   git checkout v0.9.0
   ```

3. **Rebuild and redeploy**:
   ```bash
   cd Frontend/TaskManager
   npm run build
   # Upload dist/ folder
   ```

4. **Document rollback**:
   ```bash
   echo "Rolled back to v0.9.0 due to [issue]" >> ROLLBACK_LOG.md
   ```

**Detailed Rollback**: [Deployment Checklist - Rollback](./docs/operations/DEPLOYMENT_CHECKLIST.md#rollback-procedure)

---

## Security Considerations

### Backend Security

- [ ] **HTTPS enabled** - Use SSL/TLS certificates
- [ ] **Strong passwords** - Database and admin passwords
- [ ] **File permissions** - 640 for config.php, 644 for API files
- [ ] **API authentication** - Implement API key validation
- [ ] **Rate limiting** - Prevent abuse
- [ ] **Input validation** - Validate all API inputs
- [ ] **SQL injection protection** - Use PDO prepared statements

### Frontend Security

- [ ] **HTTPS only** - Enforce SSL
- [ ] **Secure API keys** - Keep VITE_API_KEY secret
- [ ] **Content Security Policy** - Set CSP headers
- [ ] **XSS protection** - Vue 3 provides built-in protection
- [ ] **Regular updates** - Keep dependencies updated

**Security Documentation**: [Security Fixes](./docs/operations/SECURITY_FIXES.md)

---

## Performance Optimization

### Backend Optimization

- Enable **OPcache** for PHP
- Use **database indexes** on frequently queried columns
- Implement **caching** (Redis, Memcached)
- Enable **gzip compression**
- Optimize **database queries**

### Frontend Optimization

- **Server compression** - Enable gzip/brotli
- **Cache headers** - Set long cache times for assets
- **CDN** - Use Content Delivery Network (optional)
- **HTTP/2** - Enable on web server
- **Lazy loading** - Images and components

### Performance Targets

- **Page load time**: < 3 seconds
- **API response time**: < 200ms average
- **Task processing**: < 1 second per task
- **Uptime**: 99.9%

---

## Monitoring & Alerts

### Application Monitoring

**Key Metrics**:
- Error rate (target: < 1%)
- Response time (target: < 200ms)
- Request throughput
- Task completion rate
- Queue depth

**Tools**:
- **Backend logs**: Check Apache/PHP error logs
- **Frontend errors**: Sentry integration (optional)
- **Database**: Monitor query performance
- **Server**: CPU, memory, disk usage

### Error Tracking Setup

**Frontend - Sentry** (Optional but Recommended):
```bash
# Frontend/TaskManager/.env
VITE_SENTRY_DSN=https://your-dsn@sentry.io/project-id
VITE_SENTRY_ENVIRONMENT=production
VITE_SENTRY_ENABLED=true
```

Benefits:
- Real-time error notifications
- Stack traces for debugging
- Performance monitoring
- User impact tracking

**Setup Guide**: [Frontend Deployment - Error Tracking](../Frontend/TaskManager/_meta/docs/DEPLOYMENT.md#configuring-error-tracking-optional---recommended)

---

## Related Documentation

### Deployment Resources

- **[Deployment Checklist](./docs/operations/DEPLOYMENT_CHECKLIST.md)** - Pre/post-deployment verification
- **[Deployment Template](./templates/DEPLOYMENT_GUIDE_TEMPLATE.md)** - Standard deployment guide format
- **[Platform Research](./docs/archive/DEPLOYMENT_RESEARCH.md)** - Hosting platform comparison

### Module-Specific Guides

#### Backend/TaskManager
- **[Deployment Guide](../Backend/TaskManager/_meta/docs/deployment/DEPLOYMENT_GUIDE.md)** - Complete backend deployment
- **[API Reference](../Backend/TaskManager/_meta/docs/api/API_REFERENCE.md)** - API documentation
- **[README](../Backend/TaskManager/README.md)** - Backend overview

#### Frontend/TaskManager
- **[Deployment Guide](../Frontend/TaskManager/_meta/docs/DEPLOYMENT.md)** - Complete frontend deployment
- **[Quick Reference](../Frontend/TaskManager/_meta/docs/QUICK_DEPLOYMENT_REFERENCE.md)** - Fast deployment commands
- **[Deployment Runbook](../Frontend/TaskManager/_meta/docs/DEPLOYMENT_RUNBOOK.md)** - Detailed procedures
- **[Staging Checklist](../Frontend/TaskManager/_meta/docs/STAGING_DEPLOYMENT_CHECKLIST.md)** - Staging deployment
- **[README](../Frontend/TaskManager/README.md)** - Frontend overview

### Operations & Release Management

- **[Release Management](./docs/operations/RELEASE.md)** - Version control and releases
- **[Release Quick Reference](./docs/operations/RELEASE_QUICK_REFERENCE.md)** - Quick release commands
- **[Changelog](./docs/operations/CHANGELOG.md)** - Version history
- **[Security Fixes](./docs/operations/SECURITY_FIXES.md)** - Security updates

### Architecture & Development

- **[Architecture Overview](./docs/architecture/ARCHITECTURE.md)** - System architecture
- **[Development Guide](./docs/development/DEVELOPMENT.md)** - Contributing guide
- **[Testing Guide](./docs/development/TESTING.md)** - Test coverage
- **[Configuration](./docs/development/CONFIGURATION.md)** - Environment variables

### Getting Started

- **[Setup Guide](./docs/getting-started/SETUP.md)** - Installation and configuration
- **[User Guide](./docs/getting-started/USER_GUIDE.md)** - How to use the application
- **[Troubleshooting](./docs/getting-started/TROUBLESHOOTING.md)** - Common issues

---

## Worker Implementation

After deploying Backend and Frontend, you'll need workers to process tasks:

### Worker Resources

- **[Worker Implementation Guidelines](./docs/development/WORKER_IMPLEMENTATION_GUIDELINES.md)** - Best practices
- **[Worker Implementation Plan](./docs/development/WORKER_IMPLEMENTATION_PLAN.md)** - Strategic plan
- **[Worker Examples](./examples/workers/README.md)** - Production-ready examples
- **[Worker Integration Guide](./examples/workers/INTEGRATION_GUIDE.md)** - Complete integration

### Example Workers

- **[Python Worker](./examples/workers/python/)** - Python implementation
- **[PHP Worker](./examples/workers/php/)** - PHP implementation
- **[YouTube Scraper](./examples/workers/youtube/)** - Real-world example

---

## Deployment Workflow Summary

### Initial Deployment

```
1. Pre-Deployment
   └─ Run deployment checklist
   └─ Review requirements
   └─ Backup existing data

2. Backend Deployment
   └─ Upload and run check_setup.php
   └─ Run deploy.php
   └─ Verify API health

3. Frontend Deployment
   └─ Configure .env
   └─ Build package
   └─ Upload files
   └─ Run deploy.php

4. Post-Deployment
   └─ Verify all features
   └─ Monitor logs
   └─ Document deployment
```

### Update Deployment

```
1. Prepare Update
   └─ Test in staging
   └─ Backup production
   └─ Review changes

2. Update Backend
   └─ Run deploy-deploy.php
   └─ Run deploy.php (skip DB setup)
   └─ Verify API

3. Update Frontend
   └─ Build new package
   └─ Upload files
   └─ Verify application

4. Monitor
   └─ Watch error logs
   └─ Check performance
   └─ User feedback
```

---

## Support & Resources

### Documentation Index

**[Complete Documentation Index](./docs/README.md)** - Full documentation organized by role

### Quick Navigation

- **🚀 [Getting Started](./docs/getting-started/README.md)** - New users start here
- **👨‍💻 [Development](./docs/development/README.md)** - Developers and contributors
- **🏗️ [Architecture](./docs/architecture/README.md)** - System design
- **🚀 [Operations](./docs/operations/README.md)** - Deployment and release

### Additional Resources

- **[API Examples](./examples/)** - Code examples
- **[Templates](./templates/)** - Documentation templates
- **[Scripts](./\_scripts/)** - Utility scripts
- **[Tests](./tests/)** - Testing documentation

### Getting Help

- **Main README**: [PrismQ.Client README](../README.md)
- **Backend README**: [Backend/TaskManager README](../Backend/TaskManager/README.md)
- **Frontend README**: [Frontend/TaskManager README](../Frontend/TaskManager/README.md)
- **Issue Tracker**: GitHub Issues

---

## Deployment Best Practices

### Before Deployment

✅ Always test in staging environment first  
✅ Run all tests (unit, integration, end-to-end)  
✅ Review code changes and documentation  
✅ Backup production data  
✅ Plan rollback strategy  
✅ Communicate with stakeholders  

### During Deployment

✅ Follow deployment checklist  
✅ Monitor logs in real-time  
✅ Verify each step before proceeding  
✅ Keep team informed of progress  
✅ Document any issues or deviations  

### After Deployment

✅ Verify all critical features  
✅ Monitor error rates and performance  
✅ Check user feedback  
✅ Update documentation  
✅ Create deployment report  
✅ Plan for next release  

---

## Version History

### v1.0.0 (2025-11-11)
- Initial global deployment guide
- Consolidated Backend and Frontend deployment documentation
- Added deployment options and prerequisites
- Included troubleshooting and monitoring sections
- Linked to all related deployment resources

---

**Maintained By**: PrismQ Development Team  
**Questions**: Refer to module-specific documentation or GitHub Issues  
**Last Review**: 2025-11-11
