# src - PrismQ Environment Configuration Module

**Centralized environment and configuration management for all PrismQ modules.**

## Overview

src provides a standardized way to load and manage environment variables and configuration across all PrismQ modules (T, A, V, P, M, Client). It ensures consistent working directory structure and .env file management.

## Key Features

- **Standardized Working Directory**: 
  - Windows: `C:\PrismQ` (permanent MVP location)
  - Unix-like: `~/PrismQ` (user's home directory)
  - Override via `PRISMQ_WORKING_DIRECTORY` environment variable
- **Centralized .env File Management**: Single .env file for all configuration
- **Cross-Platform Path Handling**: Works on Windows, macOS, and Linux
- **Interactive Configuration**: Optional prompts for missing values
- **Module Directory Structure**: Ensures proper directory layout for T, A, V, P, M modules

## Installation

src requires the `python-dotenv` package:

```bash
pip install python-dotenv
```

## Usage

### Basic Usage

```python
from src import Config

# Create config with default settings
config = Config()

print(f"Working Directory: {config.working_directory}")
print(f"Database URL: {config.database_url}")
print(f"YouTube API Key: {config.youtube_api_key}")
```

### Non-Interactive Mode

```python
from src import Config

# For automated scripts or testing
config = Config(interactive=False)
```

### Custom .env File Location

```python
from src import Config

# Use a specific .env file
config = Config(env_file="/path/to/custom/.env")
```

### Module Directory Management

```python
from src import Config

config = Config()

# Get module directory path
text_dir = config.get_module_directory("T", content_id="12345")
# Returns: C:\PrismQ\T\12345 (on Windows)

# Ensure module structure exists
config.ensure_module_structure("T")
```

## Working Directory Structure

src ensures the following directory structure within the working directory:

```
C:\PrismQ\                              (Windows) or ~/PrismQ (Unix-like)
├── .env                                (Configuration file)
├── db.s3db                             (Default database)
├── T/                                  (Text module)
│   └── {id}/
│       ├── {Platform}/
│       └── Text/
├── A/                                  (Audio module)
│   └── {id}/
│       ├── {Platform}/
│       └── Audio/
├── V/                                  (Video module)
│   └── {id}/
│       ├── {Platform}/
│       └── Video/
├── P/                                  (Publishing module)
│   └── {Year}/{Month}/{day-range}/{day}/{hour}/{id}/{platform}/
└── M/                                  (Metrics module)
    └── {Year}/{Month}/{day-range}/{day}/{hour}/{id}/Metrics/{platform}/
```

## Environment Variables

src manages the following environment variables in the .env file:

| Variable | Description | Default |
|----------|-------------|---------|
| `WORKING_DIRECTORY` | Working directory path | `C:\PrismQ` (Windows) or `~/PrismQ` (Unix) |
| `DATABASE_URL` | Database connection URL | `sqlite:///C:\PrismQ\db.s3db` |
| `YOUTUBE_API_KEY` | YouTube API key (optional) | None |
| `YOUTUBE_CHANNEL_URL` | YouTube channel URL (optional) | None |
| `PRISMQ_WORKING_DIRECTORY` | Override for working directory | None |

## Configuration Class

### Methods

#### `__init__(env_file: Optional[str] = None, interactive: bool = True)`
Initialize configuration with optional custom .env file path and interactive mode.

#### `get_module_directory(module: str, content_id: Optional[str] = None) -> Path`
Get standardized directory path for a specific module (T, A, V, P, M).

#### `ensure_module_structure(module: str) -> None`
Ensure the working directory structure exists for a module.

### Properties

- `working_directory`: Path to the working directory
- `env_file`: Path to the .env file
- `database_url`: Database connection URL
- `database_path`: Path to the database file (for SQLite)
- `youtube_api_key`: YouTube API key
- `youtube_channel_url`: YouTube channel URL
- `youtube_max_results`: Default max results for YouTube queries
- `youtube_channel_max_shorts`: Default max shorts per channel
- `youtube_trending_max_shorts`: Default max trending shorts
- `youtube_keyword_max_shorts`: Default max shorts per keyword

## Migration from Old Config

If you're migrating from the old config system (e.g., from YouTube/Channel/src/core/config.py):

```python
# Old way
from src.core.config import Config

# New way
from src import Config

# The API remains the same!
config = Config()
```

## Testing

Run tests with pytest:

```bash
cd /path/to/PrismQ
pytest src/_meta/tests/
```

## Cross-Platform Support

src automatically handles platform differences:

- **Windows**: Uses `C:\PrismQ` and handles backslashes
- **Unix-like**: Uses `~/PrismQ` (expanded to user home)
- **Path separators**: Automatically handled by `pathlib.Path`

## Override Working Directory

You can override the working directory in several ways:

1. **Environment Variable** (highest priority):
   ```bash
   export PRISMQ_WORKING_DIRECTORY=/custom/path
   ```

2. **Custom .env File**:
   ```python
   config = Config(env_file="/custom/path/.env")
   ```

3. **Default**: Uses `C:\PrismQ` (Windows) or `~/PrismQ` (Unix-like)

## Version History

### 1.0.0 (2025-11-22)
- Initial release
- Centralized configuration management
- Standardized working directory at C:\PrismQ (Windows) / ~/PrismQ (Unix)
- Module directory structure support
- Interactive and non-interactive modes
- Cross-platform path handling
