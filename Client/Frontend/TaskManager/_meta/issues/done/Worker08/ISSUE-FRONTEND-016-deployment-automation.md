# ISSUE-FRONTEND-016: Deployment Automation and Staging Setup

## Status
🔴 **NOT STARTED** (0% Complete)

## Worker Assignment
**Worker08**: DevOps & Deployment Specialist

## Component
Frontend/TaskManager - Deployment / Infrastructure

## Type
Infrastructure / Deployment / DevOps

## Priority
🟡 HIGH

## Description
Setup and test deployment automation for staging and production environments on Vedos, including deployment scripts, health checks, and rollback procedures.

## Problem Statement
The Frontend/TaskManager application has deployment scripts (`deploy.php`, `deploy-deploy.php`) but they haven't been tested in a real environment. Before production deployment, we need to:
- Test deployment scripts on staging environment
- Verify .htaccess configuration for SPA routing
- Setup staging environment on Vedos
- Validate environment variable configuration
- Test health check endpoints
- Verify rollback procedures
- Create deployment runbook and checklist

Without tested deployment automation, production deployment is risky and manual.

## Solution
Implement and test comprehensive deployment automation:
1. **Staging Environment**: Setup staging on Vedos
2. **Deployment Testing**: Test deploy.php and deploy-deploy.php scripts
3. **SPA Routing**: Verify .htaccess configuration
4. **Environment Config**: Validate environment variables
5. **Health Checks**: Implement and test health check endpoint
6. **Rollback Procedures**: Test deployment rollback
7. **Documentation**: Create deployment runbook

## Acceptance Criteria
- [ ] Staging environment setup on Vedos
  - [ ] Staging URL configured
  - [ ] SSL certificate installed
  - [ ] Apache configured
  - [ ] Environment variables set
- [ ] Deployment scripts tested
  - [ ] deploy-deploy.php wizard tested
  - [ ] deploy.php script tested
  - [ ] Automated build and upload working
  - [ ] File permissions correct
  - [ ] Deployment logs available
- [ ] .htaccess SPA routing verified
  - [ ] Direct URL navigation works
  - [ ] Client-side routing works
  - [ ] 404 handling correct
  - [ ] API proxy working (if needed)
- [ ] Environment configuration validated
  - [ ] VITE_API_BASE_URL correct
  - [ ] VITE_SENTRY_DSN configured
  - [ ] Environment-specific settings applied
  - [ ] Secrets management working
- [ ] Health check endpoint implemented
  - [ ] /health endpoint responds
  - [ ] Version information included
  - [ ] Build timestamp included
  - [ ] API connectivity check
- [ ] Rollback procedures tested
  - [ ] Previous version backup exists
  - [ ] Rollback script working
  - [ ] Quick rollback process documented
  - [ ] Zero-downtime rollback possible
- [ ] Deployment documentation complete
  - [ ] Deployment runbook created
  - [ ] Production deployment checklist
  - [ ] Troubleshooting guide
  - [ ] Emergency procedures documented

## Implementation Details

### .htaccess for SPA Routing
```apache
# Frontend/TaskManager/dist/.htaccess
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /

  # Serve existing files/directories directly
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  
  # Route everything else to index.html (SPA)
  RewriteRule . /index.html [L]
</IfModule>

# Enable gzip compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Browser caching
<IfModule mod_expires.c>
  ExpiresActive On
  
  # HTML (no caching)
  ExpiresByType text/html "access plus 0 seconds"
  
  # CSS and JavaScript (1 year)
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  
  # Images (1 month)
  ExpiresByType image/jpeg "access plus 1 month"
  ExpiresByType image/png "access plus 1 month"
  ExpiresByType image/svg+xml "access plus 1 month"
</IfModule>

# Security headers
<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set X-Frame-Options "DENY"
  Header set X-XSS-Protection "1; mode=block"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
```

### Health Check Endpoint
```typescript
// src/api/health.ts
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy'
  version: string
  buildTime: string
  apiConnectivity: boolean
  timestamp: string
}

export const checkHealth = async (): Promise<HealthStatus> => {
  const apiHealthy = await checkApiConnectivity()
  
  return {
    status: apiHealthy ? 'healthy' : 'degraded',
    version: import.meta.env.VITE_APP_VERSION || 'unknown',
    buildTime: import.meta.env.VITE_BUILD_TIME || 'unknown',
    apiConnectivity: apiHealthy,
    timestamp: new Date().toISOString(),
  }
}

const checkApiConnectivity = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    })
    return response.ok
  } catch {
    return false
  }
}
```

```vue
<!-- src/views/Health.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { checkHealth, type HealthStatus } from '@/api/health'

const health = ref<HealthStatus | null>(null)

onMounted(async () => {
  health.value = await checkHealth()
})
</script>

<template>
  <div class="health">
    <h1>Health Check</h1>
    <div v-if="health">
      <div :class="['status', health.status]">
        Status: {{ health.status }}
      </div>
      <div>Version: {{ health.version }}</div>
      <div>Build Time: {{ health.buildTime }}</div>
      <div>API: {{ health.apiConnectivity ? '✅ Connected' : '❌ Disconnected' }}</div>
      <div>Timestamp: {{ health.timestamp }}</div>
    </div>
  </div>
</template>
```

### Deployment Script Enhancement
```php
<?php
// deploy.php enhancements
class FrontendDeployer {
    private $config;
    private $logger;
    
    public function __construct() {
        $this->config = $this->loadConfig();
        $this->logger = new DeploymentLogger();
    }
    
    public function deploy() {
        try {
            $this->logger->info('Starting deployment...');
            
            // 1. Backup current version
            $this->backupCurrentVersion();
            
            // 2. Upload new files
            $this->uploadFiles();
            
            // 3. Run health check
            if (!$this->healthCheck()) {
                throw new Exception('Health check failed');
            }
            
            // 4. Switch to new version
            $this->activateNewVersion();
            
            // 5. Final verification
            if (!$this->verify()) {
                $this->rollback();
                throw new Exception('Verification failed, rolled back');
            }
            
            $this->logger->info('Deployment successful');
            return true;
            
        } catch (Exception $e) {
            $this->logger->error('Deployment failed: ' . $e->getMessage());
            $this->rollback();
            return false;
        }
    }
    
    private function backupCurrentVersion() {
        $timestamp = date('Y-m-d_H-i-s');
        $backupDir = "backups/frontend_$timestamp";
        
        if (is_dir('dist')) {
            exec("cp -r dist $backupDir");
            $this->logger->info("Backup created: $backupDir");
        }
    }
    
    private function healthCheck() {
        $healthUrl = $this->config['app_url'] . '/health';
        $response = file_get_contents($healthUrl);
        $health = json_decode($response, true);
        
        return $health && $health['status'] !== 'unhealthy';
    }
    
    private function rollback() {
        $this->logger->warning('Rolling back deployment...');
        
        // Find latest backup
        $backups = glob('backups/frontend_*');
        if (empty($backups)) {
            $this->logger->error('No backup found for rollback');
            return;
        }
        
        rsort($backups);
        $latestBackup = $backups[0];
        
        // Restore backup
        exec("rm -rf dist");
        exec("cp -r $latestBackup dist");
        
        $this->logger->info('Rollback completed');
    }
}
?>
```

### Deployment Runbook
```markdown
# Frontend Deployment Runbook

## Pre-Deployment Checklist
- [ ] All tests passing (>80% coverage)
- [ ] Worker10 final approval received
- [ ] Build succeeds locally
- [ ] Staging deployment tested
- [ ] Health check working
- [ ] Rollback procedure tested
- [ ] Team notified of deployment

## Deployment Steps

### 1. Build Production Assets
```bash
cd Frontend/TaskManager
npm run build
```

### 2. Run Pre-Deployment Tests
```bash
# Verify build output
ls -lh dist/
du -sh dist/

# Check bundle size (<500KB)
ls -lh dist/assets/*.js

# Run health check locally
npm run preview
curl http://localhost:4173/health
```

### 3. Upload to Staging
```bash
# Upload via deployment wizard
php deploy-deploy.php

# Or direct upload
php deploy.php --env=staging
```

### 4. Verify Staging
- [ ] Visit staging URL
- [ ] Test critical paths
  - [ ] View tasks
  - [ ] Claim task
  - [ ] Complete task
  - [ ] Settings
- [ ] Check health endpoint
- [ ] Verify API connectivity
- [ ] Test on mobile device

### 5. Deploy to Production
```bash
# Deploy to production
php deploy.php --env=production

# Monitor deployment
tail -f logs/deployment.log
```

### 6. Post-Deployment Verification
- [ ] Visit production URL
- [ ] Health check passing
- [ ] Sentry receiving events
- [ ] Performance metrics normal
- [ ] No error spikes

## Rollback Procedure

### Quick Rollback (if needed)
```bash
# Automatic rollback
php deploy.php --rollback

# Manual rollback
cd backups
ls -lt frontend_*
cp -r frontend_YYYY-MM-DD_HH-mm-ss ../dist
```

### Rollback Verification
- [ ] Health check passing
- [ ] Application functional
- [ ] No errors in logs
- [ ] Team notified

## Troubleshooting

### Issue: 404 on direct URL access
**Solution**: Check .htaccess configuration, ensure mod_rewrite enabled

### Issue: API not connecting
**Solution**: Verify VITE_API_BASE_URL, check CORS, verify network

### Issue: Blank page
**Solution**: Check console for errors, verify assets loaded, check base URL

### Issue: Health check failing
**Solution**: Check API connectivity, verify backend health, check logs
```

## Dependencies
**Requires**: 
- Worker03: Build artifacts (✅ Complete)
- Worker04: Performance optimization (🟡 In Progress)
- Vedos server access
- Staging environment

**Blocks**:
- Production deployment
- ISSUE-FRONTEND-017: Production Readiness Coordination

## Enables
- Automated staging deployments
- Tested production deployment process
- Quick rollback capability
- Deployment confidence

## Related Issues
- ISSUE-FRONTEND-005: Performance Optimization (dependency)
- ISSUE-FRONTEND-017: Production Readiness (blocked)

## Files Modified
- `Frontend/TaskManager/deploy.php` (enhance)
- `Frontend/TaskManager/deploy-deploy.php` (test)
- `Frontend/TaskManager/dist/.htaccess` (create)
- `Frontend/TaskManager/src/api/health.ts` (new)
- `Frontend/TaskManager/src/views/Health.vue` (new)
- `Frontend/TaskManager/docs/DEPLOYMENT_RUNBOOK.md` (new)
- `Frontend/TaskManager/docs/ROLLBACK_PROCEDURES.md` (new)

## Testing
**Test Strategy**:
- [ ] Staging deployment test
- [ ] Health check test
- [ ] Rollback procedure test
- [ ] SPA routing test
- [ ] Production dry-run

**Test Results**:
- **Staging Deployment**: Pending
- **Health Check**: Pending
- **Rollback**: Pending
- **SPA Routing**: Pending

## Parallel Work
**Can run in parallel with**:
- ISSUE-FRONTEND-011: Performance Testing (Worker04)
- ISSUE-FRONTEND-012: Comprehensive Testing (Worker07)
- ISSUE-FRONTEND-013: Accessibility Compliance (Worker03/Worker12)
- ISSUE-FRONTEND-014: Input Validation (Worker03)
- ISSUE-FRONTEND-015: Error Handling (Worker03/Worker08)

## Timeline
**Estimated Duration**: 2-3 days
**Target Start**: 2025-11-10
**Target Completion**: 2025-11-13

## Notes
- Deployment scripts exist but need testing
- Staging environment critical for validation
- Zero-downtime deployment preferred
- Rollback must be quick (<5 minutes)

## Security Considerations
- Secure deployment credentials
- Validate file permissions
- Enable security headers in .htaccess
- Test SSL certificate

## Performance Impact
- Deployment should complete in <10 minutes
- Rollback should complete in <5 minutes
- Zero downtime preferred

## Breaking Changes
None (deployment infrastructure only)

## Critical Success Metrics
- **Staging Deployment**: Working and tested
- **Health Check**: Passing in staging
- **Rollback**: Tested and documented
- **Production Ready**: Deployment process validated

---

**Created**: 2025-11-10
**Status**: 🔴 NOT STARTED (HIGH)
**Priority**: HIGH (Deployment readiness)
**Target**: 2-3 days to completion
**Dependency**: Worker04 performance optimization
