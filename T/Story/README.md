# PrismQ.Story

**Story Production State Machine**

## Overview

The Story module serves as the **state machine coordinator** for the complete story production workflow in PrismQ. A Story manages the lifecycle from Idea through Script development to multi-format publication.

## Key Concepts

### 1:1 Idea Relationship
Each Story is linked to **exactly ONE Idea**:
```
Idea (1) ←→ (1) Story
```

### State Machine Coordinator
Story manages progression through production phases:
```
IDEA_OUTLINE → IDEA_SKELETON → IDEA_TITLE →
SCRIPT_DRAFT → SCRIPT_REVIEW → SCRIPT_APPROVED →
TEXT_PUBLISHING → TEXT_PUBLISHED →
[optional] AUDIO → VIDEO → ANALYTICS →
ARCHIVED
```

### Multi-Format Support
Stories support progressive enrichment:
- **Text-only** (fastest) - Hours to days
- **Text + Audio** (medium) - Days to week
- **Text + Audio + Video** (complete) - Weeks

## Workflow Position

```
IdeaInspiration → Idea → Story (coordinator) → Script → Publishing → Published Content
```

Story sits between Idea and Script, managing:
- State transitions
- Production phases
- Publication tracking
- Multi-format coordination

## Modules

### Story.Model
Core state machine implementation and database operations.

**[Full Documentation](./Model/README.md)**

## Quick Example

```python
from Story.Model.src.story import Story, StoryState
from Idea.Model.src.idea import Idea

# Create Idea
idea = Idea(
    title="The Echo",
    concept="Girl hears her own voice from the future",
    target_platforms=["reddit", "tiktok"],
    target_formats=["text", "video"]
)

# Create Story from Idea
story = Story.from_idea(idea, created_by="writer_1")

# Progress through states
story.transition_to(StoryState.IDEA_SKELETON)
story.transition_to(StoryState.IDEA_TITLE)
story.transition_to(StoryState.SCRIPT_DRAFT)
story.script_text = "Last night I woke up..."

story.transition_to(StoryState.SCRIPT_REVIEW)
story.transition_to(StoryState.SCRIPT_APPROVED)
story.transition_to(StoryState.TEXT_PUBLISHING)
story.published_text_url = "https://reddit.com/r/nosleep/..."
story.transition_to(StoryState.TEXT_PUBLISHED)
```

## State Machine

### Production Phases

1. **Idea Development** (3 states)
   - Outline → Skeleton → Title

2. **Script Development** (3 states)
   - Draft → Review → Approved

3. **Text Publishing** (2 states)
   - Publishing → Published

4. **Audio Production** (3 states - optional)
   - Recording → Review → Published

5. **Video Production** (4 states - optional)
   - Planning → Production → Review → Published

6. **Analytics** (3 states)
   - Text → Audio → Video

7. **Terminal** (1 state)
   - Archived

### Transition Rules

- **Forward progression** - Follow sequential path
- **Backward transitions** - Support revisions
- **Early termination** - Can archive from any state
- **Validation** - Only valid transitions allowed

## Reddit Story Production

Optimized for viral Reddit story workflow:

```python
# Idea → Story → Script → Reddit → (optional) TikTok → Analytics → Archive

story = Story.from_idea(reddit_idea)
# ... develop through states ...
story.published_text_url = "https://reddit.com/r/AITA/..."
story.transition_to(StoryState.TEXT_PUBLISHED)
# Text live on Reddit!

# Optional: Continue to video
story.transition_to(StoryState.VIDEO_PLANNING)
# ... video production ...
story.published_video_url = "https://tiktok.com/..."
story.transition_to(StoryState.VIDEO_PUBLISHED)
# Video live on TikTok!
```

## Architecture

### Data Flow

```
Idea (source)
  ↓
Story (state machine)
  ├── tracks: state, status, history
  ├── manages: script development
  └── coordinates: publication
  ↓
Published Content
  ├── Text (Reddit, Medium, Blog)
  ├── Audio (Spotify, Podcasts)
  └── Video (YouTube, TikTok)
```

### State vs Status

- **State** (19 values) - Detailed production phase
- **Status** (7 values) - Simplified tracking
  - DRAFT, IN_DEVELOPMENT, READY_FOR_REVIEW, 
  - IN_PRODUCTION, PUBLISHED, ARCHIVED, CANCELLED

## Use Cases

### Use Case 1: Reddit Story
```
Idea → Story → Reddit post → TikTok video → Archive
Timeline: 1-3 days (text) + 1 week (video)
```

### Use Case 2: Blog Post
```
Idea → Story → Medium article → Archive
Timeline: Hours to 1 day (text-only)
```

### Use Case 3: Full Production
```
Idea → Story → Blog → Podcast → YouTube → Archive
Timeline: 1 day (text) + 1 week (audio) + 2 weeks (video)
```

## Benefits

✅ **Enforced Workflow** - State machine prevents invalid transitions  
✅ **Complete Audit Trail** - State history tracks all changes  
✅ **Multi-Format** - Text, audio, video production paths  
✅ **1:1 Idea Link** - Clear traceability to source  
✅ **Flexible Termination** - Can stop at any stage  
✅ **Revision Support** - Backward transitions for improvements  
✅ **Database Persistence** - SQLite storage with indexes  

## Related Modules

- **[T/Idea](../Idea/)** - Idea model (source for Stories)
- **[T/README.md](../README.md)** - Text Generation pipeline
- **[WORKFLOW.md](/WORKFLOW.md)** - Complete content workflow

## Documentation

- **[Model Documentation](./Model/README.md)** - Complete API reference
- **[Example Usage](./Model/_meta/examples/example_usage.py)** - Code examples
- **[Tests](./Model/_meta/tests/)** - Test suite

---

**PrismQ.Story** - State machine for story production workflow
