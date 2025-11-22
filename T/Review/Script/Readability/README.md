# PrismQ.T.Review.Script.Readability

**Stage 20 (MVP-020): Script Readability Review for Voiceover Suitability**

AI-powered voiceover readability validation for scripts. This module checks natural flow, pronunciation, pacing, and spoken-word clarity to ensure scripts are perfectly suited for narration.

## Purpose

The Script Readability Review is the **final quality gate** for scripts before they proceed to Expert Review (Stage 21). It focuses 100% on **spoken-word suitability** and voiceover delivery.

### What This Module Checks

- **Pronunciation**: Difficult words, consonant clusters, hard-to-speak combinations
- **Pacing**: Sentence length, breathing points, natural pauses
- **Flow**: Natural rhythm, tongue twisters, alliteration issues
- **Mouthfeel**: Ease of speaking, complex words, formal language
- **Clarity**: How the script sounds when spoken (not just read)

## Workflow Position

```
Stage 18: Editing Review → PASS
    ↓
Stage 19: Title Readability → PASS
    ↓
Stage 20: Script Readability (THIS MODULE)
    ↓ PASS
Stage 21: Expert Review
    OR
    ↓ FAIL
Stage 11: Script Refinement (with voiceover-focused feedback)
```

## Usage

### Basic Usage

```python
from T.Review.Script.Readability import review_script_readability

script = """Your script text here.
Make sure it flows naturally when spoken aloud.
Check for breathing points and easy pronunciation."""

review = review_script_readability(
    script_text=script,
    script_id="script-001",
    script_version="v3",
    pass_threshold=85  # Default: 85
)

print(f"Overall Score: {review.overall_score}/100")
print(f"Passes: {review.passes}")
print(f"Summary: {review.summary}")

# Check specific scores
print(f"Pronunciation: {review.pronunciation_score}/100")
print(f"Pacing: {review.pacing_score}/100")
print(f"Flow: {review.flow_score}/100")
print(f"Mouthfeel: {review.mouthfeel_score}/100")

# Review issues
for issue in review.issues:
    print(f"Line {issue.line_number}: {issue.explanation}")
    print(f"  Suggestion: {issue.suggestion}")
```

### JSON Output

```python
from T.Review.Script.Readability import review_script_readability_to_json

json_result = review_script_readability_to_json(
    script_text=script,
    script_id="script-001",
    script_version="v3"
)

# Returns JSON string with complete review data
```

### Structured Feedback

```python
from T.Review.Script.Readability import (
    review_script_readability,
    get_readability_feedback
)

review = review_script_readability(script, "script-001", "v3")
feedback = get_readability_feedback(review)

if not feedback['passes']:
    print("Voiceover improvements needed:")
    for issue in feedback['high_priority_issues']:
        print(f"  Line {issue['line']}: {issue['explanation']}")
```

## Review Model

### ReadabilityReview

Main review object containing:

- **Scores** (0-100):
  - `overall_score`: Overall readability score
  - `pronunciation_score`: Pronunciation ease
  - `pacing_score`: Pacing and rhythm quality
  - `flow_score`: Natural flow
  - `mouthfeel_score`: Ease of speaking
  
- **Pass/Fail**:
  - `passes`: Boolean (True if score >= threshold)
  - `pass_threshold`: Minimum score to pass (default: 85)
  
- **Issues**:
  - `issues`: List of all ReadabilityIssue objects
  - `critical_count`, `high_count`, `medium_count`, `low_count`
  
- **Feedback**:
  - `summary`: Overall assessment
  - `primary_concerns`: Main issues to address
  - `voiceover_notes`: Specific voiceover delivery notes

### ReadabilityIssue

Individual issue with:

- `issue_type`: PRONUNCIATION, PACING, FLOW, MOUTHFEEL, BREATH, TONGUE_TWISTER, etc.
- `severity`: CRITICAL, HIGH, MEDIUM, LOW
- `line_number`: Where the issue occurs
- `text`: The problematic text
- `suggestion`: How to improve it
- `explanation`: Why it's a readability issue
- `confidence`: AI confidence (0-100)

## What Gets Detected

### 1. Pronunciation Issues

- Difficult consonant clusters (e.g., "strengths", "sixths")
- Hard-to-pronounce words
- Complex sound combinations

**Example:**
```
Issue: "The phenomenon of phosphorescence perplexed physicists"
Suggestion: "The glowing effect puzzled scientists"
```

### 2. Tongue Twisters

- Alliteration with difficult sounds (p, s, t, f, b)
- Repetitive sound patterns

**Example:**
```
Issue: "She sells seashells by the seashore"
Suggestion: "Reduce repetition of 's' sound"
```

### 3. Pacing Issues

- Sentences longer than 20 words
- No breathing points in long sentences
- Poor rhythm

**Example:**
```
Issue: "This is a very long sentence that goes on and on without any pauses..."
Suggestion: "Break into shorter sentences or add natural pauses"
```

### 4. Breathing Points

- Segments longer than 15 words without pause
- Missing commas or natural breaks

**Example:**
```
Issue: "We walked down the street and then we saw the building and entered"
Suggestion: "Add a natural pause or comma after 15 words"
```

### 5. Complex Words

- Formal, academic language
- Hard-to-speak words

**Examples:**
- "phenomenon" → "effect"
- "methodology" → "method"
- "quintessential" → "perfect"
- "aforementioned" → "mentioned"

## Scoring System

### Overall Score Calculation

```
overall_score = (pronunciation_score × 0.30) +
                (pacing_score × 0.25) +
                (flow_score × 0.25) +
                (mouthfeel_score × 0.20)
```

### Pass/Fail Rules

- **PASS**: Overall score ≥ 85 AND no critical issues
- **FAIL**: Overall score < 85 OR any critical issue

### Severity Impact

- **CRITICAL**: -20 points (auto-fail)
- **HIGH**: -12 points
- **MEDIUM**: -6 points
- **LOW**: -2 points

## Integration

### In Workflow

```python
# After Editing Review passes...
from T.Review.Script.Readability import review_script_readability

readability_review = review_script_readability(
    script_text=script_v3,
    script_id=script_id,
    script_version="v3"
)

if readability_review.passes:
    # Proceed to Stage 21: Expert Review
    expert_review = perform_expert_review(script_v3)
else:
    # Return to Script Refinement with voiceover feedback
    refined_script = refine_script(
        script_v3,
        readability_feedback=readability_review
    )
```

### With Database

```python
# Store review results
review_data = readability_review.to_dict()
db.store_readability_review(script_id, review_data)

# Retrieve later
review = ReadabilityReview.from_dict(review_data)
```

## Dependencies

- **MVP-019**: Title Readability (must pass before this stage)
- **MVP-018**: Script Editing Review (must pass before this stage)

## Module Structure

```
T/Review/Script/Readability/
├── __init__.py                          # Module exports
├── script_readability_review.py         # Main implementation
├── README.md                            # This file
└── _meta/
    ├── tests/
    │   ├── __init__.py
    │   └── test_script_readability_review.py
    └── examples/
        └── example_usage.py
```

## Testing

Run tests:
```bash
cd /home/runner/work/PrismQ/PrismQ
python -m pytest T/Review/Script/Readability/_meta/tests/ -v
```

Run example:
```bash
cd /home/runner/work/PrismQ/PrismQ
python T/Review/Script/Readability/_meta/examples/example_usage.py
```

## Key Differences from Other Reviews

Unlike other review modules (Grammar, Consistency, Editing), Script Readability focuses specifically on:

1. **Voiceover delivery** - How it sounds when spoken
2. **Pronunciation ease** - Can a narrator say it clearly?
3. **Natural pacing** - Does it flow when read aloud?
4. **Breathing comfort** - Can narrator deliver without running out of breath?

This is the **final script quality gate** before expert review.

## Configuration

### Pass Threshold

Default: 85 (can be adjusted)

```python
review = review_script_readability(
    script_text=script,
    script_id="script-001",
    pass_threshold=90  # Stricter requirement
)
```

### Customization

The `ScriptReadabilityChecker` class can be extended to add custom checks:

```python
from T.Review.Script.Readability import ScriptReadabilityChecker

class CustomReadabilityChecker(ScriptReadabilityChecker):
    def __init__(self, pass_threshold=85):
        super().__init__(pass_threshold)
        # Add custom difficult words
        self.COMPLEX_WORDS.update({
            'utilize': 'use',
            'facilitate': 'help'
        })
```

## Status

**Status**: ✅ IMPLEMENTED (MVP-020)  
**Priority**: MEDIUM  
**Effort**: 0.5 days  
**Stage**: 20 of 23  
**Dependencies**: MVP-019 (Title Readability)

## Next Stage

After passing Script Readability Review:
→ **Stage 21 (MVP-021)**: Expert Review (GPT-based comprehensive review)
