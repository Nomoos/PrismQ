# Release Management Guide

## Overview

This guide outlines the release management process for PrismQ Client, coordinated by Worker01 (Project Manager) as part of Phase 4 production deployment responsibilities.

## Version Management

### Versioning Scheme

PrismQ Client follows [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE]

Examples:
- 0.1.0 - Initial development release
- 1.0.0 - First production release
- 1.1.0 - New features (minor)
- 1.0.1 - Bug fixes (patch)
- 2.0.0-beta.1 - Major version pre-release
```

### Version Files

- **`/VERSION`**: Project version (source of truth)
- **`Frontend/package.json`**: Frontend version (should match `/VERSION`)
- **`Backend/TaskManager/composer.json`**: TaskManager version (should match `/VERSION`)

## Release Process

### 1. Pre-Release Preparation

Before creating a release, ensure:

```bash
# 1. All tests pass locally
cd Frontend && npm test
cd ../Backend/TaskManager && php tests/test.php

# 2. Code is linted
cd Frontend && npm run lint

# 3. Build succeeds
cd Frontend && npm run build

# 4. All documentation is up to date
# Check README.md, API docs, etc.
```

### 2. Version Update

Update version in all required files:

```bash
# Update VERSION file
echo "1.0.0" > VERSION

# Update Frontend package.json
cd Frontend
npm version 1.0.0 --no-git-tag-version

# Update Backend composer.json
# Edit Backend/TaskManager/composer.json manually
# Set "version": "1.0.0"
```

### 3. Create Release Commit

```bash
git add VERSION Frontend/package.json Backend/TaskManager/composer.json
git commit -m "chore: bump version to 1.0.0"
git push origin main
```

### 4. Create Git Tag

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag to trigger release workflow
git push origin v1.0.0
```

### 5. Create GitHub Release Manually

After pushing the tag, create a GitHub Release manually:

1. Go to GitHub repository → Releases → "Draft a new release"
2. Choose the tag you just pushed (e.g., `v1.0.0`)
3. Fill in release title: "Release 1.0.0"
4. Generate release notes or write manually (see template below)
5. Mark as pre-release if applicable (e.g., beta versions)
6. Publish release

**Release Notes Template:**
```markdown
# Release 1.0.0

## Changes
- Feature: Description of new feature
- Fix: Bug fix description
- Docs: Documentation updates

## Components
- **Frontend**: Vue 3 web interface
- **Backend TaskManager**: PHP task queue system with data-driven API

## Installation
See [README.md](README.md) for installation instructions.

## Documentation
- [Setup Guide](_meta/docs/SETUP.md)
- [User Guide](_meta/docs/USER_GUIDE.md)
- [API Reference](Backend/TaskManager/_meta/docs/API_REFERENCE.md)
```

### 6. Post-Release Verification

After release is created:

1. **Verify GitHub Release**: Check the release page on GitHub
2. **Test Installation**: Clone a fresh copy and verify installation works
3. **Update Documentation**: Ensure all links point to correct version
4. **Announce Release**: Update relevant channels/documentation

## Testing and Validation

### Manual Testing Process

Before creating a release, run all tests and validations manually:

**Frontend Testing:**
```bash
cd Frontend
npm run lint          # Lint code
npm test             # Run unit tests
npm run build        # Verify build works
```

**Backend Testing:**
```bash
cd Backend/TaskManager
composer validate    # Validate composer.json
php tests/test.php   # Run tests (if available)
```

**Integration Testing:**
```bash
# Use the release readiness script
./_meta/_scripts/check-release-readiness.sh
```

### Quality Checklist

Before each release:
- [ ] All tests pass locally
- [ ] Code is linted and formatted
- [ ] Build succeeds without errors
- [ ] Documentation is up to date
- [ ] No known critical bugs
- [ ] Version numbers are consistent

## Release Types

### Development Releases (0.x.x)

- For internal testing
- Breaking changes allowed
- No API stability guarantees

### Beta/RC Releases (x.x.x-beta.x, x.x.x-rc.x)

```bash
# Create beta release
echo "1.0.0-beta.1" > VERSION
git tag v1.0.0-beta.1
git push origin v1.0.0-beta.1
```

- Feature complete but needs testing
- Marked as pre-release on GitHub
- Community testing encouraged

### Production Releases (1.0.0+)

```bash
# Create production release
echo "1.0.0" > VERSION
git tag v1.0.0
git push origin v1.0.0
```

- Stable and production-ready
- Semantic versioning enforced
- Full documentation required

## Hotfix Process

For critical production issues:

```bash
# 1. Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-fix

# 2. Make fix and test
# ... make changes ...
npm test

# 3. Bump patch version
echo "1.0.1" > VERSION

# 4. Create PR and merge to main
git add .
git commit -m "fix: critical security issue"
git push origin hotfix/critical-fix

# 5. After merge, tag and release
git checkout main
git pull
git tag v1.0.1
git push origin v1.0.1
```

## Rollback Procedures

### Immediate Rollback (< 1 hour)

If critical issues detected immediately after release:

1. **Stop New Deployments**: Alert team
2. **Revert to Previous Version**: Use previous release tag
3. **Document Issue**: Create incident report
4. **Plan Fix**: Schedule hotfix release

### Planned Rollback (> 1 hour)

If issues detected after deployment:

1. **Assess Impact**: Determine severity and scope
2. **Create Hotfix**: Follow hotfix process
3. **Test Thoroughly**: Ensure fix works
4. **Deploy Hotfix**: Create new patch release

### Rollback Commands

```bash
# Find previous release
git tag -l "v*" --sort=-v:refname | head -n 2

# Deploy previous version
git checkout v1.0.0
# Follow deployment procedures for this version
```

## Release Checklist

### Pre-Release

- [ ] All tests passing (Frontend + Backend)
- [ ] No open critical/high priority issues
- [ ] Documentation updated
- [ ] CHANGELOG reviewed
- [ ] Version numbers updated consistently
- [ ] Breaking changes documented (if any)
- [ ] Migration guide prepared (if needed)

### Release

- [ ] Version commit created and pushed
- [ ] Git tag created and pushed
- [ ] GitHub Release automatically created
- [ ] Release notes reviewed and edited if needed
- [ ] Assets/artifacts uploaded (if any)

### Post-Release

- [ ] GitHub Release verified
- [ ] Installation tested from fresh clone
- [ ] Documentation links verified
- [ ] Known issues documented
- [ ] Community announcement (if applicable)
- [ ] Next milestone planned

## Monitoring & Metrics

### Post-Release Monitoring

Monitor for 24-48 hours after release:

- **Error Logs**: Watch for new error patterns
- **Performance**: Monitor response times
- **User Reports**: Track issue reports
- **Metrics**: API usage, task completion rates

### Success Criteria

A release is successful when:

- Zero critical bugs in first 48 hours
- Performance metrics stable or improved
- No rollback required
- Positive or neutral user feedback

## Automation Scripts

### Check Release Readiness

```bash
# Run from project root
./_meta/_scripts/check-release-readiness.sh
```

This script checks:
- All tests pass
- Version consistency
- Documentation up to date
- No uncommitted changes

### Prepare Release

```bash
# Run from project root
./_meta/_scripts/prepare-release.sh 1.0.0
```

This script:
- Updates version in all files
- Creates release commit
- Creates and pushes tag

## Troubleshooting

### Test Failures

**Problem**: Tests pass locally but fail in production

**Solution**: 
- Check Node.js version (should be 18+)
- Check PHP version (should be 8.0+)
- Verify all dependencies are installed
- Check for environment-specific issues

**Problem**: Build fails with version mismatch

**Solution**:
- Run `./_meta/_scripts/sync-versions.sh` to sync versions
- Clear node_modules and rebuild: `rm -rf node_modules && npm install`
- Clear composer cache: `composer clear-cache`

### Version Conflicts

**Problem**: Version mismatch between files

**Solution**:
```bash
# Check all versions
cat VERSION
grep version Frontend/package.json
grep version Backend/TaskManager/composer.json

# Update to consistent version
./_meta/_scripts/sync-versions.sh
```

## Worker01 Responsibilities

As Project Manager, Worker01 coordinates:

1. **Release Planning**: Schedule releases, coordinate team
2. **Version Management**: Ensure version consistency
3. **Release Execution**: Create and verify releases
4. **Documentation**: Maintain release notes and guides
5. **Communication**: Announce releases, coordinate deployment
6. **Monitoring**: Track post-release metrics and issues
7. **Continuous Improvement**: Refine release process based on feedback

## Related Documentation

- [Project Status Summary](Backend/TaskManager/_meta/PROJECT_STATUS_SUMMARY.md)
- [Testing Guide](_meta/docs/TESTING.md)
- [Setup Guide](_meta/docs/SETUP.md)

## Version History

| Version | Date | Type | Notes |
|---------|------|------|-------|
| 0.1.0 | 2024-11 | Development | Initial implementation |
| 1.0.0 | TBD | Production | First production release |

---

**Maintained by**: Worker01 (Project Manager)  
**Last Updated**: 2024-11-09  
**Status**: Active - Phase 4 Implementation
