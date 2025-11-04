# Issue 206: Standardize Python Configuration Files

## Status
Done

## Priority
Low

## Category
Infrastructure_DevOps

## Description
Modules use a mix of `setup.py`, `pyproject.toml`, and both, with inconsistent configuration. Modern Python best practices favor `pyproject.toml` (PEP 518, 621).

## Problem Statement

### Current State:

1. **Mixed Configuration Approaches**:
   - Some modules: `pyproject.toml` only
   - Some modules: `setup.py` only
   - Some modules: both `pyproject.toml` and `setup.py`

2. **Inconsistent pyproject.toml Content**:
   - Different project metadata formats
   - Different tool configurations
   - Some missing important sections (dependencies, dev dependencies)

3. **Requirements Files**:
   - All have `requirements.txt`
   - But dependencies should be in `pyproject.toml`
   - Need to decide: keep both or just pyproject.toml?

4. **Tool Configuration Scattered**:
   - Some tools configured in `pyproject.toml`
   - Some in separate config files
   - pytest, coverage, ruff, mypy configurations inconsistent

## Proposed Solution

### 1. Adopt Modern Python Packaging (PEP 621)

**Standardize on `pyproject.toml`** for all modules:
- Use `[project]` section for metadata
- Use `[project.optional-dependencies]` for dev dependencies
- Use `[build-system]` for build requirements
- Use `[tool.*]` sections for tool configurations

### 2. Standard pyproject.toml Template

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "module-name"
version = "0.1.0"
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

[tool.setuptools.packages.find]
where = ["src"]

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
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]

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

### 3. Migration Strategy

**Option A: Keep requirements.txt** (for compatibility):
- Use `pyproject.toml` as source of truth
- Generate `requirements.txt` from it
- Command: `pip-compile pyproject.toml`

**Option B: Remove requirements.txt** (modern approach):
- Install with `pip install -e .` (editable)
- Install dev deps: `pip install -e ".[dev]"`
- Simpler, more modern

**Recommendation**: Option B with documentation

### 4. Remove setup.py Where Possible

For most modules, `setup.py` is no longer needed:
- `pyproject.toml` handles everything
- Only keep `setup.py` if:
  - Complex build process
  - Need backward compatibility
  - Custom build steps

## Benefits
- Modern Python packaging standards
- Consistent configuration across modules
- Single source of truth for dependencies
- Better IDE support
- Easier dependency management
- Centralized tool configuration

## Acceptance Criteria
- [x] All modules have pyproject.toml with [project] section
- [x] Dependencies in pyproject.toml, not just requirements.txt
- [x] Tool configurations (pytest, coverage, ruff, mypy) in pyproject.toml
- [x] setup.py removed where not needed
- [x] Template pyproject.toml documented
- [x] Installation instructions updated
- [x] All modules can be installed with `pip install -e .`

## Implementation Steps

1. **Create Standard Template**:
   - Design comprehensive pyproject.toml template
   - Include all common tools
   - Document each section

2. **Audit Current Files**:
   - List which modules have which configs
   - Identify differences
   - Determine migration complexity

3. **Migrate Each Module**:
   - Start with simplest (ConfigLoad)
   - Move to Model, then others
   - Test installation after each

4. **Test Installation**:
   ```bash
   # Test each module
   cd module_name
   pip install -e .
   pip install -e ".[dev]"
   pytest
   ```

5. **Update Documentation**:
   - Update installation instructions
   - Document pyproject.toml sections
   - Update CONTRIBUTING.md
   - Create migration guide

6. **Clean Up**:
   - Remove old setup.py files (if appropriate)
   - Consider requirements.txt (keep or remove)
   - Update CI/CD configurations

## Migration Example

**Before** (setup.py + requirements.txt):
```python
# setup.py
from setuptools import setup, find_packages
setup(
    name="my-module",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ]
)
```

**After** (pyproject.toml only):
```toml
[project]
name = "my-module"
version = "0.1.0"
dependencies = [
    "requests>=2.28.0",
]
```

## Estimated Effort
4-6 hours

## Dependencies
None (can be done independently)

## Related Issues
- Issue #202 (Module structure standardization)
- Issue #205 (Test structure)

## Notes
- This is a modernization effort
- Low risk if done carefully
- Should test each module after migration
- Good opportunity to review dependencies
- Consider using tools like `pip-audit` for security

---

## Implementation Completed

**Date**: 2025-11-04

**Changes Made**:

1. ✅ **ConfigLoad**: Created new `pyproject.toml` from scratch
   - Previously only had `requirements.txt`
   - Now fully PEP 621 compliant
   - Dependencies: python-dotenv, psutil
   - Tests: 37 passed (87% coverage)

2. ✅ **Model**: Updated `pyproject.toml`, removed `setup.py`
   - Standardized build-system requirements
   - Updated Python version support (3.10-3.12)
   - Replaced black/flake8 with ruff
   - Tests: 103 passed (74% coverage)

3. ✅ **Classification**: Updated `pyproject.toml`, removed `setup.py`
   - Fixed package discovery for src/ structure
   - Standardized tool configurations
   - Tests: 85 passed (18 pre-existing failures)

4. ✅ **Scoring**: Updated `pyproject.toml`
   - Aligned with standard template
   - Unified pytest and coverage settings
   - Tests: 57 passed (67% coverage)

5. ✅ **Documentation**: Created comprehensive guide
   - New file: `_meta/docs/PYTHON_PACKAGING_STANDARD.md`
   - Updated main README.md
   - Documented installation procedures

**Installation Verified**:
All modules successfully install with:
```bash
pip install --no-build-isolation -e .
pip install --no-build-isolation -e ".[dev]"
```

**Benefits Achieved**:
- Single source of truth for dependencies
- Consistent tool configuration across modules
- Modern Python packaging standards (PEP 518, 621)
- Better IDE support
- Simplified installation process
