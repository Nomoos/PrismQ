# T/Review/Title/ByScriptAndIdea - AI Title Review Module

**Namespace**: `PrismQ.T.Review.Title.ByScriptAndIdea`

AI-powered title evaluation against script content and original idea intent with comprehensive scoring and improvement recommendations.

## Purpose

The Title Review module provides:
- **Title-to-script alignment** evaluation
- **Title-to-idea intent** verification
- **Audience engagement** assessment
- **Expectation setting** validation
- **SEO optimization** recommendations
- **Prioritized improvement** suggestions

This module reviews title v1 against script v1 and the original idea to ensure the title accurately represents the script content, reflects the idea's intent, and sets appropriate audience expectations.

## Core Components

### TitleReview
Main data model for title evaluation with:
- Overall quality score (0-100%)
- Category-specific scores and analysis
- Prioritized improvement points
- Script alignment metrics
- Idea alignment metrics
- Engagement and SEO assessment

### TitleReviewCategory
Evaluation categories:
- `SCRIPT_ALIGNMENT` - Title matches script content
- `IDEA_ALIGNMENT` - Title reflects original idea intent
- `ENGAGEMENT` - Title is compelling and attention-grabbing
- `EXPECTATION_SETTING` - Title sets correct expectations
- `CLARITY` - Title is clear and understandable
- `SEO_OPTIMIZATION` - SEO keywords and searchability
- `AUDIENCE_FIT` - Target audience appropriateness
- `LENGTH` - Title length optimization

## Workflow Position

```
Title v1 (from Idea) + Script v1 (from Idea + Title) + Idea
    ↓
TitleReview (AI Reviewer) - Stage 4: #MVP-004
    ↓
Title v2 (improvements based on feedback) - Stage 6
```

**Stage 4** (MVP-004): Review title v1 against script v1 and idea
- Input: Title v1, Script v1, Idea
- Output: Review feedback for title improvements
- Next: Used in Stage 6 for title v2 generation

## Usage Example

```python
from PrismQ.T.Review.Title.ByScriptAndIdea import (
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
    
    # Script context
    script_id="script-001",
    script_title="The Echo",
    script_summary="A horror short about mysterious echoes in an abandoned house",
    script_version="v1",
    script_alignment_score=85,
    key_script_elements=["echo", "haunting", "discovery", "abandoned house"],
    
    # Idea context
    idea_id="idea-001",
    idea_summary="Horror story about sounds that repeat with increasing intensity",
    idea_intent="Create suspense through auditory elements and psychological tension",
    idea_alignment_score=82,
    target_audience="Horror enthusiasts aged 18-35",
    
    # Engagement metrics
    engagement_score=75,
    clickthrough_potential=72,
    curiosity_score=80,
    expectation_accuracy=76,
    
    # SEO metrics
    seo_score=68,
    keyword_relevance=70,
    suggested_keywords=["echo", "horror short", "haunting", "mystery"]
)

# Add category scores
review.category_scores.append(TitleCategoryScore(
    category=TitleReviewCategory.SCRIPT_ALIGNMENT,
    score=85,
    reasoning="Title accurately reflects script content with 'echo' and 'haunting'",
    strengths=["Includes main element (echo)", "Indicates genre (haunting)"],
    weaknesses=["Could be more specific about setting", "Generic subtitle"]
))

review.category_scores.append(TitleCategoryScore(
    category=TitleReviewCategory.IDEA_ALIGNMENT,
    score=82,
    reasoning="Captures the auditory suspense concept from the idea",
    strengths=["Reflects sound-based horror", "Mysterious tone"],
    weaknesses=["Doesn't hint at intensification element"]
))

# Add improvement points
review.improvement_points.append(TitleImprovementPoint(
    category=TitleReviewCategory.SCRIPT_ALIGNMENT,
    title="Add setting reference",
    description="Include reference to abandoned house setting",
    priority="high",
    impact_score=20,
    suggested_fix="Consider: 'The Echo of [Location Name]' or 'The Abandoned Echo'"
))

review.improvement_points.append(TitleImprovementPoint(
    category=TitleReviewCategory.ENGAGEMENT,
    title="Strengthen emotional hook",
    description="Make subtitle more emotionally compelling",
    priority="medium",
    impact_score=15,
    suggested_fix="Replace 'A Haunting Discovery' with something more specific like 'When Silence Answers Back'"
))

# Check alignment with script and idea
alignment = review.get_alignment_summary()
print(f"Script alignment: {alignment['script_alignment']}%")
print(f"Idea alignment: {alignment['idea_alignment']}%")
print(f"Overall alignment status: {alignment['alignment_status']}")
print(f"Needs improvement: {alignment['needs_improvement']}")

# Get engagement assessment
engagement = review.get_engagement_summary()
print(f"Composite engagement score: {engagement['composite_score']}%")
print(f"Ready for publication: {engagement['ready_for_publication']}")
print(f"Top recommendations: {[r.title for r in engagement['recommendations']]}")

# Check length
length = review.get_length_assessment()
print(f"Length: {length['current_length']} chars (optimal: {length['optimal_length']})")
print(f"Status: {length['status']}")
print(f"Feedback: {length['feedback']}")

# Get high-priority improvements
high_priority = review.get_high_priority_improvements()
for imp in high_priority:
    print(f"- {imp.title} (impact: +{imp.impact_score}%)")
    print(f"  {imp.description}")
    if imp.suggested_fix:
        print(f"  Suggestion: {imp.suggested_fix}")

# Check if ready for improvement stage
if review.is_ready_for_improvement():
    print("Review is complete and ready for title improvement (v2)")
```

## Key Features

### Dual Alignment Assessment
- **Script alignment**: Evaluate how well the title reflects script content
- **Idea alignment**: Verify title captures original idea intent
- **Cross-validation**: Ensure consistency across all three elements

### Engagement Optimization
- **Clickthrough potential**: Estimate CTR based on title appeal
- **Curiosity generation**: Measure how well title creates curiosity
- **Expectation accuracy**: Assess if title sets correct expectations
- **Composite scoring**: Weighted engagement metrics

### SEO & Length Optimization
- **Keyword relevance**: Evaluate keyword integration
- **Suggested keywords**: Recommend additional keywords
- **Length assessment**: Check character count vs. optimal length
- **Platform optimization**: Consider platform-specific requirements

### Improvement Tracking
- **Priority scoring**: Rank improvements by impact
- **Category-specific**: Track improvements per review category
- **Iteration support**: Monitor score changes across versions
- **Quick wins**: Identify easy improvements with high impact

## Module Structure

```
T/Review/Title/ByScriptAndIdea/
├── __init__.py              # Module exports
├── title_review.py          # Core review model
├── README.md                # This file
└── _meta/
    ├── docs/                # Additional documentation
    ├── examples/            # Usage examples
    └── tests/               # Test suites
        ├── __init__.py
        └── test_title_review.py
```

## Integration Points

### With Title Generator
The Review module feeds into the Title Generator's improvement process:

```python
from PrismQ.T.Review.Title.ByScriptAndIdea import TitleReview
from PrismQ.T.Title.FromOriginalTitleAndReviewAndScript import TitleGenerator

# AI Reviewer evaluates title
review = TitleReview(...)

# AI Generator creates improved version based on review
generator = TitleGenerator()
result = generator.improve_from_review(
    original_title="The Echo - A Haunting Discovery",
    review=review,
    script_text=script_text,
    idea_summary=idea_summary
)

# Check if another iteration needed
if review.overall_score < 80:
    # Run another review-improvement cycle
    pass
```

### With Idea Model
Reviews reference the original Idea:

```python
from PrismQ.T.Idea.Model import Idea
from PrismQ.T.Review.Title.ByScriptAndIdea import TitleReview

idea = Idea(...)
review = TitleReview(
    title_id="title-001",
    title_text="The Echo",
    idea_id=idea.id,
    idea_summary=idea.summary,
    idea_intent=idea.core_concept
)

# Check alignment with original intent
alignment = review.get_alignment_summary()
if alignment['idea_alignment'] < 70:
    print(f"Title doesn't align well with idea: {alignment['idea_alignment']}%")
```

### With Script Model
Reviews evaluate against script content:

```python
from PrismQ.T.Review.Title.ByScriptAndIdea import TitleReview

review = TitleReview(
    title_id="title-001",
    title_text="The Echo",
    script_id="script-001",
    script_summary=script.summary,
    key_script_elements=["echo", "haunting", "abandoned", "discovery"]
)

# Verify script alignment
if review.script_alignment_score < 70:
    print(f"Title doesn't match script content well")
```

## Best Practices

### For AI Reviewers
1. **Be specific** - Provide concrete examples and suggested fixes
2. **Prioritize impact** - Focus on high-impact improvements first
3. **Consider context** - Evaluate title in context of both script and idea
4. **Track alignment** - Ensure title works for both script content and idea intent
5. **Think audience** - Consider target audience expectations

### For Integration
1. **Check readiness** - Use `is_ready_for_improvement()` before proceeding
2. **Monitor alignment** - Track both script and idea alignment scores
3. **Iterate wisely** - Maximum 2-3 iterations to avoid diminishing returns
4. **Store reviews** - Keep review history for learning and analysis
5. **Consider confidence** - Low confidence scores may need human review

## Review Criteria

### Script Alignment
- Does title reference key script elements?
- Does title indicate the script's genre/tone?
- Does title match the script's narrative arc?
- Does title reflect the script's climax or key scenes?

### Idea Alignment
- Does title capture the core concept from the idea?
- Does title reflect the idea's intent and purpose?
- Does title align with the idea's target audience?
- Does title convey the idea's unique value?

### Engagement
- Is title attention-grabbing?
- Does title create curiosity?
- Is title memorable?
- Does title have emotional appeal?

### Expectation Setting
- Does title accurately represent content?
- Does title avoid misleading the audience?
- Does title set appropriate tone expectations?
- Does title promise what the content delivers?

## Quality Gates

### Approval Thresholds
- **Overall score**: ≥ 80% for approval
- **Script alignment**: ≥ 75% required
- **Idea alignment**: ≥ 75% required
- **Engagement**: ≥ 70% recommended
- **Expectation accuracy**: ≥ 70% critical

### Review Completeness
- At least 4 category scores provided
- At least 2 improvement points identified
- Script and idea context included
- Alignment assessed and documented

## Related Modules

- **[Title/FromIdea](../../../Title/FromIdea/README.md)** - Initial title creation (v1)
- **[Title/FromOriginalTitleAndReviewAndScript](../../../Title/FromOriginalTitleAndReviewAndScript/README.md)** - Title improvements (v2+)
- **[Script/FromIdeaAndTitle](../../../Script/FromIdeaAndTitle/README.md)** - Script creation from title
- **[Review/Script](../../Script/README.md)** - Script review module
- **[Idea/Model](../../../Idea/Model/README.md)** - Core idea data model

## Navigation

**[← Back to Review](../../README.md)** | **[→ Review/_meta](../../_meta/)** | **[→ T Module](../../../README.md)**

---

*Part of the PrismQ AI-powered content creation workflow - Stage 4: #MVP-004*
