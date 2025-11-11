# Frontend/TaskManager - Project Structure

**Last Updated**: 2025-11-11

## Directory Overview

```
Frontend/TaskManager/
├── src/                          # Application source code (DEPLOYED)
├── public/                       # Public static files (DEPLOYED)
├── tests/                        # Test files (NOT DEPLOYED)
├── _meta/                        # Project metadata (NOT DEPLOYED)
├── dist/                         # Build output (generated, NOT in git)
├── node_modules/                 # Dependencies (generated, NOT in git)
├── Configuration files           # Build/dev configuration (NOT DEPLOYED)
└── Build/deployment scripts      # Scripts for building and deploying
```

## Source Code (`src/`)

Application source code that gets compiled and bundled for deployment.

```
src/
├── main.ts                       # Application entry point
├── App.vue                       # Root Vue component
├── router/                       # Vue Router configuration
│   └── index.ts
├── stores/                       # Pinia state management
│   ├── tasks.ts                  # Task store
│   └── worker.ts                 # Worker store
├── services/                     # API services
│   ├── api.ts                    # HTTP client configuration
│   ├── taskService.ts            # Task API operations
│   └── healthService.ts          # Health check service
├── components/                   # Vue components
│   ├── base/                     # Base/shared components
│   │   ├── ErrorDisplay.vue
│   │   ├── EmptyState.vue
│   │   └── ConfirmDialog.vue
│   ├── TaskCard.vue
│   ├── StatusBadge.vue
│   ├── NavigationBreadcrumb.vue
│   └── ...
├── views/                        # Page views (routes)
│   ├── TaskList.vue              # Task list page
│   ├── TaskDetail.vue            # Task detail page
│   ├── TaskCreate.vue            # Create task page
│   ├── WorkerDashboard.vue       # Worker dashboard
│   └── Settings.vue              # Settings page
├── composables/                  # Reusable composition functions
│   ├── useToast.ts
│   ├── useTaskActions.ts
│   ├── useTaskDetail.ts
│   ├── useTaskPolling.ts
│   ├── useFormValidation.ts
│   ├── useAccessibility.ts
│   └── ...
├── types/                        # TypeScript type definitions
│   └── index.ts
├── utils/                        # Utility functions
│   ├── sanitize.ts               # XSS protection
│   ├── dateFormatting.ts         # Date utilities
│   ├── statusHelpers.ts          # Status helpers
│   ├── performance.ts            # Performance utilities
│   ├── sentry.ts                 # Error monitoring
│   └── ...
├── assets/                       # Static assets
│   └── main.css                  # Global styles
└── styles/                       # Additional styles
    └── accessibility.css         # Accessibility styles
```

## Public Files (`public/`)

Static files copied as-is to the build output. Accessible at the web root.

```
public/
├── deploy-deploy.php             # Deployment bootstrap script
├── .htaccess.example             # Apache configuration template
├── sw.js                         # Service worker (PWA)
├── health.html                   # Health check page
├── health.json                   # Health check data
├── health.production.json        # Production health config
└── health.staging.json           # Staging health config
```

## Tests (`tests/`)

Test files for quality assurance. NOT included in deployment.

```
tests/
├── unit/                         # Unit tests (Vitest)
│   ├── tasks.spec.ts
│   ├── StatusBadge.spec.ts
│   ├── TaskDetail.spec.ts
│   └── ...
├── e2e/                          # End-to-end tests (Playwright)
│   ├── task-list.spec.ts
│   ├── workflows.spec.ts
│   ├── accessibility.spec.ts
│   └── ...
└── security/                     # Security tests
    └── xss.spec.ts
```

## Project Metadata (`_meta/`)

All project documentation, scripts, and metadata. NOT included in deployment.

```
_meta/
├── README.md                     # _meta organization guide
├── ORGANIZATION_REVIEW.md        # Structure review document
├── docs/                         # All project documentation
│   ├── NEXT_STEPS.md             # Project status & roadmap
│   ├── QUICK_START.md            # Quick start guide
│   ├── REQUIREMENTS.md           # System requirements
│   ├── TECHNOLOGY_STACK.md       # Tech stack details
│   ├── DEPLOYMENT.md             # Deployment guide
│   ├── TESTING.md                # Testing guide
│   ├── PERFORMANCE.md            # Performance guide
│   ├── SECURITY.md               # Security guide
│   ├── ACCESSIBILITY_GUIDE.md    # Accessibility compliance
│   └── [25+ more documents]
├── scripts/                      # Development scripts
│   ├── baseline.js               # Performance baseline
│   ├── bundle-size.js            # Bundle analysis
│   ├── perf-test.js              # Performance testing
│   └── test-deployment.sh        # Deployment testing
├── examples/                     # Code examples (future)
├── issues/                       # Issue tracking
│   ├── INDEX.md                  # Issue index
│   ├── done/                     # Completed issues
│   │   ├── Worker01/
│   │   ├── Worker02/
│   │   └── ...
│   └── new/                      # New issues
└── baselines/                    # Performance baselines
    ├── README.md
    ├── baseline-history.json
    └── performance-baseline.json
```

## Configuration Files (Root)

Build and development configuration files.

```
Frontend/TaskManager/
├── package.json                  # Dependencies and scripts
├── package-lock.json             # Dependency lock file
├── vite.config.ts                # Vite build configuration
├── tsconfig.json                 # TypeScript configuration
├── tailwind.config.js            # Tailwind CSS configuration
├── postcss.config.js             # PostCSS configuration
├── vitest.config.ts              # Vitest testing configuration
├── playwright.config.ts          # Playwright E2E configuration
├── playwright.ux-testing.config.ts
├── lighthouserc.cjs              # Lighthouse CI configuration
├── .gitignore                    # Git ignore rules
├── .env.example                  # Environment template
├── .env.production.example       # Production env template
└── .env.staging.example          # Staging env template
```

## Build Scripts (Root)

Scripts for building and deploying the application.

```
Frontend/TaskManager/
├── build-and-package.sh          # Linux/Mac build script
├── build-and-package.bat         # Windows build script
├── deploy.php                    # Server deployment script
└── deploy-auto.php               # Automated deployment script
```

## Build Output (`dist/`)

Generated build output. NOT in git, created by `npm run build`.

**Purpose:** Primary build output from Vite. Contains compiled and bundled application files.

**Created by:** `npm run build` command

```
dist/
├── index.html                    # Entry HTML file
├── assets/                       # Bundled assets
│   ├── [name]-[hash].js          # JavaScript bundles
│   └── [name]-[hash].css         # CSS bundles
├── deploy-deploy.php             # Copied from public/
├── .htaccess.example             # Copied from public/
├── sw.js                         # Copied from public/
└── health.*                      # Copied from public/
```

**Note:** `dist/` contains ONLY the built application files. For deployment, use `deploy-package/` instead (see below).

## Deployment Package (`deploy-package/`)

Generated deployment package. NOT in git, created by `build-and-package.sh`.

**Purpose:** Ready-to-upload deployment package that includes `dist/` contents plus deployment scripts.

**Created by:** `./build-and-package.sh` or `build-and-package.bat`

```
deploy-package/
├── index.html                    # From dist/
├── assets/                       # From dist/
│   ├── *.js
│   └── *.css
├── deploy-deploy.php             # From dist/
├── sw.js                         # From dist/
├── health.*                      # From dist/
├── deploy.php                    # Deployment wizard (ADDED)
├── deploy-auto.php               # CLI deployment script (ADDED)
├── .htaccess                     # Apache config (ADDED)
├── .htaccess.example             # Backup template (ADDED)
└── README_DEPLOYMENT.txt         # Deployment instructions (ADDED)
```

**Key Difference:**
- `dist/` = Build output (minimal, for development/preview)
- `deploy-package/` = Deployment package (includes deployment scripts and configurations)

**For deployment:** Always upload `deploy-package/` contents, NOT `dist/` directly.

## Generated Directories

These are generated and should NOT be in version control:

- `node_modules/` - npm dependencies (created by `npm install`)
- `dist/` - Build output (created by `npm run build`)
- `deploy-package/` - Deployment package (created by `build-and-package.sh`)
- `deploy-package-*.tar.gz` - Compressed archives (created by `build-and-package.sh`)
- `deploy-package-*.zip` - Windows archives (created by `build-and-package.sh`)
- `.vite/` - Vite cache

## Build & Deployment Workflow

Understanding the relationship between `dist/` and `deploy-package/`:

```
Step 1: npm run build
        ↓
     dist/ directory created
     (Vite build output)
        ↓
Step 2: ./build-and-package.sh
        ↓
     Copies dist/* to deploy-package/
     Adds deployment scripts
     Creates archives (.tar.gz, .zip)
        ↓
     deploy-package/ directory ready
     (Ready for server upload)
        ↓
Step 3: Upload to server
     - Via FTP: upload deploy-package/* contents
     - Via SCP: scp deploy-package-latest.tar.gz
     - Via deploy.php: run deployment wizard
```

## What Gets Deployed?

The contents of `deploy-package/` (NOT `dist/` directly):

```
Deployed Files:
├── index.html                    # Application entry point
├── assets/                       # Bundled JS/CSS
│   ├── *.js                      # JavaScript bundles
│   └── *.css                     # CSS bundles
├── deploy.php                    # Deployment setup wizard
├── deploy-auto.php               # CLI deployment script
├── deploy-deploy.php             # Script downloader
├── .htaccess                     # Apache SPA routing
├── .htaccess.example             # Configuration template
├── sw.js                         # Service worker
├── health.*                      # Health check files
└── README_DEPLOYMENT.txt         # Deployment instructions
```

## File Organization Principles

1. **Source code** → `src/` (gets compiled)
2. **Static files** → `public/` (copied as-is)
3. **Tests** → `tests/` (not deployed)
4. **Documentation** → `_meta/docs/` (not deployed)
5. **Scripts** → `_meta/scripts/` (not deployed)
6. **Config** → Root level (for build tools)
7. **Build scripts** → Root level (for deployment)

## Related Documentation

- [_meta Organization Guide](../_meta/README.md)
- [Quick Start Guide](./QUICK_START.md)
- [Deployment Guide](./DEPLOYMENT.md)
