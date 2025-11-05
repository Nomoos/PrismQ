# PrismQ Web Client - Troubleshooting Guide

Solutions to common problems and issues with the PrismQ Web Client.

## Table of Contents

- [Backend Issues](#backend-issues)
- [Frontend Issues](#frontend-issues)
- [Module Execution Issues](#module-execution-issues)
- [Performance Issues](#performance-issues)
- [Network and Connectivity Issues](#network-and-connectivity-issues)
- [Data and Storage Issues](#data-and-storage-issues)
- [Getting Help](#getting-help)

## Backend Issues

### Backend Won't Start

#### Error: "Address already in use"

**Symptom:**
```
ERROR: [Errno 48] error while attempting to bind on address ('127.0.0.1', 8000): address already in use
```

**Cause:** Another process is using port 8000.

**Solution 1: Kill the existing process**

Windows:
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Linux/macOS:
```bash
lsof -ti:8000 | xargs kill -9
```

**Solution 2: Use a different port**

Edit `Backend/.env`:
```env
PORT=8001
```

Then update `Frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8001
```

#### Error: "Module 'fastapi' not found" or "No module named 'uvicorn'"

**Symptom:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause:** Dependencies not installed or virtual environment not activated.

**Solution:**
```bash
cd Backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Verify installation:
```bash
python -c "import fastapi; import uvicorn; print('OK')"
```

#### Error: "Permission denied" when accessing config files

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: 'configs/modules.json'
```

**Cause:** File permissions issue.

**Solution:**

Windows:
```bash
icacls Backend\configs /grant Everyone:(OI)(CI)F /T
```

Linux/macOS:
```bash
chmod -R 755 Backend/configs
chmod -R 755 Backend/data
chmod -R 755 Backend/logs
```

#### Error: "Failed to load modules.json"

**Symptom:**
```
ERROR: Failed to load module configuration from configs/modules.json
```

**Cause:** Invalid JSON syntax in modules.json.

**Solution:**
1. Validate JSON syntax using a JSON validator
2. Common issues:
   - Missing commas between objects
   - Trailing commas
   - Unescaped quotes in strings
   - Missing closing brackets

```bash
# Validate JSON
python -m json.tool Backend/configs/modules.json
```

### Backend Performance Issues

#### Slow API responses

**Symptom:** API requests take several seconds to complete.

**Cause:** Large module list, slow disk I/O, or resource constraints.

**Solution:**
1. Check system resources (CPU, RAM, Disk)
2. Reduce number of configured modules
3. Enable caching (if available)
4. Check for disk I/O bottlenecks

```bash
# Check disk I/O (Linux)
iostat -x 1

# Check disk I/O (Windows)
perfmon
```

#### Memory leaks

**Symptom:** Backend memory usage grows over time.

**Cause:** Long-running processes, log accumulation, or unclosed resources.

**Solution:**
1. Restart backend regularly
2. Configure log rotation
3. Limit run history retention
4. Monitor memory usage:

```bash
# Linux
ps aux | grep uvicorn

# Windows
tasklist | findstr python
```

## Frontend Issues

### Node.js and npm Issues

#### Error: "npm is not recognized" or "node is not recognized"

**Symptom:**
```
npm : The term 'npm' is not recognized as the name of a cmdlet, function, script file, or operable program.
node : The term 'node' is not recognized...
```

**Cause:** Node.js is not installed or not in system PATH.

**Solution:**
See the **[Node.js Installation Guide](NODEJS_INSTALLATION.md)** for complete step-by-step installation instructions for Windows, Linux, and macOS.

Quick fixes:
1. **Restart your terminal/PowerShell** - PATH is only updated in new sessions
2. **Verify Node.js is installed**: Check `C:\Program Files\nodejs\` (Windows)
3. **Add to PATH manually** (Windows):
   - Win + R → `sysdm.cpl` → Advanced → Environment Variables
   - Edit "Path" → Add `C:\Program Files\nodejs\`
   - Restart terminal
4. **Reinstall Node.js** with "Add to PATH" option checked

#### Error: Wrong Node.js version

**Symptom:**
```
error: unsupported engine "node@16.0.0"
```

**Cause:** Node.js version is too old (minimum 18.0, recommended 20.11.0+).

**Solution:**
Update to Node.js 20.11.0 or higher. See **[Node.js Installation Guide](NODEJS_INSTALLATION.md)**.

Using NVM:
```bash
nvm install 20.11.0
nvm use 20.11.0
```

### Frontend Won't Start

#### Error: "Cannot find module 'vue'" or similar

**Symptom:**
```
Error: Cannot find module 'vue'
```

**Cause:** Node dependencies not installed.

**Solution:**
```bash
cd Frontend
npm install
```

If issues persist:
```bash
rm -rf node_modules package-lock.json
npm install
```

#### Error: "Port 5173 is already in use"

**Symptom:**
```
Port 5173 is already in use
```

**Cause:** Vite dev server already running or another app using port 5173.

**Solution 1: Kill existing process**

Find and kill:
```bash
# Linux/macOS
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**Solution 2: Use different port**
```bash
npm run dev -- --port 3000
```

Then update `Backend/.env`:
```env
CORS_ORIGINS=http://localhost:3000
```

#### Error: TypeScript compilation errors

**Symptom:**
```
TS2304: Cannot find name 'Module'
```

**Cause:** Missing type definitions or TypeScript configuration issues.

**Solution:**
1. Ensure types are imported:
   ```typescript
   import type { Module } from '@/types/module';
   ```

2. Check `tsconfig.json` paths are correct

3. Restart TypeScript server:
   - VS Code: Ctrl+Shift+P → "TypeScript: Restart TS Server"

### Frontend Performance Issues

#### Slow page load

**Symptom:** Dashboard takes several seconds to load.

**Cause:** Large number of modules, slow API, or network issues.

**Solution:**
1. Check browser console for errors
2. Check Network tab for slow requests
3. Reduce number of modules displayed
4. Enable browser caching
5. Use production build:
   ```bash
   npm run build
   ```

#### UI freezes or becomes unresponsive

**Symptom:** Browser tab freezes when viewing logs.

**Cause:** Too many log lines, memory issues, or infinite loops.

**Solution:**
1. Clear browser cache
2. Close other tabs
3. Limit log display (implement pagination)
4. Check browser memory usage (Task Manager)

## Module Execution Issues

### Module Won't Execute

#### Error: "Script not found"

**Symptom:**
```
ERROR: Module script not found at path: ../../Sources/...
```

**Cause:** Invalid `script_path` in `modules.json`.

**Solution:**
1. Verify the path exists:
   ```bash
   ls -la ../../Sources/Content/Shorts/YouTubeShorts/src/main.py
   ```

2. Check path is relative to `Backend/` directory

3. Update `modules.json` with correct path:
   ```json
   {
     "script_path": "../../Sources/Content/Shorts/YouTubeShorts/src/main.py"
   }
   ```

#### Error: "Module returned non-zero exit code"

**Symptom:**
```
ERROR: Module execution failed with exit code 1
```

**Cause:** Module script error, missing dependencies, or invalid parameters.

**Solution:**
1. Check module logs in `Backend/logs/runs/`
2. Run module manually to see full error:
   ```bash
   cd Sources/Content/Shorts/YouTubeShorts
   python src/main.py --max_results 10
   ```
3. Verify module dependencies are installed
4. Check parameter values are valid

#### Error: "Permission denied" when executing module

**Symptom:**
```
PermissionError: [Errno 13] Permission denied
```

**Cause:** Script not executable or permission issues.

**Solution:**

Linux/macOS:
```bash
chmod +x ../../Sources/Content/Shorts/YouTubeShorts/src/main.py
```

Windows: Ensure Python is in PATH and `.py` files are associated with Python.

### Module Execution Hangs

**Symptom:** Module status shows "Running" but no logs appear.

**Causes and Solutions:**

1. **Module is waiting for input:**
   - Check if module expects user input
   - Modify module to accept parameters instead

2. **Module is stuck in infinite loop:**
   - Cancel the run
   - Check module code for logic errors

3. **Process spawning issue:**
   - Check backend logs: `Backend/logs/app.log`
   - Restart backend server

#### Error: "NotImplementedError" on Windows (Subprocess Creation Failed)

**Symptom:**
```
NotImplementedError
  File "asyncio\base_events.py", line 493, in _make_subprocess_transport
    raise NotImplementedError
```

**Cause:** On Windows, the default asyncio event loop doesn't support subprocess operations. The backend needs to use `ProactorEventLoop` for subprocess support.

**Solution:**

Use the custom uvicorn runner that sets the correct event loop policy:

```bash
cd Client/Backend
python -m src.uvicorn_runner
```

Or use the development scripts (already updated):
```powershell
# Windows PowerShell
Client\_meta\_scripts\run_dev.ps1
```

**Verification:**
Run the event loop test to confirm the fix:
```bash
cd Client/Backend
python src/test_event_loop.py
```

Expected output:
```
Platform: win32
Event loop policy: WindowsProactorEventLoopPolicy
✅ PASS: Windows event loop policy is correctly set
✅ PASS: Subprocess created successfully
```

For more details, see: `Backend/_meta/doc/WINDOWS_SUBPROCESS_FIX.md`

   - Check system resource limits

### Logs Don't Stream

**Symptom:** Logs don't appear in real-time or don't appear at all.

**Causes and Solutions:**

1. **SSE connection failed:**
   - Check browser console for SSE errors
   - Verify backend is running
   - Check firewall/antivirus blocking connections

2. **Module not printing to stdout:**
   - Modify module to use `print()` or `logging`
   - Ensure Python output isn't buffered:
     ```python
     import sys
     sys.stdout.flush()
     ```

3. **Browser SSE limit reached:**
   - Close other SSE connections
   - Refresh the page
   - Use different browser

## Performance Issues

### High CPU Usage

**Symptom:** CPU at 100% when running modules.

**Causes:**
- Module is CPU-intensive
- Multiple concurrent runs
- Inefficient module code

**Solutions:**
1. Run fewer modules concurrently
2. Optimize module code
3. Add delays in module loops
4. Monitor with:
   ```bash
   # Linux
   top
   
   # Windows
   Task Manager
   ```

### High Memory Usage

**Symptom:** System runs out of RAM.

**Causes:**
- Memory leaks in modules
- Large datasets in memory
- Too many concurrent runs

**Solutions:**
1. Limit `MAX_CONCURRENT_RUNS` in `Backend/.env`
2. Process data in chunks (modules)
3. Restart backend periodically
4. Monitor memory:
   ```bash
   # Linux
   free -h
   
   # Windows
   Task Manager → Performance → Memory
   ```

### Slow Log Streaming

**Symptom:** Logs appear with significant delay.

**Causes:**
- Network latency
- SSE buffering
- Server overload

**Solutions:**
1. Check network latency
2. Reduce concurrent runs
3. Check server resources
4. Disable output buffering in modules:
   ```python
   print("Log message", flush=True)
   ```

## Network and Connectivity Issues

### Frontend Can't Connect to Backend

#### Error: "Network Error" in browser console

**Symptom:**
```
AxiosError: Network Error
```

**Causes and Solutions:**

1. **Backend not running:**
   - Start backend: `uvicorn src.main:app --reload`
   - Verify: http://localhost:8000/health

2. **Wrong API URL:**
   - Check `Frontend/.env`:
     ```env
     VITE_API_BASE_URL=http://localhost:8000
     ```
   - Restart frontend after changes

3. **Firewall blocking connection:**
   - Allow Python through firewall
   - Allow Node through firewall
   - Temporarily disable firewall to test

#### Error: "CORS policy" error

**Symptom:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/modules' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Cause:** Backend CORS configuration doesn't allow frontend origin.

**Solution:**

Edit `Backend/.env`:
```env
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Restart backend.

Verify CORS headers:
```bash
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/api/modules
```

### SSE Connection Drops

**Symptom:** Logs stop streaming mid-execution.

**Causes and Solutions:**

1. **Network timeout:**
   - SSE will auto-reconnect
   - Check browser console for reconnection attempts

2. **Backend restarted:**
   - Logs may be lost during restart
   - SSE will reconnect automatically

3. **Proxy or firewall interference:**
   - SSE requires persistent connection
   - Configure proxy to allow SSE
   - Disable proxies for localhost

## Data and Storage Issues

### Configuration Not Saving

**Symptom:** Module parameters don't persist between launches.

**Causes and Solutions:**

1. **"Remember parameters" not checked:**
   - Ensure checkbox is checked before launching

2. **Permission denied writing to configs:**
   - Check file permissions:
     ```bash
     ls -la Backend/configs/parameters/
     chmod -R 755 Backend/configs/parameters/
     ```

3. **Disk space full:**
   - Check disk space:
     ```bash
     df -h  # Linux
     dir    # Windows
     ```

### Run History Missing

**Symptom:** Previous runs don't appear in history.

**Causes and Solutions:**

1. **run_history.json deleted or corrupted:**
   - File location: `Backend/data/run_history.json`
   - Backup and recreate if corrupted:
     ```json
     {
       "runs": []
     }
     ```

2. **Automatic cleanup triggered:**
   - Old runs are cleaned up automatically
   - Configure retention in backend code

### Logs Not Saved

**Symptom:** Log files missing from `Backend/logs/runs/`.

**Causes:**
- Log directory doesn't exist
- Permission issues
- Disk full

**Solutions:**
```bash
# Create log directory
mkdir -p Backend/logs/runs

# Fix permissions
chmod -R 755 Backend/logs

# Check disk space
df -h
```

## Getting Help

### Before Asking for Help

1. **Check this guide** for your specific issue
2. **Check logs:**
   - Backend: `Backend/logs/app.log`
   - Run logs: `Backend/logs/runs/`
   - Browser console: F12 → Console
3. **Try basic troubleshooting:**
   - Restart backend
   - Restart frontend
   - Clear browser cache
   - Check for typos in configuration

### Gathering Information

When reporting issues, include:

1. **Error Message:**
   - Full error text
   - Stack trace if available

2. **Environment:**
   - OS (Windows/Linux/macOS)
   - Python version: `python --version`
   - Node version: `node --version`
   - Browser and version

3. **Configuration:**
   - Relevant parts of `.env` files (remove secrets!)
   - Module configuration if relevant

4. **Logs:**
   - Backend logs
   - Browser console logs
   - Network tab screenshots

5. **Steps to Reproduce:**
   - What you did
   - What you expected
   - What actually happened

### Where to Get Help

1. **Documentation:**
   - [Setup Guide](SETUP.md)
   - [User Guide](USER_GUIDE.md)
   - [API Reference](API.md)
   - [Development Guide](DEVELOPMENT.md)

2. **GitHub Issues:**
   - Search existing issues: https://github.com/Nomoos/PrismQ.IdeaInspiration/issues
   - Open new issue with template

3. **API Documentation:**
   - http://localhost:8000/docs (when running)
   - Auto-generated, always up-to-date

### Enable Debug Mode

For more detailed error information:

**Backend:**
```env
# Backend/.env
DEBUG=true
LOG_LEVEL=DEBUG
```

**Frontend:**
```typescript
// Check browser console (F12)
// Enable Vue DevTools for component inspection
```

Restart both servers after enabling debug mode.

### Common Solutions Summary

| Problem | Quick Solution |
|---------|---------------|
| Port in use | Kill process or use different port |
| Module not found | Check script_path in modules.json |
| CORS error | Add frontend origin to Backend/.env |
| Dependencies missing | Run `pip install -r requirements.txt` or `npm install` |
| Logs not streaming | Check SSE connection, verify backend running |
| High memory usage | Reduce concurrent runs, restart backend |
| Config not saving | Check file permissions, ensure checkbox checked |
| Frontend can't connect | Verify backend running, check API URL |

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Maintained by**: PrismQ Development Team

**Need more help?** Open an issue at https://github.com/Nomoos/PrismQ.IdeaInspiration/issues
