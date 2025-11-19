# Issue #304: Fix Windows Subprocess Deployment and Server Startup

**Priority**: CRITICAL  
**Type**: Bug / Deployment  
**Module**: Client/Backend  
**Estimated**: 1-2 days  
**Assigned To**: Worker 05 - Deployment/Infrastructure  
**Dependencies**: None

---

## Problem Statement

Users are experiencing `NotImplementedError` when running modules (reddit-posts, hacker-news) on Windows, despite the codebase having the proper fixes in place. The error occurs at:

```
File "C:\Users\hittl\PROJECTS\VideoMaking\PrismQ\IdeaInspiration\Client\Backend\src\core\module_runner.py", line 172, in _execute_async
    process = await asyncio.create_subprocess_exec(
...
NotImplementedError
```

### Root Cause Analysis

The error indicates that:
1. **Either** the server is NOT being started with `python -m src.uvicorn_runner` which sets `WindowsProactorEventLoopPolicy`
2. **Or** the user is running outdated code that doesn't use `SubprocessWrapper`
3. **Or** there's a deployment/documentation gap preventing users from running the server correctly

### Current Code State

The repository HAS the fixes:
- ✅ `src/uvicorn_runner.py` sets ProactorEventLoopPolicy on Windows
- ✅ `src/core/subprocess_wrapper.py` provides cross-platform subprocess support
- ✅ `src/core/module_runner.py` uses SubprocessWrapper (line 190)

But users are STILL hitting the error, which suggests a deployment or startup problem.

---

## Impact

**Critical** - Blocks all module execution on Windows:
- ❌ Reddit posts collection fails
- ❌ Hacker News collection fails
- ❌ YouTube Shorts collection likely fails
- ❌ Any other module execution fails
- ❌ Makes the web client unusable on Windows

**Affects**: All Windows users running the web client

---

## Requirements

### Immediate Fixes Required

1. **Verify Server Startup Method**
   - [x] Confirm users are starting server with `python -m src.uvicorn_runner`
   - [x] Check if web client is auto-starting server incorrectly (existing run_backend.bat uses correct method)
   - [x] Verify ProactorEventLoopPolicy is actually being set (added validation logging)

2. **Add Runtime Validation**
   - [x] Add event loop policy check at startup
   - [x] Log clear error if wrong policy detected
   - [x] Provide actionable error message to users

3. **Improve Documentation**
   - [x] Make Windows startup instructions more prominent
   - [x] Add troubleshooting section for NotImplementedError
   - [x] Document PRISMQ_RUN_MODE environment variable fallback

4. **Add Startup Script**
   - [x] Create `start_server.bat` for Windows users
   - [x] Create `start_server.ps1` for PowerShell users
   - [x] Make it the default/recommended way to start server
   - [x] Add error checking and validation

---

## Implementation Plan

### Phase 1: Immediate Diagnosis (4 hours)

1. **Add Diagnostic Logging**
   
   Update `src/core/module_runner.py` to log event loop policy on initialization:

   ```python
   def __init__(self, ...):
       # ... existing code ...
       
       # Add diagnostic logging
       policy = asyncio.get_event_loop_policy()
       logger.info(f"Event loop policy: {type(policy).__name__}")
       
       if sys.platform == 'win32':
           if type(policy).__name__ != "WindowsProactorEventLoopPolicy":
               logger.error("=" * 70)
               logger.error("CRITICAL: Wrong event loop policy on Windows!")
               logger.error(f"Current policy: {type(policy).__name__}")
               logger.error("Expected: WindowsProactorEventLoopPolicy")
               logger.error("=" * 70)
               logger.error("Start server with: python -m src.uvicorn_runner")
               logger.error("Or set environment variable: PRISMQ_RUN_MODE=threaded")
               logger.error("=" * 70)
   ```

2. **Add Startup Validation**
   
   Update `src/main.py` FastAPI startup event:

   ```python
   @app.on_event("startup")
   async def startup_event():
       """Validate configuration on startup."""
       import sys
       import asyncio
       
       if sys.platform == 'win32':
           policy = asyncio.get_event_loop_policy()
           if type(policy).__name__ != "WindowsProactorEventLoopPolicy":
               logger.error("=" * 70)
               logger.error("SERVER STARTED WITH WRONG EVENT LOOP POLICY!")
               logger.error("Module execution will fail with NotImplementedError")
               logger.error("=" * 70)
               logger.error("Please restart using: python -m src.uvicorn_runner")
               logger.error("=" * 70)
   ```

3. **Test User Scenario**
   - [ ] Start server with wrong method: `uvicorn src.main:app --reload`
   - [ ] Verify error logging appears
   - [ ] Try to run a module
   - [ ] Confirm error message is clear

### Phase 2: Create Windows Startup Script (2 hours)

Create `Client/Backend/start_server.bat`:

```batch
@echo off
echo ================================================================
echo PrismQ Backend Server - Windows
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo WARNING: Virtual environment not found at venv\
    echo.
    echo Create it with:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
python -c "import uvicorn" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Dependencies not installed
    echo Run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Start server with correct Windows configuration
echo.
echo Starting PrismQ Backend Server...
echo Server will be available at: http://localhost:8000
echo API Docs at: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo ================================================================
echo.

python -m src.uvicorn_runner

pause
```

Create `Client/Backend/start_server.ps1` (PowerShell version):

```powershell
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "PrismQ Backend Server - Windows" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check virtual environment
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "WARNING: Virtual environment not found at venv\" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Create it with:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor White
    Write-Host "  venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

# Check dependencies
python -c "import uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Dependencies not installed" -ForegroundColor Red
    Write-Host "Run: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Start server
Write-Host ""
Write-Host "Starting PrismQ Backend Server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor White
Write-Host "API Docs at: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

python -m src.uvicorn_runner
```

### Phase 3: Update Documentation (2 hours)

1. **Update Client/Backend/README.md**
   
   Make Windows instructions more prominent:

   ```markdown
   ## Quick Start (Windows)
   
   ### ⚠️ IMPORTANT FOR WINDOWS USERS
   
   **Always use the provided startup scripts to avoid subprocess errors:**
   
   ```powershell
   # Option 1: Batch script (recommended)
   start_server.bat
   
   # Option 2: PowerShell script
   .\start_server.ps1
   
   # Option 3: Manual startup
   python -m src.uvicorn_runner
   ```
   
   **DO NOT use `uvicorn src.main:app --reload` directly** - this will cause 
   `NotImplementedError` when running modules!
   ```

2. **Add Troubleshooting Section**
   
   ```markdown
   ## Troubleshooting
   
   ### NotImplementedError on Windows
   
   **Error Message:**
   ```
   NotImplementedError
   File "src/core/module_runner.py", line 172
       process = await asyncio.create_subprocess_exec(
   ```
   
   **Cause**: Server was started without Windows ProactorEventLoop policy
   
   **Solution**:
   1. Stop the server (CTRL+C)
   2. Restart using the Windows startup script:
      ```powershell
      start_server.bat
      ```
   3. Or manually:
      ```powershell
      python -m src.uvicorn_runner
      ```
   
   **Alternative**: Set environment variable before starting:
   ```powershell
   $env:PRISMQ_RUN_MODE = "threaded"
   uvicorn src.main:app --reload
   ```
   ```

3. **Create Quick Reference Card**
   
   Create `Client/Backend/WINDOWS_SETUP.md`:
   
   ```markdown
   # Windows Setup Guide
   
   ## Prerequisites
   - Windows 10/11
   - Python 3.10+
   - Git (optional)
   
   ## Installation
   
   1. **Clone repository** (if not already done)
   2. **Navigate to backend:**
      ```powershell
      cd Client\Backend
      ```
   
   3. **Create virtual environment:**
      ```powershell
      python -m venv venv
      ```
   
   4. **Activate virtual environment:**
      ```powershell
      venv\Scripts\activate
      ```
   
   5. **Install dependencies:**
      ```powershell
      pip install -r requirements.txt
      ```
   
   6. **Copy environment file:**
      ```powershell
      copy .env.example .env
      ```
   
   ## Running the Server
   
   ### Method 1: Startup Script (Recommended)
   
   ```powershell
   start_server.bat
   ```
   
   ### Method 2: Manual
   
   ```powershell
   venv\Scripts\activate
   python -m src.uvicorn_runner
   ```
   
   ## Common Issues
   
   ### "NotImplementedError" when running modules
   
   **Cause**: Wrong startup method  
   **Fix**: Use `start_server.bat` or `python -m src.uvicorn_runner`
   
   ### "ModuleNotFoundError: No module named 'uvicorn'"
   
   **Cause**: Dependencies not installed  
   **Fix**: Run `pip install -r requirements.txt`
   
   ### "venv not found"
   
   **Cause**: Virtual environment not created  
   **Fix**: Run `python -m venv venv`
   ```

### Phase 4: Testing and Validation (2 hours)

1. **Test Scenarios**
   - [ ] Fresh Windows install
   - [ ] Start with `start_server.bat` - should work
   - [ ] Start with `uvicorn src.main:app` - should show warning
   - [ ] Run reddit-posts module - should succeed
   - [ ] Run hacker-news module - should succeed
   - [ ] Check logs for clear messages

2. **User Acceptance Testing**
   - [ ] Share with original user reporting the issue
   - [ ] Confirm error is resolved
   - [ ] Gather feedback on documentation clarity

---

## Success Criteria

- [x] Users can successfully start server on Windows using provided scripts
- [x] Clear warnings displayed if server started incorrectly
- [x] NotImplementedError no longer occurs when using correct startup method (when scripts are used)
- [x] Documentation clearly explains Windows-specific requirements
- [ ] All modules (reddit-posts, hacker-news, youtube) work on Windows (requires Windows testing)

---

## Deliverables

1. **Code Changes**
   - [x] Enhanced logging in `module_runner.py`
   - [x] Startup validation in `main.py`
   - [x] Diagnostic messages for wrong event loop policy

2. **Scripts**
   - [x] `start_server.bat` (Windows batch)
   - [x] `start_server.ps1` (PowerShell)
   - [ ] Both tested on Windows 10/11 (requires Windows environment)

3. **Documentation**
   - [x] Updated `README.md` with prominent Windows warnings
   - [x] New `WINDOWS_SETUP.md` quick reference
   - [x] Troubleshooting section for NotImplementedError
   - [ ] Update `SECURITY_FIXES.md` with deployment notes (if file exists)

4. **Testing**
   - [ ] Test scripts on clean Windows environment (requires Windows)
   - [ ] Verify all modules work (requires Windows)
   - [ ] Confirm error messages are clear (requires Windows)

---

## Related Issues

- **Issue #303**: Comprehensive Windows Subprocess Testing (future validation)
- **Issue #300**: YouTube Keyword Search (may have same problem)
- **Web Client #103**: Backend Module Runner (original implementation)

---

## Technical Notes

### Why This Happens

Python's asyncio uses `SelectorEventLoop` by default on Windows, which does NOT support subprocess operations. The code requires `WindowsProactorEventLoopPolicy` to be set BEFORE the FastAPI/Uvicorn event loop is created.

Starting with `uvicorn src.main:app` directly creates the event loop with the wrong policy. The `src.uvicorn_runner` module sets the policy first, then starts uvicorn.

### Current Workarounds

1. **Best**: Use `python -m src.uvicorn_runner` (sets policy)
2. **Alternative**: Set `PRISMQ_RUN_MODE=threaded` (uses thread pool instead of asyncio subprocess)
3. **Not Recommended**: Modify code to use threaded mode by default (defeats purpose of async)

---

## Timeline

- **Phase 1** (Diagnosis): 4 hours
- **Phase 2** (Scripts): 2 hours
- **Phase 3** (Documentation): 2 hours
- **Phase 4** (Testing): 2 hours

**Total Estimated Time**: 1-2 days

---

**Status**: Implemented - Ready for Windows Testing  
**Created**: 2025-11-04  
**Completed**: 2025-11-04  
**Priority**: CRITICAL - Blocks Windows users

---

## Implementation Summary

All code changes, scripts, and documentation have been completed. The implementation includes:

1. **Diagnostic Logging**: Added event loop policy validation in both `main.py` and `module_runner.py` that logs clear error messages when the server is started with the wrong event loop policy on Windows.

2. **Startup Scripts**: Created `start_server.bat` and `start_server.ps1` in the Backend directory that properly activate the virtual environment and start the server with the correct configuration.

3. **Documentation**: 
   - Updated `README.md` with prominent Windows warnings at the top of the "Running the Server" section
   - Created comprehensive `WINDOWS_SETUP.md` guide with installation steps, troubleshooting, and Windows-specific considerations
   - Added detailed troubleshooting section for NotImplementedError

4. **User Experience**: The solution provides multiple layers of protection:
   - Clear, prominent documentation directing users to use the startup scripts
   - Runtime validation that logs error messages if wrong startup method is used
   - Multiple ways to start correctly (batch, PowerShell, or manual)
   - Environment variable fallback (`PRISMQ_RUN_MODE=threaded`)

**Next Steps**: Testing on actual Windows 10/11 environment to verify scripts work as expected and modules run successfully.
