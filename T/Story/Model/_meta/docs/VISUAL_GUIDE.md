# Story State Machine - Visual Guide

## State Machine Diagram

### Complete Flow (Text + Audio + Video)

```
┌─────────────────────────────────────────────────────────────────────┐
│                      STORY PRODUCTION WORKFLOW                      │
└─────────────────────────────────────────────────────────────────────┘

                              START
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                    PHASE 1: IDEA DEVELOPMENT                      │
├───────────────────────────────────────────────────────────────────┤
│   IDEA_OUTLINE  →  IDEA_SKELETON  →  IDEA_TITLE                  │
│        │                 │                  │                      │
│        └─────────────────┴──────────────────┴──→ ARCHIVED        │
└───────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                   PHASE 2: SCRIPT DEVELOPMENT                     │
├───────────────────────────────────────────────────────────────────┤
│   SCRIPT_DRAFT  →  SCRIPT_REVIEW  →  SCRIPT_APPROVED             │
│        │                 │   ↑              │                      │
│        └─────────────────┘   │              │                      │
│                      ┌────────┘              │                      │
│                      │                       ▼                      │
│                      └──────────────────→ ARCHIVED                 │
└───────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                    PHASE 3: TEXT PUBLISHING                       │
├───────────────────────────────────────────────────────────────────┤
│   TEXT_PUBLISHING  →  TEXT_PUBLISHED                              │
│         │                    │                                     │
│         └────────────────────┴──────────→ TEXT_ANALYTICS          │
│                                                  │                 │
│                                                  ▼                 │
│                                              ARCHIVED              │
└───────────────────────────────────────────────────────────────────┘
                                │
                        ┌───────┴───────┐
                        │               │
                        ▼               ▼
              (Continue to Audio)   (Stop here)
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│                 PHASE 4: AUDIO PRODUCTION (Optional)              │
├───────────────────────────────────────────────────────────────────┤
│   AUDIO_RECORDING  →  AUDIO_REVIEW  →  AUDIO_PUBLISHED           │
│         │                  │   ↑              │                    │
│         └──────────────────┘   │              │                    │
│                      ┌─────────┘              │                    │
│                      │                        ▼                    │
│                      └─────────────→  AUDIO_ANALYTICS              │
│                                             │                      │
│                                             ▼                      │
│                                         ARCHIVED                   │
└───────────────────────────────────────────────────────────────────┘
                                │
                        ┌───────┴───────┐
                        │               │
                        ▼               ▼
              (Continue to Video)   (Stop here)
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│                PHASE 5: VIDEO PRODUCTION (Optional)               │
├───────────────────────────────────────────────────────────────────┤
│   VIDEO_PLANNING  →  VIDEO_PRODUCTION  →  VIDEO_REVIEW           │
│         │                  │   ↑              │   ↑               │
│         └──────────────────┘   │              │   │               │
│                      ┌─────────┘              │   │               │
│                      │                        │   │               │
│                      └────────────────────────┘   │               │
│                                                   │               │
│                                                   ▼               │
│                                          VIDEO_PUBLISHED          │
│                                                   │               │
│                                                   ▼               │
│                                         VIDEO_ANALYTICS           │
│                                                   │               │
│                                                   ▼               │
│                                              ARCHIVED             │
└───────────────────────────────────────────────────────────────────┘
```

## Production Paths

### Path 1: Text-Only (Fastest - Hours to Days)

```
IDEA_OUTLINE → IDEA_SKELETON → IDEA_TITLE →
SCRIPT_DRAFT → SCRIPT_REVIEW → SCRIPT_APPROVED →
TEXT_PUBLISHING → TEXT_PUBLISHED →
TEXT_ANALYTICS → ARCHIVED

Use Case: Blog posts, Reddit stories, Medium articles
Timeline: Hours to 2 days
Platforms: Reddit, Medium, Blog, LinkedIn
```

### Path 2: Text + Audio (Medium - Days to Week)

```
... TEXT_PUBLISHED →
AUDIO_RECORDING → AUDIO_REVIEW → AUDIO_PUBLISHED →
AUDIO_ANALYTICS → ARCHIVED

Use Case: Podcasts, audio storytelling, Spotify content
Timeline: 2-7 days
Platforms: Spotify, Apple Podcasts, SoundCloud
```

### Path 3: Full Production (Complete - Weeks)

```
... AUDIO_PUBLISHED →
VIDEO_PLANNING → VIDEO_PRODUCTION → VIDEO_REVIEW →
VIDEO_PUBLISHED →
VIDEO_ANALYTICS → ARCHIVED

Use Case: YouTube videos, TikTok, Instagram Reels
Timeline: 1-3 weeks
Platforms: YouTube, TikTok, Instagram
```

## State Transitions Matrix

| From State         | Valid Next States                                                    |
|--------------------|----------------------------------------------------------------------|
| IDEA_OUTLINE       | IDEA_SKELETON, ARCHIVED                                              |
| IDEA_SKELETON      | IDEA_TITLE, IDEA_OUTLINE↩, ARCHIVED                                  |
| IDEA_TITLE         | SCRIPT_DRAFT, IDEA_SKELETON↩, ARCHIVED                               |
| SCRIPT_DRAFT       | SCRIPT_REVIEW, IDEA_TITLE↩, ARCHIVED                                 |
| SCRIPT_REVIEW      | SCRIPT_APPROVED, SCRIPT_DRAFT↩, IDEA_TITLE↩, ARCHIVED               |
| SCRIPT_APPROVED    | TEXT_PUBLISHING, SCRIPT_REVIEW↩, ARCHIVED                            |
| TEXT_PUBLISHING    | TEXT_PUBLISHED, SCRIPT_APPROVED↩, ARCHIVED                           |
| TEXT_PUBLISHED     | TEXT_ANALYTICS, AUDIO_RECORDING, ARCHIVED                            |
| AUDIO_RECORDING    | AUDIO_REVIEW, TEXT_PUBLISHED↩, ARCHIVED                              |
| AUDIO_REVIEW       | AUDIO_PUBLISHED, AUDIO_RECORDING↩, ARCHIVED                          |
| AUDIO_PUBLISHED    | AUDIO_ANALYTICS, VIDEO_PLANNING, ARCHIVED                            |
| VIDEO_PLANNING     | VIDEO_PRODUCTION, AUDIO_PUBLISHED↩, ARCHIVED                         |
| VIDEO_PRODUCTION   | VIDEO_REVIEW, VIDEO_PLANNING↩, ARCHIVED                              |
| VIDEO_REVIEW       | VIDEO_PUBLISHED, VIDEO_PRODUCTION↩, ARCHIVED                         |
| VIDEO_PUBLISHED    | VIDEO_ANALYTICS, ARCHIVED                                            |
| TEXT_ANALYTICS     | ARCHIVED                                                             |
| AUDIO_ANALYTICS    | ARCHIVED                                                             |
| VIDEO_ANALYTICS    | ARCHIVED                                                             |
| ARCHIVED           | (terminal - no exits)                                                |

Legend: ↩ = Backward transition (revision)

## Status Progression

```
State                    →  Status
─────────────────────────────────────────────
IDEA_OUTLINE            →  DRAFT
IDEA_SKELETON           →  DRAFT
IDEA_TITLE              →  DRAFT

SCRIPT_DRAFT            →  IN_DEVELOPMENT
SCRIPT_REVIEW           →  IN_DEVELOPMENT

SCRIPT_APPROVED         →  READY_FOR_REVIEW

TEXT_PUBLISHING         →  IN_PRODUCTION
AUDIO_RECORDING         →  IN_PRODUCTION
AUDIO_REVIEW            →  IN_PRODUCTION
VIDEO_PLANNING          →  IN_PRODUCTION
VIDEO_PRODUCTION        →  IN_PRODUCTION
VIDEO_REVIEW            →  IN_PRODUCTION

TEXT_PUBLISHED          →  PUBLISHED
AUDIO_PUBLISHED         →  PUBLISHED
VIDEO_PUBLISHED         →  PUBLISHED
TEXT_ANALYTICS          →  PUBLISHED
AUDIO_ANALYTICS         →  PUBLISHED
VIDEO_ANALYTICS         →  PUBLISHED

ARCHIVED                →  ARCHIVED
```

## Reddit Story Example Timeline

### Week 1: Text Production
```
Monday     → IDEA_OUTLINE (2 hours)
           → IDEA_SKELETON (1 hour)
           → IDEA_TITLE (30 min)

Tuesday    → SCRIPT_DRAFT (4 hours)

Wednesday  → SCRIPT_REVIEW (2 hours)
           → SCRIPT_APPROVED ✓

Thursday   → TEXT_PUBLISHING (1 hour)
           → TEXT_PUBLISHED 📝 (Live on Reddit!)

Friday     → TEXT_ANALYTICS (monitoring)
```

### Week 2: Video Production (Optional)
```
Monday     → AUDIO_RECORDING (2 hours)
           → AUDIO_REVIEW (1 hour)
           → AUDIO_PUBLISHED 🎵

Tuesday    → VIDEO_PLANNING (3 hours)

Wednesday  → VIDEO_PRODUCTION (5 hours)

Thursday   → VIDEO_REVIEW (2 hours)
           → VIDEO_PUBLISHED 🎬 (Live on TikTok!)

Friday     → VIDEO_ANALYTICS (monitoring)

Weekend    → ARCHIVED ✓
```

## State Machine Features

### 1. Enforced Transitions
```python
# ✓ Valid
story.transition_to(StoryState.IDEA_SKELETON)

# ✗ Invalid - Raises ValueError
story.transition_to(StoryState.VIDEO_PUBLISHED)
```

### 2. Revision Support
```python
# Forward: SCRIPT_DRAFT → SCRIPT_REVIEW
story.transition_to(StoryState.SCRIPT_REVIEW)

# Backward: SCRIPT_REVIEW → SCRIPT_DRAFT (for revisions)
story.transition_to(StoryState.SCRIPT_DRAFT, notes="Major revisions needed")
```

### 3. Early Termination
```python
# Can archive from any state
story.transition_to(StoryState.ARCHIVED)
```

### 4. State History
```python
# Complete audit trail
for entry in story.state_history:
    print(f"{entry['state']} at {entry['entered_at']}")
    if 'notes' in entry:
        print(f"  Notes: {entry['notes']}")
```

### 5. Valid Transition Checking
```python
# Check before transition
valid_states = story.get_valid_transitions()
if StoryState.SCRIPT_DRAFT in valid_states:
    story.transition_to(StoryState.SCRIPT_DRAFT)

# Or use can_transition_to
if story.can_transition_to(StoryState.SCRIPT_DRAFT):
    story.transition_to(StoryState.SCRIPT_DRAFT)
```

## Multi-Format Decision Tree

```
TEXT_PUBLISHED
    │
    ├─── Stop here? ──→ TEXT_ANALYTICS → ARCHIVED
    │                   (Text-only release)
    │
    └─── Continue to Audio?
            │
            └─→ AUDIO_RECORDING ... AUDIO_PUBLISHED
                    │
                    ├─── Stop here? ──→ AUDIO_ANALYTICS → ARCHIVED
                    │                   (Text + Audio release)
                    │
                    └─── Continue to Video?
                            │
                            └─→ VIDEO_PLANNING ... VIDEO_PUBLISHED
                                    │
                                    └─→ VIDEO_ANALYTICS → ARCHIVED
                                        (Full multi-format release)
```

## Integration with Idea Model

```
┌─────────────┐
│    Idea     │  (T/Idea/Model)
│             │
│ - title     │
│ - concept   │
│ - premise   │
│ - outline   │
│ - skeleton  │
│ - ...       │
└──────┬──────┘
       │ (exactly 1:1)
       ▼
┌─────────────┐
│    Story    │  (T/Story/Model) ← Coordinator
│             │
│ - idea_id   │  (references Idea)
│ - state     │  (current state)
│ - status    │  (simplified)
│ - script_*  │  (script fields)
│ - published_*│ (publication URLs)
│ - ...       │
└──────┬──────┘
       │
       ├─→ Script Development
       ├─→ Text Publishing
       ├─→ Audio Production
       └─→ Video Production
```

## Summary

### States: 19
- Idea: 3
- Script: 3
- Text: 2
- Audio: 3
- Video: 4
- Analytics: 3
- Terminal: 1

### Transitions: 54
- Forward: 19
- Backward: 14
- To Archive: 18
- From Archive: 0

### Features
✅ Enforced transitions
✅ State history
✅ Revision support
✅ Multi-format paths
✅ Early termination
✅ 1:1 Idea relationship

---

**Story State Machine** - Complete visual guide for production workflow
