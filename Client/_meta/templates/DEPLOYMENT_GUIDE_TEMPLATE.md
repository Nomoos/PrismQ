# [Component Name] Deployment Guide

**Version**: [X.Y.Z]  
**Last Updated**: [YYYY-MM-DD]  
**Target Environment**: [Production / Staging / Shared Hosting]

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Deployment Steps](#deployment-steps)
- [Configuration](#configuration)
- [Verification](#verification)
- [Post-Deployment Tasks](#post-deployment-tasks)
- [Rollback Procedure](#rollback-procedure)
- [Troubleshooting](#troubleshooting)
- [Monitoring](#monitoring)

---

## Overview

This guide provides step-by-step instructions for deploying [Component Name] to [environment type].

### Deployment Strategy

- **Method**: [Manual / Automated / CI/CD]
- **Downtime**: [Expected downtime, if any]
- **Rollback Time**: [Estimated time to rollback]

### What Gets Deployed

- [Component 1]: [Description]
- [Component 2]: [Description]
- [Database Changes]: [Yes/No - describe if yes]
- [Configuration Changes]: [Yes/No - describe if yes]

---

## Prerequisites

### System Requirements

**Server Requirements**:
- **OS**: [Linux / Windows / macOS] [specific version]
- **CPU**: [Minimum cores/speed]
- **RAM**: [Minimum memory]
- **Disk Space**: [Minimum storage]
- **Network**: [Required ports, bandwidth]

**Software Requirements**:
- [Runtime 1]: [Version] (e.g., PHP 8.0+)
- [Runtime 2]: [Version] (e.g., Node.js 18+)
- [Database]: [Version] (e.g., MySQL 5.7+)
- [Web Server]: [Version] (e.g., Apache 2.4+ with mod_rewrite)

**Access Requirements**:
- [ ] SSH/FTP access to server
- [ ] Database admin credentials
- [ ] DNS configuration access (if needed)
- [ ] SSL certificate (for HTTPS)
- [ ] Required API keys/secrets

### Local Tools

- [ ] [Tool 1] (e.g., Git)
- [ ] [Tool 2] (e.g., Composer)
- [ ] [Tool 3] (e.g., npm)
- [ ] [FTP/SFTP client] (e.g., FileZilla)

---

## Pre-Deployment Checklist

### Code Preparation

- [ ] All code merged to release branch
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Version number updated
- [ ] CHANGELOG.md updated
- [ ] Dependencies up to date
- [ ] Build completed successfully
- [ ] Security scan completed

### Environment Preparation

- [ ] Backup current production code
- [ ] Backup current database
- [ ] Verify server resources available
- [ ] Review server logs for issues
- [ ] Test deployment on staging
- [ ] Prepare rollback plan
- [ ] Notify stakeholders of deployment

### Configuration Review

- [ ] Environment variables reviewed
- [ ] Configuration files prepared
- [ ] Database credentials verified
- [ ] API keys/secrets ready
- [ ] SSL certificates valid
- [ ] DNS settings verified

---

## Deployment Steps

### Step 1: Environment Check

**Verify server environment meets requirements**:

```bash
# Check PHP version
php -v

# Check required PHP extensions
php -m | grep -E 'pdo_mysql|json|mbstring'

# Check web server
apache2 -v  # or nginx -v

# Check database
mysql --version

# Check disk space
df -h

# Check permissions
ls -la /path/to/deployment/directory
```

**Expected Output**:
```
[Provide example of successful output]
```

### Step 2: Backup Current Installation

**Backup files**:
```bash
# Create backup directory with timestamp
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup application files
cp -r /path/to/app "$BACKUP_DIR/"

# Or use tar for compression
tar -czf "$BACKUP_DIR/app_backup.tar.gz" /path/to/app
```

**Backup database**:
```bash
# MySQL/MariaDB
mysqldump -u username -p database_name > "$BACKUP_DIR/database_backup.sql"

# Add timestamp to filename
mysqldump -u username -p database_name > "$BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sql"
```

### Step 3: Download/Upload Application Files

**Option A: Using Git** (Recommended):
```bash
# Clone repository
cd /path/to/deployment
git clone https://github.com/username/repo.git

# Or pull latest changes
cd /path/to/app
git pull origin main
git checkout v[X.Y.Z]  # Specific version tag
```

**Option B: Using FTP/SFTP**:
```bash
# Upload files using CLI
sftp user@server.com
put -r /local/path/to/files /remote/path/

# Or use FTP client like FileZilla
# - Connect to server
# - Navigate to deployment directory
# - Upload files
```

**Option C: Using rsync**:
```bash
rsync -avz --exclude '.git' \
  /local/path/to/app/ \
  user@server.com:/remote/path/to/app/
```

### Step 4: Install Dependencies

**PHP dependencies** (if applicable):
```bash
cd /path/to/app
composer install --no-dev --optimize-autoloader
```

**Node.js dependencies** (if applicable):
```bash
cd /path/to/app
npm install --production
npm run build
```

**Python dependencies** (if applicable):
```bash
cd /path/to/app
pip install -r requirements.txt
```

### Step 5: Database Setup

**Create database** (if new installation):
```bash
mysql -u root -p
```

```sql
CREATE DATABASE database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON database_name.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Run migrations**:
```bash
# Import schema
mysql -u app_user -p database_name < schema.sql

# Or run migrations
php artisan migrate  # Laravel example
# npm run migrate     # Node.js example
```

### Step 6: Configuration

**Create configuration file**:
```bash
# Copy template
cp config.example.php config.php

# Or create from scratch
cat > config.php << 'EOF'
<?php
return [
    'database' => [
        'host' => 'localhost',
        'name' => 'database_name',
        'user' => 'app_user',
        'password' => 'secure_password'
    ],
    'api_key' => 'your_api_key',
    'debug' => false
];
EOF
```

**Set environment variables**:
```bash
# Create .env file
cat > .env << 'EOF'
DB_HOST=localhost
DB_NAME=database_name
DB_USER=app_user
DB_PASSWORD=secure_password
API_KEY=your_api_key
DEBUG=false
EOF
```

**Update configuration values**:
- Database credentials
- API keys
- Base URL
- Debug mode (should be `false` in production)
- Cache settings
- Session settings

### Step 7: Set File Permissions

```bash
# Set proper ownership
chown -R www-data:www-data /path/to/app

# Set directory permissions
find /path/to/app -type d -exec chmod 755 {} \;

# Set file permissions
find /path/to/app -type f -exec chmod 644 {} \;

# Writable directories (logs, cache, uploads)
chmod -R 775 /path/to/app/storage
chmod -R 775 /path/to/app/cache
chmod -R 775 /path/to/app/uploads

# Secure sensitive files
chmod 600 /path/to/app/config.php
chmod 600 /path/to/app/.env
```

### Step 8: Web Server Configuration

**Apache (.htaccess)**:
```apache
# Enable mod_rewrite
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    
    # Redirect to HTTPS
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]
    
    # Route all requests to index.php
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^(.*)$ index.php/$1 [L]
</IfModule>

# Security headers
<IfModule mod_headers.c>
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "SAMEORIGIN"
    Header set X-XSS-Protection "1; mode=block"
</IfModule>

# Deny access to sensitive files
<FilesMatch "^\.">
    Order allow,deny
    Deny from all
</FilesMatch>
```

**Nginx** (if applicable):
```nginx
server {
    listen 80;
    server_name example.com;
    root /path/to/app/public;
    index index.php index.html;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;
    root /path/to/app/public;
    index index.php index.html;

    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.0-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
}
```

### Step 9: SSL/TLS Configuration

**Using Let's Encrypt** (free):
```bash
# Install certbot
apt-get update
apt-get install certbot python3-certbot-apache

# Obtain certificate
certbot --apache -d example.com -d www.example.com

# Auto-renewal
certbot renew --dry-run
```

**Manual SSL certificate**:
```bash
# Copy certificate files
cp cert.pem /path/to/ssl/
cp key.pem /path/to/ssl/
cp ca-bundle.pem /path/to/ssl/

# Set permissions
chmod 600 /path/to/ssl/key.pem
chmod 644 /path/to/ssl/cert.pem
```

---

## Configuration

### Required Configuration

**Database Configuration**:
```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=app_database
DB_USER=app_user
DB_PASSWORD=secure_password_here
```

**Application Configuration**:
```
APP_URL=https://example.com
APP_ENV=production
APP_DEBUG=false
APP_KEY=base64:random_key_here
```

**Cache Configuration**:
```
CACHE_DRIVER=file
SESSION_DRIVER=file
QUEUE_DRIVER=database
```

### Optional Configuration

**Email Configuration** (if applicable):
```
MAIL_HOST=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=noreply@example.com
MAIL_PASSWORD=email_password
MAIL_ENCRYPTION=tls
```

**External Services** (if applicable):
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
```

---

## Verification

### Step 1: Basic Health Check

```bash
# Check if web server is running
curl -I https://example.com

# Expected: HTTP/1.1 200 OK
```

### Step 2: Test Endpoints

```bash
# Test homepage
curl https://example.com

# Test API health endpoint
curl https://example.com/api/health

# Expected response:
# {"status":"ok","version":"1.0.0"}
```

### Step 3: Database Connection

```bash
# Test database connectivity
php artisan tinker  # Laravel example
# >>> DB::select('SELECT 1');

# Or use custom test script
php test-db-connection.php
```

### Step 4: Functionality Tests

- [ ] User can access homepage
- [ ] API endpoints respond correctly
- [ ] Database queries work
- [ ] File uploads work (if applicable)
- [ ] Email sending works (if applicable)
- [ ] Cron jobs scheduled (if applicable)

### Step 5: Performance Check

```bash
# Check response time
time curl https://example.com

# Load test (if appropriate)
ab -n 100 -c 10 https://example.com/
```

---

## Post-Deployment Tasks

### Immediate Tasks

- [ ] Clear application cache
- [ ] Clear web server cache
- [ ] Warm up application cache
- [ ] Verify all critical features
- [ ] Monitor error logs for 15-30 minutes
- [ ] Check performance metrics
- [ ] Update documentation

### Cache Management

```bash
# Clear application cache
php artisan cache:clear  # Laravel
# npm run cache:clear    # Node.js

# Clear web server cache
# Apache
service apache2 reload

# Nginx
nginx -s reload
```

### Monitoring Setup

- [ ] Enable application monitoring
- [ ] Set up error alerting
- [ ] Configure uptime monitoring
- [ ] Set up log aggregation
- [ ] Enable performance monitoring

### Communication

- [ ] Notify team of successful deployment
- [ ] Update status page (if applicable)
- [ ] Announce new features to users (if applicable)
- [ ] Document any issues encountered

---

## Rollback Procedure

### When to Rollback

Consider rollback if:
- Critical functionality is broken
- Database migrations fail
- Performance degradation > [X%]
- Error rate increases significantly
- Security vulnerability discovered

### Quick Rollback Steps

**1. Restore application files**:
```bash
# If using Git
cd /path/to/app
git checkout [previous-version-tag]

# If using backup
rm -rf /path/to/app
cp -r backup_YYYYMMDD_HHMMSS/app /path/to/app
```

**2. Restore database** (if needed):
```bash
mysql -u username -p database_name < backup_YYYYMMDD_HHMMSS/database_backup.sql
```

**3. Restore configuration**:
```bash
cp backup_YYYYMMDD_HHMMSS/config.php /path/to/app/config.php
cp backup_YYYYMMDD_HHMMSS/.env /path/to/app/.env
```

**4. Clear cache and restart**:
```bash
# Clear cache
php artisan cache:clear

# Restart web server
service apache2 restart  # or nginx
```

**5. Verify rollback**:
```bash
curl https://example.com/api/health
```

---

## Troubleshooting

### Common Issues

#### Issue 1: "500 Internal Server Error"

**Symptoms**: White page or generic error message

**Solution**:
```bash
# Check error logs
tail -f /var/log/apache2/error.log

# Common causes:
# 1. Wrong file permissions
chmod -R 755 /path/to/app

# 2. Missing .htaccess
# Verify .htaccess file exists and mod_rewrite is enabled

# 3. PHP errors
# Enable error display temporarily (disable after fixing)
php -d display_errors=1 /path/to/app/index.php
```

#### Issue 2: "Database Connection Failed"

**Symptoms**: Cannot connect to database

**Solution**:
```bash
# Verify database credentials
mysql -u app_user -p -h localhost database_name

# Check if database exists
mysql -u root -p -e "SHOW DATABASES;"

# Verify user permissions
mysql -u root -p -e "SHOW GRANTS FOR 'app_user'@'localhost';"
```

#### Issue 3: "Permission Denied"

**Symptoms**: Cannot write to files/directories

**Solution**:
```bash
# Fix ownership
chown -R www-data:www-data /path/to/app

# Fix permissions
chmod -R 775 /path/to/app/storage
chmod -R 775 /path/to/app/cache
```

#### Issue 4: "Module Not Found" or "Class Not Found"

**Symptoms**: PHP/Node.js errors about missing dependencies

**Solution**:
```bash
# Reinstall dependencies
composer install --no-dev --optimize-autoloader
# or
npm install --production

# Clear autoload cache
composer dump-autoload
```

### Getting Help

- **Documentation**: [Link to docs]
- **Support Email**: [email]
- **Issue Tracker**: [Link to GitHub issues]
- **Emergency Contact**: [Phone/Slack/Discord]

---

## Monitoring

### Key Metrics to Monitor

**Application Metrics**:
- Response time (should be < [X]ms)
- Error rate (should be < [Y]%)
- Request rate
- Active users

**Server Metrics**:
- CPU usage (should be < [X]%)
- Memory usage (should be < [Y]%)
- Disk space (should have > [Z]GB free)
- Network bandwidth

**Database Metrics**:
- Query time
- Connection pool usage
- Slow query count

### Monitoring Tools

- **Application Logs**: `/path/to/app/logs/`
- **Web Server Logs**: `/var/log/apache2/` or `/var/log/nginx/`
- **Database Logs**: `/var/log/mysql/`
- **System Monitoring**: [Tool name, e.g., Nagios, New Relic]

### Log Files

```bash
# Application logs
tail -f /path/to/app/storage/logs/app.log

# Web server access log
tail -f /var/log/apache2/access.log

# Web server error log
tail -f /var/log/apache2/error.log

# PHP error log
tail -f /var/log/php/error.log
```

---

## Maintenance

### Regular Maintenance Tasks

**Daily**:
- [ ] Monitor error logs
- [ ] Check application health
- [ ] Verify backup completion

**Weekly**:
- [ ] Review performance metrics
- [ ] Check disk space
- [ ] Update dependencies (security patches)

**Monthly**:
- [ ] Full system audit
- [ ] Performance optimization
- [ ] Database maintenance (vacuum, optimize)
- [ ] Review and rotate logs

### Backup Schedule

- **Frequency**: [Daily/Weekly]
- **Retention**: [Keep last X backups]
- **Location**: [Backup storage location]
- **Verification**: [How to verify backups]

---

## Security Checklist

- [ ] HTTPS enabled and enforced
- [ ] Strong database passwords
- [ ] File permissions properly set
- [ ] Sensitive files not publicly accessible
- [ ] Security headers configured
- [ ] Regular security updates applied
- [ ] Firewall rules configured
- [ ] Fail2ban or similar protection enabled
- [ ] Regular security audits scheduled

---

## Version History

### v1.0.0 (YYYY-MM-DD)
- Initial deployment guide

### v1.1.0 (YYYY-MM-DD)
- Added SSL/TLS configuration
- Updated troubleshooting section

---

**Deployment Guide Version**: 1.0  
**Last Updated**: [YYYY-MM-DD]  
**Maintained by**: [Team/Person Name]  
**Questions**: [Contact information]
