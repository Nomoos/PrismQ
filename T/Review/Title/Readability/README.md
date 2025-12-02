# PrismQ.T.Review.Title.Readability

Title Readability Review module for the PrismQ workflow.

## Overview

This module implements the title readability review workflow stage that:
1. Selects the Story with state `PrismQ.T.Review.Title.Readability` that has the Script with the **lowest current version number** (where "current version" is the highest version among all scripts for that story)
2. Reviews the title for voiceover readability
3. Outputs a Review model (text, score, created_at)
4. Updates the Story state based on review acceptance

## Selection Logic

Stories are selected by:
1. **Primary sort**: Lowest current script version number (Stories with less refined scripts are processed first)
2. **Secondary sort**: Oldest creation date (tie-breaker when versions are equal)

This ensures stories with fewer revision iterations get processed before heavily revised ones.

## State Transitions

- **If review doesn't accept title** → `PrismQ.T.Script.From.Title.Review.Script` (return to script refinement)
- **If review accepts title** → `PrismQ.T.Story.Review` (proceed to story review)

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

# Process a single story (selects by lowest script version)
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
- `STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT`: State for rejected titles
- `STATE_STORY_REVIEW`: State for accepted titles
