# Test Coverage Improvement Plan

**Date:** 2024-11-01  
**Overall Coverage:** 88.7% (716/807 statements covered)  
**Goal:** Maintain >90% coverage across all modules

## Executive Summary

The PrismQ.IdeaInspiration repository has **good overall test coverage at 88.7%** across the core modules analyzed. The repository contains **182 test files** with **270 test cases** in the core modules alone.

### Key Findings

✅ **Strengths:**
- Excellent coverage in Classification module (96.1%)
- All tested modules have comprehensive test suites
- Well-structured test organization with `_meta/tests` directories
- Good use of pytest and pytest-cov for coverage measurement
- Model module has 103 tests demonstrating thorough testing

⚠️ **Areas for Improvement:**
- Scoring module at 79.9% (just below 80% threshold)
- 18 failing tests in Classification module need attention
- 2 files in Scoring with zero coverage (main.py, logging_config.py)
- Coverage configuration could be enhanced across modules
- Missing coverage reporting for Model and ConfigLoad (configuration issue)

---

## Priority 1: Fix Failing Tests (CRITICAL)

### Classification Module - 18 Failing Tests

**Issue:** Tests are failing due to API changes in the codebase that haven't been reflected in tests.

**Common Failures:**
1. `AttributeError: 'IdeaInspiration' object has no attribute 'created_at'`
2. `AttributeError: 'IdeaInspiration' object has no attribute 'all_text'`
3. `AttributeError: 'ClassificationEnrichment' object has no attribute 'is_story'`
4. `AssertionError: assert <ContentType.VIDEO: 'video'> == 'video'` (enum vs string comparison)

**Action Items:**
- [ ] Review IdeaInspiration model API changes
- [ ] Update tests to use `flags['is_story']` instead of direct `is_story` attribute
- [ ] Fix enum comparisons (use `.value` or compare to enum directly)
- [ ] Remove references to deprecated `created_at`, `all_text`, `has_content` attributes
- [ ] Run tests after each fix to verify

**Timeline:** Immediate (within 1 week)

---

## Priority 2: Improve Scoring Module Coverage

### Current Status
- **Coverage:** 79.9% (294/368 statements)
- **Tests:** 52 passing tests
- **Uncovered Files:** 2 (main.py, logging_config.py)

### Recommended Actions

#### 2.1 Add Tests for main.py
```python
# Create: Scoring/_meta/tests/test_main.py

"""Tests for main.py CLI entry point."""

import pytest
from unittest.mock import patch, MagicMock
from src.main import main, parse_args, process_ideas


class TestCLI:
    """Test suite for CLI functionality."""
    
    def test_parse_args_default(self):
        """Test argument parsing with defaults."""
        with patch('sys.argv', ['main.py']):
            args = parse_args()
            assert args.input is not None
            
    def test_parse_args_custom_input(self):
        """Test argument parsing with custom input."""
        with patch('sys.argv', ['main.py', '--input', 'test.json']):
            args = parse_args()
            assert args.input == 'test.json'
            
    def test_main_with_valid_input(self, tmp_path):
        """Test main function with valid input file."""
        # Create test input file
        input_file = tmp_path / "test_ideas.json"
        input_file.write_text('[]')
        
        with patch('sys.argv', ['main.py', '--input', str(input_file)]):
            result = main()
            assert result == 0
            
    def test_main_with_missing_file(self):
        """Test main function with missing input file."""
        with patch('sys.argv', ['main.py', '--input', 'nonexistent.json']):
            result = main()
            assert result != 0
```

#### 2.2 Add Tests for logging_config.py
```python
# Create: Scoring/_meta/tests/test_logging_config.py

"""Tests for logging configuration."""

import pytest
import logging
from src.logging_config import setup_logging, get_logger


class TestLoggingConfig:
    """Test suite for logging configuration."""
    
    def test_setup_logging_default(self):
        """Test default logging setup."""
        setup_logging()
        logger = logging.getLogger()
        assert logger.level == logging.INFO
        
    def test_setup_logging_debug(self):
        """Test debug logging setup."""
        setup_logging(level=logging.DEBUG)
        logger = logging.getLogger()
        assert logger.level == logging.DEBUG
        
    def test_get_logger_returns_logger(self):
        """Test getting a named logger."""
        logger = get_logger('test')
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test'
```

#### 2.3 Improve text_scorer.py Coverage (Currently 91%)

Focus on edge cases:
- [ ] Test with extremely long text (>10,000 words)
- [ ] Test with unicode/emoji characters
- [ ] Test with malformed input (None, empty strings)
- [ ] Test boundary conditions for scoring thresholds
- [ ] Test all branches in conditional logic

**Target:** >95% coverage for all files

---

## Priority 3: Fix Coverage Reporting Configuration

### Issue
Model and ConfigLoad modules show 0.0% coverage despite having 103 and 37 passing tests respectively.

### Root Cause
Coverage measurement is not configured correctly in the test runs. The scripts are measuring the wrong source directories or files.

### Solution

#### Model Module
Update test command to include proper source:
```bash
cd Model
PYTHONPATH=.:$PYTHONPATH python -m pytest tests \
  --cov=idea_inspiration \
  --cov-report=term \
  --cov-report=html
```

#### ConfigLoad Module  
Update test command:
```bash
cd ConfigLoad
PYTHONPATH=.:$PYTHONPATH python -m pytest tests \
  --cov=config.py \
  --cov=logging_config.py \
  --cov-report=term \
  --cov-report=html
```

Update `_meta/scripts/analyze_coverage.py` to properly detect and measure these modules.

---

## Priority 4: Enhance Coverage Configuration

### 4.1 Add Coverage Configuration to Scoring Module

Update `Scoring/pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/venv/*",
]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "def __str__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "pass",
]
precision = 1
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"
```

### 4.2 Add Coverage Badges

Add to module READMEs:
```markdown
![Coverage](https://img.shields.io/badge/coverage-88.7%25-green)
```

### 4.3 Set Minimum Coverage Thresholds

Add to `pyproject.toml`:
```toml
[tool.coverage.report]
fail_under = 80
```

---

## Priority 5: Testing Best Practices

### 5.1 Add Integration Tests

Create integration test suites that test module interactions:

```python
# _meta/tests/test_integration.py

"""Integration tests for module interactions."""

def test_scoring_with_classification():
    """Test that scoring works with classified content."""
    from Classification import TextClassifier
    from Scoring import ScoringEngine
    from Model import IdeaInspiration
    
    # Create test idea
    idea = IdeaInspiration.from_text(
        title="Test Article",
        content="This is a test article about technology."
    )
    
    # Classify
    classifier = TextClassifier()
    classified = classifier.classify(idea)
    
    # Score
    scorer = ScoringEngine()
    score = scorer.score_idea_inspiration(classified)
    
    assert score.overall_score >= 0
    assert score.overall_score <= 100
```

### 5.2 Add Property-Based Testing

Install hypothesis:
```bash
pip install hypothesis
```

Example property-based test:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=1000))
def test_text_scorer_handles_any_text(text):
    """Test that text scorer handles any valid text input."""
    from Scoring import TextScorer
    
    scorer = TextScorer()
    score = scorer.score_text(text)
    
    # Score should always be in valid range
    assert 0 <= score <= 100
```

### 5.3 Add Performance Benchmarks

Already exists in `_meta/performance/benchmarks/` - ensure they're running:

```python
# Example benchmark
def test_scoring_performance(benchmark):
    """Benchmark scoring performance."""
    from Scoring import ScoringEngine
    from Model import IdeaInspiration
    
    engine = ScoringEngine()
    idea = IdeaInspiration.from_text(
        title="Performance Test",
        content="Content for performance testing."
    )
    
    result = benchmark(engine.score_idea_inspiration, idea)
    assert result is not None
```

### 5.4 Create Shared Test Fixtures

Create `conftest.py` files with common fixtures:

```python
# Scoring/_meta/tests/conftest.py

import pytest
from Model import IdeaInspiration


@pytest.fixture
def sample_text_idea():
    """Create a sample text idea for testing."""
    return IdeaInspiration.from_text(
        title="Test Article",
        description="Test description",
        content="This is test content for unit testing."
    )


@pytest.fixture
def sample_video_idea():
    """Create a sample video idea for testing."""
    return IdeaInspiration.from_video(
        title="Test Video",
        description="Test video description",
        metadata={
            "views": 10000,
            "likes": 500,
            "duration": 300
        }
    )
```

---

## Priority 6: Coverage Trends and CI/CD Integration

### 6.1 Track Coverage Over Time

Create coverage history:
```bash
# Add to CI/CD pipeline
mkdir -p coverage_history
python _meta/scripts/analyze_coverage.py > coverage_history/coverage_$(date +%Y%m%d).txt
```

### 6.2 Add GitHub Actions Workflow

Create `.github/workflows/coverage.yml`:

```yaml
name: Test Coverage

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  coverage:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install pytest pytest-cov python-dotenv
    
    - name: Run coverage analysis
      run: |
        python _meta/scripts/analyze_coverage.py
    
    - name: Upload coverage report
      uses: actions/upload-artifact@v3
      with:
        name: coverage-report
        path: _meta/docs/TEST_COVERAGE_REPORT.md
```

### 6.3 Add Coverage Reporting to PR Comments

Use coverage-comment action to automatically comment on PRs with coverage changes.

---

## Timeline & Milestones

### Week 1 (Immediate)
- [x] Create coverage analysis script
- [x] Generate initial coverage report
- [ ] Fix 18 failing tests in Classification module
- [ ] Add tests for Scoring/main.py and logging_config.py

### Week 2
- [ ] Fix coverage reporting for Model and ConfigLoad
- [ ] Improve Scoring coverage to >85%
- [ ] Add coverage configuration enhancements

### Week 3
- [ ] Create integration test suites
- [ ] Add property-based tests for critical paths
- [ ] Set up GitHub Actions for coverage tracking

### Week 4
- [ ] Add performance benchmarks to CI
- [ ] Create shared test fixtures
- [ ] Add coverage badges to READMEs
- [ ] Document testing best practices

### Month 2+
- [ ] Achieve >90% coverage across all core modules
- [ ] Implement mutation testing
- [ ] Add type checking with mypy to CI
- [ ] Quarterly coverage reviews

---

## Success Metrics

### Short-term (1 month)
- ✅ 0 failing tests
- ✅ Scoring module >85% coverage
- ✅ All core modules have coverage reporting
- ✅ Coverage configuration in all pyproject.toml files

### Medium-term (3 months)
- ✅ Overall coverage >90%
- ✅ All modules >85% coverage
- ✅ Integration tests for all module interactions
- ✅ Automated coverage reporting in CI/CD

### Long-term (6 months)
- ✅ Overall coverage >95%
- ✅ Coverage trends tracked and improving
- ✅ Property-based testing for critical paths
- ✅ Mutation testing showing high test quality
- ✅ Zero tolerance for coverage regressions

---

## Conclusion

The PrismQ.IdeaInspiration repository has a solid foundation with **88.7% overall coverage** and comprehensive test suites. By addressing the failing tests, improving coverage in the Scoring module, and enhancing testing infrastructure, we can achieve our goal of >90% coverage while maintaining high code quality.

The focus should be on:
1. **Quality over quantity** - Fix failing tests first
2. **Targeted improvements** - Focus on uncovered files and low-coverage areas
3. **Infrastructure** - Enhance coverage configuration and CI/CD integration
4. **Best practices** - Implement integration tests, property-based testing, and shared fixtures

This plan provides a clear roadmap to maintain and improve test coverage across the repository.
