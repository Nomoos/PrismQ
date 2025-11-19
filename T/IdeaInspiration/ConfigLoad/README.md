# ConfigLoad

Centralized configuration management for all PrismQ modules.

## ✨ Highlights

- **Automatic `.env` discovery** - Finds and loads configuration automatically
- **Centralized storage** - Single `PrismQ_WD` directory for all configs
- **Interactive prompting** - Prompts for missing configuration values
- **Module logging** - Comprehensive logging with metadata and system info
- **Type-safe** - Full type hints support
- **SOLID principles** - Clean, maintainable design

## 🚀 Quick Start

```python
from ConfigLoad import Config

# Initialize configuration
config = Config()

# Get configuration values
database_url = config.get("DATABASE_URL", "sqlite:///default.db")

# Get or prompt for values
api_key = config.get_or_prompt("API_KEY", "Enter your API key", required=True)
```

## 📚 Documentation

### Basic Usage

**Configuration Loading:**
```python
from ConfigLoad import Config

config = Config()
database_url = config.get("DATABASE_URL", "sqlite:///default.db")
api_key = config.get_or_prompt("API_KEY", "Enter your API key", required=True)
config.set("MY_CONFIG_KEY", "my_value")
```

**Module Logging:**
```python
from ConfigLoad import get_module_logger

logger = get_module_logger(
    module_name="PrismQ.MyModule",
    module_version="1.0.0"
)

logger.info("Processing started")
logger.warning("Low memory detected")
```

### API Reference

**Config Class:**
- `get(key, default)` - Get configuration value
- `set(key, value)` - Set configuration value  
- `get_or_prompt(key, description, default, required)` - Get or prompt for value

**Logging Functions:**
- `get_module_logger(module_name, module_version, module_path, log_startup)` - Get configured logger
- `setup_basic_logging(log_level)` - Set up basic logging

**Utility Functions:**
- `find_prismq_directory()` - Find topmost PrismQ directory

### How It Works

The `Config` class automatically finds the topmost directory named `PrismQ` in the current path hierarchy and creates a `PrismQ_WD` (working directory) at the same level to store the `.env` file.

```
./home/user/
├── PrismQ/                    # Topmost PrismQ directory
│   ├── Module1/
│   └── Module2/
└── PrismQ_WD/                 # Working directory (created automatically)
    └── .env                   # Configuration file
```

## 🔗 Related

- [Main Repository](../) - PrismQ.IdeaInspiration overview
- [Model Module](../Model/) - Uses ConfigLoad for configuration

## 📄 License

Proprietary - All Rights Reserved
