# Python Version Decision: 3.10.x Only

**Decision Date**: 2025-11-04  
**Status**: ✅ Implemented

## Summary

All PrismQ.IdeaInspiration modules are now restricted to **Python 3.10.x only** for compatibility with DaVinci Resolve and the Client module.

## Problem Statement

The user needs to run PrismQ.IdeaInspiration modules on the same PC as DaVinci Resolve. However:

1. **DaVinci Resolve** works best with Python 3.10
2. **Client module** has compatibility issues with Python 3.11+
3. Python 3.11 and 3.12 cause issues with DaVinci Resolve

## Research Findings

### DaVinci Resolve Compatibility

From community research and official documentation:

- **Official Support**: DaVinci Resolve 19+ supports Python 3.6 and 2.7 (64-bit)
- **Community Experience**: Python 3.10 works reliably with Resolve 18+
- **Known Issues**: Python 3.11+ can cause problems
  - Users reported: "After uninstalling Python 3.12.1, the issue in Resolve was resolved"
  - Recommendation: "Use Python 3.10 for Resolve 18, 3.11 may have issues with latest Resolve"

### Client Module Compatibility

- The Client module cannot work with newer Python versions
- Missing modules in Python 3.11+

## Decision

**Restrict all modules to Python 3.10.x only**

### Implementation

```toml
requires-python = ">=3.10,<3.11"
```

This ensures:
- ✅ Compatible with DaVinci Resolve
- ✅ Compatible with Client module
- ✅ Works on the same PC without conflicts
- ✅ Clear, enforced requirement (pip will reject Python 3.11+)

### Recommended Version

**Python 3.10.11** (latest 3.10.x patch release)

Download: [python-3.10.11-amd64.exe](https://www.python.org/downloads/release/python-31011/)

### Windows Python Launcher (`py`) - Recommended

For better version management on Windows, use the **Python Launcher (`py`)**:

```powershell
# Check if Python 3.10 is installed
py -3.10 --version

# Create virtual environment with Python 3.10
py -3.10 -m venv venv

# Install package with Python 3.10
py -3.10 -m pip install -e .
```

**Benefits of using `py` launcher:**
- ✅ Multiple Python versions can coexist (3.10 for PrismQ, 3.11+ for other projects)
- ✅ Explicit version selection with `py -3.10`
- ✅ Better compatibility with future Python versions
- ✅ `python` command can be aliased to 3.10, while `py` provides access to all versions
- ✅ Recommended by Python.org for Windows users

**Installation:**
- Comes with Python 3.3+ installers for Windows
- Make sure to check "py launcher" during Python installation

## Changes Made

### 1. Configuration Files (41 files)

Updated all `pyproject.toml` files:
- Classification
- Client/Backend
- ConfigLoad
- Model
- Scoring
- Sources (all 36 source modules)

Changes:
- `requires-python = ">=3.10,<3.11"` (was `>=3.10`)
- Removed Python 3.11 and 3.12 from classifiers
- mypy `python_version = "3.10"` (already correct)
- ruff/black `target-version = "py310"` (already correct)

### 2. Documentation (3 files)

- **README.md**: Added prominent Python version requirement section
- **SETUP.md**: Updated prerequisites with specific version requirement
- **PYTHON_PACKAGING_STANDARD.md**: Updated standard template and rationale

### 3. Version Control

- Created `.python-version` file with `3.10.11`
- Used by pyenv, asdf, and other version managers

## Verification

### Test Configuration

```bash
# Verify Python version specification
grep -r "requires-python" */pyproject.toml

# All should show: requires-python = ">=3.10,<3.11"
```

### Installation Test

When users try to install with wrong Python version:

```bash
# With Python 3.12 (will fail)
pip install -e .
# ERROR: Package requires a different Python: 3.12.x not in '>=3.10,<3.11'

# With Python 3.10.11 (will succeed)
pip install -e .
# Successfully installed...
```

## Future Considerations

### When to Update

Consider supporting newer Python versions when:

1. **DaVinci Resolve** officially supports Python 3.11+
2. **Client module** dependencies are compatible with Python 3.11+
3. **Testing confirms** no compatibility issues

### Migration Path

If/when we support Python 3.11:

1. Update `requires-python = ">=3.10,<3.12"`
2. Add Python 3.11 classifier
3. Test thoroughly with DaVinci Resolve
4. Update documentation

## References

### External Resources

- [DaVinci Resolve Scripting API](https://gist.github.com/X-Raym/2f2bf453fc481b9cca624d7ca0e19de8)
- [PyDavinci Documentation](https://pedrolabonia.github.io/pydavinci/)
- [Blackmagic Forum: Python Environments](https://forum.blackmagicdesign.com/viewtopic.php?f=12&t=215336)
- [Python 3.10 Downloads](https://www.python.org/downloads/release/python-31011/)

### Internal Documentation

- [Python Packaging Standard](./_meta/docs/PYTHON_PACKAGING_STANDARD.md)
- [Setup Guide](./_meta/docs/SETUP.md)
- [Known Issues](./_meta/issues/KNOWN_ISSUES.md)

## Impact

### Positive

- ✅ **Compatibility**: Works with DaVinci Resolve out of the box
- ✅ **Stability**: Python 3.10 is mature and stable
- ✅ **Clear Requirements**: No ambiguity about supported versions
- ✅ **Enforced**: pip will prevent installation with wrong version

### Considerations

- ⚠️ **Limited to 3.10**: Cannot use Python 3.11+ features
- ⚠️ **Future Updates**: Will need manual update when moving to 3.11+
- ℹ️ **Ecosystem**: Most libraries still support 3.10

## Conclusion

Restricting to Python 3.10.x is the **correct decision** for this project because:

1. Primary use case requires DaVinci Resolve compatibility
2. Client module has compatibility constraints
3. Python 3.10 is stable, well-supported, and feature-complete
4. Clear version constraint prevents user confusion

---

**Author**: GitHub Copilot  
**Approved**: PrismQ Team  
**Last Updated**: 2025-11-04
