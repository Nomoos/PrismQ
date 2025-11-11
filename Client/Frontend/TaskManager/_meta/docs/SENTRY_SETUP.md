# Sentry Error Tracking - Setup Guide

**Document Owner**: Implementation Team  
**Created**: 2025-11-10  
**Status**: Complete

This guide explains how to set up and use Sentry error tracking in the Frontend/TaskManager application.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Configuration Options](#configuration-options)
5. [Source Maps](#source-maps)
6. [Testing Sentry](#testing-sentry)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

Sentry provides real-time error tracking and performance monitoring for the Frontend/TaskManager application. It helps you:

- 🐛 **Catch errors** before users report them
- 📊 **Track error trends** across releases
- 🔍 **Debug production issues** with source maps
- 📈 **Monitor performance** of API calls and page loads
- 👥 **Identify affected users** and error frequency

### What's Integrated?

- ✅ Vue 3 error boundary
- ✅ API error tracking
- ✅ Performance monitoring
- ✅ User context (Worker ID)
- ✅ Breadcrumb tracking (user actions)
- ✅ Source map support
- ✅ Privacy controls (PII scrubbing)

---

## Quick Start

### 1. Sign Up for Sentry

1. Go to [sentry.io](https://sentry.io/)
2. Sign up for free account (5,000 errors/month)
3. Create a new project:
   - Platform: **Vue**
   - Project name: **prismq-taskmanager-frontend**
4. Copy your **DSN** (Data Source Name)
   - Format: `https://[key]@[org].ingest.sentry.io/[project-id]`

### 2. Configure Environment Variables

**For Production:**

```bash
# Copy production template
cp .env.production.example .env

# Edit .env and add your Sentry DSN
VITE_SENTRY_DSN=https://your-actual-dsn@sentry.io/your-project-id
VITE_SENTRY_ENVIRONMENT=production
VITE_SENTRY_ENABLED=true
```

**For Staging:**

```bash
# Copy staging template
cp .env.staging.example .env

# Edit .env and add your Sentry DSN
VITE_SENTRY_DSN=https://your-actual-dsn@sentry.io/your-project-id
VITE_SENTRY_ENVIRONMENT=staging
VITE_SENTRY_ENABLED=true
```

**For Development:**

```bash
# Copy example
cp .env.example .env

# Leave Sentry disabled in development (default)
# VITE_SENTRY_ENABLED=false
```

### 3. Build and Deploy

```bash
# Build with Sentry enabled
npm run build

# Deploy to your server
# (Sentry will start capturing errors automatically)
```

### 4. Verify Setup

1. Visit your deployed app
2. Trigger a test error (see [Testing Sentry](#testing-sentry))
3. Check your Sentry dashboard for the error

---

## Detailed Setup

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_SENTRY_DSN` | Yes | - | Your Sentry project DSN |
| `VITE_SENTRY_ENVIRONMENT` | No | `production` | Environment name (production/staging/development) |
| `VITE_SENTRY_ENABLED` | No | `true` | Enable/disable Sentry |
| `VITE_SENTRY_RELEASE` | No | - | Release version (e.g., `frontend-taskmanager@1.0.0`) |
| `VITE_SENTRY_SAMPLE_RATE` | No | `1.0` | % of errors to capture (0.0-1.0) |
| `VITE_SENTRY_TRACES_SAMPLE_RATE` | No | `0.1` | % of performance traces (0.0-1.0) |

### Full Configuration Example

**Production (.env.production.example):**

```bash
# Sentry Configuration
VITE_SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/789012
VITE_SENTRY_ENVIRONMENT=production
VITE_SENTRY_ENABLED=true
VITE_SENTRY_RELEASE=frontend-taskmanager@1.0.0
VITE_SENTRY_SAMPLE_RATE=1.0        # Capture 100% of errors
VITE_SENTRY_TRACES_SAMPLE_RATE=0.1 # Capture 10% of transactions
```

**Staging (.env.staging.example):**

```bash
# Sentry Configuration
VITE_SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/789012
VITE_SENTRY_ENVIRONMENT=staging
VITE_SENTRY_ENABLED=true
VITE_SENTRY_RELEASE=frontend-taskmanager@1.0.0-staging
VITE_SENTRY_SAMPLE_RATE=1.0        # Capture 100% of errors in staging
VITE_SENTRY_TRACES_SAMPLE_RATE=0.5 # Capture 50% of transactions (more testing)
```

---

## Configuration Options

### Error Sampling

Control how many errors are sent to Sentry:

```bash
# Capture all errors (recommended for production)
VITE_SENTRY_SAMPLE_RATE=1.0

# Capture 50% of errors (if high volume)
VITE_SENTRY_SAMPLE_RATE=0.5

# Capture 10% of errors (if very high volume)
VITE_SENTRY_SAMPLE_RATE=0.1
```

### Performance Monitoring

Control how many performance transactions are tracked:

```bash
# Capture 10% of transactions (recommended for production)
VITE_SENTRY_TRACES_SAMPLE_RATE=0.1

# Capture 50% of transactions (staging)
VITE_SENTRY_TRACES_SAMPLE_RATE=0.5

# Capture all transactions (not recommended - high quota usage)
VITE_SENTRY_TRACES_SAMPLE_RATE=1.0
```

### Release Tracking

Track errors per deployment:

```bash
# Use semantic versioning
VITE_SENTRY_RELEASE=frontend-taskmanager@1.0.0

# Include build number
VITE_SENTRY_RELEASE=frontend-taskmanager@1.0.0-build.42

# Include git commit
VITE_SENTRY_RELEASE=frontend-taskmanager@$(git rev-parse --short HEAD)
```

---

## Source Maps

Source maps allow Sentry to show you the original TypeScript/Vue code instead of minified JavaScript.

### Automatic Upload (Recommended)

1. **Get Sentry Auth Token:**
   - Go to Sentry → Settings → Account → API → Auth Tokens
   - Create new token with `project:releases` scope
   - Copy the token

2. **Set Environment Variable:**
   ```bash
   # Add to your build environment (CI/CD or local)
   export SENTRY_AUTH_TOKEN=your-auth-token
   
   # Also set these for the Vite plugin
   export VITE_SENTRY_ORG=your-org-name
   export VITE_SENTRY_PROJECT=prismq-taskmanager-frontend
   ```

3. **Build:**
   ```bash
   # Source maps will be automatically uploaded
   npm run build
   ```

### Manual Upload

If automatic upload fails, upload manually:

```bash
# Install Sentry CLI
npm install -g @sentry/cli

# Configure Sentry CLI
export SENTRY_AUTH_TOKEN=your-auth-token
export SENTRY_ORG=your-org-name
export SENTRY_PROJECT=prismq-taskmanager-frontend

# Create release
sentry-cli releases new frontend-taskmanager@1.0.0

# Upload source maps
sentry-cli releases files frontend-taskmanager@1.0.0 upload-sourcemaps ./dist/assets

# Finalize release
sentry-cli releases finalize frontend-taskmanager@1.0.0
```

### Verify Source Maps

1. Trigger an error in production
2. Go to Sentry dashboard
3. Click on the error
4. Check if you see TypeScript code (not minified JavaScript)
5. If you see `[minified]`, source maps aren't working

---

## Testing Sentry

### Test Error Capture

Add this to any Vue component to test error tracking:

```vue
<template>
  <button @click="triggerError">Test Sentry</button>
</template>

<script setup lang="ts">
import { captureSentryException } from '@/utils/sentry'

function triggerError() {
  try {
    throw new Error('Test error from Frontend/TaskManager')
  } catch (error) {
    captureSentryException(error as Error, {
      component: 'TestComponent',
      action: 'manual_test'
    })
  }
}
</script>
```

### Test API Error Capture

API errors are automatically captured. To test:

1. Make an API call that will fail (e.g., wrong endpoint)
2. Check Sentry dashboard for the error
3. Verify it includes request details

### Test Performance Monitoring

Performance is automatically tracked. To verify:

1. Navigate through the app
2. Go to Sentry → Performance
3. Check for transactions like:
   - `/tasks` (TaskList page)
   - `/tasks/:id` (TaskDetail page)
   - API calls

---

## Best Practices

### 1. Environment-Aware Configuration

✅ **DO:**
- Enable Sentry only in production/staging
- Use different DSNs or projects for staging vs production
- Set appropriate sampling rates per environment

❌ **DON'T:**
- Enable Sentry in development (slows down debugging)
- Use the same release version for staging and production

### 2. Error Filtering

The Sentry integration already filters:
- ✅ Browser extension errors
- ✅ Network errors (expected)
- ✅ Cancelled requests
- ✅ Non-error console output

Add more filters if needed in `src/utils/sentry.ts`:

```typescript
ignoreErrors: [
  'YourCustomErrorToIgnore',
  /regex pattern to ignore/,
]
```

### 3. Privacy

The integration already scrubs:
- ✅ Authorization headers
- ✅ API keys
- ✅ Password fields
- ✅ Token fields

**Additional PII scrubbing:**

Edit `beforeSend` hook in `src/utils/sentry.ts`:

```typescript
beforeSend(event) {
  // Remove email from error messages
  if (event.message) {
    event.message = event.message.replace(/[\w.-]+@[\w.-]+\.\w+/g, '[email]')
  }
  return event
}
```

### 4. User Context

Worker ID is automatically set as user context when:
- Worker initializes on app load
- Worker ID is changed in Settings

**Manually set user context:**

```typescript
import { setSentryUser } from '@/utils/sentry'

// Set user
setSentryUser('my-worker-id')

// Clear user
setSentryUser(null)
```

### 5. Custom Breadcrumbs

Add context for debugging:

```typescript
import { addSentryBreadcrumb } from '@/utils/sentry'

// Add breadcrumb when user performs action
addSentryBreadcrumb('User claimed task', {
  taskId: '123',
  taskType: 'data-collection'
})
```

### 6. Quota Management

Free tier limits:
- **5,000 errors/month**
- **10,000 performance events/month**

If you exceed limits:
- Lower `VITE_SENTRY_SAMPLE_RATE` (e.g., 0.5 = 50%)
- Lower `VITE_SENTRY_TRACES_SAMPLE_RATE` (e.g., 0.05 = 5%)
- Filter more error types
- Upgrade to paid plan ($26-$80/month)

---

## Troubleshooting

### Errors Not Appearing in Sentry

**Check:**

1. Is `VITE_SENTRY_DSN` set correctly?
   ```bash
   echo $VITE_SENTRY_DSN
   ```

2. Is Sentry enabled?
   ```bash
   # Should be 'true'
   echo $VITE_SENTRY_ENABLED
   ```

3. Did you rebuild after changing env vars?
   ```bash
   npm run build
   ```

4. Check browser console for Sentry logs:
   ```
   [Sentry] Initialized successfully
   ```

5. Verify in Network tab:
   - Look for requests to `sentry.io`
   - If none, Sentry isn't sending data

### Source Maps Not Working

**Check:**

1. Are source maps enabled in build?
   ```bash
   # Should see .map files in dist/assets/
   ls -la dist/assets/*.map
   ```

2. Is `SENTRY_AUTH_TOKEN` set for build?
   ```bash
   echo $SENTRY_AUTH_TOKEN
   ```

3. Are `VITE_SENTRY_ORG` and `VITE_SENTRY_PROJECT` set?
   ```bash
   echo $VITE_SENTRY_ORG
   echo $VITE_SENTRY_PROJECT
   ```

4. Check build logs for source map upload:
   ```
   [sentry-vite-plugin] Uploaded source maps to Sentry
   ```

5. Manually upload if automatic fails (see [Manual Upload](#manual-upload))

### Too Many Events (Quota Exceeded)

**Solutions:**

1. **Lower error sampling:**
   ```bash
   VITE_SENTRY_SAMPLE_RATE=0.5  # Capture 50% instead of 100%
   ```

2. **Lower performance sampling:**
   ```bash
   VITE_SENTRY_TRACES_SAMPLE_RATE=0.05  # Capture 5% instead of 10%
   ```

3. **Filter more errors:**
   - Edit `ignoreErrors` in `src/utils/sentry.ts`
   - Add patterns for errors you don't care about

4. **Upgrade plan:**
   - Free: 5,000 errors/month
   - Team: 50,000 errors/month ($26/month)
   - Business: 100,000 errors/month ($80/month)

### Performance Impact

Sentry adds ~10KB (3.4KB gzipped) to bundle size.

**If bundle is too large:**

1. Lazy-load Sentry:
   ```typescript
   // Load Sentry only when needed
   const initSentry = async () => {
     const { initSentry, getSentryConfig } = await import('@/utils/sentry')
     initSentry(app, router, getSentryConfig())
   }
   
   if (import.meta.env.PROD) {
     initSentry()
   }
   ```

2. Disable Sentry in specific environments

### Sentry Not Initializing

**Check browser console for:**

```
[Sentry] Disabled - no DSN or explicitly disabled
[Sentry] Skipping initialization in development mode
[Sentry] Failed to initialize: [error message]
```

**Common issues:**

- DSN is empty or invalid
- `VITE_SENTRY_ENABLED=false`
- Running in development mode without forcing enable

---

## Support

### Documentation

- **Official Sentry Docs**: https://docs.sentry.io/platforms/javascript/guides/vue/
- **Sentry Vue Guide**: https://docs.sentry.io/platforms/javascript/guides/vue/configuration/
- **Source Maps Guide**: https://docs.sentry.io/platforms/javascript/sourcemaps/

### Getting Help

1. **Check Sentry Dashboard**: Settings → Project → Health
2. **Review Sentry Logs**: Check browser console for `[Sentry]` messages
3. **Test Configuration**: Use test error button (see [Testing](#testing-sentry))
4. **Contact Support**: Sentry has excellent support (even on free tier)

### Useful Sentry CLI Commands

```bash
# Check configuration
sentry-cli info

# List releases
sentry-cli releases list

# Delete release (if upload failed)
sentry-cli releases delete frontend-taskmanager@1.0.0

# Test connection
sentry-cli send-event -m "Test message"
```

---

## Summary

### Setup Checklist

- [ ] Sign up for Sentry account
- [ ] Create Vue project in Sentry
- [ ] Copy DSN
- [ ] Set `VITE_SENTRY_DSN` in `.env`
- [ ] Set `VITE_SENTRY_ENVIRONMENT` (production/staging)
- [ ] Build application (`npm run build`)
- [ ] Deploy to server
- [ ] Test error capture
- [ ] Verify errors appear in Sentry dashboard
- [ ] (Optional) Configure source map upload
- [ ] (Optional) Set up alerts in Sentry

### Next Steps

After basic setup:

1. **Configure Alerts**: Sentry → Alerts → Create Alert Rule
2. **Set Up Integrations**: Connect to Slack, GitHub, etc.
3. **Monitor Performance**: Check Performance tab regularly
4. **Review Errors**: Triage errors weekly
5. **Track Releases**: Mark deployments in Sentry

---

**Last Updated**: 2025-11-10  
**Status**: Complete  
**Sentry Version**: @sentry/vue@8.38.0
