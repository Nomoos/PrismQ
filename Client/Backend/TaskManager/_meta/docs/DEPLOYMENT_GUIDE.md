# TaskManager Deployment Guide

## Quick Reference

This guide provides essential information for deploying the TaskManager backend API. For detailed step-by-step instructions, see the [comprehensive deployment guide](deployment/DEPLOYMENT_GUIDE.md).

## Prerequisites

Before deploying TaskManager, ensure your environment meets these requirements:

- **PHP**: 8.0 or higher
- **MySQL**: 5.7+ or MariaDB 10.2+
- **PHP Extensions**: PDO, PDO_MySQL, JSON, cURL
- **Apache**: mod_rewrite enabled
- **Permissions**: Write access to deployment directory

## Quick Start

### 1. Environment Check (Recommended First Step)

Before deployment, verify your server meets all requirements:

```bash
# Upload check_setup.php to your server
php check_setup.php
```

Or access via browser: `https://yourdomain.com/check_setup.php`

### 2. Deploy

**Web-based (Recommended for shared hosting):**

1. Upload `deploy.php` to your server
2. Navigate to `https://yourdomain.com/deploy.php`
3. Enter admin password and database credentials
4. Click "Deploy TaskManager"

**Command-line:**

```bash
php deploy.php
```

### 3. Verify Installation

Test the API health endpoint:

```bash
curl https://yourdomain.com/taskmanager/api/health
```

Expected response:
```json
{
  "success": true,
  "message": "TaskManager API is healthy",
  "data": {
    "status": "healthy",
    "timestamp": "2025-11-11T09:00:00Z"
  }
}
```

## Post-Deployment

### Access API Documentation

Interactive Swagger UI is available at:
```
https://yourdomain.com/taskmanager/api/docs/
```

### Directory Structure

```
TaskManager/
├── api/              # REST API endpoints
├── config/           # Configuration files
├── database/         # Database schema and utilities
└── public/           # Public assets (Swagger UI, OpenAPI spec)
```

### Security Checklist

- [ ] Change default admin password in `deploy.php`
- [ ] Secure `config/config.php` with appropriate permissions (640)
- [ ] Enable HTTPS/SSL
- [ ] Configure API authentication
- [ ] Set up regular backups

## Common Issues

### Authentication Failed
- Verify the admin password in `deploy.php` matches your input
- Ensure you changed it from the default `changeme123`

### Database Connection Failed
- Check database credentials
- Verify database exists and is accessible
- Ensure MySQL service is running

### Missing PHP Extensions
- Enable required extensions via php.ini or hosting control panel
- Contact hosting provider if needed

## Detailed Documentation

For comprehensive deployment instructions, troubleshooting, and advanced configuration:

- **[Full Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)** - Complete step-by-step instructions
- **[Quick Start](deployment/QUICK_START_DEPLOY.md)** - Fastest path to deployment
- **[Environment Check Guide](deployment/CHECK_SETUP_GUIDE.md)** - Pre-deployment verification
- **[Performance Monitoring](deployment/PERFORMANCE_MONITORING.md)** - Production monitoring setup
- **[Hosting Information](deployment/HOSTING_INFO.md)** - Hosting-specific notes

## API Usage

After deployment, you can:

1. **Register task types** via `/api/task-types/register`
2. **Enqueue tasks** via `/api/tasks/enqueue`
3. **Claim tasks** via `/api/tasks/claim`
4. **Complete tasks** via `/api/tasks/complete`

See the [API Reference](api/API_REFERENCE.md) for complete endpoint documentation.

## Architecture

TaskManager uses a data-driven architecture:

- **Data-driven endpoints** - API endpoints configured in database
- **Dynamic routing** - Endpoints discovered and routed at runtime
- **Task queue** - Persistent task management with status tracking
- **Type system** - Flexible task types with JSON schema validation

Learn more in the [Architecture Documentation](architecture/DATA_DRIVEN_ARCHITECTURE.md).

## Support

- **[Main README](../README.md)** - Project overview
- **[Documentation Index](README.md)** - All documentation
- **[Examples](../examples/)** - Code examples and templates
- **[Tests](../tests/)** - Test suite and guides

## Next Steps

After successful deployment:

1. Configure workers to process tasks
2. Register your task types via API
3. Monitor task queue and performance
4. Set up automated backups
5. Review security settings

For detailed information on each step, refer to the [comprehensive deployment guide](deployment/DEPLOYMENT_GUIDE.md).
