# Configuration Guide

This guide explains how PrismQ modules manage configuration settings.

## Overview

PrismQ modules use a **local .env file** that is automatically stored in the nearest parent directory with "PrismQ" in its name. This allows all PrismQ packages in the same directory tree to share the same configuration, providing a unified setup experience across the PrismQ ecosystem.

## Key Features

### 1. Automatic Working Directory Detection

When you run a PrismQ module, it automatically:

1. **Searches for PrismQ project directory** - Finds the nearest parent directory with "PrismQ" in its name
2. **Creates a .env file at project root** - Automatically creates `.env` in the PrismQ project directory
3. **Stores the working directory** - Saves `WORKING_DIRECTORY` in the `.env` file for reference
4. **Remembers your settings** - Configuration is persisted across multiple runs

### 2. PrismQ Directory Search

The module searches upward from your current directory to find the nearest parent directory that contains "PrismQ" in its name. This ensures that:

- All subdirectories within a PrismQ project share the same configuration
- You can run commands from anywhere within your project structure
- Configuration and data files are centralized at the project root

**Example directory structure:**
```
MyPrismQProject/              ← .env created here
├── .env
├── db.s3db
├── scripts/
│   └── processing/
│       └── run_here/         ← Run from here
└── data/
```

If no directory with "PrismQ" in the name is found, the module falls back to using the current directory.

### 3. Interactive and Non-Interactive Modes

- **Interactive mode (default)** - Prompts for missing values when needed
- **Non-interactive mode** - Uses defaults, no prompts (useful for automation and CI/CD)

## Configuration Options

### Automatically Managed Settings

| Setting | Description |
|---------|-------------|
| `WORKING_DIRECTORY` | Your working directory (automatically detected and stored) |

### Optional Settings

Configure these in your `.env` file or they'll use defaults:

| Setting | Default | Description |
|---------|---------|-------------|
| `APP_NAME` | `PrismQ.ModuleName` | Application name |
| `APP_ENV` | `development` | Environment (development, production, testing) |
| `DEBUG` | `true` | Debug mode flag |
| `LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `PYTHON_EXECUTABLE` | `python` | Python executable path |
| `INPUT_DIR` | `./input` | Input directory path |
| `OUTPUT_DIR` | `./output` | Output directory path |
| `CACHE_DIR` | `./cache` | Cache directory path |

### API Keys

Add API keys as needed:
```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

## Usage Examples

### Example 1: Standard PrismQ Project

```bash
# Directory structure
/projects/
  └── PrismQ.MyModule/              ← .env created here
      ├── .env
      ├── scripts/
      └── src/

# Run from any subdirectory
cd /projects/PrismQ.MyModule/scripts
python ../src/main.py
# Uses /projects/PrismQ.MyModule/.env
```

### Example 2: Nested PrismQ Structure

```bash
# Directory structure
/projects/
  └── PrismQ.Ecosystem/                 ← .env created here
      ├── .env
      ├── PrismQ.Module1/
      ├── PrismQ.Module2/
      └── PrismQ.Module3/

# All three modules share the same .env file
# Run from any module subdirectory
cd /projects/PrismQ.Ecosystem/PrismQ.Module1
python src/main.py
# Uses /projects/PrismQ.Ecosystem/.env
```

### Example 3: Multiple Independent Projects

```bash
# Project A
cd /projects/PrismQProjectA/scripts
python ../src/main.py
# Uses /projects/PrismQProjectA/.env

# Project B
cd /projects/PrismQProjectB/data/processing
python ../../src/main.py
# Uses /projects/PrismQProjectB/.env
```

Each PrismQ project maintains completely independent configuration.

## Configuration File Format

The `.env` file uses simple KEY=VALUE format:

```env
# Working Directory (automatically managed)
WORKING_DIRECTORY=/path/to/PrismQProject

# Application Settings
APP_NAME=PrismQ.MyModule
APP_ENV=development
DEBUG=true

# Logging Configuration
LOG_LEVEL=INFO

# Python Configuration
PYTHON_EXECUTABLE=python

# API Keys
OPENAI_API_KEY=your_api_key_here

# Paths
INPUT_DIR=./input
OUTPUT_DIR=./output
CACHE_DIR=./cache
```

## Python API

### Using Config in Your Code

```python
from src.config import Config, config

# Use the global config instance
print(config.app_name)
print(config.working_directory)
print(config.log_level)

# Or create a custom config instance
custom_config = Config(env_file="/custom/path/.env", interactive=False)
```

### Config Class

```python
class Config:
    """Configuration class for the PrismQ module."""
    
    def __init__(self, env_file: Optional[str] = None, interactive: bool = True):
        """
        Args:
            env_file: Path to .env file (default: .env in nearest PrismQ directory)
            interactive: Whether to prompt for missing values (default: True)
        """
```

### Properties

- `working_directory: str` - The detected working directory
- `env_file: str` - Path to the .env file being used
- `app_name: str` - Application name
- `app_env: str` - Environment (development/production/testing)
- `debug: bool` - Debug mode flag
- `log_level: str` - Logging level
- `python_executable: str` - Python executable path
- `input_dir: Path` - Input directory path
- `output_dir: Path` - Output directory path
- `cache_dir: Path` - Cache directory path

### Methods

```python
def get_api_key(self, service: str) -> str | None:
    """Get API key for a service.
    
    Args:
        service: Name of the service (e.g., 'openai', 'anthropic')
        
    Returns:
        API key or None if not found
    """
```

## Database Setup (Model Repositories)

For repositories that are Model type (contain database definitions), use the provided setup scripts:

### Windows

```batch
scripts\setup_db.bat
```

### Linux/macOS

```bash
./scripts/setup_db.sh
```

These scripts will:
1. Detect the nearest PrismQ directory
2. Create or use existing .env configuration
3. Create the database in the working directory
4. Remember settings for future use

## Best Practices

### 1. Use PrismQ in Project Names

Create project directories with "PrismQ" in the name for automatic configuration management:

```bash
mkdir MyPrismQTrendingIdeas
cd MyPrismQTrendingIdeas
# Configuration will be stored here
```

### 2. Version Control

**DO NOT** commit `.env` files to version control if they contain sensitive data like API keys.

Add to `.gitignore`:
```
.env
*.db
*.s3db
```

### 3. Use .env.example as Template

Copy the example file to create your own:

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Environment Variables Override

Environment variables take precedence over `.env` file values:

```bash
APP_ENV=production python src/main.py
```

## Troubleshooting

### Problem: Configuration not persisting

**Solution:** Check file permissions on the `.env` file and directory.

```bash
ls -la .env
# Should be readable and writable by your user
```

### Problem: Wrong working directory detected

**Solution:** Check which directory is being used:

```python
from src.config import Config
config = Config(interactive=False)
print(f'Env file: {config.env_file}')
print(f'Working directory: {config.working_directory}')
```

### Problem: Want to reset configuration

**Solution:** Simply delete the `.env` file and run again:

```bash
rm .env
python src/main.py
```

### Problem: Need custom .env location

**Solution:** Override with environment variable:

```bash
export PRISMQ_WORKING_DIR=/custom/path
python src/main.py
```

Or specify directly in code:

```python
config = Config(env_file="/custom/path/.env")
```

## Environment Variables

The configuration system respects these environment variables:

- `PRISMQ_WORKING_DIR` - Override working directory detection
- All settings from `.env` can be overridden via environment variables

## Advanced Usage

### Programmatic Configuration

```python
from src.config import Config

# Load config from specific location
config = Config(env_file="/path/to/.env", interactive=False)

# Access configuration
print(f"App Name: {config.app_name}")
print(f"Working Dir: {config.working_directory}")
print(f"Debug: {config.debug}")

# Get API keys
openai_key = config.get_api_key("openai")
if openai_key:
    # Use API key
    pass
```

### Non-Interactive Mode

Use non-interactive mode for automation:

```python
config = Config(interactive=False)
# No prompts will be shown, defaults will be used
```

## Integration with PrismQ Modules

The configuration system is designed to work across all PrismQ modules:

- **PrismQ.IdeaInspiration.Model** - Data models
- **PrismQ.IdeaInspiration.Scoring** - Content scoring
- **PrismQ.IdeaInspiration.Classification** - Content classification
- **PrismQ.IdeaInspiration.Builder** - Model construction
- **PrismQ.IdeaInspiration.Sources** - Content sources
- **Any custom PrismQ module** - Your own modules

Each module can maintain its own configuration while sharing the working directory.

## Security Considerations

1. **Never commit sensitive data** - Add `.env` to `.gitignore` if it contains secrets
2. **Use environment variables for secrets** - Set via environment variables in production
3. **File permissions** - Ensure `.env` has appropriate read/write permissions (0600 recommended)
4. **No secrets in code** - Always use Config class to retrieve sensitive values

## See Also

- [README.md](../README.md) - Main documentation
- [.env.example](../.env.example) - Example configuration file
- [pyproject.toml](../pyproject.toml) - Project configuration

---

**Part of the PrismQ Ecosystem** - Unified content processing and generation platform
