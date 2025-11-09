# TaskManager Deployment Quick Reference

## 🚀 Fast Track Deployment

### Step 0: Check Environment (IMPORTANT!)
Before deployment, verify your environment:
```bash
# Upload check_setup.php to server, then:
php check_setup.php
# Or visit: https://yourdomain.com/path/check_setup.php
```
**Only proceed if all critical checks pass!**

### Prerequisites Check
```bash
✓ PHP 8.0+
✓ MySQL 5.7+
✓ Apache mod_rewrite
✓ cURL extension
✓ Write permissions
```

### 3 Steps to Deploy

#### Step 1: Change Password
Edit `deploy.php`:
```php
define('ADMIN_PASSWORD', 'YourSecurePassword123!');
```

#### Step 2: Upload & Run
- Upload `deploy.php` to server
- Visit: `https://yourdomain.com/path/deploy.php`
- Or CLI: `php deploy.php`

#### Step 3: Configure & Deploy
Enter in the form:
- Admin password
- Database host (usually `localhost`)
- Database name
- Database username
- Database password

Click **Deploy TaskManager** → Done! ✓

### Post-Deployment
```bash
# Test API
curl https://yourdomain.com/path/api/health

# View API documentation (open in browser)
# https://yourdomain.com/path/api/docs/
```

**Production Example:**
- Health: `https://api.prismq.nomoos.cz/api/health`
- Swagger: `https://api.prismq.nomoos.cz/api/docs/`

## 📁 What Gets Created

```
TaskManager/
├── api/                 # REST API endpoints
├── config/              # Configuration files
│   └── config.php       # Generated with your DB creds
└── database/            # Database files
```

## 🔗 Quick Links

- **Detailed Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **API Docs**: [README.md](README.md)
- **Source**: https://github.com/Nomoos/PrismQ.Client

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Authentication failed" | Check password in deploy.php matches entry |
| "PHP version too old" | Upgrade PHP via hosting control panel |
| "Database connection failed" | Verify database credentials & MySQL running |
| "Failed to download files" | Check internet connectivity & GitHub access |
| "Permission denied" | Run `chmod 755` on directory |

## ⚠️ Security Checklist

- [ ] Changed ADMIN_PASSWORD in deploy.php
- [ ] Using HTTPS (SSL enabled)
- [ ] config.php has 640 permissions
- [ ] Reviewed database user permissions

## 📋 Common Shared Hosting Settings

### cPanel
- Database Host: `localhost`
- Create via: MySQL Databases → Create New Database
- Grant user via: Add User to Database

### Plesk
- Database Host: `localhost`
- Create via: Databases → Add Database
- User created automatically

### DirectAdmin
- Database Host: `localhost`
- Create via: MySQL Management → Create New

## 🎯 What the Script Does

1. ✓ Authenticates with admin password
2. ✓ Validates PHP version & extensions
3. ✓ Downloads 33 files from GitHub (API, database, Swagger UI)
4. ✓ Creates database & tables
5. ✓ Generates config.php
6. ✓ Sets secure permissions
7. ✓ Validates installation

**Total time: ~30 seconds**

## 📞 Need Help?

See full documentation: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
