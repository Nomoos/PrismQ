# T/Review/Script - AI Script Review Module

**Namespace**: `PrismQ.T.Review.Script`

AI-powered script evaluation with comprehensive scoring system (0-100%) and detailed improvement recommendations for target audience optimization.

## Purpose

The Review module provides:
- **AI-driven script evaluation** with numerical scoring
- **Category-specific analysis** (engagement, pacing, clarity, etc.)
- **Prioritized improvement recommendations** with impact estimates
- **YouTube short optimization** (< 3 minutes, variable length)
- **Feedback loop integration** with Script Writer
- **Script versioning** for comparison and research ⭐ NEW

## Core Components

### ScriptReview
Main data model for script evaluation with:
- Overall quality score (0-100%)
- Category-specific scores and analysis
- Prioritized improvement points
- YouTube short readiness assessment
- Target audience alignment metrics
- **Script version tracking** for research

### ScriptVersion ⭐ NEW
Version tracking for comparison and research:
- Stores script text for each iteration
- Tracks changes between versions
- Enables side-by-side comparison
- Measures feedback loop effectiveness

### ReviewCategory
Evaluation categories:
- `ENGAGEMENT` - Hook strength, audience retention
- `PACING` - Timing, rhythm, flow
- `CLARITY` - Message clarity, understandability
- `AUDIENCE_FIT` - Target audience alignment
- `STRUCTURE` - Story structure, organization
- `IMPACT` - Emotional impact, memorability
- `YOUTUBE_SHORT_OPTIMIZATION` - YouTube short specific
- `LENGTH_OPTIMIZATION` - Duration optimization

### ContentLength
Target content length categories:
- `YOUTUBE_SHORT` - < 60 seconds
- `YOUTUBE_SHORT_EXTENDED` - 60-180 seconds
- `SHORT_FORM` - < 3 minutes
- `MEDIUM_FORM` - 3-10 minutes
- `LONG_FORM` - > 10 minutes
- `VARIABLE` - Variable length

## Workflow Position

```
ScriptDraft → ScriptReview (AI Reviewer) → ScriptWriter (with feedback) → ScriptApproved
                    ↓
        (Feedback Loop if score < 80%)
```

## Usage Example

```python
from PrismQ.T.Review.Script import (
    ScriptReview,
    ReviewCategory,
    ContentLength,
    ImprovementPoint,
    CategoryScore
)

# Create a review
review = ScriptReview(
    script_id="script-001",
    script_title="The Echo - Horror Short",
    overall_score=72,
    target_audience="Horror enthusiasts aged 18-35",
    audience_alignment_score=85,
    target_length=ContentLength.YOUTUBE_SHORT_EXTENDED,
    current_length_seconds=145,
    optimal_length_seconds=90,
    is_youtube_short=True,
    hook_strength_score=95,
    retention_score=68,
    viral_potential_score=78,
    needs_major_revision=False,
    iteration_number=1
)

# Add category scores
review.category_scores.append(CategoryScore(
    category=ReviewCategory.ENGAGEMENT,
    score=85,
    reasoning="Strong hook, needs better pacing in middle",
    strengths=["Compelling opening", "Emotional impact"],
    weaknesses=["Mid-section drag", "Predictable twist"]
))

# Add improvement points
review.improvement_points.append(ImprovementPoint(
    category=ReviewCategory.PACING,
    title="Reduce middle section length",
    description="Cut 30-40 seconds from investigation sequence",
    priority="high",
    impact_score=25,
    suggested_fix="Focus on 2-3 key moments instead of 5"
))

# Check YouTube short readiness
readiness = review.get_youtube_short_readiness()
print(f"Ready: {readiness['ready']}")
print(f"Readiness Score: {readiness['readiness_score']}%")
print(f"Length: {readiness['length_feedback']}")

# Get high-priority improvements
high_priority = review.get_high_priority_improvements()
for imp in high_priority:
    print(f"- {imp.title} (impact: +{imp.impact_score})")

# Store script version for comparison and research
review.add_script_version(
    script_text=script_text,
    length_seconds=145,
    created_by="AI-Writer-001",
    changes_from_previous="Initial version after first review"
)

# Later, compare versions
comparison = review.get_version_comparison()
if comparison["comparison_available"]:
    print(f"Versions: {comparison['versions_count']}")
    print(f"Score improvement: +{comparison['improvements']['score_change']}%")
    print(f"Length change: {comparison['improvements']['length_change_seconds']}s")
```

## Key Features

### Scoring System
- **0-100% scale** for overall and category scores
- **Confidence scoring** for AI evaluation reliability
- **Impact scoring** for improvement recommendations
- **Trajectory tracking** across iterations

### YouTube Short Optimization
- **Length compliance** checking (≤60s or ≤180s)
- **Hook strength** evaluation (first 3 seconds)
- **Retention prediction** based on content analysis
- **Viral potential** scoring
- **Readiness assessment** with actionable feedback

### Feedback Loop Integration
- **Iteration tracking** across review cycles
- **Score improvement** monitoring
- **Previous review linking** for context
- **Major revision flagging** for significant issues

### Audience Alignment
- **Target audience** specification
- **Alignment scoring** (0-100%)
- **Demographic optimization** recommendations
- **Platform-specific** guidance

### Script Versioning ⭐ NEW
- **Version storage** - Store complete script text for each iteration
- **Change tracking** - Track what changed between versions
- **Side-by-side comparison** - Compare any two versions
- **Research support** - Analyze feedback loop effectiveness
- **Export capability** - Export version history for analysis

## Module Structure

```
T/Review/Script/
├── __init__.py              # Module exports
├── script_review.py         # Core review model
├── README.md                # This file
└── _meta/
    ├── docs/                # Additional documentation
    ├── examples/            # Usage examples
    └── tests/               # Test suites
```

## Integration Points

### With Script Writer
The Review module feeds directly into the Script Writer's feedback loop:

```python
from PrismQ.T.Review.Script import ScriptReview
from PrismQ.T.Script.Writer import ScriptWriter

# AI Reviewer evaluates script
review = ScriptReview(...)

# AI Writer optimizes based on review
writer = ScriptWriter()
result = writer.optimize_from_review(
    original_script=script_text,
    review=review,
    target_audience="Horror fans 18-35"
)

# Check if another iteration needed
if not review.overall_score >= 80:
    # Run another review-write cycle
    pass
```

### With Idea Model
Reviews can reference and update the Idea status:

```python
from PrismQ.T.Idea.Model import Idea, IdeaStatus
from PrismQ.T.Review.Script import ScriptReview

idea = Idea(...)
review = ScriptReview(script_id=f"script-{idea.title}")

if review.overall_score >= 80:
    idea.status = IdeaStatus.SCRIPT_APPROVED
else:
    idea.status = IdeaStatus.SCRIPT_REVIEW
```

## Best Practices

### For AI Reviewers
1. **Be specific** - Provide concrete examples and suggested fixes
2. **Prioritize impact** - Focus on high-impact improvements first
3. **Consider audience** - Align recommendations with target demographic
4. **Track progress** - Monitor score improvement across iterations
5. **Set realistic targets** - 80%+ for approval, iterate below that

### For Integration
1. **Check readiness** - Use `get_youtube_short_readiness()` for shorts
2. **Iterate wisely** - Maximum 3 iterations to avoid diminishing returns
3. **Store reviews** - Keep review history for learning and analysis
4. **Monitor confidence** - Low confidence scores may need human review

## Related Modules

- **[Script/Writer](../Writer/README.md)** - AI Writer with feedback loop
- **[Script/Draft](../Draft/README.md)** - Initial script drafting
- **[Script/Optimization](../Optimization/README.md)** - Script optimization
- **[Idea/Model](../../Idea/Model/README.md)** - Core idea data model

## Navigation

**[← Back to Script](../README.md)** | **[Writer Module →](../Writer/README.md)** | **[T Module →](../../README.md)**

---

*Part of the PrismQ AI-powered content creation workflow*
