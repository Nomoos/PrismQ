# Creation Module Examples

Example usage of the Idea Creation module.

## Basic Creation from Title

```python
from T.Idea.Creation.src import IdeaCreator
from T.Idea.Model.src import ContentGenre

# Create a single idea from a title
creator = IdeaCreator()
ideas = creator.create_from_title("The Future of Artificial Intelligence")

idea = ideas[0]
print(f"Title: {idea.title}")
print(f"Concept: {idea.concept}")
print(f"Premise: {idea.premise}")
print(f"Keywords: {idea.keywords}")
print(f"Themes: {idea.themes}")
```

## Multiple Ideas from Title

```python
from T.Idea.Creation.src import IdeaCreator

# Create multiple idea variations from a single title
creator = IdeaCreator()
ideas = creator.create_from_title(
    "Digital Privacy in Modern Society",
    num_ideas=3
)

for i, idea in enumerate(ideas):
    print(f"\nVariation {i+1}:")
    print(f"  Title: {idea.title}")
    print(f"  Concept: {idea.concept[:60]}...")
    print(f"  Hook: {idea.hook}")
```

## Creation with Target Platforms

```python
from T.Idea.Creation.src import IdeaCreator
from T.Idea.Model.src import ContentGenre

# Create ideas for specific platforms
creator = IdeaCreator()
ideas = creator.create_from_title(
    "Quick Cooking Tips",
    num_ideas=2,
    target_platforms=["youtube", "tiktok", "instagram"],
    target_formats=["video"],
    genre=ContentGenre.LIFESTYLE,
    length_target="60 seconds"
)

for idea in ideas:
    print(f"Platforms: {idea.target_platforms}")
    print(f"Length target: {idea.length_target}")
```

## Creation from Description

```python
from T.Idea.Creation.src import IdeaCreator
from T.Idea.Model.src import ContentGenre

# Create ideas from a description
creator = IdeaCreator()
description = """
A detective story set in virtual reality where the protagonist must solve 
mysteries by navigating between the real world and digital spaces. The line 
between reality and simulation becomes increasingly blurred.
"""

ideas = creator.create_from_description(
    description,
    num_ideas=2,
    genre=ContentGenre.SCIENCE_FICTION,
    target_platforms=["youtube", "medium"],
    target_formats=["video", "text"]
)

for i, idea in enumerate(ideas):
    print(f"\nIdea {i+1}:")
    print(f"  Title: {idea.title}")
    print(f"  Logline: {idea.logline}")
    print(f"  Synopsis: {idea.synopsis[:100]}...")
```

## Variable Length Configuration

```python
from T.Idea.Creation.src import IdeaCreator, CreationConfig

# Configure variable lengths for content
config = CreationConfig(
    min_title_length=30,
    max_title_length=100,
    min_story_length=200,
    max_story_length=2000,
    variation_degree="high"
)

creator = IdeaCreator(config)
ideas = creator.create_from_title(
    "Climate Change Solutions",
    num_ideas=5
)

for idea in ideas:
    print(f"Title length: {len(idea.title)}")
    print(f"Synopsis length: {len(idea.synopsis)}")
```

## Educational Content Creation

```python
from T.Idea.Creation.src import IdeaCreator
from T.Idea.Model.src import ContentGenre

# Create educational content ideas
creator = IdeaCreator()
ideas = creator.create_from_title(
    "Introduction to Quantum Computing",
    num_ideas=3,
    genre=ContentGenre.EDUCATIONAL,
    target_platforms=["youtube", "medium", "linkedin"],
    target_formats=["video", "text"],
    length_target="10-15 minutes / 2000-3000 words"
)

for idea in ideas:
    print(f"\nTitle: {idea.title}")
    print(f"Skeleton:\n{idea.skeleton}")
    print(f"Outline:\n{idea.outline[:200]}...")
```

## Horror Story Creation

```python
from T.Idea.Creation.src import IdeaCreator
from T.Idea.Model.src import ContentGenre

# Create horror story ideas
creator = IdeaCreator()
description = "A family moves into an old house where mirrors show alternate versions of reality"

ideas = creator.create_from_description(
    description,
    num_ideas=3,
    genre=ContentGenre.HORROR,
    target_platforms=["youtube", "tiktok"],
    target_formats=["video", "audio"],
    length_target="5-10 minutes"
)

for i, idea in enumerate(ideas):
    print(f"\nStory {i+1}:")
    print(f"  Title: {idea.title}")
    print(f"  Hook: {idea.hook}")
    print(f"  Premise: {idea.premise}")
    print(f"  Keywords: {', '.join(idea.keywords[:5])}")
```

## Minimal vs Complete Field Generation

```python
from T.Idea.Creation.src import IdeaCreator, CreationConfig

# Minimal fields configuration
minimal_config = CreationConfig(include_all_fields=False)
minimal_creator = IdeaCreator(minimal_config)

# Complete fields configuration
complete_config = CreationConfig(include_all_fields=True)
complete_creator = IdeaCreator(complete_config)

title = "The Last Message"

# Minimal generation
minimal_ideas = minimal_creator.create_from_title(title, num_ideas=1)
print("Minimal fields:")
print(f"  Has synopsis: {bool(minimal_ideas[0].synopsis)}")
print(f"  Has keywords: {bool(minimal_ideas[0].keywords)}")
print(f"  Has premise: {bool(minimal_ideas[0].premise)}")

# Complete generation
complete_ideas = complete_creator.create_from_title(title, num_ideas=1)
print("\nComplete fields:")
print(f"  Has synopsis: {bool(complete_ideas[0].synopsis)}")
print(f"  Has keywords: {bool(complete_ideas[0].keywords)}")
print(f"  Has premise: {bool(complete_ideas[0].premise)}")
print(f"  Has logline: {bool(complete_ideas[0].logline)}")
print(f"  Has hook: {bool(complete_ideas[0].hook)}")
print(f"  Has skeleton: {bool(complete_ideas[0].skeleton)}")
print(f"  Has outline: {bool(complete_ideas[0].outline)}")
```

## Multi-Format Content Creation

```python
from T.Idea.Creation.src import IdeaCreator
from T.Idea.Model.src import ContentGenre

# Create ideas optimized for multiple formats
creator = IdeaCreator()
ideas = creator.create_from_title(
    "Understanding Blockchain Technology",
    num_ideas=1,
    genre=ContentGenre.TECHNOLOGY,
    target_platforms=["youtube", "medium", "spotify", "linkedin"],
    target_formats=["text", "audio", "video"],
    length_target="Text: 2000 words, Audio: 15 min, Video: 12 min"
)

idea = ideas[0]
print(f"Title: {idea.title}")
print(f"Platforms: {', '.join(idea.target_platforms)}")
print(f"Formats: {', '.join(idea.target_formats)}")
print(f"Length target: {idea.length_target}")
print(f"\nSynopsis: {idea.synopsis}")
```

## Batch Creation for Content Series

```python
from T.Idea.Creation.src import IdeaCreator, CreationConfig
from T.Idea.Model.src import ContentGenre

# Create a series of related ideas
config = CreationConfig(variation_degree="medium")
creator = IdeaCreator(config)

topics = [
    "Machine Learning Fundamentals",
    "Neural Networks Explained",
    "Deep Learning Applications",
    "AI Ethics and Responsibility"
]

series_ideas = []
for topic in topics:
    ideas = creator.create_from_title(
        topic,
        num_ideas=1,
        genre=ContentGenre.EDUCATIONAL,
        target_platforms=["youtube"],
        target_formats=["video"],
        length_target="15-20 minutes"
    )
    series_ideas.extend(ideas)

print(f"Created {len(series_ideas)} ideas for series:")
for i, idea in enumerate(series_ideas):
    print(f"{i+1}. {idea.title}")
```
