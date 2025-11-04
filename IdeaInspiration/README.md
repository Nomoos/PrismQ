# PrismQ.IdeaInspiration

Central hub for AI-powered content idea collection, classification, scoring, and processing.

## ✨ Highlights

- **24 source integrations** - YouTube, Reddit, Google Trends, TikTok, and more
- **8-category classification** - Automated content categorization with story detection
- **0-100 scoring system** - Comprehensive engagement and quality evaluation
- **Unified data model** - IdeaInspiration structure for cross-platform content
- **Web control panel** - Run and monitor modules via localhost interface
- **Optimized for RTX 5090** - GPU-accelerated processing on Windows

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
cd PrismQ.IdeaInspiration

# Setup virtual environments
.\_meta\_scripts\setup_all_envs.ps1  # Windows
./_meta/_scripts/setup_all_envs.sh   # Linux/macOS

# Start web client (Windows quick launcher)
_meta\_scripts\run_both.bat
```

## 📦 Modules

| Module | Purpose |
|--------|---------|
| **[Client](./Client/)** | Web control panel for running modules |
| **[Classification](./Classification/)** | Content categorization and story detection |
| **[ConfigLoad](./ConfigLoad/)** | Centralized configuration management |
| **[Model](./Model/)** | Core IdeaInspiration data model |
| **[Scoring](./Scoring/)** | Content scoring and evaluation engine |
| **[Sources](./Sources/)** | Content source integrations (24 sources) |

## 📚 Documentation

### Architecture & Design
- **[System Architecture](./_meta/docs/ARCHITECTURE.md)** - Complete system architecture with diagrams
- **[Web Client Architecture](./Client/docs/ARCHITECTURE.md)** - Detailed Client architecture
- **[Scoring Module Architecture](./Scoring/_meta/docs/ARCHITECTURE.md)** - Scoring module details
- **[Python Packaging Standard](./_meta/docs/PYTHON_PACKAGING_STANDARD.md)** - Standardized configuration
- **[Contributing](./_meta/docs/CONTRIBUTING.md)** - How to contribute to this project

### Planning & Development
- **[Project Roadmap](./_meta/issues/ROADMAP.md)** - Future development plans
- **[Known Issues](./_meta/issues/KNOWN_ISSUES.md)** - Current limitations and bugs
- **[Research](./_meta/research/)** - Experimental work and investigations
- **[Setup Guide](./_meta/docs/SETUP.md)** - Installation and environment setup
- **[Documentation Index](./_meta/docs/README.md)** - Complete documentation overview

## 🔗 Related

- [PrismQ.IdeaCollector](https://github.com/Nomoos/PrismQ.IdeaCollector) - CLI tool for idea collection
- [StoryGenerator](https://github.com/Nomoos/StoryGenerator) - Automated story and video generation
- [PrismQ.RepositoryTemplate](https://github.com/Nomoos/PrismQ.RepositoryTemplate) - Base template for PrismQ modules

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
