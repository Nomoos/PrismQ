# PrismQ.T.Review.Script.Tone

Script tone and style review module for the PrismQ workflow.

## Purpose

This module implements the script tone review stage that:
1. Selects the oldest Story with state `PrismQ.T.Review.Script.Tone`
2. Reviews the script for tone and style consistency
3. Outputs a Review model (text, score, created_at)
4. Updates Story state based on review acceptance

## State Transitions

- If review **doesn't accept** script → `PrismQ.T.Script.From.Title.Review.Script` (for rewrite)
- If review **accepts** script → `PrismQ.T.Review.Script.Editing` (proceed to editing review)

## Review Output

The module outputs a simple Review model:

```
Review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
```

Story references Review via StoryReview linking table.

## Tone Evaluation

The tone review evaluates:
- Emotional intensity consistency
- Style alignment with target tone (if specified)
- Voice/POV consistency throughout the script
- Overall tone appropriateness

## Usage

```python
from T.Review.Script.Tone import (
    process_review_script_tone,
    ReviewResult
)

# Using database connection
result = process_review_script_tone(conn)
if result:
    print(f"Review created with score: {result.review.score}")
    print(f"Story state changed to: {result.new_state}")
    print(f"Accepted: {result.accepted}")
```

## Module Structure

```
T/Review/Script/Tone/
├── __init__.py              # Module exports
├── README.md                # This file
├── _meta/
│   └── tests/
│       └── test_review_script_tone.py
└── src/
    ├── __init__.py
    └── review_script_tone.py  # Main implementation
```

## Configuration

- `ACCEPTANCE_THRESHOLD`: Score threshold (0-100) for accepting a script
  - Default: 70
  - Scripts scoring >= 70 proceed to editing review
  - Scripts scoring < 70 are sent back for rewrite

## Related Components

- `T/Database/models/review.py` - Review model
- `T/Database/repositories/story_repository.py` - Story repository
- `T/State/constants/state_names.py` - State constants
- `T/Review/Script/From/Title/` - Similar review implementation pattern
