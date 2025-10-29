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

**Note**: Linux shell scripts (`.sh`) are provided for GitHub Copilot Agent usage only.

## 📁 Repository Structure

```
PrismQ.RepositoryTemplate/
├── .github/                    # GitHub configuration
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   ├── copilot-instructions.md # Copilot development guidelines
│   └── PULL_REQUEST_TEMPLATE.md
├── doc/                        # Sphinx API documentation
├── issues/                     # Issue tracking
│   ├── new/                   # New issues
│   ├── wip/                   # Work in progress
│   └── done/                  # Completed issues
├── scripts/                    # Utility scripts
│   ├── setup.bat / setup.sh    # Setup scripts (Windows/Linux)
│   └── quickstart.bat / quickstart.sh  # Quick start scripts
├── src/                        # Core Python package
│   ├── __init__.py            # Package initialization
│   ├── main.py                # Main entry point
│   ├── config.py              # Configuration management
│   └── logging_config.py      # Logging infrastructure
├── tests/                      # Test suite
│   ├── __init__.py            # Test package initialization
│   └── test_*.py              # Test files
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── LICENSE                    # Proprietary license
├── pyproject.toml             # Python project configuration
├── README.md                  # This file
└── requirements.txt           # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.14 or higher
- Windows OS (recommended)
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

   The configuration system automatically manages `.env` files and working directories. See [Configuration System Usage](doc/CONFIG_USAGE.md) for details.

4. Run the module:
   ```batch
   scripts\quickstart.bat
   ```

> **Note for GitHub Copilot Agents**: Linux shell scripts (`.sh`) are available in the `scripts/` directory for automated agent usage.

## 🛠️ Development

### Creating Your Module

1. **Rename the project**: Update references to "PrismQ.RepositoryTemplate" with your module name
2. **Define purpose**: Update README.md with your module's specific purpose
3. **Configure dependencies**: Edit `requirements.txt` and `pyproject.toml`
4. **Implement functionality**: Add your code in the `src/` directory
5. **Write tests**: Add tests in the `tests/` directory
6. **Update documentation**: Keep docs up-to-date

### Project Structure Guidelines

The repository follows a clear structure:

- **src/** - Core Python package implementation
  - Configuration management
  - Logging infrastructure
  - Core utilities and common functionality
  - Package initialization
  - Main entry point and business logic

- **tests/** - Test suite mirroring `src/` structure

- **doc/** - Detailed documentation for users and developers

- **scripts/** - Utility scripts for common tasks

- **issues/** - Track issues and roadmap items

### Development Workflow

The template includes utility scripts for common development tasks:

```batch
# Format code (PEP 8 compliance)
scripts\format.bat

# Run linting and type checking
scripts\lint.bat

# Run tests with coverage
scripts\test.bat

# Generate API documentation
scripts\docs.bat

# Setup database (for Model repositories)
scripts\setup_db.bat
```

> **Note**: Shell script equivalents (`.sh`) are available for GitHub Copilot Agent automation.

### Database Setup (Model Repositories)

If your repository is a Model type (contains database definitions), use the provided database setup scripts:

**Windows:**
```batch
scripts\setup_db.bat
```

**Linux/macOS:**
```bash
./scripts/setup_db.sh
```

These scripts will:
- Automatically detect the nearest PrismQ directory
- Create or use existing `.env` configuration
- Create the database in the working directory
- Remember settings for future use

Alternatively, activate the virtual environment and use commands directly:

```batch
# Activate virtual environment first
venv\Scripts\activate

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Build documentation
cd docs\sphinx
sphinx-build -b html source build\html
```

## 🤝 Contributing

This is a proprietary template repository. When using this template for your project:
1. Add a CONTRIBUTING.md file in the docs/ directory with your project's contribution guidelines
2. Define coding standards, testing requirements, and review processes
3. Update this section with a link to your CONTRIBUTING.md file

## ⚙️ Configuration System

The template includes a robust configuration system with automatic `.env` loading and working directory management:

- **Automatic .env Loading**: Uses `python-dotenv` for reliable environment variable loading
- **Smart Working Directory**: Automatically detects the topmost `PrismQ` directory and creates a `PrismQ_WD` sibling for shared configuration
- **Interactive Prompting**: Can prompt for missing configuration values in interactive mode
- **Built-in Configuration**: Pre-configured support for common settings (app name, debug mode, log level, paths, etc.)

**Quick Example:**
```python
from src.config import Config

# Initialize configuration (auto-loads .env)
config = Config()

print(f"Working directory: {config.working_directory}")
print(f"App name: {config.app_name}")
print(f"Debug mode: {config.debug}")
```

For detailed documentation, see [Configuration System Usage](doc/CONFIG_USAGE.md).

## 📋 Features

### Included in Template

- ✅ Python project structure with best practices
- ✅ PEP-compliant configuration (PEP 517/518/621/660)
- ✅ Type checking with MyPy (PEP 484/526/544/561)
- ✅ Code quality with Ruff (PEP 8/257)
- ✅ UTF-8 encoding standard (`.gitattributes` and `.editorconfig`)
- ✅ SOLID principles documentation and guidelines
- ✅ AI-assisted coding best practices (GitHub Copilot guidelines)
- ✅ Robust configuration system with `python-dotenv` integration
- ✅ Smart working directory detection - finds topmost PrismQ directory
- ✅ Shared `.env` files across PrismQ modules via `PrismQ_WD` directory
- ✅ Interactive prompting for missing configuration values
- ✅ Automatic `.env` management - no manual file handling needed
- ✅ Comprehensive logging system with module identification and environment detection
- ✅ Test framework setup (pytest with coverage)
- ✅ Documentation system with Sphinx (auto-generated API docs)
- ✅ Comprehensive documentation structure
- ✅ Issue tracking system
- ✅ Development scripts (setup, lint, format, test, docs, setup_db for Models)
- ✅ GitHub templates (issues, PRs)
- ✅ Copilot development guidelines
- ✅ Optimized for Windows + RTX 5090

### What You Need to Add

- ⬜ Your module-specific functionality
- ⬜ Module-specific dependencies
- ⬜ Comprehensive tests
- ⬜ Detailed documentation
- ⬜ Usage examples

## 📊 Logging Features

The template includes a comprehensive logging system designed for better reporting and easier recognition of where the application is running and which module is being used.

### Key Logging Features

- **Module Identification**: Automatically logs module name, version, and location at startup
- **Environment Detection**: Logs OS, Python version, architecture, and hardware information
- **Hardware Awareness**: Optional detailed CPU, RAM, and GPU information (with psutil)
- **Dual Output**: Supports both console and file logging simultaneously
- **Structured Format**: Includes timestamp, module name, log level, file location, and line number
- **Flexible Configuration**: Control log level and file output via environment variables
- **Production Ready**: Easy to switch between development and production logging modes

### Example Output

```
2025-10-16 16:08:11 - PrismQ.MyModule - INFO - [logging_config.py:109] - Module Information:
2025-10-16 16:08:11 - PrismQ.MyModule - INFO - [logging_config.py:110] -   Name: PrismQ.MyModule
2025-10-16 16:08:11 - PrismQ.MyModule - INFO - [logging_config.py:111] -   Version: 1.0.0
2025-10-16 16:08:11 - PrismQ.MyModule - INFO - [logging_config.py:116] -   Operating System: Windows 11
2025-10-16 16:08:11 - PrismQ.MyModule - INFO - [logging_config.py:119] -   Processor: AMD Ryzen 9 7950X
2025-10-16 16:08:11 - PrismQ.MyModule - INFO - [logging_config.py:148] -   CPU: 16 physical cores, 32 logical cores
2025-10-16 16:08:11 - PrismQ.MyModule - INFO - [logging_config.py:155] -   RAM: 64.00 GB total
2025-10-16 16:08:11 - PrismQ.MyModule - INFO - [logging_config.py:171] -   GPU: NVIDIA GeForce RTX 5090, 32768 MiB
```

## 🔧 Configuration

The template uses a smart configuration system that automatically manages `.env` files:

### Automatic Configuration Management

- **PrismQ Directory Detection**: Automatically finds the nearest parent directory with "PrismQ" in its name
- **Shared Configuration**: All PrismQ modules in the same directory tree share the same `.env` file
- **Automatic Creation**: Creates `.env` file at the PrismQ project root if it doesn't exist
- **Working Directory Storage**: Remembers your working directory in the `.env` file
- **Interactive & Non-Interactive**: Works in both manual and CI/CD environments

### Example Directory Structure

```
MyPrismQProject/              ← .env stored here
├── .env
├── PrismQ.Module1/
│   └── src/
├── PrismQ.Module2/
│   └── src/
└── scripts/
```

All modules share the same configuration from `MyPrismQProject/.env`.

### Configuration Options

Copy `.env.example` to `.env` and customize:

```bash
# Working Directory (automatically managed)
WORKING_DIRECTORY=

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
- `PYTHON_EXECUTABLE=python` (default)
- `PYTHON_EXECUTABLE=C:\Python310\python.exe` (specific installation)

The setup script (`scripts/setup.bat`) will automatically use this configuration when creating the virtual environment.

### Advanced Configuration

For detailed configuration options and advanced usage, see the [Configuration Guide](doc/CONFIGURATION.md).

### UTF-8 Encoding Standard

This repository enforces UTF-8 encoding as the standard across all text files for maximum cross-platform compatibility. This is configured through:

- **`.gitattributes`**: Ensures Git handles text files with UTF-8 encoding and proper line endings
  - Linux/Mac files (`.py`, `.sh`, etc.): UTF-8 with LF line endings
  - Windows files (`.bat`, `.cmd`, `.ps1`): UTF-8 with CRLF line endings
  - Binary files are explicitly marked to prevent encoding issues

- **`.editorconfig`**: Ensures all editors and IDEs use UTF-8 encoding
  - Supported by Visual Studio Code, PyCharm, IntelliJ IDEA, Sublime Text, and many others
  - Automatically applies settings when you open the project

**Benefits:**
- ✅ Consistent encoding across all platforms (Windows, Linux, Mac)
- ✅ Proper handling of Unicode characters and emoji
- ✅ Prevents encoding-related bugs in version control
- ✅ Industry standard for Git, GitHub, and modern web applications

No additional configuration is needed - the files are automatically applied by Git and modern editors.

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

For questions, issues, or feature requests, open a new issue using the appropriate template.

## 🎨 Template Usage

To use this template for a new PrismQ module:

1. Click "Use this template" on GitHub
2. Clone your new repository
3. Run the setup script
4. Replace template content with your module specifics
5. Start building your PrismQ module!

---

**Note**: This is a template repository. Replace placeholder content with your actual module implementation.
