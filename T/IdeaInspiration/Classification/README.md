# PrismQ.IdeaInspiration.Classification

Platform-agnostic content classification with generalized text analysis.

## ✨ Highlights

- **8-category classifier** - Optimized for short-form video content
- **Story detection** - Binary classifier for story-based content
- **Platform-independent** - Works with standard text fields (title, description, tags, subtitles)
- **Zero external dependencies** - Local processing, no API calls
- **IdeaInspiration model** - Unified data structure across text, video, and audio
- **Worker architecture** - Distributed processing via TaskManager API integration
- **48 comprehensive tests** - Well-tested with realistic examples

## 🚀 Quick Start

```bash
# Install from source
git clone https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification.git
cd PrismQ.IdeaInspiration.Classification
pip install -e .

# Basic usage
python -c "from prismq.idea.classification import CategoryClassifier; print('OK')"

# Run as distributed worker
python scripts/register_task_types.py
python scripts/run_worker.py
```

## 🔄 Worker Mode (NEW)

Classification now supports distributed processing via TaskManager API:

```bash
# Register classification task types
python scripts/register_task_types.py

# Start a classification worker
python scripts/run_worker.py --claiming-policy FIFO

# Start multiple workers for parallel processing
python scripts/run_worker.py --worker-id worker-001 &
python scripts/run_worker.py --worker-id worker-002 &
```

**Benefits:**
- Distributed classification across multiple workers
- Task deduplication and priority management
- Fault tolerance with automatic retries
- Centralized monitoring and coordination

See [Worker README](src/workers/README.md) for detailed documentation.
```

## 📚 Documentation

- **[Setup Guide](./_meta/docs/SETUP.md)** - Installation and development environment
- **[User Guide](./_meta/docs/USER_GUIDE.md)** - Complete usage examples and features
- **[API Reference](./_meta/docs/API.md)** - Detailed API documentation
- **[Worker Guide](src/workers/README.md)** - Distributed processing with TaskManager API
- **[Generalized Classification](./_meta/docs/GENERALIZED_CLASSIFICATION.md)** - Advanced classification concepts
- **[Contributing](./_meta/docs/CONTRIBUTING.md)** - Development guidelines

## 🔗 Related

- [Main Repository](../) - PrismQ.IdeaInspiration overview
- [Model Module](../Model/) - Core IdeaInspiration data model
- [Scoring Module](../Scoring/) - Content scoring engine

## 📄 License

MIT License - See LICENSE file for details
