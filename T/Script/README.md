# T/Script - Script Development Module

**Namespace**: `PrismQ.T.Script`

Develop and refine scripts through iterative drafting, improvement, and optimization.

## Purpose

Transform structured ideas into polished scripts ready for review and publication.

## Submodules

#### [FromIdeaAndTitle](./FromIdeaAndTitle/)
**Stage 3: Initial script draft from idea and title** (v1)

Generate initial script draft from the idea and initial title.

**[→ View FromIdeaAndTitle Documentation](./FromIdeaAndTitle/README.md)**
**[→ View FromIdeaAndTitle Metadata](./FromIdeaAndTitle/_meta/)**

#### [FromOriginalScriptAndReviewAndTitle](./FromOriginalScriptAndReviewAndTitle/)
**Stages 7, 11, 14-18, 20: All script improvements** (v2, v3, v4, v5...)

Generate improved script versions using review feedback, original script, and title context.

This state handles:
- **Stage 7**: First improvements (v1 → v2) using both reviews + new title
- **Stage 11**: Iterative refinements (v2 → v3+) until accepted
- **Stages 14-18**: Quality reviews (Grammar, Tone, Content, Consistency, Editing)
- **Stage 20 Feedback**: Final voiceover readability polish

**[→ View FromOriginalScriptAndReviewAndTitle Documentation](./FromOriginalScriptAndReviewAndTitle/README.md)**
**[→ View FromOriginalScriptAndReviewAndTitle Metadata](./FromOriginalScriptAndReviewAndTitle/_meta/)**

#### [Writer](./Writer/)
**AI script writer with feedback loop** ⭐ NEW

AI-powered script writer that optimizes content based on review feedback from **[T/Review/Script](../Review/Script/)**.

- Iterative optimization (review → write → review cycle)
- Multiple optimization strategies
- Score-driven improvement (target: 80%+)
- YouTube short content generation

**[→ View Writer Documentation](./Writer/README.md)**
**[→ View Writer Metadata](./Writer/_meta/)**

## Module Metadata

**[→ View Script/_meta/docs/](./_meta/docs/)**
**[→ View Script/_meta/examples/](./_meta/examples/)**
**[→ View Script/_meta/tests/](./_meta/tests/)**

## AI-Powered Feedback Loop Workflow

The **[T/Review/Script](../Review/Script/)** (AI Script Reviewer) and Writer modules work together in an iterative feedback loop:

```
1. Draft → Original Script (145 seconds)
              ↓
2. AI Reviewer → Evaluates (Score: 65%)
   - Length: Too long for YouTube short
   - Pacing: Middle section drags
   - Engagement: Strong hook, weak middle
              ↓
3. AI Writer → Optimizes (applies improvements)
   - Cuts 30 seconds from investigation
   - Strengthens opening hook
   - Improves pacing
              ↓
4. AI Reviewer → Re-evaluates (Score: 78%)
   - Length: Better, still needs 10s reduction
   - Pacing: Much improved
   - Engagement: Excellent
              ↓
5. AI Writer → Final optimization
   - Fine-tunes climax sequence
   - Removes remaining padding
              ↓
6. AI Reviewer → Final evaluation (Score: 85% ✓)
   - Target reached!
   - Ready for publication
```

### Key Features

- **Automatic iteration** until target score reached (default: 80%)
- **Maximum 3 iterations** to avoid diminishing returns
- **YouTube short optimization** (< 60s or < 180s)
- **Variable length support** for different content types
- **Score progression tracking** across iterations

### Quick Start

```python
from PrismQ.T.Review.Script import ScriptReview, ContentLength
from PrismQ.T.Script.Writer import ScriptWriter

# AI Reviewer evaluates
review = ScriptReview(
    script_id="script-001",
    script_title="Horror Short",
    overall_score=65,
    is_youtube_short=True,
    current_length_seconds=145,
    optimal_length_seconds=90
)

# AI Writer optimizes
writer = ScriptWriter(target_score_threshold=80)
result = writer.optimize_from_review(
    original_script=script_text,
    review=review
)

# Check if iteration needed
if writer.should_continue_iteration():
    # Run another review-write cycle
    pass
```

See **[Feedback Loop Example](../Review/Script/_meta/examples/feedback_loop_example.py)** for complete implementation.

## Navigation

**[← Back to T](../README.md)** | **[→ T/_meta](../_meta/)**
