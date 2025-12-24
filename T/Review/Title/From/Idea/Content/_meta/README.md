# T/Review/Title/ByScriptAndIdea - Module Metadata

## Testing

### Setup Test Environment

Install test dependencies:
```bash
cd /path/to/PrismQ/T/Review/Title/ByScriptAndIdea
pip install -r requirements.txt
```

Or install with optional test dependencies:
```bash
pip install ".[test]"
```

### Running Tests

From the PrismQ root directory:
```bash
# Set PYTHONPATH to project root
export PYTHONPATH=/path/to/PrismQ

# Run all tests
python -m pytest T/Review/Title/ByScriptAndIdea/_meta/tests/ -v

# Run with coverage
python -m pytest T/Review/Title/ByScriptAndIdea/_meta/tests/ --cov=T.Review.Title.ByScriptAndIdea -v
```

From the module directory:
```bash
cd T/Review/Title/ByScriptAndIdea
export PYTHONPATH=/path/to/PrismQ
pytest _meta/tests/ -v
```

### Running Examples

From the PrismQ root directory:
```bash
export PYTHONPATH=/path/to/PrismQ
python T/Review/Title/ByScriptAndIdea/_meta/examples/example_usage.py
```

## Directory Structure

```
_meta/
├── docs/          # Documentation files
├── examples/      # Example usage scripts
│   └── example_usage.py
├── tests/         # Test suite
│   ├── __init__.py
│   └── test_title_review.py
└── README.md      # This file
```

## Examples

See `examples/example_usage.py` for comprehensive usage examples including:
- Basic title review creation
- Complete review with full context
- Serialization (to_dict/from_dict)
- Workflow integration (Stage 4 → Stage 6)

## Tests

See `tests/test_title_review.py` for test coverage including:
- Basic functionality tests
- Complete review tests
- Category score tests
- Improvement point tests
- Alignment summary tests
- Engagement metrics tests
- Length assessment tests
- Serialization tests

## Issues

See `../../../_meta/issues/` for module-level issues and planning.
