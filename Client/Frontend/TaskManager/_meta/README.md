# Frontend/TaskManager - _meta Directory

**Purpose**: This directory contains all project metadata, documentation, examples, scripts, and artifacts that are NOT part of the production deployment.

**Last Updated**: 2025-11-11  
**Status**: ✅ Organized following SOLID principles

---

## 📋 Directory Structure

```
_meta/
├── README.md                    # This file - _meta navigation guide
├── ORGANIZATION_REVIEW.md       # Detailed organization review
├── baselines/                   # Performance baselines and history
├── docs/                        # All project documentation (30+ files)
├── examples/                    # Code examples and templates
├── issues/                      # Issue tracking and project management
└── scripts/                     # Development and testing scripts
```

---

## 📚 Documentation (`docs/`)

### Project Status & Planning
- **[NEXT_STEPS.md](./docs/NEXT_STEPS.md)** - Current status, roadmap, and action items
- **[CZECH_SUMMARY.md](./docs/CZECH_SUMMARY.md)** - Czech language project summary
- **[PARALLELIZATION_MATRIX.md](./docs/PARALLELIZATION_MATRIX.md)** - Worker coordination strategy

### Getting Started
- **[REQUIREMENTS.md](./docs/REQUIREMENTS.md)** - System and browser requirements
- **[QUICK_START.md](./docs/QUICK_START.md)** - Installation and setup guide
- **[PROJECT_STRUCTURE.md](./docs/PROJECT_STRUCTURE.md)** - Directory organization
- **[TECHNOLOGY_STACK.md](./docs/TECHNOLOGY_STACK.md)** - Frameworks and tools

### Development Guides
- **[API_INTEGRATION.md](./docs/API_INTEGRATION.md)** - Backend API integration
- **[CODE_QUALITY_ANALYSIS.md](./docs/CODE_QUALITY_ANALYSIS.md)** - Code quality standards
- **[COMPONENT_EXTRACTION_SUMMARY.md](./docs/COMPONENT_EXTRACTION_SUMMARY.md)** - Component architecture
- **[COMPONENT_REFACTORING_SUMMARY.md](./docs/COMPONENT_REFACTORING_SUMMARY.md)** - Refactoring history

### Performance
- **[PERFORMANCE.md](./docs/PERFORMANCE.md)** - Performance guidelines
- **[PERFORMANCE_OPTIMIZATION_GUIDE.md](./docs/PERFORMANCE_OPTIMIZATION_GUIDE.md)** - Optimization techniques
- **[PERFORMANCE_RESULTS.md](./docs/PERFORMANCE_RESULTS.md)** - Test results
- **[PERFORMANCE_USAGE.md](./docs/PERFORMANCE_USAGE.md)** - Tool usage
- **[PERFORMANCE_EXAMPLES.md](./docs/PERFORMANCE_EXAMPLES.md)** - Examples

### Accessibility
- **[ACCESSIBILITY_GUIDE.md](./docs/ACCESSIBILITY_GUIDE.md)** - WCAG 2.1 AA compliance
- **[ACCESSIBILITY_IMPLEMENTATION_SUMMARY.md](./docs/ACCESSIBILITY_IMPLEMENTATION_SUMMARY.md)** - Implementation details
- **[ACCESSIBILITY_TESTING_REPORT.md](./docs/ACCESSIBILITY_TESTING_REPORT.md)** - Test results
- **[FINAL_ACCESSIBILITY_COMPLIANCE_REPORT.md](./docs/FINAL_ACCESSIBILITY_COMPLIANCE_REPORT.md)** - Final report
- **[KEYBOARD_NAVIGATION_GUIDE.md](./docs/KEYBOARD_NAVIGATION_GUIDE.md)** - Keyboard navigation

### Deployment
- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - Complete deployment guide
- **[DEPLOYMENT_RUNBOOK.md](./docs/DEPLOYMENT_RUNBOOK.md)** - Operational procedures
- **[DEPLOYMENT_SUMMARY.md](./docs/DEPLOYMENT_SUMMARY.md)** - Deployment history
- **[QUICK_DEPLOYMENT_REFERENCE.md](./docs/QUICK_DEPLOYMENT_REFERENCE.md)** - Quick reference
- **[ROLLBACK_PROCEDURES.md](./docs/ROLLBACK_PROCEDURES.md)** - Emergency rollback
- **[STAGING_DEPLOYMENT_CHECKLIST.md](./docs/STAGING_DEPLOYMENT_CHECKLIST.md)** - Staging checklist

### Testing
- **[TESTING.md](./docs/TESTING.md)** - Testing strategy
- **[TESTING_GUIDE.md](./docs/TESTING_GUIDE.md)** - Testing guidelines
- **[VALIDATION_TESTING.md](./docs/VALIDATION_TESTING.md)** - Validation testing

### Monitoring & Security
- **[MONITORING_SETUP.md](./docs/MONITORING_SETUP.md)** - Monitoring configuration
- **[SECURITY.md](./docs/SECURITY.md)** - Security best practices
- **[SENTRY_EVALUATION.md](./docs/SENTRY_EVALUATION.md)** - Sentry evaluation
- **[SENTRY_IMPLEMENTATION_SUMMARY.md](./docs/SENTRY_IMPLEMENTATION_SUMMARY.md)** - Sentry implementation
- **[SENTRY_SETUP.md](./docs/SENTRY_SETUP.md)** - Sentry setup guide
- **[SENTRY_TESTING.md](./docs/SENTRY_TESTING.md)** - Sentry testing

---

## 🔧 Development Scripts (`scripts/`)

- **[baseline.js](./scripts/baseline.js)** - Performance baseline tracking and comparison
- **[bundle-size.js](./scripts/bundle-size.js)** - Bundle size analysis and reporting
- **[perf-test.js](./scripts/perf-test.js)** - Performance testing utilities
- **[test-deployment.sh](./scripts/test-deployment.sh)** - Deployment testing script

**Usage**: Run from project root, see individual scripts for documentation.

---

## 📊 Issue Tracking (`issues/`)

**Main Index**: [INDEX.md](./issues/INDEX.md) - Central issue tracking

### Structure
- **[done/](./issues/done/)** - Completed issues organized by worker
- **[new/](./issues/new/)** - New/unassigned issues

### Workers
- **Worker01**: Project Manager & Planning
- **Worker02**: API Integration Expert
- **Worker03**: Vue.js/TypeScript Expert
- **Worker04**: Mobile Performance Specialist
- **Worker06**: Documentation Specialist
- **Worker07**: Testing & QA Specialist
- **Worker08**: DevOps & Deployment
- **Worker10**: Senior Review Master
- **Worker11**: UX Design Specialist
- **Worker12**: UX Review & Testing

**Status**: All 15 issues complete (100%) - Production approved ✅

---

## 📈 Performance Baselines (`baselines/`)

Performance metrics and historical data for tracking improvements.

- **[README.md](./baselines/README.md)** - Baseline documentation
- **baseline-history.json** - Historical performance data
- **performance-baseline.json** - Current performance baseline

---

## 📝 Examples (`examples/`)

Code examples and templates (future use).

**Status**: Empty - ready for future examples

---

## 🎯 Organization Principles

This directory follows **SOLID principles**:

1. **Single Responsibility**: Each subdirectory has one clear purpose
2. **Open/Closed**: Easy to extend without modifying structure
3. **Liskov Substitution**: Consistent file formats and patterns
4. **Interface Segregation**: Separate concerns (docs/scripts/issues)
5. **Dependency Inversion**: Navigation flows from general to specific

**Detailed Review**: See [ORGANIZATION_REVIEW.md](./ORGANIZATION_REVIEW.md)

---

## 🔍 Quick Reference

### Finding Information

| Need | Location |
|------|----------|
| Project status | [docs/NEXT_STEPS.md](./docs/NEXT_STEPS.md) |
| Getting started | [docs/QUICK_START.md](./docs/QUICK_START.md) |
| Deployment | [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) |
| API integration | [docs/API_INTEGRATION.md](./docs/API_INTEGRATION.md) |
| Testing | [docs/TESTING.md](./docs/TESTING.md) |
| Performance | [docs/PERFORMANCE.md](./docs/PERFORMANCE.md) |
| Accessibility | [docs/ACCESSIBILITY_GUIDE.md](./docs/ACCESSIBILITY_GUIDE.md) |
| Security | [docs/SECURITY.md](./docs/SECURITY.md) |
| Issues | [issues/INDEX.md](./issues/INDEX.md) |
| Scripts | [scripts/](./scripts/) |

---

## 📞 Contact

For questions about _meta organization:
- **Worker01** (Project Manager) - Overall organization
- **Worker06** (Documentation) - Documentation structure
- **Worker08** (DevOps) - Scripts and tooling

---

**Created**: 2025-11-11  
**Purpose**: Establish clear organization for non-deployment project files  
**Principles**: SOLID, DRY, clear separation of concerns
