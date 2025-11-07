# Quick Start: YouTube Channel Download Tests

## TL;DR - One-Click Execution 🚀

**Easiest way - Double-click one of these scripts:**

### Windows
- **Double-click**: `Client\_meta\_scripts\run_youtube_tests.bat`

OR in PowerShell:
```powershell
.\Client\_meta\_scripts\run_youtube_tests.ps1
```

### Linux / macOS
```bash
./Client/_meta/_scripts/run_youtube_tests.sh
```

These scripts handle **everything automatically**:
- ✅ Virtual environment setup
- ✅ Dependency installation  
- ✅ Test validation
- ✅ Test execution
- ✅ Results display

## Alternative - Manual Execution

```bash
# Navigate to integration tests directory
cd Client/Backend/_meta/tests/integration

# Validate tests are ready
python validate_youtube_tests.py

# Run all YouTube tests with detailed output
python run_youtube_tests.py

# Or run with pytest directly
pytest test_youtube_channel_download.py -v -s
```

## What You Get

These tests demonstrate downloading YouTube channel content through the PrismQ Backend API with **extensive logging** (103+ log statements) perfect for:
- Debugging issues
- Understanding the workflow
- Agent analysis tasks
- Learning the system

## Test Overview

### 1. Main Workflow Test (Recommended First Run)
```bash
python run_youtube_tests.py workflow
```

**What it does**:
- Downloads 5 videos from @TED channel
- Shows step-by-step progress
- Captures all logs
- Analyzes results
- ~1-2 minutes runtime

**Sample Output**:
```
================================================================================
YOUTUBE CHANNEL DOWNLOAD TEST - START
================================================================================

[Step 1] Checking Backend health...
✓ Backend status: healthy

[Step 2] Discovering YouTube Shorts module...
✓ Found module: YouTube Shorts Source

[Step 5] Launching YouTube channel download...
✓ Module launched successfully
  - Run ID: abc123...

[Step 7] Retrieving execution logs...
✓ Retrieved 127 log entries

--------------------------------------------------------------------------------
EXECUTION LOGS (for Agent analysis)
--------------------------------------------------------------------------------
[  1] 2025-11-04T20:30:00 | INFO | Starting YouTube Shorts scraper...
[  2] 2025-11-04T20:30:01 | INFO | Channel: @TED
... (all execution logs displayed)
--------------------------------------------------------------------------------

✓ TEST PASSED - Channel download completed successfully
```

### 2. Error Handling Test
```bash
python run_youtube_tests.py error
```
Tests invalid inputs and error scenarios.

### 3. Log Streaming Test
```bash
python run_youtube_tests.py streaming
```
Tests real-time log polling.

### 4. Configuration Test
```bash
python run_youtube_tests.py config
```
Tests saving/loading YouTube configurations.

## Prerequisites

### Install Python Dependencies
```bash
pip install pytest pytest-asyncio httpx
```

### Optional: Install yt-dlp (for actual downloads)
```bash
pip install yt-dlp
```

**Note**: Tests will run without yt-dlp, but won't download real data.

## Files Overview

```
integration/
├── test_youtube_channel_download.py    # Main test file (4 tests)
├── run_youtube_tests.py                # Helper script to run tests
├── validate_youtube_tests.py           # Validate test structure
├── README_YOUTUBE_TESTS.md             # Detailed documentation
└── QUICK_START.md                      # This file
```

## Validation Before Running

Always validate first to ensure everything is ready:

```bash
python validate_youtube_tests.py
```

Expected output:
```
✓ Python syntax is valid
✓ Found 4 test functions
✓ Found 103 print statements (for detailed logging)
✓ Test file is valid
✓ Ready for execution
```

## Common Issues

### "pytest not found"
```bash
pip install pytest pytest-asyncio
```

### "httpx not found"
```bash
pip install httpx
```

### "Module not found: src.main"
Make sure you're in the Backend directory:
```bash
cd Client/Backend
pytest _meta/tests/integration/test_youtube_channel_download.py -v -s
```

### Tests timeout or hang
- Check if Backend can access YouTube
- Increase timeout in test (default: 5 minutes)
- Check network connectivity

### No logs generated
- Tests may have failed early
- Check Backend configuration
- Verify module exists in configs/modules.json

## Understanding the Output

### Log Levels
- **INFO**: Normal operations
- **WARNING**: Non-critical issues
- **ERROR**: Problems that don't stop execution
- **CRITICAL**: Fatal errors

### Status Flow
```
queued → running → completed/failed/cancelled
```

### Log Indicators
The test looks for these patterns in logs:
- ✓ Channel detected
- ✓ Video processing
- ✓ Metadata extracted
- ✓ Database saved
- ✗ Errors found

## Example: Running Your First Test

```bash
# 1. Navigate to Backend directory
cd /path/to/PrismQ.IdeaInspiration/Client/Backend

# 2. Validate tests
python _meta/tests/integration/validate_youtube_tests.py

# 3. Run main workflow test with full output
pytest _meta/tests/integration/test_youtube_channel_download.py::test_youtube_channel_download_workflow -v -s

# 4. Watch the detailed logs scroll by showing:
#    - Backend health check
#    - Module discovery
#    - Configuration
#    - Download progress
#    - Log analysis
#    - Results
```

## What Makes These Tests Special

1. **Extensive Logging**: 103 print statements show every step
2. **Agent-Friendly**: Structured output for automated analysis
3. **Real Integration**: Tests actual Backend API, not mocks
4. **Multiple Scenarios**: Success, failure, configuration, streaming
5. **Self-Documenting**: Output explains what's happening
6. **Flexible**: Works with or without yt-dlp installed

## Use Cases

### For Debugging
Run tests to see detailed execution flow and identify issues.

### For Learning
Read the test output to understand how the system works.

### For Agents
Parse the structured log output for automated analysis.

### For Development
Verify changes don't break YouTube integration.

## Next Steps

1. ✓ Run validation script
2. ✓ Run main workflow test
3. ✓ Review the logs
4. ✓ Try other test scenarios
5. ✓ Read full documentation (README_YOUTUBE_TESTS.md)
6. ✓ Adapt tests for your needs

## Getting Help

- **Detailed docs**: `README_YOUTUBE_TESTS.md`
- **Implementation**: See `_meta/docs/IMPLEMENTATION_SUMMARY.md`
- **Test validation**: Run `validate_youtube_tests.py`
- **GitHub issues**: Report problems on the repository

## Quick Reference

| Command | Description |
|---------|-------------|
| `python validate_youtube_tests.py` | Check test structure |
| `python run_youtube_tests.py` | Run all tests |
| `python run_youtube_tests.py workflow` | Run main test |
| `python run_youtube_tests.py error` | Run error tests |
| `pytest test_youtube_channel_download.py -v -s` | Run with pytest |

---

**Ready to test?** Start with: `python validate_youtube_tests.py`
