# Python Configuration Standardization

## Overview

As of Issue #206, all PrismQ modules now use standardized `pyproject.toml` configuration files following modern Python packaging standards (PEP 518, 621).

## Standard Template

All modules follow this standardized configuration:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "module-name"
version = "X.Y.Z"
description = "Module description"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "Proprietary"}
authors = [
    {name = "PrismQ", email = "info@prismq.example"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    # Production dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = [
    "--verbose",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__pycache__/*", "*/venv/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
show_missing = true

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N"]
ignore = []

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Module Status

### ✅ Standardized Modules

| Module | Configuration | Status |
|--------|---------------|--------|
| **ConfigLoad** | `pyproject.toml` only | ✅ Standardized |
| **Model** | `pyproject.toml` only | ✅ Standardized (setup.py removed) |
| **Classification** | `pyproject.toml` only | ✅ Standardized (setup.py removed) |
| **Scoring** | `pyproject.toml` only | ✅ Standardized |

### 📦 Package Structure

Different modules use different package structures:

- **ConfigLoad**: Direct module files (`config.py`, `logging_config.py`)
- **Model**: Direct module files (`idea_inspiration.py`, `config_manager.py`, etc.)
- **Classification**: `src/classification/` package structure
- **Scoring**: `src/` package structure

## Installation

All modules can now be installed using modern pip commands:

### Development Installation

Install a module in editable mode with all development dependencies:

```bash
cd ModuleName
pip install -e ".[dev]"
```

### Production Installation

Install a module with only production dependencies:

```bash
cd ModuleName
pip install -e .
```

### Quick Install (Without Build Isolation)

For environments where network is slow or build dependencies are already installed:

```bash
cd ModuleName
pip install --no-build-isolation -e .
```

## Tool Configuration

All tools are now configured in `pyproject.toml`:

### pytest
- Test discovery in `tests/` or `_meta/tests/` directories
- Code coverage enabled by default
- HTML and terminal coverage reports

### ruff
- PEP 8 compliance
- Line length: 100 characters
- Target: Python 3.10+

### mypy
- Type checking enabled
- Python 3.10 baseline
- Strict type checking (where configured)

### coverage
- Source coverage from module source
- Excludes test files and cache directories
- Shows missing lines in reports

## Migration Summary

### Changes Made

1. **Created `pyproject.toml`** for ConfigLoad (previously only had `requirements.txt`)
2. **Updated `pyproject.toml`** for Model, Classification, and Scoring:
   - Standardized build-system requirements
   - Updated classifiers for Python 3.10-3.12
   - Replaced `black` and `flake8` with `ruff`
   - Standardized pytest and coverage configurations
   - Unified tool configuration format
3. **Removed `setup.py`** from Model and Classification (no longer needed)
4. **Kept `requirements.txt`** files for backward compatibility

### Benefits

- ✅ **Modern Python Standards**: PEP 518, 621 compliant
- ✅ **Single Source of Truth**: All configuration in `pyproject.toml`
- ✅ **Consistent Tool Configuration**: Unified across all modules
- ✅ **Better IDE Support**: Modern IDEs understand `pyproject.toml`
- ✅ **Simpler Installation**: `pip install -e .` works everywhere
- ✅ **Easier Dependency Management**: Clear separation of prod/dev deps

## Testing

All modules were tested with:

```bash
# Install with dev dependencies
cd ModuleName
pip install --no-build-isolation -e ".[dev]"

# Run tests
pytest

# Results:
# - ConfigLoad: 37 tests passed (87% coverage)
# - Model: 103 tests passed (74% coverage)
# - Classification: 85 tests passed (18 failures - pre-existing issues)
# - Scoring: 57 tests passed (67% coverage)
```

## Future Considerations

### requirements.txt Files

The `requirements.txt` files are currently kept for backward compatibility. In the future, consider:

- **Option A**: Keep for compatibility with older tools
- **Option B**: Remove and use only `pyproject.toml` (modern approach)

Current recommendation: Keep both until all CI/CD pipelines are updated.

### Python Version Support

All modules now target Python 3.10+ as the baseline. Consider:

- Python 3.8-3.9 are no longer officially supported
- Focus on 3.10, 3.11, 3.12
- Future: Add Python 3.13 when stable

## References

- [PEP 518](https://peps.python.org/pep-0518/) - Build system requirements
- [PEP 621](https://peps.python.org/pep-0621/) - Project metadata in pyproject.toml
- [Setuptools Documentation](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html)
- [Issue #206](../issues/done/206-standardize-python-configuration.md)
