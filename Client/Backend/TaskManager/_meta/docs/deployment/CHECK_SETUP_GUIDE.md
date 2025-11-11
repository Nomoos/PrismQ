# TaskManager Environment Check Guide

## Overview

The `check_setup.php` script validates that your shared hosting environment meets all requirements for running TaskManager. **Always run this script before attempting deployment** to identify and fix potential issues.

## Why Run This Check?

Running the environment check before deployment helps you:
- ✅ Identify missing PHP extensions or incorrect versions
- ✅ Verify file and directory permissions
- ✅ Confirm MySQL/MariaDB support
- ✅ Check available disk space and memory limits
- ✅ Validate Apache configuration
- ✅ Save time by catching issues early

## Quick Start

### Method 1: Command Line (SSH Access)

If you have SSH access to your server:

```bash
# Upload check_setup.php to your server directory
# Then run:
php check_setup.php
```

**Expected Output:**
```
=====================================
TaskManager Environment Check
=====================================

✓ PHP Version: PHP 8.1.2
✓ PHP Extensions: All required extensions present
✓ Directory Permissions: Installation directory is writable
✓ MySQL Support: MySQL/MariaDB support available via PDO
✓ Disk Space: 2048.00 MB available
...

=====================================
Summary
=====================================

Checks passed: 14/14

✓ Your environment is ready for TaskManager deployment!

Next steps:
1. Run: php deploy.php
2. Or access deploy.php via web browser
```

### Method 2: Web Browser (Most Common for Shared Hosting)

1. **Upload the Script**
   - Use FTP, cPanel File Manager, or your hosting provider's file upload tool
   - Upload `check_setup.php` to your desired installation directory
   - Example: `/home/yourusername/public_html/taskmanager/`

2. **Access Via Browser**
   - Navigate to: `https://yourdomain.com/taskmanager/check_setup.php`
   - Replace `yourdomain.com` and `taskmanager` with your actual domain and path

3. **Review Results**
   - Green checkmarks (✓) indicate passed checks
   - Red X marks (✗) indicate failed checks that must be fixed
   - Yellow warnings suggest improvements but won't block deployment

## What Gets Checked

### 1. PHP Version
- **Requirement**: PHP 7.4 or higher
- **Recommended**: PHP 8.0 or higher
- **Why**: TaskManager uses modern PHP features for security and performance

**How to Fix:**
- Most shared hosting control panels (cPanel, Plesk) allow you to select PHP version
- Contact your hosting provider if you can't change the PHP version

### 2. PHP Extensions

**Required Extensions:**
- `pdo` - Database abstraction layer
- `pdo_mysql` - MySQL/MariaDB driver
- `json` - JSON data handling
- `curl` - HTTP requests for GitHub file downloads

**Recommended Extensions:**
- `mbstring` - Multi-byte string handling
- `openssl` - Secure connections

**How to Fix:**
- Enable extensions via PHP settings in your hosting control panel
- For cPanel: Software → Select PHP Version → Extensions
- Contact hosting support if extensions can't be enabled

### 3. File and Directory Permissions

**What's Checked:**
- Can write to installation directory
- Can create new files
- Can create subdirectories

**How to Fix:**
```bash
# Set directory permissions (via SSH)
chmod 755 /path/to/taskmanager

# Or use your hosting control panel's File Manager
# Right-click folder → Permissions → Set to 755
```

### 4. Apache mod_rewrite

**Why Required**: Clean URLs for API endpoints (e.g., `/api/tasks` instead of `/api/index.php?endpoint=tasks`)

**Note**: Most shared hosting providers enable mod_rewrite by default

**How to Verify:**
- Check with your hosting provider's documentation
- Most cPanel/Plesk setups have it enabled

### 5. .htaccess Support

**What's Checked**: Ability to create and use `.htaccess` files for URL rewriting

**How to Fix:**
- Usually enabled by default on shared hosting
- Ensure `AllowOverride All` is set in Apache config (hosting provider responsibility)

### 6. MySQL/MariaDB Support

**What's Checked**: PDO MySQL extension is available

**How to Fix:**
- Enable PDO MySQL extension in PHP settings
- Verify MySQL/MariaDB service is running (hosting provider responsibility)

### 7. Disk Space

**Requirements:**
- Minimum: 50 MB free space
- Recommended: 100 MB+ free space

**What It's Used For:**
- Application files (~5 MB)
- Database (~10-50 MB depending on usage)
- Logs (~5-20 MB)

**How to Fix:**
- Delete unnecessary files
- Upgrade hosting plan if needed
- Contact hosting provider for quota increase

### 8. Memory Limit

**Requirement**: At least 64 MB

**How to Fix:**
```php
// Add to .htaccess (if allowed)
php_value memory_limit 128M

// Or create/edit php.ini
memory_limit = 128M
```

### 9. Upload Limits

**What's Checked**: `upload_max_filesize` and `post_max_size`

**Why It Matters**: Affects API request sizes, especially for tasks with large parameters

**Typical Values:**
- Small: 2M / 8M
- Medium: 10M / 20M
- Large: 50M / 64M

### 10. Execution Time

**Recommendation**: 60 seconds or more

**How to Fix:**
```php
// Add to .htaccess
php_value max_execution_time 60

// Or in php.ini
max_execution_time = 60
```

### 11. OpenSSL

**Status**: Recommended but not required

**Why**: Secure HTTPS connections for downloading files from GitHub

### 12. cURL Functionality

**What's Checked**: Can make HTTPS requests

**Why**: Required to download TaskManager files from GitHub repository

## Understanding Results

### Success (All Passed)
```
✓ Your environment is ready for TaskManager deployment!

Next steps:
1. Run: php deploy.php
2. Or access deploy.php via web browser
```

**Action**: Proceed with deployment using `deploy.php`

### Partial Success (Warnings Only)
```
⚠ Warnings (2):
  • upload_max_filesize: 2M, post_max_size: 8M
  • HTTPS test inconclusive
```

**Action**: You can proceed with deployment, but consider addressing warnings for optimal performance

### Failure (Critical Issues)
```
✗ Your environment has 3 issue(s) that must be fixed:
  • PHP 7.2.5 found (7.4+ required)
  • Missing required extensions: pdo_mysql, curl
  • Installation directory is not writable
```

**Action**: Fix all critical issues before attempting deployment

## Common Issues and Solutions

### Issue: "PHP version too old"
**Solution:**
1. Log into your hosting control panel
2. Find PHP settings (usually under "Software" or "Advanced")
3. Select PHP 7.4 or higher (8.0+ recommended)
4. Save and run the check again

### Issue: "Missing required extension: pdo_mysql"
**Solution:**
1. Access PHP Extensions settings in control panel
2. Enable "pdo" and "pdo_mysql" checkboxes
3. Save changes
4. Run check again

### Issue: "Installation directory is not writable"
**Solution:**
```bash
# Via SSH:
chmod 755 /path/to/directory

# Via cPanel File Manager:
# Right-click folder → Permissions → Set to 755 (rwxr-xr-x)
```

### Issue: "Cannot detect mod_rewrite"
**Solution:**
- This is common on shared hosting
- Most shared hosts enable mod_rewrite by default
- Verify with hosting documentation
- If in doubt, proceed anyway - it will be tested during deployment

### Issue: "Disk space below minimum"
**Solution:**
1. Check what's using space: `du -sh * | sort -h`
2. Delete old backups, logs, or temporary files
3. Consider upgrading hosting plan
4. Contact hosting provider

## Shared Hosting Provider-Specific Notes

### cPanel Hosting
- PHP version: Software → Select PHP Version
- Extensions: Same section → Check desired extensions
- File Manager: File Manager → Right-click → Permissions
- MySQL: MySQL Databases → Create Database

### Plesk Hosting
- PHP version: Domains → PHP Settings → PHP version
- Extensions: Same section → PHP extensions list
- File Manager: Files → Select file/folder → Change Permissions
- MySQL: Databases → Add Database

### DirectAdmin
- PHP version: Account Manager → Select PHP version
- Extensions: Advanced Features → PHP Configuration
- File Manager: File Manager → Select → Permissions
- MySQL: MySQL Management → Create Database

## Next Steps After Successful Check

Once all checks pass:

1. **Download deploy.php**
   - Get it from the TaskManager repository
   - Or it may already be uploaded with check_setup.php

2. **Change Admin Password**
   ```php
   // In deploy.php, change:
   define('ADMIN_PASSWORD', 'changeme123');
   // To:
   define('ADMIN_PASSWORD', 'YourSecurePassword123!');
   ```

3. **Run Deployment**
   - CLI: `php deploy.php`
   - Web: `https://yourdomain.com/path/deploy.php`

4. **Follow Deployment Instructions**
   - Enter database credentials
   - Wait for files to download
   - Verify installation

## Security Note

**Important**: Delete or restrict access to `check_setup.php` after deployment to prevent information disclosure about your server environment.

```bash
# Option 1: Delete the file
rm check_setup.php

# Option 2: Restrict access via .htaccess
<Files "check_setup.php">
    Require all denied
</Files>
```

## Troubleshooting

### Script Returns Blank Page
**Possible Causes:**
- PHP syntax error (unlikely - script is tested)
- PHP execution disabled
- Insufficient memory

**Solution:**
```bash
# Check error log
tail -f /path/to/error.log

# Or enable error display temporarily
php -d display_errors=1 check_setup.php
```

### Script Shows PHP Code Instead of Running
**Cause**: PHP not configured to handle .php files

**Solution:**
- Verify file has .php extension (not .php.txt)
- Contact hosting provider to ensure PHP is configured

### Can't Access Via Web Browser
**Possible Causes:**
- Wrong URL
- File not uploaded
- Permissions incorrect

**Solution:**
1. Verify file exists: `ls -la check_setup.php`
2. Check permissions: Should be 644 or 755
3. Verify URL matches file location

## Support

For issues with TaskManager or deployment:
1. Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions
2. Check [README.md](README.md) for API documentation
3. Review your hosting provider's documentation for PHP/MySQL configuration
4. Contact your hosting provider for server-specific issues

## Related Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Full deployment instructions
- [QUICK_START_DEPLOY.md](QUICK_START_DEPLOY.md) - Quick reference for deployment
- [README.md](README.md) - TaskManager overview and API documentation

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-07  
**Maintained By**: Worker08 - DevOps & Deployment Specialist
