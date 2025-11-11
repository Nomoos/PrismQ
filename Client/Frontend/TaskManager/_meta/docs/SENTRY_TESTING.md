# Sentry Testing Guide

**Document Owner**: Implementation Team  
**Created**: 2025-11-10  
**Status**: Complete

This guide shows how to test that Sentry error tracking is working correctly.

---

## Quick Test

### 1. Browser Console Test

The simplest way to test Sentry:

1. Open your deployed application
2. Open browser console (F12)
3. Run this command:
   ```javascript
   throw new Error('Test Sentry error from console')
   ```
4. Check your Sentry dashboard - you should see the error within seconds

### 2. Test Button in App (Development)

For thorough testing during development, add a test button to any view:

**Add to `src/views/Settings.vue` (temporary):**

```vue
<template>
  <div class="container mx-auto p-4">
    <!-- Existing settings content -->
    
    <!-- Sentry Test Section (remove before production) -->
    <section v-if="isDevelopment" class="mt-8 p-4 border-2 border-yellow-500 rounded-lg">
      <h3 class="text-lg font-semibold mb-2">🧪 Sentry Testing (Development Only)</h3>
      <p class="text-sm text-gray-600 mb-4">
        These buttons test different types of errors. Check your Sentry dashboard after clicking.
      </p>
      
      <div class="space-y-2">
        <button
          @click="testSimpleError"
          class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Test Simple Error
        </button>
        
        <button
          @click="testApiError"
          class="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600"
        >
          Test API Error
        </button>
        
        <button
          @click="testUnhandledError"
          class="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
        >
          Test Unhandled Error
        </button>
        
        <button
          @click="testCustomMessage"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Test Custom Message
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { captureSentryException, captureSentryMessage, addSentryBreadcrumb } from '@/utils/sentry'
import api from '@/services/api'

const isDevelopment = computed(() => import.meta.env.DEV)

// Test 1: Simple caught error
function testSimpleError() {
  try {
    throw new Error('Test error from Settings page')
  } catch (error) {
    captureSentryException(error as Error, {
      component: 'Settings',
      test: 'simple_error',
      timestamp: new Date().toISOString()
    })
    console.log('✅ Simple error sent to Sentry')
  }
}

// Test 2: API error (will fail)
async function testApiError() {
  try {
    await api.get('/this-endpoint-does-not-exist')
  } catch (error) {
    console.log('✅ API error captured (should appear in Sentry)')
  }
}

// Test 3: Unhandled error (triggers global handler)
function testUnhandledError() {
  addSentryBreadcrumb('User clicked unhandled error test button')
  // This will be caught by Vue's error handler
  setTimeout(() => {
    throw new Error('Unhandled test error from Settings page')
  }, 100)
  console.log('⚠️ Unhandled error will be thrown in 100ms')
}

// Test 4: Custom message
function testCustomMessage() {
  captureSentryMessage('User tested Sentry custom message', 'info', {
    component: 'Settings',
    test: 'custom_message',
    workerId: localStorage.getItem('worker_id'),
    timestamp: new Date().toISOString()
  })
  console.log('✅ Custom message sent to Sentry')
}
</script>
```

**Remember to remove this test section before deploying to production!**

---

## Testing Checklist

### Before Deployment

- [ ] Sentry DSN configured in `.env`
- [ ] `VITE_SENTRY_ENABLED=true`
- [ ] `VITE_SENTRY_ENVIRONMENT` set correctly (staging/production)
- [ ] Build completed successfully (`npm run build`)
- [ ] No console errors about Sentry initialization

### After Deployment

- [ ] Open application in browser
- [ ] Check browser console for: `[Sentry] Initialized successfully`
- [ ] Trigger test error (console or test button)
- [ ] Verify error appears in Sentry dashboard (within 1 minute)
- [ ] Check error includes:
  - [ ] Correct environment (production/staging)
  - [ ] Worker ID (if set)
  - [ ] Breadcrumbs (user actions)
  - [ ] Stack trace
  - [ ] Browser/OS information

### Source Maps Verification

- [ ] Trigger error in production
- [ ] Go to Sentry dashboard
- [ ] Click on the error
- [ ] Verify stack trace shows TypeScript code (not `[minified]`)
- [ ] File names should be `.vue` and `.ts` (not minified JS)

If you see `[minified]` instead of actual code:
1. Check that `SENTRY_AUTH_TOKEN` was set during build
2. Verify source maps were uploaded (check build logs)
3. See [SENTRY_SETUP.md](./SENTRY_SETUP.md) for manual upload

---

## Expected Behavior

### Development Environment

**Sentry should be DISABLED by default:**
- No errors sent to Sentry
- Errors only logged to console
- Faster debugging

To enable in development (for testing):
```bash
# .env
VITE_SENTRY_DSN=https://your-dsn@sentry.io/project-id
VITE_SENTRY_ENVIRONMENT=development
VITE_SENTRY_ENABLED=true
```

### Staging Environment

**Sentry should be ENABLED:**
- All errors captured
- High sampling rate (100% errors, 50% performance)
- Helps catch issues before production

### Production Environment

**Sentry should be ENABLED:**
- All errors captured
- Standard sampling rate (100% errors, 10% performance)
- Real-time alerts configured

---

## What Gets Captured?

### ✅ Captured Automatically

1. **JavaScript Errors**
   - Unhandled exceptions
   - Promise rejections
   - Vue component errors

2. **API Errors**
   - 5xx server errors (500, 502, 503, etc.)
   - Network failures (after retries exhausted)

3. **Context**
   - Worker ID (user identification)
   - API calls (breadcrumbs)
   - User actions (breadcrumbs)
   - Browser/OS information
   - Current URL/route

### ❌ NOT Captured (Filtered Out)

1. **Expected Errors**
   - Network timeouts (temporary)
   - Cancelled requests
   - 4xx client errors (400, 404, etc.)

2. **Browser Extension Errors**
   - Chrome extensions
   - Firefox add-ons

3. **Console Logs**
   - `console.log()`, `console.info()`
   - Only `console.error()` is captured

4. **PII (Privacy Protected)**
   - Passwords
   - API keys
   - Authorization tokens
   - Automatically scrubbed by Sentry config

---

## Error Examples

### Example 1: Simple Error

**Code:**
```typescript
throw new Error('Something went wrong')
```

**Sentry Dashboard:**
```
Error: Something went wrong
  at testError (Settings.vue:42)
  at onClick (Settings.vue:38)
  
Environment: production
Worker ID: worker-123
Breadcrumbs:
  - Navigation to /settings
  - Clicked test button
```

### Example 2: API Error

**Code:**
```typescript
await api.post('/tasks', { invalid: 'data' })
```

**Sentry Dashboard:**
```
APIError: Validation failed
  at ApiClient.post (api.ts:110)
  at createTask (TaskCreate.vue:45)
  
Status: 400
URL: /api/tasks
Method: POST
Environment: production
```

### Example 3: Network Error

**Code:**
```typescript
// Backend is down
await api.get('/tasks')
```

**Sentry Dashboard:**
```
NetworkError: Network error - please check your connection
  at ApiClient.get (api.ts:89)
  at fetchTasks (TaskList.vue:67)
  
Retries: 3
Environment: production
Breadcrumbs:
  - GET /api/tasks (attempt 1)
  - GET /api/tasks (attempt 2)
  - GET /api/tasks (attempt 3)
```

---

## Debugging Tips

### 1. Check Browser Network Tab

Look for requests to `sentry.io`:
- Should see POST requests to `https://[org].ingest.sentry.io/api/[id]/envelope/`
- Status should be 200 (success)
- If no requests, Sentry isn't initialized or errors aren't being sent

### 2. Check Browser Console

Look for Sentry logs:
```
[Sentry] Initialized successfully { environment: 'production', ... }
[Sentry] Event sent to Sentry
```

If you see:
```
[Sentry] Disabled - no DSN or explicitly disabled
```
Check your environment variables.

### 3. Check Sentry Dashboard Health

Go to: Sentry → Settings → Project → Health

Should show:
- ✅ Events being received
- ✅ Source maps uploaded (if configured)
- ✅ Recent events in timeline

### 4. Enable Debug Mode (Temporarily)

Add to `src/utils/sentry.ts`:
```typescript
Sentry.init({
  // ... existing config
  debug: true, // Enable debug logs
})
```

This will log all Sentry activity to console.

---

## Common Issues

### Issue: No errors in Sentry

**Causes:**
- DSN not configured
- `VITE_SENTRY_ENABLED=false`
- Running in development mode
- Errors are being filtered out

**Fix:**
1. Check `VITE_SENTRY_DSN` is set
2. Check `VITE_SENTRY_ENABLED=true`
3. Rebuild after changing env vars
4. Check browser console for Sentry logs

### Issue: Too many events (quota exceeded)

**Causes:**
- High error rate
- Infinite error loop
- Aggressive sampling

**Fix:**
1. Lower sampling: `VITE_SENTRY_SAMPLE_RATE=0.5`
2. Add error filters in `src/utils/sentry.ts`
3. Fix the underlying errors

### Issue: Can't see source code (minified)

**Causes:**
- Source maps not uploaded
- Wrong release version
- Auth token not configured

**Fix:**
See [SENTRY_SETUP.md](./SENTRY_SETUP.md) source maps section

---

## Next Steps

After successful testing:

1. **Configure Alerts**
   - Sentry → Alerts → Create Alert Rule
   - Set up email/Slack notifications
   - Configure thresholds (e.g., >10 errors/hour)

2. **Monitor Regularly**
   - Check Sentry dashboard daily
   - Review error trends
   - Prioritize frequent errors

3. **Release Tracking**
   - Set `VITE_SENTRY_RELEASE` for each deployment
   - Track errors per release
   - See which releases are stable

4. **Team Integration**
   - Invite team members to Sentry
   - Assign errors to developers
   - Track resolution status

---

**Last Updated**: 2025-11-10  
**Status**: Complete
