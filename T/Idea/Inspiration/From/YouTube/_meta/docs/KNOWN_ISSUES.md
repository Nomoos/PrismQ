# YouTube Shorts Module - Known Issues

**Platform Focus**: Windows 10/11 with NVIDIA RTX 5090  
**Last Updated**: 2025-11-04

## Overview

This document lists known issues, limitations, and platform-specific considerations for the YouTube Shorts Source module. Issues are categorized by severity and platform impact.

---

## Critical Issues

### 1. Keyword Search Mode Not Implemented ⚠️

**Status**: Open (Issue #300)  
**Severity**: HIGH  
**Platform**: All platforms  

**Description**:
The keyword/search mode for YouTube Shorts scraping is not yet implemented. When users select "keyword" mode and provide a search query, the module falls back to trending results instead.

**Impact**:
- Users cannot search for specific topics or keywords
- "Search" parameter is ignored
- Falls back to trending mode silently (with warning)

**Current Behavior**:
```python
if mode == 'keyword':
    print("WARNING: Keyword search not yet implemented, using trending fallback")
    plugin = YouTubeTrendingPlugin(config)
    ideas = plugin.scrape(max_results=max_results)
```

**Expected Behavior**:
```python
if mode == 'keyword':
    plugin = YouTubeSearchPlugin(config)
    ideas = plugin.scrape(query=query, max_results=max_results)
```

**Workaround**:
- Use **channel mode** to scrape specific channels
- Use **trending mode** to discover popular content
- Manual keyword filtering on scraped results

**Planned Fix**:
- Issue #300: Implement YouTube Data API v3 search
- Estimated: 1-2 weeks
- Requires: YouTube API key configuration
- Consideration: API quota limits (10,000 units/day)

**Related Files**:
- `src/cli.py` (line ~120) - Mode routing
- `src/plugins/youtube_search_plugin.py` (to be created)

**References**:
- Issue #300: Implement YouTube Shorts Keyword Search Mode
- Worker 1 Assignment

---

## Windows-Specific Issues

### 2. Windows Subprocess Execution Requires ProactorEventLoop 🪟

**Status**: **RESOLVED** (Workaround implemented)  
**Severity**: CRITICAL  
**Platform**: Windows only  

**Description**:
On Windows, the default `SelectorEventLoop` doesn't support subprocess operations with `asyncio.create_subprocess_shell()`. This causes a `NotImplementedError` when the backend attempts to spawn the CLI subprocess.

**Error Message**:
```
NotImplementedError: Subprocess not supported on Windows with SelectorEventLoop
```

**Root Cause**:
Windows asyncio uses `SelectorEventLoop` by default, which lacks subprocess support. The `ProactorEventLoop` is required for subprocess operations on Windows.

**Solution** (Implemented):
The backend uses `uvicorn_runner.py` to set the event loop policy before starting Uvicorn:

```python
# Client/Backend/src/uvicorn_runner.py
import sys
import asyncio

if sys.platform == "win32":
    # CRITICAL: Set ProactorEventLoop policy for subprocess support on Windows
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Then start Uvicorn
import uvicorn
uvicorn.run("main:app", host="0.0.0.0", port=8000)
```

**Important**:
⚠️ Always start the backend using `uvicorn_runner.py`, not `uvicorn` directly:

```powershell
# ✓ CORRECT (Windows)
cd Client\Backend
py -3.10 -m src.uvicorn_runner

# ✗ WRONG (Windows) - Will fail with NotImplementedError
uvicorn main:app --reload
```

**Verification**:
```python
# Check current event loop policy (Python REPL)
import asyncio
import sys

if sys.platform == "win32":
    policy = asyncio.get_event_loop_policy()
    print(f"Event loop policy: {policy}")
    # Should print: WindowsProactorEventLoopPolicy
```

**Related Files**:
- `Client/Backend/src/uvicorn_runner.py` (Solution implementation)
- `Client/Backend/src/core/subprocess_wrapper.py` (Subprocess spawning)

**References**:
- Python asyncio documentation: Windows Subprocess Support
- Client/_meta/docs/ARCHITECTURE.md: Windows Subprocess Handling

---

### 3. Windows Path Separators 🪟

**Status**: **MITIGATED** (Using pathlib)  
**Severity**: MEDIUM  
**Platform**: Windows only  

**Description**:
Windows uses backslashes (`\`) for path separators, while Unix uses forward slashes (`/`). Hardcoded paths can break on Windows.

**Problem Example**:
```python
# ✗ BAD: Hardcoded Unix paths
db_path = "Sources/Content/Shorts/YouTube/youtube_shorts.db"

# On Windows, this becomes:
# Sources\Content\Shorts\YouTube\youtube_shorts.db
```

**Solution** (Implemented):
Use `pathlib.Path` for cross-platform compatibility:

```python
# ✓ GOOD: Cross-platform paths
from pathlib import Path

db_path = Path("Sources") / "Content" / "Shorts" / "YouTube" / "youtube_shorts.db"
# Automatically uses correct separator for platform
```

**Best Practices**:
```python
from pathlib import Path

# Working directory
working_dir = Path.cwd()

# Absolute paths
abs_path = Path(relative_path).resolve()

# Join paths
config_path = working_dir / "config" / "settings.json"

# Convert to string when needed
sqlite_path = str(db_path)  # For SQLite connection
```

**Related Files**:
- `src/core/config.py` - Configuration path handling
- `src/core/database.py` - Database path resolution

---

### 4. File Encoding Issues (Windows-1252 vs UTF-8) 🪟

**Status**: **MITIGATED** (Encoding handling added)  
**Severity**: LOW  
**Platform**: Windows only  

**Description**:
Windows may use different text encodings (Windows-1252, UTF-8 with BOM) which can cause decoding errors when reading subprocess output or files.

**Error Example**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x92 in position 10
```

**Solution** (Implemented):
Fallback encoding when reading subprocess output:

```python
# Client/Backend/src/core/subprocess_wrapper.py
async def stream_output(stream):
    while True:
        line = await stream.readline()
        if not line:
            break
        
        # Try UTF-8 first, fallback to Windows-1252
        try:
            text = line.decode('utf-8')
        except UnicodeDecodeError:
            text = line.decode('windows-1252', errors='ignore')
        
        yield text
```

**File Writing**:
```python
# Always specify UTF-8 encoding when writing files
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
```

**Related Files**:
- `Client/Backend/src/core/subprocess_wrapper.py` - Output decoding
- `src/core/config.py` - .env file reading

---

### 5. FFmpeg Not Found on Windows 🪟

**Status**: Known limitation  
**Severity**: MEDIUM  
**Platform**: Windows only  

**Description**:
yt-dlp requires FFmpeg for processing videos and extracting audio. On Windows, FFmpeg is not installed by default.

**Error Message**:
```
WARNING: ffmpeg not found. Audio/video processing may fail.
```

**Impact**:
- Subtitle extraction may fail
- Audio track processing unavailable
- Some metadata may be incomplete

**Solution**:
Install FFmpeg on Windows using Chocolatey:

```powershell
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg

# Verify installation
ffmpeg -version
```

**Manual Installation**:
1. Download FFmpeg from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg\`
3. Add `C:\ffmpeg\bin\` to PATH environment variable
4. Restart terminal/IDE

**Verification**:
```powershell
# Check if FFmpeg is in PATH
where ffmpeg

# Should output: C:\ffmpeg\bin\ffmpeg.exe (or similar)
```

**Related Files**:
- `src/plugins/youtube_channel_plugin.py` - Uses yt-dlp with FFmpeg

---

## Platform-Independent Issues

### 6. YouTube API Quota Limits

**Status**: Known limitation  
**Severity**: MEDIUM  
**Platform**: All platforms  

**Description**:
YouTube Data API v3 has strict quota limits (10,000 units/day by default). Search operations consume quota quickly.

**Quota Costs**:
- Search request: 100 units
- Video details: 1 unit each
- Channel details: 1 unit each

**Example**:
```
50 search results = 100 units (search) + 50 units (video details) = 150 units
Daily limit: 10,000 units ÷ 150 = ~66 searches/day
```

**Impact**:
- Limited daily scraping capacity
- Quota exhaustion stops scraping
- Requires multiple API keys for large-scale scraping

**Workaround**:
- Use **channel mode** with yt-dlp (no quota limits)
- Use **trending mode** with web scraping (no API required)
- Rotate multiple API keys
- Request quota increase from Google

**Related**:
- Issue #300: Keyword search will use API (quota limited)
- Channel mode uses yt-dlp (quota unlimited)

---

### 7. Rate Limiting and IP Blocking

**Status**: Known limitation  
**Severity**: LOW  
**Platform**: All platforms  

**Description**:
Aggressive scraping can trigger YouTube's rate limiting or temporary IP blocks.

**Symptoms**:
- HTTP 429 (Too Many Requests)
- HTTP 403 (Forbidden)
- CAPTCHA challenges
- Temporary scraping failures

**Mitigation**:
```python
# Add delays between requests
import time

for video in videos:
    scrape_video(video)
    time.sleep(2)  # 2 second delay
```

**Best Practices**:
- Limit concurrent requests (max 2-3)
- Add 1-2 second delays between requests
- Use residential proxies if available
- Rotate user agents
- Respect robots.txt

**Related Files**:
- `src/plugins/youtube_trending_plugin.py` - Web scraping
- `src/plugins/youtube_channel_plugin.py` - yt-dlp (handles rate limiting)

---

### 8. Incomplete Metadata for Some Shorts

**Status**: Known limitation  
**Severity**: LOW  
**Platform**: All platforms  

**Description**:
Some YouTube Shorts may have incomplete metadata (missing likes, comments, descriptions).

**Common Missing Data**:
- Like/dislike counts (disabled by creator)
- Comment counts (comments disabled)
- Subtitles/captions (not available)
- Hashtags/tags (not provided)

**Handling**:
```python
# Gracefully handle missing data
views = entry.get('view_count', 0)
likes = entry.get('like_count', None)  # May be None
comments = entry.get('comment_count', 0)

# Calculate metrics with fallbacks
engagement_rate = calculate_engagement(views, likes or 0, comments)
```

**Impact**:
- Scoring may be less accurate
- Some analytics unavailable
- Classification may be harder

**Workaround**:
- Use available metrics only
- Flag incomplete records for manual review
- Focus on high-quality channels with complete metadata

---

## Database Issues

### 9. SQLite Database Locking on Windows 🪟

**Status**: **MITIGATED** (WAL mode enabled)  
**Severity**: LOW  
**Platform**: Windows (more common than Unix)  

**Description**:
SQLite database locking can occur when multiple processes try to write simultaneously.

**Error Message**:
```
sqlite3.OperationalError: database is locked
```

**Solution** (Implemented):
Enable Write-Ahead Logging (WAL) mode for better concurrency:

```python
# src/core/database.py
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode
```

**Benefits of WAL Mode**:
- Readers don't block writers
- Writers don't block readers
- Better performance on NVMe SSD (Windows RTX 5090 workstation)
- Concurrent access support

**Verification**:
```python
# Check journal mode
import sqlite3
conn = sqlite3.connect('youtube_shorts.db')
cursor = conn.execute("PRAGMA journal_mode")
print(cursor.fetchone()[0])  # Should print: wal
```

**Related Files**:
- `src/core/database.py` - WAL mode configuration

---

### 10. Large Database Performance

**Status**: Expected behavior  
**Severity**: LOW  
**Platform**: All platforms  

**Description**:
Database queries slow down as the database grows (100K+ records).

**Symptoms**:
- Slow queries (>1 second)
- High disk I/O
- Increased memory usage

**Solution** (Implemented):
Proper indexing and query optimization:

```python
# Indexes on frequently queried columns
CREATE INDEX idx_source_source_id ON idea_inspirations(source, source_id);
CREATE INDEX idx_created_at ON idea_inspirations(created_at);
CREATE INDEX idx_score ON idea_inspirations(score DESC);
```

**Query Optimization**:
```python
# Use LIMIT for large result sets
SELECT * FROM idea_inspirations ORDER BY score DESC LIMIT 100;

# Use pagination
SELECT * FROM idea_inspirations ORDER BY created_at DESC LIMIT 100 OFFSET 100;
```

**Windows Optimizations**:
```python
# For Windows NVMe SSD (RTX 5090 workstation)
conn.execute("PRAGMA cache_size=-262144")  # 256MB cache
conn.execute("PRAGMA temp_store=MEMORY")   # Memory temp storage
```

**Related Files**:
- `src/core/database.py` - Database schema and optimizations

---

## Configuration Issues

### 11. Missing .env File

**Status**: User error  
**Severity**: LOW  
**Platform**: All platforms  

**Description**:
Module fails if `.env` file is missing or improperly configured.

**Error Message**:
```
FileNotFoundError: .env file not found
```

**Solution**:
Copy `.env.example` to `.env` and configure:

```powershell
# Windows
cd Sources\Content\Shorts\YouTube
copy .env.example .env
notepad .env
```

**Required Variables** (Minimum):
```env
DATABASE_PATH=.\youtube_shorts.db
YOUTUBE_MAX_RESULTS=50
```

**Optional Variables**:
```env
YOUTUBE_API_KEY=your_key_here  # Only for API mode
MAX_VIDEO_LENGTH=180
```

**Related Files**:
- `.env.example` - Template configuration
- `src/core/config.py` - Configuration loading

---

## Future Enhancements

### 12. GPU Acceleration Not Yet Implemented

**Status**: Planned (Phase 2)  
**Severity**: N/A (Future feature)  
**Platform**: Windows with NVIDIA RTX 5090  

**Description**:
The module doesn't yet utilize GPU acceleration for ML-based classification and scoring.

**Planned GPU Features**:
- Sentence transformers for semantic classification
- Thumbnail analysis with computer vision
- Batch processing optimization
- Real-time scoring with neural networks

**Target Platform**:
- NVIDIA RTX 5090 (32GB VRAM)
- CUDA 12.x
- PyTorch with GPU support

**Timeline**:
- Phase 2: Q3 2025
- Blocked by: Issue #009 (ML Enhanced Classification)

**Related Issues**:
- Issue #003: Batch Processing Optimization
- Issue #009: ML Enhanced Classification

---

## Workarounds Summary

| Issue | Severity | Workaround |
|-------|----------|------------|
| Keyword search not implemented | HIGH | Use channel or trending mode |
| Windows subprocess error | CRITICAL | Use `uvicorn_runner.py` to start backend |
| FFmpeg not found | MEDIUM | Install FFmpeg via Chocolatey or manually |
| YouTube API quota limits | MEDIUM | Use yt-dlp modes (channel/trending) |
| Database locked | LOW | WAL mode enabled (automatic) |
| Missing .env file | LOW | Copy `.env.example` to `.env` |

---

## Reporting New Issues

If you encounter an issue not listed here:

1. **Check existing issues**: Search GitHub Issues for similar problems
2. **Gather information**:
   - Platform (Windows version, Python version)
   - Error message (full traceback)
   - Steps to reproduce
   - Expected vs actual behavior
3. **Create issue**: Use GitHub issue template
4. **Tag appropriately**: Label as `bug`, `windows`, `documentation`, etc.

**Issue Template**: `.github/ISSUE_TEMPLATE/bug_report.md`

---

## Related Documentation

- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Detailed troubleshooting guide
- **[EXECUTION_FLOW.md](./EXECUTION_FLOW.md)** - Understanding module execution
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Module architecture
- **[Module README](../README.md)** - Quick start and usage

---

**Platform**: Windows 10/11 (Primary)  
**GPU**: NVIDIA RTX 5090  
**Python**: 3.10.x (Required)  
**Last Updated**: 2025-11-04

**Issue Tracking**: `_meta/issues/`  
**GitHub Issues**: https://github.com/Nomoos/PrismQ.T.Idea.Inspiration/issues
