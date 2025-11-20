# T/Script/Writer - AI Script Writer with Feedback Loop

**Namespace**: `PrismQ.T.Script.Writer`

AI-powered script writer with iterative optimization based on review feedback from the AI Script Reviewer.

## Purpose

The Writer module implements:
- **Feedback loop integration** with AI Script Reviewer
- **Iterative optimization** based on review reports
- **Audience-aligned content** generation
- **YouTube short optimization** (< 3 minutes, variable length)
- **Score-driven improvement** (target: 80%+)

## Core Components

### ScriptWriter
Main class implementing the feedback loop:
- Takes original text + review report
- Analyzes improvement points by priority
- Applies targeted optimizations
- Tracks iteration progress
- Manages score improvement trajectory

### OptimizationStrategy
Strategies for script optimization:
- `YOUTUBE_SHORT` - Optimize for YouTube shorts
- `ENGAGEMENT_BOOST` - Focus on engagement
- `PACING_IMPROVEMENT` - Fix pacing issues
- `CLARITY_ENHANCEMENT` - Improve clarity
- `AUDIENCE_ALIGNMENT` - Better audience fit
- `COMPREHENSIVE` - Address all issues

### OptimizationResult
Result of optimization containing:
- Original and optimized text
- List of changes made
- Strategy used
- Estimated score improvement
- Length before/after
- Key improvements applied

## Workflow Position

```
ScriptDraft → AI Reviewer → Review Report → AI Writer → Optimized Script
                       ↓                              ↓
                   (Feedback Loop if score < 80%)
```

## The Feedback Loop

The Writer implements an iterative feedback loop:

```
1. AI Reviewer evaluates script → Score: 65%
2. AI Writer receives review report
3. AI Writer applies high-priority improvements
4. AI Reviewer re-evaluates → Score: 78%
5. AI Writer applies remaining improvements
6. AI Reviewer final evaluation → Score: 85% ✓
```

Loop continues until:
- Score reaches threshold (default: 80%)
- Maximum iterations reached (default: 3)
- Diminishing returns detected (< 5% improvement)

## Usage Example

### Basic Feedback Loop

```python
from PrismQ.T.Script.Review import ScriptReview, ReviewCategory
from PrismQ.T.Script.Writer import ScriptWriter, OptimizationStrategy

# Original script
original_script = """
A girl wakes up at 3 AM and hears a voice calling her name.
The voice sounds exactly like her own...
[145 seconds of content]
"""

# AI Reviewer evaluates (score: 72%)
review = ScriptReview(
    script_id="script-001",
    script_title="The Echo",
    overall_score=72,
    current_length_seconds=145,
    optimal_length_seconds=90,
    is_youtube_short=True,
    needs_major_revision=False
)

# Add improvement points
review.improvement_points = [
    ImprovementPoint(
        category=ReviewCategory.PACING,
        title="Reduce middle section",
        description="Cut 30-40 seconds from investigation",
        priority="high",
        impact_score=25,
        suggested_fix="Focus on 2-3 key moments instead of 5"
    )
]

# AI Writer optimizes based on review
writer = ScriptWriter(
    target_score_threshold=80,
    max_iterations=3,
    optimization_strategy=OptimizationStrategy.YOUTUBE_SHORT
)

result = writer.optimize_from_review(
    original_script=original_script,
    review=review,
    target_audience="Horror enthusiasts aged 18-35"
)

# Check results
print(f"Changes made: {len(result.changes_made)}")
print(f"Length: {result.length_before_seconds}s → {result.length_after_seconds}s")
print(f"Expected improvement: +{result.estimated_score_improvement}%")
print(f"\nOptimized script:\n{result.optimized_text}")
```

### Complete Feedback Loop

```python
from PrismQ.T.Script.Review import ScriptReview
from PrismQ.T.Script.Writer import ScriptWriter

# Initialize writer
writer = ScriptWriter(
    target_score_threshold=80,
    max_iterations=3
)

current_script = original_script
iteration = 0

# Feedback loop
while writer.should_continue_iteration():
    iteration += 1
    print(f"\n=== Iteration {iteration} ===")
    
    # AI Reviewer evaluates
    review = ai_reviewer.evaluate(current_script)
    print(f"Review Score: {review.overall_score}%")
    
    # AI Writer optimizes
    result = writer.optimize_from_review(
        original_script=current_script,
        review=review
    )
    
    current_script = result.optimized_text
    print(f"Applied {len(result.changes_made)} improvements")
    print(f"Expected new score: {review.overall_score + result.estimated_score_improvement}%")
    
    # Check if target reached
    if review.overall_score >= writer.target_score_threshold:
        print(f"\n✓ Target score reached!")
        break

# Get summary
summary = writer.get_feedback_loop_summary()
print(f"\n=== Summary ===")
print(f"Total iterations: {summary['current_iteration']}")
print(f"Score: {summary['initial_score']}% → {summary['current_score']}%")
print(f"Total improvement: +{summary['total_improvement']}%")
print(f"Improvements applied: {summary['improvements_applied']}")
```

### YouTube Short Optimization

```python
# Configure for YouTube shorts
writer = ScriptWriter(
    optimization_strategy=OptimizationStrategy.YOUTUBE_SHORT,
    target_score_threshold=85
)

# Set YouTube short context
review = ScriptReview(
    script_id="short-001",
    script_title="Quick Horror",
    overall_score=70,
    is_youtube_short=True,
    target_length=ContentLength.YOUTUBE_SHORT,  # < 60s
    current_length_seconds=85,
    optimal_length_seconds=55,
    hook_strength_score=92,
    retention_score=65,
    viral_potential_score=75
)

# Optimize
result = writer.optimize_from_review(
    original_script=long_script,
    review=review
)

print(f"Optimized for YouTube short:")
print(f"  Length: {result.length_before_seconds}s → {result.length_after_seconds}s")
print(f"  Strategy: {result.optimization_strategy.value}")
print(f"  Key improvements: {', '.join(result.key_improvements)}")
```

## Key Features

### Intelligent Strategy Selection
Writer automatically selects optimization strategy based on:
- Review category weaknesses
- YouTube short requirements
- Length optimization needs
- Audience alignment gaps

### Progress Tracking
- **Score progression** across iterations
- **Cumulative improvements** list
- **Iteration history** with details
- **Performance metrics** and analytics

### Feedback Loop Management
- **Automatic iteration** control
- **Diminishing returns** detection
- **Target threshold** enforcement
- **Maximum iterations** limit

### Optimization Context
- **Target audience** adaptation
- **Length optimization** (variable)
- **YouTube short mode** support
- **Focus areas** from review

## Module Structure

```
T/Script/Writer/
├── __init__.py              # Module exports
├── script_writer.py         # Core writer model
├── README.md                # This file
└── _meta/
    ├── docs/                # Additional documentation
    ├── examples/            # Usage examples
    └── tests/               # Test suites
```

## Integration Points

### With Script Review
Primary integration for feedback loop:

```python
# 1. Review evaluates
review = ScriptReview(...)

# 2. Writer optimizes
writer = ScriptWriter()
result = writer.optimize_from_review(
    original_script=script,
    review=review
)

# 3. Check if continue
if writer.should_continue_iteration():
    # Another iteration needed
    pass
```

### With Idea Model
Track optimization in workflow:

```python
from PrismQ.T.Idea.Model import Idea, IdeaStatus

idea = Idea(...)
writer = ScriptWriter()

# Optimize
result = writer.optimize_from_review(original, review)

# Update status
if writer.current_score >= 80:
    idea.status = IdeaStatus.SCRIPT_APPROVED
else:
    idea.status = IdeaStatus.SCRIPT_REVIEW
```

## Best Practices

### For AI Writers
1. **Prioritize impact** - Apply high-impact improvements first
2. **Respect audience** - Maintain target audience alignment
3. **Monitor progress** - Track score improvement trajectory
4. **Avoid over-iteration** - Stop at 3 iterations max
5. **Document changes** - List all modifications clearly

### For Integration
1. **Set realistic thresholds** - 80% is good, 90% is excellent
2. **Limit iterations** - 3 max to avoid diminishing returns
3. **Check convergence** - Stop if improvement < 5%
4. **Store history** - Keep iteration records for analysis
5. **Monitor confidence** - Consider human review if AI confidence low

## Configuration

### Default Settings
```python
writer = ScriptWriter(
    target_score_threshold=80,    # Target quality score
    max_iterations=3,              # Maximum feedback loops
    optimization_strategy=OptimizationStrategy.COMPREHENSIVE
)
```

### YouTube Short Settings
```python
writer = ScriptWriter(
    target_score_threshold=85,     # Higher bar for shorts
    max_iterations=2,              # Faster iteration
    optimization_strategy=OptimizationStrategy.YOUTUBE_SHORT
)
writer.youtube_short_mode = True
writer.target_length_seconds = 60  # Strict 60s limit
```

## Related Modules

- **[Script/Review](../Review/README.md)** - AI Script Reviewer
- **[Script/Draft](../Draft/README.md)** - Initial script drafting
- **[Script/Improvements](../Improvements/README.md)** - Script enhancement
- **[Script/Optimization](../Optimization/README.md)** - Script optimization

## Navigation

**[← Back to Script](../README.md)** | **[Review Module →](../Review/README.md)** | **[T Module →](../../README.md)**

---

*Part of the PrismQ AI-powered content creation workflow*
