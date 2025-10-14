# PrismQ.RepositoryTemplate

A comprehensive template repository for creating new PrismQ modules - specialized AI-powered content generation applications.

## 🎯 Purpose

This template provides a standardized structure for developing PrismQ modules that are part of the AI-powered content generation ecosystem. PrismQ modules work together to automate various stages of content creation, from idea generation to final video production.

### Related PrismQ Projects
- **PrismQ.IdeaInspiration.Scoring** - Score idea inspirations
- **PrismQ.IdeaInspiration.Classification** - Classify idea inspirations
- **[PrismQ.IdeaInspiration.Sources](https://github.com/Nomoos/PrismQ.IdeaInspiration.Sources)** - Gather idea inspirations from various sources
- **[StoryGenerator](https://github.com/Nomoos/StoryGenerator)** - Automated story and video generation pipeline
- **Other PrismQ Modules** - Specialized tools for content generation

## 💻 Target Platform

This template is optimized for:
- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## 📁 Repository Structure

```
PrismQ.RepositoryTemplate/
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
│   ├── __init__.py            # Package initialization
│   ├── main.py                # Main entry point
│   └── config.py              # Configuration management
├── tests/                      # Test suite
│   ├── __init__.py            # Test package initialization
│   └── test_config.py         # Configuration tests
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

1. Clone this template repository:
   ```batch
   git clone https://github.com/Nomoos/PrismQ.RepositoryTemplate.git YourModuleName
   cd YourModuleName
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

## 🛠️ Development

### Creating Your Module

1. **Rename the project**: Update references to "PrismQ.RepositoryTemplate" with your module name
2. **Define purpose**: Update README.md with your module's specific purpose
3. **Configure dependencies**: Edit `requirements.txt` and `pyproject.toml`
4. **Implement functionality**: Add your code in the `src/` directory
5. **Write tests**: Add tests in the `tests/` directory
6. **Update documentation**: Keep docs up-to-date

### Project Structure Guidelines

- **src/** - Keep your main source code here, organized by functionality
- **tests/** - Mirror the `src/` structure in your tests
- **docs/** - Add detailed documentation for users and developers
- **scripts/** - Add utility scripts for common tasks
- **issues/** - Track issues and roadmap items

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

## 📚 Documentation

- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute to the project
- **[Documentation Overview](docs/README.md)** - Documentation structure and guidelines
- **[Known Issues](issues/KNOWN_ISSUES.md)** - Current known issues
- **[Roadmap](issues/ROADMAP.md)** - Future development plans

## 🤝 Contributing

This is a proprietary template repository. For contribution guidelines, see [CONTRIBUTING.md](docs/CONTRIBUTING.md).

## 📋 Features

### Included in Template

- ✅ Python project structure with best practices
- ✅ Configuration management with environment variables
- ✅ Test framework setup (pytest)
- ✅ Documentation structure
- ✅ Issue tracking system
- ✅ Setup and quickstart scripts
- ✅ GitHub templates (issues, PRs)
- ✅ Copilot development guidelines
- ✅ Optimized for Windows + RTX 5090

### What You Need to Add

- ⬜ Your module-specific functionality
- ⬜ Module-specific dependencies
- ⬜ Comprehensive tests
- ⬜ Detailed documentation
- ⬜ Usage examples

## 🔧 Configuration

The template uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```bash
# Application Settings
APP_NAME=PrismQ.YourModule
APP_ENV=development
DEBUG=true

# Python Configuration
# Specify which Python executable to use for virtual environments
PYTHON_EXECUTABLE=python  # or python3, python3.10, C:\Python310\python.exe, etc.

# Add your API keys
OPENAI_API_KEY=your_key_here

# Configure paths
INPUT_DIR=./input
OUTPUT_DIR=./output
```

### Python Executable Configuration

The `PYTHON_EXECUTABLE` setting allows you to specify which Python interpreter to use when creating virtual environments. This is particularly useful when:

- You have multiple Python versions installed
- Working across different subprojects with different Python requirements
- Using specific Python installations with custom configurations

**Examples:**
- Windows: `PYTHON_EXECUTABLE=python` or `PYTHON_EXECUTABLE=C:\Python310\python.exe`
- Linux: `PYTHON_EXECUTABLE=python3` or `PYTHON_EXECUTABLE=/usr/bin/python3.11`

The setup scripts (`scripts/setup.bat` and `scripts/setup.sh`) will automatically use this configuration when creating the virtual environment.

## 🚨 Hardware Requirements

This template is designed for high-performance AI workloads:

- **GPU**: NVIDIA RTX 5090 (32GB VRAM) for AI model inference/training
- **CPU**: AMD Ryzen (multi-core) for preprocessing and orchestration
- **RAM**: 64GB for large dataset handling
- **Storage**: SSD recommended for fast I/O

## 📄 License

This repository is proprietary software. See [LICENSE](LICENSE) file for details.

**All Rights Reserved** - Copyright (c) 2025 PrismQ

## 🔗 Related Resources

- [PrismQ.IdeaCollector](https://github.com/Nomoos/PrismQ.IdeaCollector) - Idea generation module
- [StoryGenerator](https://github.com/Nomoos/StoryGenerator) - Story generation pipeline

## 💬 Support

For questions, issues, or feature requests:
1. Check [Known Issues](issues/KNOWN_ISSUES.md)
2. Review [Documentation](docs/)
3. Open a new issue using the appropriate template

## 🎨 Template Usage

To use this template for a new PrismQ module:

1. Click "Use this template" on GitHub
2. Clone your new repository
3. Run the setup script
4. Replace template content with your module specifics
5. Start building your PrismQ module!

---

**Note**: This is a template repository. Replace placeholder content with your actual module implementation.
