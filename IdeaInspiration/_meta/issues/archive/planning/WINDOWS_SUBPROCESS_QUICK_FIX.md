# URGENT: Windows Subprocess Fix - Quick Reference

**Issue**: Modules fail on Windows with `NotImplementedError` or `RuntimeError` about ProactorEventLoopPolicy

**Affects**: reddit-posts, hacker-news, YouTube Shorts, and potentially all modules

**Status**: FIX DEPLOYED - Auto-detection now works!

---

## Immediate Solution (Users)

### Option 1: Restart Server Correctly (Recommended)

**The server MUST be started with the uvicorn_runner on Windows:**

```powershell
# Stop current server (CTRL+C)

# Navigate to backend
cd Client\Backend

# Activate virtual environment
venv\Scripts\activate

# Start server correctly
python -m src.uvicorn_runner
```

**Why**: This sets the Windows ProactorEventLoopPolicy BEFORE FastAPI/uvicorn creates the event loop.

### Option 2: Use Auto-Detection (After Latest Update)

**If you have the latest code**, the system will automatically detect the event loop policy and use THREADED mode if ProactorEventLoop is not available.

**Pull latest changes:**
```powershell
git pull origin main
```

Then start the server any way you want - it will auto-detect and use the appropriate mode.

### Option 3: Force THREADED Mode (Environment Variable)

**Set environment variable before starting server:**

```powershell
# PowerShell
$env:PRISMQ_RUN_MODE = "threaded"
uvicorn src.main:app --reload

# Or in one line
$env:PRISMQ_RUN_MODE = "threaded"; uvicorn src.main:app --reload
```

```batch
# CMD
set PRISMQ_RUN_MODE=threaded
uvicorn src.main:app --reload
```

---

## For Developers

### What Was Fixed

1. **Improved Event Loop Detection** (`subprocess_wrapper.py`)
   - Now correctly detects `WindowsProactorEventLoopPolicy` by name
   - Auto-falls back to THREADED mode if not detected
   - Logs clear messages about which mode is being used

2. **Better Error Handling** (`module_runner.py`)
   - Catches `RuntimeError` from subprocess wrapper
   - Provides actionable error messages
   - Guides users to restart with uvicorn_runner

3. **Updated Documentation** (Issue #304)
   - Startup scripts for Windows (`.bat` and `.ps1`)
   - Clear troubleshooting guide
   - Prominent Windows warnings in README

### Files Changed

- `Client/Backend/src/core/subprocess_wrapper.py` - Fixed `_detect_mode()` 
- `Client/Backend/src/core/module_runner.py` - Added `RuntimeError` handling

### Testing

After the fix, the following should work:

**Scenario 1: Start with uvicorn_runner**
```
→ Detects WindowsProactorEventLoopPolicy
→ Uses ASYNC mode
→ ✅ All modules work
```

**Scenario 2: Start with regular uvicorn**
```
→ Detects wrong event loop policy
→ Auto-falls back to THREADED mode
→ ⚠️ Logs warning about performance
→ ✅ All modules still work
```

**Scenario 3: Set PRISMQ_RUN_MODE=threaded**
```
→ Forces THREADED mode
→ ✅ All modules work
```

---

## Verification

### Check What Mode Is Being Used

Look for this line in the server logs on startup:

```
src.core.subprocess_wrapper - INFO - Windows detected with [policy] - using [mode]
```

**Good (optimal performance):**
```
Windows ProactorEventLoop detected - using ASYNC mode
```

**OK (works but warns):**
```
Windows detected with WindowsSelectorEventLoopPolicy - using THREADED mode
For better performance, start server with: python -m src.uvicorn_runner
```

### Test a Module

1. Start backend server
2. Open http://localhost:8000
3. Go to Modules
4. Select any module (e.g., reddit-posts)
5. Configure parameters
6. Click "Run Module"
7. Check run status

**Before fix**: ❌ FAILED with NotImplementedError  
**After fix**: ✅ COMPLETED or RUNNING

---

## Related Issues

- **#304**: Windows Subprocess Deployment Fix (comprehensive fix)
- **#305**: Verify YouTube Module (testing)
- **#303**: Comprehensive Windows Subprocess Testing (future validation)

---

## Need Help?

### Still getting errors?

1. **Pull latest code**: `git pull origin main`
2. **Restart server**: `python -m src.uvicorn_runner`
3. **Check logs**: Look for subprocess_wrapper INFO/WARNING messages
4. **Try THREADED mode**: `$env:PRISMQ_RUN_MODE = "threaded"`

### Report Issues

If none of the solutions work:
1. Copy full error stack trace
2. Include server startup method
3. Include subprocess_wrapper log messages
4. Create issue with template in `_meta/issues/templates/`

---

**Last Updated**: 2025-11-04  
**Status**: Fix Deployed, Testing in Progress
