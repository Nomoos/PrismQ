# TaskManager Directory Structure

This document describes the organization of the `_meta` directory.

## Directory Organization

```
_meta/
├── README.md                    # Navigation file
├── STRUCTURE.md                 # This file - directory structure details
├── STATUS.md                    # Project status and metrics
├── ORGANIZATION_REVIEW.md       # SOLID principles and reorganization details
│
├── docs/                        # All documentation (organized by category)
│   ├── README.md                # Documentation index
│   ├── architecture/            # Architecture & design (4 docs)
│   │   ├── README.md
│   │   ├── DATA_DRIVEN_ARCHITECTURE.md
│   │   ├── DATA_DRIVEN_API.md
│   │   ├── CUSTOM_HANDLERS_ANALYSIS.md
│   │   └── TASKMANAGER_ORGANIZATION.md
│   │
│   ├── api/                     # API reference (4 docs)
│   │   ├── README.md
│   │   ├── API_REFERENCE.md
│   │   ├── ENDPOINT_EXAMPLES.md
│   │   ├── OPENAPI_IMPLEMENTATION_SUMMARY.md
│   │   └── SWAGGER_DEPLOYMENT_INFO.md
│   │
│   ├── deployment/              # Deployment & operations (9 docs)
│   │   ├── README.md
│   │   ├── QUICK_START_DEPLOY.md
│   │   ├── DEPLOYMENT.md
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   ├── DEPLOYMENT_SCRIPT.md
│   │   ├── CHECK_SETUP_GUIDE.md
│   │   ├── HOSTING_INFO.md
│   │   ├── PRODUCTION_OPTIMIZATION_GUIDE.md
│   │   ├── PERFORMANCE_MONITORING.md
│   │   └── PERFORMANCE_MONITORING_STRATEGY.md
│   │
│   ├── development/             # Developer guides (3 docs)
│   │   ├── README.md
│   │   ├── QUERY_PROFILER_GUIDE.md
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   └── IMPLEMENTATION_SUMMARY_CLAIM_ENHANCEMENT.md
│   │
│   ├── security/                # Security documentation (2 docs)
│   │   ├── README.md
│   │   ├── SECURITY.md
│   │   └── SECURITY_HARDENING_SUMMARY.md
│   │
│   └── planning/                # Planning archive - historical (4 docs)
│       ├── README.md
│       ├── PROJECT_PLAN.md
│       ├── PARALLELIZATION_MATRIX.md
│       ├── NEXT_STEPS_RECOMMENDATIONS.md
│       └── UPDATE_SUMMARY_OPENAPI.md
│
├── examples/                    # Code examples
│   ├── enhanced_worker_examples.php
│   └── query_profiler_example.php
│
├── issues/                      # Issue tracking
│   └── INDEX.md                 # Issue status and tracking
│
└── tests/                       # Test suite and documentation
    ├── README.md
    ├── API_TESTING_GUIDE.md
    ├── QUICKSTART.md
    ├── TEST_STRATEGY.md
    ├── WORKER_TESTING_GUIDE.md
    ├── TestRunner.php
    ├── run_tests.php
    ├── validate.php
    ├── config/
    ├── integration/
    ├── security/
    ├── unit/
    └── worker/
```

## Organization Principles

This directory structure follows **SOLID principles**:

### Single Responsibility Principle
Each directory has one clear purpose:
- `architecture/` - System design documents only
- `api/` - API documentation only
- `deployment/` - Operations guides only
- `development/` - Developer tools and implementation history
- `security/` - Security guidelines only
- `planning/` - Historical planning documents only

### Open/Closed Principle
The structure is extensible without modification:
- New documents can be added to existing categories
- New categories can be added if needed
- Existing structure remains stable

### Interface Segregation Principle
Documentation is organized by audience:
- **Developers** use `architecture/` and `development/`
- **Operators** use `deployment/`
- **Security reviewers** use `security/`
- **Project managers** use `planning/` (historical)

### Liskov Substitution Principle
All category README files follow the same structure:
- Title and description
- List of documents
- Quick links or key concepts
- Consistent navigation patterns

### Dependency Inversion Principle
High-level navigation (main README) doesn't depend on low-level file details:
- Categories can reorganize internally
- README links to categories, not specific files
- Abstraction through category directories

## File Counts

- **Total Documentation**: 22 files
- **Active Documentation**: 18 files (architecture, api, deployment, development, security)
- **Archived Documentation**: 4 files (planning)
- **Navigation Files**: 7 README files
- **Meta Files**: 3 files (README, STRUCTURE, STATUS, ORGANIZATION_REVIEW)

## Navigation Strategy

1. **Main README** - Quick start and role-based navigation
2. **Category READMEs** - Context and document lists for each category
3. **docs/README.md** - Complete documentation index
4. **Individual docs** - Detailed content

This layered approach makes it easy to find information regardless of familiarity with the project.
