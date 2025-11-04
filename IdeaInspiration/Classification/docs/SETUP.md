# Classification Module - Setup Guide

## Installation

### From Source (Development)

```bash
git clone https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification.git
cd PrismQ.IdeaInspiration.Classification
pip install -e .
```

### From PyPI (Future)

```bash
pip install prismq-idea-classification
```

### Development Environment

```bash
# Clone the repository
git clone https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification.git
cd PrismQ.IdeaInspiration.Classification

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Testing

Run the comprehensive test suite (48 tests):

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run with coverage
pytest --cov=prismq --cov-report=html

# Run specific test file
pytest tests/test_category_classifier.py -v
pytest tests/test_story_detector.py -v
```

## Design Principles

1. **Platform Agnostic** - No platform-specific code or dependencies
2. **Minimal Requirements** - Only standard text fields (title, description, tags, subtitles)
3. **Local Processing** - All computation happens locally, no external API calls
4. **Zero Cost** - No external AI service fees
5. **Well Tested** - Comprehensive test coverage with realistic examples
6. **High Performance** - Pure Python, optimized for speed
7. **Easy Integration** - Simple import and usage patterns

## Package Structure

```
PrismQ.IdeaInspiration.Classification/
├── prismq/
│   └── idea/
│       └── classification/
│           ├── __init__.py              # Package exports
│           ├── categories.py            # Category enums and models
│           ├── category_classifier.py   # Primary category classifier
│           └── story_detector.py        # Story detection classifier
├── tests/
│   ├── test_category_classifier.py      # Category classifier tests
│   ├── test_story_detector.py           # Story detector tests
│   └── test_story_detection_integration.py
├── setup.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements

- Python 3.8+
- No external API dependencies
- Pure Python implementation

## Troubleshooting

### Import Errors

If you encounter import errors:
```bash
# Make sure package is installed
pip install -e .

# Verify installation
python -c "from prismq.idea.classification import CategoryClassifier; print('OK')"
```

### Test Failures

```bash
# Run tests with verbose output
pytest -v

# Run specific test
pytest tests/test_category_classifier.py::TestCategoryClassifier::test_storytelling_classification -v
```

## Support

For questions, issues, or feature requests, please open an issue on GitHub:
- https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification/issues
