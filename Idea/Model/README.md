# PrismQ.Idea.Model

Core data model for content ideas in the PrismQ content creation workflow.

## ✨ Highlights

- **Standalone or Derived** - Can be created independently or fused from multiple IdeaInspiration sources
- **M:N Relationship** - Links multiple inspirations to create cohesive ideas (optional)
- **Workflow Integration** - Second stage in content pipeline: IdeaInspiration → **Idea** → Script
- **AI-Ready** - Rich fields optimized for AI story generation (synopsis, story_premise, character_notes, etc.)
- **Platform Targeting** - Built-in support for different content platforms (YouTube, TikTok, Podcast, etc.)
- **Structured Content** - Keywords, outline, skeleton, themes for comprehensive content planning
- **Story Depth** - Character notes, setting details, tone guidance for complex narratives
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
python -c "from idea import Idea, ContentGenre; print('OK')"
```

## 📋 Basic Usage

### Creating a Basic Idea

```python
from idea import Idea, ContentGenre, IdeaStatus

# Create a new idea with structure
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
    target_platform="youtube",
    genre=ContentGenre.TRUE_CRIME,
    style="narrative investigation",
    keywords=["mystery", "unsolved", "internet", "investigation"],
    outline="1. Hook\n2. Case Introduction\n3. Investigation\n4. Theory\n5. Conclusion",
    skeleton="Mystery → Evidence → Analysis → Resolution"
)

print(idea)
# Output: Idea(title='The Digital Phantom Mystery...', version=1, status=draft, inspirations=0 sources)
```

### Creating Ideas Without IdeaInspiration

Ideas can be created independently without any source inspirations:

```python
from idea import Idea, ContentGenre

# Create idea manually (no IdeaInspiration sources needed)
manual_idea = Idea(
    title="Python Tutorial Series",
    concept="Teaching Python fundamentals through projects",
    purpose="Help beginners learn programming",
    target_platform="youtube",
    genre=ContentGenre.EDUCATIONAL,
    keywords=["python", "programming", "tutorial", "beginner"],
    outline="1. Setup\n2. Variables\n3. Functions\n4. Projects",
    skeleton="Intro → Theory → Practice → Challenge",
    inspiration_ids=[]  # No source inspirations
)

print(f"Has inspirations: {len(manual_idea.inspiration_ids) > 0}")
# Output: Has inspirations: False
```

### Creating from IdeaInspiration Sources

When you have multiple IdeaInspiration sources, you can fuse them:

```python
from idea import Idea, ContentGenre

# Assume we have IdeaInspiration instances
inspirations = [inspiration1, inspiration2, inspiration3]

# Fuse/distill into a single Idea
# Keywords are automatically aggregated from inspirations
idea = Idea.from_inspirations(
    inspirations=inspirations,
    title="Mystery of the Lost Internet Archive",
    concept="Exploring digital content that disappeared from the internet",
    purpose="Investigate fascinating cases of lost digital history",
    emotional_quality="nostalgic, mysterious, investigative",
    target_audience="Tech-savvy millennials and Gen Z",
    target_platform="youtube",
    genre=ContentGenre.DOCUMENTARY,
    outline="Custom outline for this specific idea",
    created_by="AI-Agent-001"
)

print(f"Created from {len(idea.inspiration_ids)} inspirations")
print(f"Aggregated keywords: {idea.keywords}")  # From inspirations
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

## 🤖 AI-Ready Fields for Story Generation

The model includes rich fields specifically designed to help AI generate complex, comprehensive stories:

### Synopsis & Story Premise

```python
idea = Idea(
    title="The Last Archive",
    concept="A librarian discovers humanity's lost memories in a digital vault",
    synopsis="""
        In a world where memories can be digitized and stored, a young librarian 
        named Ada discovers a hidden section of the Global Archive containing 
        memories that were supposed to be deleted. As she explores these forbidden 
        recollections, she uncovers a conspiracy that challenges everything she 
        knows about her society.
    """,
    story_premise="""
        Set in 2147, memories are currency and identity. The Global Archive stores 
        everyone's experiences, but some memories are deemed too dangerous. When Ada 
        finds the deletion vault, she must decide whether to expose the truth or 
        protect the carefully constructed peace of her world.
    """
)
```

### Character & Setting Details

```python
idea.character_notes = """
    Ada: 28, introverted librarian, photographic memory, haunted by deleted childhood
    Marcus: Archive security chief, Ada's mentor, hiding dark past
    Collective Voice: AI consciousness representing the Archive's will
"""

idea.setting_notes = """
    Primary: The Global Archive - vast digital library with physical manifestation
    Secondary: Memory Districts - neighborhoods organized by emotional themes
    Atmosphere: Clean futuristic aesthetic hiding dystopian control
"""
```

### Themes & Tone

```python
idea.themes = [
    "identity and memory",
    "truth vs. comfort",
    "digital consciousness",
    "rebellion against authority"
]

idea.tone_guidance = """
    Act 1: Wonder and discovery (mysterious, hopeful)
    Act 2: Growing unease (suspenseful, philosophical)
    Act 3: Confrontation (intense, thought-provoking)
    Overall: Balance sci-fi concepts with human emotion
"""

idea.length_target = "Feature film, 110-120 minutes, or 8-episode limited series"
```

These fields provide AI with comprehensive context for generating detailed, coherent narratives.

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

The `target_platform` field is a string that can contain any platform name, such as:
- `"youtube"` - Long-form video content
- `"tiktok"` - Short-form video content
- `"podcast"` - Audio content
- `"blog"` - Written content
- `"social_media"` - Social posts
- `"multiple"` - Multi-platform content
- Or any custom platform name you need

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
