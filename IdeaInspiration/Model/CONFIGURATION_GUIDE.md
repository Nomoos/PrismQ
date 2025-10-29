# Configuration Management Guide

## Overview

The PrismQ.IdeaInspiration.Model package includes a robust configuration manager that handles `.env` file operations, ensuring that working directory and other configuration values are persisted and never need to be re-entered.

**Important**: The `.env` file is automatically stored in the nearest parent directory with "PrismQ" in its name. This allows all PrismQ packages in the same directory tree to share the same configuration, providing a unified setup experience across the PrismQ ecosystem.

## Key Features

### 1. Working Directory Persistence
- **Never asks for current directory again** - Once configured, the working directory is stored in `.env`
- **Automatic detection** - Checks environment variables and existing `.env` files in PrismQ directories
- **Shared configuration** - All PrismQ modules in the same directory tree share the same `.env` file
- **Smart location** - `.env` file is stored in the nearest parent directory with "PrismQ" in its name

### 2. Configuration Storage
- **`.env` file management** - Automatic creation and updating of configuration files
- **Key-value storage** - Simple string-based configuration values
- **Sorted output** - Configuration keys are alphabetically sorted for readability
- **Comment preservation** - Automatically adds informative headers

### 3. Interactive and Non-Interactive Modes
- **CI/CD friendly** - Automatically detects non-interactive environments
- **User prompts** - In interactive mode, prompts for missing values
- **Default values** - Supports default values for non-interactive scenarios

## Quick Start

### Using in Your Python Code

```python
from config_manager import ConfigManager, setup_working_directory

# Method 1: Setup with automatic working directory detection
config = setup_working_directory("MyApp")

# Method 2: Create ConfigManager with specific directory
config = ConfigManager("/path/to/working/directory")

# Get configuration values
working_dir = config.get('WORKING_DIR')
db_path = config.get('DATABASE_PATH', 'default.db')

# Set configuration values (automatically saves)
config.set('API_KEY', 'your-secret-key')

# Update multiple values at once
config.update({
    'DEBUG': 'true',
    'LOG_LEVEL': 'INFO',
    'MAX_RETRIES': '3'
})

# Check if key exists
if config.has('API_KEY'):
    print("API key is configured")

# Prompt for missing values (interactive only)
api_key = config.prompt_if_missing(
    'API_KEY',
    'Enter your API key',
    default='default-key'
)
```

### Using in Setup Scripts

The configuration manager is integrated into both `setup_db.bat` (Windows) and `setup_db.sh` (Linux/macOS):

**Windows:**
```batch
setup_db.bat
```

**Linux/macOS:**
```bash
./setup_db.sh
```

Both scripts will:
1. Set up working directory configuration (prompts only on first run)
2. Create `.env` file in working directory if it doesn't exist
3. Store configuration values for future use
4. Remember Python executable and working directory

## .env File Location

The configuration manager intelligently locates the `.env` file using the following priority:

1. **PRISMQ_WORKING_DIR environment variable** - If set, `.env` is stored at this location
2. **Nearest PrismQ directory** - Searches up the directory tree for a directory with "PrismQ" in its name (case-insensitive)
3. **Working directory** - Falls back to the configured working directory

### Examples

**Example 1: Standard PrismQ project structure**
```
/projects/
  └── PrismQ.IdeaInspiration.Model/    ← .env stored here
      ├── .env
      ├── config_manager.py
      ├── idea_inspiration.py
      └── tests/
```

**Example 2: Nested PrismQ structure**
```
/projects/
  └── PrismQ.Ecosystem/                 ← .env stored here
      ├── .env
      ├── PrismQ.IdeaInspiration.Model/
      ├── PrismQ.IdeaInspiration.Scoring/
      └── PrismQ.IdeaInspiration.Classification/
```
All three packages share the same `.env` file in `PrismQ.Ecosystem/`.

**Example 3: No PrismQ directory**
```
/projects/
  └── my-project/                       ← .env stored here
      ├── .env
      └── app.py
```
Falls back to the working directory.

## Configuration File Format

The `.env` file uses a simple key=value format:

```env
# PrismQ Module Configuration
# This file stores package-specific configuration
# Auto-generated - do not edit manually unless necessary

API_ENDPOINT=https://api.prismq.com/v1
APP_NAME=PrismQ.IdeaInspiration.Model
DATABASE_PATH=/path/to/working/dir/db.s3db
DEBUG_MODE=false
LOG_LEVEL=INFO
WORKING_DIR=/path/to/working/dir
```

## API Reference

### `ConfigManager` Class

#### Constructor
```python
ConfigManager(working_dir: Optional[str] = None)
```
- `working_dir`: Path to working directory (uses current directory if None)

#### Methods

##### `get(key: str, default: Optional[str] = None) -> Optional[str]`
Get a configuration value with optional default.

##### `set(key: str, value: str) -> None`
Set a configuration value and save to `.env` file.

##### `update(values: Dict[str, str]) -> None`
Update multiple configuration values at once.

##### `has(key: str) -> bool`
Check if a configuration key exists.

##### `ensure_exists() -> None`
Ensure `.env` file exists in working directory.

##### `prompt_if_missing(key: str, prompt_message: str, default: Optional[str] = None) -> str`
Prompt user for a configuration value if not set (interactive mode only).

### Module Functions

#### `find_prismq_directory() -> Optional[Path]`
Find the nearest parent directory with 'PrismQ' in its name (case-insensitive).
Walks up the directory tree from the current directory to find a directory whose name contains 'PrismQ'.

Returns:
- Path to the nearest PrismQ directory or None if not found

#### `get_working_directory_from_env() -> Optional[str]`
Get the working directory from environment variable or `.env` file.
Checks in order:
1. PRISMQ_WORKING_DIR environment variable
2. .env file in nearest PrismQ directory
3. .env file in current directory

#### `setup_working_directory(package_name: str, quiet: bool = False) -> ConfigManager`
Set up working directory configuration for a package.
- `package_name`: Name of the package
- `quiet`: If True, suppress informational messages (for scripting)

The .env file is stored in the nearest parent directory with 'PrismQ' in its name,
allowing configuration to be shared across all PrismQ modules in that directory tree.

## Environment Variables

The configuration manager respects the following environment variables:

- `PRISMQ_WORKING_DIR`: Override working directory detection

## Design Principles

The configuration manager follows these design principles:

1. **Single Responsibility Principle (SRP)**: Only manages configuration, nothing else
2. **DRY (Don't Repeat Yourself)**: Centralized configuration management
3. **KISS (Keep It Simple)**: Simple, focused API
4. **Type Safety**: Full type hints for IDE support
5. **Persistence**: All values automatically saved to `.env`
6. **Flexibility**: Works in both interactive and non-interactive modes

## Testing

The configuration manager includes comprehensive test coverage:

```bash
# Run config manager tests
pytest tests/test_config_manager.py -v

# Run all tests
pytest tests/ -v
```

Test coverage includes:
- Basic operations (get, set, update, has)
- File operations (create, load, save)
- Edge cases (empty files, malformed lines, unicode, spaces in paths)
- Interactive and non-interactive modes
- Persistence across instances

## Examples

See `example_config_usage.py` for a complete working example:

```bash
python example_config_usage.py
```

This example demonstrates:
1. Setting up working directory configuration
2. Storing and retrieving configuration values
3. Checking configuration existence
4. Using default values
5. Configuration persistence across instances

## Best Practices

1. **Use `setup_working_directory()` for initialization** - It handles first-time setup
2. **Store all configuration in `.env`** - Keep configuration centralized
3. **Use meaningful key names** - Use uppercase with underscores (e.g., `DATABASE_PATH`)
4. **Provide default values** - Use `get(key, default)` for optional configuration
5. **Document your configuration** - Add comments to your `.env` file
6. **Never commit `.env` with secrets** - Add `.env` to `.gitignore` if it contains sensitive data

## Troubleshooting

### .env file not found
- The `.env` file is created automatically in the nearest parent directory with "PrismQ" in its name
- If no PrismQ directory is found, it falls back to the working directory
- Check that you have write permissions in the target directory
- Use `config.ensure_exists()` to force creation

### Configuration not persisting
- Verify the `.env` file exists and is writable
- Check for file system permissions issues
- Ensure you're using the same working directory across instances

### Non-interactive mode not working
- The configuration manager detects non-interactive mode via `sys.stdin.isatty()`
- Ensure you provide default values for required configuration
- Check that `PRISMQ_WORKING_DIR` environment variable is set if needed

## Integration with PrismQ Modules

The configuration manager is designed to work across all PrismQ modules:

- **PrismQ.IdeaInspiration.Model** - This package
- **PrismQ.IdeaInspiration.Scoring** - Content scoring engine
- **PrismQ.IdeaInspiration.Classification** - Content classification
- **PrismQ.IdeaInspiration.Builder** - Model construction
- **PrismQ.IdeaInspiration.Sources** - Content source integrations

Each module can maintain its own configuration while sharing the working directory.

## Security Considerations

1. **Never commit sensitive data** - Add `.env` to `.gitignore` if it contains secrets
2. **Use environment variables for secrets** - Set via `PRISMQ_*` environment variables
3. **File permissions** - Ensure `.env` has appropriate read/write permissions
4. **No secrets in code** - Use configuration manager to retrieve sensitive values

## Version History

- **v0.2.0** - Added configuration manager with `.env` file support
- **v0.1.0** - Initial release with core IdeaInspiration model

## Support

For questions or issues with the configuration manager:
1. Check this guide first
2. Review the example script (`example_config_usage.py`)
3. Check the test files for usage patterns
4. Open an issue on GitHub

---

**Part of the PrismQ Ecosystem** - Unified content processing and generation platform
