# Backend/TaskManager Organization

## Structure Overview

```
Backend/TaskManager/
├── README.md               # Module documentation (WHY: Essential entry point)
├── composer.json           # PHP dependencies (WHY: Essential for deployment)
├── composer.lock           # Locked dependencies (WHY: Essential for deployment)
├── src/                    # DEPLOYMENT CODE
│   ├── .gitignore          # Git ignore rules
│   ├── api/                # API endpoints
│   ├── config/             # Configuration files
│   ├── database/           # Database scripts and schema
│   ├── public/             # Public assets (Swagger UI, etc.)
│   ├── *.php               # PHP deployment scripts
│   └── *.sh                # Shell deployment scripts
└── _meta/                  # META-INFORMATION
    ├── docs/               # All documentation
    ├── examples/           # Example code
    ├── tests/              # Test files and documentation
    └── issues/             # Issue tracking
```

## File Organization Rules

### In `/src/*` (Deployment Code)
✅ All code that gets deployed to production
✅ API endpoints (`api/`)
✅ Configuration (`config/`)
✅ Database scripts (`database/`)
✅ Public assets (`public/`)
✅ PHP deployment scripts
✅ Shell scripts
✅ .gitignore

**Why:** This is the actual application code that runs in production.

### In `/_meta/` (Meta-Information)
✅ Documentation (`docs/`)
✅ Examples (`examples/`)
✅ Tests (`tests/`)
✅ Issue tracking (`issues/`)
✅ Planning documents (*.md files)

**Why:** This is information ABOUT the project, not the project itself.

### At Module Root (Essential Files)
✅ `README.md` - Module entry point and documentation
✅ `composer.json` - Dependency specification
✅ `composer.lock` - Locked dependency versions

**Why:** These files are essential for understanding and deploying the module. They should be immediately visible at the module root.

## Benefits

1. **Clear Separation**
   - Deployment code in `src/`
   - Meta-information in `_meta/`
   - Essential files at root

2. **Easy Deployment**
   - Deploy only `src/` folder
   - Include `composer.json` and `composer.lock` for dependencies
   - No accidental deployment of docs or tests

3. **Easy Navigation**
   - Developers know where to find code (`src/`)
   - Developers know where to find docs (`_meta/`)
   - Root level is clean and minimal

4. **Consistent Pattern**
   - Same structure can be applied to other modules
   - Predictable organization
   - Easy to onboard new developers

## What Goes Where?

| Item | Location | Reason |
|------|----------|--------|
| API endpoints | `src/api/` | Deployment code |
| Configuration files | `src/config/` | Deployment code |
| Database schema | `src/database/` | Deployment code |
| Public assets | `src/public/` | Deployment code |
| PHP scripts | `src/*.php` | Deployment code |
| Shell scripts | `src/*.sh` | Deployment code |
| Documentation | `_meta/docs/` | Meta-information |
| Examples | `_meta/examples/` | Meta-information |
| Tests | `_meta/tests/` | Meta-information |
| Issues | `_meta/issues/` | Meta-information |
| README | Root | Essential entry point |
| composer.json | Root | Essential for dependencies |
| composer.lock | Root | Essential for dependencies |

## Deployment Instructions

To deploy TaskManager:

1. Copy `src/` folder to production server
2. Copy `composer.json` and `composer.lock` to production server
3. Run `composer install --no-dev` in production
4. Configure `src/config/config.php` based on `src/config/config.example.php`
5. Run database setup: `php src/setup_database.php`
6. Point web server to `src/public/` as document root

**Note:** `_meta/` folder is NOT needed in production.
