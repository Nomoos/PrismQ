# MVP Workflow Stages

**Complete 26-Stage Workflow Implementation**

## Complete Workflow Stages

### Workflow Sequence (26 Stages)

```
Stage 1: PrismQ.T.Idea.From.User
    ↓
Stage 1.5: PrismQ.T.Story.From.Idea (creates 10 Story objects per Idea)
    ↓
Stage 2: PrismQ.T.Title.From.Idea (v1)
    ↓
Stage 3: PrismQ.T.Content.From.Idea.Title (v1)
    ↓
Stage 4: PrismQ.T.Review.Title.From.Content (v1)
    ↓
Stage 5: PrismQ.T.Review.Content.From.Title (v1)
    ↓
Stage 6: PrismQ.T.Title.From.Title.Review.Content (v2)
    ↓
Stage 7: PrismQ.T.Content.Improvements (v2)
    ↓
Stage 8: PrismQ.T.Review.Title.From.Content (v2) ←──────────────┐
    ↓                                                       │
Stage 9: PrismQ.T.Title.Refinement (v3)                    │
    ↓                                                       │
Stage 10: PrismQ.T.Review.Content.From.Title (v2) ←─────────┐  │
    ↓                                                    │  │
Stage 11: PrismQ.T.Content.Refinement (v3)               │  │
    ↓                                                    │  │
Stage 12: Title Acceptance Check ─NO────────────────────┘  │
    ↓ YES                                                   │
Stage 13: Content Acceptance Check ─NO──────────────────────┘
    ↓ YES

━━━━ Local AI Reviews (Stages 14-20) ━━━━

Stage 14: PrismQ.T.Review.Content.Grammar ←──────────┐
    ↓                                               │
    ├─FAILS─→ Return to Content.Refinement ─────────┘
    ↓ PASSES
Stage 15: PrismQ.T.Review.Content.Tone ←────────────┐
    ↓                                              │
    ├─FAILS─→ Return to Content.Refinement ────────┘
    ↓ PASSES
Stage 16: PrismQ.T.Review.Content.Content ←─────────┐
    ↓                                              │
    ├─FAILS─→ Return to Content.Refinement ────────┘
    ↓ PASSES
Stage 17: PrismQ.T.Review.Content.Consistency ←─────┐
    ↓                                              │
    ├─FAILS─→ Return to Content.Refinement ────────┘
    ↓ PASSES
Stage 18: PrismQ.T.Review.Content.Editing ←─────────┐
    ↓                                              │
    ├─FAILS─→ Return to Content.Refinement ────────┘
    ↓ PASSES
Stage 19: PrismQ.T.Review.Title.Readability ←──────┐
    ↓                                              │
    ├─FAILS─→ Return to Title.Refinement ─────────┘
    ↓ PASSES
Stage 20: PrismQ.T.Review.Content.Readability ←─────┐
    ↓                                              │
    ├─FAILS─→ Return to Content.Refinement ────────┘
    ↓ PASSES

━━━━ GPT Expert Review Loop (Stages 21-22) ━━━━

Stage 21: PrismQ.T.Story.ExpertReview (GPT) ←──────────┐
    ↓                                                   │
    ├─ Improvements Needed ─→ Stage 22 ────────────────┘
    ↓ Ready for Publishing
Stage 23: PrismQ.T.Publishing.Finalization
```

---

## Stage Details

This section provides comprehensive documentation for all 26 stages of the MVP workflow. Each stage includes purpose, inputs, outputs, API examples, and usage examples.

### Stages 1-11: Initial Creation and Refinement

These stages handle initial content creation, cross-reviews, and iterative improvement cycles.

---

### Stage 1: PrismQ.T.Idea.From.User

**Purpose**: Capture initial content idea

**Folder**: `T/Idea/From/User/`  
**Worker**: Worker02  
**Effort**: 2 days

**Input**:
- Text description of idea
- Optional: inspiration sources, target audience

**Output**:
- Idea object with unique ID
- Metadata (timestamp, author, tags)
- Initial classification

**Validation**:
- Not empty
- Basic format check
- Contains minimum required fields

**API**:
```python
from PrismQ.T.Idea.From.User import create_idea

idea = create_idea(
    description="Story about mysterious events in a small town",
    target_audience="US female 14-29",
    genre="mystery/suspense"
)
# Returns: Idea object with ID
```

**Usage Example**:
```python
# Create a new idea
idea = {
    "id": "PQ001",
    "description": "A suspenseful story about unexplained disappearances",
    "target_audience": "Young adults",
    "genre": "Mystery",
    "platforms": ["YouTube", "TikTok"],
    "created_at": "2025-01-01T10:00:00Z"
}
```

**Next Stage**: Stage 1.5 (Story.From.Idea)

---

### Stage 1.5: PrismQ.T.Story.From.Idea

**Purpose**: Create 10 Story objects from each Idea

**Folder**: `T/Story/From/Idea/`  
**Worker**: Automated  
**Effort**: Immediate

**Input**:
- Idea object with unique ID

**Output**:
- 10 Story objects per Idea
- Each Story with `idea_id` reference
- State set to `PrismQ.T.Title.From.Idea`

**Validation**:
- Idea exists in database
- Idea doesn't already have Stories (optional, can be skipped)

**API**:
```python
from T.Story.From.Idea import StoryFromIdeaService, create_stories_from_idea

# Using the service
service = StoryFromIdeaService(story_connection, idea_db)
result = service.create_stories_from_idea(idea_id=1)
# Returns: StoryCreationResult with 10 Story objects

# Or process all unreferenced ideas
results = service.process_unreferenced_ideas()
# Returns: List of StoryCreationResult for all ideas without stories
```

**Usage Example**:
```python
# Stories created with following structure:
story = {
    "id": 1,
    "idea_id": "PQ001",
    "state": "PrismQ.T.Title.From.Idea",
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
}
```

**Next Stage**: Stage 2 (Title.From.Idea)

---

### Stage 2: PrismQ.T.Title.From.Idea (v1)

**Purpose**: Generate first title from idea

**Folder**: `T/Title/From/Idea/`  
**Worker**: Worker13 (Prompt Master)  
**Effort**: 2 days

**Input**:
- Idea object from Stage 1
- Target audience metadata
- Platform requirements

**Output**:
- 3-5 title variants (v1)
- Metadata for each variant
- Engagement score predictions

**Process**:
- AI generation using simple prompt
- Context: Based on idea only
- Version: v1 (initial)

**API**:
```python
from PrismQ.T.Title.From.Idea import generate_title_v1

titles = generate_title_v1(
    idea=idea,
    num_variants=5,
    style="suspenseful"
)
# Returns: List of title variants
```

**Usage Example**:
```python
# Generate initial title variants
titles_v1 = [
    "The Mystery of Hollow Creek",
    "When the Town Went Silent",
    "Vanished: The Hollow Creek Enigma",
    "Shadows Over Hollow Creek",
    "The Hollow Creek Disappearances"
]

selected_title_v1 = titles_v1[0]  # Best scored variant
```

**Next Stage**: Stage 3 (Content.From.Idea.Title)

---

### Stage 3: PrismQ.T.Content.From.Idea.Title (v1)

**Purpose**: Generate first content from idea and title v1

**Folder**: `T/Content/From/Idea/Title/`  
**Worker**: Worker02  
**Effort**: 3 days

**Input**:
- Idea object
- Title v1
- Target word count
- Structural requirements

**Output**:
- Initial content (v1)
- Structure: Intro, body, conclusion
- Metadata: word count, reading time

**Process**:
- AI generation with structured prompt
- Context: Based on idea + title v1
- Version: v1 (initial)

**API**:
```python
from PrismQ.T.Content.From.Idea.Title import generate_content_v1

content = generate_content_v1(
    idea=idea,
    title=title_v1,
    target_words=1500,
    structure="intro-body-conclusion"
)
# Returns: Content object
```

**Next Stage**: Stage 4 (Review.Title.From.Content)

---

### Stages 4-11: Cross-Review and Improvement Cycles

These stages implement the co-dependent improvement methodology where title and content are reviewed against each other and iteratively refined. The complete workflow includes:

**Stage 4**: PrismQ.T.Review.Title.From.Content (v1) - Review title v1 against content v1 and idea  
**Stage 5**: PrismQ.T.Review.Content.From.Title (v1) - Review content v1 against title v1 and idea  
**Stage 6**: PrismQ.T.Title.From.Title.Review.Content (v2) - Generate improved title v2 using both reviews  
**Stage 7**: PrismQ.T.Content.Improvements (v2) - Generate improved content v2 with new title v2  
**Stage 8**: PrismQ.T.Review.Title.From.Content (v2) - Review title v2 against content v2  
**Stage 9**: PrismQ.T.Title.Refinement (v3) - Refine title to v3 based on v2 review  
**Stage 10**: PrismQ.T.Review.Content.From.Title (v2) - Review content v2 against title v3  
**Stage 11**: PrismQ.T.Content.Refinement (v3) - Refine content to v3 aligned with title v3

Each of these stages follows a similar API pattern. For the original detailed specification with complete examples for all stages, see the [MVP_WORKFLOW.md](./_meta/issues/MVP_WORKFLOW.md) source document.

---

### Stages 12-13: Acceptance Gates

**Stage 12: Title Acceptance Check**

**Purpose**: Verify title is ready to proceed

**Input**: Title (latest version - v3, v4, v5, etc.)  
**Output**: ACCEPTED or NOT ACCEPTED

**Decision**:
- **ACCEPTED**: Proceed to stage 13
- **NOT ACCEPTED**: Return to stage 8 for additional refinement

**API**:
```python
from PrismQ.T.Review.Idea import check_title_acceptance

acceptance = check_title_acceptance(title=title_v3)
# Returns: {"accepted": True/False, "reason": "..."}
```

**Stage 13: Content Acceptance Check**

**Purpose**: Verify content is ready to proceed

**Input**: Content (latest version - v3, v4, v5, etc.), Title (accepted version)  
**Output**: ACCEPTED or NOT ACCEPTED

**Decision**:
- **ACCEPTED**: Proceed to stage 14
- **NOT ACCEPTED**: Return to stage 10 for additional refinement

**API**:
```python
from PrismQ.T.Review.Content import check_content_acceptance

acceptance = check_content_acceptance(content=content_v3, title=title_v3)
# Returns: {"accepted": True/False, "reason": "..."}
```

---

### Stages 14-20: Quality Reviews

These stages validate 7 quality dimensions using local AI reviews.

**Stage 14**: Grammar Review - Technical correctness  
**Stage 15**: Tone Review - Emotional and stylistic consistency  
**Stage 16**: Content Review - Narrative logic and coherence  
**Stage 17**: Consistency Review - Internal continuity  
**Stage 18**: Editing Review - Clarity and flow  
**Stage 19**: Title Readability - Final title validation  
**Stage 20**: Content Readability - Voiceover quality validation

Each quality review follows the same pattern:

**API Pattern**:
```python
from PrismQ.T.Review.<Dimension> import review_<dimension>

result = review_<dimension>(content=content_v3)
# Returns: {"pass": True/False, "issues": [...], "suggestions": [...]}
```

**Decision Pattern**:
- **PASSES**: Proceed to next stage
- **FAILS**: Return to appropriate refinement stage with feedback

---

### Stages 21-23: Expert Review and Publishing

**Stage 21: PrismQ.T.Story.ExpertReview**

**Purpose**: GPT-based expert review of complete story

**Input**:
- Title (final version)
- Content (final version)
- Audience context
- Original idea

**Output**:
- Ready for Publishing or Improvements Needed
- Expert review JSON with scores and feedback

**API**:
```python
from PrismQ.T.Story.ExpertReview import expert_review

result = expert_review(
    title=title_final,
    content=content_final,
    idea=idea,
    audience="US female 14-29"
)
```

**Stage 22: PrismQ.T.Story.Polish**

**Purpose**: Apply GPT-based expert improvements

**Input**: Title, content, expert review feedback  
**Output**: Polished title and content

**Iteration Limit**: Maximum 2 polish iterations

**API**:
```python
from PrismQ.T.Story.Polish import polish_story_with_gpt

polished = polish_story_with_gpt(story_id, title, content, expert_review_result)
```

**Stage 23: PrismQ.T.Publishing.Finalization**

**Purpose**: Publish approved and validated content

**Input**: Final title, final content, original idea  
**Output**: Published content package

**API**:
```python
from PrismQ.T.Publishing.Finalization import publish_content

published = publish_content(
    title=title_final,
    content=content_final,
    idea=idea,
    format="markdown"
)
```

---

