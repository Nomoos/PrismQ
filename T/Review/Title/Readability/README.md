# PrismQ.T.Review.Title.Readability

Title Readability Review module for the PrismQ workflow.

## Overview

This module implements the title readability review workflow stage that:
1. Selects the oldest Story with state `PrismQ.T.Review.Title.Readability`
2. Reviews the title for voiceover readability
3. Outputs a Review model (text, score, created_at)
4. Updates the Story state based on review acceptance

## State Transitions

- **If review doesn't accept title** → `PrismQ.T.Title.From.Script.Review.Title` (return to title refinement)
- **If review accepts title** → `PrismQ.T.Review.Script.Readability` (proceed to script readability review)

## Review Output Schema

```sql
Review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
```

## Usage

```python
from T.Review.Title.Readability.src import (
    process_review_title_readability,
    ReviewResult
)

# Process a single story
result = process_review_title_readability(db_connection)
if result:
    print(f"Review score: {result.review.score}")
    print(f"Accepted: {result.accepted}")
    print(f"New state: {result.new_state}")

# Process all pending reviews
from T.Review.Title.Readability.src import process_all_pending_reviews
results = process_all_pending_reviews(db_connection)
print(f"Processed {len(results)} stories")
```

## Readability Evaluation Criteria

The title readability evaluation checks:
- **Length appropriateness**: Optimal word count for voiceover
- **Pronunciation difficulty**: Detects difficult consonant clusters
- **Word complexity**: Flags long/complex words
- **Flow and rhythm**: Checks for tongue-twister patterns
- **Engagement elements**: Rewards engaging words

## Constants

- `ACCEPTANCE_THRESHOLD = 70`: Minimum score required to accept a title
- `STATE_REVIEW_TITLE_READABILITY`: Current state being processed
- `STATE_TITLE_FROM_SCRIPT_REVIEW_TITLE`: State for rejected titles
- `STATE_REVIEW_SCRIPT_READABILITY`: State for accepted titles
