# TaskManager Deployment Guide

Complete step-by-step guide for deploying TaskManager to Vedos shared hosting or any PHP/MySQL hosting provider.

> 📋 **Hosting Account Information**: See [HOSTING_INFO.md](HOSTING_INFO.md) for details about the Vedos/Wedos hosting account, including resource allocation and account status.

## Prerequisites

- Shared hosting account with:
  - PHP 7.4+ support
  - MySQL 5.7+ or MariaDB 10.2+
  - Apache with mod_rewrite
  - FTP/SFTP or file manager access
- Database credentials (usually provided by hosting provider)
- FTP client (FileZilla, WinSCP, etc.) or SSH access

## Step 1: Prepare Database

### Option A: Using phpMyAdmin (Common on Shared Hosting)

1. Log into your hosting control panel (cPanel, Plesk, etc.)
2. Open phpMyAdmin
3. Create a new database:
   - Click "New" or "Create Database"
   - Name: `taskmanager` (or your preferred name)
   - Click "Create"
4. Create a database user (if not using existing):
   - Go to "Users" tab
   - Click "Add user"
   - Username: `taskmanager_user`
   - Password: Generate strong password
   - Host: `localhost`
   - Grant all privileges on the `taskmanager` database
5. Import schema:
   - Select your database from the left sidebar
   - Click "Import" tab
   - Click "Choose File" and select `database/schema.sql`
   - Click "Go"
   - Verify tables are created: `task_types`, `tasks`, `task_history`

### Option B: Using MySQL Command Line

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE taskmanager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Create user and grant privileges
mysql -u root -p -e "CREATE USER 'taskmanager_user'@'localhost' IDENTIFIED BY 'your_secure_password';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON taskmanager.* TO 'taskmanager_user'@'localhost';"
mysql -u root -p -e "FLUSH PRIVILEGES;"

# Import schema
mysql -u taskmanager_user -p taskmanager < database/schema.sql
```

## Step 2: Configure Application

1. Copy configuration template:
   ```bash
   cp config/config.example.php config/config.php
   ```

2. Edit `config/config.php` with your database credentials:
   ```php
   <?php
   define('DB_HOST', 'localhost');           // Usually 'localhost' on shared hosting
   define('DB_NAME', 'taskmanager');         // Your database name
   define('DB_USER', 'taskmanager_user');    // Your database username
   define('DB_PASS', 'your_secure_password'); // Your database password
   define('DB_CHARSET', 'utf8mb4');
   
   // Keep other settings as default or adjust as needed
   define('TASK_CLAIM_TIMEOUT', 300);
   define('MAX_TASK_ATTEMPTS', 3);
   define('ENABLE_TASK_HISTORY', true);
   define('ENABLE_SCHEMA_VALIDATION', true);
   
   date_default_timezone_set('UTC');
   ?>
   ```

3. **Important**: Secure the config file
   - Set file permissions to 644 or 640
   - Never commit config.php to version control
   - Keep config.example.php as a template only

## Step 3: Upload Files to Server

### Recommended Directory Structure on Server

```
public_html/
├── api/                         # TaskManager API (publicly accessible)
│   ├── .htaccess
│   ├── index.php
│   ├── ApiResponse.php
│   ├── TaskController.php
│   ├── TaskTypeController.php
│   └── JsonSchemaValidator.php
├── taskmanager/                 # Private files (above public_html or protected)
│   ├── config/
│   │   ├── config.php          # SECURE THIS - contains credentials
│   │   └── config.example.php
│   └── database/
│       ├── Database.php
│       └── schema.sql
└── .htaccess                    # Root htaccess (if needed)
```

### Upload via FTP/SFTP

1. Connect to your server using FTP client
2. Navigate to `public_html` (or `www`, `htdocs` depending on host)
3. Create `api` directory if it doesn't exist
4. Upload all files from `Backend/TaskManager/api/` to `public_html/api/`
5. Create `taskmanager` directory (preferably outside public_html for security)
6. Upload `config/` and `database/` directories to `taskmanager/`
7. Update paths in `api/index.php` if needed:
   ```php
   // Update this line to point to your config location
   require_once __DIR__ . '/../../taskmanager/config/config.php';
   ```

### Alternative: Upload to Subdirectory

If you want TaskManager at `/taskmanager/api/`:
```
public_html/
└── taskmanager/
    ├── api/          # Publicly accessible API
    └── private/      # Protected files (config, database classes)
```

Update `.htaccess` RewriteBase accordingly.

## Step 4: Configure Apache (mod_rewrite)

The `.htaccess` file should already be configured, but verify:

```apache
RewriteEngine On
RewriteBase /api/

RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php [QSA,L]
```

**Important**: Adjust `RewriteBase` to match your actual path:
- Root: `RewriteBase /api/`
- Subdirectory: `RewriteBase /taskmanager/api/`

### Verify mod_rewrite is enabled

Test with health check endpoint:
```bash
curl https://yourdomain.com/api/health
```

If you get 404, check:
1. Apache mod_rewrite is enabled (ask hosting support)
2. `.htaccess` files are being read (AllowOverride enabled)
3. Path in RewriteBase matches your directory structure

## Step 5: Set File Permissions

Recommended permissions for shared hosting:

```bash
# Directories
chmod 755 api/
chmod 755 taskmanager/
chmod 755 taskmanager/config/
chmod 755 taskmanager/database/

# Files
chmod 644 api/*.php
chmod 644 api/.htaccess
chmod 640 taskmanager/config/config.php  # More restrictive for config
chmod 644 taskmanager/database/*.php
```

**Security Note**: 
- Config files should NOT be in publicly accessible directories
- If they must be, protect with .htaccess:
  ```apache
  <Files "config.php">
      Order Allow,Deny
      Deny from all
  </Files>
  ```

## Step 6: Test Installation

### 1. Health Check
```bash
curl https://yourdomain.com/api/health
```

Expected response:
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "status": "healthy",
    "timestamp": 1699999999
  },
  "timestamp": 1699999999
}
```

### 2. Test Task Type Registration
```bash
curl -X POST https://yourdomain.com/api/task-types/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test.Simple",
    "version": "1.0.0",
    "param_schema": {
      "type": "object",
      "properties": {
        "message": {"type": "string"}
      },
      "required": ["message"]
    }
  }'
```

### 3. Test Task Creation
```bash
curl -X POST https://yourdomain.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Test.Simple",
    "params": {
      "message": "Hello World"
    }
  }'
```

### 4. Test Task Claiming
```bash
curl -X POST https://yourdomain.com/api/tasks/claim \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": "test-worker"
  }'
```

If all tests pass, your installation is successful! 🎉

## Step 7: Configure Error Logging

1. Create a log directory (outside public_html):
   ```bash
   mkdir /home/username/logs/taskmanager
   chmod 755 /home/username/logs/taskmanager
   ```

2. Configure PHP error logging in `api/.htaccess` or `php.ini`:
   ```apache
   php_flag log_errors On
   php_value error_log /home/username/logs/taskmanager/php_errors.log
   ```

3. Monitor logs for issues:
   ```bash
   tail -f /home/username/logs/taskmanager/php_errors.log
   ```

## Step 8: Security Hardening

### 1. Database Security
- Use strong passwords (20+ characters, mixed case, numbers, symbols)
- Grant only necessary privileges to database user
- Regularly update passwords
- Keep database backups

### 2. File Security
- Keep config files outside public directories
- Set restrictive permissions (640 for config.php)
- Disable directory listing in .htaccess
- Use HTTPS only (force with .htaccess redirect)

### 3. API Security
Consider adding API authentication:

```php
// In api/index.php, before routing:
$api_key = $_SERVER['HTTP_X_API_KEY'] ?? '';
if ($api_key !== 'your_secret_api_key') {
    ApiResponse::error('Unauthorized', 401);
}
```

Then clients must send:
```bash
curl -H "X-API-Key: your_secret_api_key" ...
```

### 4. Force HTTPS
Add to root `.htaccess`:
```apache
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

## Step 9: Monitoring Setup

### Create Simple Monitoring Script

`monitor.php`:
```php
<?php
require_once 'config/config.php';
require_once 'database/Database.php';

$db = Database::getInstance()->getConnection();

// Count tasks by status
$stmt = $db->query("SELECT status, COUNT(*) as count FROM tasks GROUP BY status");
$stats = $stmt->fetchAll(PDO::FETCH_KEY_PAIR);

echo "Task Statistics:\n";
foreach ($stats as $status => $count) {
    echo "  $status: $count\n";
}

// Check for stuck claimed tasks
$timeout = date('Y-m-d H:i:s', time() - TASK_CLAIM_TIMEOUT);
$stmt = $db->prepare("SELECT COUNT(*) FROM tasks WHERE status = 'claimed' AND claimed_at < ?");
$stmt->execute([$timeout]);
$stuck = $stmt->fetchColumn();

echo "Stuck claimed tasks: $stuck\n";
```

Run periodically via cron:
```bash
*/5 * * * * php /path/to/monitor.php >> /path/to/logs/monitor.log 2>&1
```

## Troubleshooting

### Issue: "Database connection failed"
**Solutions**:
- Verify database credentials in config.php
- Check if database exists and user has permissions
- Test connection with mysql command line
- Check if MySQL service is running
- Review PHP error logs

### Issue: "Route not found" or 404 errors
**Solutions**:
- Verify .htaccess file is present and readable
- Check Apache mod_rewrite is enabled (ask hosting support)
- Verify RewriteBase matches your directory structure
- Check Apache error logs
- Test with direct file access: `/api/index.php?test`

### Issue: "Class not found" errors
**Solutions**:
- Verify all PHP files were uploaded correctly
- Check file paths in require_once statements
- Ensure PHP files have correct permissions (644)
- Check for PHP version compatibility (need 7.4+)

### Issue: "Permission denied" errors
**Solutions**:
- Adjust file permissions (see Step 5)
- Check directory ownership
- Verify PHP can read config files
- Check SELinux settings (if applicable)

### Issue: Tasks not being claimed
**Solutions**:
- Check task status in database
- Verify TASK_CLAIM_TIMEOUT isn't too low
- Ensure worker_id matches when claiming/completing
- Check for database locking issues

## Vedos-Specific Configuration

If deploying to Vedos hosting:

1. **Database Access**: Use provided phpMyAdmin interface
2. **PHP Version**: Select PHP 7.4+ in control panel
3. **File Manager**: Use built-in file manager if FTP not available
4. **Cron Jobs**: May be limited on shared plans, adjust monitoring accordingly
5. **Resource Limits**: Be aware of shared hosting limits:
   - Memory: Usually 128MB
   - Execution time: Usually 30 seconds
   - Database connections: Limited pool

## Backup Strategy

### Database Backups
```bash
# Daily backup via cron
mysqldump -u taskmanager_user -p taskmanager > backup_$(date +%Y%m%d).sql

# Keep last 7 days
find /path/to/backups -name "backup_*.sql" -mtime +7 -delete
```

### File Backups
- Keep backups of config.php
- Version control API files (but not config.php)
- Document any custom modifications

## Next Steps

1. Set up worker implementations (see main README.md)
2. Configure monitoring and alerting
3. Set up regular database backups
4. Document your specific TaskType schemas
5. Create worker deployment guide for your specific use case

## Related Documentation

For more information, see:
- **[README.md](../README.md)** - Overview and quick start
- **[DATA_DRIVEN_ARCHITECTURE.md](DATA_DRIVEN_ARCHITECTURE.md)** - Complete guide to data-driven API architecture
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation

## Support

For issues or questions:
- Check troubleshooting section above
- Review PHP error logs
- Check Apache error logs
- Verify database connection and permissions
- Test with simple curl commands

---

**Deployment Checklist**:
- [ ] Database created and schema imported
- [ ] Config file created with correct credentials
- [ ] Files uploaded to correct directories
- [ ] File permissions set correctly
- [ ] .htaccess configured with correct RewriteBase
- [ ] Health check endpoint returns success
- [ ] Task type registration works
- [ ] Task creation works
- [ ] Task claiming works
- [ ] Error logging configured
- [ ] HTTPS enforced
- [ ] API authentication added (recommended)
- [ ] Monitoring script created
- [ ] Backup strategy implemented
