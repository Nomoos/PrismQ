# Issue 205: Remove Duplicate Test Files and Consolidate Test Structure

## Status
New

## Priority
Medium

## Category
Infrastructure_DevOps

## Description
Several modules have test files in inconsistent locations, including duplicates and misplaced test/example files that should be organized properly.

## Problem Statement

### Issues Found:

1. **Test Files in Module Root**:
   - `Classification/test_batch_input.py` - should be in tests/
   - `Scoring/test_batch_input.py` - should be in tests/ or examples/

2. **Inconsistent Test Locations**:
   - Some modules: `tests/` directory (standard)
   - Some modules: `_meta/tests/` directory
   - Some modules: test files in root
   - ConfigLoad: `tests/` directory (good!)
   - Model: `tests/` directory (good!)

3. **Example vs Test Confusion**:
   - Files named `test_batch_input.py` appear to be examples, not unit tests
   - `example.py` and `example_generalized.py` in Classification root
   - `example_config_usage.py` in Model root

4. **Test Coverage Inconsistency**:
   - Some modules have comprehensive tests
   - Some modules have no tests
   - Test coverage reports scattered across modules

## Proposed Solution

### 1. Standardize Test Location

**All modules should use**:
```
module/
├── tests/              # Unit and integration tests
│   ├── __init__.py
│   ├── test_*.py
│   └── conftest.py    # pytest configuration
└── examples/           # Example scripts
    └── *.py
```

**Not**:
- `_meta/tests/` - This should be for testing documentation or meta-processes
- Test files in module root
- Example files in module root

### 2. Migrate Files

**Classification**:
- Move `test_batch_input.py` → `examples/batch_processing_example.py` (or tests/ if it's a real test)
- Move `example.py` → `examples/basic_classification.py`
- Move `example_generalized.py` → `examples/generalized_classification.py`

**Scoring**:
- Move `test_batch_input.py` → `examples/batch_processing_example.py` (or tests/ if it's a real test)

**Model**:
- Move `example_config_usage.py` → `examples/config_usage.py`

**Client**:
- Review `_meta/tests/` - might be appropriate as meta-tests for the module structure
- Ensure Frontend and Backend have proper test directories

### 3. Create Test Infrastructure Guide

Document in `_meta/docs/development/TESTING.md`:
- Where tests should go
- How to structure tests
- Running tests
- Test coverage expectations
- pytest configuration
- Example vs test distinction

### 4. Add pytest Configuration

Create `pytest.ini` or `pyproject.toml` configuration:
```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
]
```

## Benefits
- Clear separation of tests and examples
- Consistent test discovery
- Better IDE support
- Easier CI/CD configuration
- Clear testing documentation
- Improved developer experience

## Acceptance Criteria
- [ ] All test files in `tests/` directories
- [ ] All example files in `examples/` directories
- [ ] No loose .py files in module roots (except setup.py)
- [ ] Each module with code has a tests/ directory
- [ ] pytest configuration is consistent
- [ ] TESTING.md documentation created
- [ ] All tests still pass after migration
- [ ] Examples still work after migration

## Implementation Steps

1. **Audit Current State**:
   - Find all test files: `find . -name "test_*.py"`
   - Find all example files: `find . -name "example*.py"`
   - Document current locations

2. **Determine File Purposes**:
   - Review each file - is it a test or example?
   - Check if tests are real unit tests or just examples
   - Determine appropriate destination

3. **Create Standard Directories**:
   - Ensure all modules have `tests/` and `examples/`
   - Add `__init__.py` where needed
   - Add README.md in examples/

4. **Migrate Files**:
   - Move test files to tests/
   - Move example files to examples/
   - Rename for clarity if needed

5. **Add pytest Configuration**:
   - Add to pyproject.toml in each module
   - Ensure consistent configuration

6. **Update Documentation**:
   - Update module READMEs
   - Create TESTING.md guide
   - Update CONTRIBUTING.md

7. **Verify**:
   - Run all tests
   - Run all examples
   - Check CI/CD still works

## Commands for Verification

```bash
# Find test files not in tests/ directory
find . -name "test_*.py" ! -path "*/tests/*" ! -path "*/_meta/*" ! -path "*/node_modules/*"

# Find example files
find . -name "example*.py" ! -path "*/examples/*" ! -path "*/node_modules/*"

# Run all tests
pytest --collect-only  # Show what would be collected

# Run tests with coverage
pytest --cov --cov-report=html
```

## Estimated Effort
3-4 hours

## Dependencies
- Issue #202 (Module structure standardization)

## Related Issues
- Issue #202 (Module structure)
- Issue #206 (Testing infrastructure)

## Notes
- Need to verify each `test_*.py` file is actually a test
- Some might be examples disguised as tests
- After migration, imports might need updating
- Good opportunity to add missing tests
