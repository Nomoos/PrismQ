# Configuration Persistence

## Overview

The PrismQ Web Client implements a parameter persistence system that remembers user-provided module parameters between runs. This eliminates the need to re-enter parameters every time a module is launched, significantly improving the user experience.

## Storage Strategy

Configuration parameters are stored in JSON files in the `Client/Backend/configs/parameters/` directory. Each module has its own JSON file named after the module ID (e.g., `youtube-shorts.json`).

**Benefits:**
- **Simpler** than database for local applications
- **Human-readable** and manually editable
- **Version control friendly** (can be committed if desired)
- **Easy backup/restore**

## Configuration File Structure

```json
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming",
    "api_key": "YOUR_API_KEY_HERE",
    "output_format": "json",
    "include_transcripts": true
  },
  "updated_at": "2025-10-30T15:45:23.123456Z"
}
```

## API Endpoints

### Get Module Configuration

```http
GET /api/modules/{module_id}/config
```

Returns the saved configuration for a module, merged with default values.

**Response:**
```json
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming"
  },
  "updated_at": "2025-10-30T15:45:23.123456Z"
}
```

### Save Module Configuration

```http
POST /api/modules/{module_id}/config
Content-Type: application/json

{
  "parameters": {
    "max_results": 200,
    "trending_category": "Music"
  }
}
```

Validates and saves the configuration for a module.

**Validation:**
- Required parameters must be present
- Number parameters must be within min/max bounds
- Select parameters must match allowed options
- Type validation for all parameter types

**Response:**
```json
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 200,
    "trending_category": "Music"
  },
  "updated_at": "2025-10-30T15:50:10.987654Z"
}
```

### Delete Module Configuration

```http
DELETE /api/modules/{module_id}/config
```

Deletes the saved configuration (resets to defaults).

**Response:**
```json
{
  "message": "Configuration deleted successfully"
}
```

## Backend Integration

### ConfigStorage Service

The `ConfigStorage` class in `src/core/config_storage.py` handles all file I/O operations:

```python
from src.core import get_config_storage

storage = get_config_storage()

# Get saved configuration
params = storage.get_config("youtube-shorts")

# Save configuration
storage.save_config("youtube-shorts", {"max_results": 100})

# Delete configuration
storage.delete_config("youtube-shorts")

# List all saved configurations
configs = storage.list_configs()
```

### ModuleRunner Integration

The `ModuleRunner` automatically saves configuration when `save_config=True`:

```python
run = await runner.execute_module(
    module_id="youtube-shorts",
    module_name="YouTube Shorts Source",
    script_path=Path("path/to/script.py"),
    parameters={"max_results": 100},
    save_config=True  # Saves parameters to config storage
)
```

## Frontend Integration

### Module Service

The `moduleService` in `src/services/modules.ts` provides methods to interact with the configuration API:

```typescript
import { moduleService } from '@/services/modules'

// Get saved configuration
const config = await moduleService.getConfig('youtube-shorts')

// Save configuration
await moduleService.saveConfig('youtube-shorts', { max_results: 100 })

// Delete configuration
await moduleService.deleteConfig('youtube-shorts')

// Launch module with saved config
await moduleService.launchModule('youtube-shorts', params, true)
```

### ModuleLaunchModal Component

The launch modal automatically:
1. Loads saved configuration on mount
2. Merges saved values with defaults
3. Provides a "Save configuration" checkbox
4. Provides a "Reset to defaults" button

## User Experience

### First Time Launch

1. User opens the launch modal for a module
2. Form fields are pre-populated with default values from module definition
3. "Save configuration" checkbox is checked by default
4. User fills in parameters and launches the module
5. Parameters are automatically saved for next time

### Subsequent Launches

1. User opens the launch modal
2. Form fields are pre-populated with **saved values** from last run
3. User can modify values if needed
4. User can uncheck "Save configuration" to launch without saving
5. User can click "Reset to defaults" to clear saved values

### Reset to Defaults

1. Click "Reset to defaults" button in the launch modal
2. Saved configuration is deleted via API
3. Form fields are immediately reset to default values
4. Next launch will use defaults again (until saved)

## File Locations

```
Client/Backend/
├── configs/
│   └── parameters/           # User configuration files
│       ├── youtube-shorts.json
│       ├── reddit-source.json
│       └── tiktok-source.json
├── data/
│   ├── run_history.json      # Run history (gitignored)
│   └── logs/                 # Log files (gitignored)
└── src/
    └── core/
        └── config_storage.py  # Storage service
```

## Security Considerations

### Sensitive Data

- API keys and passwords are stored in plain text in JSON files
- Config directory should have restricted file permissions (user-only)
- Consider encrypting sensitive fields in production deployments

### Validation

- All parameters are validated against module schema before saving
- Invalid parameters are rejected with clear error messages
- Type checking ensures data integrity

### Backup

- Configuration files can be backed up by copying the `configs/parameters/` directory
- Files are human-readable JSON for easy inspection and recovery

## Testing

The implementation includes comprehensive test coverage:

- `test_config_storage.py` - Unit tests for ConfigStorage service (14 tests)
- `test_config_integration.py` - Integration tests for API endpoints (13 tests)
- `test_module_runner.py` - Tests for save_config parameter integration

Run tests:
```bash
cd Client/Backend
pytest ../_meta/tests/Backend/test_config_*.py -v
```

## Related Issues

- **#103**: Backend Module Runner (prerequisite)
- **#105**: Frontend UI (parallel development)
- **#106**: Parameter Persistence (this feature)

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
