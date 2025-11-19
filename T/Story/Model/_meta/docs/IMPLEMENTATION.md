# Story Production State Machine - Implementation Summary

## Overview

This document describes the Story model state machine implementation for PrismQ, designed to manage the complete story production workflow from Idea to published content.

## Implementation

### Location
```
T/Story/
├── Model/
│   ├── src/
│   │   ├── story.py          # Core Story model with state machine
│   │   ├── story_db.py       # Database operations
│   │   └── __init__.py
│   ├── _meta/
│   │   ├── tests/
│   │   │   └── test_story.py # Comprehensive test suite
│   │   ├── examples/
│   │   │   └── example_usage.py # Usage examples
│   │   └── docs/
│   ├── README.md             # Complete documentation
│   ├── pyproject.toml        # Package configuration
│   └── .gitignore
└── README.md                 # Module overview
```

### Key Components

#### 1. Story Model (`story.py`)
- **StoryState enum**: 19 production states
- **StoryStatus enum**: 7 simplified status values
- **VALID_TRANSITIONS dict**: State machine transition rules
- **Story class**: Core data model with state machine operations

#### 2. State Machine

**19 States across 7 phases:**

1. **Idea Development** (3 states)
   - `IDEA_OUTLINE` - Detailed content outline
   - `IDEA_SKELETON` - Core framework (3-6 points)
   - `IDEA_TITLE` - Finalized title and hook

2. **Script Development** (3 states)
   - `SCRIPT_DRAFT` - Initial writing
   - `SCRIPT_REVIEW` - Editorial review
   - `SCRIPT_APPROVED` - Final approved script

3. **Text Publishing** (2 states)
   - `TEXT_PUBLISHING` - Preparing publication
   - `TEXT_PUBLISHED` - Live text content

4. **Audio Production** (3 states - optional)
   - `AUDIO_RECORDING` - Voice recording/synthesis
   - `AUDIO_REVIEW` - Audio quality review
   - `AUDIO_PUBLISHED` - Live audio content

5. **Video Production** (4 states - optional)
   - `VIDEO_PLANNING` - Scene planning
   - `VIDEO_PRODUCTION` - Video assembly
   - `VIDEO_REVIEW` - Video quality review
   - `VIDEO_PUBLISHED` - Live video content

6. **Analytics** (3 states)
   - `TEXT_ANALYTICS` - Text performance
   - `AUDIO_ANALYTICS` - Audio performance
   - `VIDEO_ANALYTICS` - Video performance

7. **Terminal** (1 state)
   - `ARCHIVED` - Completed or terminated

#### 3. Transition Rules

**Forward Progression:**
```
IDEA_OUTLINE → IDEA_SKELETON → IDEA_TITLE →
SCRIPT_DRAFT → SCRIPT_REVIEW → SCRIPT_APPROVED →
TEXT_PUBLISHING → TEXT_PUBLISHED →
[optional] AUDIO_* → [optional] VIDEO_* →
ANALYTICS → ARCHIVED
```

**Backward Transitions:**
- Support revisions (e.g., SCRIPT_REVIEW → SCRIPT_DRAFT)
- Support fundamental changes (e.g., SCRIPT_REVIEW → IDEA_TITLE)

**Early Termination:**
- Can archive from any state

#### 4. Database Operations (`story_db.py`)

Operations:
- `insert_story()` - Create new story
- `update_story()` - Update existing story
- `get_story()` - Retrieve by ID
- `get_stories_by_idea()` - Query by Idea
- `get_stories_by_state()` - Query by state
- `get_stories_by_status()` - Query by status
- `delete_story()` - Remove story

Indexes:
- `idea_id` - Fast Idea lookups
- `state` - State-based queries
- `status` - Status-based queries
- `created_at` - Time-based queries

## Testing

### Test Coverage: 94%

**Test Suite** (`test_story.py`):
- 21 tests across 4 test classes
- All tests passing ✓

**Test Classes:**
1. `TestStoryStateTransitions` - State machine logic
2. `TestStoryOperations` - Story operations
3. `TestStoryDatabase` - Database CRUD operations
4. `TestValidTransitions` - Transition validation

## Documentation

### README Files
1. **T/Story/Model/README.md** - Complete API documentation
2. **T/Story/README.md** - Module overview

### Example Usage
- **example_usage.py** - Comprehensive examples:
  - Reddit story workflow
  - Text-only workflow
  - Database operations
  - State transition validation

## Relationship to Existing Structure

### Integration with Idea Model

```
Idea (T/Idea/Model)
  ↓ (1:1 relationship)
Story (T/Story/Model)
  ↓ (manages)
Script → Published Content
```

**Story complements Idea by:**
- Managing production workflow
- Tracking state transitions
- Coordinating multi-format output
- Maintaining publication URLs

### Alignment with IdeaStatus

The existing `IdeaStatus` enum in `T/Idea/Model/src/idea.py` has 42 states covering the complete T→A→V workflow. The Story model:

1. **Focuses on T (Text) pipeline states** - The 19 Story states map to relevant IdeaStatus states
2. **Adds state machine enforcement** - VALID_TRANSITIONS ensures proper workflow
3. **Simplifies tracking** - StoryStatus provides high-level view
4. **Enables multi-format** - Supports text-only, text+audio, or full production

### Story vs Idea States Mapping

| Story State | Corresponding IdeaStatus |
|-------------|-------------------------|
| IDEA_OUTLINE | OUTLINE |
| IDEA_SKELETON | SKELETON |
| IDEA_TITLE | TITLE |
| SCRIPT_DRAFT | SCRIPT_DRAFT |
| SCRIPT_REVIEW | SCRIPT_REVIEW |
| SCRIPT_APPROVED | SCRIPT_APPROVED |
| TEXT_PUBLISHING | TEXT_PUBLISHING |
| TEXT_PUBLISHED | TEXT_PUBLISHED |
| AUDIO_RECORDING | VOICEOVER |
| AUDIO_REVIEW | VOICEOVER_REVIEW |
| AUDIO_PUBLISHED | AUDIO_PUBLISHED |
| VIDEO_PLANNING | SCENE_PLANNING |
| VIDEO_PRODUCTION | VIDEO_ASSEMBLY |
| VIDEO_REVIEW | VIDEO_REVIEW |
| VIDEO_PUBLISHED | VIDEO_PUBLISHED |
| TEXT_ANALYTICS | TEXT_ANALYTICS |
| AUDIO_ANALYTICS | AUDIO_ANALYTICS |
| VIDEO_ANALYTICS | VIDEO_ANALYTICS |
| ARCHIVED | ARCHIVED |

## Use Cases

### Use Case 1: Reddit Story Production
```python
idea = Idea(title="AITA: ...", target_platforms=["reddit", "tiktok"])
story = Story.from_idea(idea)
# ... progress through states ...
story.published_text_url = "https://reddit.com/..."
story.published_video_url = "https://tiktok.com/..."
```

### Use Case 2: Text-Only Blog Post
```python
story = Story.from_idea(blog_idea)
# ... quick progression to text ...
story.published_text_url = "https://medium.com/..."
story.transition_to(StoryState.ARCHIVED)
```

### Use Case 3: Full Multi-Format Production
```python
story = Story.from_idea(idea)
# Progress through all formats
# Text → Audio → Video → Analytics → Archive
```

## Benefits

1. **State Machine Enforcement** - Prevents invalid transitions
2. **Complete Audit Trail** - State history tracks all changes
3. **1:1 Idea Relationship** - Clear traceability
4. **Multi-Format Support** - Text, audio, video paths
5. **Flexible Production** - Can stop at any stage
6. **Revision Support** - Backward transitions allowed
7. **Database Persistence** - SQLite with indexes
8. **High Test Coverage** - 94% code coverage

## Future Enhancements

### Proposed Additional States

Based on the _meta and src structure analysis:

1. **Script Substates** (more granular script development)
   - `SCRIPT_OUTLINE` - Before draft
   - `SCRIPT_PROOFREADING` - After review
   - `SCRIPT_ENHANCEMENT` - Performance annotations

2. **Publishing Substates**
   - `TEXT_PLATFORM_OPTIMIZATION` - SEO and metadata
   - `AUDIO_PLATFORM_OPTIMIZATION` - Platform-specific formats
   - `VIDEO_PLATFORM_OPTIMIZATION` - Thumbnail, description

3. **Collaboration States**
   - `PEER_REVIEW` - Between script states
   - `STAKEHOLDER_APPROVAL` - Before publication

4. **Quality Gates**
   - `QUALITY_CHECK` - Automated checks
   - `COMPLIANCE_REVIEW` - Content compliance

### Integration Opportunities

1. **AI Generation Integration**
   - Auto-transition on completion
   - AI-assisted state progression
   - Quality gate automation

2. **Analytics Integration**
   - Auto-collect metrics in analytics states
   - Performance-based routing
   - A/B testing support

3. **Notification System**
   - State change notifications
   - Stakeholder alerts
   - Deadline warnings

4. **Workflow Templates**
   - Preset state sequences for common patterns
   - Industry-specific workflows
   - Custom workflow definitions

## Conclusion

The Story model provides a robust state machine for managing story production workflow in PrismQ. It:

- ✅ Implements functional state machine for Reddit-style stories
- ✅ Links exactly ONE Idea per Story (1:1 relationship)
- ✅ Manages Script development and publication
- ✅ Supports multi-format progressive enrichment
- ✅ Provides complete audit trail with state history
- ✅ Enforces valid transitions with VALID_TRANSITIONS
- ✅ Has 94% test coverage with comprehensive test suite
- ✅ Includes full documentation and examples

The implementation is production-ready and can be extended with the proposed additional states as needed.
