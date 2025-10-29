# PrismQ.IdeaInspiration.Scoring

A comprehensive scoring engine for evaluating idea inspirations from various content sources including YouTube, Reddit, and other social media platforms.

## 🎯 Purpose

This module provides a standardized scoring system for content ideas based on engagement metrics, performance indicators, and content quality measures. It's part of the PrismQ ecosystem for AI-powered content generation.

### Related PrismQ Projects

- **[PrismQ.IdeaCollector](https://github.com/Nomoos/PrismQ.IdeaCollector)** - Gather idea inspirations from various sources
- **[StoryGenerator](https://github.com/Nomoos/StoryGenerator)** - Automated story and video generation pipeline
- **[PrismQ.RepositoryTemplate](https://github.com/Nomoos/PrismQ.RepositoryTemplate)** - Base template for PrismQ modules

## 💻 Target Platform

This module is optimized for:
- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## 📁 Repository Structure

```
PrismQ.IdeaInspiration.Scoring/
├── .github/                    # GitHub configuration
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   ├── copilot-instructions.md # Copilot development guidelines
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/                       # Documentation
│   ├── CONTRIBUTING.md        # Contribution guidelines
│   └── README.md              # Documentation overview
├── issues/                     # Issue tracking
│   ├── new/                   # New issues
│   ├── wip/                   # Work in progress
│   ├── done/                  # Completed issues
│   ├── KNOWN_ISSUES.md        # Known issues list
│   ├── ROADMAP.md             # Project roadmap
│   └── README.md              # Issue tracking guide
├── scripts/                    # Utility scripts
│   ├── setup.bat              # Windows setup script
│   ├── setup.sh               # Linux setup script (development only)
│   ├── quickstart.bat         # Windows quick start
│   ├── quickstart.sh          # Linux quick start (development only)
│   └── README.md              # Scripts documentation
├── src/                        # Source code
│   ├── scoring/               # Scoring engine module
│   │   └── __init__.py        # ScoringEngine implementation
│   ├── __init__.py            # Package initialization
│   ├── main.py                # Main entry point with examples
│   └── config.py              # Configuration management
├── tests/                      # Test suite
│   ├── __init__.py            # Test package initialization
│   ├── test_config.py         # Configuration tests
│   └── test_scoring.py        # Scoring engine tests
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── LICENSE                    # Proprietary license
├── pyproject.toml             # Python project configuration
├── README.md                  # This file
└── requirements.txt           # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Windows OS (required)
- NVIDIA RTX 5090 with latest drivers
- 64GB RAM

### Installation

#### Windows

1. Clone this repository:
   ```batch
   git clone https://github.com/PrismQDev/PrismQ.IdeaInspiration.Scoring.git
   cd PrismQ.IdeaInspiration.Scoring
   ```

2. Run setup script:
   ```batch
   scripts\setup.bat
   ```

3. Configure environment:
   ```batch
   copy .env.example .env
   REM Edit .env with your configuration
   ```

4. Run the module:
   ```batch
   scripts\quickstart.bat
   ```

> **Note for Linux users**: Limited Linux support is available for development purposes only. See the scripts folder for Linux shell scripts. macOS is not supported.

## 📚 Usage

### Basic Usage

```python
from src.scoring import ScoringEngine

# Initialize the scoring engine
engine = ScoringEngine()

# Calculate score for generic metrics
metrics = {
    'views': 1000000,
    'likes': 50000,
    'comments': 1000,
    'shares': 5000,
    'saves': 2000
}

score, details = engine.calculate_score(metrics)
print(f"Score: {score:.2f}")
print(f"Details: {details}")
```

### YouTube Video Scoring

```python
from src.scoring import ScoringEngine

engine = ScoringEngine()

# YouTube video data from API
video_data = {
    'statistics': {
        'viewCount': '1000000',
        'likeCount': '50000',
        'commentCount': '1000'
    }
}

score, details = engine.calculate_youtube_score(video_data)
print(f"YouTube Score: {score:.2f}")
```

### Reddit Post Scoring

```python
from src.scoring import ScoringEngine

engine = ScoringEngine()

# Reddit post data
post_data = {
    'num_views': 50000,
    'score': 1000,
    'num_comments': 50
}

score, details = engine.calculate_reddit_score(post_data)
print(f"Reddit Score: {score:.2f}")
```

### Universal Content Score (UCS)

The Universal Content Score provides a comprehensive evaluation using multiple metrics:

```python
from src.scoring import ScoringEngine

engine = ScoringEngine()

metrics = {
    'views': 1000000,
    'likes': 50000,
    'comments': 1000,
    'shares': 5000,
    'saves': 2000,
    'average_watch_time': 45,
    'video_length': 60,
    'channel_median_views': 500000,
    'conversions': 1000
}

ucs_results = engine.calculate_universal_content_score(metrics)
print(f"Universal Content Score: {ucs_results['universal_content_score']:.2f}")
print(f"Engagement Rate: {ucs_results['engagement_rate']:.2f}%")
print(f"Watch-Through Rate: {ucs_results['watch_through_rate']:.2f}%")
print(f"RPI: {ucs_results['relative_performance_index']:.2f}%")
```

### AI-Based Text Quality Scoring (NEW)

Score text content using AI-powered quality metrics including readability, sentiment, and structure:

```python
from src.scoring import ScoringEngine
from src.models import IdeaInspiration, ContentType

engine = ScoringEngine()

# Score plain text content
idea = IdeaInspiration.from_text(
    title="Introduction to Machine Learning",
    description="A comprehensive guide to ML basics.",
    text_content="Machine learning is a subset of artificial intelligence..."
)

results = engine.score_idea_inspiration(idea)
print(f"Composite Score: {results['composite_score']:.2f}")
print(f"Text Quality: {results['text_quality']['overall_text_score']:.2f}")
print(f"Readability: {results['text_quality']['readability_score']:.2f}")
print(f"Sentiment: {results['text_quality']['sentiment_category']}")
```

### Generalized Content Scoring

The new `IdeaInspiration` model unifies text, video, and audio content:

```python
from src.models import IdeaInspiration, ContentType
from src.scoring import ScoringEngine

engine = ScoringEngine()

# From YouTube video with transcription
video_data = {
    'id': 'abc123',
    'snippet': {
        'title': "Python Tutorial",
        'description': "Learn Python programming",
        'channelTitle': "CodeMaster"
    },
    'statistics': {
        'viewCount': '500000',
        'likeCount': '25000',
        'commentCount': '500'
    }
}

transcription = "Welcome to this Python tutorial. We'll cover..."
video_idea = IdeaInspiration.from_youtube_video(video_data, transcription)
video_score = engine.score_idea_inspiration(video_idea)

print(f"Composite Score: {video_score['composite_score']:.2f}")
print(f"Engagement Score: {video_score['engagement_score']:.2f}")
print(f"Text Quality: {video_score['text_quality']['overall_text_score']:.2f}")
print(f"Content Type: {video_score['content_type']}")
```

### Direct Text Scoring

Score text without creating an IdeaInspiration object:

```python
from src.scoring import ScoringEngine

engine = ScoringEngine()

results = engine.score_text_content(
    title="Great Article Title",
    description="This is a brief description.",
    text_content="Full article text goes here..."
)

print(f"Score: {results['composite_score']:.2f}")
print(f"Title Quality: {results['title_quality']['title_quality_score']:.2f}")
print(f"Description Quality: {results['description_quality']['description_quality_score']:.2f}")
```

## 🔧 Scoring Metrics

### Engagement-Based Metrics

1. **Basic Score**: Weighted score based on views, likes, comments, and engagement
2. **Engagement Rate (ER)**: `(likes + comments + shares + saves) / views × 100%`
3. **Watch-Through Rate**: `(average watch time / video length) × 100%`
4. **Conversion Rate (CR)**: `conversions / views × 100%`
5. **Relative Performance Index (RPI)**: `(current metric / channel median) × 100%`
6. **Universal Content Score (UCS)**: Composite score using ER, Watch-Through, and RPI

### AI-Based Text Quality Metrics (NEW)

7. **Readability Score**: Flesch Reading Ease and Flesch-Kincaid Grade Level
8. **Text Structure**: Evaluates paragraph and sentence structure
9. **Length Score**: Optimal length ranges for different content types
10. **Sentiment Analysis**: Positive, negative, or neutral sentiment detection
11. **Title Relevance**: How well the title matches the content
12. **Title Quality**: Optimal length and word count for titles
13. **Description Quality**: Optimal length and structure for descriptions

### Custom Weights

You can customize the scoring weights:

```python
# Custom weights for different scoring components
custom_weights = [1.0, 0.5, 0.3]
engine = ScoringEngine(weights=custom_weights)
```

## 🛠️ Development

### Running Tests

```batch
# Activate virtual environment first (Windows)
venv\Scripts\activate

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

> **Note for Linux users**: Use `source venv/bin/activate` to activate the virtual environment on Linux.

### Running the Example

```batch
# Activate virtual environment
venv\Scripts\activate

# Run the main module
python -m src.main
```

## 📋 Features

### Implemented Features

**Engagement-Based Scoring:**
- ✅ Generic content scoring based on engagement metrics
- ✅ YouTube video scoring
- ✅ Reddit post scoring
- ✅ Engagement rate calculation
- ✅ Watch-through rate calculation
- ✅ Conversion rate calculation
- ✅ Relative Performance Index (RPI)
- ✅ Universal Content Score (UCS)

**AI-Based Text Quality Scoring (NEW):**
- ✅ `IdeaInspiration` model for unified content structure (text/video/audio)
- ✅ Readability scoring (Flesch Reading Ease, Flesch-Kincaid Grade Level)
- ✅ Text structure and coherence analysis
- ✅ Sentiment analysis (positive/negative/neutral)
- ✅ Title quality and relevance scoring
- ✅ Description quality scoring
- ✅ Composite scoring combining engagement and text quality
- ✅ Support for text, video, and audio content types
- ✅ Factory methods for creating IdeaInspiration from various sources

**General:**
- ✅ Comprehensive test suite
- ✅ Custom weight support

### Future Enhancements

- ⬜ Advanced AI models (transformers, sentence-transformers) for semantic analysis
- ⬜ Audio transcription integration (Whisper, speech-to-text)
- ⬜ Video subtitle extraction
- ⬜ TikTok content scoring
- ⬜ Instagram Reels scoring
- ⬜ Twitter/X post scoring
- ⬜ Multi-platform comparison
- ⬜ Trend detection algorithms
- ⬜ Real-time scoring API

## 🔧 Configuration

The module uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```bash
# Application Settings
APP_NAME=PrismQ.IdeaInspiration.Scoring
APP_ENV=development
DEBUG=true

# Paths
INPUT_DIR=./input
OUTPUT_DIR=./output
```

## 📄 License

This repository is proprietary software. See [LICENSE](LICENSE) file for details.

**All Rights Reserved** - Copyright (c) 2025 PrismQ

## 🔗 Related Resources

- [PrismQ.IdeaCollector](https://github.com/Nomoos/PrismQ.IdeaCollector) - Idea generation module
- [StoryGenerator](https://github.com/Nomoos/StoryGenerator) - Story generation pipeline
- [PrismQ.RepositoryTemplate](https://github.com/Nomoos/PrismQ.RepositoryTemplate) - Base template

## 💬 Support

For questions, issues, or feature requests:
1. Check [Known Issues](issues/KNOWN_ISSUES.md)
2. Review [Documentation](docs/)
3. Open a new issue using the appropriate template

---

**Built with the PrismQ.RepositoryTemplate** - A comprehensive template for PrismQ modules.