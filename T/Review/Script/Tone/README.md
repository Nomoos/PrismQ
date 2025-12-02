# PrismQ.T.Review.Script.Tone

Script tone and style review module for the PrismQ workflow.

## Purpose

This module implements the script tone review stage that:
1. Selects the Story with lowest current script version in state `PrismQ.T.Review.Script.Tone`
   (current version = highest version number for that story_id)
2. Gets the Script (latest version) associated with the Story
3. Reviews the script for tone and style consistency
4. Outputs a Review model (text, score, created_at) and saves it to database
5. Links the Review to the Script via `Script.review_id` FK
6. Updates Story state based on review acceptance

## Selection Logic

The module selects the Story whose Script has the **lowest current version number**:
- Current version = MAX(version) across all scripts for the same story_id
- If Story A has script versions 0,1,2 (max=2) and Story B has versions 0,1 (max=1), Story B is selected

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

**Script references Review directly via FK** (`Script.review_id` → `Review.id`).

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
    print(f"Script reviewed: {result.script.id}")
    print(f"Script now references review: {result.script.review_id}")
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
└── src/
    ├── __init__.py
    └── review_script_tone.py  # Main implementation
```

## Configuration

- `ACCEPTANCE_THRESHOLD`: Score threshold (0-100) for accepting a script
  - Default: 75
  - Scripts scoring >= 75 proceed to editing review
  - Scripts scoring < 70 are sent back for rewrite

## Related Components

- `T/Database/models/review.py` - Review model
- `T/Database/models/script.py` - Script model (with `review_id` FK)
- `T/Database/repositories/story_repository.py` - Story repository
- `T/Database/repositories/script_repository.py` - Script repository
- `T/State/constants/state_names.py` - State constants
- `T/Review/Script/From/Title/` - Similar review implementation pattern
