# Tests

Module test suite.

## Structure

- Mirror the structure of the `src/` directory
- Use `test_*.py` naming convention
- Use pytest for testing

## Running Tests

```bash
# From module root
pytest tests/

# With coverage
pytest --cov=src --cov-report=html tests/
```

## Guidelines

- Write tests for all public APIs
- Aim for high code coverage
- Use fixtures for common setup
- Keep tests isolated and independent
