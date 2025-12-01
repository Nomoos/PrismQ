# PrismQ Test Framework Documentation

This document describes the test framework infrastructure for the PrismQ iterative workflow, particularly focusing on version tracking and integration testing.

## Overview

The test framework supports the **26-stage iterative co-improvement workflow** with specialized helpers for:
- Version tracking across iterations
- Workflow stage validation
- Cross-module integration testing
- Iteration path verification

## Test Infrastructure

### Root pytest Configuration

The root `pytest.ini` provides unified configuration for all tests across the project:

```ini
[pytest]
minversion = 6.0
testpaths = tests EnvLoad/_meta/tests T/Idea/Creation/_meta/tests ...
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests for individual components
    integration: Integration tests for component interactions
    version_tracking: Tests for version tracking and iteration
    slow: Tests that take significant time to run
```

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_basic_functionality():
    """Unit test for basic functionality."""
    pass

@pytest.mark.integration
def test_module_interaction():
    """Integration test for module interaction."""
    pass

@pytest.mark.version_tracking
def test_version_increment():
    """Test for version tracking behavior."""
    pass

@pytest.mark.slow
def test_complete_workflow():
    """Slow test for complete workflow."""
    pass
```

## Test Helpers Module

The `tests/helpers.py` module provides utilities for testing the iterative workflow.

### VersionTracker

Tracks versions through the iterative workflow, ensuring proper version sequencing.

```python
from tests.helpers import VersionTracker

# Create a tracker for an entity
tracker = VersionTracker(entity_type="Title")

# Add versions with metadata
tracker.add_version(1, {"stage": "initial", "from_idea": 1})
tracker.add_version(2, {"stage": "reviewed", "changes": ["better alignment"]})

# Query version information
current_version = tracker.get_current_version()  # Returns 2
version_count = tracker.get_version_count()      # Returns 2
is_valid = tracker.validate_sequence()           # Returns True

# Get version history
history = tracker.get_history()
# [
#     {'version': 1, 'metadata': {'stage': 'initial', 'from_idea': 1}},
#     {'version': 2, 'metadata': {'stage': 'reviewed', 'changes': [...]}}
# ]
```

**Key Features:**
- Enforces sequential version numbering (1, 2, 3, ...)
- Tracks metadata for each version
- Validates version sequences
- Maintains complete version history

**Errors:**
- `ValueError`: If first version is not 1
- `ValueError`: If versions are not sequential

### WorkflowStageValidator

Validates stage transitions in the workflow using module-based state names.

```python
from tests.helpers import WorkflowStageValidator

validator = WorkflowStageValidator()

# Transition through stages using module-based state names
validator.transition_to('PrismQ.T.Idea.Creation')      # True
validator.transition_to('PrismQ.T.Title.From.Idea')    # True
validator.transition_to('PrismQ.T.Script.From.Idea.Title')  # True

# Invalid transition
validator.transition_to('PrismQ.T.Publishing')         # False (can't skip to end)

# Check workflow validity
is_valid = validator.is_valid_path()      # True
history = validator.get_stage_history()   # ['PrismQ.T.Idea.Creation', 'PrismQ.T.Title.From.Idea', 'PrismQ.T.Script.From.Idea.Title']
```

**Valid Stage Transitions:**
- `PrismQ.T.Idea.Creation` → `PrismQ.T.Title.From.Idea`
- `PrismQ.T.Title.From.Idea` → `PrismQ.T.Script.From.Idea.Title`
- `PrismQ.T.Script.From.Idea.Title` → `PrismQ.T.Review.Title.ByScriptAndIdea`
- `PrismQ.T.Review.Title.ByScriptAndIdea` → `PrismQ.T.Review.Script.ByTitleAndIdea`, `PrismQ.T.Title.From.Title.Review.Script`
- See `tests/helpers.py` for the complete transition map

### IntegrationTestHelper

Helper for integration testing across multiple modules.

```python
from tests.helpers import IntegrationTestHelper

helper = IntegrationTestHelper()

# Start tracking multiple entities
idea_tracker = helper.start_workflow("Idea")
title_tracker = helper.start_workflow("Title")
script_tracker = helper.start_workflow("Script")

# Add versions
idea_tracker.add_version(1)
title_tracker.add_version(1)
title_tracker.add_version(2)
script_tracker.add_version(1)
script_tracker.add_version(2)

# Validate cross-module alignment
is_aligned = helper.validate_cross_version_alignment(
    idea_version=1,
    title_version=2,
    script_version=2
)  # Returns True

# Get all trackers
trackers = helper.get_all_trackers()
# {'Idea': <tracker>, 'Title': <tracker>, 'Script': <tracker>}
```

**Version Alignment Rules:**
- Title and Script should be within 1 version of each other
- Idea can stay at v1 while Title/Script iterate
- Or Idea should be within 1 version of max(Title, Script)

### Helper Functions

#### assert_version_increment

Asserts that a version increments by exactly 1.

```python
from tests.helpers import assert_version_increment

# Valid increment
assert_version_increment(1, 2)  # Passes

# Invalid increment
assert_version_increment(1, 3)  # AssertionError: should increment by 1
```

#### assert_version_sequence

Asserts that a version sequence is valid (1, 2, 3, ...).

```python
from tests.helpers import assert_version_sequence

# Valid sequences
assert_version_sequence([1, 2, 3])  # Passes
assert_version_sequence([1])        # Passes
assert_version_sequence([])         # Passes

# Invalid sequences
assert_version_sequence([2, 3, 4])  # AssertionError: First version should be 1
assert_version_sequence([1, 2, 4])  # AssertionError: Version sequence broken
```

#### create_version_history

Creates a VersionTracker with pre-populated history.

```python
from tests.helpers import create_version_history

# Simple history
tracker = create_version_history("Idea", num_versions=3)
# Creates tracker with versions [1, 2, 3]

# With metadata function
def metadata_fn(version):
    return {"version": version, "type": f"v{version}"}

tracker = create_version_history("Title", num_versions=2, metadata_fn=metadata_fn)
```

#### create_test_idea

Creates a test Idea instance for testing (if Idea model is available).

```python
from tests.helpers import create_test_idea

idea = create_test_idea(
    title="Test Idea",
    concept="Test concept",
    version=1,
    status=IdeaStatus.DRAFT
)
```

## Running Tests

### Run All Tests

```bash
# From project root
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=tests --cov-report=html
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Version tracking tests
pytest -m version_tracking

# Exclude slow tests
pytest -m "not slow"
```

### Run Tests in Specific Modules

```bash
# Test helpers
pytest tests/test_helpers.py

# Integration tests
pytest tests/test_integration.py

# EnvLoad tests
pytest EnvLoad/_meta/tests/

# All T module tests
pytest T/
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=tests --cov=EnvLoad --cov=T

# HTML coverage report
pytest --cov=tests --cov-report=html
# Open htmlcov/index.html in browser
```

## Writing Tests

### Unit Test Example

```python
import pytest

@pytest.mark.unit
def test_version_tracker_creation():
    """Test creating a version tracker."""
    from tests.helpers import VersionTracker
    
    tracker = VersionTracker(entity_type="Title")
    
    assert tracker.entity_type == "Title"
    assert tracker.versions == []
    assert tracker.history == []
```

### Integration Test Example

```python
import pytest
from tests.helpers import (
    IntegrationTestHelper,
    assert_version_sequence,
)

@pytest.mark.integration
def test_idea_to_script_workflow():
    """Test Idea → Title → Script workflow."""
    helper = IntegrationTestHelper()
    
    # Setup workflow
    helper.stage_validator.transition_to('PrismQ.T.Idea.Creation')
    idea_tracker = helper.start_workflow("Idea")
    idea_tracker.add_version(1)
    
    helper.stage_validator.transition_to('PrismQ.T.Title.From.Idea')
    title_tracker = helper.start_workflow("Title")
    title_tracker.add_version(1)
    
    helper.stage_validator.transition_to('PrismQ.T.Script.From.Idea.Title')
    script_tracker = helper.start_workflow("Script")
    script_tracker.add_version(1)
    
    # Verify
    assert helper.validate_cross_version_alignment(1, 1, 1)
    assert helper.stage_validator.is_valid_path()
    assert_version_sequence(title_tracker.versions)
```

### Version Tracking Test Example

```python
import pytest
from tests.helpers import VersionTracker, assert_version_increment

@pytest.mark.version_tracking
def test_version_progression():
    """Test version progression through iterations."""
    tracker = VersionTracker("Script")
    
    # v1: Initial
    tracker.add_version(1, {"stage": "initial"})
    
    # v2: After review
    tracker.add_version(2, {"stage": "reviewed"})
    assert_version_increment(1, 2)
    
    # v3: Refined
    tracker.add_version(3, {"stage": "refined"})
    assert_version_increment(2, 3)
    
    # Verify sequence
    assert tracker.validate_sequence()
```

## Best Practices

### 1. Use Appropriate Markers

Mark tests with appropriate markers to enable selective test execution:

```python
@pytest.mark.unit
@pytest.mark.version_tracking
def test_version_logic():
    """Test version logic."""
    pass
```

### 2. Test Version Sequences

Always validate version sequences in tests involving iterations:

```python
from tests.helpers import assert_version_sequence

# After creating multiple versions
assert_version_sequence(tracker.versions)
```

### 3. Validate Workflow Paths

For integration tests, validate that the workflow path is valid:

```python
helper = IntegrationTestHelper()
# ... perform workflow transitions ...
assert helper.stage_validator.is_valid_path()
```

### 4. Use Metadata for Context

Add metadata when tracking versions to provide context:

```python
tracker.add_version(2, {
    "stage": "reviewed",
    "review_source": "script",
    "changes": ["improved alignment", "better flow"],
    "reviewer": "automated"
})
```

### 5. Test Cross-Module Alignment

Test version alignment across modules in integration tests:

```python
helper = IntegrationTestHelper()

# ... add versions to trackers ...

assert helper.validate_cross_version_alignment(
    idea_version=1,
    title_version=2,
    script_version=2
)
```

### 6. Isolate Tests

Each test should be independent and not rely on state from other tests:

```python
@pytest.mark.integration
def test_workflow_cycle():
    """Test complete workflow cycle."""
    # Create fresh helper for this test
    helper = IntegrationTestHelper()
    
    # ... test logic ...
```

## Example: Complete Integration Test

Here's a complete example demonstrating the test framework:

```python
import pytest
from tests.helpers import (
    IntegrationTestHelper,
    assert_version_sequence,
    assert_version_increment,
)

@pytest.mark.integration
@pytest.mark.version_tracking
class TestTitleScriptCoImprovement:
    """Integration test for Title-Script co-improvement cycle."""
    
    def test_two_iteration_cycle(self):
        """Test two iterations of co-improvement."""
        helper = IntegrationTestHelper()
        
        # Initial setup
        helper.stage_validator.transition_to('PrismQ.T.Idea.Creation')
        idea_tracker = helper.start_workflow("Idea")
        idea_tracker.add_version(1, {"status": "draft"})
        
        # v1: Initial versions
        helper.stage_validator.transition_to('PrismQ.T.Title.From.Idea')
        title_tracker = helper.start_workflow("Title")
        title_tracker.add_version(1, {
            "stage": "initial",
            "from_idea": 1,
        })
        
        helper.stage_validator.transition_to('PrismQ.T.Script.From.Idea.Title')
        script_tracker = helper.start_workflow("Script")
        script_tracker.add_version(1, {
            "stage": "initial",
            "from_title": 1,
        })
        
        # Verify initial alignment
        assert helper.validate_cross_version_alignment(1, 1, 1)
        
        # Iteration 1: v1 → v2
        helper.stage_validator.transition_to('title_review')
        helper.stage_validator.transition_to('PrismQ.T.Title.From.Title.Review.Script')
        title_tracker.add_version(2, {
            "stage": "reviewed",
            "feedback": "script_review",
        })
        assert_version_increment(1, 2)
        
        helper.stage_validator.transition_to('PrismQ.T.Script.From.Script.Review.Title')
        script_tracker.add_version(2, {
            "stage": "reviewed",
            "from_title": 2,
        })
        
        # Verify alignment after iteration
        assert helper.validate_cross_version_alignment(1, 2, 2)
        
        # Verify sequences
        assert_version_sequence(title_tracker.versions)
        assert_version_sequence(script_tracker.versions)
        
        # Verify workflow
        assert helper.stage_validator.is_valid_path()
        
        # Check history
        title_history = title_tracker.get_history()
        assert len(title_history) == 2
        assert title_history[1]['metadata']['stage'] == 'reviewed'
```

## Continuous Integration (CI/CD)

**Note:** CI/CD pipeline setup is **NOT** in scope for the MVP. The test framework is designed to be CI/CD-ready but pipeline configuration will be handled in a future iteration by the DevOps team (Worker05).

Current status:
- ✅ Unit test framework configured
- ✅ Integration test support
- ✅ Test helpers for version tracking
- ❌ CI/CD pipeline (future work)

## Contributing

When adding new tests:

1. Place tests in appropriate location:
   - Root-level framework tests: `tests/`
   - Module-specific tests: `{Module}/_meta/tests/`

2. Use appropriate markers:
   - `@pytest.mark.unit` for unit tests
   - `@pytest.mark.integration` for integration tests
   - `@pytest.mark.version_tracking` for version tracking tests
   - `@pytest.mark.slow` for slow tests

3. Follow naming conventions:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test functions: `test_*`

4. Document test purpose in docstring

5. Ensure tests are independent and isolated

## Troubleshooting

### Import Errors

If you encounter import errors, ensure:

1. You're running tests from the project root
2. Paths are added to `sys.path` in conftest.py
3. Required modules are installed

### Test Discovery Issues

If pytest doesn't discover tests:

1. Check `pytest.ini` configuration
2. Ensure test files match `test_*.py` pattern
3. Ensure test functions match `test_*` pattern

### Version Tracking Errors

If version tracking tests fail:

1. Verify versions start at 1
2. Ensure versions increment sequentially
3. Check that metadata is properly formatted

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest Markers](https://docs.pytest.org/en/stable/how-to/mark.html)
- [WORKFLOW.md](../_meta/WORKFLOW.md) - Complete workflow documentation
- [T/README.md](../T/README.md) - Text pipeline documentation

## Summary

The PrismQ test framework provides:

- **Unified Configuration**: Single `pytest.ini` for all tests
- **Version Tracking**: Specialized helpers for version tracking
- **Workflow Validation**: Stage transition validation
- **Integration Testing**: Cross-module test support
- **Flexible Markers**: Selective test execution
- **Best Practices**: Clear patterns for test development

This framework supports the 26-stage iterative co-improvement workflow and enables comprehensive testing of version tracking and module interactions.
