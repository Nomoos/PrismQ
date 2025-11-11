# Deployment Documentation

This directory contains deployment guides and operational documentation.

## Quick Start

- **[QUICK_START_DEPLOY.md](QUICK_START_DEPLOY.md)** - Fast deployment guide (START HERE)

## Deployment Guides

### Setup & Configuration
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Comprehensive deployment instructions
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment overview and requirements
- **[DEPLOYMENT_SCRIPT.md](DEPLOYMENT_SCRIPT.md)** - Deployment script documentation
- **[CHECK_SETUP_GUIDE.md](CHECK_SETUP_GUIDE.md)** - Environment validation guide

### Hosting
- **[HOSTING_INFO.md](HOSTING_INFO.md)** - Hosting requirements and recommendations

## Operations

### Performance & Monitoring
- **[PRODUCTION_OPTIMIZATION_GUIDE.md](PRODUCTION_OPTIMIZATION_GUIDE.md)** - Production optimization strategies
- **[PERFORMANCE_MONITORING.md](PERFORMANCE_MONITORING.md)** - Performance monitoring setup
- **[PERFORMANCE_MONITORING_STRATEGY.md](PERFORMANCE_MONITORING_STRATEGY.md)** - Monitoring strategy overview

## Deployment Checklist

1. ✅ Run `php check_setup.php` to validate environment
2. ✅ Configure database credentials
3. ✅ Run `php setup_database.php` or `./setup_database.sh`
4. ✅ Deploy code using `deploy.php`
5. ✅ Verify installation with test suite
6. ✅ Access Swagger UI to test endpoints
