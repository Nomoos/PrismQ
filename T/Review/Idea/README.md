# T/Review/Idea - Idea Review Module

**Namespace**: `PrismQ.T.Review.Idea`

Worker10's comprehensive idea review system for analyzing ideas generated from Idea.Creation.

## Purpose

This module provides quality assurance capabilities for analyzing multiple idea variants
generated from a single text input, producing comprehensive reviews containing:

- **Gaps**: Missing or weak content areas in each variant
- **Pros**: Strengths and positive aspects of each variant  
- **Cons**: Weaknesses and areas for improvement
- **Differences across variants**: How variants differ in approach and content
- **Similarity/compatibility with original text**: How well variants align with the input

## Quick Start

### Using the CLI

```bash
# Generate review from a keyword
python T/Review/Idea/idea_review_cli.py "skirts 2000"

# Generate review from longer text
python T/Review/Idea/idea_review_cli.py "když jsem se probudil sobotního rána po tahu"

# Generate with custom count and output to file
python T/Review/Idea/idea_review_cli.py "AI in medicine" --count 5 --output review.md

# Use reproducible seed
python T/Review/Idea/idea_review_cli.py "test input" --seed 42

# Output as JSON
python T/Review/Idea/idea_review_cli.py "mystery story" --json
```

### Using in Python Code

```python
from T.Review.Idea import generate_idea_review, IdeaReviewGenerator

# Simple usage with convenience function
review = generate_idea_review("skirts 2000", num_ideas=10, seed=42)
print(review.format_as_markdown())

# Advanced usage with generator
generator = IdeaReviewGenerator(num_ideas=5)
review = generator.generate_review("když jsem se probudil sobotního rána po tahu")

# Access review data
print(f"Input: {review.original_input}")
print(f"Input Type: {review.input_type}")
print(f"Average Similarity: {review.average_similarity_score}%")

# Analyze individual variants
for analysis in review.variant_analyses:
    print(f"\n{analysis.variant_name}:")
    print(f"  Type: {analysis.variant_type}")
    print(f"  Similarity: {analysis.similarity_score}%")
    print(f"  Pros: {analysis.pros}")
    print(f"  Cons: {analysis.cons}")
    print(f"  Gaps: {analysis.gaps}")

# Get overall insights
print(f"\nOverall Strengths: {review.overall_strengths}")
print(f"Overall Gaps: {review.overall_gaps}")
print(f"Differences: {review.cross_variant_differences}")
print(f"Recommendations: {review.recommendations}")
```

## Module Structure

```
T/Review/Idea/
├── __init__.py           # Module exports
├── idea_review.py        # Core review generator
├── idea_review_cli.py    # Command-line interface
├── README.md             # This file
└── _meta/
    └── tests/
        └── test_idea_review.py  # Unit tests
```

## Key Classes

### IdeaReviewGenerator

Main class for generating comprehensive reviews.

```python
class IdeaReviewGenerator:
    def __init__(self, num_ideas: int = 10):
        """Initialize generator with number of ideas to generate."""
    
    def generate_review(
        self,
        text_input: str,
        seed: Optional[int] = None,
        allow_duplicate_types: bool = True
    ) -> IdeaReviewResult:
        """Generate complete review from text input."""
```

### IdeaReviewResult

Contains the complete review data.

**Attributes:**
- `original_input`: The original text input
- `input_type`: Classification (keyword, phrase, longer text)
- `total_variants`: Number of variants generated
- `variant_analyses`: List of individual variant analyses
- `cross_variant_differences`: Key differences between variants
- `overall_gaps`: Gaps common across variants
- `overall_strengths`: Strengths common across variants
- `compatibility_summary`: Summary of alignment with input
- `recommendations`: Suggestions for improvement
- `average_similarity_score`: Mean similarity score (0-100)

**Methods:**
- `to_dict()`: Convert to dictionary
- `format_as_markdown()`: Format as markdown report

### IdeaVariantAnalysis

Analysis data for a single variant.

**Attributes:**
- `variant_index`: Position in the variant list
- `variant_type`: Template type used (e.g., "emotion_first")
- `variant_name`: Human-readable name
- `pros`: List of strengths
- `cons`: List of weaknesses
- `gaps`: List of missing elements
- `similarity_score`: Alignment with input (0-100)
- `key_themes`: Main themes identified
- `unique_elements`: Elements unique to this variant

## Input Types

The review generator classifies inputs into three types:

1. **Keyword** (≤30 chars, ≤3 words): Simple seed words
   - Example: "skirts 2000", "AI", "mystery"

2. **Phrase** (≤100 chars, ≤15 words): Short descriptions
   - Example: "A mysterious night adventure"
   - Example: "když jsem se probudil sobotního rána po tahu"

3. **Longer text** (>100 chars or >15 words): Detailed prompts
   - Used for complex scenarios or story seeds

## Review Components

### Pros Analysis

Identifies strengths such as:
- Clear hooks that capture attention
- Strong emotional appeal
- Well-defined target audience
- Visual hooks for engagement
- Clear climax/wow moments
- Built-in engagement mechanisms

### Cons Analysis

Identifies weaknesses such as:
- Missing clear hooks
- Potentially generic phrases
- Need for more context/setup
- Minimal structures needing expansion
- Risk of confusing audiences

### Gaps Analysis

Identifies missing elements such as:
- No expanded description provided
- No explicit engagement mechanism
- Platform targeting not specified
- Content safety guidelines not addressed
- Character growth arc not defined
- Resolution approach not specified

### Cross-Variant Differences

Analyzes:
- Template type distribution
- Similarity score variance
- Narrative approaches (emotion-driven, mystery, short-form)
- Audience targeting diversity

## Running Tests

```bash
# Run all idea review tests
pytest T/Review/Idea/_meta/tests/test_idea_review.py -v

# Run specific test class
pytest T/Review/Idea/_meta/tests/test_idea_review.py::TestIdeaReviewGenerator -v

# Run with coverage
pytest T/Review/Idea/_meta/tests/test_idea_review.py --cov=T/Review/Idea
```

## Integration with Workflow

This module integrates with the PrismQ workflow as follows:

1. **Input**: User provides text (keyword, phrase, or longer text)
2. **Generation**: Uses `T.Idea.Creation.create_ideas_from_input` for variant generation
3. **Analysis**: Each variant is analyzed for pros, cons, gaps
4. **Comparison**: Cross-variant differences are identified
5. **Report**: Complete review with recommendations is generated

## Example Output

```markdown
# Idea Review Report

**Original Input**: `skirts 2000`
**Input Type**: keyword
**Total Variants**: 10
**Average Similarity Score**: 82.0%

## Executive Summary

The input 'skirts 2000' was treated as a keyword seed. Variants show excellent 
alignment with the original input (avg 82% similarity).

## Overall Analysis

### Overall Strengths
- ✅ Well-defined target audience

### Overall Gaps
- ⚠️ No expanded description provided
- ⚠️ No explicit engagement mechanism defined

## Differences Across Variants

- Template distribution: 9 unique types
- Multiple narrative approaches present: emotion-driven, mystery/puzzle

## Recommendations

- 💡 Add engagement hooks before production
- 💡 Review variants for content safety
- 💡 Test top variants with target audience
```

## Worker10 Role

This module implements Worker10's "Review Master & Quality Assurance Lead" responsibilities:

- Code review and quality validation
- Acceptance criteria verification
- Quality gate enforcement
- Constructive feedback delivery

The review report follows Worker10's feedback format:
- Specific, actionable comments
- Positive acknowledgment of strengths
- Clear improvement suggestions
- Priority-based recommendations

---

**Owner**: Worker10  
**Created**: 2025-11-30  
**Status**: ✅ Complete
