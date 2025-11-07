# Modules Module Documentation

## Overview

The Modules module provides a separated, standalone module for PrismQ module discovery, configuration, and management in the PrismQ Client Backend. This module is designed following the single responsibility principle, focusing solely on module-related operations.

## Architecture

The Modules module is organized as follows:

```
Backend/Modules/
├── __init__.py              # Module initialization
├── README.md                # This documentation
├── models/                  # Pydantic models
│   ├── __init__.py
│   └── module.py            # Module-related models
├── endpoints/               # API endpoints
│   ├── __init__.py
│   └── modules.py          # Module CRUD endpoints
└── services/                # Business logic services
    ├── __init__.py
    ├── config_storage.py   # Configuration persistence
    └── loader.py           # Module discovery and loading
```

## Key Concepts

### Module

A **Module** represents a PrismQ data collection module that can be discovered, configured, and executed. Each module includes:

- Metadata (id, name, description, category)
- Parameter definitions (with types, validation, and conditional display)
- Runtime statistics (last run, total runs, success rate)
- Status information (active, inactive, maintenance)

### Module Configuration

Module configurations are persisted to allow users to save their preferred parameter settings. Configurations are stored as JSON files and merged with default values when retrieved.

## Models

### Module

Core module definition with all metadata and parameters.

**Fields:**
- `id`: Unique module identifier
- `name`: Human-readable module name
- `description`: Module description
- `category`: Module category (e.g., "Content/Shorts")
- `version`: Module version
- `script_path`: Path to module's main script
- `parameters`: List of parameter definitions
- `tags`: Module tags
- `status`: Module status (active/inactive/maintenance)
- `enabled`: Whether module can be launched
- `last_run`: Timestamp of last run
- `total_runs`: Total number of runs
- `success_rate`: Success rate percentage

### ModuleParameter

Parameter definition for module inputs.

**Fields:**
- `name`: Parameter name
- `type`: Parameter type (text/number/select/checkbox/password)
- `default`: Default value
- `options`: Options for select type parameters
- `required`: Whether parameter is required
- `description`: Parameter description
- `min/max`: Min/max values for number type
- `placeholder`: Placeholder text
- `label`: Human-readable label
- `conditional_display`: Conditional display rules
- `validation`: Additional validation rules
- `warning`: Warning message

### ModuleConfig

Configuration data for a module.

**Fields:**
- `module_id`: Module identifier
- `parameters`: Dictionary of parameter values
- `updated_at`: Last update timestamp

## API Endpoints

### GET /api/modules

List all available modules with runtime statistics.

**Response:** 200 OK
```json
{
  "modules": [
    {
      "id": "youtube_channel_download",
      "name": "YouTube Channel Download",
      "description": "Download videos from a YouTube channel",
      "category": "Content",
      "version": "1.0.0",
      "script_path": "/path/to/script.py",
      "parameters": [...],
      "tags": ["youtube", "download"],
      "status": "active",
      "enabled": true,
      "last_run": "2025-11-06T22:00:00Z",
      "total_runs": 15,
      "success_rate": 93.3
    }
  ],
  "total": 1
}
```

### GET /api/modules/{module_id}

Get detailed information about a specific module.

**Response:** 200 OK or 404 Not Found
```json
{
  "id": "youtube_channel_download",
  "name": "YouTube Channel Download",
  ...
}
```

### GET /api/modules/{module_id}/config

Get saved configuration for a module.

**Response:** 200 OK
```json
{
  "module_id": "youtube_channel_download",
  "parameters": {
    "channel_url": "https://youtube.com/@example",
    "max_videos": 10
  },
  "updated_at": "2025-11-06T22:00:00Z"
}
```

### POST /api/modules/{module_id}/config

Save configuration for a module.

**Request Body:**
```json
{
  "parameters": {
    "channel_url": "https://youtube.com/@example",
    "max_videos": 10
  }
}
```

**Response:** 200 OK

### DELETE /api/modules/{module_id}/config

Delete saved configuration (reset to defaults).

**Response:** 204 No Content

### POST /api/modules/{module_id}/validate

Validate parameters against module parameter definitions.

**Request Body:**
```json
{
  "parameters": {
    "channel_url": "https://youtube.com/@example",
    "max_videos": 10
  }
}
```

**Response:** 200 OK or 422 Unprocessable Entity
```json
{
  "valid": true,
  "errors": []
}
```

## Services

### ConfigStorage

Manages persistent storage of module configurations using JSON files.

**Methods:**
- `get_config(module_id)` - Retrieve saved configuration
- `save_config(module_id, parameters)` - Save configuration
- `delete_config(module_id)` - Delete configuration
- `list_configs()` - List all saved configurations

### ModuleLoader

Discovers and loads PrismQ modules from the file system.

**Methods:**
- `get_modules()` - Get all discovered modules
- `get_module(module_id)` - Get specific module by ID
- `reload()` - Reload module definitions from disk

## Error Handling

All endpoints follow standard HTTP status codes:

- **200 OK** - Successful GET/POST request
- **204 No Content** - Successful DELETE request
- **404 Not Found** - Module not found
- **422 Unprocessable Entity** - Validation error
- **500 Internal Server Error** - Server error

Error responses include details:
```json
{
  "detail": "Module 'unknown_module' not found",
  "error_code": "MODULE_NOT_FOUND",
  "timestamp": "2025-11-06T22:00:00Z"
}
```

## Parameter Validation

The module supports sophisticated parameter validation:

1. **Type Validation**: Ensures parameters match their declared types
2. **Required Fields**: Validates required parameters are present
3. **Range Validation**: Checks min/max for number types
4. **Pattern Validation**: Supports regex patterns for text types
5. **Conditional Display**: Parameters can be shown/hidden based on other parameter values

## Integration with Main Application

The Modules module is integrated into the main FastAPI application in `src/main.py`:

```python
from Modules.endpoints import router as modules_router

app.include_router(modules_router, prefix="/api", tags=["Modules"])
```

## Configuration Storage

Module configurations are stored as JSON files in:
- **Windows**: `C:\Data\PrismQ\configs\parameters\{module_id}.json`
- **Linux/macOS**: Configured via `PRISMQ_CONFIG_DIR` environment variable

## Usage Examples

### Example 1: List All Modules

```bash
curl http://localhost:8000/api/modules
```

### Example 2: Get Module Details

```bash
curl http://localhost:8000/api/modules/youtube_channel_download
```

### Example 3: Save Module Configuration

```bash
curl -X POST http://localhost:8000/api/modules/youtube_channel_download/config \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "channel_url": "https://youtube.com/@example",
      "max_videos": 10
    }
  }'
```

### Example 4: Validate Parameters

```bash
curl -X POST http://localhost:8000/api/modules/youtube_channel_download/validate \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "channel_url": "https://youtube.com/@example",
      "max_videos": 10
    }
  }'
```

## Single Responsibility Principle

This module follows the single responsibility principle by:

1. **Focused Scope**: Only handles module discovery, configuration, and metadata
2. **Clear Boundaries**: Does not handle run execution (that's in the Runs module)
3. **Separated Concerns**: Configuration storage is separate from module loading
4. **Minimal Dependencies**: Only depends on core utilities and shared models

## Future Enhancements

Potential future improvements:

1. **Database Storage**: Migrate from JSON files to SQLite for configuration storage
2. **Module Versioning**: Support multiple versions of the same module
3. **Module Dependencies**: Track dependencies between modules
4. **Module Marketplace**: Support downloading modules from a central repository
5. **Module Testing**: Built-in module validation and testing framework

## See Also

- [Main Backend README](../README.md)
- [API Module Documentation](../API/README.md)
- [Runs Module Documentation](../Runs/README.md) (when created)
- [System Module Documentation](../System/README.md) (when created)
