# T/Review - Content Review Module

**Namespace**: `PrismQ.T.Review`

Multi-dimensional content quality review and enhancement.

## Purpose

Ensure content quality through comprehensive review across multiple dimensions including title-script alignment, grammar, readability, tone, content accuracy, consistency, and final editing. The Review module is central to the iterative co-improvement workflow that drives quality across all content stages.

## MVP Workflow Integration

The Review module plays a critical role in the MVP iterative workflow:

### Stage 4 (MVP-004): Title Review by Script and Idea
**Module**: `T.Review.Title.ByScriptAndIdea`  
**Input**: Title v1 + Script v1 + Idea  
**Output**: Title Review with feedback  
**Next**: Stage 6 (Title Improvements v2)

### Stage 5 (MVP-005): Script Review by Title and Idea
**Module**: `T.Review.Script` (ByTitle submodule)  
**Input**: Script v1 + Title v1 + Idea  
**Output**: Script Review with feedback  
**Next**: Stage 7 (Script Improvements v2)

### Stages 8, 10, 12-13: Iterative Review Loops
Reviews continue at each iteration to validate improvements until acceptance gates pass.

### Stages 14-20: Quality Review Dimensions
Final validation through multiple quality dimensions:
- **Stage 14**: Grammar Review → Script Refinement loop
- **Stage 15**: Tone Review → Script Refinement loop
- **Stage 16**: Content Review → Script Refinement loop
- **Stage 17**: Consistency Review → Script Refinement loop
- **Stage 18**: Editing Review → Script Refinement loop
- **Stage 19**: Title Readability → Title Refinement loop
- **Stage 20**: Script Readability → Script Refinement loop

### Workflow Visualization

```
Idea → Title v1 → Script v1
        ↓           ↓
    [Stage 4]   [Stage 5]
    Title       Script
    Review      Review
        ↓           ↓
    Title v2 ← Script v2
        ↓           ↓
    Reviews → Refinements v3
        ↓           ↓
    Acceptance Gates (12-13)
        ↓
    Quality Reviews (14-20)
        ↓
    Publishing (Stage 23)
```

## Submodules

### Implementation Status

| Module | Status | MVP Stage | Implementation |
|--------|--------|-----------|----------------|
| Title/ByScriptAndIdea | ✅ **Complete** | Stage 4 | Full data model, tests, examples |
| Script | ✅ **Complete** | Stage 5, 10, 13 | Full review system |
| Grammar | 📋 **Planned** | Stage 14 | Placeholder only |
| Tone | 📋 **Planned** | Stage 15 | Placeholder only |
| Content | 📋 **Planned** | Stage 16 | Placeholder only |
| Consistency | 📋 **Planned** | Stage 17 | Placeholder only |
| Editing | 📋 **Planned** | Stage 18 | Placeholder only |
| Readability | 📋 **Planned** | Stages 19-20 | Placeholder only |

### [Idea](./Idea/)
**Idea review and validation** (Future)

Review and validate initial idea concepts for viability, target audience fit, and potential impact.

- Concept viability assessment
- Target audience validation
- Originality and uniqueness check
- Resource requirements evaluation
- Impact assessment

**[→ View Idea Documentation](./Idea/README.md)**
**[→ View Idea Metadata](./Idea/_meta/)**

### [Script](./Script/)
**AI-powered script review** ⭐ NEW

Comprehensive script evaluation with scoring (0-100%) and improvement recommendations.

- Overall and category-specific scoring (engagement, pacing, clarity, etc.)
- YouTube short optimization (< 3 minutes, variable length)
- Prioritized improvement points with impact scores
- Script versioning for comparison and research
- Feedback loop integration with **[T/Script/Writer](../Script/Writer/)**

**[→ View Script Documentation](./Script/README.md)**
**[→ View Script Metadata](./Script/_meta/)**

### [Title](./Title/)
**AI-powered title review** ⭐ **IMPLEMENTED**

Title evaluation against script content and original idea intent for the iterative co-improvement workflow.

#### [Title/ByScriptAndIdea](./Title/ByScriptAndIdea/)
**Stage 4 (MVP-004): Review title v1 against script v1 and idea**

**Status**: ✅ Fully implemented with tests (21 tests passing)

Comprehensive title evaluation with dual alignment assessment:
- **Script Alignment**: Scoring (0-100%) on how well title matches script content
- **Idea Alignment**: Verification that title reflects original idea intent
- **Engagement Metrics**: Clickthrough potential, curiosity score, expectation setting
- **SEO Optimization**: Keyword relevance and searchability recommendations
- **Length Assessment**: Character count optimization for platform
- **Categorized Feedback**: 8 review categories with strengths/weaknesses
- **Improvement Points**: Prioritized suggestions with impact scores
- **Version Tracking**: Support for iterative improvements (v1, v2, v3+)
- **Workflow Integration**: Ready for Stage 6 (Title Improvements v2)

**Key Features**:
- Dual context review (script + idea)
- Comprehensive scoring system
- Prioritized improvement recommendations
- Serialization support (to_dict/from_dict)
- Iteration tracking and score trajectory
- Ready-for-improvement validation

**Testing**: All 21 tests passing, includes examples

**[→ View Title/ByScriptAndIdea Documentation](./Title/ByScriptAndIdea/README.md)**
**[→ View Title/ByScriptAndIdea Metadata](./Title/ByScriptAndIdea/_meta/)**
**[→ View Title/ByScriptAndIdea Tests](./Title/ByScriptAndIdea/_meta/tests/)**

### [Grammar](./Grammar/)
**Stage 14 (MVP-014): Grammar and syntax review**

**Status**: 📋 Placeholder only - needs implementation

Grammar checking and syntax corrections for technical correctness.

**What goes here**:
- Grammar corrections
- Punctuation adjustments
- Spelling fixes
- Syntax improvements
- Minor sentence reshaping for correctness
- Ensuring consistent tense and person

**Goal**: The script should be technically correct before deeper checks.

**Loop**: If FAILS → Return to Script Refinement (Stage 11)

**[→ View Grammar Documentation](./Grammar/README.md)**
**[→ View Grammar Metadata](./Grammar/_meta/)**

### [Tone](./Tone/)
**Stage 15 (MVP-015): Tone and voice consistency**

**Status**: 📋 Placeholder only - needs implementation

Ensure the emotional and narrative tone matches target audience and style.

**What goes here**:
- Adjustments to emotional intensity
- Style alignment (dark, suspense, dramatic, etc.)
- Voice and POV consistency
- Audience-specific tone tuning (e.g., US female 14–29)
- Balance of mystery/creepiness/drama
- Removing tonal mismatches

**Goal**: The script feels right, emotionally and stylistically.

**Loop**: If FAILS → Return to Script Refinement (Stage 11)

**[→ View Tone Documentation](./Tone/README.md)**
**[→ View Tone Metadata](./Tone/_meta/)**

### [Content](./Content/)
**Stage 16 (MVP-016): Content accuracy and narrative coherence**

**Status**: 📋 Placeholder only - needs implementation

High-level story review to check whether the script makes sense narratively.

**What goes here**:
- Notes about missing logic
- Plot issues, contradictions in events
- Character motivation fixes
- Pacing problems
- Structural feedback
- Scene ordering issues

**Goal**: Ensure the story works before refining language or tone.

**Loop**: If FAILS → Return to Script Refinement (Stage 11)

**[→ View Content Documentation](./Content/README.md)**
**[→ View Content Metadata](./Content/_meta/)**

### [Consistency](./Consistency/)
**Stage 17 (MVP-017): Internal consistency and continuity**

**Status**: 📋 Placeholder only - needs implementation

Verify internal continuity and logic across the entire script.

**What goes here**:
- Character name consistency
- Timeline alignment
- Location/scene continuity
- Repeated details matching
- Lore or fact alignment
- Ensuring no contradictions after edits

**Goal**: The script behaves like a coherent single story.

**Loop**: If FAILS → Return to Script Refinement (Stage 11)

**[→ View Consistency Documentation](./Consistency/README.md)**
**[→ View Consistency Metadata](./Consistency/_meta/)**

### [Editing](./Editing/)
**Stage 18 (MVP-018): Clarity, flow, and readability polish**

**Status**: 📋 Placeholder only - needs implementation

Improve clarity, flow, and readability (but not yet voiceover flow).

**What goes here**:
- Sentence rewrites
- Structural paragraph fixes
- Clarifying confusing lines
- Removing redundancy
- Improving transitions
- Rewriting sentences for clarity

**Goal**: Make the script smooth, readable, and stylistically coherent.

**Loop**: If FAILS → Return to Script Refinement (Stage 11)

**[→ View Editing Documentation](./Editing/README.md)**
**[→ View Editing Metadata](./Editing/_meta/)**

### [Readability](./Readability/)
**Stages 19-20 (MVP-019, MVP-020): Final voiceover suitability validation**

**Status**: 📋 Placeholder only - needs implementation

Final and MOST important review for the workflow. Focused 100% on spoken-word suitability.

**What goes here**:
- Voiceover flow improvements
- Natural rhythm and pacing notes
- Hard-to-read sentences
- Mouthfeel: ease of speaking aloud
- Adjustments for dramatic pauses or delivery
- Clarity when listened to (not read)

**Goal**: Ensure the script sounds perfect as narration.

**Stages**:
- **Stage 19**: Title Readability → Title Refinement loop if fails
- **Stage 20**: Script Readability → Script Refinement loop if fails

**Note**: This is the last review stage — if this passes, content is ready for Expert Review (Stage 21) or Finalization (Stage 23).

**[→ View Readability Documentation](./Readability/README.md)**
**[→ View Readability Metadata](./Readability/_meta/)**

## Module Metadata

**[→ View Review/_meta/docs/](./_meta/docs/)**
**[→ View Review/_meta/examples/](./_meta/examples/)**
**[→ View Review/_meta/tests/](./_meta/tests/)**

## Getting Started

### Running Title Review (Implemented)

```bash
# Install dependencies
cd T/Review/Title/ByScriptAndIdea
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH=/path/to/PrismQ

# Run examples
python T/Review/Title/ByScriptAndIdea/_meta/examples/example_usage.py

# Run tests
pytest T/Review/Title/ByScriptAndIdea/_meta/tests/ -v
```

### Using Title Review in Code

```python
from T.Review.Title.ByScriptAndIdea import (
    TitleReview,
    TitleReviewCategory,
    TitleImprovementPoint,
    TitleCategoryScore
)

# Create a title review
review = TitleReview(
    title_id="title-001",
    title_text="The Echo - A Haunting Discovery",
    title_version="v1",
    overall_score=78,
    script_id="script-001",
    script_alignment_score=85,
    idea_id="idea-001",
    idea_alignment_score=82,
    engagement_score=75
)

# Check if ready for improvement stage
if review.is_ready_for_improvement():
    print("Ready for Stage 6: Title Improvements v2")
    
# Get high-priority improvements
improvements = review.get_high_priority_improvements()
for imp in improvements:
    print(f"{imp.title}: {imp.description}")
```

### Quality Review Modules (Planned)

The following quality review modules are planned for Stages 14-20 but not yet implemented:
- Grammar (Stage 14)
- Tone (Stage 15)
- Content (Stage 16)
- Consistency (Stage 17)
- Editing (Stage 18)
- Readability (Stages 19-20)

These will follow a similar pattern to Title Review with:
- Comprehensive data models
- Scoring systems (0-100%)
- Improvement recommendations
- Loop-back integration with refinement stages
- Test coverage

## Navigation

**[← Back to T](../README.md)** | **[→ T/_meta](../_meta/)**
