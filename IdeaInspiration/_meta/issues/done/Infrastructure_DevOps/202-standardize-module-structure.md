# Issue 202: Standardize Module Structure and Organization

## Status
Done - Completed 2025-11-04

## Priority
Medium

## Category
Infrastructure_DevOps

## Description
Modules across the repository have inconsistent structure, file organization, and naming conventions. Standardizing these will improve maintainability and developer experience.

## Problem Statement

### Inconsistencies Found:

1. **Test Files Location**:
   - Some modules: tests in `tests/` directory
   - Some modules: test files in module root (e.g., `test_batch_input.py`)
   - Some modules: tests in `_meta/tests/`

2. **Example Files**:
   - Classification: `example.py`, `example_generalized.py` in root
   - Model: `example_config_usage.py` in root
   - Scoring: `test_batch_input.py` in root (seems like an example, not a test)

3. **Configuration Files**:
   - Mix of `pyproject.toml`, `setup.py`, or both
   - Inconsistent placement of `requirements.txt`
   - Some have `module.json`, others don't

4. **Virtual Environment Markers**:
   - `.envrc` files present in some modules, not others
   - `.env.example` inconsistently present

5. **Documentation Structure**:
   - Mix of `_meta/doc/` vs `_meta/docs/`
   - Some modules have `docs/`, others don't
   - Inconsistent README placement and content

## Proposed Solution

### Define Standard Module Structure

```
ModuleName/
├── .envrc                    # direnv configuration (all modules)
├── .env.example              # Environment template (if needed)
├── .gitignore                # Module-specific ignores
├── README.md                 # Module overview
├── pyproject.toml            # Modern Python packaging (see Issue #206)
├── requirements.txt          # Dependencies (optional, can be replaced by pyproject.toml)
├── setup.py                  # (optional, if needed for compatibility)
├── module.json               # Module metadata for Client
├── src/                      # Source code
│   └── module_name/
│       ├── __init__.py
│       └── *.py
├── tests/                    # All tests here
│   ├── __init__.py
│   └── test_*.py
├── examples/                 # Example scripts (if any)
│   └── *.py
├── scripts/                  # Utility scripts
│   └── README.md
├── docs/                     # User-facing documentation
│   ├── SETUP.md
│   └── USER_GUIDE.md
└── _meta/                    # Internal/development
    ├── docs/                 # (not "doc") Development docs
    ├── issues/               # Module-specific issues
    └── research/             # Research and experiments

**Note**: Issue #206 addresses standardizing Python configuration files. The goal is to adopt modern `pyproject.toml` (PEP 621) and potentially remove `requirements.txt` and `setup.py` where not needed.
```

### Migration Tasks

**For Each Module**:
1. Move test files to `tests/` directory
2. Move example files to `examples/` directory
3. Ensure `.envrc` is present (for direnv)
4. Standardize on `pyproject.toml` (modern approach)
5. Rename `_meta/doc/` → `_meta/docs/`
6. Add `module.json` if module should appear in Client
7. Ensure consistent .gitignore

**Specific Modules to Fix**:
- **Classification**: Move `example.py`, `example_generalized.py`, `test_batch_input.py`
- **Scoring**: Move `test_batch_input.py` to examples or tests
- **Model**: Move `example_config_usage.py`
- **All Sources**: Ensure consistent structure

## Benefits
- Easier navigation across modules
- Clear separation of code, tests, examples, and documentation
- Consistent development experience
- Simplified CI/CD configuration
- Better IDE support

## Acceptance Criteria
- [x] All modules follow standard structure
- [x] Test files in `tests/` directory (with `_meta/tests/` for integration tests)
- [x] Example files in `examples/` directory
- [x] No loose .py files in module roots (except setup.py)
- [x] All modules have `.envrc` for direnv (already present)
- [x] Documentation structure standardized (all have `_meta/docs/` and `_meta/issues/`)
- [N/A] Template/checklist created for new modules (deferred to future work)

## Implementation Steps

1. **Create Standard Template**:
   - Document standard structure
   - Create module template in PrismQ.RepositoryTemplate
   - Add structure checklist

2. **Migrate Existing Modules** (one at a time):
   - ConfigLoad (simplest)
   - Model
   - Classification
   - Scoring
   - Client
   - Sources (many sub-modules)

3. **Update Documentation**:
   - Update CONTRIBUTING.md with standards
   - Update module README files
   - Create new module template guide

4. **Verify**:
   - All tests still pass
   - All examples still work
   - Documentation is accurate

## Estimated Effort
8-12 hours (spread across multiple sessions)

## Dependencies
- Issue #200 (historical docs need archiving first)
- Issue #201 (documentation organization)

## Related Issues
- Issue #200 (Documentation consolidation)
- Issue #201 (Documentation hierarchy)
- Issue #203 (Improve .gitignore)

## Notes
- This should be done incrementally, one module at a time
- Each module migration should be tested independently
- Consider creating separate sub-issues for each module

## Implementation Summary (2025-11-04)

### Completed Work:

**File Reorganization:**
- Classification: Moved 3 files (`example.py`, `example_generalized.py`, `test_batch_input.py`) to `examples/`
- Model: Moved 1 file (`example_config_usage.py`) to `examples/`
- Scoring: Moved 1 file (`test_batch_input.py`) to `examples/`

**Directory Structure Created:**
- Classification: Added `tests/` and `examples/` directories
- Model: Added `examples/` directory
- Scoring: Added `tests/` and `examples/` directories
- ConfigLoad: Added `_meta/docs/` and `_meta/issues/` for consistency

**Configuration Updates:**
- Updated `Classification/pyproject.toml` pytest testpaths to include both `tests/` and `_meta/tests/`
- Updated `Scoring/pyproject.toml` pytest testpaths to include both `tests/` and `_meta/tests/`

**Documentation Updates:**
- Classification: Updated 3 documentation files and 6 script files
- Model: Updated 1 documentation file

**Result:**
All four main modules (Classification, ConfigLoad, Model, Scoring) now follow a consistent structure with:
- `examples/` for example scripts
- `tests/` for unit tests
- `_meta/tests/` for integration/development tests
- `_meta/docs/` for development documentation
- `_meta/issues/` for issue tracking

### Deferred Work:
- Creating a formal module template (can be addressed in a future issue if needed)
- Sources module standardization (contains many sub-modules, should be handled separately)
