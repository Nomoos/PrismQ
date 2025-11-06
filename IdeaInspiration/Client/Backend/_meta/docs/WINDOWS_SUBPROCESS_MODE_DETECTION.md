# Windows Subprocess Execution Fix

## Problem Statement

On Windows, the default asyncio event loop (`SelectorEventLoop`) does not support subprocess operations. When attempting to use `asyncio.create_subprocess_exec()`, it raises `NotImplementedError`.

### Error Message
```
NotImplementedError: asyncio.create_subprocess_exec not supported on this platform.
```

### Root Cause
Windows requires `ProactorEventLoopPolicy` for subprocess operations, but:
1. The default event loop policy is `SelectorEventLoopPolicy`
2. FastAPI/uvicorn may not automatically set the correct policy
3. Test environments may create event loops before policy is set

## Solution

### 1. Automatic Mode Detection

The `SubprocessWrapper` class now intelligently detects the platform and event loop policy:

```python
@staticmethod
def _detect_mode() -> RunMode:
    if sys.platform == 'win32':
        # Check if ProactorEventLoopPolicy is set
        policy = asyncio.get_event_loop_policy()
        if isinstance(policy, asyncio.WindowsProactorEventLoopPolicy):
            return RunMode.ASYNC  # Safe to use async subprocess
        else:
            return RunMode.THREADED  # Fallback to thread-based
    else:
        return RunMode.ASYNC  # Linux/macOS support async subprocess
```

### 2. Event Loop Policy Setup

In `src/main.py`, the policy is set at application startup:

```python
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

### 3. Fallback Mechanisms

If `ProactorEventLoopPolicy` is not set, the system automatically falls back to `THREADED` mode:

- **ASYNC mode**: Uses `asyncio.create_subprocess_exec()` (fastest, requires ProactorEventLoop on Windows)
- **THREADED mode**: Uses `subprocess.Popen()` in a thread pool (Windows-safe fallback)

### 4. Environment Variable Override

Users can explicitly set the execution mode:

```bash
# Windows
set PRISMQ_RUN_MODE=threaded
python -m uvicorn src.main:app

# Linux/macOS
export PRISMQ_RUN_MODE=threaded
python -m uvicorn src.main:app
```

## Testing

### Run Mode Detection Tests

```bash
cd Client/Backend
python -m pytest _meta/tests/test_subprocess_mode_detection.py -v
```

### Windows-Specific Tests

```bash
# On Windows only
python -m pytest _meta/tests/test_subprocess_mode_detection.py -v -k "windows"
```

## Deployment Recommendations

### Production (Windows)

1. **Preferred**: Let automatic detection use ProactorEventLoop
   ```python
   # In main.py (already implemented)
   if sys.platform == 'win32':
       asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
   ```

2. **Alternative**: Force THREADED mode for maximum compatibility
   ```bash
   set PRISMQ_RUN_MODE=threaded
   ```

### Development (Windows)

Use THREADED mode for reliability:
```bash
set PRISMQ_RUN_MODE=threaded
```

### CI/CD (Any Platform)

Use DRY_RUN mode for testing without executing modules:
```bash
export PRISMQ_RUN_MODE=dry-run
```

## Performance Comparison

| Mode | Platform | Performance | Reliability | Use Case |
|------|----------|-------------|-------------|----------|
| ASYNC | Linux/macOS | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Production |
| ASYNC | Windows (Proactor) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Production |
| THREADED | Windows | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Development/Fallback |
| LOCAL | Any | ⭐⭐⭐ | ⭐⭐⭐ | Debugging |
| DRY_RUN | Any | N/A | ⭐⭐⭐⭐⭐ | CI Testing |

## Troubleshooting

### Issue: "ASYNC mode requires Windows ProactorEventLoopPolicy"

**Solution 1**: Let automatic detection use THREADED mode (no action needed)

**Solution 2**: Explicitly set THREADED mode
```bash
set PRISMQ_RUN_MODE=threaded
```

**Solution 3**: Ensure ProactorEventLoopPolicy is set before importing FastAPI
```python
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI  # Import after setting policy
```

### Issue: Tests failing with subprocess errors

**Solution**: Set event loop policy in pytest configuration

Create `conftest.py`:
```python
import asyncio
import sys
import pytest

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

@pytest.fixture(scope="session")
def event_loop_policy():
    if sys.platform == 'win32':
        return asyncio.WindowsProactorEventLoopPolicy()
    return asyncio.DefaultEventLoopPolicy()
```

## Related Documentation

- **[WINDOWS_SUBPROCESS_FIX.md](./WINDOWS_SUBPROCESS_FIX.md)** - Original fix documentation
- **[WINDOWS_DEPLOYMENT.md](./WINDOWS_DEPLOYMENT.md)** - Windows deployment guide
- **[Issue #303](../../issues/new/Worker4/303-comprehensive-windows-subprocess-testing.md)** - Windows subprocess testing

## References

- [Python asyncio - Subprocess](https://docs.python.org/3/library/asyncio-subprocess.html)
- [Windows ProactorEventLoop](https://docs.python.org/3/library/asyncio-platforms.html#windows)
- [FastAPI + Windows + asyncio](https://github.com/tiangolo/fastapi/issues/1640)

---

**Status**: ✅ Implemented and Tested  
**Platform**: Windows 10/11 (Primary), Linux/macOS (Supported)  
**Version**: 1.0.0  
**Last Updated**: 2025-11-04
