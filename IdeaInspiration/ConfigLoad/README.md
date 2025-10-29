# ConfigLoad - Centralized Configuration Management for PrismQ

This module provides centralized `.env` file loading and configuration management for all PrismQ modules.

## Overview

ConfigLoad is based on the pattern from `PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeShortsSource` and provides:

- Automatic `.env` file discovery and loading
- Centralized configuration storage in `PrismQ_WD` directory
- Interactive prompting for missing configuration values
- Comprehensive logging with module metadata and system information
- Support for both console and file logging

## Usage

### Basic Configuration Loading

```python
from ConfigLoad import Config

# Initialize configuration (automatically finds PrismQ directory)
config = Config()

# Get configuration values
database_url = config.get("DATABASE_URL", "sqlite:///default.db")

# Get or prompt for values
api_key = config.get_or_prompt(
    "API_KEY",
    "Enter your API key",
    default="",
    required=True
)

# Set configuration values
config.set("MY_CONFIG_KEY", "my_value")
```

### Module Logging

```python
from ConfigLoad import get_module_logger

# Get a configured logger with startup information
logger = get_module_logger(
    module_name="PrismQ.MyModule",
    module_version="1.0.0",
    module_path="/path/to/module"
)

# Use the logger
logger.info("Processing started")
logger.warning("Low memory detected")
logger.error("Operation failed", exc_info=True)
```

### Basic Logging (Simple Use Case)

```python
from ConfigLoad import setup_basic_logging

# Set up basic logging
setup_basic_logging(log_level="INFO")
```

## How It Works

### Directory Discovery

The `Config` class automatically finds the topmost directory named `PrismQ` in the current path hierarchy. It then creates a `PrismQ_WD` (working directory) at the same level to store the `.env` file.

For example:
```
/home/user/
├── PrismQ/                    # Topmost PrismQ directory
│   ├── Module1/
│   └── Module2/
└── PrismQ_WD/                 # Working directory (created automatically)
    └── .env                   # Configuration file
```

### Configuration Storage

All configuration values are stored in the `.env` file in the `PrismQ_WD` directory. This ensures:
- Centralized configuration across all modules
- Persistence of configuration values
- Easy management and backup

### Environment Variable Loading

When you create a `Config` instance, it:
1. Finds the topmost PrismQ directory
2. Creates `PrismQ_WD/.env` if it doesn't exist
3. Loads all environment variables from the `.env` file
4. Makes them available via `os.getenv()` or the `Config` methods

## API Reference

### Config Class

#### `__init__(env_file: Optional[str] = None, interactive: bool = True)`
Initialize configuration.

**Parameters:**
- `env_file`: Path to .env file (default: auto-discovered)
- `interactive`: Whether to prompt for missing values (default: True)

#### `get(key: str, default: Optional[str] = None) -> Optional[str]`
Get a configuration value from environment.

#### `set(key: str, value: str) -> None`
Set a configuration value and save to .env file.

#### `get_or_prompt(key: str, description: str, default: str = "", required: bool = False) -> str`
Get value from environment or prompt user if missing.

### Logging Functions

#### `get_module_logger(module_name: str, module_version: str = "0.1.0", module_path: str | None = None, log_startup: bool = True) -> logging.Logger`
Get a configured logger for a PrismQ module with comprehensive startup information.

#### `setup_basic_logging(log_level: str = "INFO") -> None`
Set up basic logging for simple use cases.

### Utility Functions

#### `find_prismq_directory() -> Optional[Path]`
Find the topmost parent directory with exact name 'PrismQ'.

## Environment Variables

The following environment variables can be configured in your `.env` file:

- `WORKING_DIRECTORY`: Working directory path (automatically set)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FILE`: Path to log file (optional)
- `APP_ENV`: Application environment (default: development)

## Installation

Install the required dependencies:

```bash
pip install -r ConfigLoad/requirements.txt
```

## Testing

Run the test suite:

```bash
pytest ConfigLoad/tests/
```

## Design Principles

This module follows SOLID principles and PrismQ coding standards:

- **Single Responsibility**: Manages .env configuration only
- **DRY**: Centralized configuration management
- **KISS**: Simple, focused API for config operations
- **Type Hints**: All functions have proper type annotations
- **Documentation**: Comprehensive docstrings using Google style
