# Script Editing Review (MVP-018)

**Stage 18**: AI-powered editing validation for script clarity, flow, and conciseness.

## Purpose

The Editing Review module validates scripts for:
- **Clarity**: Clear, understandable sentences
- **Flow**: Smooth transitions and coherent structure
- **Redundancy**: Elimination of repetitive or unnecessary content
- **Wordiness**: Concise expression without verbose phrases
- **Structure**: Well-organized paragraphs and narrative flow

## Workflow Position

```
Stage 17: Consistency Review (MVP-017)
    ↓ PASSES
Stage 18: Editing Review (MVP-018) ← YOU ARE HERE
    ↓ PASSES
Stage 19: Title Readability (MVP-019)
```

If the editing review **FAILS**, the script returns to Script Refinement (Stage 11) with detailed feedback.

## Features

### Issue Detection
- ✅ **Wordiness**: Detects and suggests concise alternatives for verbose phrases
- ✅ **Redundancy**: Identifies repeated words and redundant expressions
- ✅ **Clarity**: Flags passive voice and overly complex sentences
- ✅ **Transitions**: Detects weak transitions between sentences
- ✅ **Structure**: Analyzes overall paragraph flow and variety

### Severity Levels
- **CRITICAL**: Must be fixed for clarity
- **HIGH**: Should be addressed for quality
- **MEDIUM**: Recommended improvements
- **LOW**: Minor suggestions

### Output Formats
- ✅ Python objects (EditingReview)
- ✅ JSON for API integration
- ✅ Structured feedback for script refinement

## Quick Start

```python
from T.Review.Script.Editing import review_script_editing

# Review a script
script = """In order to complete this task, we proceed carefully."""
review = review_script_editing(script, script_id="script-001")

# Check results
print(f"Score: {review.overall_score}/100")
print(f"Passes: {review.passes}")

# Get issues
for issue in review.issues:
    print(f"Line {issue.line_number}: {issue.explanation}")
    print(f"  Suggestion: {issue.suggestion}")
```

## API Reference

### Main Functions

#### `review_script_editing(script_text, script_id, script_version, pass_threshold)`
Reviews a script for editing quality.

**Parameters:**
- `script_text` (str): The script text to review
- `script_id` (str): Identifier for the script (default: "script-001")
- `script_version` (str): Version of the script (default: "v3")
- `pass_threshold` (int): Minimum score to pass (default: 85)

**Returns:** `EditingReview` object

#### `review_script_editing_to_json(script_text, script_id, script_version, pass_threshold)`
Reviews a script and returns JSON string.

**Returns:** JSON string with review results

#### `get_editing_feedback(review)`
Extracts structured feedback from a review.

**Returns:** Dictionary with formatted feedback

### Data Models

#### EditingReview
Main review object containing:
- `script_id`: Script identifier
- `overall_score`: Score from 0-100
- `passes`: Whether review passes
- `issues`: List of detected issues
- `summary`: Overall assessment
- `primary_concerns`: Main issues to address
- `quick_fixes`: Easy improvements

#### EditingIssue
Individual issue with:
- `issue_type`: Type of issue (clarity, redundancy, etc.)
- `severity`: Critical, high, medium, or low
- `line_number`: Location in script
- `text`: Problematic text
- `suggestion`: Improvement suggestion
- `explanation`: Why this needs editing

## Examples

See `_meta/examples/example_usage.py` for complete examples including:
1. Well-edited script (passes)
2. Wordy script (needs editing)
3. Redundant script
4. JSON output
5. Structured feedback
6. Custom thresholds

## Testing

Run tests with:
```bash
pytest T/Review/Script/Editing/_meta/tests/test_script_editing_review.py -v
```

Test coverage:
- ✅ Well-edited scripts pass
- ✅ Issue detection (wordiness, redundancy, clarity, transitions)
- ✅ Score calculation
- ✅ JSON serialization
- ✅ Feedback generation
- ✅ Edge cases (empty scripts, dialogue, formatting)

## Integration

### With Quality Review Pipeline
```python
# After Consistency Review (Stage 17)
from T.Review.Script.Editing import review_script_editing

review = review_script_editing(script_v3)

if review.passes:
    # Proceed to Title Readability (Stage 19)
    proceed_to_title_readability()
else:
    # Return to Script Refinement
    refine_script(review.issues)
```

### Custom Configuration
```python
# Adjust threshold for different content types
review = review_script_editing(
    script,
    script_id="technical-001",
    pass_threshold=75  # More lenient for technical content
)
```

## Common Issues Detected

### Wordiness
- "in order to" → "to"
- "due to the fact that" → "because"
- "at this point in time" → "now"
- "make a decision" → "decide"

### Redundancy
- "very unique" → "unique"
- "past history" → "history"
- "close proximity" → "proximity"
- "exact same" → "same"

### Clarity
- Passive voice in long sentences
- Sentences over 30 words
- Complex nested structures

### Transitions
- Weak transitions like "and then", "and so"
- Missing transitions between paragraphs
- Overuse of simple connectors

## Configuration

### Pass Threshold
Default: 85 (out of 100)

Adjust based on:
- Content type (narrative, technical, dialogue-heavy)
- Target audience
- Production stage

### Scoring
- Critical issues: -15 points each
- High severity: -10 points each
- Medium severity: -5 points each
- Low severity: -2 points each

## Notes

- Dialogue lines are handled differently (passive voice checks skipped)
- Screenplay formatting (INT., EXT.) is ignored
- Multiple issues can be detected on the same line
- Suggestions preserve original case and formatting

## See Also

- [MVP-017: Consistency Review](../../Consistency/README.md)
- [MVP-019: Title Readability](../../../Title/Readability/README.md)
- [Script Refinement (Stage 11)](../../../../Script/Refinement/README.md)

## Status

✅ **IMPLEMENTED** - MVP-018 Complete
- Module: `PrismQ.T.Review.Script.Editing`
- Tests: 21 passing
- Integration: Ready for Stage 18
