# Windows Subprocess Support - Configuration Guide

**Platform**: Windows 10/11 (Primary Platform)  
**Hardware**: NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Overview

PrismQ is optimized for Windows as the primary platform. This document explains the Windows-specific asyncio configuration required for subprocess module execution.

## Problem

When running the PrismQ Web Client Backend on Windows, module execution would fail with a `NotImplementedError` when trying to create subprocesses using `asyncio.create_subprocess_exec()`.

### Error Details

```
NotImplementedError
  File "asyncio\base_events.py", line 493, in _make_subprocess_transport
    raise NotImplementedError
```

This error occurred in the `ModuleRunner._execute_async()` method at line 172 when attempting to launch module scripts as subprocesses.

### Root Cause

On Windows, the default event loop (`SelectorEventLoop`) does not support subprocess operations. Windows **requires** the `ProactorEventLoop` for subprocess functionality.

While the `main.py` file had code to set the Windows event loop policy:

```python
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

This wasn't working reliably when using `uvicorn --reload` because:
1. Uvicorn with `--reload` spawns child processes
2. The event loop policy must be set BEFORE uvicorn creates any event loops
3. When importing `main.py`, uvicorn may have already created its event loop

## Solution

Created a dedicated `uvicorn_runner.py` module that:
1. Sets the Windows event loop policy BEFORE importing uvicorn
2. Ensures the policy is applied to the main process before any event loops are created
3. Works correctly with uvicorn's reload functionality

### Implementation

**File: `src/uvicorn_runner.py`**

```python
import asyncio
import sys

def main():
    # Set Windows event loop policy BEFORE importing uvicorn
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Now import and run uvicorn
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
```

### Updated Startup Scripts

**PowerShell (`run_dev.ps1`):**
```powershell
python -m src.uvicorn_runner
```

**Bash (`run_dev.sh`):**
```bash
python -m src.uvicorn_runner
```

## Additional Fix: Frontend Run ID Display

### Problem

The frontend was displaying "Run ID: undefined" in the success alert when launching modules.

### Root Cause

The backend API returns `run_id` as the primary identifier field, but the frontend code was accessing `run.id`:

```javascript
alert(`Module "${selectedModule.value.name}" launched successfully! Run ID: ${run.id}`)
```

The TypeScript `Run` interface had both fields for backward compatibility:
```typescript
interface Run {
  id?: string  // Optional, for backward compatibility
  run_id: string  // Primary field
  // ...
}
```

### Solution

Updated `Dashboard.vue` to use the correct field:
```javascript
alert(`Module "${selectedModule.value.name}" launched successfully! Run ID: ${run.run_id}`)
```

Also updated frontend tests to use the correct API contract with `run_id` and `created_at` fields instead of deprecated `id` and `start_time` fields.

## Testing

### Verification on Linux

The fix has been verified on Linux to ensure it doesn't break non-Windows platforms:

```
Platform: linux
Event loop policy: _UnixDefaultEventLoopPolicy
✅ PASS: Non-Windows platform using _UnixDefaultEventLoopPolicy
✅ PASS: Subprocess created successfully
```

### Verification on Windows

To verify the fix on Windows:

1. Run the test script:
   ```
   python src/test_event_loop.py
   ```
   
   Expected output:
   ```
   Platform: win32
   Event loop policy: WindowsProactorEventLoopPolicy
   ✅ PASS: Windows event loop policy is correctly set
   ✅ PASS: Subprocess created successfully
   ```

2. Start the backend:
   ```
   python -m src.uvicorn_runner
   ```

3. Launch a module through the frontend or API and verify no `NotImplementedError` occurs

## Files Changed

### Backend
- **NEW**: `Client/Backend/src/uvicorn_runner.py` - Uvicorn runner with Windows subprocess support
- **NEW**: `Client/Backend/src/test_event_loop.py` - Test script for event loop verification
- **MODIFIED**: `Client/Backend/README.md` - Updated documentation with Windows note
- **MODIFIED**: `Client/_meta/_scripts/run_dev.ps1` - Updated to use uvicorn_runner
- **MODIFIED**: `Client/_meta/_scripts/run_dev.sh` - Updated to use uvicorn_runner

### Frontend
- **MODIFIED**: `Client/Frontend/src/views/Dashboard.vue` - Fixed run.id → run.run_id
- **MODIFIED**: `Client/Frontend/_meta/tests/unit/services.spec.ts` - Updated test mocks
- **MODIFIED**: `Client/Frontend/_meta/tests/unit/types.spec.ts` - Updated test mocks

## Migration Guide

### For Developers

If you're running the backend directly with uvicorn:

**Before:**
```bash
uvicorn src.main:app --reload
```

**After (recommended on Windows):**
```bash
python -m src.uvicorn_runner
```

**Alternative (if you need custom uvicorn options):**
```python
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn
uvicorn.run("src.main:app", host="0.0.0.0", port=8000, ...)
```

### For Production Deployments on Windows (Primary Platform)

**Recommended Approach**: Use the `uvicorn_runner` for both development and production on Windows.

#### Option 1: Windows Service with NSSM (Recommended)

1. Install [NSSM (Non-Sucking Service Manager)](https://nssm.cc/download)

2. Create a Windows Service:
   ```powershell
   # Navigate to Backend directory
   cd C:\Path\To\PrismQ.IdeaInspiration\Client\Backend
   
   # Install as Windows service
   nssm install PrismQBackend "C:\Path\To\Python310\python.exe" "-m" "src.uvicorn_runner"
   nssm set PrismQBackend AppDirectory "C:\Path\To\PrismQ.IdeaInspiration\Client\Backend"
   nssm set PrismQBackend DisplayName "PrismQ Web Client Backend"
   nssm set PrismQBackend Description "PrismQ content idea collection backend service"
   nssm set PrismQBackend Start SERVICE_AUTO_START
   
   # Start the service
   nssm start PrismQBackend
   ```

3. Manage the service:
   ```powershell
   # Check status
   nssm status PrismQBackend
   
   # Stop service
   nssm stop PrismQBackend
   
   # Restart service
   nssm restart PrismQBackend
   
   # Remove service
   nssm remove PrismQBackend confirm
   ```

#### Option 2: Task Scheduler (Auto-start on Windows boot)

1. Open Task Scheduler
2. Create New Task with these settings:
   - **General**: 
     - Name: PrismQ Backend
     - Run whether user is logged on or not
     - Run with highest privileges
   - **Triggers**: At startup
   - **Actions**: 
     - Program: `C:\Path\To\Python310\python.exe`
     - Arguments: `-m src.uvicorn_runner`
     - Start in: `C:\Path\To\PrismQ.IdeaInspiration\Client\Backend`

#### Option 3: Batch Script with Auto-restart

Use the provided `start_backend.bat` script:
```powershell
Client\_meta\_scripts\start_backend.bat
```

Or create a PowerShell auto-restart script:
```powershell
# run_backend_service.ps1
$BackendPath = "C:\Path\To\PrismQ.IdeaInspiration\Client\Backend"
cd $BackendPath

while ($true) {
    Write-Host "Starting PrismQ Backend..."
    & python -m src.uvicorn_runner
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Backend stopped normally"
        break
    }
    
    Write-Host "Backend crashed. Restarting in 5 seconds..."
    Start-Sleep -Seconds 5
}
```

### For Production Deployments on Linux

For Linux production deployments (secondary platform):

```bash
# Use systemd service
sudo systemctl start prismq-backend

# Or run with multiple workers
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## References

- [Python asyncio subprocess on Windows](https://docs.python.org/3/library/asyncio-platforms.html#windows)
- [Uvicorn deployment](https://www.uvicorn.org/deployment/)
- [FastAPI on Windows](https://fastapi.tiangolo.com/deployment/manually/#run-a-server-manually)

## Related Issues

- Fixes: "Module launched successfully! Run ID: undefined"
- Fixes: `NotImplementedError` when executing modules on Windows
- Implements: Proper Windows event loop policy configuration

---

**Last Updated**: 2025-11-04  
**Authors**: PrismQ Development Team
