# T/Story/Polish - GPT-Based Expert Story Polishing

**Namespace**: `PrismQ.T.Story.Polish`

Apply expert-level improvements to title and script based on GPT ExpertReview feedback.

## Purpose

Implement the expert-level improvements suggested by GPT ExpertReview (Stage 21) to achieve professional publishing quality. This is Stage 22 in the MVP workflow.

## Workflow Position

**Stage 22** in MVP workflow: After expert review, before publishing

```
Stage 21: Story.ExpertReview (GPT-based)
    ↓ Improvements needed
Stage 22: Story.Polish (GPT-based) ← THIS MODULE
    ↓
Return to Stage 21: Story.ExpertReview for verification
    ↓ If ready
Stage 23: Publishing.Finalization
```

## Module Structure

```
Polish/
├── polish.py              # Core implementation
├── __init__.py            # Module exports
├── _meta/
│   ├── tests/            # Test suite (25 tests)
│   │   ├── __init__.py
│   │   └── test_polish.py
│   └── examples/         # Usage examples
│       ├── __init__.py
│       └── example_usage.py
└── README.md             # This file
```

## Key Components

### Data Models

- **`StoryPolish`**: Result of polishing with all metadata
- **`ChangeLogEntry`**: Single change made during polishing
- **`PolishConfig`**: Configuration for polishing behavior

### Core Class

- **`StoryPolisher`**: Main class that applies expert improvements

### Enums

- **`ComponentType`**: TITLE, SCRIPT
- **`ChangeType`**: CAPITALIZATION, OPENING_ENHANCEMENT, etc.
- **`PriorityLevel`**: HIGH, MEDIUM, LOW

## Usage

### Basic Usage

```python
from T.Story.Polish import polish_story_with_gpt

# Expert review data from Stage 21
review_data = {
    'overall_assessment': {
        'quality_score': 92,
        'ready_for_publishing': False
    },
    'improvement_suggestions': [
        {
            'component': 'title',
            'priority': 'high',
            'suggestion': 'Capitalize "and" for visual impact'
        },
        {
            'component': 'script',
            'priority': 'high',
            'suggestion': 'Add relatable opening context'
        }
    ]
}

# Polish the story
polish = polish_story_with_gpt(
    story_id="story_001",
    current_title="The House: and Hunts",
    current_script="Every night at midnight...",
    expert_review_data=review_data
)

# Access results
print(f"Quality: {polish.original_quality_score} → {polish.expected_quality_score}")
print(f"Changes: {len(polish.change_log)}")
```

### Custom Configuration

```python
from T.Story.Polish import StoryPolisher, PolishConfig, PriorityLevel

config = PolishConfig(
    gpt_model="gpt-5",
    apply_priority_threshold=PriorityLevel.MEDIUM,
    max_iterations=3
)

polisher = StoryPolisher(config)
polish = polisher.polish_story(...)
```

## Input Components

### Primary Inputs
- **Current Title** (from local AI reviews)
- **Current Script** (from local AI reviews)
- **Expert Review Data** (from Stage 21: ExpertReview)
  - Improvement suggestions with priorities
  - Quality score
  - Decision (polish/publish)

### Context
- **Audience Context** (optional)
- **Original Idea** (optional, for context)
- **Iteration Number** (1, 2, etc.)

## Process

1. **Analyze Expert Feedback**: Extract and prioritize suggestions
2. **Apply Title Improvements**: Capitalization, word choice, SEO
3. **Apply Script Improvements**: Opening hook, relatability, pacing
4. **Validate Changes**: Ensure alignment with suggestions
5. **Generate Result**: Polished content + change log + quality delta

## Output

- **Polished Title**: Expertly improved title
- **Polished Script**: Expertly improved script
- **Change Log**: Detailed list of improvements
- **Quality Delta**: Expected quality increase
- **Ready for Re-Review**: Boolean flag

## Key Principles

1. **Surgical Improvements**: Small, high-impact changes
2. **Preserve Essence**: Don't change the core story
3. **Priority-Based**: Apply high-priority improvements first
4. **Iterative**: Support multiple polish iterations (max 2)
5. **Transparent**: Track all changes with rationale

## Testing

Run tests:
```bash
pytest T/Story/Polish/_meta/tests/test_polish.py -v
```

25 comprehensive tests covering:
- Data model creation and validation
- Priority filtering
- Title polishing
- Script polishing
- Complete polish flow
- Iteration tracking
- JSON serialization

## Examples

Run example:
```bash
python3 T/Story/Polish/_meta/examples/example_usage.py
```

## Integration

This module integrates with:
- **Stage 21 (ExpertReview)**: Receives feedback
- **Stage 23 (Publishing)**: Passes polished content

## Configuration Options

- **`gpt_model`**: GPT model to use (gpt-4, gpt-5)
- **`max_iterations`**: Maximum polish iterations (default: 2)
- **`apply_priority_threshold`**: Minimum priority (HIGH/MEDIUM/LOW)
- **`preserve_length`**: Maintain approximate length (default: True)
- **`preserve_essence`**: Maintain core story (default: True)
- **`target_quality_score`**: Target quality (default: 95)

## Success Metrics

- **Quality Improvement**: +3-5% typical
- **Iteration Count**: 1-2 iterations typical
- **Publishing Rate**: >95% after 1-2 cycles

## Navigation

**[← Back to Story](../README.md)** | **[→ ExpertReview](../ExpertReview/)** | **[→ ExpertPolish](../ExpertPolish/)**
