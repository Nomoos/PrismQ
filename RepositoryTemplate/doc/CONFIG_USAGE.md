# Configuration System Usage

This document explains how to use the configuration system in the PrismQ module template.

## Overview

The configuration system automatically manages `.env` files and working directories for PrismQ modules. It uses `python-dotenv` for robust environment variable loading and provides interactive prompting for missing values.

## Key Features

### 1. Automatic Working Directory Detection

The configuration system automatically detects the topmost `PrismQ` directory and creates a `PrismQ_WD` (Working Directory) sibling folder where the `.env` file is stored.

```python
from src.config import Config

# Create config instance
config = Config()

# Access working directory
print(f"Working directory: {config.working_directory}")
print(f".env file: {config.env_file}")
```

**Directory Structure:**
```
/path/to/
├── PrismQ/
│   ├── module1/
│   ├── module2/
│   └── ...
└── PrismQ_WD/          # Auto-created
    └── .env            # Shared config
```

### 2. Environment Variable Loading

The system uses `python-dotenv` to load environment variables from the `.env` file:

- Automatically loads `.env` on initialization
- Creates `.env` if it doesn't exist
- Stores the working directory in `.env` automatically

### 3. Interactive Prompting

The config system can interactively prompt for missing values:

```python
from src.config import Config

# Non-interactive mode (default values only)
config = Config(interactive=False)

# Interactive mode (will prompt for missing values)
config = Config(interactive=True)

# Use _get_or_prompt to get values
api_key = config._get_or_prompt(
    key="OPENAI_API_KEY",
    description="Enter your OpenAI API key",
    default="",
    required=True  # Will prompt if missing
)
```

### 4. Built-in Configuration

The following configuration values are automatically loaded:

```python
config.app_name           # Application name (APP_NAME)
config.app_env            # Environment (APP_ENV: development/production)
config.debug              # Debug mode (DEBUG: true/false)
config.log_level          # Logging level (LOG_LEVEL: DEBUG/INFO/WARNING/ERROR)
config.python_executable  # Python executable (PYTHON_EXECUTABLE)
config.input_dir          # Input directory path (INPUT_DIR)
config.output_dir         # Output directory path (OUTPUT_DIR)
config.cache_dir          # Cache directory path (CACHE_DIR)
```

### 5. API Key Management

Retrieve API keys for various services:

```python
from src.config import Config

config = Config()

# Get API keys
openai_key = config.get_api_key("openai")      # OPENAI_API_KEY
anthropic_key = config.get_api_key("anthropic") # ANTHROPIC_API_KEY
```

## Working Directory Behavior

### Case 1: No PrismQ Directory

If no directory named exactly `PrismQ` is found in the parent chain, the current directory is used:

```
/some/path/project/
└── .env  # Created here
```

### Case 2: PrismQ Directory Found

If a directory named exactly `PrismQ` is found, a sibling `PrismQ_WD` directory is created:

```
/parent/
├── PrismQ/
│   └── MyModule/
└── PrismQ_WD/    # Auto-created
    └── .env      # Shared across all modules
```

### Case 3: Custom .env Path

You can specify a custom `.env` file location:

```python
config = Config(env_file="/custom/path/.env")
# Working directory will be /custom/path
```

## Example Usage

### Basic Setup

```python
from src.config import Config

# Initialize config
config = Config(interactive=False)

# Access configuration
print(f"App: {config.app_name}")
print(f"Debug: {config.debug}")
print(f"Log Level: {config.log_level}")

# Create directories (automatically done)
config.input_dir.mkdir(parents=True, exist_ok=True)
```

### Loading Custom Configuration

```python
import os
from src.config import Config

# Set environment variables before creating config
os.environ["APP_NAME"] = "MyPrismQModule"
os.environ["DEBUG"] = "true"
os.environ["LOG_LEVEL"] = "DEBUG"

config = Config(interactive=False)
```

### Using .env File

Create a `.env` file in your working directory:

```bash
# .env
APP_NAME=PrismQ.MyModule
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Paths
INPUT_DIR=./data/input
OUTPUT_DIR=./data/output
CACHE_DIR=./cache

# Python Configuration
PYTHON_EXECUTABLE=python3.11
```

Then use it in your code:

```python
from src.config import Config

config = Config()
# All values from .env are now loaded
```

## Advanced Usage

### Extending Config Class

You can extend the `Config` class for module-specific configuration:

```python
from pathlib import Path
from src.config import Config

class MyModuleConfig(Config):
    def __init__(self, env_file=None, interactive=True):
        super().__init__(env_file, interactive)
        
        # Load module-specific config
        self.database_path = self._get_or_prompt(
            "DATABASE_PATH",
            "Database file path",
            "db.sqlite",
            required=False
        )
        
        # Make paths absolute
        if not Path(self.database_path).is_absolute():
            self.database_path = str(
                Path(self.working_directory) / self.database_path
            )
```

### Programmatically Updating .env

```python
from dotenv import set_key
from src.config import Config

config = Config()

# Update a value in .env
set_key(config.env_file, "NEW_SETTING", "value")

# Reload to pick up changes
from dotenv import load_dotenv
load_dotenv(config.env_file, override=True)
```

## Best Practices

1. **Use Non-Interactive Mode in Production**: Set `interactive=False` to avoid prompts
2. **Store Secrets in .env**: Never commit `.env` to version control (use `.env.example`)
3. **Use Absolute Paths**: Convert relative paths to absolute based on `working_directory`
4. **Validate Configuration**: Check required values are present before using them
5. **Document Custom Config**: If extending `Config`, document new fields in `.env.example`

## Troubleshooting

### .env File Not Found

The `.env` file is automatically created if it doesn't exist. Check `config.env_file` to see where it should be located.

### Working Directory Not Expected

Use `config.working_directory` to see where the system detected the working directory. If it's not correct, you can specify a custom `env_file` path.

### Environment Variables Not Loading

Ensure your `.env` file has the correct format (`KEY=value`, no spaces around `=`). Comments start with `#`.

## Migration from Manual .env Loading

If you were previously using manual `.env` loading:

**Before (simplified example - not production code):**
```python
# Old manual loading (simplified - lacks error handling)
# This is a basic example and should not be used in production
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key] = value
```

**After:**
```python
# New config system with robust error handling
from src.config import Config
config = Config()
# .env is automatically loaded via python-dotenv with proper error handling
```

**Note**: The manual example above is simplified and lacks proper error handling for edge cases. The new `python-dotenv` based system handles these cases correctly.

## Reference

- [python-dotenv documentation](https://pypi.org/project/python-dotenv/)
- [PrismQ Module Template](https://github.com/Nomoos/PrismQ.RepositoryTemplate)
- [Reference Implementation](https://github.com/Nomoos/PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeShortsSource)
