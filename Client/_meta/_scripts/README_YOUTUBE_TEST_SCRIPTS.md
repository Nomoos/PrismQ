# One-Click Test Runner Scripts

## Quick Start - Choose Your Platform

### Windows (Recommended Method)

**Double-click** `run_youtube_tests.bat` 

OR in PowerShell:
```powershell
.\run_youtube_tests.ps1
```

### Linux / macOS

```bash
./run_youtube_tests.sh
```

## What These Scripts Do

These scripts provide **one-click** execution of YouTube channel download tests:

1. ✅ Check/create Python virtual environment
2. ✅ Activate virtual environment automatically
3. ✅ Install missing test dependencies (pytest, httpx, pytest-asyncio)
4. ✅ Validate test structure
5. ✅ Run all YouTube integration tests
6. ✅ Display comprehensive output
7. ✅ Show results and next steps

## Files

### `run_youtube_tests.bat` (Windows)
- **Platform**: Windows (all versions)
- **Usage**: Double-click to run
- **What it does**: Launches PowerShell script
- **Requirements**: Windows with PowerShell

### `run_youtube_tests.ps1` (Windows PowerShell)
- **Platform**: Windows
- **Usage**: `.\run_youtube_tests.ps1`
- **What it does**: Main test runner with full automation
- **Requirements**: PowerShell 5.0+

### `run_youtube_tests.sh` (Linux/macOS)
- **Platform**: Linux, macOS, WSL
- **Usage**: `./run_youtube_tests.sh`
- **What it does**: Bash version of test runner
- **Requirements**: Bash shell

## Running Specific Tests

All scripts support running individual tests:

### Windows
```powershell
.\run_youtube_tests.ps1 workflow
.\run_youtube_tests.ps1 error
.\run_youtube_tests.ps1 streaming
.\run_youtube_tests.ps1 config
```

### Linux/macOS
```bash
./run_youtube_tests.sh workflow
./run_youtube_tests.sh error
./run_youtube_tests.sh streaming
./run_youtube_tests.sh config
```

## What Gets Installed

The scripts automatically install these dependencies if missing:

1. **pytest** - Test framework
2. **pytest-asyncio** - Async test support
3. **httpx** - HTTP client for API testing

**Optional**: 
- **yt-dlp** - For actual YouTube downloads (tests work without it)

## Sample Output

```
======================================
  YouTube Channel Download Tests
======================================

Working directory: C:\...\Client\Backend

✅ Virtual environment found
✅ Virtual environment activated

Checking test dependencies...
✅ pytest installed
✅ httpx installed
✅ pytest-asyncio installed
⚠️  yt-dlp not installed (tests will run but won't download real data)

======================================
  Validating Test Structure
======================================

✓ Python syntax is valid
✓ Found 4 test functions
✓ Found 103 print statements (for detailed logging)
✓ Test file is valid

======================================
🚀 Running YouTube Tests
======================================

Running all YouTube tests...

test_youtube_channel_download.py::test_youtube_channel_download_workflow PASSED
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
```

## Troubleshooting

### Windows: "Running scripts is disabled"

If you get an execution policy error:

```powershell
# Option 1: Run with bypass (one time)
powershell -ExecutionPolicy Bypass -File run_youtube_tests.ps1

# Option 2: Change policy permanently (requires admin)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux/macOS: "Permission denied"

Make the script executable:
```bash
chmod +x run_youtube_tests.sh
./run_youtube_tests.sh
```

### "Python not found"

Install Python 3.10 or higher:
- **Windows**: https://www.python.org/downloads/
- **Linux**: `sudo apt install python3` or equivalent
- **macOS**: `brew install python3`

### Tests fail with "ModuleNotFoundError"

The scripts should install dependencies automatically, but you can install manually:

```bash
# Activate venv first
# Windows
.\Backend\venv\Scripts\Activate.ps1

# Linux/macOS
source Backend/venv/bin/activate

# Install dependencies
pip install pytest pytest-asyncio httpx
```

## Script Features

### Auto Virtual Environment
- Creates venv if not exists
- Activates automatically
- Verifies activation

### Dependency Management
- Checks for required packages
- Installs missing dependencies
- Reports optional packages (yt-dlp)

### Validation
- Runs test structure validation
- Checks syntax before running
- Verifies imports and decorators

### Error Handling
- Clear error messages
- Helpful suggestions
- Graceful failure

### Output
- Colored output (where supported)
- Progress indicators
- Detailed logs
- Next steps guidance

## Advanced Usage

### Custom pytest Options

Edit the script and modify the pytest command:

```powershell
# In run_youtube_tests.ps1, line ~185
python -m pytest $TestPath -v -s --tb=short --color=yes --maxfail=1
```

### Run with Coverage

```powershell
python -m pytest _meta\tests\integration\test_youtube_channel_download.py --cov=src --cov-report=html
```

### Run in CI/CD

For automated environments (no pause at end):

```bash
# Remove the pause/ReadKey commands
# Or set environment variable
export CI=true
./run_youtube_tests.sh
```

## Integration with IDE

### Visual Studio Code

1. Open `Client/_meta/_scripts/run_youtube_tests.ps1`
2. Press F5 to run in integrated terminal
3. Or use VS Code's Run and Debug

### PyCharm

1. Right-click `run_youtube_tests.sh` or `run_youtube_tests.ps1`
2. Select "Run"
3. Output appears in Run window

### Windows Terminal

Add as a custom profile:

```json
{
  "name": "YouTube Tests",
  "commandline": "powershell.exe -ExecutionPolicy Bypass -File C:\\...\\run_youtube_tests.ps1",
  "startingDirectory": "C:\\...\\Client\\_meta\\_scripts"
}
```

## Related Files

- Test file: `Backend/_meta/tests/integration/test_youtube_channel_download.py`
- Documentation: `Backend/_meta/tests/integration/README_YOUTUBE_TESTS.md`
- Quick start: `Backend/_meta/tests/integration/QUICK_START.md`
- Validation: `Backend/_meta/tests/integration/validate_youtube_tests.py`

## Platform Compatibility

| Platform | .bat | .ps1 | .sh |
|----------|------|------|-----|
| Windows 10/11 | ✅ | ✅ | ❌ |
| Windows WSL | ❌ | ❌ | ✅ |
| Linux | ❌ | ❌ | ✅ |
| macOS | ❌ | ❌ | ✅ |

## Support

For issues with the scripts:
1. Check this README
2. Review error messages
3. Try manual execution steps
4. Check main test documentation
5. Open GitHub issue

---

**Last Updated**: 2025-11-04  
**Scripts**: 3 files (Windows .bat, PowerShell .ps1, Bash .sh)  
**Purpose**: One-click YouTube test execution
