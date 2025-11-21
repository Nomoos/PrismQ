# YouTube Shorts Module - Troubleshooting Guide

**Platform Focus**: Windows 10/11 with NVIDIA RTX 5090  
**Last Updated**: 2025-11-04

## Overview

This guide provides solutions to common problems and debugging techniques for the YouTube Shorts Source module on Windows platforms.

---

## Common Errors

### 1. "NotImplementedError: Subprocess not supported on Windows"

**Full Error**:
```
NotImplementedError: Subprocess transport not supported on Windows with SelectorEventLoop
```

**Cause**:
Backend started without Windows ProactorEventLoop policy. The default `SelectorEventLoop` doesn't support subprocess operations on Windows.

**Solution**:
Always start the backend using `uvicorn_runner.py`:

```powershell
# Navigate to backend directory
cd Client\Backend

# Start using uvicorn_runner.py (sets ProactorEventLoop)
py -3.10 -m src.uvicorn_runner
```

**Don't Use**:
```powershell
# ✗ WRONG - Will fail on Windows
uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Verify Fix**:
Check that the backend starts without errors and you see:
```
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Related Files**:
- `Client/Backend/src/uvicorn_runner.py` - Sets event loop policy
- `Client/Backend/src/core/subprocess_wrapper.py` - Subprocess creation

---

### 2. "ModuleNotFoundError: No module named 'src'"

**Full Error**:
```
ModuleNotFoundError: No module named 'src'
```

**Cause**:
Virtual environment not activated or dependencies not installed.

**Solution (Windows)**:

```powershell
# Navigate to YouTube module
cd Sources\Content\Shorts\YouTube

# Create virtual environment (if not exists)
py -3.10 -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
py -m src.cli --help
```

**Expected Output**:
```
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

  YouTube Shorts Scraper CLI

Options:
  --help  Show this message and exit.

Commands:
  run              Run scraping with specified mode
  scrape-channel   Scrape channel Shorts
  scrape-trending  Scrape trending Shorts
  stats            Show database statistics
```

**Troubleshooting**:
If activation fails, check Python installation:
```powershell
# Check Python version
py -3.10 --version

# Should output: Python 3.10.x
```

---

### 3. "WARNING: Keyword search not yet implemented, using trending fallback"

**Full Message**:
```
WARNING: Keyword search not yet implemented, using trending fallback
Scraping trending Shorts instead...
```

**Cause**:
Keyword/search mode not yet implemented (Issue #300). Module falls back to trending mode.

**Impact**:
- Search query parameter ignored
- Trending Shorts returned instead of search results
- Not an error - expected behavior

**Workaround**:
Use alternative modes:

```powershell
# ✓ Use channel mode for specific creators
py -m src.cli run --mode channel --channel-url "@SnappyStories_1" --max-results 50

# ✓ Use trending mode for popular content
py -m src.cli run --mode trending --max-results 50

# Manual keyword filtering on results
py -m src.cli export --output results.json
# Then filter JSON manually for keywords
```

**Status**:
Tracked in Issue #300 (Worker 1). Will be implemented in future release.

**Related**:
- See `docs/KNOWN_ISSUES.md` #1 for details

---

### 4. "sqlite3.OperationalError: database is locked"

**Full Error**:
```
sqlite3.OperationalError: database is locked
```

**Cause**:
Multiple processes trying to write to database simultaneously, or database not using WAL mode.

**Solution 1: Enable WAL Mode** (Recommended)

```python
# Already implemented in src/core/database.py
# Verify WAL mode is enabled
import sqlite3

conn = sqlite3.connect('youtube_shorts.db')
cursor = conn.execute("PRAGMA journal_mode")
print(cursor.fetchone()[0])  # Should output: wal
```

**Solution 2: Close Existing Connections**

```powershell
# Check if database is open in other programs
# Close: DB Browser for SQLite, DBeaver, etc.

# Or restart module
py -m src.cli run --mode trending --max-results 10
```

**Solution 3: Manual WAL Conversion**

If WAL mode is not enabled:

```powershell
# Using SQLite command line
sqlite3 youtube_shorts.db "PRAGMA journal_mode=WAL;"

# Or using Python
py -c "import sqlite3; conn = sqlite3.connect('youtube_shorts.db'); conn.execute('PRAGMA journal_mode=WAL'); print('WAL mode enabled')"
```

**Prevention**:
WAL mode is automatically enabled in `src/core/database.py`. If you created database manually, convert it to WAL.

---

### 5. "PermissionError: [WinError 5] Access is denied"

**Full Error**:
```
PermissionError: [WinError 5] Access is denied: 'youtube_shorts.db'
```

**Cause**:
Insufficient permissions or file locked by another process.

**Solution 1: Run as Administrator**

Right-click PowerShell → "Run as administrator"

```powershell
cd C:\Path\To\Sources\Content\Shorts\YouTube
py -3.10 -m src.cli run --mode trending
```

**Solution 2: Check File Permissions**

1. Right-click `youtube_shorts.db` → Properties
2. Security tab → Edit
3. Ensure your user has "Full control"

**Solution 3: Disable Antivirus Temporarily**

Windows Defender may block database writes:

1. Windows Security → Virus & threat protection
2. Manage settings → Add exclusion
3. Add folder: `Sources\Content\Shorts\YouTube`

**Solution 4: Check File Lock**

```powershell
# Install Handle tool (Sysinternals)
# https://docs.microsoft.com/en-us/sysinternals/downloads/handle

handle youtube_shorts.db

# Shows processes using the file
# Close those processes
```

---

### 6. "FileNotFoundError: [Errno 2] No such file or directory: '.env'"

**Full Error**:
```
FileNotFoundError: [Errno 2] No such file or directory: '.env'
```

**Cause**:
`.env` configuration file missing.

**Solution**:

```powershell
# Navigate to module directory
cd Sources\Content\Shorts\YouTube

# Copy example .env file
copy .env.example .env

# Edit configuration
notepad .env
```

**Minimum Configuration**:
```env
# .env
DATABASE_PATH=.\youtube_shorts.db
YOUTUBE_MAX_RESULTS=50
WORKING_DIR=.
```

**Optional Configuration**:
```env
YOUTUBE_API_KEY=your_api_key_here  # Only for API mode
MAX_VIDEO_LENGTH=180
MIN_ASPECT_RATIO=0.5
```

**Verify**:
```powershell
# Check .env exists
dir .env

# Test configuration loading
py -c "from src.core import Config; c = Config(); print(f'DB: {c.database_path}')"
```

---

### 7. "WARNING: ffmpeg not found. Audio/video processing may fail."

**Cause**:
FFmpeg not installed on Windows. Required by yt-dlp for video processing.

**Solution: Install via Chocolatey** (Recommended)

```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg

# Verify installation
ffmpeg -version
```

**Solution: Manual Installation**

1. Download FFmpeg: https://ffmpeg.org/download.html (Windows builds)
2. Extract to `C:\ffmpeg\`
3. Add to PATH:
   ```powershell
   # Add to PATH (current session)
   $env:Path += ";C:\ffmpeg\bin"
   
   # Add to PATH (permanently)
   [System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", "User")
   ```
4. Verify:
   ```powershell
   ffmpeg -version
   where ffmpeg  # Should show: C:\ffmpeg\bin\ffmpeg.exe
   ```

**Alternative: Embedded FFmpeg**

```powershell
# Install yt-dlp with embedded FFmpeg
pip install yt-dlp[ffmpeg]
```

**Impact if Missing**:
- Subtitle extraction may fail
- Some metadata incomplete
- Audio track processing unavailable

---

### 8. "HTTP Error 403: Forbidden" or "HTTP Error 429: Too Many Requests"

**Cause**:
Rate limiting or IP blocking from YouTube.

**Solution 1: Add Delays**

Modify plugin to add delays between requests:

```python
# Temporary fix in src/plugins/youtube_channel_plugin.py
import time

for video in videos:
    # Scrape video
    scrape_video(video)
    
    # Add delay (2 seconds)
    time.sleep(2)
```

**Solution 2: Use VPN or Proxy**

```powershell
# Configure proxy in .env
# .env
HTTP_PROXY=http://proxy-server:port
HTTPS_PROXY=http://proxy-server:port
```

**Solution 3: Reduce Concurrent Requests**

```powershell
# Reduce max results
py -m src.cli run --mode channel --max-results 10  # Instead of 50
```

**Solution 4: Wait and Retry**

```powershell
# Wait 10-30 minutes
# Then retry scraping
```

**Prevention**:
- Limit scraping to 50-100 Shorts per hour
- Add 1-2 second delays between requests
- Avoid scraping same channel repeatedly
- Use residential IP (not datacenter/VPN)

---

### 9. "ValueError: Invalid mode: 'search'"

**Full Error**:
```
ValueError: Invalid mode: 'search'. Expected: trending, channel, keyword
```

**Cause**:
Using outdated mode name. Mode should be `keyword`, not `search`.

**Solution**:

```powershell
# ✗ WRONG
py -m src.cli run --mode search --query "ideas"

# ✓ CORRECT
py -m src.cli run --mode keyword --query "ideas"

# Note: Keyword mode not yet implemented (Issue #300)
# Will fallback to trending mode with warning
```

**Valid Modes**:
- `trending` - Scrape trending Shorts
- `channel` - Scrape from specific channel (requires `--channel-url`)
- `keyword` - Search by keywords (not yet implemented, falls back to trending)

---

### 10. "UnicodeDecodeError: 'utf-8' codec can't decode byte..."

**Full Error**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x92 in position 10: invalid start byte
```

**Cause**:
Windows encoding issues (Windows-1252 vs UTF-8).

**Solution**:
Already handled in `subprocess_wrapper.py`. If you encounter this in custom scripts:

```python
# Reading subprocess output
try:
    text = line.decode('utf-8')
except UnicodeDecodeError:
    text = line.decode('windows-1252', errors='ignore')

# Reading files
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Writing files (always use UTF-8)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
```

**Prevention**:
Always specify encoding when reading/writing files on Windows.

---

## Debugging Techniques

### Enable Debug Logging

```powershell
# Set environment variable
$env:LOG_LEVEL = "DEBUG"

# Run CLI with debug output
py -m src.cli run --mode trending --max-results 10

# Or for backend
cd Client\Backend
$env:LOG_LEVEL = "DEBUG"
py -m src.uvicorn_runner
```

**Expected Output**:
```
DEBUG: Loading configuration from .env
DEBUG: Database path: C:\...\youtube_shorts.db
DEBUG: Creating YouTubeTrendingPlugin
DEBUG: Scraping trending Shorts...
INFO: Found 10 Shorts
DEBUG: Saving to database...
```

---

### Check Process Execution

**View Run Logs in Web Client**:

1. Open browser: `http://localhost:5173`
2. Navigate to "Logs" section
3. Find your run ID
4. View real-time logs

**View Subprocess Output**:

```powershell
# Run CLI directly to see output
py -m src.cli run --mode trending --max-results 10

# Output shows:
# - Configuration loading
# - Plugin initialization
# - Scraping progress
# - Database writes
# - Summary
```

---

### Verify Configuration

```powershell
# Test config loading
py -c "from src.core import Config; c = Config(); print(f'DB: {c.database_path}'); print(f'Max results: {c.max_results}')"

# Expected output:
# DB: C:\...\youtube_shorts.db
# Max results: 50
```

**Check Environment Variables**:

```powershell
# View all environment variables
Get-ChildItem Env:

# Check specific variable
echo $env:DATABASE_PATH
echo $env:YOUTUBE_API_KEY
```

---

### Database Inspection

**Using DB Browser for SQLite** (Windows GUI):

1. Download: https://sqlitebrowser.org/dl/
2. Install and open `youtube_shorts.db`
3. Browse Data → `idea_inspirations` table
4. Execute SQL queries

**Using Python**:

```powershell
# View database contents
py -m src.cli stats

# Export to JSON
py -m src.cli export --output results.json

# View in text editor
notepad results.json
```

**Using SQLite CLI**:

```powershell
# Install SQLite tools
choco install sqlite

# Open database
sqlite3 youtube_shorts.db

# SQL queries
.tables
SELECT COUNT(*) FROM idea_inspirations;
SELECT * FROM idea_inspirations LIMIT 10;
.quit
```

---

### Network Debugging

**Check Internet Connection**:

```powershell
# Test YouTube connectivity
Test-NetConnection -ComputerName youtube.com -Port 443

# Should show: TcpTestSucceeded : True
```

**Check Proxy Settings**:

```powershell
# View proxy settings
netsh winhttp show proxy

# Import Internet Explorer proxy settings
netsh winhttp import proxy source=ie
```

**Test with curl**:

```powershell
# Test YouTube API (if using API key)
curl "https://www.googleapis.com/youtube/v3/search?part=snippet&q=test&key=YOUR_KEY"

# Should return JSON response
```

---

### Memory and Performance

**Monitor Memory Usage**:

```powershell
# During scraping, open Task Manager (Ctrl+Shift+Esc)
# Processes → Find python.exe
# Check Memory usage (should be 200-500 MB)
```

**Profile Performance**:

```python
# Add to CLI script for profiling
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run scraping
plugin.scrape()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(20)  # Top 20 functions by time
```

---

## Windows-Specific Troubleshooting

### Python Version Issues

**Check Python Version**:

```powershell
# Check version
py -3.10 --version

# Should output: Python 3.10.x
```

**If Python 3.10 not found**:

1. Download: https://www.python.org/downloads/release/python-31011/
2. Install: `python-3.10.11-amd64.exe`
3. Check "Add Python to PATH"
4. Verify: `py -3.10 --version`

**Multiple Python Versions**:

```powershell
# List all installed Python versions
py --list

# Use specific version
py -3.10 -m venv venv
py -3.10 -m pip install -r requirements.txt
```

---

### PowerShell Execution Policy

**If scripts fail to run**:

```powershell
# Check current policy
Get-ExecutionPolicy

# Set to RemoteSigned (recommended)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for current session
Set-ExecutionPolicy Bypass -Scope Process
```

---

### Windows Defender / Antivirus

**If scraping is slow or fails**:

1. Windows Security → Virus & threat protection
2. Manage settings → Exclusions
3. Add folder exclusion: `C:\...\Sources\Content\Shorts\YouTube`
4. Add folder exclusion: `C:\...\Client\Backend`

**Check Real-time Protection logs**:

1. Windows Security → Protection history
2. Look for blocked actions related to Python or database files

---

### Virtual Environment Issues

**Activation fails**:

```powershell
# If .\venv\Scripts\activate fails, try:
.\venv\Scripts\Activate.ps1

# Or use CMD instead of PowerShell
cmd
venv\Scripts\activate.bat
```

**Dependencies not found after installation**:

```powershell
# Ensure venv is activated (prompt should show (venv))
# Reinstall dependencies
pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
```

---

## Getting Help

### Check Logs

**Backend Logs** (Web Client):
- Location: `Client/Backend/logs/` (if configured)
- Or: Real-time logs in terminal where backend is running

**CLI Output**:
- Captured in Web Client log viewer
- Or: Visible in terminal when running directly

**Database Logs**:
```powershell
# Check last 10 records
py -c "from src.core import Database; db = Database('./youtube_shorts.db'); ideas = db.get_ideas(limit=10); print(ideas)"
```

---

### Collect Debug Information

When reporting issues, include:

1. **Platform**: Windows version (Win 10/11, build number)
2. **Python**: Version (`py --version`)
3. **Error**: Full error message and traceback
4. **Steps**: Exact commands that triggered error
5. **Configuration**: Sanitized `.env` file (remove API keys)
6. **Logs**: Recent CLI/backend output

**Example**:

```
Platform: Windows 11 Pro (Build 22631)
Python: 3.10.11
Error: NotImplementedError: Subprocess not supported
Command: uvicorn main:app --reload
.env: DATABASE_PATH=.\youtube_shorts.db
Logs: [attach terminal output]
```

---

### Community Resources

- **Documentation**: `docs/` directory
- **GitHub Issues**: https://github.com/Nomoos/PrismQ.IdeaInspiration/issues
- **Known Issues**: `docs/KNOWN_ISSUES.md`
- **Architecture**: `docs/ARCHITECTURE.md`

---

## Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| Subprocess error on Windows | Use `py -3.10 -m src.uvicorn_runner` |
| Module not found | Activate venv: `.\venv\Scripts\activate` |
| Keyword search warning | Expected - use channel/trending mode |
| Database locked | Close other DB programs, WAL mode auto-enabled |
| Permission denied | Run as Administrator or check file permissions |
| Missing .env | Copy `.env.example` to `.env` |
| FFmpeg not found | `choco install ffmpeg` |
| Rate limiting | Add delays, reduce max-results |
| Encoding error | Already handled - ignore if no impact |

---

## Related Documentation

- **[KNOWN_ISSUES.md](./KNOWN_ISSUES.md)** - Complete list of known issues
- **[EXECUTION_FLOW.md](./EXECUTION_FLOW.md)** - Understanding how module works
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Module design and patterns
- **[Module README](../README.md)** - Quick start guide

---

**Platform**: Windows 10/11 (Primary)  
**GPU**: NVIDIA RTX 5090  
**Python**: 3.10.x (Required)  
**Last Updated**: 2025-11-04
