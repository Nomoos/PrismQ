# PrismQ.IdeaInspiration

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
git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
cd PrismQ.IdeaInspiration

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
