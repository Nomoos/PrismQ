# PrismQ.Story.Model

**Story production state machine for PrismQ content workflow**

---

## What is PrismQ.Story?

The Story module is the state machine coordinator for story production in PrismQ:

```
IdeaInspiration → Idea → Story (manages workflow) → Script → Publishing → Published Content
```

A **Story** represents the complete production lifecycle:
- Linked to exactly **ONE Idea** (1:1 relationship)
- Manages state transitions through production phases
- Tracks script development and publication
- Supports multi-format output (text, audio, video)

---

## Quick Start

```bash
# Install (from T/Story/Model directory)
cd T/Story/Model
pip install -e .

# Setup database
python -c "
from src.story_db import StoryDatabase
db = StoryDatabase('stories.db')
db.connect()
db.close()
print('Database created!')
"
```

### Create a Story from an Idea

```python
from src.story import Story, StoryState
from src.story_db import StoryDatabase

# Assuming you have an Idea object
from T.Idea.Model.src.idea import Idea

idea = Idea(
    title="The Echo",
    concept="A girl hears her own voice from the future",
    target_platforms=["reddit", "tiktok"],
    target_formats=["text", "video"]
)

# Create Story from Idea
story = Story.from_idea(idea, created_by="writer_1")
print(story)  # Story(title='The Echo...', state=idea_outline, ...)

# Progress through states
story.transition_to(StoryState.IDEA_SKELETON)
story.transition_to(StoryState.IDEA_TITLE)
story.transition_to(StoryState.SCRIPT_DRAFT)
story.script_text = "Last night I woke up... but my body kept sleeping."

# Continue to publication
story.transition_to(StoryState.SCRIPT_REVIEW)
story.transition_to(StoryState.SCRIPT_APPROVED)
story.transition_to(StoryState.TEXT_PUBLISHING)
story.published_text_url = "https://reddit.com/r/nosleep/..."
story.transition_to(StoryState.TEXT_PUBLISHED)

# Save to database
db = StoryDatabase("stories.db")
db.connect()
story_id = db.insert_story(story.to_dict())
db.close()
```

---

## State Machine

### Story States

The Story state machine has **19 states** organized into phases:

#### 1. Idea Development (3 states)
- `IDEA_OUTLINE` - Detailed content outline
- `IDEA_SKELETON` - Core framework (3-6 points)
- `IDEA_TITLE` - Finalized title and hook

#### 2. Script Development (3 states)
- `SCRIPT_DRAFT` - Initial writing
- `SCRIPT_REVIEW` - Editorial review
- `SCRIPT_APPROVED` - Final approved script

#### 3. Text Publishing (2 states)
- `TEXT_PUBLISHING` - Preparing publication
- `TEXT_PUBLISHED` - Live text content

#### 4. Audio Production (3 states - optional)
- `AUDIO_RECORDING` - Voice recording/synthesis
- `AUDIO_REVIEW` - Audio quality review
- `AUDIO_PUBLISHED` - Live audio content

#### 5. Video Production (4 states - optional)
- `VIDEO_PLANNING` - Scene planning
- `VIDEO_PRODUCTION` - Video assembly
- `VIDEO_REVIEW` - Video quality review
- `VIDEO_PUBLISHED` - Live video content

#### 6. Analytics (3 states)
- `TEXT_ANALYTICS` - Text performance analysis
- `AUDIO_ANALYTICS` - Audio performance analysis
- `VIDEO_ANALYTICS` - Video performance analysis

#### 7. Terminal
- `ARCHIVED` - Completed or terminated

### State Transitions

The state machine enforces valid transitions:

```python
# Valid transitions
story.transition_to(StoryState.IDEA_SKELETON)  # ✓ Valid

# Invalid transitions raise ValueError
story.transition_to(StoryState.VIDEO_PUBLISHED)  # ✗ Raises ValueError
```

**Forward Progression** (typical path):
```
IDEA_OUTLINE → IDEA_SKELETON → IDEA_TITLE → 
SCRIPT_DRAFT → SCRIPT_REVIEW → SCRIPT_APPROVED →
TEXT_PUBLISHING → TEXT_PUBLISHED → ARCHIVED
```

**Backward Transitions** (for revisions):
```python
# Script needs major revision
story.transition_to(StoryState.SCRIPT_DRAFT, notes="Major revisions needed")

# Fundamental concept change
story.transition_to(StoryState.IDEA_TITLE, notes="Rethinking approach")
```

**Early Archive** (from any state):
```python
story.transition_to(StoryState.ARCHIVED)  # Works from any state
```

### Multi-Format Production

Stories support progressive multi-format production:

**Text-Only Path** (fastest):
```
... → TEXT_PUBLISHED → TEXT_ANALYTICS → ARCHIVED
```

**Text + Audio Path**:
```
... → TEXT_PUBLISHED → AUDIO_RECORDING → ... → AUDIO_PUBLISHED → ARCHIVED
```

**Full Production Path** (text + audio + video):
```
... → TEXT_PUBLISHED → AUDIO_RECORDING → ... → AUDIO_PUBLISHED →
VIDEO_PLANNING → ... → VIDEO_PUBLISHED → ARCHIVED
```

---

## Story Operations

### Check Valid Transitions

```python
# Get all valid transitions from current state
valid_states = story.get_valid_transitions()
print([s.value for s in valid_states])
# ['idea_skeleton', 'archived']

# Check if specific transition is valid
if story.can_transition_to(StoryState.SCRIPT_DRAFT):
    story.transition_to(StoryState.SCRIPT_DRAFT)
```

### State History

Every transition is recorded:

```python
for entry in story.state_history:
    print(f"{entry['state']} at {entry['entered_at']}")
    if 'notes' in entry:
        print(f"  Notes: {entry['notes']}")
```

### Status Tracking

Stories have both **state** (detailed) and **status** (simplified):

```python
print(f"State: {story.state.value}")    # idea_skeleton
print(f"Status: {story.status.value}")  # draft
```

Status automatically updates with state:
- `DRAFT` - Idea development
- `IN_DEVELOPMENT` - Script writing
- `READY_FOR_REVIEW` - Script approved
- `IN_PRODUCTION` - Publishing/production
- `PUBLISHED` - Live content
- `ARCHIVED` - Completed

---

## Database Operations

### Basic CRUD

```python
from src.story_db import StoryDatabase

db = StoryDatabase("stories.db")
db.connect()

# Insert
story_id = db.insert_story(story.to_dict())

# Retrieve
story_dict = db.get_story(story_id)
story = Story.from_dict(story_dict)

# Update
story.transition_to(StoryState.SCRIPT_DRAFT)
db.update_story(story_id, story.to_dict())

# Delete
db.delete_story(story_id)

db.close()
```

### Queries

```python
# Get all stories for an Idea
stories = db.get_stories_by_idea("idea_123")

# Get stories in specific state
drafts = db.get_stories_by_state(StoryState.SCRIPT_DRAFT)

# Get stories by status
published = db.get_stories_by_status(StoryStatus.PUBLISHED)
```

---

## Reddit Story Workflow

Optimized workflow for Reddit-style stories:

```python
from src.story import Story, StoryState
from T.Idea.Model.src.idea import Idea, ContentGenre

# 1. Create Idea for Reddit story
idea = Idea(
    title="AITA: Family Won't Support My Career Change",
    concept="Person vs family over career choice",
    premise="I want to quit accounting to become a tattoo artist...",
    target_platforms=["reddit", "tiktok"],
    target_formats=["text", "video"],
    genre=ContentGenre.DRAMA,
    keywords=["AITA", "family drama", "career change"]
)

# 2. Create Story from Idea
story = Story.from_idea(idea, created_by="writer_1")

# 3. Develop through states
story.transition_to(StoryState.IDEA_SKELETON)
# Add skeleton: "Hook → Background → Conflict → Current State → AITA Question"

story.transition_to(StoryState.IDEA_TITLE)
# Finalize title

story.transition_to(StoryState.SCRIPT_DRAFT)
story.script_text = """
I (25F) told my family I'm quitting accounting to become a tattoo artist...
[full Reddit post text]
"""

story.transition_to(StoryState.SCRIPT_REVIEW)
# Editorial review

story.transition_to(StoryState.SCRIPT_APPROVED)
# Ready for publication

story.transition_to(StoryState.TEXT_PUBLISHING)
# Prepare for Reddit

story.published_text_url = "https://reddit.com/r/AmItheAsshole/comments/..."
story.transition_to(StoryState.TEXT_PUBLISHED)
# Live on Reddit!

# Optional: Continue to TikTok video
story.transition_to(StoryState.AUDIO_RECORDING)
# Record voiceover

story.transition_to(StoryState.AUDIO_REVIEW)
story.transition_to(StoryState.AUDIO_PUBLISHED)

story.transition_to(StoryState.VIDEO_PLANNING)
# Plan visual scenes

story.transition_to(StoryState.VIDEO_PRODUCTION)
story.transition_to(StoryState.VIDEO_REVIEW)
story.published_video_url = "https://tiktok.com/@user/video/..."
story.transition_to(StoryState.VIDEO_PUBLISHED)
# Live on TikTok!

# Analytics
story.transition_to(StoryState.VIDEO_ANALYTICS)
# Analyze performance

story.transition_to(StoryState.ARCHIVED)
# Complete!
```

---

## Architecture

### Data Model

```
Story (State Machine Coordinator)
├── title: str
├── idea_id: str (exactly ONE Idea)
├── state: StoryState (current state)
├── status: StoryStatus (simplified status)
├── script_id: Optional[str]
├── script_text: str
├── published_text_url: Optional[str]
├── published_audio_url: Optional[str]
├── published_video_url: Optional[str]
├── target_platforms: List[str]
├── target_formats: List[str]
├── state_history: List[Dict]
└── metadata: Dict
```

### Relationships

```
Idea (1) ←→ (1) Story ←→ (0..1) Script
                ↓
        Published Content (0..*)
        ├── Text
        ├── Audio
        └── Video
```

### State Machine Design

- **Enforced transitions**: Only valid transitions allowed
- **State history**: Complete audit trail
- **Backward transitions**: Support revisions
- **Early termination**: Can archive from any state
- **Multi-format support**: Optional audio/video paths

---

## Testing

```bash
# Run tests
pytest _meta/tests/test_story.py -v

# With coverage
pytest _meta/tests/test_story.py --cov=src --cov-report=html
```

---

## Related Modules

- **[T/Idea/Model](../Idea/Model/)** - Idea model (feeds Story)
- **[T/README.md](../../README.md)** - Text Generation pipeline overview
- **[WORKFLOW.md](/WORKFLOW.md)** - Complete content workflow

---

## Key Features

✅ **State Machine Enforcement** - Only valid transitions allowed  
✅ **1:1 Idea Relationship** - Each Story links to exactly one Idea  
✅ **State History Tracking** - Complete audit trail  
✅ **Multi-Format Support** - Text, audio, video production paths  
✅ **Reddit Story Optimized** - Perfect for viral story production  
✅ **Database Persistence** - SQLite storage with indexes  
✅ **Flexible Status** - Both detailed state and simplified status  
✅ **Backward Transitions** - Support for revisions and iterations

---

## License

Proprietary - All Rights Reserved © 2025 PrismQ
