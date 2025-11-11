# Frontend/TaskManager - Quick Start Guide

**Last Updated**: 2025-11-11

## Development Setup

### 1. Install Dependencies

```bash
cd Frontend/TaskManager
npm install
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your Backend/TaskManager API URL
# Example:
# VITE_API_BASE_URL=https://api.prismq.nomoos.cz/api
# VITE_API_KEY=your-api-key
```

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at http://localhost:5173

### 4. Available Development Commands

```bash
# Development server with hot reload
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Build for production
npm run build

# Preview production build locally
npm run preview
```

## Building for Production

### Understanding Build Output

There are two types of build outputs:

1. **`dist/`** - Vite build output (created by `npm run build`)
   - Contains only compiled application files
   - For local preview and testing
   - ❌ Do NOT deploy this directory directly

2. **`deploy-package/`** - Deployment package (created by `build-and-package.sh`)
   - Contains everything from `dist/` plus deployment scripts
   - Ready for production deployment
   - ✅ Always deploy this directory

### Automated Build & Package (Recommended)

**Linux/Mac:**
```bash
./build-and-package.sh
```

**Windows:**
```bash
build-and-package.bat
```

**Clean rebuild:**
```bash
./build-and-package.sh --clean
```

This creates:
- `dist/` - Vite build output (intermediate)
- `deploy-package/` - Complete deployment package with all files
- `deploy-package-YYYYMMDD_HHMMSS.tar.gz` - Archive for easy transfer
- `deploy-package-YYYYMMDD_HHMMSS.zip` - Windows-compatible archive
- `deploy-package-latest.tar.gz` - Symlink to latest build

### Manual Build (Advanced)

If you only need the Vite build without deployment scripts:

```bash
# Build static files only
npm run build

# Output will be in dist/ directory
# Note: This does NOT create deploy-package/
```

**For production deployment, always use `build-and-package.sh` instead of manual build.**

## Deployment to Vedos/Wedos

See the comprehensive [Deployment Guide](./DEPLOYMENT.md) for detailed instructions.

### Quick Deployment Methods

**Method 1: FTP Upload (Easiest)**
1. Build package: `./build-and-package.sh`
2. Upload `deploy-package/` contents via FTP to your web root
3. Open browser: `https://your-domain.com/deploy.php`
4. Follow the deployment wizard

**Method 2: Automated CLI (SSH access required)**
```bash
# On local machine
./build-and-package.sh
scp deploy-package-latest.tar.gz user@server:/path/to/web/

# On server via SSH
cd /path/to/web
php deploy-auto.php --source=deploy-package-latest.tar.gz
```

**Method 3: Legacy deploy-deploy.php**
1. Build locally: `npm run build`
2. Upload `deploy-deploy.php` to your server root
3. Access via browser: `https://your-domain.com/taskmanager/deploy-deploy.php`
4. Follow the deployment wizard

## Next Steps

- **Configuration**: See [`.env.example`](../../.env.example) for all available environment variables
- **API Integration**: Read [API Integration Guide](./API_INTEGRATION.md)
- **Deployment**: Read [Deployment Guide](./DEPLOYMENT.md)
- **Testing**: Read [Testing Guide](./TESTING.md)
- **Troubleshooting**: Read [Troubleshooting Guide](./TROUBLESHOOTING.md) (coming soon)
