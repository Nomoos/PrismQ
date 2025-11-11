# Build vs Deploy Directories - Clarification Guide

**Version:** 1.0.0  
**Last Updated:** 2025-11-11  
**Purpose:** Clear explanation of dist/ vs deploy-package/ directories

## Quick Answer

**Which directory should I deploy?**  
→ **Always deploy `deploy-package/`**, never `dist/` directly.

**Why are there two directories?**  
→ `dist/` is the raw build output from Vite. `deploy-package/` adds deployment scripts and configurations on top of it.

---

## The Two Directories

### `dist/` Directory

**What it is:**
- Primary build output from Vite (the bundler)
- Created by: `npm run build`
- Location: `Frontend/TaskManager/dist/`

**What it contains:**
- Compiled JavaScript bundles
- Processed CSS files
- Optimized images and assets
- Generated `index.html`
- Public files (copied as-is)

**What it does NOT contain:**
- Deployment scripts (deploy.php, deploy-auto.php)
- Configured .htaccess (only .htaccess.example)
- Deployment documentation

**When to use it:**
- Local development preview (`npm run preview`)
- CI/CD intermediate step
- Bundle analysis
- **NOT for production deployment**

**Ignored by git:** ✅ Yes (in .gitignore)

---

### `deploy-package/` Directory

**What it is:**
- Complete deployment package
- Created by: `./build-and-package.sh` or `build-and-package.bat`
- Location: `Frontend/TaskManager/deploy-package/`

**What it contains:**
- Everything from `dist/` directory
- PLUS deployment scripts:
  - `deploy.php` - Deployment wizard
  - `deploy-auto.php` - CLI deployment script
  - `deploy-deploy.php` - Script downloader
- PLUS server configuration:
  - `.htaccess` - Apache SPA routing (generated from .htaccess.example)
  - `.htaccess.example` - Backup template
- PLUS deployment documentation:
  - `README_DEPLOYMENT.txt` - Deployment instructions

**When to use it:**
- Production deployment
- Staging deployment
- Any server deployment
- **This is what you upload to the server**

**Ignored by git:** ✅ Yes (in .gitignore)

---

## Build Workflow

```
┌─────────────────────┐
│  npm run build      │  Step 1: Vite builds the application
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  dist/ created      │  Raw build output (Vite)
└──────────┬──────────┘
           │
           │
┌──────────▼──────────┐
│ build-and-package.sh│  Step 2: Package for deployment
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ deploy-package/     │  Complete deployment package
│ created             │
│                     │
│ Contains:           │
│ • dist/* files      │
│ • deploy scripts    │
│ • .htaccess         │
│ • documentation     │
└──────────┬──────────┘
           │
           │
┌──────────▼──────────┐
│ Archives created:   │  Step 3: Archives for easy transfer
│ • .tar.gz           │
│ • .zip              │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Upload to server   │  Step 4: Deploy
└─────────────────────┘
```

---

## Common Questions

### Q: Why not just deploy dist/?

**A:** `dist/` lacks essential deployment tools:
- No deployment wizard (deploy.php) for easy setup
- No CLI deployment script (deploy-auto.php) for automation
- No configured .htaccess (only example file)
- No deployment documentation

### Q: Can I use npm run build instead of build-and-package.sh?

**A:** For local preview, yes. For deployment, no.
- `npm run build` → Creates `dist/` only
- `build-and-package.sh` → Creates `dist/` AND `deploy-package/`

### Q: What gets deployed on the server?

**A:** The contents of `deploy-package/` are uploaded to the server root:

```
Server Root (e.g., /www/ or /public_html/)
├── index.html           # From deploy-package/
├── assets/              # From deploy-package/
│   ├── index-[hash].js
│   ├── index-[hash].css
│   └── ...
├── deploy.php           # From deploy-package/
├── deploy-auto.php      # From deploy-package/
├── .htaccess            # From deploy-package/
└── health.json          # From deploy-package/
```

Note: There is NO `dist/` or `deploy-package/` directory on the server. Files are deployed flat.

### Q: I see dist/ in some documentation. Is it wrong?

**A:** Context matters:
- ✅ Correct: "Run `npm run build` to create `dist/`"
- ✅ Correct: "Check bundle size in `dist/stats.html`"
- ✅ Correct: "Source maps are in `dist/assets/*.map`"
- ❌ Wrong: "Upload `dist/` to your server"
- ❌ Wrong: "Deploy `dist/` to production"

### Q: What about in scripts and CI/CD?

**A:** Best practices:
- Use `build-and-package.sh` to create the full package
- Deploy `deploy-package/` or the generated archives
- Don't deploy `dist/` directly

**Example (Good):**
```bash
./build-and-package.sh
scp deploy-package-latest.tar.gz user@server:/tmp/
ssh user@server "cd /www && php deploy-auto.php --source=/tmp/deploy-package-latest.tar.gz"
```

**Example (Bad):**
```bash
npm run build
scp -r dist/* user@server:/www/
# Missing: deployment scripts, .htaccess, documentation
```

---

## Directory Comparison

| Feature | dist/ | deploy-package/ |
|---------|-------|-----------------|
| Created by | `npm run build` | `build-and-package.sh` |
| Contains build output | ✅ Yes | ✅ Yes |
| Contains deployment scripts | ❌ No | ✅ Yes |
| Contains .htaccess | ⚠️ Example only | ✅ Configured |
| Contains documentation | ❌ No | ✅ Yes |
| Ready for deployment | ❌ No | ✅ Yes |
| Use for local preview | ✅ Yes | ✅ Yes |
| Use for production | ❌ No | ✅ Yes |
| Ignored by git | ✅ Yes | ✅ Yes |

---

## Related Documentation

- [Project Structure](./PROJECT_STRUCTURE.md) - Detailed project organization
- [Deployment Guide](./DEPLOYMENT.md) - Full deployment instructions
- [Quick Start](./QUICK_START.md) - Getting started guide

---

## Summary

**Remember:**
1. `npm run build` → creates `dist/`
2. `build-and-package.sh` → creates `deploy-package/` (includes dist/ + extras)
3. Always deploy `deploy-package/`, never `dist/` directly
4. On the server, files are deployed flat (no dist/ or deploy-package/ directory)

**When in doubt:** Use `build-and-package.sh` and upload `deploy-package/`.
