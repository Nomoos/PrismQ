# Script Consistency Review (MVP-017)

**Module**: `PrismQ.T.Review.Script.Consistency`  
**Stage**: 17 in the iterative co-improvement workflow  
**Dependencies**: MVP-016 (Content Review) ✅  
**Next Stage**: MVP-018 (Editing Review)

## Purpose

The Script Consistency Review module provides AI-powered consistency validation for scripts, checking for:
- **Character name consistency** - Detecting variations in character names (e.g., "John" vs "Johnny")
- **Timeline verification** - Tracking temporal markers and event sequences
- **Location tracking** - Monitoring location mentions and continuity
- **Internal contradictions** - Identifying logical inconsistencies
- **Detail consistency** - Checking for matching repeated details

## Workflow Position

```
Stage 16: Content Review (MVP-016) ✅
    ↓
Stage 17: Consistency Review (MVP-017) ← YOU ARE HERE
    ↓
    ├─ PASS (score ≥ 80, no critical issues) → Stage 18: Editing Review
    └─ FAIL (score < 80 or critical issues) → Stage 11: Script Refinement
```

## Key Features

### Consistency Checks
- **Character Name Tracking**: Identifies potential name variations
- **Timeline Analysis**: Tracks temporal markers and sequences
- **Location Monitoring**: Records location mentions
- **Contradiction Detection**: Identifies logical inconsistencies
- **Pass/Fail Logic**: Score-based quality gate (default threshold: 80/100)

### Severity Levels
- **CRITICAL**: Must be fixed - breaks story logic
- **HIGH**: Should be fixed - major inconsistency
- **MEDIUM**: Recommended to fix - noticeable issue
- **LOW**: Minor issue - polish

### Scoring
- **Character Score**: Character name consistency (0-100)
- **Timeline Score**: Timeline consistency (0-100)
- **Location Score**: Location consistency (0-100)
- **Detail Score**: Detail and contradiction consistency (0-100)
- **Overall Score**: Weighted average of all scores

## Installation

```bash
# No additional dependencies required
# Module is part of PrismQ.T.Review.Script package
```

## Quick Start

```python
from T.Review.Script.Consistency import review_script_consistency

# Review a script
script = """John walked into the room.
He looked around nervously.
Johnny picked up the book."""

review = review_script_consistency(script, "script-001", "v3")

print(f"Score: {review.overall_score}/100")
print(f"Passes: {review.passes}")

# Check for issues
for issue in review.issues:
    print(f"{issue.location}: {issue.description}")
```

## Usage Examples

### Example 1: Basic Review

```python
from T.Review.Script.Consistency import review_script_consistency

script = """Sarah walked into the library.
The library was quiet and peaceful.
Sarah found a book and sat down."""

review = review_script_consistency(script, "script-001", "v3")

print(f"Overall Score: {review.overall_score}/100")
print(f"Character Score: {review.character_score}/100")
print(f"Passes: {'YES' if review.passes else 'NO'}")
```

### Example 2: Detecting Character Inconsistencies

```python
script = """John entered the room.
Johnny looked around.
John left the building."""

review = review_script_consistency(script, "script-002", "v3")

# Get character-specific issues
character_issues = review.get_character_issues()
for issue in character_issues:
    print(f"{issue.description}: {issue.details}")
```

### Example 3: JSON Output

```python
from T.Review.Script.Consistency import review_script_consistency_to_json

script = "Alice met Bob. They talked."

json_result = review_script_consistency_to_json(script, "script-003", "v3")
print(json_result)
```

### Example 4: Structured Feedback

```python
from T.Review.Script.Consistency import (
    review_script_consistency,
    get_consistency_feedback
)

script = "..."
review = review_script_consistency(script)
feedback = get_consistency_feedback(review)

if not feedback['passes']:
    print("Script needs revision:")
    for issue in feedback['high_priority_issues']:
        print(f"  {issue['location']}: {issue['description']}")
```

### Example 5: Custom Threshold

```python
from T.Review.Script.Consistency import ScriptConsistencyChecker

script = "..."

# Use stricter threshold
checker = ScriptConsistencyChecker(pass_threshold=85)
review = checker.review_script(script, "script-005", "v3")
```

## API Reference

### Main Classes

#### `ConsistencyReview`
Data model for consistency review results.

**Attributes:**
- `script_id`: str - Script identifier
- `script_version`: str - Script version (v3, v4, etc.)
- `overall_score`: int - Overall consistency score (0-100)
- `character_score`: int - Character name consistency (0-100)
- `timeline_score`: int - Timeline consistency (0-100)
- `location_score`: int - Location consistency (0-100)
- `detail_score`: int - Detail consistency (0-100)
- `passes`: bool - Whether review passes
- `issues`: List[ConsistencyIssue] - Detected issues
- `characters_found`: Set[str] - Tracked character names
- `locations_found`: Set[str] - Tracked locations

**Methods:**
- `add_issue(issue: ConsistencyIssue)` - Add an issue
- `get_issues_by_severity(severity)` - Filter by severity
- `get_issues_by_type(issue_type)` - Filter by type
- `get_character_issues()` - Get character name issues
- `get_timeline_issues()` - Get timeline issues
- `get_location_issues()` - Get location issues
- `to_dict()` - Convert to dictionary
- `from_dict(data)` - Create from dictionary

#### `ConsistencyIssue`
Individual consistency issue.

**Attributes:**
- `issue_type`: ConsistencyIssueType - Type of issue
- `severity`: ConsistencySeverity - Severity level
- `location`: str - Location in script
- `description`: str - Issue description
- `details`: str - Specific details
- `suggestion`: str - Fix suggestion
- `confidence`: int - AI confidence (0-100)

#### `ScriptConsistencyChecker`
Main checker class for reviewing scripts.

**Methods:**
- `review_script(script_text, script_id, script_version)` - Review a script

### Convenience Functions

#### `review_script_consistency()`
```python
review_script_consistency(
    script_text: str,
    script_id: str = "script-001",
    script_version: str = "v3",
    pass_threshold: int = 80
) -> ConsistencyReview
```

#### `review_script_consistency_to_json()`
```python
review_script_consistency_to_json(
    script_text: str,
    script_id: str = "script-001",
    script_version: str = "v3",
    pass_threshold: int = 80
) -> str
```

#### `get_consistency_feedback()`
```python
get_consistency_feedback(
    review: ConsistencyReview
) -> Dict[str, Any]
```

## Issue Types

- `CHARACTER_NAME` - Character name inconsistency
- `TIMELINE` - Timeline contradiction
- `LOCATION` - Location inconsistency
- `DETAIL` - Repeated detail mismatch
- `CONTRADICTION` - Internal contradiction
- `CONTINUITY` - Story continuity issue

## Severity Levels

- `CRITICAL` - Must be fixed - breaks story logic
- `HIGH` - Should be fixed - major inconsistency
- `MEDIUM` - Recommended to fix - noticeable issue
- `LOW` - Minor issue - polish

## Pass/Fail Criteria

A script **FAILS** if:
1. Any critical issues are present, OR
2. 3 or more high severity issues are present, OR
3. Overall score < pass threshold (default 80)

A script **PASSES** if:
- No critical issues
- Fewer than 3 high severity issues
- Overall score ≥ pass threshold

## Testing

```bash
# Run tests
python -m pytest T/Review/Script/Consistency/_meta/tests/ -v

# Run specific test
python -m pytest T/Review/Script/Consistency/_meta/tests/test_consistency_review.py::TestConsistencyReviewBasic -v
```

## Examples

See `_meta/examples/example_usage.py` for comprehensive examples:

```bash
python T/Review/Script/Consistency/_meta/examples/example_usage.py
```

## Integration with PrismQ Workflow

```python
# Stage 17: Consistency Review
from T.Review.Script.Consistency import review_script_consistency

# Review script after content review passes
review = review_script_consistency(script_text, script_id, "v3")

if review.passes:
    # Proceed to Stage 18: Editing Review (MVP-018)
    print("✓ Proceed to Editing Review")
else:
    # Return to Stage 11: Script Refinement
    print("✗ Return to Script Refinement")
    print(f"Issues to fix: {review.primary_concerns}")
```

## Development

### Project Structure
```
T/Review/Script/Consistency/
├── __init__.py                    # Module exports
├── consistency_review.py          # Main implementation
├── README.md                      # This file
└── _meta/
    ├── examples/
    │   └── example_usage.py       # Usage examples
    └── tests/
        └── test_consistency_review.py  # Test suite
```

### Running the Module Directly
```bash
# Run with example script
python T/Review/Script/Consistency/consistency_review.py
```

## License

Part of PrismQ - Iterative Co-Improvement System for Creative Content

## See Also

- MVP-016: Content Review (T.Review.Content)
- MVP-018: Editing Review (T.Review.Script.Editing)
- PrismQ Workflow Documentation
