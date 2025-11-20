# T/Script - Script Development Module

**Namespace**: `PrismQ.T.Script`

Develop and refine scripts through iterative drafting, improvement, and optimization.

## Purpose

Transform structured ideas into polished scripts ready for review and publication.

## Submodules

### [Draft](./Draft/)
**Initial script writing**

First draft creation from idea outlines.

**[→ View Draft Documentation](./Draft/README.md)**
**[→ View Draft Metadata](./Draft/_meta/)**

### [Review](./Review/)
**AI-powered script review** ⭐ NEW

AI script reviewer with comprehensive scoring (0-100%) and improvement recommendations.

- Category-specific evaluation (engagement, pacing, clarity, etc.)
- YouTube short optimization (< 3 minutes, variable length)
- Prioritized improvement points with impact scores
- Target audience alignment scoring

**[→ View Review Documentation](./Review/README.md)**
**[→ View Review Metadata](./Review/_meta/)**

### [Writer](./Writer/)
**AI script writer with feedback loop** ⭐ NEW

AI-powered script writer that optimizes content based on review feedback.

- Iterative optimization (review → write → review cycle)
- Multiple optimization strategies
- Score-driven improvement (target: 80%+)
- YouTube short content generation

**[→ View Writer Documentation](./Writer/README.md)**
**[→ View Writer Metadata](./Writer/_meta/)**

### [Improvements](./Improvements/)
**Script enhancement**

Iterative improvements and refinements.

**[→ View Improvements Documentation](./Improvements/README.md)**
**[→ View Improvements Metadata](./Improvements/_meta/)**

### [Optimization](./Optimization/)
**Script optimization**

Final optimization for flow, readability, and impact.

**[→ View Optimization Documentation](./Optimization/README.md)**
**[→ View Optimization Metadata](./Optimization/_meta/)**

## Module Metadata

**[→ View Script/_meta/docs/](./_meta/docs/)**
**[→ View Script/_meta/examples/](./_meta/examples/)**
**[→ View Script/_meta/tests/](./_meta/tests/)**

## AI-Powered Feedback Loop Workflow

The Review and Writer modules work together in an iterative feedback loop:

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
from PrismQ.T.Script.Review import ScriptReview, ContentLength
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

See **[Feedback Loop Example](./Review/_meta/examples/feedback_loop_example.py)** for complete implementation.

## Navigation

**[← Back to T](../README.md)** | **[→ T/_meta](../_meta/)**
