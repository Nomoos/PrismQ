# PrismQ.Idea.Model

Core data model for content ideas in the PrismQ content creation workflow.

## ✨ Highlights

- **Distillation Model** - Represents refined concepts fused from multiple IdeaInspiration sources
- **M:N Relationship** - Links multiple inspirations to create cohesive ideas
- **Workflow Integration** - Second stage in content pipeline: IdeaInspiration → **Idea** → Script
- **Platform Targeting** - Built-in support for different content platforms (YouTube, TikTok, Podcast, etc.)
- **Versioning** - Track idea evolution through iterations
- **Potential Scoring** - Evaluate cross-platform, regional, and demographic potential
- **Zero Dependencies** - Pure Python implementation
- **Type-Safe** - Full type hints support

## 🚀 Quick Start

```bash
# Install in development mode
cd Idea/Model
pip install -e .

# Basic usage
python -c "from idea import Idea, TargetPlatform, ContentGenre; print('OK')"
```

## 📋 Basic Usage

### Creating a Basic Idea

```python
from idea import Idea, TargetPlatform, ContentGenre, IdeaStatus

# Create a new idea
idea = Idea(
    title="The Digital Phantom Mystery",
    concept="An investigation into unsolved internet mysteries",
    purpose="Engage true crime audience with unique digital angle",
    emotional_quality="mysterious, suspenseful, intriguing",
    target_audience="True crime enthusiasts aged 18-35",
    target_demographics={
        "age_range": "18-35",
        "interests": "true_crime,technology",
        "regions": "US,UK,CA"
    },
    target_platform=TargetPlatform.YOUTUBE,
    genre=ContentGenre.TRUE_CRIME,
    style="narrative investigation",
)

print(idea)
# Output: Idea(title='The Digital Phantom Mystery...', version=1, status=draft, inspirations=0 sources)
```

### Creating from IdeaInspiration Sources

```python
from idea import Idea, TargetPlatform, ContentGenre

# Assume we have IdeaInspiration instances
inspirations = [inspiration1, inspiration2, inspiration3]

# Fuse/distill into a single Idea
idea = Idea.from_inspirations(
    inspirations=inspirations,
    title="Mystery of the Lost Internet Archive",
    concept="Exploring digital content that disappeared from the internet",
    purpose="Investigate fascinating cases of lost digital history",
    emotional_quality="nostalgic, mysterious, investigative",
    target_audience="Tech-savvy millennials and Gen Z",
    target_platform=TargetPlatform.YOUTUBE,
    genre=ContentGenre.DOCUMENTARY,
    created_by="AI-Agent-001"
)

print(f"Created from {len(idea.inspiration_ids)} inspirations")
```

### Working with Versions

```python
# Create a new version with updates
updated_idea = idea.create_new_version(
    concept="Enhanced: Exploring lost digital treasures and their stories",
    emotional_quality="nostalgic, mysterious, investigative, thought-provoking",
    status=IdeaStatus.VALIDATED
)

print(f"Version: {updated_idea.version}")  # Version: 2
print(f"Status: {updated_idea.status}")    # Status: validated
```

### Serialization

```python
# Convert to dictionary
idea_dict = idea.to_dict()

# Create from dictionary
restored_idea = Idea.from_dict(idea_dict)
```

## 🔗 Relationship with IdeaInspiration

The Idea model maintains a many-to-many (M:N) relationship with IdeaInspiration:

- **Multiple Inspirations → One Idea**: Blend several inspirations into a cohesive concept
- **One Inspiration → Multiple Ideas**: A single inspiration can seed different ideas
- **Traceability**: `inspiration_ids` field tracks source inspirations

```python
# Example: Fusion of multiple sources
idea = Idea.from_inspirations(
    inspirations=[true_crime_insp, tech_insp, mystery_insp],
    title="Digital Detective: Cold Cases of the Internet",
    concept="Using technology to solve internet's unsolved mysteries",
    # ... other fields
)

# Tracks all source inspirations
print(idea.inspiration_ids)
# Output: ['insp-123', 'insp-456', 'insp-789']
```

## 📊 Potential Scoring

Ideas can include potential scores for different contexts:

```python
idea.potential_scores = {
    "platform:youtube": 85,
    "platform:tiktok": 72,
    "platform:podcast": 90,
    "region:us": 88,
    "region:uk": 82,
    "age:18-24": 75,
    "age:25-34": 92,
    "language:english": 95,
}
```

## 🎯 Target Platforms

Supported platforms:
- `TargetPlatform.YOUTUBE` - Long-form video content
- `TargetPlatform.TIKTOK` - Short-form video content
- `TargetPlatform.PODCAST` - Audio content
- `TargetPlatform.BLOG` - Written content
- `TargetPlatform.SOCIAL_MEDIA` - Social posts
- `TargetPlatform.MULTIPLE` - Multi-platform content

## 📚 Content Genres

Available genres:
- `ContentGenre.TRUE_CRIME`
- `ContentGenre.MYSTERY`
- `ContentGenre.HORROR`
- `ContentGenre.SCIENCE_FICTION`
- `ContentGenre.DOCUMENTARY`
- `ContentGenre.EDUCATIONAL`
- `ContentGenre.ENTERTAINMENT`
- `ContentGenre.LIFESTYLE`
- `ContentGenre.TECHNOLOGY`
- `ContentGenre.OTHER`

## 🔄 Workflow Status

Idea lifecycle states:
- `IdeaStatus.DRAFT` - Initial concept
- `IdeaStatus.VALIDATED` - Reviewed and validated
- `IdeaStatus.APPROVED` - Approved for production
- `IdeaStatus.IN_PRODUCTION` - Being developed into content
- `IdeaStatus.ARCHIVED` - No longer active

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

## 📚 Documentation

- **[User Guide](./_meta/docs/USER_GUIDE.md)** - Detailed usage examples
- **[Setup Guide](./_meta/docs/SETUP.md)** - Installation and configuration
- **[Contributing](./_meta/docs/CONTRIBUTING.md)** - Development guidelines

## 🔗 Related

- [Parent Directory](../) - PrismQ.Idea overview
- [IdeaInspiration Model](../../IdeaInspiration/Model/) - Source inspiration model

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
