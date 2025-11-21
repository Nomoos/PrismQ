# T/Idea/Fusion - Idea Fusion Module

**Namespace**: `PrismQ.T.Idea.Fusion`

The Fusion module combines multiple Ideas or IdeaInspiration sources into new, cohesive Ideas using AI-powered combination logic. It processes batches of source ideas and generates fused concepts that synthesize the best elements from multiple sources.

## Purpose

Transform multiple Ideas or IdeaInspiration instances into unified, coherent Ideas that combine signals, keywords, stories, titles, and descriptions from the best source concepts.

## Key Features

- **Batch Processing**: Process multiple source ideas simultaneously
- **AI-Powered Fusion**: Intelligent combination logic for synthesizing ideas
- **Signal Aggregation**: Combine keywords, themes, and signals from multiple sources
- **Story Synthesis**: Merge narrative elements into cohesive stories
- **Quality Scoring**: Select best elements based on potential scores

## Workflow Position

```
IdeaInspiration (multiple) → Fusion → New Idea(s)
Idea (multiple) → Fusion → New Idea(s)
```

## Usage Example

```python
from PrismQ.T.Idea.Fusion import IdeaFusion
from PrismQ.T.Idea.Model import Idea

# Fuse multiple ideas into one
fusion = IdeaFusion()
sources = [idea1, idea2, idea3]
fused_idea = fusion.fuse_ideas(
    sources=sources,
    strategy="best_elements",  # or "weighted_merge", "theme_based"
    title_generation="ai"  # Generate new title from fusion
)

# Batch fusion - create multiple fused ideas from a pool
fused_ideas = fusion.batch_fuse(
    source_pool=[idea1, idea2, idea3, idea4, idea5],
    num_outputs=2,
    fusion_size=3  # Each output combines 3 sources
)
```

## Module Metadata

### Documentation
Technical documentation and implementation guides.

**[→ View Fusion/_meta/docs/](./_meta/docs/)**

### Examples
Usage examples and sample implementations.

**[→ View Fusion/_meta/examples/](./_meta/examples/)**

### Tests
Test suites and test data.

**[→ View Fusion/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Idea](../README.md)** | **[→ Model Module](../Model/)** | **[→ Creation Module](../Creation/)**

---

*Part of the PrismQ.T.Idea content development workflow*
