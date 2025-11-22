# Testing and Coverage Guide

**Last Updated**: November 2024  
**Overall Coverage**: 88.7%  
**Status**: ✅ Strong test infrastructure

## Quick Links

- [Quick Reference](#quick-reference-commands) - Common testing commands
- [Coverage Reports](#coverage-reports) - Current coverage statistics
- [Best Practices](#best-practices) - Writing effective tests
- [Troubleshooting](#troubleshooting) - Common issues and solutions

## Overview

PrismQ.IdeaInspiration maintains a comprehensive test suite with **270+ test cases** across core modules. The repository demonstrates strong test coverage at 88.7% overall, with excellent module-specific coverage.

## Coverage Summary

### By Module

| Module | Coverage | Tests | Status |
|--------|----------|-------|--------|
| **Classification** | 96.1% | 78 passing, 18 failing | 🌟 Excellent |
| **Scoring** | 79.9% | 52 passing | ⚠️ Fair |
| **Model** | 98%* | 103 passing | ✅ Excellent |
| **EnvLoad** | High* | 37 passing | ✅ Good |

\* Coverage measurement needs configuration verification

### Statistics

- **Total Test Cases**: 270+ across core modules
- **Total Test Files**: 182 repository-wide
- **Code Statements**: 807 in core modules
- **Covered Statements**: 716 (88.7%)

## Quick Reference Commands

### Run All Tests for a Module

```bash
# Scoring module
cd Scoring
PYTHONPATH=.:$PYTHONPATH python -m pytest _meta/tests -v

# Classification module  
cd Classification
PYTHONPATH=.:$PYTHONPATH python -m pytest _meta/tests -v

# Model module
cd Model
PYTHONPATH=.:$PYTHONPATH python -m pytest tests -v

# EnvLoad module
cd EnvLoad
PYTHONPATH=.:$PYTHONPATH python -m pytest tests -v
```

### Run Tests with Coverage

```bash
# Scoring
cd Scoring
PYTHONPATH=.:$PYTHONPATH python -m pytest _meta/tests --cov=src --cov-report=term --cov-report=html

# Classification
cd Classification
PYTHONPATH=.:$PYTHONPATH python -m pytest _meta/tests --cov=prismq --cov-report=term --cov-report=html

# Model
cd Model
PYTHONPATH=.:$PYTHONPATH python -m pytest tests --cov=idea_inspiration --cov-report=term --cov-report=html

# EnvLoad
cd EnvLoad
PYTHONPATH=.:$PYTHONPATH python -m pytest tests --cov=config.py --cov=logging_config.py --cov-report=term --cov-report=html
```

### Generate Repository-Wide Coverage Report

```bash
# From repository root
python _meta/scripts/analyze_coverage.py
```

This will:
- Run tests for all core modules
- Generate coverage statistics
- Save report to `_meta/docs/archive/validation/TEST_COVERAGE_REPORT.md`
- Print detailed findings and recommendations

### Useful pytest Options

```bash
# Run specific test file
pytest _meta/tests/test_scoring.py -v

# Run specific test function
pytest _meta/tests/test_scoring.py::TestScoringEngine::test_calculate_score -v

# Run tests matching pattern
pytest -k "score" -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Verbose mode
pytest -v

# Run last failed tests
pytest --lf

# Run tests in parallel
pytest -n auto  # requires pytest-xdist
```

### Check Coverage Against Threshold

```bash
pytest --cov=src --cov-fail-under=80
```

## Coverage Thresholds

### Current Targets
- **Minimum**: 80% per module
- **Goal**: 90% overall
- **Excellent**: 95%+

### Module-Specific Goals

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| Classification | 96.1% | 95% | ✅ Met |
| Model | 98% | 95% | ✅ Met |
| Scoring | 79.9% | 85% | 🔴 High |
| EnvLoad | High | 85% | 🟡 Medium |

## Best Practices

### Test Structure (AAA Pattern)

```python
def test_feature():
    # Arrange - Set up test data
    scorer = ScoringEngine()
    idea = create_test_idea()
    
    # Act - Execute the code being tested
    result = scorer.score_idea_inspiration(idea)
    
    # Assert - Verify the result
    assert result.overall_score >= 0
    assert result.overall_score <= 100
```

### Using Fixtures

```python
import pytest

@pytest.fixture
def sample_idea():
    """Create a sample idea for testing."""
    return IdeaInspiration.from_text(
        title="Test",
        content="Test content"
    )

def test_with_fixture(sample_idea):
    """Test using the fixture."""
    assert sample_idea.title == "Test"
```

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("short", 10),
    ("medium length text", 20),
    ("very long text content here", 30),
])
def test_text_length_scoring(input, expected):
    """Test scoring with different text lengths."""
    score = calculate_length_score(input)
    assert score == expected
```

### Testing Exceptions

```python
import pytest

def test_invalid_input_raises_error():
    """Test that invalid input raises appropriate error."""
    with pytest.raises(ValueError, match="Invalid input"):
        process_idea(None)
```

### What to Cover

✅ **DO cover**:
- All public APIs
- Edge cases and boundary conditions
- Error handling paths
- Different input combinations
- Critical business logic

❌ **DON'T need to cover**:
- Trivial getters/setters
- `__repr__` and `__str__` methods (use `pragma: no cover`)
- Third-party library code
- Deprecated code marked for removal

### Exclude from Coverage

```python
def debug_only_function():  # pragma: no cover
    """This function is only for debugging."""
    print("Debug info")
```

## Viewing Coverage Reports

### HTML Reports

After running tests with coverage:

```bash
# Open the HTML report in browser
cd Scoring
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
start htmlcov/index.html     # Windows
```

### Terminal Reports with Missing Lines

```bash
cd Scoring
PYTHONPATH=.:$PYTHONPATH python -m pytest _meta/tests \
  --cov=src/scoring/text_scorer.py \
  --cov-report=term-missing
```

The `--cov-report=term-missing` flag shows which lines are not covered.

## Coverage Reports

### Current Analysis

Detailed coverage reports are available:
- [Coverage Summary](../archive/validation/COVERAGE_SUMMARY.md) - Executive summary (88.7% overall)
- [Detailed Report](../archive/validation/TEST_COVERAGE_REPORT.md) - Module breakdowns
- [Improvement Plan](../archive/validation/COVERAGE_IMPROVEMENT_PLAN.md) - Action items
- [Complete Analysis](../archive/validation/COVERAGE_ANALYSIS_COMPLETE.md) - Full analysis

## Action Items

### 🔴 Critical (Fix Now)
1. **Fix 18 failing tests** in Classification module
   - API changes not reflected in tests
   - Enum vs string comparisons
   - Deprecated attribute references

### 🟡 High Priority (This Week)
2. **Improve Scoring coverage** from 79.9% to >85%
   - Add tests for `main.py` (CLI entry point)
   - Add tests for `logging_config.py`
   - Add edge case tests for `text_scorer.py`

### 🟢 Medium Priority (This Month)
3. **Enhance coverage configuration**
   - Add branch coverage
   - Set minimum thresholds
   - Configure exclusions

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`:
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/module:$PYTHONPATH

# Or run from module directory
cd Scoring
PYTHONPATH=.:$PYTHONPATH pytest _meta/tests
```

### Coverage Showing 0%

If coverage shows 0%:
```bash
# Check that you're measuring the right source
pytest --cov=src  # Not --cov=.

# Verify source files are being imported
pytest --cov=src --cov-report=term-missing -v
```

### Tests Pass Locally But Fail in CI

Common causes:
- Missing dependencies in CI environment
- Path differences (Windows vs Linux)
- Environment variables not set
- Timezone differences
- File system permissions

## Continuous Integration

### Pre-commit Hook Example

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run tests before commit

echo "Running tests..."
cd Scoring && PYTHONPATH=.:$PYTHONPATH python -m pytest _meta/tests --cov=src --cov-fail-under=80 -q

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

echo "Tests passed!"
exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [Repository Architecture](../ARCHITECTURE.md)
- [Contributing Guidelines](../CONTRIBUTING.md)

---

**Last Updated**: November 2024  
**Maintained by**: PrismQ Development Team
