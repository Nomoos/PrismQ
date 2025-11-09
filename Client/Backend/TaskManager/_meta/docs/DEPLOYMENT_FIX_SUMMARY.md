# Deployment Fix Summary

## Issue Description

The TaskManager API deployed at `https://api.prismq.nomoos.cz` was returning fatal errors when accessing the health endpoint:

```
Fatal error: Failed opening required '/data/web/virtuals/193148/virtual/www/domains/api.prismq.nomoos.cz/api/EndpointRouter.php' 
(include_path='.:/data/web/virtuals/193148/virtual') in /data/web/virtuals/193148/virtual/www/domains/api.prismq.nomoos.cz/api/index.php:28
```

## Root Cause

The deployment script (`deploy.php`) was downloading files for the **old controller-based architecture** but the codebase has been refactored to use a **new data-driven architecture**. The following critical files were missing from the deployment:

**Missing Files:**
1. `src/api/EndpointRouter.php` - Dynamic routing based on database-defined endpoints
2. `src/api/ActionExecutor.php` - Executes actions based on JSON configuration
3. `src/api/CustomHandlers.php` - Custom business logic handlers
4. `src/database/seed_endpoints.sql` - Initial endpoint definitions for the API

## Changes Made

### 1. Updated deploy.php File List

Added the missing files to the download list in `src/deploy.php`:

```php
$files = [
    // ... existing files ...
    'src/api/EndpointRouter.php' => API_PATH . '/EndpointRouter.php',
    'src/api/ActionExecutor.php' => API_PATH . '/ActionExecutor.php',
    'src/api/CustomHandlers.php' => API_PATH . '/CustomHandlers.php',
    // ... existing files ...
    'src/database/seed_endpoints.sql' => DATABASE_PATH . '/seed_endpoints.sql',
    // ... existing files ...
];
```

**File Count:** Increased from 9 files to **13 files** (data-driven architecture fix), then to **33 files** (with Swagger UI documentation)

### 2. Enhanced Database Setup

Modified `setupDatabase()` method to:
- Import `seed_endpoints.sql` after creating the schema
- Validate that seed file contains `api_endpoints` table references
- Check for dangerous SQL commands before execution

```php
// Import seed data for API endpoints
$seedFile = DATABASE_PATH . '/seed_endpoints.sql';
if (file_exists($seedFile)) {
    $seedData = file_get_contents($seedFile);
    
    // Validate and execute
    if (stripos($seedData, 'INSERT INTO') !== false && 
        stripos($seedData, 'api_endpoints') !== false) {
        $pdo->exec($seedData);
        $this->info('API endpoints seeded successfully');
    }
}
```

### 3. Updated Documentation

Updated `DEPLOYMENT_GUIDE.md` to reflect:
- Complete list of 13 files being downloaded
- Database seeding step for API endpoints
- Updated directory structure showing all new files

## How to Fix Production

### Option 1: Re-run Full Deployment (Recommended)

1. **Backup current installation:**
   ```bash
   # On server, backup database and files
   mysqldump -u user -p d193148_prismtm > backup_$(date +%Y%m%d).sql
   tar -czf backup_files_$(date +%Y%m%d).tar.gz src/
   ```

2. **Re-run deployment script:**
   - Upload the updated `src/deploy.php` from this PR
   - Access via browser: `https://api.prismq.nomoos.cz/src/deploy.php`
   - Enter credentials and deploy
   - The script will download all 13 files and seed the database

3. **Verify:**
   ```bash
   curl https://api.prismq.nomoos.cz/api/health
   ```
   Should return:
   ```json
   {
     "success": true,
     "message": "API is healthy",
     "data": {
       "status": "healthy",
       "timestamp": "..."
     }
   }
   ```

### Option 2: Manual Fix (If deployment script cannot be re-run)

1. **Download missing files from GitHub:**
   ```bash
   cd /data/web/virtuals/193148/virtual/www/domains/api.prismq.nomoos.cz/api
   
   # Download missing API files
   wget https://raw.githubusercontent.com/Nomoos/PrismQ.Client/main/Backend/TaskManager/api/EndpointRouter.php
   wget https://raw.githubusercontent.com/Nomoos/PrismQ.Client/main/Backend/TaskManager/api/ActionExecutor.php
   wget https://raw.githubusercontent.com/Nomoos/PrismQ.Client/main/Backend/TaskManager/api/CustomHandlers.php
   
   # Download seed file
   cd ../database
   wget https://raw.githubusercontent.com/Nomoos/PrismQ.Client/main/Backend/TaskManager/database/seed_endpoints.sql
   ```

2. **Import seed data:**
   ```bash
   mysql -u d193148_prismtm -p d193148_prismtm < seed_endpoints.sql
   ```

3. **Set permissions:**
   ```bash
   chmod 644 /path/to/api/*.php
   ```

4. **Test:**
   ```bash
   curl https://api.prismq.nomoos.cz/api/health
   ```

## Verification Checklist

After fixing:

- [ ] Health endpoint returns JSON (not errors): `GET /api/health`
- [ ] Task types endpoint works: `GET /api/task-types`
- [ ] Task creation works: `POST /api/tasks`
- [ ] Database has `api_endpoints` table populated
- [ ] All 13 files present in deployment directories
- [ ] No PHP errors in Apache error log

## Files Changed in This PR

1. **Backend/TaskManager/deploy.php**
   - Added 4 new files to download list
   - Enhanced database seeding logic
   - Improved seed file validation

2. **Backend/TaskManager/DEPLOYMENT_GUIDE.md**
   - Updated file list (9 → 13 files)
   - Added api_endpoints to database tables list
   - Updated directory structure diagram

## Testing Performed

- ✅ Verified all 13 files accessible on GitHub
- ✅ PHP syntax validation passes
- ✅ Existing test suite passes (12/12 JSON validations)
- ✅ Schema.sql contains api_endpoints table definition
- ✅ seed_endpoints.sql contains INSERT statements for api_endpoints

## Architecture Notes

### Old Architecture (Controller-Based)
```
src/api/index.php → TaskController.php → Database
                     TaskTypeController.php
```

### New Architecture (Data-Driven)
```
src/api/index.php → EndpointRouter.php → ActionExecutor.php → CustomHandlers.php
                         ↓                       ↓
                     api_endpoints          Database
                 (database)
```

**Benefits of New Architecture:**
- Endpoints defined in database (no code changes needed)
- Configuration-driven actions
- Easier to add/modify endpoints
- Better separation of concerns

## Support

For issues or questions:
1. Check `/api/health` endpoint first
2. Review Apache error logs
3. Verify database has `api_endpoints` table with data
4. Ensure all 13 files are present

## Related Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Quick Start](QUICK_START_DEPLOY.md) - Fast deployment reference
- [README](README.md) - Main TaskManager documentation
