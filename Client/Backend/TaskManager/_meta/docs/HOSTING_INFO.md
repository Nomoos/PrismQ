# Hosting Information - Vedos/Wedos

This document contains information about the Vedos/Wedos webhosting account where TaskManager is deployed or intended to be deployed.

## Account Information

| Field | Value |
|-------|-------|
| **Order Number** | 3218052549 |
| **Status** | Aktivní (Active) |
| **Ordered** | 16.05.2018 11:17:11 |
| **Provisioned** | 16.05.2018 11:33:17 |
| **Operating System** | Linux |

## Resource Allocation

| Resource | Current Usage | Notes |
|----------|--------------|-------|
| **Website Size** | 356 MB | Total web content storage |
| **Email Size** | 6 MB | Email storage allocation |
| **Database Size** | 7 MB | MySQL/MariaDB storage |
| **Total Used** | 369 MB | Combined storage across all services |

## Hosting Plan Details

| Field | Value |
|-------|-------|
| **Plan Variant** | NoLimit |
| **Expiration** | 16.05.2026 |
| **VAT Billing** | No (Účtování bez DPH: ne) |

## Deployment Considerations

### Resource Planning
- **Available Space**: Significant capacity remains (NoLimit plan)
- **Database Space**: 7 MB currently used, sufficient for TaskManager
- **Growth Headroom**: NoLimit plan provides flexibility for expansion

### TaskManager Deployment
- **Estimated TaskManager Size**: < 1 MB (API files + documentation)
- **Database Requirements**: Minimal (< 5 MB for active task queue)
- **Email Requirements**: Not applicable for TaskManager
- **Projected Total Impact**: < 10 MB additional usage

### Capacity Monitoring
- Regular monitoring recommended as task queue grows
- Database size will increase with task history
- Consider implementing task history cleanup if needed
- NoLimit plan provides buffer for growth

## Hosting Provider Details

**Provider**: Vedos (https://vedos.cz)  
**Product**: NoLimit Webhosting (https://vedos.cz/en/webhosting/nolimit/)  
**Hosting Type**: Shared Linux Hosting  
**Control Panel**: Vedos Control Panel with phpMyAdmin  
**Support**: Available through Vedos support channels

### Supported PHP Versions
- **PHP 5.4 - 5.6**: Available (outdated, not recommended)
- **PHP 7.0 - 7.4**: Available (deprecated, but still supported)
- **PHP 8.0 - 8.4**: Available (current and recommended for new applications)
- **Configuration**: PHP version can be selected during order and changed later via control panel
- **Advanced Settings**: Customizable php.ini parameters available through admin interface
- **Concurrent Threads**: Up to 25 concurrent PHP threads (NoLimit tariff)
- **Memory Limit**: 512 MB per script (NoLimit tariff)
- **File Upload Limit**: 256 MB (NoLimit tariff)
- **POST Request Limit**: 256 MB (NoLimit tariff)

### Database Support
- **Database System**: MariaDB (fully MySQL-compatible)
- **Number of Databases**: Unlimited MariaDB databases
- **Storage Capacity**: Up to 2 GB database storage (applies to NoLimit tariff as used in this project)
- **Management Tool**: phpMyAdmin (accessible from Vedos control panel)
- **User Accounts**: Each database includes:
  - **Admin user**: Full privileges (recommended only for phpMyAdmin administration)
  - **Web user**: Limited rights (intended for PHP application connections)
- **Remote Access**: Not supported (connections must originate from web server for security)
- **User Management**: Fixed predefined users; permissions cannot be changed (security feature)
- **CRON Support**: Available for periodic PHP script execution

**Note**: NoLimit Extra tariff provides 5 GB database storage, but this project uses the standard NoLimit tariff (2 GB limit).

## Renewal Information

- **Next Renewal**: 16.05.2026
- **Renewal Period**: Annual (based on 2018 order to 2026 expiration)
- **Action Required**: Renewal before 16.05.2026
- **Current Status**: Active (check expiration date above for time remaining)

## Security Notes

⚠️ **Important**: This document contains account information but should not contain credentials.

- Database credentials: Store in `config/config.php` (not version controlled)
- FTP/SFTP credentials: Keep secure, not in repository
- Control panel credentials: Maintain separately from code repository
- API keys (if any): Use environment variables or secure config files

## Deployment Checklist

When deploying to this hosting account:

- [ ] Verify sufficient database space (7 MB → will grow to ~10-15 MB within 2 GB limit)
- [ ] Select PHP version (PHP 8.0+ recommended, 8.0-8.4 available)
- [ ] Confirm MariaDB compatibility (MySQL-compatible, managed via phpMyAdmin)
- [ ] Use web user account (not admin) for PHP application database connections
- [ ] Verify Apache mod_rewrite availability
- [ ] Test FTP/SFTP access
- [ ] Backup existing data before deployment
- [ ] Configure database credentials in config.php (use web user, not admin user)
- [ ] Test API endpoints after deployment
- [ ] Monitor resource usage post-deployment (512 MB memory limit, 25 concurrent threads)
- [ ] Set up CRON jobs if needed for periodic tasks

## Related Documentation

- [Deployment Guide](DEPLOYMENT.md) - Step-by-step deployment instructions
- [API Reference](API_REFERENCE.md) - API documentation
- [TaskManager README](../README.md) - System overview

## Update History

| Date | Update | Notes |
|------|--------|-------|
| 07.11.2025 | Initial documentation | Documented hosting account details from order information |
| 07.11.2025 | Added provider and product details | Updated to include Vedos NoLimit webhosting specifications, supported PHP versions (5.4-8.4), and MariaDB database details |

---

**Note**: Keep this information updated as hosting details change or when the account is renewed.
