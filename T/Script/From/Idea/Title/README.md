# T/Script/From/Idea/Title - Initial Script Draft

**Namespace**: `PrismQ.T.Script.From.Idea.Title`

Generate initial script draft from the idea and initial title.

## Purpose

Create the first version (v1) of the script based on the original idea and the initial title (v1).

## Workflow Position

**Stage 3** in MVP workflow: `PrismQ.T.Script.Draft (v1)`

```
Stage 1: PrismQ.T.Idea.Creation
    ↓
Stage 2: PrismQ.T.Title.From.Idea (v1)
    ↓
Stage 3: PrismQ.T.Script.From.Idea.Title (v1) ← THIS STATE
    ↓
Stage 4: PrismQ.T.Review.Title.ByScript
```

## Input Components

### Primary Inputs
- **Idea Object**:
  - Core concept
  - Target audience (e.g., US female 14-29)
  - Content theme (e.g., horror, mystery)
  - Key message
  - Inspiration source

- **Title v1** (from Title.From.Idea):
  - Selected title variant
  - Title promises and expectations
  - Engagement angle

### Context
- **Platform Requirements** (YouTube short: < 180 seconds)
- **Content Type** (narration, voiceover)
- **Style Guidelines** (tone, pacing)

## Process

1. **Analyze inputs**:
   - Understand idea core concept
   - Study title promises
   - Identify target audience expectations

2. **Structure content**:
   - **Introduction/Hook** (10-15 seconds)
     - Grab attention immediately
     - Set up intrigue
     - Establish tone
   
   - **Main Content/Body** (60-150 seconds)
     - Deliver on title promise
     - Build narrative or argument
     - Maintain engagement
     - Develop story/concept
   
   - **Conclusion/Call-to-Action** (10-20 seconds)
     - Satisfying resolution
     - Memorable ending
     - Optional CTA

3. **Format for platform**:
   - Optimize for YouTube short length
   - Structure for voiceover narration
   - Consider pacing and pauses
   - Estimate timing

4. **Store and link**:
   - Save script v1
   - Link to source idea
   - Link to title v1
   - Add metadata

## Output

- **Script v1** (initial draft)
- **Structure Metadata**:
  - Section breakdown (intro, body, conclusion)
  - Timing estimates per section
  - Total estimated duration
- **References**:
  - Link to source idea
  - Link to title v1
- **Platform Tags**:
  - Content type
  - Target length
  - Format

## Key Principle

Creates script that **delivers on title promises** while **staying true to idea intent**.

## Next Stage

Script v1 flows to:
- **Stage 4**: Review.Title.ByScript (reviews Title v1 against Script v1)
- **Stage 5**: Review.Script.ByTitle (reviews Script v1 against Title v1)

## Example Creation

**Inputs:**
- Idea: "Abandoned house with time-loop paranormal activity"
- Title v1: "The Mystery of the Abandoned House"
- Target: 90-second horror short for US female 14-29

**Process:**
- Hook: "Every night at midnight, she returns..." (12s)
- Body: Narrator describes the time-loop discovery (75s)
- Conclusion: "Some mysteries repeat forever" (8s)
- Total: 95 seconds

**Output:**
- Script v1: Full narration text
- Metadata: 3 sections, 95s total
- Ready for review

## State-Based Processing

The module implements state-based processing following the PrismQ workflow state machine:

- **Input State**: `PrismQ.T.Script.From.Idea.Title`
- **Output State**: `PrismQ.T.Review.Title.From.Script.Idea`

### Usage with ScriptFromIdeaTitleService

```python
import sqlite3
from T.Script.From.Idea.Title.src.story_script_service import (
    ScriptFromIdeaTitleService,
    process_oldest_from_idea_title,
    STATE_SCRIPT_FROM_IDEA_TITLE,
    STATE_REVIEW_TITLE_FROM_SCRIPT_IDEA
)

# Connect to database
conn = sqlite3.connect("prismq.db")
conn.row_factory = sqlite3.Row

# Option 1: Use convenience function to process oldest story
result = process_oldest_from_idea_title(conn)
if result.success:
    print(f"Generated script {result.script_id} for story {result.story_id}")
    print(f"Story state changed from {result.previous_state} to {result.new_state}")
else:
    print(f"Error: {result.error}")

# Option 2: Use service for more control
service = ScriptFromIdeaTitleService(conn)

# Count pending stories
pending_count = service.count_pending()
print(f"Stories waiting: {pending_count}")

# Process all pending stories
results = service.process_all_pending()
summary = service.get_processing_summary(results)
print(f"Processed {summary['successful']} stories successfully")
```

### Processing Behavior

1. **FIFO Order**: Stories are processed in FIFO order (oldest first) based on `created_at`
2. **State Transition**: On success, story state changes from `PrismQ.T.Script.From.Idea.Title` to `PrismQ.T.Review.Title.From.Script.Idea`
3. **Script Creation**: Generates Script v0 from the story's Idea and Title

## Module Metadata

**[→ View From/Idea/Title/_meta/docs/](./_meta/docs/)**
**[→ View From/Idea/Title/_meta/examples/](./_meta/examples/)**
**[→ View From/Idea/Title/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Script](../../../README.md)** | **[→ Script/_meta](../../../_meta/)**
