# src Migration Guide

This guide helps you migrate existing PrismQ modules to use the centralized `src` module for .env file loading and logging configuration.

## Benefits of Migration

- **Centralized Configuration**: Single source of truth for .env loading across all modules
- **Consistent Logging**: Standardized logging with module metadata and system information
- **Less Duplication**: No need to copy .env loading code in every module
- **Automatic Discovery**: Finds PrismQ root directory and creates PrismQ_WD automatically
- **Better Testing**: Comprehensive test coverage for configuration management

## Before You Start

1. Ensure `src` is available in the repository root
2. Install dependencies: `pip install python-dotenv psutil`

## Migration Steps

### Step 1: Update Imports

#### Before (using dotenv directly):
```python
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

#### After (using src):
```python
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))  # Adjust as needed

from src import Config, get_module_logger

# Initialize configuration
config = Config(interactive=False)

# Get logger with startup information
logger = get_module_logger(
    module_name="PrismQ.YourModule",
    module_version="0.1.0",
    module_path=str(Path(__file__).parent),
    log_startup=True
)
```

### Step 2: Access Configuration Values

#### Before:
```python
import os
database_url = os.getenv("DATABASE_URL", "sqlite:///default.db")
api_key = os.getenv("API_KEY", "")
```

#### After (Option 1 - Direct environment access):
```python
import os
# Config automatically loads .env, so os.getenv() still works
database_url = os.getenv("DATABASE_URL", "sqlite:///default.db")
api_key = os.getenv("API_KEY", "")
```

#### After (Option 2 - Using Config methods):
```python
# Using Config instance
database_url = config.get("DATABASE_URL", "sqlite:///default.db")

# With interactive prompting (only in interactive mode)
api_key = config.get_or_prompt(
    "API_KEY",
    "Enter your API key",
    default="",
    required=True
)
```

### Step 3: Update Module-Specific logging_config.py (If Exists)

If your module has its own `logging_config.py`, you have two options:

#### Option A: Delete it and use src directly
Remove the file and update all imports to use src.

#### Option B: Create a backward compatibility shim (Recommended)
Keep the file but re-export from src:

```python
"""DEPRECATED: Use src module instead.

This file is kept for backward compatibility.
New code should import from src module.
"""

import warnings
warnings.warn(
    "YourModule/logging_config is deprecated. Use src module instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from src
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logging_config import (
    ModuleLogger,
    get_module_logger,
    setup_basic_logging
)

__all__ = ["ModuleLogger", "get_module_logger", "setup_basic_logging"]
```

### Step 4: Test Your Changes

1. Run your module's tests: `pytest tests/`
2. Run the module directly to verify it works
3. Check that .env file is created in PrismQ_WD directory
4. Verify logging output includes module startup information

## Example: Complete Migration

### Before (example module):

**my_module/src/main.py:**
```python
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db_path = os.getenv("DATABASE_PATH", "./db.sqlite")
    logger.info(f"Using database: {db_path}")
    # ... rest of code
```

### After (migrated):

**my_module/src/main.py:**
```python
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src import Config, get_module_logger

# Initialize configuration
config = Config(interactive=False)

# Get logger
logger = get_module_logger(
    module_name="PrismQ.MyModule",
    module_version="1.0.0",
    module_path=str(Path(__file__).parent),
    log_startup=True
)

def main():
    # Option 1: Use config.get()
    db_path = config.get("DATABASE_PATH", "./db.sqlite")
    
    # Option 2: Use os.getenv (still works after Config init)
    # import os
    # db_path = os.getenv("DATABASE_PATH", "./db.sqlite")
    
    # Option 3: Use Config.get_or_prompt for interactive input
    # db_path = config.get_or_prompt(
    #     "DATABASE_PATH",
    #     "Enter database path",
    #     default="./db.sqlite"
    # )
    
    logger.info(f"Using database: {db_path}")
    # ... rest of code
```

## Path Adjustment

The path adjustment depends on your module structure:

```
PrismQ.T.Idea.Inspiration/
├── src/          # Root level
├── MyModule/
│   ├── src/
│   │   └── main.py     # Need: parent.parent.parent to reach root
│   └── tests/
└── AnotherModule/
    └── script.py        # Need: parent.parent to reach root
```

Adjust the number of `.parent` calls based on how deep your file is:
- Module root → 1 parent: `Path(__file__).parent.parent`
- Module/src → 2 parents: `Path(__file__).parent.parent.parent`
- Module/src/subdir → 3 parents: `Path(__file__).parent.parent.parent.parent`

## Common Issues

### Issue: ModuleNotFoundError: No module named 'src'

**Solution**: Adjust the sys.path.insert() to point to the correct parent directory:
```python
# Check your current file location relative to root
print(f"Current file: {Path(__file__)}")
print(f"Looking for src at: {Path(__file__).parent.parent.parent}")
```

### Issue: .env file not found

**Solution**: src automatically creates .env in PrismQ_WD directory. If you're in a PrismQ directory structure, it will find it. Otherwise, it uses current directory.

### Issue: Existing tests break

**Solution**: 
1. Update test imports to include src in path
2. Mock the Config initialization in tests if needed:
```python
from unittest.mock import patch

@patch('src.config.Config')
def test_something(mock_config):
    # Your test code
```

## Need Help?

- See `src/README.md` for full API documentation
- Check `Scoring/src/main.py` for a complete example
- Review `src/_meta/tests/` for usage examples

## Rollback

If you need to rollback:

1. Restore your original imports
2. Add back `load_dotenv()` calls
3. Restore logging configuration
4. Remove src imports

The old pattern will still work - src is an enhancement, not a requirement.
