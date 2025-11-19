# PrismQ.IdeaInspiration.Scoring

Comprehensive scoring engine for evaluating content ideas from various sources.

## ✨ Highlights

- **0-100 scoring system** - Standardized quality and engagement evaluation
- **Multi-source support** - YouTube, Reddit, and other social media platforms
- **Engagement metrics** - Views, likes, comments, shares analysis
- **Performance indicators** - Watch time, CTR, retention metrics
- **Quality measures** - Content quality and relevance scoring
- **Worker pattern** - Distributed task processing with TaskManager API integration
- **Optimized for RTX 5090** - GPU-accelerated processing on Windows

## 🚀 Quick Start

### As a Library

```python
from src.scoring import ScoringEngine

engine = ScoringEngine()
score, details = engine.calculate_youtube_score(video_data)
```

### As a Worker

```bash
# Start scoring worker
python scripts/run_worker.py

# With custom configuration
python scripts/run_worker.py --worker-id scorer-01 --strategy PRIORITY
```

## 📚 Documentation

- **[Architecture](./_meta/docs/ARCHITECTURE.md)** - System design and scoring algorithms
- **[AI Text Scoring](./_meta/docs/AI_TEXT_SCORING.md)** - Text-based content scoring
- **[Worker Implementation](./src/workers/README.md)** - Worker pattern and distributed processing
- **[Contributing](./_meta/docs/CONTRIBUTING.md)** - Development guidelines
- **[Roadmap](./_meta/issues/ROADMAP.md)** - Future development plans
- **[Known Issues](./_meta/issues/KNOWN_ISSUES.md)** - Current limitations

## 🔧 Usage Modes

### 1. Library Mode (Direct API)

Use the scoring engine directly in your code:

```python
from src.scoring import ScoringEngine

engine = ScoringEngine()

# Score YouTube video
video_data = {'statistics': {'viewCount': '1000000', 'likeCount': '50000'}}
score, details = engine.calculate_youtube_score(video_data)

# Score text content
text_scores = engine.score_text_content(
    title="Title",
    description="Description",
    text_content="Content..."
)
```

### 2. Worker Mode (Distributed Processing)

Run as a worker for distributed task processing:

```bash
# Basic worker
python scripts/run_worker.py

# Priority-based claiming
python scripts/run_worker.py --strategy PRIORITY

# Local queue only (no TaskManager API)
python scripts/run_worker.py --no-taskmanager
```

**Worker Features:**
- Task claiming strategies (FIFO, LIFO, PRIORITY)
- TaskManager API integration for centralized coordination
- Local SQLite queue for persistence
- Automatic retry and error handling
- Heartbeat monitoring

See [Worker Documentation](./src/workers/README.md) for detailed usage.

## 🔗 Related

- [Main Repository](../) - PrismQ.IdeaInspiration overview
- [Model Module](../Model/) - Core IdeaInspiration data model
- [Classification Module](../Classification/) - Content categorization
- [PrismQ.IdeaCollector](https://github.com/Nomoos/PrismQ.IdeaCollector) - CLI tool for idea collection
- [StoryGenerator](https://github.com/Nomoos/StoryGenerator) - Automated story generation

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
