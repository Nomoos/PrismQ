# Release Management Quick Reference

Quick commands and procedures for Worker01 release coordination.

## Quick Commands

### Check if Ready for Release
```bash
./_meta/_scripts/check-release-readiness.sh
```

### Sync All Versions
```bash
# Use VERSION file as source
./_meta/_scripts/sync-versions.sh

# Or specify version
./_meta/_scripts/sync-versions.sh 1.0.0
```

### Prepare Release
```bash
# Creates commit and tag
./_meta/_scripts/prepare-release.sh 1.0.0

# Push changes
git push origin main
git push origin v1.0.0
```

## Release Workflow

### 1. Pre-Release (Before creating tag)
```bash
# Install dependencies
cd Frontend && npm install && cd ..

# Run all checks
./_meta/_scripts/check-release-readiness.sh

# Fix any errors found
# Re-run until all checks pass
```

### 2. Version Update
```bash
# Update versions everywhere
./_meta/_scripts/sync-versions.sh 1.0.0

# Update CHANGELOG.md manually
nano CHANGELOG.md
```

### 3. Create Release
```bash
# Prepare (creates commit + tag)
./_meta/_scripts/prepare-release.sh 1.0.0

# Review changes
git show HEAD
git show v1.0.0

# Push to repository
git push origin main
git push origin v1.0.0
```

### 4. GitHub Release (Manual)
1. Go to: https://github.com/Nomoos/PrismQ.Client/releases
2. Click "Draft a new release"
3. Choose tag: v1.0.0
4. Use RELEASE_NOTES_TEMPLATE.md for content
5. Publish release

### 5. Deploy to Production
```bash
# Follow deployment checklist
cat DEPLOYMENT_CHECKLIST.md

# Build frontend
cd Frontend
npm ci
npm run build

# Deploy dist/ folder to web server
```

### 6. Post-Release Monitoring
- Check error logs for 24-48 hours
- Monitor performance metrics
- Track user feedback
- Document any issues

## Common Tasks

### Check Current Version
```bash
cat VERSION
grep version Frontend/package.json
```

### Update Documentation
```bash
# Update CHANGELOG.md
nano CHANGELOG.md

# Update release notes
nano RELEASE_NOTES_TEMPLATE.md
```

### Test Build Locally
```bash
cd Frontend
npm install
npm test
npm run lint
npm run build
cd ..
```

### Rollback to Previous Version
```bash
# Find previous version
git tag -l "v*" --sort=-v:refname | head -n 2

# Checkout previous version
git checkout v0.9.0

# Rebuild and deploy
cd Frontend && npm run build
# Deploy dist/ folder
```

## Release Types

### Development Release (0.x.x)
```bash
./_meta/_scripts/prepare-release.sh 0.2.0
git push origin main && git push origin v0.2.0
```

### Beta Release (x.x.x-beta.x)
```bash
./_meta/_scripts/prepare-release.sh 1.0.0-beta.1
git push origin main && git push origin v1.0.0-beta.1
# Mark as "pre-release" on GitHub
```

### Production Release (1.0.0+)
```bash
./_meta/_scripts/prepare-release.sh 1.0.0
git push origin main && git push origin v1.0.0
# Full deployment checklist required
```

### Hotfix (x.x.1+)
```bash
# Create hotfix branch
git checkout -b hotfix/critical-fix main

# Make fix and test
# ...

# Bump patch version
./_meta/_scripts/prepare-release.sh 1.0.1

# Merge and deploy
git checkout main
git merge hotfix/critical-fix
git push origin main && git push origin v1.0.1
```

## Troubleshooting

### Script Won't Run
```bash
# Make executable
chmod +x _meta/_scripts/*.sh
```

### Version Mismatch
```bash
# Sync all versions to match VERSION file
./_meta/_scripts/sync-versions.sh
```

### Tests Fail
```bash
# Install dependencies
cd Frontend && npm install && cd ..

# Run tests manually
cd Frontend && npm test
```

### Build Fails
```bash
# Clear and reinstall
cd Frontend
rm -rf node_modules
npm install
npm run build
```

### Tag Already Exists
```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0

# Recreate
./_meta/_scripts/prepare-release.sh 1.0.0
```

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| VERSION | `/VERSION` | Source of truth for version |
| CHANGELOG | `/CHANGELOG.md` | Version history |
| Release Guide | `/RELEASE.md` | Full release documentation |
| Deployment Checklist | `/DEPLOYMENT_CHECKLIST.md` | Production deployment |
| Release Notes Template | `/RELEASE_NOTES_TEMPLATE.md` | GitHub release template |
| Scripts | `/_meta/_scripts/` | Automation scripts |

## Documentation Links

- [Full Release Guide](./RELEASE.md)
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)
- [Changelog](./CHANGELOG.md)
- [Worker01 Phase 4](./Backend/TaskManager/_meta/issues/new/Worker01/PHASE4_RELEASE_MANAGEMENT.md)

## Version Numbers

Current: **0.1.0**

Next releases:
- Development: 0.2.0, 0.3.0, etc.
- Beta: 1.0.0-beta.1, 1.0.0-beta.2, etc.
- RC: 1.0.0-rc.1, 1.0.0-rc.2, etc.
- Production: 1.0.0

---

**Quick Reference Version**: 1.0  
**Last Updated**: 2024-11-09  
**Maintained By**: Worker01
