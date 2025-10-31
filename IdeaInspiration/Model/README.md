# PrismQ.IdeaInspiration.Model

**Core data model and database setup for content ideas across the PrismQ ecosystem**

## Overview

This repository provides:
1. The `IdeaInspiration` data model used across PrismQ modules
2. Database setup script to create and configure the SQLite database in your working directory

The model is used by:
- **[PrismQ.IdeaInspiration.Scoring](https://github.com/Nomoos/PrismQ.IdeaInspiration.Scoring)** - Content scoring engine
- **[PrismQ.IdeaInspiration.Classification](https://github.com/Nomoos/PrismQ.IdeaInspiration.Classification)** - Content classification
- **PrismQ.IdeaInspiration.Builder** - Model construction from various sources
- **PrismQ.IdeaInspiration.Sources** - Content source integrations
- **PrismQ.Idea.Model** - Content generation model

The model provides a unified structure for representing content ideas from various sources (text, video, audio) with factory methods for easy creation from different content types.

**Note:** `PrismQ.Idea.Model` maintains an M:N (many-to-many) relationship with this model, as multiple `IdeaInspiration` instances can be blended together to create new `Idea` objects for scripts, content generation, and other creative purposes. See the [Blending Multiple IdeaInspiration Objects](#blending-multiple-ideainspiration-objects) section for examples and strategies.

## Features

- 🎯 **Unified Data Model** - Single structure for text, video, and audio content
- 🏭 **Factory Methods** - Easy creation from different sources (text, YouTube, Reddit, etc.)
- 🔀 **Blending Support** - Combine multiple inspirations by topic, trend, or platform
- 📦 **Serialization** - Convert to/from dictionaries for storage and transmission
- 💾 **Database Setup** - Automated script to create and configure SQLite database
- 🔌 **Zero Dependencies** - Pure Python with no external requirements
- 🧪 **Well Tested** - Comprehensive test coverage
- 📝 **Type Hints** - Full type annotation support

## Quick Setup

### Database Setup

#### Windows (Primary Platform)

Run the setup script to create the database in your working directory:

**PowerShell (Recommended):**
```powershell
.\setup_db.ps1
```

**Batch (Legacy):**
```batch
setup_db.bat
```

This script will:
- Set up `.env` configuration in your working directory (creates one if missing)
- Remember your working directory for future use
- Store configuration values (Python executable, working directory) in `.env`
- Create `db.s3db` in your configured working directory
- Create the `IdeaInspiration` table with the complete data model
- Never ask for current directory - uses remembered working directory from `.env`

**Why PowerShell?** PowerShell scripts provide better error handling, colored output, and are more AI-friendly (GitHub Copilot/ChatGPT). If you get an execution policy error, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

#### Linux/macOS (CI/Testing)

For CI environments and testing on Linux/macOS:

```bash
./setup_db.sh
```

This script provides the same functionality optimized for non-interactive CI environments. It automatically detects non-interactive mode (pipes/redirects) and uses sensible defaults.

### Configuration Management

The package includes a configuration manager that:
- **Remembers your working directory** - Never asks for current directory again
- **Stores configuration in `.env`** - Creates and manages `.env` file in the nearest parent directory with "PrismQ" in its name
- **Shared configuration** - All PrismQ packages in the same directory tree share the same `.env` file
- **Automatic persistence** - Configuration values are saved and restored automatically
- **Interactive and non-interactive modes** - Works in both CI environments and manual usage

#### Database Fields

The database will include the following fields:
- Basic fields: title, description, content, keywords
- Source fields: source_type, source_id, source_url, source_created_by, source_created_at, metadata
- Scoring fields: score, category, subcategory_relevance, contextual_category_scores
- Database system fields: id (auto-increment), created_at, updated_at (timestamps)

## Installation

### From Source

```bash
git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.Model.git
cd PrismQ.IdeaInspiration.Model
pip install -e .
```

### For Development

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from idea_inspiration import IdeaInspiration, ContentType

# Create from text content
idea = IdeaInspiration.from_text(
    title="Introduction to Python",
    description="Learn Python basics",
    text_content="Python is a high-level programming language...",
    keywords=["python", "programming", "tutorial"]
)

# Create from video with subtitles
video_idea = IdeaInspiration.from_video(
    title="Python Tutorial",
    description="Video tutorial",
    subtitle_text="Welcome to this tutorial...",
    keywords=["python", "video", "tutorial"]
)

# Create from audio with transcription
audio_idea = IdeaInspiration.from_audio(
    title="Python Podcast",
    description="Episode 1",
    transcription="Today we discuss Python...",
    keywords=["python", "podcast"]
)
```

## Usage Examples

### Basic Creation

```python
from idea_inspiration import IdeaInspiration, ContentType

# Manual creation
idea = IdeaInspiration(
    title="My Article",
    description="Article description",
    content="Full article text",
    keywords=["article", "example"],
    source_type=ContentType.TEXT,
    metadata={"author": "John Doe", "publish_date": "2025-01-15"},
    source_id="article-123",
    source_url="https://example.com/article"
)
```

### Serialization

```python
from idea_inspiration import IdeaInspiration

# Create an idea
idea = IdeaInspiration.from_text(
    title="Test Article",
    text_content="Article content",
    keywords=["test"]
)

# Convert to dictionary
data = idea.to_dict()
print(data)
# {
#     'title': 'Test Article',
#     'description': '',
#     'content': 'Article content',
#     'keywords': ['test'],
#     'source_type': 'text',
#     'metadata': {},
#     'source_id': None,
#     'source_url': None
# }

# Create from dictionary
restored = IdeaInspiration.from_dict(data)
assert restored.title == idea.title
```

### Scoring and Category Fields

The model supports scoring and categorization fields for content evaluation:

```python
from idea_inspiration import IdeaInspiration

# Create with scoring and category information
idea = IdeaInspiration.from_text(
    title="True Crime Documentary",
    text_content="A gripping investigation into...",
    keywords=["true crime", "mystery", "thriller"],
    score=85,  # Overall score
    category="true_crime",  # Primary category
    subcategory_relevance={
        "true_crime": 92,             # Strong true crime relevance
        "psychological_thriller": 81,  # Strong psychological thriller elements
        "mystery": 88,                 # Strong mystery elements
        "horror": 75,                  # Moderate horror elements
        "drama": 69,                   # Some drama elements
        "romance": 34                  # Minimal romance elements
    },
    contextual_category_scores={
        "language:english": 145,   # 145% of base for English
        "language:spanish": 95,    # 95% of base for Spanish
        "language:german": 72,     # 72% of base for German
        "region:us": 160,          # 160% of base for US
        "region:latam": 110,       # 110% of base for Latin America
        "region:europe": 87,       # 87% of base for Europe
        "age:13-17": 125,          # 125% of base for ages 13-17
        "age:18-24": 142,          # 142% of base for ages 18-24
        "age:25-34": 98,           # 98% of base for ages 25-34
        "gender:female": 135,      # 135% of base for female
        "gender:male": 76          # 76% of base for male
    }
)

# Access scoring fields
print(f"Score: {idea.score}")
print(f"Category: {idea.category}")
print(f"True crime relevance: {idea.subcategory_relevance['true_crime']}")
print(f"English context score: {idea.contextual_category_scores['language:english']}%")
```

**Subcategory Relevance**: Relevance scores (0-100) for secondary categories/subcategories showing how strongly content aligns with each subcategory.

**Contextual Category Scores**: Contextual performance scores as percentages of base score for different contexts (language, region, age, gender). Used by the Builder for score calculation.

## Data Model

### IdeaInspiration

The core data model with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `title` | `str` | Content title or headline |
| `description` | `str` | Brief description or summary |
| `content` | `str` | Main text content (body, subtitles, or transcription) |
| `keywords` | `List[str]` | List of relevant keywords or tags |
| `source_type` | `ContentType` | Type of content source (TEXT/VIDEO/AUDIO/UNKNOWN) |
| `metadata` | `Dict[str, str]` | Additional source-specific metadata (string key-value pairs for SQLite compatibility) |
| `source_id` | `Optional[str]` | Unique identifier from source platform |
| `source_url` | `Optional[str]` | URL to original content |
| `source_created_by` | `Optional[str]` | Creator/author of the source content |
| `source_created_at` | `Optional[str]` | Creation timestamp of the source content (ISO 8601 format recommended) |
| `score` | `Optional[int]` | Numerical score value for content evaluation |
| `category` | `Optional[str]` | Primary category classification for the content |
| `subcategory_relevance` | `Dict[str, int]` | Relevance scores for subcategories (e.g., `{'true_crime': 92, 'mystery': 88, 'horror': 75}`) |
| `contextual_category_scores` | `Dict[str, int]` | Contextual performance scores as % of base (e.g., `{'language:english': 145, 'region:us': 160, 'age:18-24': 142}`) |

### ContentType

Enumeration for content source types:

- `ContentType.TEXT` - Text articles, blog posts, Reddit posts
- `ContentType.VIDEO` - Video content with subtitles/transcriptions
- `ContentType.AUDIO` - Audio content with transcriptions
- `ContentType.UNKNOWN` - Unknown or unspecified source type

## Metadata Examples

The `metadata` field uses `Dict[str, str]` (string key-value pairs) for SQLite/S3DB compatibility. Here are examples for different content types:

### Text Content Metadata

```python
idea = IdeaInspiration.from_text(
    title="Understanding Neural Networks",
    text_content="Neural networks are...",
    metadata={
        "author": "Dr. Sarah Johnson",
        "publish_date": "2025-01-15",
        "word_count": "2500",
        "reading_time_minutes": "12",
        "category": "machine-learning",
        "platform": "medium",
        "language": "en",
    }
)
```

### Video Content Metadata

```python
idea = IdeaInspiration.from_video(
    title="Python Deep Dive",
    subtitle_text="In this video...",
    metadata={
        "channel": "CodeMasters",
        "channel_id": "UC123456",
        "views": "150000",
        "likes": "8500",
        "duration_seconds": "2400",
        "upload_date": "2025-01-10",
        "resolution": "1080p",
        "language": "en",
    }
)
```

### Audio Content Metadata

```python
idea = IdeaInspiration.from_audio(
    title="Tech Talk Podcast #42",
    transcription="Welcome everyone...",
    metadata={
        "host": "Mike Developer",
        "guest": "Jane Engineer",
        "episode_number": "42",
        "season": "3",
        "duration_seconds": "4200",
        "release_date": "2025-01-12",
        "format": "mp3",
        "bitrate": "128kbps",
        "language": "en",
    }
)
```

### SQLite/S3DB Best Practices

- **All values as strings**: Store numeric values as strings, convert when needed
- **Date format**: Use ISO 8601 format (YYYY-MM-DD) for dates
- **Key naming**: Use snake_case for consistency
- **Easy serialization**: Data can be easily serialized to JSON for SQLite TEXT fields

## Factory Methods

### General Purpose

- `IdeaInspiration.from_text()` - Create from text content
- `IdeaInspiration.from_video()` - Create from video with subtitles
- `IdeaInspiration.from_audio()` - Create from audio with transcription

### Serialization

- `IdeaInspiration.to_dict()` - Convert to dictionary
- `IdeaInspiration.from_dict()` - Create from dictionary

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests
pytest

# Run with coverage
pytest --cov=prismq --cov-report=html

# Run specific test file
pytest tests/test_idea_inspiration.py -v
```

## Configuration Manager

The package includes a `ConfigManager` class for handling `.env` file configuration:

```python
from config_manager import ConfigManager, setup_working_directory

# Set up working directory configuration (prompts if needed)
config = setup_working_directory("MyApp")

# Get configuration values
working_dir = config.get('WORKING_DIR')
python_exec = config.get('PYTHON_EXECUTABLE', 'python')

# Set configuration values (automatically saves to .env)
config.set('DATABASE_PATH', '/path/to/db.s3db')

# Update multiple values at once
config.update({
    'API_KEY': 'your-api-key',
    'LOG_LEVEL': 'INFO'
})

# Check if configuration exists
if config.has('API_KEY'):
    api_key = config.get('API_KEY')

# Prompt user for missing configuration
db_path = config.prompt_if_missing(
    'DATABASE_PATH',
    'Enter database path',
    default='db.s3db'
)
```

### Key Features

- **Automatic `.env` creation** - Creates `.env` file if it doesn't exist
- **Persistent configuration** - All values saved to `.env` file automatically
- **Working directory management** - Stores and retrieves working directory location
- **Interactive prompts** - Can prompt users for missing configuration values
- **Non-interactive support** - Works in CI/CD environments without prompts
- **Type-safe** - Full type hints for IDE support

## Usage in Python Code

Once the database is set up, you can use the IdeaInspiration model in your Python code:

```python
from idea_inspiration import IdeaInspiration, ContentType
import sqlite3
import json

# Connect to the database
conn = sqlite3.connect('db.s3db')
cursor = conn.cursor()

# Create an IdeaInspiration instance
idea = IdeaInspiration.from_text(
    title="My Article",
    description="Article description",
    text_content="Full article content...",
    keywords=["article", "example"],
    score=85,
    category="technology"
)

# Convert to dictionary for storage
data = idea.to_dict()

# Store in database
cursor.execute('''
    INSERT INTO IdeaInspiration 
    (title, description, content, keywords, source_type, metadata, source_id, 
     source_url, score, category, subcategory_relevance, contextual_category_scores)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    data['title'],
    data['description'],
    data['content'],
    json.dumps(data['keywords']),
    data['source_type'],
    json.dumps(data['metadata']),
    data['source_id'],
    data['source_url'],
    data['score'],
    data['category'],
    json.dumps(data['subcategory_relevance']),
    json.dumps(data['contextual_category_scores'])
))

conn.commit()
conn.close()
```

## Architecture: IdeaInspiration Collection Layer

The IdeaInspiration model serves as the **collection layer** in the PrismQ content generation pipeline:

```
┌─────────────────────────────────┐
│  Sources (This Repository)      │
│  YouTube, TikTok, Lyrics, etc.  │
└────────────┬────────────────────┘
             │
             │ Collect & Transform
             ▼
┌─────────────────────────────────┐
│  IdeaInspiration Objects        │  ← This Repository's Output
│  (This Model)                   │
│  - Unified format               │
│  - Queryable database           │
└────────────┬────────────────────┘
             │
             │ Query & Retrieve
             ▼
┌─────────────────────────────────┐
│  PrismQ.Idea.Extractor          │  ← Blending/Mixing Happens Here
│  (Separate Module)              │
│  - Blend multiple IdeaInspiration│
│  - Add trending signals         │
│  - Create story concepts        │
└────────────┬────────────────────┘
             │
             │ Story Concepts
             ▼
┌─────────────────────────────────┐
│  PrismQ.Idea.Model              │  ← Content Generation
│  (Separate Module)              │
│  - Generate scripts             │
│  - Create videos                │
└─────────────────────────────────┘
```

### Role of This Repository

**Input**: Platform-specific data from various Sources  
**Processing**: Transform to unified IdeaInspiration format  
**Output**: Queryable IdeaInspiration objects  

**What This Repository Does:**
- ✅ Collect content from sources (YouTube, lyrics, trends)
- ✅ Transform to IdeaInspiration model
- ✅ Store in queryable database
- ✅ Provide search/filter capabilities

**What This Repository Does NOT Do:**
- ❌ Blend multiple IdeaInspiration together (→ PrismQ.Idea.Extractor)
- ❌ Generate story scripts (→ PrismQ.Idea.Model)
- ❌ Create video content (→ PrismQ.Idea.Model)

### Querying IdeaInspiration for Downstream Use

The primary interface for downstream modules (like PrismQ.Idea.Extractor) is **querying**:

```python
from idea_inspiration_db import IdeaInspirationDatabase

db = IdeaInspirationDatabase("db.s3db")

# Query by keywords
true_crime_ideas = db.filter(keywords=["true_crime"])

# Query by platform
youtube_ideas = db.filter(metadata_contains={'platform': 'youtube'})

# Query recent content
recent_ideas = db.filter(days_back=7)

# Query by score threshold
high_quality = db.filter(min_score=80)

# Combine filters
trending_shorts = db.filter(
    keywords=["mystery"],
    metadata_contains={'platform': 'youtube', 'is_short': 'true'},
    min_score=70,
    days_back=7
)
```

These queries provide IdeaInspiration objects that **PrismQ.Idea.Extractor** can then blend, mix, and transform into story concepts.

### Example Workflow

```python
# 1. Collect (This Repository)
from sources.youtube import YouTubeTrendingPlugin

plugin = YouTubeTrendingPlugin(config)
shorts = plugin.scrape_by_keyword("true crime", top_n=20)
# Returns: List[IdeaInspiration]

# Save to database
db = IdeaInspirationDatabase("db.s3db")
for idea in shorts:
    db.insert(idea)

# 2. Query (This Repository provides)
true_crime_inspirations = db.filter(keywords=["true_crime"])

# 3. Blend (PrismQ.Idea.Extractor - Separate Module)
# from prismq.idea.extractor import IdeaExtractor
# extractor = IdeaExtractor()
# story_concept = extractor.blend(true_crime_inspirations, strategy="topic")

# 4. Generate (PrismQ.Idea.Model - Separate Module)
# from prismq.idea.model import ScriptGenerator
# generator = ScriptGenerator()
# script = generator.create_script(story_concept)
```

### Related Documentation

For information on blending multiple IdeaInspiration objects:
- See **[Model Extension Research](_meta/docs/MODEL_EXTENSION_RESEARCH.md)** - Architecture and blending strategies
- See **PrismQ.Idea.Extractor** documentation (separate repository) - Implementation of blending logic

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.Model.git
cd PrismQ.IdeaInspiration.Model

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code with black
black prismq/ tests/

# Check code style with flake8
flake8 prismq/ tests/

# Type checking with mypy
mypy prismq/
```

## Integration with Other PrismQ Modules

### With Builder Module

The Builder module (PrismQ.IdeaInspiration.Builder) handles platform-specific transformations from various sources (YouTube, Reddit, etc.) into the clean IdeaInspiration model:

```python
from idea_inspiration import IdeaInspiration
from prismq.idea.builder import YouTubeBuilder, RedditBuilder

# Builder transforms YouTube data into clean model
youtube_builder = YouTubeBuilder()
idea = youtube_builder.build(video_data, transcription)

# Builder transforms Reddit data into clean model  
reddit_builder = RedditBuilder()
idea = reddit_builder.build(post_data)
```

### With Scoring Module

```python
from idea_inspiration import IdeaInspiration
from prismq.idea.scoring import ScoringEngine

engine = ScoringEngine()
idea = IdeaInspiration.from_text(
    title="My Article",
    text_content="Article content..."
)
score_results = engine.score_idea_inspiration(idea)
```

### With Classification Module

```python
from idea_inspiration import IdeaInspiration
from prismq.idea.classification import TextClassifier

classifier = TextClassifier()
idea = IdeaInspiration.from_text(
    title="My Story",
    text_content="This is my story..."
)
result = classifier.classify(idea)
```

## Package Structure

```
PrismQ.IdeaInspiration.Model/
├── idea_inspiration.py                  # Core IdeaInspiration model
├── config_manager.py                    # Configuration and .env management
├── tests/
│   ├── __init__.py
│   ├── test_model.py                    # Model tests
│   └── test_config_manager.py           # Configuration tests
├── setup_db.bat                         # Database setup (Windows)
├── setup_db.sh                          # Database setup (Linux/CI)
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml                       # Project configuration
├── requirements.txt                     # Dependencies (none)
└── setup.py                             # Setup configuration
```

## Design Principles

1. **Zero Dependencies** - Pure Python with no external requirements
2. **Type Safe** - Full type hints for IDE support
3. **Extensible** - Easy to add new factory methods for different sources
4. **Serializable** - Convert to/from dictionaries for storage
5. **SQLite Compatible** - Metadata uses string values for database compatibility
6. **Well Documented** - Clear documentation and examples
7. **Well Tested** - Comprehensive test coverage
8. **Single Responsibility** - Each class and method has one clear purpose
9. **Configuration Management** - Persistent configuration via `.env` files
10. **SOLID Principles** - Adheres to SOLID design patterns (SRP, OCP, LSP, ISP, DIP)

## Version History

- **v0.2.0** - Added blending patterns and comprehensive model extension research
- **v0.1.1** - SQLite/S3DB compatibility with `Dict[str, str]` metadata, comprehensive examples
- **v0.1.0** - Initial release with core IdeaInspiration model

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

## Related Projects

- **[PrismQ.IdeaInspiration.Scoring](https://github.com/Nomoos/PrismQ.IdeaInspiration.Scoring)** - Scoring engine for content evaluation
- **[PrismQ.IdeaInspiration.Classification](https://github.com/Nomoos/PrismQ.IdeaInspiration.Classification)** - Content classification system
- **PrismQ.IdeaInspiration.Builder** - Builder for creating models from sources (see [Issue #503](https://github.com/Nomoos/PrismQ.IdeaInspiration/issues/503))
- **PrismQ.IdeaInspiration.Sources** - Content source integrations
- **PrismQ.Idea.Model** - Content generation model (has M:N relation with this model - multiple IdeaInspirations can be blended into a new Idea for scripts, content generation, etc.)

## Research & Documentation

- **[Model Extension Research](_meta/docs/MODEL_EXTENSION_RESEARCH.md)** - Comprehensive research on extending the model with new entity types (Source, Content, Signal, Category, Collection) and advanced blending strategies
- **[Database Integration Summary](_meta/docs/DATABASE_INTEGRATION_SUMMARY.md)** - Dual-save architecture implementation details

## Support

For questions, issues, or feature requests:
1. Open an issue on GitHub
2. Review the documentation
3. Check the test files for usage examples

---

**Part of the PrismQ Ecosystem** - Unified content processing and generation platform