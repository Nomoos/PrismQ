# T/Idea/Inspiration - Idea Inspiration Submodule

**Namespace**: `PrismQ.T.Idea.Inspiration`

The Inspiration submodule represents the initial stage of idea development where raw inspiration is collected, classified, and scored before being developed into structured Ideas. It serves as the entry point for all content creation in the PrismQ workflow.

## Purpose

Gather and evaluate content inspiration from diverse sources to identify high-potential concepts for idea development. This submodule transforms raw inspiration into structured, scored concepts ready for the Idea development process (Model, Outline, Review).

## Workflow Position

```
[*] → Idea.Inspiration → Idea (Model/Outline/Review) → Script...
       ↑
       └─── Analytics Feedback Loop (Text/Audio/Video Performance)
```

**Entry Point**: Initial state for all new content  
**Next Stage**: Idea development (Model, Outline, Review)  
**Feedback Loop**: Performance analytics from published content

## Key Features

### Multi-Source Inspiration Collection

Collects ideas from **24+ sources** including:
- **Social Media**: Reddit, Twitter, Instagram, TikTok trends
- **News & Articles**: RSS feeds, news aggregators, Medium, Substack
- **Analytics**: Performance data from published content
- **User Feedback**: Comments, engagement, audience requests
- **Research**: Academic papers, industry reports, whitepapers
- **Competitors**: Trending content in your niche
- **Personal Notes**: Manual idea capture and brainstorming

### Content Classification

Organizes inspiration into **8 content categories**:
- Educational/Tutorial
- Entertainment/Storytelling
- News/Commentary
- Product Reviews
- Behind-the-Scenes
- Opinion/Analysis
- How-To Guides
- Trends/Reactions

### Engagement Scoring

Scores each inspiration on a **0-100 scale** based on:
- **Trend Velocity**: How fast the topic is growing
- **Audience Interest**: Target demographic engagement
- **Platform Fit**: Alignment with target platforms (YouTube, TikTok, etc.)
- **Competition**: Content saturation and opportunity gaps
- **Timeliness**: Time-sensitivity and evergreen potential
- **Production Feasibility**: Resource requirements and complexity

## Submodule Structure

```
Inspiration/
├── README.md              # This file
├── Collection/            # (Planned) Source collection strategies
├── Classification/        # (Planned) Content categorization
├── Scoring/              # (Planned) Engagement potential scoring
└── _meta/                # Submodule metadata
    ├── docs/             # Documentation
    ├── examples/         # Usage examples
    └── tests/            # Test suites
```

## Key Activities

1. **Source Monitoring**
   - Track multiple content sources continuously
   - Identify emerging trends and topics
   - Collect audience feedback and requests

2. **Idea Capture**
   - Extract relevant content concepts
   - Tag with source, timestamp, and context
   - Preserve links to original inspiration

3. **Classification**
   - Categorize by content type
   - Identify target platforms
   - Map to audience segments

4. **Potential Scoring**
   - Analyze trend velocity and timing
   - Assess production feasibility
   - Calculate engagement potential
   - Rank against other inspirations

5. **Queue Management**
   - Maintain prioritized inspiration queue
   - Archive low-scoring ideas
   - Surface high-potential concepts for development

## Deliverables

Each Inspiration produces:

- **Concept Summary**: Brief description of the inspiration
- **Source Attribution**: Where the idea came from
- **Category**: Content type classification
- **Score**: 0-100 engagement potential rating
- **Target Audience**: Demographic and platform fit
- **Timing Notes**: Timeliness and urgency indicators
- **Related Ideas**: Connections to other inspirations

## Transition Criteria

**Move to Idea.Model when**:
- Inspiration score ≥ 70 (high potential)
- Clear story angle identified
- Target audience defined
- Platform requirements understood
- Production feasibility confirmed

**Archive when**:
- Score < 40 (low potential)
- Already covered by existing content
- Outside content strategy scope
- Production not feasible
- Timing window missed

## Integration with Analytics

### Feedback Loop from Published Content

Performance data feeds back to improve future inspiration:

- **AnalyticsReviewText → Idea.Inspiration**
  - Which topics performed well in text format
  - SEO keywords and search trends
  - Reader engagement patterns

- **AnalyticsReviewAudio → Idea.Inspiration**
  - Podcast listening patterns
  - Audio completion rates
  - Platform-specific preferences

- **AnalyticsReviewVideo → Idea.Inspiration**
  - Video watch time and retention
  - Thumbnail and title effectiveness
  - Platform algorithm preferences

This creates a continuous improvement loop where published content performance informs future inspiration collection and scoring.

## Usage Examples

### Python Namespace
```python
from datetime import datetime
from PrismQ.T.Idea.Inspiration import Collection, Classification, Scoring

# Collect inspiration from sources
inspiration = Collection.from_reddit(subreddit="technology")

# Classify the content
category = Classification.categorize(inspiration)

# Score engagement potential
score = Scoring.calculate_potential(inspiration)

# Create inspiration record
idea_inspiration = Inspiration(
    concept=inspiration.summary,
    source="Reddit: r/technology",
    category=category,
    score=score,
    timestamp=datetime.now()
)
```

### State Transitions
```python
# Start with inspiration
idea = Idea(status=IdeaStatus.INSPIRATION)

# Collect and score
idea.inspiration = collect_inspiration(sources)
idea.score = calculate_score(idea.inspiration)

# High score → move to Model development
if idea.score >= 70:
    idea.status = IdeaStatus.MODEL
    
# Low score → archive
elif idea.score < 40:
    idea.status = IdeaStatus.ARCHIVED
```

## Best Practices

### Source Diversity
- Monitor at least 5 different source types
- Balance trending and evergreen topics
- Include both audience-driven and strategy-driven ideas

### Regular Collection
- Daily trend monitoring for time-sensitive content
- Weekly deep dives for evergreen topics
- Continuous analytics review for feedback

### Scoring Discipline
- Use consistent scoring criteria
- Calibrate scores against actual performance
- Update scoring models based on analytics feedback

### Queue Management
- Review inspiration queue weekly
- Archive stale or low-scoring items
- Resurface relevant archived ideas when trending

## Metrics & Monitoring

### Collection Metrics
- Sources monitored
- Ideas captured per day
- Source diversity index

### Quality Metrics
- Average inspiration score
- High-potential idea rate (score ≥ 70)
- Conversion rate (inspiration → published content)

### Effectiveness Metrics
- Time from inspiration to publication
- Published content performance vs. predicted score
- Scoring accuracy improvement over time

## Related Submodules

- **Next Stage**: [Model](../Model/README.md) - Idea data structure
- **Next Stage**: [Outline](../Outline/README.md) - Content outline development
- **Next Stage**: [Review](../Review/README.md) - Idea validation

## Submodule Metadata

### Documentation
Technical documentation and implementation guides.

**[→ View Inspiration/_meta/docs/](./_meta/docs/)**

### Examples
Usage examples and sample implementations.

**[→ View Inspiration/_meta/examples/](./_meta/examples/)**

### Tests
Test suites and test data.

**[→ View Inspiration/_meta/tests/](./_meta/tests/)**

---

## Navigation

**[← Back to Idea Module](../README.md)** | **[Next: Model →](../Model/README.md)** | **[T Pipeline](../../README.md)** | **[Workflow](../../../_meta/WORKFLOW.md)**

---

*Part of the PrismQ.T.Idea module in the sequential progressive enrichment workflow*
# PrismQ.T.Idea.Inspiration

Central hub for AI-powered content idea collection, classification, scoring, and processing.

**Primary Platform**: Windows 10/11 with NVIDIA RTX 5090

## 🖥️ Platform & Requirements

### Primary Platform
- **OS**: Windows 10/11 (Primary)
- **GPU**: NVIDIA RTX 5090 (Ada Lovelace, 32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5
- **Python**: 3.10.x (Required)

### Cross-Platform Support
- Linux and macOS are supported for development and testing
- Production deployment optimized for Windows

## ⚠️ Python Version Requirement

**IMPORTANT: This project requires Python 3.10.x (NOT 3.11 or 3.12)**

- **Required Version**: Python 3.10.x (recommended: 3.10.11)
- **Download**: [python-3.10.11-amd64.exe](https://www.python.org/downloads/release/python-31011/)
- **Reason**: DaVinci Resolve compatibility + module dependencies
- **Do NOT use**: Python 3.11+ will cause compatibility issues

### Windows Python Launcher (`py`) - Recommended

For better version management on Windows, use the **Python Launcher (`py`)**:

```powershell
# Check Python 3.10 is available
py -3.10 --version

# Use py to run scripts and create virtual environments
py -3.10 -m venv venv
py -3.10 -m pip install -e .
```

The `py` launcher allows you to:
- ✅ Have multiple Python versions installed simultaneously
- ✅ Explicitly specify Python 3.10 with `py -3.10`
- ✅ Keep other Python versions (3.11, 3.12) for other projects
- ✅ Better compatibility with future Python versions

All modules are configured with `requires-python = ">=3.10,<3.11"` to ensure compatibility.

## ✨ Highlights

- **24 source integrations** - YouTube, Reddit, Google Trends, TikTok, and more
- **8-category classification** - Automated content categorization with story detection
- **0-100 scoring system** - Comprehensive engagement and quality evaluation
- **Unified data model** - IdeaInspiration structure for cross-platform content
- **Web control panel** - Run and monitor modules via localhost interface
- **Optimized for Windows RTX 5090** - GPU-accelerated processing with proper async support

## 🚀 Quick Start (Windows)

```powershell
# Clone repository
git clone https://github.com/Nomoos/PrismQ.T.Idea.Inspiration.git
cd PrismQ.T.Idea.Inspiration

# Setup virtual environments
.\_meta\_scripts\setup_all_envs.ps1  # Windows
./_meta/_scripts/setup_all_envs.sh   # Linux/macOS
```

## 📦 Modules

| Module | Purpose |
|--------|---------|
| **[Classification](./Classification/)** | Content categorization and story detection |
| **[ConfigLoad](./ConfigLoad/)** | Centralized configuration management |
| **[Model](./Model/)** | Core IdeaInspiration data model |
| **[Scoring](./Scoring/)** | Content scoring and evaluation engine |
| **[Sources](./Sources/)** | Content source integrations (24 sources) |

## 📚 Documentation

### Architecture & Design
- **[System Architecture](./_meta/docs/ARCHITECTURE.md)** - Complete system architecture with diagrams
- **[Scoring Module Architecture](./Scoring/_meta/docs/ARCHITECTURE.md)** - Scoring module details
- **[Python Packaging Standard](./_meta/docs/PYTHON_PACKAGING_STANDARD.md)** - Standardized configuration
- **[Contributing](./_meta/docs/CONTRIBUTING.md)** - How to contribute to this project

### Planning & Development
- **[Development Plan](./DEVELOPMENT_PLAN.md)** - Unified development plan and current status (START HERE)
- **[Project Roadmap](./_meta/issues/ROADMAP.md)** - Long-term roadmap and future plans
- **[Known Issues](./_meta/issues/KNOWN_ISSUES.md)** - Current limitations and bugs
- **[Issue Tracking](./_meta/issues/INDEX.md)** - Issue management and workflow
- **[Setup Guide](./_meta/docs/SETUP.md)** - Installation and environment setup
- **[Documentation Index](./_meta/docs/README.md)** - Complete documentation overview
- **[Archive](./_meta/docs/archive/)** - Historical documentation and completed phases

### Legacy Reference Materials
- **[Legacy Reference](./Legacy_Reference/)** - Legacy code and reference materials for learning
  - **Architecture/** - SOLID principles, project splitting, and design patterns from StoryGenerator
  - **Documentation/** - Repository overview and architecture philosophy
  - **Pipeline/** - Pipeline architecture and modular design patterns
  - **Content/, Commerce/, Signals/, etc.** - Previous source implementations organized by category

## 🔗 Related

- [PrismQ.IdeaCollector](https://github.com/Nomoos/PrismQ.IdeaCollector) - CLI tool for idea collection
- [StoryGenerator](https://github.com/Nomoos/StoryGenerator) - Automated story and video generation
- [PrismQ.RepositoryTemplate](https://github.com/Nomoos/PrismQ.RepositoryTemplate) - Base template for PrismQ modules

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
