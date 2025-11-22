# PrismQ.T.Review.Script.Grammar

AI-powered grammar validation for scripts - Stage 14 (MVP-014) in the PrismQ workflow.

## Purpose

Provides comprehensive grammar checking for script content before proceeding to tone and content reviews. This module serves as a quality gate ensuring technical correctness of scripts.

## Features

- **Grammar Checking**: Subject-verb agreement, sentence structure
- **Punctuation Validation**: Proper use of periods, commas, etc.
- **Spelling Detection**: Common spelling errors with suggestions
- **Syntax Analysis**: Sentence structure issues
- **Tense Consistency**: Checks for consistent verb tense usage
- **Line-by-Line Analysis**: Precise error location with line references
- **JSON Output**: Machine-readable results for integration
- **Severity Levels**: Critical, High, Medium, Low prioritization

## Workflow Position

```
Stage 11: Script Writer (creates/refines script)
    ↓
Stage 14: Grammar Review (MVP-014) ← YOU ARE HERE
    ↓
    ├─→ [PASS] → Stage 15: Tone Review (MVP-015)
    └─→ [FAIL] → Return to Stage 11 with feedback
```

## Usage

### Basic Usage

```python
from T.Review.Script.Grammar import review_script_grammar

script = """The hero stands at the edge of the cliff.
Below, the ocean crashes against jagged rocks."""

review = review_script_grammar(script, script_id="script-001", script_version="v3")

print(f"Score: {review.overall_score}/100")
print(f"Passes: {review.passes}")

if not review.passes:
    for issue in review.issues:
        print(f"Line {issue.line_number}: {issue.explanation}")
        print(f"  Change '{issue.text}' to '{issue.suggestion}'")
```

### JSON Output

```python
from T.Review.Script.Grammar import review_script_grammar_to_json
import json

json_output = review_script_grammar_to_json(script, script_id="script-001")
data = json.loads(json_output)

print(f"Score: {data['overall_score']}")
print(f"Issues: {len(data['issues'])}")
```

### Structured Feedback

```python
from T.Review.Script.Grammar import review_script_grammar, get_grammar_feedback

review = review_script_grammar(script)
feedback = get_grammar_feedback(review)

print(feedback['summary'])
print(f"Next action: {feedback['next_action']}")

for issue in feedback['critical_issues']:
    print(f"Line {issue['line']}: {issue['explanation']}")
```

## API Reference

### Functions

#### `review_script_grammar(script_text, script_id, script_version, pass_threshold)`

Main function to review script grammar.

**Parameters:**
- `script_text` (str): The script text to review
- `script_id` (str): Identifier for the script (default: "script-001")
- `script_version` (str): Version of the script (default: "v3")
- `pass_threshold` (int): Minimum score to pass (default: 85)

**Returns:**
- `GrammarReview`: Review object with issues and scoring

#### `review_script_grammar_to_json(script_text, script_id, script_version, pass_threshold)`

Review script grammar and return JSON string.

**Returns:**
- `str`: JSON-formatted review results

#### `get_grammar_feedback(review)`

Get structured feedback from a grammar review.

**Parameters:**
- `review` (GrammarReview): The review object

**Returns:**
- `dict`: Structured feedback for script refinement

### Classes

#### `ScriptGrammarChecker`

Main grammar checking class.

**Methods:**
- `review_script(script_text, script_id, script_version)`: Perform grammar review
- `_check_spelling(line, line_num, review)`: Check spelling errors
- `_check_grammar(line, line_num, review)`: Check grammar errors
- `_check_punctuation(line, line_num, review)`: Check punctuation
- `_check_capitalization(line, line_num, review)`: Check capitalization
- `_check_tense_consistency(script_text, lines, review)`: Check tense consistency
- `_calculate_score(review)`: Calculate overall score
- `_generate_feedback(review)`: Generate feedback and summary

## Issue Types

- **GRAMMAR**: General grammar errors
- **PUNCTUATION**: Punctuation issues
- **SPELLING**: Spelling mistakes
- **SYNTAX**: Sentence structure problems
- **TENSE**: Tense inconsistency
- **AGREEMENT**: Subject-verb agreement errors
- **CAPITALIZATION**: Capitalization errors

## Severity Levels

- **CRITICAL**: Must be fixed (auto-fails review)
- **HIGH**: Should be fixed
- **MEDIUM**: Recommended to fix
- **LOW**: Minor issue

## Scoring System

- Start with 100 points
- Deduct points based on severity:
  - Critical: -15 points each
  - High: -8 points each
  - Medium: -4 points each
  - Low: -1 point each
- Pass threshold: 85 points (configurable)
- Any critical issue auto-fails the review

## Examples

See `_meta/examples/example_usage.py` for comprehensive examples including:
- Basic grammar review
- Error detection and feedback
- JSON output format
- Structured feedback for refinement
- Workflow integration

## Testing

Run tests with:
```bash
python -m pytest T/Review/Script/Grammar/_meta/tests/ -v
```

Tests cover:
- Grammatically correct scripts (should PASS)
- Grammatically incorrect scripts (should FAIL with specific issues)
- Line reference accuracy
- JSON output format
- Issue detection and categorization
- Edge cases and special formatting

## Dependencies

- Python 3.6+
- T.Review.Grammar (GrammarReview model)
- Standard library (re, json, dataclasses)

## Integration

```python
from T.Review.Script.Grammar import review_script_grammar

def stage_14_grammar_review(script_text, script_id, script_version):
    """Stage 14: Grammar Review in the workflow."""
    
    # Perform grammar review
    review = review_script_grammar(script_text, script_id, script_version)
    
    if review.passes:
        # Proceed to Stage 15: Tone Review
        return {
            'status': 'pass',
            'next_stage': 'tone_review',
            'review': review
        }
    else:
        # Return to Stage 11: Script Refinement
        return {
            'status': 'fail',
            'next_stage': 'script_refinement',
            'review': review,
            'feedback': get_grammar_feedback(review)
        }
```

## Future Enhancements

- Integration with advanced NLP libraries (spaCy, LanguageTool)
- AI-powered grammar suggestions
- Custom dictionary support
- Style guide enforcement
- Multi-language support
- Performance optimization for large scripts

## License

Part of the PrismQ project.
