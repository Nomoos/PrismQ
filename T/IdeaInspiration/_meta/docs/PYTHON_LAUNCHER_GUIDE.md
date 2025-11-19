# Python Launcher (`py`) - Quick Reference

**For Windows Users**

The Python Launcher (`py`) is the recommended way to work with PrismQ modules on Windows.

## Why Use `py`?

- ✅ **Multiple Versions**: Have Python 3.10 (for PrismQ/DaVinci) AND Python 3.11+ (for other projects)
- ✅ **Explicit Version**: Always use `py -3.10` to ensure correct version
- ✅ **Future-Proof**: Better compatibility as new Python versions are released
- ✅ **Official**: Recommended by Python.org for Windows users
- ✅ **Flexible**: `python` can be 3.10 default, `py` gives access to all versions

## Installation

The Python Launcher comes with Python 3.3+ installers for Windows:

1. Download [python-3.10.11-amd64.exe](https://www.python.org/downloads/release/python-31011/)
2. During installation, ensure "py launcher" is checked
3. Install Python 3.10 as your default (optional)

## Basic Usage

### Check Available Python Versions

```powershell
# List all installed Python versions
py --list

# Example output:
#  -3.12-64 *
#  -3.10-64
```

### Verify Python 3.10

```powershell
# Check Python 3.10 version
py -3.10 --version
# Output: Python 3.10.11
```

### Run Python Scripts

```powershell
# Run a script with Python 3.10
py -3.10 script.py

# Run Python 3.10 REPL
py -3.10
```

## PrismQ Workflows

### Setup Virtual Environment

```powershell
# Navigate to module directory
cd Classification

# Create virtual environment with Python 3.10
py -3.10 -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
py -3.10 -m pip install -e ".[dev]"
```

### Run Tests

```powershell
# With virtual environment activated
py -3.10 -m pytest

# Or directly
.\venv\Scripts\python.exe -m pytest
```

### Install Packages

```powershell
# Install to Python 3.10 specifically
py -3.10 -m pip install package-name

# Or with venv activated
pip install package-name
```

### Run Modules

```powershell
# Run a Python module with Python 3.10
py -3.10 -m module_name

# Example: Run pytest with Python 3.10
py -3.10 -m pytest tests/
```

## Setup Scripts Integration

All PrismQ setup scripts now support the `py` launcher:

### setup_all_envs.ps1

The script automatically detects and uses `py -3.10` if available:

```powershell
# Run setup script (it will use py -3.10 automatically)
.\_meta\_scripts\setup_all_envs.ps1
```

The script will:
1. Try `py -3.10` first (recommended)
2. Fall back to `python` if `py` not available
3. Warn if Python version is not 3.10.x

## Common Commands Reference

| Task | Command |
|------|---------|
| Check version | `py -3.10 --version` |
| List installed | `py --list` |
| Run script | `py -3.10 script.py` |
| Create venv | `py -3.10 -m venv venv` |
| Install package | `py -3.10 -m pip install pkg` |
| Run module | `py -3.10 -m module_name` |
| REPL | `py -3.10` |

## Configuration

### Set Default Python Version

Create `py.ini` in your home directory (`%LOCALAPPDATA%`):

```ini
[defaults]
python=3.10
```

Now `py` without version will use 3.10:

```powershell
py --version  # Uses 3.10 as default
```

### Per-Project Configuration

Add `.python-version` file (already in repository root):

```
3.10.11
```

Tools like `pyenv` and `asdf` will respect this file.

## Troubleshooting

### `py` command not found

**Solution**: Install or reinstall Python with the launcher option checked.

### Wrong Python version selected

```powershell
# Always specify version explicitly
py -3.10 script.py

# Check what py is using
py --list
```

### Virtual environment uses wrong Python

```powershell
# Delete and recreate with explicit version
Remove-Item -Recurse -Force venv
py -3.10 -m venv venv
```

### Multiple Python 3.10 versions

```powershell
# py will use the latest 3.10.x
py -3.10 --version

# Check all versions
py --list
```

## Best Practices

1. **Always use `py -3.10`** for PrismQ modules
2. **Use venv** for project isolation
3. **Check version** before running scripts: `py -3.10 --version`
4. **Update pip** in venv: `py -3.10 -m pip install --upgrade pip`
5. **Use `requirements.txt`** or `pyproject.toml` for dependencies

## Migration from `python` command

If you're currently using `python` directly:

**Before:**
```powershell
python -m venv venv
python -m pip install -e .
```

**After (with py launcher):**
```powershell
py -3.10 -m venv venv
py -3.10 -m pip install -e .
```

This ensures you're always using Python 3.10, even if other versions are installed.

## Additional Resources

- [Python Launcher Documentation](https://docs.python.org/3/using/windows.html#python-launcher-for-windows)
- [PEP 397 - Python launcher for Windows](https://peps.python.org/pep-0397/)
- [Python 3.10 Download](https://www.python.org/downloads/release/python-31011/)

---

**Last Updated**: 2025-11-04  
**Repository**: PrismQ.IdeaInspiration
