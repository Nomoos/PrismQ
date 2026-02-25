# _meta Directory Structure Overview

## Visual Structure

```
_meta/
│
├── META_ORGANIZATION_REVIEW.md    # Comprehensive review of reorganization
├── STRUCTURE_OVERVIEW.md          # This file - structure reference
│
├── docs/                          # Documentation (SOLID-organized)
│   ├── README.md                  # Navigation hub (DIP)
│   │
│   ├── getting-started/           # SRP: User onboarding (ISP: User role)
│   │   ├── README.md             # Category navigation
│   │   ├── SETUP.md              # Installation & configuration
│   │   ├── USER_GUIDE.md         # How to use the application
│   │   ├── NODEJS_INSTALLATION.md # Node.js setup (consolidated)
│   │   ├── TROUBLESHOOTING.md    # Common issues & solutions
│   │   └── screenshots/          # UI screenshots
│   │
│   ├── development/               # SRP: Developer docs (ISP: Developer role)
│   │   ├── README.md             # Category navigation
│   │   ├── DEVELOPMENT.md        # Contributing guide
│   │   ├── TESTING.md            # Test coverage & commands
│   │   ├── CONFIGURATION.md      # Environment variables
│   │   ├── MODULES.md            # How to add modules
│   │   ├── SINGLE_RESPONSIBILITY_MODULE_PATTERN.md  # Code organization
│   │   ├── WORKER_IMPLEMENTATION_PLAN.md           # Worker strategy
│   │   └── WORKER_IMPLEMENTATION_GUIDELINES.md     # Worker best practices
│   │
│   ├── architecture/              # SRP: Design docs (ISP: Architect role)
│   │   ├── README.md             # Category navigation
│   │   ├── ARCHITECTURE.md       # System architecture
│   │   ├── ONDEMAND_ARCHITECTURE.md  # On-demand principles
│   │   ├── INTEGRATION_GUIDE.md  # Integration patterns
│   │   ├── DATA_DIRECTORY_RATIONALE.md  # Data design decisions
│   │   ├── POSTMAN_COLLECTION.md # API testing guide
│   │   └── SCREENSHOTS_GUIDE.md  # Screenshot documentation
│   │
│   ├── operations/                # SRP: Deployment/release (ISP: Operator role)
│   │   ├── README.md             # Category navigation
│   │   ├── DEPLOYMENT_CHECKLIST.md  # Pre-deployment verification
│   │   ├── RELEASE.md            # Release management guide
│   │   ├── RELEASE_QUICK_REFERENCE.md  # Quick commands
│   │   ├── RELEASE_NOTES_TEMPLATE.md   # Template
│   │   ├── SECURITY_FIXES.md     # Security updates
│   │   └── CHANGELOG.md          # Version history
│   │
│   └── archive/                   # SRP: Historical reference
│       ├── README.md             # Archive explanation
│       ├── IMPLEMENTATION_SUMMARY.md  # Historical: On-demand work
│       ├── IMPLEMENTATION_SUMMARY_MODULE_PATTERN.md  # Historical: Module work
│       ├── DEPLOYMENT_RESEARCH.md  # Historical: Platform research
│       ├── ROOT_FOLDER_STRUCTURE.md  # Outdated structure doc
│       ├── INSTALL_NODEJS_FIRST.md   # Superseded redirect
│       ├── NODEJS_WINDOWS_QUICKSTART.md  # Consolidated
│       └── OLD_README.md         # Previous docs README
│
├── examples/                      # Code examples
│   ├── workers/                   # Worker implementations
│   │   ├── README.md
│   │   ├── INTEGRATION_GUIDE.md
│   │   ├── python/              # Python worker example
│   │   ├── youtube/             # YouTube scraper example
│   │   └── php/                 # PHP worker example
│   └── PrismQ_Web_Client.postman_collection.json  # API collection
│
├── templates/                     # Documentation templates
│   ├── README.md
│   ├── API_DOCUMENTATION_TEMPLATE.md
│   ├── DEPLOYMENT_GUIDE_TEMPLATE.md
│   ├── INTEGRATION_GUIDE_TEMPLATE.md
│   ├── ISSUE_TEMPLATE.md
│   ├── README_TEMPLATE.md
│   └── WORKER_IMPLEMENTATION_TEMPLATE.md
│
├── tests/                         # Test documentation & load tests
│   ├── TESTING_GUIDE.md
│   ├── PERFORMANCE_BENCHMARKS.md
│   └── load/                    # Load testing scripts
│       ├── README.md
│       └── locustfile.py
│
├── issues/                        # Issue tracking
│   └── INDEX.md
│
└── _scripts/                      # Utility scripts
    ├── README_YOUTUBE_TEST_SCRIPTS.md
    ├── capture-screenshots.js
    ├── check-release-readiness.sh
    ├── check_installation.ps1
    ├── check_installation.sh
    ├── prepare-release.sh
    ├── run_dev.ps1
    ├── run_dev.sh
    ├── run_youtube_tests.*
    ├── start_backend.bat
    └── sync-versions.sh
```

## SOLID Principles Applied

### Single Responsibility Principle (SRP)
- **getting-started/**: User onboarding only
- **development/**: Developer information only
- **architecture/**: Design decisions only
- **operations/**: Deployment/release only
- **archive/**: Historical reference only

### Open/Closed Principle (OCP)
- Core structure (5 categories) is stable
- New docs added to appropriate category without restructuring
- Category READMEs provide extension points

### Liskov Substitution Principle (LSP)
- All category READMEs follow same structure
- Consistent navigation patterns
- Predictable user experience

### Interface Segregation Principle (ISP)
- Documentation segregated by user role
- Users see only relevant docs for their role
- No information overload

### Dependency Inversion Principle (DIP)
- Main README depends on categories (abstraction)
- Categories can reorganize internally without affecting top-level navigation
- Navigation through abstraction layers

## Quick Access by Role

| Role | Start Here | Key Documents |
|------|------------|---------------|
| **New User** | [getting-started/](docs/getting-started/) | SETUP.md, USER_GUIDE.md, TROUBLESHOOTING.md |
| **Developer** | [development/](docs/development/) | DEVELOPMENT.md, TESTING.md, MODULES.md |
| **Architect** | [architecture/](docs/architecture/) | ARCHITECTURE.md, ONDEMAND_ARCHITECTURE.md |
| **Operator** | [operations/](docs/operations/) | DEPLOYMENT_CHECKLIST.md, RELEASE.md |
| **Researcher** | [archive/](docs/archive/) | Historical documents, research notes |

## File Count Summary

| Category | Files | Purpose |
|----------|-------|---------|
| **getting-started/** | 4 docs + screenshots | User onboarding |
| **development/** | 7 docs | Developer guides |
| **architecture/** | 6 docs | Design documentation |
| **operations/** | 6 docs | Deployment/release |
| **archive/** | 7 docs | Historical reference |
| **Total docs/** | 30 organized | (was 31 flat) |
| **examples/** | 3 workers + API collection | Code examples |
| **templates/** | 7 templates | Documentation standards |
| **tests/** | 2 docs + load tests | Testing guides |
| **_scripts/** | 13 scripts | Automation |
| **issues/** | 1 index | Issue tracking |

## Navigation Flow

```
User arrives at repository
        ↓
    README.md (root)
        ↓
Selects documentation category based on role
        ↓
    _meta/docs/README.md
        ↓
Category README (getting-started, development, architecture, operations)
        ↓
Specific document
```

## Key Features

✅ **Role-Based Navigation**: Users find relevant docs quickly  
✅ **Single Responsibility**: Each category has one clear purpose  
✅ **Consistent Structure**: All categories follow same pattern  
✅ **Preserved History**: Archive keeps institutional knowledge  
✅ **Extensible Design**: Easy to add new docs without restructuring  
✅ **Clear Ownership**: Maintainers know which category to update  

## Maintenance Guide

### Adding New Documentation
1. Determine appropriate category
2. Add document to category directory
3. Update category README.md
4. Add entry to main docs/README.md if needed

### Archiving Documents
1. Move to archive/ directory
2. Add entry to archive/README.md explaining why
3. Update category README to remove reference
4. Update any cross-references

### Category Guidelines
- **Keep under 10 docs per category** - Create subcategories if needed
- **Consistent naming** - Use SCREAMING_SNAKE_CASE.md
- **Update READMEs** - Always update category README when adding docs
- **Cross-reference** - Link related docs across categories

## Related Documentation

- **[META_ORGANIZATION_REVIEW.md](META_ORGANIZATION_REVIEW.md)** - Detailed reorganization review
- **[docs/README.md](docs/README.md)** - Main documentation navigation hub
- **[templates/README.md](templates/README.md)** - Documentation templates

---

**Last Updated**: 2025-11-11  
**Maintained by**: Development Team  
**Status**: ✅ Active
