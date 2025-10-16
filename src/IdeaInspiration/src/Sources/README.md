# PrismQ.Idea.Sources

A comprehensive library for managing various types of content sources for the PrismQ idea generation system.

## Overview

This library provides a unified interface for collecting and managing different types of signals and inspiration sources. Each source type has its own data model (DTO/Entity), interface contract, and example implementation.

## Source Types

| Source Type              | DTO / Entity           | Interface              | Example Implementation    |
| ------------------------ | ---------------------- | ---------------------- | ------------------------- |
| Content                  | `InspirationItem`      | `IContentSource`       | `YouTubeShortsSource`     |
| Signal                   | `TrendSignal`          | `ISignalSource`        | `GoogleTrendsSource`      |
| Product                  | `ProductSignal`        | `IProductSource`       | `AmazonBestsellersSource` |
| Event                    | `EventSignal`          | `IEventSource`         | `CalendarHolidaysSource`  |
| Community (global)       | `CommunitySignal`      | `ICommunitySource`     | `CommentMiningSource`     |
| Community (own channel)  | `UserFeedbackSignal`   | `IUserFeedbackSource`  | `UserFeedbackSource`      |
| Creative                 | `CreativeCue`          | `ICreativeSource`      | `VisualMoodboardSource`   |
| Internal                 | `InspirationItem`      | `IContentSource`       | `ManualBacklogSource`     |

## Project Structure

```
PrismQ.Idea.Sources/
├── src/                     # Source code
│   ├── models/              # Data models
│   │   ├── baseline.py
│   │   └── inspiration_metrics.py
│   ├── interfaces/          # Interface contracts
│   └── sources/             # Example implementations
├── tests/                   # Test files
│   └── models/              # Model tests
│       ├── test_baseline.py
│       └── test_inspiration_metrics.py
├── docs/                    # Documentation
├── pyproject.toml           # Python project configuration
└── requirements.txt         # Python dependencies
```

## Key Features

### UserFeedbackSource (Community - Own Channel)

The `UserFeedbackSource` provides functionality for collecting and analyzing user feedback from your own channel:

- **GetUserFeedbackAsync()**: Retrieve all user feedback
- **GetUserFeedbackByVideoAsync(videoId)**: Filter feedback by specific video
- **GetUserFeedbackBySentimentAsync(sentiment)**: Filter by sentiment (-1: negative, 0: neutral, 1: positive)

#### Example Usage

```python
from src.models import Baseline, InspirationMetrics
from datetime import datetime

# Create a baseline
baseline = Baseline(
    id="baseline123",
    scope_type="account",
    metric="engagement_rate",
    baseline_value=0.045,
    computed_at=datetime.now()
)

# Create inspiration metrics
metrics = InspirationMetrics(
    id="metrics123",
    inspiration_item_id="item456",
    views=10000,
    engagement_rate_pct=150,
    computed_at=datetime.now()
)
```

## Installation

```bash
pip install -r requirements.txt
```

## Running Tests

```bash
pytest tests/ -v
```

## Contributing

When implementing a new source:

1. Create the appropriate data model in `src/models/`
2. Define the interface contract in `src/interfaces/`
3. Implement the example class in `src/sources/`
4. Add comprehensive tests in `tests/`

## License

This project is part of the PrismQ ecosystem.
Source taxonomy for content ideation — from earliest signal to rich content (before IdeaBrief synthesis).

## Overview

This repository serves as a navigation point and documentation hub for various content sources organized by type and purpose. Each source represents a different data stream that can inform content creation, trend analysis, and idea generation.

## Source Taxonomy

```
PrismQ.Idea.Sources
 ├─ Content
 │   ├─ Shorts
 │   │   ├─ YouTubeShortsSource
 │   │   ├─ TikTokSource
 │   │   └─ InstagramReelsSource
 │   ├─ Streams
 │   │   ├─ TwitchClipsSource
 │   │   └─ KickClipsSource
 │   ├─ Forums
 │   │   ├─ RedditSource
 │   │   └─ HackerNewsSource
 │   ├─ Articles
 │   │   ├─ MediumSource
 │   │   └─ WebArticleSource
 │   └─ Podcasts
 │       ├─ SpotifyPodcastsSource
 │       └─ ApplePodcastsSource
 ├─ Signals
 │   ├─ Trends
 │   │   ├─ GoogleTrendsSource
 │   │   └─ TrendsFileSource
 │   ├─ Hashtags
 │   │   ├─ TikTokHashtagSource
 │   │   └─ InstagramHashtagSource
 │   ├─ Memes
 │   │   ├─ MemeTrackerSource
 │   │   └─ KnowYourMemeSource
 │   ├─ Challenges
 │   │   └─ SocialChallengeSource
 │   ├─ Sounds
 │   │   ├─ TikTokSoundsSource
 │   │   └─ InstagramAudioTrendsSource
 │   ├─ Locations
 │   │   └─ GeoLocalTrendsSource
 │   └─ News
 │       ├─ GoogleNewsSource
 │       └─ NewsApiSource
 ├─ Commerce
 │   ├─ AmazonBestsellersSource
 │   ├─ EtsyTrendingSource
 │   └─ AppStoreTopChartsSource
 ├─ Events
 │   ├─ CalendarHolidaysSource
 │   ├─ SportsHighlightsSource
 │   └─ EntertainmentReleasesSource
 ├─ Community
 │   ├─ QASource                 (StackExchange/Quora)
 │   ├─ CommentMiningSource      (YouTube/IG/TikTok comments — global)
 │   ├─ UserFeedbackSource       (your own channel comments / DMs)
 │   └─ PromptBoxSource          (user-submitted prompts, forms)
 ├─ Creative
 │   ├─ LyricSnippetsSource
 │   ├─ ScriptBeatsSource
 │   └─ VisualMoodboardSource
 └─ Internal
     ├─ ManualBacklogSource
     └─ CSVImportSource
```

## Categories

### Content
Rich, fully-formed content sources including short-form videos, streams, forum discussions, articles, and podcasts. These provide direct content examples and inspiration.

### Signals
Early indicators of emerging trends including search trends, hashtags, memes, challenges, sounds, location-based trends, and breaking news.

### Commerce
Product and app marketplace trends that indicate consumer interests and purchasing behavior.

### Events
Scheduled and recurring events including holidays, sports events, and entertainment releases that drive content opportunities.

### Community
Direct audience feedback and community-driven content including Q&A platforms, comment analysis, user feedback, and submitted prompts.

### Creative
Creative resources and inspiration including lyric snippets, narrative structures, and visual aesthetics.

### Internal
Internally managed sources including manual backlogs and data imports.

## Usage

Navigate to each source directory to find detailed documentation about:
- Data points captured
- Integration methods
- Use cases
- Example outputs

## Contributing

Each source should include:
1. Clear description of what it captures
2. List of data points collected
3. Source type and category
4. Integration guidance (when applicable)
**Central Documentation and Navigation Hub for the PrismQ Ecosystem**

This repository serves as the primary entry point and navigation center for all PrismQ projects. It provides comprehensive documentation about the ecosystem's structure, taxonomy, and links to all related repositories.

## Overview

PrismQ is a modular ecosystem designed for idea collection, processing, and management. This repository maintains:

- **Taxonomy Documentation**: Comprehensive structure and organization of the ecosystem
- **Navigation Guide**: Quick access to all PrismQ repositories and resources
- **Ecosystem Overview**: High-level understanding of component relationships

## Quick Start

### Explore the Ecosystem

1. **[Taxonomy](docs/TAXONOMY.md)**: Understand the structure and organization of PrismQ components
2. **[Navigation Guide](docs/NAVIGATION.md)**: Find and access all PrismQ repositories
3. **Related Projects**: Discover connections to other initiatives

### Key Repositories

| Repository | Purpose | Link |
|-----------|---------|------|
| **PrismQ.IdeaCollector** | CLI tool for idea collection | [View Repository](https://github.com/Nomoos/PrismQ.IdeaCollector) |
| **PrismQ.RepositoryTemplate** | Template for new projects | [View Repository](https://github.com/Nomoos/PrismQ.RepositoryTemplate) |

## Documentation Structure

```
PrismQ.Idea.Sources/
├── README.md           # This file - main overview
└── docs/
    ├── TAXONOMY.md     # Ecosystem taxonomy and structure
    └── NAVIGATION.md   # Comprehensive navigation guide
```

## Purpose

This repository exists to:

- ✅ Provide clear navigation across the PrismQ ecosystem
- ✅ Maintain comprehensive taxonomy documentation
- ✅ Serve as the authoritative source for ecosystem structure
- ✅ Guide new users and contributors
- ✅ Document relationships between components

## Getting Started

### For New Users
Start by reviewing the [Navigation Guide](docs/NAVIGATION.md) to understand what's available in the ecosystem.

### For Contributors
Review the [Taxonomy](docs/TAXONOMY.md) to understand the ecosystem structure before contributing to specific repositories.

### For Developers
Explore individual repositories linked in the [Navigation Guide](docs/NAVIGATION.md) for technical documentation and setup instructions.

## Maintaining This Repository

This repository should be updated whenever:

- A new PrismQ repository is created
- Repository relationships change
- Major architectural decisions are made
- Documentation standards evolve

## License

All Rights Reserved

## Contact

For questions about the PrismQ ecosystem, please open an issue in the relevant repository or contact the maintainers.
