# PrismQ.IdeaInspiration

**Central hub for AI-powered content idea collection, classification, scoring, and processing**

## Overview

PrismQ.IdeaInspiration is a comprehensive ecosystem for discovering, evaluating, and managing content ideas from various sources. This repository contains multiple specialized modules that work together to power the PrismQ content generation pipeline.

## 🎯 Purpose

This ecosystem provides tools for:
- **Collecting** ideas from diverse content sources (YouTube, Reddit, articles, etc.)
- **Classifying** content into categories and detecting story potential
- **Scoring** content based on engagement metrics and quality indicators
- **Modeling** unified data structures for cross-platform content

## 📦 Modules

### Core Components

| Module | Purpose | Documentation |
|--------|---------|---------------|
| **[Classification](./Classification/)** | Content categorization and story detection | [README](./Classification/README.md) |
| **[ConfigLoad](./ConfigLoad/)** | Centralized configuration management | [README](./ConfigLoad/README.md) |
| **[Model](./Model/)** | Core IdeaInspiration data model | [README](./Model/README.md) |
| **[Scoring](./Scoring/)** | Content scoring and evaluation engine | [README](./Scoring/README.md) |
| **[Sources](./Sources/)** | Content source integrations and taxonomy | [README](./Sources/README.md) |

### Supporting Directories

| Directory | Purpose |
|-----------|---------|
| **[_meta](./_meta/)** | Project-level documentation, issues, and research |

## 🚀 Quick Start

### For Users

1. Choose the module you need (Classification, Scoring, etc.)
2. Navigate to its directory
3. Follow the module-specific README for installation and usage

### For Developers

1. Clone this repository:
   ```bash
   git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
   cd PrismQ.IdeaInspiration
   ```

2. Set up the module you want to work with:
   ```bash
   cd Classification  # or ConfigLoad, Model, Scoring, Sources
   # Follow module-specific setup instructions
   ```

## 💻 Target Platform

All modules are optimized for:
- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## 📊 Module Integration

```
┌─────────────────────────────────────────────────┐
│              PrismQ.IdeaInspiration             │
└─────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
    ┌───▼───┐    ┌───▼────┐   ┌───▼──────┐
    │Sources│───▶│  Model │◀──│ConfigLoad│
    └───┬───┘    └───┬────┘   └──────────┘
        │            │
        │      ┌─────┴──────┐
        │      │            │
    ┌───▼──────▼─┐   ┌─────▼────────┐
    │Classification│   │   Scoring    │
    └──────────────┘   └──────────────┘
```

### Typical Workflow

1. **Sources** → Collect content from various platforms
2. **Model** → Transform into unified IdeaInspiration structure
3. **Classification** → Categorize and detect story potential
4. **Scoring** → Evaluate quality and engagement metrics
5. **ConfigLoad** → Manage configuration across all modules

## 📚 Documentation

### Architecture & Design
- **[System Architecture](./_meta/docs/ARCHITECTURE.md)** - Complete system architecture with diagrams
- **[Web Client Architecture](./Client/docs/ARCHITECTURE.md)** - Detailed Client architecture
- **[Scoring Module Architecture](./Scoring/_meta/doc/ARCHITECTURE.md)** - Scoring module details
- **[Contributing](./_meta/docs/CONTRIBUTING.md)** - How to contribute to this project

### Planning & Development
- **[Project Roadmap](./_meta/issues/ROADMAP.md)** - Future development plans
- **[Known Issues](./_meta/issues/KNOWN_ISSUES.md)** - Current limitations and bugs
- **[Research](./_meta/research/)** - Experimental work and investigations

## 🔗 Related Projects

- **[PrismQ.IdeaCollector](https://github.com/Nomoos/PrismQ.IdeaCollector)** - CLI tool for idea collection
- **[StoryGenerator](https://github.com/Nomoos/StoryGenerator)** - Automated story and video generation
- **[PrismQ.RepositoryTemplate](https://github.com/Nomoos/PrismQ.RepositoryTemplate)** - Base template for PrismQ modules

## 📄 License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

## 💬 Support

- **Issues**: Use the [GitHub issue tracker](https://github.com/Nomoos/PrismQ.IdeaInspiration/issues)
- **Documentation**: Check individual module READMEs
- **Project Tracking**: See [_meta/issues](./_meta/issues/) for planning and roadmap

---

**Part of the PrismQ Ecosystem** - AI-powered content generation platform
