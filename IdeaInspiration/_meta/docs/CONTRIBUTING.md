# Contributing to PrismQ.IdeaInspiration

Thank you for your interest in contributing to PrismQ.IdeaInspiration! This document provides guidelines for contributing to this ecosystem.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style and Standards](#code-style-and-standards)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Tracking](#issue-tracking)

## Getting Started

PrismQ.IdeaInspiration is a multi-module ecosystem. Before contributing:

1. **Familiarize yourself with the modules**: Read the main [README.md](../../README.md) and individual module READMEs
2. **Review the roadmap**: Check [_meta/issues/ROADMAP.md](../issues/ROADMAP.md) for planned work
3. **Check existing issues**: See [_meta/issues/](../issues/) for current tasks

## Development Setup

### Prerequisites

- **Operating System**: Windows (primary), Linux (CI/testing only)
- **GPU**: NVIDIA RTX 5090 with latest drivers (for performance testing)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5
- **Python**: 3.10 or higher
- **Git**: Latest version

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
cd PrismQ.IdeaInspiration

# Choose the module you want to work on
cd Classification  # or ConfigLoad, Model, Scoring, Sources

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux

# Install in development mode
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

## Code Style and Standards

### Python Code Style

- **Follow PEP 8**: Use standard Python style guidelines
- **Type hints**: All function parameters and return values must have type hints
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Line length**: Maximum 100 characters (not the default 79)

### SOLID Principles

All code must follow SOLID design principles:

- **Single Responsibility**: Each class should have one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for their base types
- **Interface Segregation**: Use focused, minimal interfaces (Python Protocols)
- **Dependency Inversion**: Depend on abstractions, inject dependencies

See [SOLID_PRINCIPLES.md](./SOLID_PRINCIPLES.md) for detailed examples.

### Additional Design Principles

- **DRY (Don't Repeat Yourself)**: Eliminate code duplication
- **KISS (Keep It Simple)**: Favor simplicity over complexity
- **YAGNI (You Aren't Gonna Need It)**: Only implement what's needed now

### Code Formatting

```bash
# Format code with black
black prismq/ tests/

# Check style with flake8
flake8 prismq/ tests/

# Type checking with mypy
mypy prismq/
```

## Making Changes

### Workflow

1. **Create a branch**: Use descriptive names
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes**: Follow code style guidelines

3. **Write tests**: All new features must have tests

4. **Update documentation**: Keep READMEs and docstrings current

5. **Test thoroughly**: Run the full test suite
   ```bash
   pytest
   pytest --cov=prismq --cov-report=html
   ```

### Commit Messages

Use clear, descriptive commit messages:

```
Add sentiment analysis to text quality scoring

- Implement VADER sentiment analyzer
- Add sentiment category field to results
- Update tests for sentiment scoring
- Update documentation
```

Format:
- First line: Brief summary (50 chars max)
- Blank line
- Detailed description with bullet points

## Testing

### Test Requirements

- **Coverage**: Aim for >80% code coverage
- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test module interactions
- **Performance tests**: Benchmark GPU-intensive operations (if applicable)

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=prismq --cov-report=html

# Run specific test file
pytest tests/test_classifier.py -v

# Run tests matching pattern
pytest -k "test_sentiment"
```

### Writing Tests

```python
import pytest
from prismq.idea.classification import TextClassifier

def test_text_classifier_basic():
    """Test basic classification functionality."""
    classifier = TextClassifier()
    result = classifier.classify_text("Sample text")
    
    assert result is not None
    assert result.category is not None
    assert 0 <= result.confidence <= 1.0

def test_text_classifier_empty_input():
    """Test classifier handles empty input gracefully."""
    classifier = TextClassifier()
    
    with pytest.raises(ValueError):
        classifier.classify_text("")
```

## Submitting Changes

### Pull Request Process

1. **Update your branch**: Rebase on latest main
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run all checks**:
   ```bash
   pytest
   black prismq/ tests/
   flake8 prismq/ tests/
   mypy prismq/
   ```

3. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**:
   - Use a descriptive title
   - Reference related issues
   - Describe changes in detail
   - List any breaking changes

### PR Requirements

- [ ] All tests pass
- [ ] Code coverage >80% for new code
- [ ] Documentation updated
- [ ] Type hints on all functions
- [ ] Follows SOLID principles
- [ ] No linting errors
- [ ] Commit messages are clear

## Issue Tracking

### Finding Issues

Issues are tracked in two places:

1. **GitHub Issues**: https://github.com/Nomoos/PrismQ.IdeaInspiration/issues
2. **Local Issues**: `_meta/issues/new/`, `wip/`, `done/`

### Creating Issues

Use the issue template:

```markdown
## Issue Title

**Type**: Bug / Feature / Enhancement
**Priority**: High / Medium / Low
**Module**: Classification / ConfigLoad / Model / Scoring / Sources

### Description
Clear description of the issue or feature

### Steps to Reproduce (for bugs)
1. Step 1
2. Step 2
3. Step 3

### Expected Behavior
What should happen

### Actual Behavior
What actually happens

### Environment
- OS: Windows [version]
- GPU: NVIDIA RTX 5090
- Python: [version]
- Module version: [version]
```

### Working on Issues

1. **Comment on the issue**: Let others know you're working on it
2. **Move to WIP**: Move issue file from `new/` to `wip/`
3. **Create branch**: Use issue number in branch name
4. **Complete work**: Implement, test, document
5. **Move to Done**: Move issue file to `done/` when merged

## Performance Considerations

When working on GPU-intensive features:

- **Profile first**: Use cProfile and GPU profilers
- **Optimize for RTX 5090**: Consider 32GB VRAM, Ada Lovelace architecture
- **Batch operations**: Group operations for better GPU utilization
- **Mixed precision**: Use FP16 when appropriate
- **Memory management**: Implement proper CUDA memory cleanup

## Questions?

- **Documentation**: Check individual module READMEs
- **Roadmap**: See [_meta/issues/ROADMAP.md](../issues/ROADMAP.md)
- **Known Issues**: See [_meta/issues/KNOWN_ISSUES.md](../issues/KNOWN_ISSUES.md)
- **GitHub Issues**: Open a question on GitHub

## License

By contributing, you agree that your contributions will be licensed under the same license as this project (Proprietary - All Rights Reserved).

---

Thank you for contributing to PrismQ.IdeaInspiration! 🚀
