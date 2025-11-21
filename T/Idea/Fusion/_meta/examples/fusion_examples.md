# Fusion Module Examples

Example usage of the Idea Fusion module.

## Basic Fusion

```python
from T.Idea.Fusion.src import IdeaFusion
from T.Idea.Model.src import Idea, ContentGenre

# Create source ideas
idea1 = Idea(
    title="AI in Healthcare",
    concept="Using artificial intelligence to improve patient care",
    keywords=["ai", "healthcare", "medicine"],
    themes=["technology", "innovation"],
    genre=ContentGenre.TECHNOLOGY
)

idea2 = Idea(
    title="Medical Diagnostics",
    concept="Advanced diagnostic techniques using machine learning",
    keywords=["diagnostics", "machine learning", "healthcare"],
    themes=["technology", "healthcare"],
    genre=ContentGenre.TECHNOLOGY
)

# Fuse ideas
fusion = IdeaFusion()
fused_idea = fusion.fuse_ideas([idea1, idea2])

print(f"Fused Title: {fused_idea.title}")
print(f"Fused Concept: {fused_idea.concept}")
print(f"Keywords: {fused_idea.keywords}")
print(f"Themes: {fused_idea.themes}")
```

## Batch Fusion

```python
from T.Idea.Fusion.src import IdeaFusion, FusionConfig
from T.Idea.Model.src import Idea, ContentGenre

# Create a pool of ideas
ideas = [
    Idea(title="AI Ethics", concept="Ethical considerations in AI development", 
         genre=ContentGenre.EDUCATIONAL),
    Idea(title="Machine Learning Basics", concept="Introduction to ML algorithms",
         genre=ContentGenre.EDUCATIONAL),
    Idea(title="Neural Networks", concept="Deep learning and neural networks",
         genre=ContentGenre.EDUCATIONAL),
    Idea(title="AI Applications", concept="Real-world AI use cases",
         genre=ContentGenre.TECHNOLOGY),
    Idea(title="Data Science", concept="Data analysis and visualization",
         genre=ContentGenre.TECHNOLOGY),
    Idea(title="Automation", concept="AI-powered automation",
         genre=ContentGenre.TECHNOLOGY),
]

# Batch fuse - create 2 fused ideas from pool of 6
fusion = IdeaFusion()
fused_ideas = fusion.batch_fuse(
    source_pool=ideas,
    num_outputs=2,
    fusion_size=3  # Each output combines 3 sources
)

for i, idea in enumerate(fused_ideas):
    print(f"\nFused Idea {i+1}:")
    print(f"  Title: {idea.title}")
    print(f"  Keywords: {idea.keywords[:5]}")  # First 5 keywords
```

## Custom Fusion Strategy

```python
from T.Idea.Fusion.src import IdeaFusion
from T.Idea.Model.src import Idea

# Create ideas with potential scores
idea1 = Idea(
    title="Low Priority",
    concept="Less important concept",
    potential_scores={"platform_youtube": 30, "region_us": 40}
)

idea2 = Idea(
    title="High Priority",
    concept="Very important concept with detailed information",
    premise="This is a much more detailed and valuable premise",
    potential_scores={"platform_youtube": 90, "region_us": 85}
)

# Use weighted_merge strategy - prioritizes high-scoring ideas
fusion = IdeaFusion()
fused = fusion.fuse_ideas([idea1, idea2], strategy="weighted_merge")

# The fused idea should prefer content from higher-scoring ideas
print(f"Premise length: {len(fused.premise)}")  # Should be longer
print(f"Average score: {sum(fused.potential_scores.values()) / len(fused.potential_scores)}")
```

## Theme-Based Fusion

```python
from T.Idea.Fusion.src import IdeaFusion
from T.Idea.Model.src import Idea

# Create ideas with overlapping themes
idea1 = Idea(
    title="Climate Action",
    concept="Taking action against climate change",
    themes=["environment", "sustainability", "activism"]
)

idea2 = Idea(
    title="Green Technology",
    concept="Sustainable technology solutions",
    themes=["technology", "sustainability", "innovation"]
)

idea3 = Idea(
    title="Renewable Energy",
    concept="Clean energy for the future",
    themes=["energy", "sustainability", "environment"]
)

# Fuse with theme_based strategy - emphasizes common themes
fusion = IdeaFusion()
fused = fusion.fuse_ideas([idea1, idea2, idea3], strategy="theme_based")

print(f"Common theme: sustainability")
print(f"Fused themes: {fused.themes}")
# Should prioritize "sustainability" (common to all)
```

## Custom Configuration

```python
from T.Idea.Fusion.src import IdeaFusion, FusionConfig
from T.Idea.Model.src import Idea

# Create custom configuration
config = FusionConfig(
    strategy="keyword_cluster",
    title_generation="ai",
    preserve_sources=True,
    max_sources=5
)

# Create fusion with config
fusion = IdeaFusion(config)

ideas = [
    Idea(title=f"Idea {i}", concept=f"Concept {i}", 
         keywords=[f"kw{i}", "common"])
    for i in range(10)
]

# Will only use first 5 sources (max_sources=5)
fused = fusion.fuse_ideas(ideas)

print(f"Number of source IDs: {len(fused.inspiration_ids)}")
print(f"Keywords (by frequency): {fused.keywords[:5]}")
```

## Explicit Title and Concept

```python
from T.Idea.Fusion.src import IdeaFusion
from T.Idea.Model.src import Idea

idea1 = Idea(title="Part 1", concept="First part")
idea2 = Idea(title="Part 2", concept="Second part")

# Provide explicit title and concept for fused idea
fusion = IdeaFusion()
fused = fusion.fuse_ideas(
    [idea1, idea2],
    title="Complete Story",
    concept="A comprehensive narrative combining both parts"
)

print(f"Title: {fused.title}")
print(f"Concept: {fused.concept}")
```
