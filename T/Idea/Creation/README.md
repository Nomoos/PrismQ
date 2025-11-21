# T/Idea/Creation - Idea Creation Module

**Namespace**: `PrismQ.T.Idea.Creation`

The Creation module generates multiple Ideas from simple inputs like titles or descriptions. It uses AI-powered generation to create rich, detailed Ideas with variable-length titles and stories optimized for different platforms and formats.

## Purpose

Transform minimal input (title or description) into multiple, fully-formed Ideas with comprehensive narrative structure, targeting information, and content specifications.

## Key Features

- **Batch Generation**: Create multiple Ideas from single input
- **Variable Length**: Generate titles and stories with flexible length
- **AI-Powered**: Intelligent content generation with rich context
- **Multi-Format Ready**: Ideas optimized for text, audio, and video
- **Platform Targeting**: Automatic platform-specific optimization

## Workflow Position

```
Title/Description → Creation → Multiple Ideas
Simple Input → Creation → Detailed Ideas
```

## Usage Example

```python
from PrismQ.T.Idea.Creation import IdeaCreator, CreationConfig

# Create multiple ideas from a title
creator = IdeaCreator()
ideas = creator.create_from_title(
    title="The Future of AI",
    num_ideas=3,
    target_platforms=["youtube", "medium"],
    target_formats=["text", "video"]
)

# Create ideas from a description
ideas = creator.create_from_description(
    description="A story about time travel paradoxes",
    num_ideas=2,
    genre=ContentGenre.SCIENCE_FICTION,
    length_target="10-15 minutes"
)

# Create with custom configuration
config = CreationConfig(
    min_title_length=30,
    max_title_length=100,
    min_story_length=500,
    max_story_length=2000
)
creator = IdeaCreator(config)
ideas = creator.create_from_title("Digital Privacy", num_ideas=5)
```

## Module Metadata

### Documentation
Technical documentation and implementation guides.

**[→ View Creation/_meta/docs/](./_meta/docs/)**

### Examples
Usage examples and sample implementations.

**[→ View Creation/_meta/examples/](./_meta/examples/)**

### Tests
Test suites and test data.

**[→ View Creation/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Idea](../README.md)** | **[→ Model Module](../Model/)** | **[→ Fusion Module](../Fusion/)**

---

*Part of the PrismQ.T.Idea content development workflow*
