# PrismQ.T.Content.From.Title.Review.Script

Module for generating improved script versions based on review feedback.

**Status**: ✅ Production Ready

## Overview

This module takes:
- Original script (any version)
- Title (corresponding version)
- Script review feedback
- Title review feedback

And generates:
- Improved script (next version) that addresses review feedback
- Maintains narrative quality while improving alignment

## Workflow Position

```
Script vN + Title vN + Reviews → Script v(N+1) (improved)

Examples:
- MVP-007: Script v1 + Title v1 + Reviews → Script v2
- MVP-010: Script v2 + Title v2 + Reviews → Script v3
- Iteration: Script v3 + Title v3 + Reviews → Script v4, v5, v6, v7, etc.
```

## Production Readiness

This module includes:
- ✅ **Input Validation**: Comprehensive validation of all inputs
- ✅ **Error Handling**: Graceful degradation on failures
- ✅ **Logging**: Structured logging with performance metrics
- ✅ **Security**: Input sanitization and length limits
- ✅ **Testing**: 42 comprehensive tests (100% pass rate)
- ✅ **Idempotency**: Deterministic IDs for safe re-runs
- ✅ **Performance**: Timing metrics and large text warnings

See `ISSUE-IMPL-009-PRODUCTION-READINESS.md` for complete details.

## Usage

### Interactive Mode
```bash
python script_from_review_interactive.py
```

### Preview Mode (no database save)
```bash
python script_from_review_interactive.py --preview --debug
```

### Using Batch Files (Windows)
```batch
_meta/scripts/09_PrismQ.T.Content.From.Title.Review.Script/Run.bat
_meta/scripts/09_PrismQ.T.Content.From.Title.Review.Script/Preview.bat
```

### Programmatic Usage
```python
from script_improver import ScriptImprover

improver = ScriptImprover()
result = improver.improve_content(
    original_content="Your script text...",
    title_text="Your Title",
    script_review=review_object,
    original_version_number="v1",
    new_version_number="v2",
)

print(f"Improved: {result.new_version.text}")
print(f"Rationale: {result.rationale}")
```

## Validation & Security

### Input Limits
- Script content: 10 - 1,000,000 characters
- Title: 3 - 500 characters
- Review scores: 0 - 100

### Security Features
- Null byte removal (database protection)
- Length limits (DoS protection)
- Type validation (prevents type confusion)
- Input sanitization (XSS/injection protection)

## Testing

Run all tests:
```bash
python -m pytest T/Content/From/Title/Review/Script/_meta/tests/ -v
```

Run with coverage:
```bash
python -m pytest T/Content/From/Title/Review/Script/_meta/tests/ --cov
```

**Test Coverage**: 42 tests covering validation, error handling, sanitization, and edge cases.

## Performance

Typical execution times:
- Small scripts (<10KB): <0.1s
- Medium scripts (10-50KB): 0.1-0.5s  
- Large scripts (50-100KB): 0.5-2s
- Very large (100KB-1MB): 2-10s (with warning)

## Dependencies

**Production**: None (Python stdlib only)
**Testing**: pytest, pytest-cov (see requirements.txt)

## Logging

The module uses Python's standard logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

Log levels:
- **INFO**: Key operations, completions
- **DEBUG**: Detailed flow, validation
- **WARNING**: Recoverable errors, large inputs
- **ERROR**: Failures with context
