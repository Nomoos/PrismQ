# Production Readiness Changes - Quick Reference

**Module**: `T/Review/Title/From/Content/Idea`  
**Script**: `_meta/scripts/05_PrismQ.T.Review.Title.By.Content.Idea`  
**Date**: 2025-12-23

---

## Required Changes Summary

### 🔴 CRITICAL - Must Fix Immediately

#### 1. Fix Script Paths
**Files**: `_meta/scripts/05_PrismQ.T.Review.Title.By.Content.Idea/Run.bat`, `Preview.bat`

**Current (WRONG)**:
```batch
python ..\..\..\T\Review\Title\ByContentIdea\src\review_title_by_content_idea_interactive.py
set MODULE_DIR=%SCRIPT_DIR%..\..\..\T\Review\Title\ByContentIdea
```

**Fixed (CORRECT)**:
```batch
python ..\..\..\T\Review\Title\From\Content\Idea\src\review_title_by_content_idea_interactive.py
set MODULE_DIR=%SCRIPT_DIR%..\..\..\T\Review\Title\From\Content\Idea
```

#### 2. Create Missing Interactive Script
**Create**: `T/Review/Title/From/Content/Idea/src/review_title_by_content_idea_interactive.py`

Based on pattern from: `T/Review/Title/From/Script/src/review_title_from_content_interactive.py`

#### 3. Add Parameter Validation
**File**: `T/Review/Title/From/Content/Idea/by_content_and_idea.py`
**Function**: `review_title_by_content_and_idea()`

Add at function start:
- Type validation (must be str)
- Empty/None checks
- Length limits (title: 1-200, content: 10-100000, idea: 10-5000 chars)
- Strip whitespace
- Raise ValueError/TypeError for invalid inputs

#### 4. Add Error Handling
**File**: `T/Review/Title/From/Content/Idea/by_content_and_idea.py`
**Location**: Wrap all analysis steps in try-except

Add:
- Try-except around each analysis function call
- Fallback AlignmentAnalysis with score=0 on error
- Safe division helper: `_safe_divide(n, d, default=0)`
- Log all errors with logging.error()
- Return minimal TitleReview with error metadata if complete failure

#### 5. Add Logging Infrastructure
**File**: `T/Review/Title/From/Content/Idea/by_content_and_idea.py`

Add:
```python
import logging
logger = logging.getLogger(__name__)

# Log at function entry with key params
# Log each analysis step completion with scores
# Log warnings for large inputs
# Log errors with exc_info=True
# Add timing decorator for performance monitoring
```

---

### 🟡 HIGH PRIORITY - Fix Soon

#### 6. Add Input Sanitization
**File**: `T/Review/Title/From/Content/Idea/by_content_and_idea.py`

Create function:
```python
def sanitize_text_input(text: str, max_length: int) -> str:
    # Remove null bytes
    # Normalize whitespace
    # Length check
    # Strip and return
```

Apply to all user inputs before processing.

#### 7. Fix ID Generation (Idempotency)
**File**: `T/Review/Title/From/Content/Idea/by_content_and_idea.py`
**Location**: Lines 550-552

**Current (WRONG)**:
```python
title_id = title_id or f"title-{abs(hash(title_text)) % 10000:04d}"
```

**Fixed (CORRECT)**:
```python
import hashlib

def _generate_deterministic_id(text: str, prefix: str) -> str:
    hash_hex = hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]
    return f"{prefix}-{hash_hex}"

title_id = title_id or _generate_deterministic_id(title_text, "title")
```

#### 8. Add Comprehensive Tests
**Create**: `T/Review/Title/From/Content/Idea/_meta/tests/test_validation_errors.py`

Add tests for:
- Empty inputs (should raise ValueError)
- Invalid types (should raise TypeError)
- Extremely long inputs (should raise ValueError)
- Special characters (should handle safely)
- Null bytes (should handle safely)
- Unicode (should work correctly)

**Create**: `T/Review/Title/From/Content/Idea/_meta/tests/test_performance.py`

Add tests with pytest.mark.timeout for:
- Large content (50KB) completes in <5 seconds
- Normal content completes in <1 second

---

### 🟢 MEDIUM PRIORITY - Improvements

#### 9. Add Performance Optimization
**File**: `T/Review/Title/From/Content/Idea/by_content_and_idea.py`

Add:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def extract_keywords_cached(text: str, max_keywords: int = 10) -> tuple:
    return tuple(extract_keywords(text, max_keywords))
```

Add warning for large texts:
```python
if len(content_text) > 50000:
    logger.warning(f"Large content: {len(content_text)} chars may be slow")
```

#### 10. Document Environment Requirements
**Update**: `T/Review/Title/From/Content/Idea/requirements.txt`

Add:
```txt
# Python version requirement: >=3.9

# Production dependencies
# (currently none - stdlib only)

# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-timeout>=2.1.0
black>=23.0.0
mypy>=1.0.0
pylint>=2.15.0
```

**Create**: `T/Review/Title/From/Content/Idea/pyproject.toml` or update existing:
```toml
[project]
requires-python = ">=3.9"
```

---

## Implementation Order

### Week 1: Critical Fixes
**Day 1-2**:
1. ✅ Fix Run.bat and Preview.bat paths (30 min)
2. ✅ Create interactive script (2-3 hours)
3. ✅ Test script execution manually (30 min)

**Day 3-4**:
4. ✅ Add parameter validation (2 hours)
5. ✅ Add error handling (2 hours)
6. ✅ Add logging infrastructure (2 hours)

**Day 5**:
7. ✅ Test all critical fixes (2 hours)
8. ✅ Code review and adjustments (2 hours)

### Week 2: Security & Testing
**Day 1-2**:
9. ✅ Add input sanitization (2 hours)
10. ✅ Fix ID generation (1 hour)
11. ✅ Add validation tests (3 hours)

**Day 3-4**:
12. ✅ Add error handling tests (2 hours)
13. ✅ Add performance tests (2 hours)
14. ✅ Add integration test (2 hours)

**Day 5**:
15. ✅ Code review and bug fixes (2 hours)
16. ✅ Documentation updates (2 hours)

### Week 3 (Optional): Optimization
**Day 1-2**:
17. ✅ Add caching (1 hour)
18. ✅ Optimize string operations (2 hours)
19. ✅ Add performance warnings (1 hour)

**Day 3-5**:
20. ✅ Performance benchmarking (2 hours)
21. ✅ Final testing and validation (3 hours)
22. ✅ Production deployment preparation (2 hours)

---

## Verification Checklist

### Before Marking Complete
- [ ] Run.bat executes without errors
- [ ] Preview.bat executes without errors
- [ ] All validation tests pass
- [ ] All error handling tests pass
- [ ] All performance tests pass
- [ ] Code coverage >90%
- [ ] No linting errors
- [ ] Type checking passes
- [ ] Manual testing successful
- [ ] Documentation updated

### Acceptance Criteria
- [ ] Script can run from command line
- [ ] Invalid inputs are rejected with clear errors
- [ ] Errors don't crash the program
- [ ] All operations are logged
- [ ] Reviews are idempotent (same input → same ID)
- [ ] All inputs are sanitized
- [ ] Security tests pass
- [ ] Performance is acceptable (<5s for large content)

---

## Quick Command Reference

### Run Tests
```bash
cd T/Review/Title/From/Content/Idea
python -m pytest _meta/tests/ -v
python -m pytest _meta/tests/ --cov=. --cov-report=html
```

### Run Script
```bash
cd _meta/scripts/05_PrismQ.T.Review.Title.By.Content.Idea
Run.bat          # Full mode (saves to DB)
Preview.bat      # Preview mode (no save)
```

### Type Checking
```bash
cd T/Review/Title/From/Content/Idea
mypy by_content_and_idea.py title_review.py
```

### Linting
```bash
cd T/Review/Title/From/Content/Idea
pylint by_content_and_idea.py title_review.py
black by_content_and_idea.py title_review.py --check
```

---

## Related Files

### Must Modify
- `_meta/scripts/05_PrismQ.T.Review.Title.By.Content.Idea/Run.bat`
- `_meta/scripts/05_PrismQ.T.Review.Title.By.Content.Idea/Preview.bat`
- `T/Review/Title/From/Content/Idea/by_content_and_idea.py`
- `T/Review/Title/From/Content/Idea/requirements.txt`

### Must Create
- `T/Review/Title/From/Content/Idea/src/review_title_by_content_idea_interactive.py`
- `T/Review/Title/From/Content/Idea/_meta/tests/test_validation_errors.py`
- `T/Review/Title/From/Content/Idea/_meta/tests/test_performance.py`

### Should Update
- `T/Review/Title/From/Content/Idea/README.md` (document changes)
- `T/Review/Title/From/Content/Idea/pyproject.toml` (Python version requirement)

---

## Contact & Questions

For questions about these changes:
1. Review detailed analysis: `ISSUE-IMPL-005-05_PRODUCTION_READINESS_CHANGES.md`
2. Check coding guidelines: `_meta/docs/guidelines/CODING_GUIDELINES.md`
3. Consult PR checklist: `_meta/docs/guidelines/PR_CODE_REVIEW_CHECKLIST.md`

---

**Document Version**: 1.0  
**Created**: 2025-12-23  
**Status**: Ready for Implementation

---

## ⚠️ Important Note on Directory Structure

**Current Directory**: `T/Review/Title/From/Script/Idea` (currently exists on filesystem)  
**Correct Directory**: `T/Review/Title/From/Content/Idea` (should be renamed)

The directory is currently named `Script` but should be renamed to `Content` for consistency with:
- The function name: `review_title_by_content_and_idea()`
- The correct terminology: "Content" (Script is obsolete)
- The coding guidelines: Content refers to content artifacts

**Action Required**: Rename the directory from `Script` to `Content` before implementing the fixes described in this document.

---
