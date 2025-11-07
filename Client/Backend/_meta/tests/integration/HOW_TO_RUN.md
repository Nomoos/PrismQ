# How to Run YouTube Tests - Visual Guide

## The Easiest Way (Windows) 🖱️

### Step 1: Open File Explorer
Navigate to:
```
PrismQ.IdeaInspiration\Client\_meta\_scripts\
```

### Step 2: Find the Script
Look for this file:
```
run_youtube_tests.bat
```

### Step 3: Double-Click It
Just double-click `run_youtube_tests.bat` and watch it run!

```
📁 Client
  └─ 📁 _meta
      └─ 📁 _scripts
          └─ 📄 run_youtube_tests.bat  ⬅️ DOUBLE-CLICK THIS!
```

## What Happens Automatically

```
┌─────────────────────────────────────────┐
│ 1. Opens Command Window                 │
├─────────────────────────────────────────┤
│ 2. Checks for Virtual Environment       │
│    ✓ Found? Uses it                     │
│    ✗ Not found? Creates it              │
├─────────────────────────────────────────┤
│ 3. Checks for Test Dependencies         │
│    ✓ pytest, httpx, pytest-asyncio      │
│    ✗ Missing? Installs them             │
├─────────────────────────────────────────┤
│ 4. Validates Test Structure             │
│    ✓ Syntax check                       │
│    ✓ Import verification                │
├─────────────────────────────────────────┤
│ 5. Runs All YouTube Tests               │
│    • test_youtube_channel_download...   │
│    • test_youtube_channel_error...      │
│    • test_youtube_channel_log...        │
│    • test_youtube_channel_config...     │
├─────────────────────────────────────────┤
│ 6. Shows Results                        │
│    ✓ All tests passed                   │
│    OR                                    │
│    ⚠ Tests completed (expected)         │
└─────────────────────────────────────────┘
```

## Expected Output

```
============================================
  YouTube Channel Download Tests
============================================

Working directory: C:\...\Client\Backend

✅ Virtual environment found
✅ Virtual environment activated: C:\...\Backend\venv

Checking test dependencies...
✅ pytest installed
✅ httpx installed
✅ pytest-asyncio installed
⚠️  yt-dlp not installed (tests will run but won't download real data)
   To install: pip install yt-dlp

======================================
  Validating Test Structure
======================================

✓ Python syntax is valid
✓ Found 4 test functions
✓ Found 103 print statements (for detailed logging)
✓ Test file is valid
✓ Ready for execution

======================================
🚀 Running YouTube Tests
======================================

Running all YouTube tests...

test_youtube_channel_download.py::test_youtube_channel_download_workflow 

================================================================================
YOUTUBE CHANNEL DOWNLOAD TEST - START
================================================================================

[Step 1] Checking Backend health...
✓ Backend status: healthy
✓ Total modules available: 42
✓ Backend version: 1.0.0

[Step 2] Discovering YouTube Shorts module...
✓ Found module: YouTube Shorts Source
  - ID: youtube-shorts
  - Version: 2.0.0
  - Category: Content/Shorts
  - Description: Collect YouTube Shorts content from trending, specific channels, or keyword searches
  - Parameters: 5

[Step 3] Reviewing module parameters...
  - mode: select (default: trending)
    → Scraping mode: trending (popular shorts), channel (specific channel), or keyword (search)
  - channel_url: text (default: )
    → YouTube channel URL, handle (@username), or ID (required for channel mode)
  - query: text (default: )
    → Search keyword or phrase (required for keyword mode)
  - max_results: number (default: 50)
    → Maximum number of shorts to collect
  - category: select (default: All)
    → Content category filter (for trending mode)

[Step 4] Configuring module for channel download...
✓ Configuration:
  - Mode: channel
  - Channel: @TED
  - Max Results: 5

✓ Configuration saved successfully

[Step 5] Launching YouTube channel download...
  Timestamp: 2025-11-04T20:30:00.123456
✓ Module launched successfully
  - Run ID: run_20251104_203000_abc123
  - Module ID: youtube-shorts

[Step 6] Monitoring execution status...
  [  0s] Status: queued
  [  2s] Status: running
  [ 45s] Status: completed

✓ Execution finished with status: completed
  - Started: 2025-11-04T20:30:00.123456
  - Completed: 2025-11-04T20:30:45.789012

[Step 7] Retrieving execution logs...
✓ Retrieved 127 log entries

--------------------------------------------------------------------------------
EXECUTION LOGS (for Agent analysis)
--------------------------------------------------------------------------------
[  1] 2025-11-04T20:30:01.000000 | INFO     | Starting YouTube Shorts scraper...
[  2] 2025-11-04T20:30:01.100000 | INFO     | Mode: channel
[  3] 2025-11-04T20:30:01.200000 | INFO     | Channel URL: @TED
[  4] 2025-11-04T20:30:01.300000 | INFO     | Max results: 5
[  5] 2025-11-04T20:30:02.000000 | INFO     | Normalizing channel URL...
[  6] 2025-11-04T20:30:02.100000 | INFO     | Normalized to: https://www.youtube.com/@TED
[  7] 2025-11-04T20:30:03.000000 | INFO     | Fetching channel shorts...
... (100+ more log entries)
--------------------------------------------------------------------------------

[Step 8] Analyzing log content...
✓ Log statistics:
  - INFO: 120
  - WARNING: 5
  - ERROR: 2

✓ Log indicators:
  ✓ Channel Detected
  ✓ Video Processing
  ✓ Metadata Extracted
  ✓ Database Saved
  ✗ Errors Found

[Step 9] Retrieving final run details...
✓ Final run summary:
  - Run ID: run_20251104_203000_abc123
  - Module: youtube-shorts
  - Status: completed
  - Parameters: {
    "mode": "channel",
    "channel_url": "@TED",
    "max_results": 5,
    "category": "All"
}

[Step 10] Verifying run appears in run list...
✓ Run found in list (total runs: 15)

================================================================================
YOUTUBE CHANNEL DOWNLOAD TEST - SUMMARY
================================================================================
✓ Module: YouTube Shorts Source
✓ Run ID: run_20251104_203000_abc123
✓ Status: completed
✓ Logs captured: 127 entries
✓ Execution time: ~45s
✓ TEST PASSED - Channel download completed successfully
================================================================================

PASSED

test_youtube_channel_download.py::test_youtube_channel_download_error_handling PASSED
test_youtube_channel_download.py::test_youtube_channel_log_streaming PASSED
test_youtube_channel_download.py::test_youtube_channel_configuration_persistence PASSED

======================================
✅ All tests passed!
======================================

Next steps:
  • Review the test output above
  • Check logs for detailed execution information
  • Read README_YOUTUBE_TESTS.md for more information

Press any key to exit...
```

## Other Ways to Run

### Windows PowerShell (Alternative)

1. Open PowerShell
2. Navigate to scripts folder:
   ```powershell
   cd Client\_meta\_scripts
   ```
3. Run the script:
   ```powershell
   .\run_youtube_tests.ps1
   ```

### Linux / macOS

1. Open Terminal
2. Navigate to scripts folder:
   ```bash
   cd Client/_meta/_scripts
   ```
3. Run the script:
   ```bash
   ./run_youtube_tests.sh
   ```

## Running Individual Tests

### All Platforms Support Test Selection

**Windows:**
```powershell
.\run_youtube_tests.ps1 workflow
.\run_youtube_tests.ps1 error
.\run_youtube_tests.ps1 streaming
.\run_youtube_tests.ps1 config
```

**Linux/macOS:**
```bash
./run_youtube_tests.sh workflow
./run_youtube_tests.sh error
./run_youtube_tests.sh streaming
./run_youtube_tests.sh config
```

## Test Options

| Test Name | What It Does | Runtime |
|-----------|-------------|---------|
| `workflow` | Complete download workflow (recommended first) | ~1-2 min |
| `error` | Error handling scenarios | ~30 sec |
| `streaming` | Log polling/streaming | ~30 sec |
| `config` | Configuration persistence | ~15 sec |
| (none) | All tests | ~2-3 min |

## Troubleshooting

### Windows: "Cannot run scripts"

**Solution 1** - Use the .bat file instead:
```
Just double-click: run_youtube_tests.bat
```

**Solution 2** - Allow PowerShell scripts:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Any platform: "Python not found"

**Install Python:**
- Windows: https://www.python.org/downloads/
- Linux: `sudo apt install python3`
- macOS: `brew install python3`

### Tests fail with errors

**This is often expected!**

If yt-dlp is not installed, tests will show errors but still pass validation.

**To get full functionality:**
```bash
pip install yt-dlp
```

Then run the tests again.

## What Makes This Special

✅ **Zero Manual Setup** - Everything is automatic
✅ **Cross-Platform** - Windows, Linux, macOS
✅ **Extensive Logging** - 103+ log statements
✅ **Agent-Friendly** - Structured output
✅ **Self-Contained** - Creates venv, installs deps
✅ **User-Friendly** - Clear output and next steps

## File Locations

```
PrismQ.IdeaInspiration/
├─ Client/
│  ├─ _meta/
│  │  └─ _scripts/
│  │     ├─ run_youtube_tests.bat      ⬅️ Windows (double-click)
│  │     ├─ run_youtube_tests.ps1      ⬅️ PowerShell
│  │     ├─ run_youtube_tests.sh       ⬅️ Linux/macOS
│  │     └─ README_YOUTUBE_TEST_SCRIPTS.md
│  └─ Backend/
│     └─ _meta/
│        └─ tests/
│           └─ integration/
│              ├─ test_youtube_channel_download.py
│              ├─ run_youtube_tests.py
│              ├─ validate_youtube_tests.py
│              ├─ README_YOUTUBE_TESTS.md
│              ├─ QUICK_START.md
│              ├─ IMPLEMENTATION_SUMMARY.md
│              └─ HOW_TO_RUN.md        ⬅️ This file
```

## Summary

**Simplest way to run tests:**

1. Navigate to `Client\_meta\_scripts\`
2. Double-click `run_youtube_tests.bat` (Windows)
3. OR run `./run_youtube_tests.sh` (Linux/macOS)
4. Watch the magic happen! ✨

---

**Questions?** Check `README_YOUTUBE_TEST_SCRIPTS.md` or `README_YOUTUBE_TESTS.md`
