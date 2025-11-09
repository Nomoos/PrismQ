# Changelog

All notable changes to Frontend/TaskManager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- [List new features that are in development but not yet released]

### Changed
- [List changes to existing functionality]

### Deprecated
- [List features that will be removed in upcoming releases]

### Removed
- [List removed features]

### Fixed
- [List bug fixes]

### Security
- [List security improvements or fixes]

---

## [0.1.0] - 2025-11-09

### Added
- Initial release of Frontend/TaskManager
- Task List view with filtering (All, Pending, Claimed, Completed, Failed)
- Task Detail view with claim and complete functionality
- Worker Dashboard for worker management
- Settings page for API and worker configuration
- Mobile-first responsive design optimized for Redmi 24115RA8EG
- Bottom navigation for mobile devices
- Pull-to-refresh support on task list
- Real-time task status updates
- Task progress tracking (0-100%)
- Error handling and retry mechanisms
- LocalStorage for persisting worker ID and settings
- Environment-based configuration via .env files
- Deployment wizard (deploy.php and deploy-auto.php)
- Comprehensive documentation suite:
  - User Guide
  - Developer Guide
  - Deployment Guide
  - API Integration Guide
  - Component Library Reference
  - Contributing Guide
  - Performance Guide
  - Troubleshooting Guide
  - Browser Support Guide

### Technical Stack
- Vue 3.4+ with Composition API
- TypeScript for type safety
- Tailwind CSS for styling
- Pinia for state management
- Vue Router for navigation
- Axios for HTTP requests
- Vite for build tooling
- Vitest for unit testing
- Playwright for E2E testing

### Performance
- Bundle size: ~180KB (gzipped)
- First Contentful Paint: < 2s
- Time to Interactive: < 2.5s
- Lighthouse score: 85+ (Performance)

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Chrome Mobile (Android)
- Safari Mobile (iOS 14+)

---

## Changelog Format Guide

> **Instructions for maintaining this changelog**

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.X.0): New features, backwards-compatible
- **PATCH** (0.0.X): Bug fixes, backwards-compatible

### Categories

Use these categories in order (omit empty sections):

1. **Added**: New features
2. **Changed**: Changes to existing functionality
3. **Deprecated**: Features that will be removed soon
4. **Removed**: Removed features
5. **Fixed**: Bug fixes
6. **Security**: Security improvements or vulnerability fixes

### Writing Guidelines

#### Be Specific and Clear

❌ Bad:
```markdown
- Fixed bugs
- Improved performance
- Updated dependencies
```

✅ Good:
```markdown
- Fixed task claiming race condition causing duplicate claims (#42)
- Improved task list rendering performance by 40% through virtualization
- Updated axios from 1.6.0 to 1.6.2 for security patch (CVE-2024-xxxxx)
```

#### Use Present Tense

✅ Correct: "Add feature", "Fix bug", "Change behavior"  
❌ Incorrect: "Added feature", "Fixed bug", "Changed behavior"

#### Include Issue References

When applicable, reference issue numbers:
```markdown
- Fix memory leak in task polling component (#38)
- Add WebSocket support for real-time updates (#45)
```

#### Link to Pull Requests

For transparency, link to PRs:
```markdown
- Add dark mode toggle ([#52](https://github.com/org/repo/pull/52))
```

### Entry Examples

#### Added (New Features)

```markdown
### Added
- Add real-time task updates via WebSocket connection
- Add dark mode toggle in settings
- Add keyboard shortcuts for task navigation (Ctrl+N for next, Ctrl+P for previous)
- Add task export functionality to CSV/JSON formats
- Add offline mode with service worker caching
```

#### Changed (Modifications)

```markdown
### Changed
- Update task card design with improved status indicators
- Change API polling interval from 5s to 10s to reduce server load
- Improve mobile navigation with larger touch targets (48px minimum)
- Refactor task store to use more efficient state updates
```

#### Deprecated (Will be Removed)

```markdown
### Deprecated
- Deprecate `TaskService.legacyClaimTask()` - use `TaskService.claimTask()` instead
- Deprecate environment variable `VITE_OLD_API_URL` - use `VITE_API_BASE_URL`
- Legacy task status format will be removed in v2.0.0
```

#### Removed (Breaking Changes)

```markdown
### Removed
- **BREAKING**: Remove support for Internet Explorer 11
- **BREAKING**: Remove deprecated `useOldTaskStore` composable
- Remove unused polyfills reducing bundle size by 20KB
- Remove legacy deployment scripts (deploy-v1.php)
```

#### Fixed (Bug Fixes)

```markdown
### Fixed
- Fix task claiming race condition causing duplicate claims (#42)
- Fix incorrect timestamp display in Safari (#38)
- Fix memory leak in task polling component (#37)
- Fix scroll position not persisting after navigation
- Fix bottom navigation overlap on iOS Safari
- Fix API error messages not displaying correctly
```

#### Security (Security Fixes)

```markdown
### Security
- Fix XSS vulnerability in task description rendering (CVE-2024-xxxxx)
- Update axios dependency to patch security issue (CVE-2024-yyyyy)
- Add Content Security Policy headers
- Implement rate limiting on API requests
- Add input sanitization for worker ID field
```

---

## Version Entry Template

Copy this template when adding a new version:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- [New feature 1]
- [New feature 2]

### Changed
- [Change 1]
- [Change 2]

### Deprecated
- [Deprecated feature 1]

### Removed
- [Removed feature 1]

### Fixed
- [Bug fix 1] (#issue-number)
- [Bug fix 2] (#issue-number)

### Security
- [Security fix 1]
```

---

## Release Process Checklist

When preparing a release:

- [ ] Update version in `package.json`
- [ ] Update `[Unreleased]` section to new version number
- [ ] Add release date (YYYY-MM-DD format)
- [ ] Create new `[Unreleased]` section at top
- [ ] Update version comparison links at bottom
- [ ] Review all entries for clarity and completeness
- [ ] Commit changelog: `git commit -m "docs: update changelog for vX.Y.Z"`
- [ ] Tag release: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Push changes and tags: `git push && git push --tags`
- [ ] Create GitHub release with notes from changelog
- [ ] Update release notes using RELEASE_NOTES_TEMPLATE.md

---

## Comparison Links

> **Note**: Add comparison links when you have multiple released versions

[Unreleased]: https://github.com/Nomoos/PrismQ.Client/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Nomoos/PrismQ.Client/releases/tag/v0.1.0

---

**Maintained by**: Documentation Team (Worker06)  
**Format**: [Keep a Changelog](https://keepachangelog.com/)  
**Versioning**: [Semantic Versioning](https://semver.org/)  
**Last Updated**: 2025-11-09
