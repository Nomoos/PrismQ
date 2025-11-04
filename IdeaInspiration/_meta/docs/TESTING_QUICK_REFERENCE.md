# Testing Quick Reference Guide

This guide provides quick commands and best practices for running tests in the PrismQ.IdeaInspiration repository.

## Running Tests

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

# ConfigLoad module
cd ConfigLoad
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

# ConfigLoad
cd ConfigLoad
PYTHONPATH=.:$PYTHONPATH python -m pytest tests --cov=config.py --cov=logging_config.py --cov-report=term --cov-report=html
```

### Run Specific Test File

```bash
cd Scoring
PYTHONPATH=.:$PYTHONPATH python -m pytest _meta/tests/test_scoring.py -v
```

### Run Specific Test Function

```bash
cd Scoring
PYTHONPATH=.:$PYTHONPATH python -m pytest _meta/tests/test_scoring.py::TestScoringEngine::test_calculate_score_basic -v
```

### Run Tests Matching Pattern

```bash
cd Scoring
PYTHONPATH=.:$PYTHONPATH python -m pytest _meta/tests -k "score" -v
```

## Coverage Analysis

### Generate Full Coverage Report

```bash
# From repository root
python _meta/scripts/analyze_coverage.py
```

This will:
- Run tests for all core modules
- Generate coverage statistics
- Save report to `_meta/docs/TEST_COVERAGE_REPORT.md`
- Print detailed findings and recommendations

### View HTML Coverage Report

After running tests with coverage:

```bash
# Open the HTML report in browser
cd Scoring
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
start htmlcov/index.html     # Windows
```

### Check Coverage for Specific File

```bash
cd Scoring
PYTHONPATH=.:$PYTHONPATH python -m pytest _meta/tests \
  --cov=src/scoring/text_scorer.py \
  --cov-report=term-missing
```

The `--cov-report=term-missing` flag shows which lines are not covered.

## Common Test Options

### Verbose Output
```bash
pytest -v           # Verbose mode
pytest -vv          # More verbose
pytest -q           # Quiet mode
```

### Stop on First Failure
```bash
pytest -x           # Stop on first failure
pytest --maxfail=3  # Stop after 3 failures
```

### Show Print Statements
```bash
pytest -s           # Don't capture stdout
```

### Run Only Failed Tests
```bash
pytest --lf         # Run last failed
pytest --ff         # Run failed first, then rest
```

### Parallel Test Execution
```bash
pip install pytest-xdist
pytest -n auto      # Use all CPU cores
pytest -n 4         # Use 4 workers
```

## Coverage Thresholds

### Current Targets
- **Minimum:** 80% per module
- **Goal:** 90% overall
- **Excellent:** 95%+

### Check Against Threshold
```bash
pytest --cov=src --cov-fail-under=80
```

This will fail if coverage is below 80%.

## Writing Good Tests

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

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test using mocked dependencies."""
    mock_api = Mock()
    mock_api.fetch_data.return_value = {"score": 85}
    
    scorer = ScoringEngine(api=mock_api)
    result = scorer.score_idea_inspiration(idea)
    
    assert result.overall_score == 85
    mock_api.fetch_data.assert_called_once()
```

## Performance Testing

### Run Benchmarks
```bash
cd _meta/performance
pytest benchmarks/ --benchmark-only
```

### Compare Performance
```bash
pytest benchmarks/ --benchmark-compare
```

## Coverage Best Practices

### What to Cover

✅ **DO cover:**
- All public APIs
- Edge cases and boundary conditions  
- Error handling paths
- Different input combinations
- Critical business logic

❌ **DON'T need to cover:**
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

### Focus on Important Code

```bash
# Focus on critical modules
pytest --cov=src/scoring --cov=src/models --cov-fail-under=95
```

## Continuous Integration

### Pre-commit Hook

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

### Coverage Not Working

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

## Quick Commands Cheat Sheet

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_file.py::test_function

# Run matching pattern
pytest -k "test_pattern"

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Verbose mode
pytest -v

# Quiet mode
pytest -q

# Run last failed tests
pytest --lf

# Run tests in parallel
pytest -n auto

# Generate coverage report
python _meta/scripts/analyze_coverage.py
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [Repository coverage report](./_meta/docs/TEST_COVERAGE_REPORT.md)
- [Coverage improvement plan](./_meta/docs/COVERAGE_IMPROVEMENT_PLAN.md)

---

**Last Updated:** 2024-11-01  
**Maintained by:** PrismQ Development Team
