# Windows Setup Guide

Complete setup guide for running PrismQ Web Client Backend on Windows.

## Prerequisites

- Windows 10/11
- Python 3.10.x (Required - see note below)
- Git (optional, for cloning the repository)

### ⚠️ Python Version Requirement

**IMPORTANT: This project requires Python 3.10.x (NOT 3.11 or 3.12)**

- **Required Version**: Python 3.10.x (recommended: 3.10.11)
- **Download**: [python-3.10.11-amd64.exe](https://www.python.org/downloads/release/python-31011/)
- **Reason**: DaVinci Resolve compatibility + Client module dependencies
- **Do NOT use**: Python 3.11+ will cause compatibility issues

## Installation

### Step 1: Navigate to Backend Directory

```powershell
cd Client\Backend
```

### Step 2: Create Virtual Environment

```powershell
python -m venv venv
```

### Step 3: Activate Virtual Environment

```powershell
# PowerShell
venv\Scripts\Activate.ps1

# Command Prompt
venv\Scripts\activate.bat
```

### Step 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 5: Configure Environment

```powershell
# PowerShell
Copy-Item .env.example .env

# Command Prompt
copy .env.example .env
```

## Running the Server

### Method 1: Batch Script (Recommended)

The easiest way to start the server:

```powershell
start_server.bat
```

### Method 2: PowerShell Script

```powershell
.\start_server.ps1
```

### Method 3: Manual Startup

```powershell
venv\Scripts\activate
python -m src.uvicorn_runner
```

### ⚠️ CRITICAL: Do NOT Use Direct Uvicorn

**DO NOT run the server using:**
```powershell
uvicorn src.main:app --reload  # ❌ WRONG - Will cause NotImplementedError
```

**Why?** The server must be started with `python -m src.uvicorn_runner` to properly configure Windows event loop policy. Without this, module execution will fail with `NotImplementedError`.

## Verifying the Server

Once started, the server will be available at:

- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Common Issues

### NotImplementedError when running modules

**Error Message:**
```
NotImplementedError
File "src/core/module_runner.py", line 172
    process = await asyncio.create_subprocess_exec(
```

**Cause**: Server was started without Windows ProactorEventLoop policy

**Solution**:
1. Stop the server (CTRL+C)
2. Restart using one of the recommended methods:
   ```powershell
   start_server.bat
   ```
   Or manually:
   ```powershell
   python -m src.uvicorn_runner
   ```

**Alternative**: Set environment variable before starting:
```powershell
$env:PRISMQ_RUN_MODE = "threaded"
uvicorn src.main:app --reload
```

### ModuleNotFoundError: No module named 'uvicorn'

**Cause**: Dependencies not installed

**Fix**: 
```powershell
venv\Scripts\activate
pip install -r requirements.txt
```

### Virtual environment not found

**Cause**: Virtual environment not created

**Fix**: 
```powershell
python -m venv venv
```

### Wrong Python version installed

**Error**: Dependencies fail to install or runtime errors

**Fix**: 
1. Uninstall current Python if it's 3.11+
2. Download and install Python 3.10.11
3. Delete the `venv` folder
4. Recreate the virtual environment with Python 3.10

### Server won't start or crashes immediately

**Debug Steps**:
1. Check Python version: `python --version` (should be 3.10.x)
2. Verify dependencies: `pip list | findstr uvicorn`
3. Check logs for error messages
4. Ensure no other service is using port 8000

## Tips for Development

### Auto-Reload

The server automatically reloads when code changes are detected. This is enabled by default when using `src.uvicorn_runner`.

### Checking Logs

The server logs important information to the console, including:
- Event loop policy configuration
- Module execution status
- API request/response details

Watch for warnings about incorrect event loop policy at startup.

### Testing Module Execution

To verify module execution is working:

1. Start the server
2. Navigate to http://localhost:8000/docs
3. Try the `/api/modules` endpoint to list available modules
4. Use `/api/runs/execute` to run a test module
5. Check logs for successful subprocess creation

## Advanced Configuration

### Environment Variables

You can set these environment variables in `.env`:

- `DEBUG`: Enable debug mode (true/false)
- `LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `PRISMQ_RUN_MODE`: Force subprocess mode (async/threaded)

### Using Threaded Mode

If you encounter persistent subprocess issues, you can force threaded mode:

```powershell
# Set in PowerShell session
$env:PRISMQ_RUN_MODE = "threaded"

# Or add to .env file
echo "PRISMQ_RUN_MODE=threaded" >> .env
```

**Note**: Threaded mode uses a thread pool instead of async subprocess, which may be slightly slower but more compatible.

## Getting Help

If you encounter issues not covered here:

1. Check the main [Backend README.md](./README.md) for general documentation
2. Review [API_REFERENCE.md](./API_REFERENCE.md) for API details
3. Check the [issue tracker](https://github.com/Nomoos/PrismQ.IdeaInspiration/issues)
4. Look at server logs for specific error messages

## Platform-Specific Notes

### Windows 10 vs Windows 11

Both Windows 10 and Windows 11 are fully supported. The Windows event loop configuration works identically on both versions.

### Windows Subsystem for Linux (WSL)

If using WSL, you can follow the Linux setup instructions instead. WSL uses the Linux event loop policy, not the Windows one.

### Running in Windows Sandbox

The server can run in Windows Sandbox, but ensure:
- Python 3.10 is installed in the sandbox
- Network access is allowed
- Sufficient memory is allocated (4GB+ recommended)

## Security Considerations

- The server runs on localhost (127.0.0.1) by default
- Ensure `.env` file is not committed to version control
- Review CORS settings in production deployments
- Keep dependencies updated for security patches
