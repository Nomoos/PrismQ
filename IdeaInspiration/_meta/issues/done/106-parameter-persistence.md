# Issue #106: Implement Parameter Persistence

**Type**: Feature  
**Priority**: Medium  
**Status**: Done  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 1 week  
**Dependencies**: #103 (Backend Module Runner)  
**Can be parallelized with**: #105 (Frontend UI), #107 (Log Display)

---

## Description

Implement a system to remember user-provided parameters between module runs. This improves UX by pre-populating forms with last-used values, eliminating the need to re-enter parameters every time.

## Storage Strategy

Use JSON configuration files for structured parameter storage:
- **Simpler** than database for local app
- **Human-readable** and editable
- **Version control friendly**
- **Easy backup/restore**

## Architecture

```
Client/Backend/
├── configs/
│   ├── modules.json           # Module definitions (read-only)
│   └── parameters/            # User configurations (read-write)
│       ├── youtube-shorts.json
│       ├── reddit-source.json
│       └── tiktok-source.json
```

## Implementation

### 1. Config Storage Service

```python
# src/core/config_storage.py

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConfigStorage:
    """
    Manages persistent storage of module configurations.
    
    Responsibilities:
    - Save module parameters to JSON files
    - Load saved parameters
    - Provide default values
    - Handle config validation
    """
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir / "parameters"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def get_config(self, module_id: str) -> Dict:
        """
        Get saved configuration for a module.
        
        Args:
            module_id: Module identifier
            
        Returns:
            Dictionary of saved parameters
        """
        config_file = self.config_dir / f"{module_id}.json"
        
        if not config_file.exists():
            return {}
        
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded config for {module_id}")
                return data.get("parameters", {})
        except Exception as e:
            logger.error(f"Error loading config for {module_id}: {e}")
            return {}
    
    def save_config(self, module_id: str, parameters: Dict) -> bool:
        """
        Save configuration for a module.
        
        Args:
            module_id: Module identifier
            parameters: Dictionary of parameters to save
            
        Returns:
            True if successful
        """
        config_file = self.config_dir / f"{module_id}.json"
        
        try:
            data = {
                "module_id": module_id,
                "parameters": parameters,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved config for {module_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving config for {module_id}: {e}")
            return False
    
    def delete_config(self, module_id: str) -> bool:
        """Delete saved configuration for a module."""
        config_file = self.config_dir / f"{module_id}.json"
        
        if config_file.exists():
            config_file.unlink()
            logger.info(f"Deleted config for {module_id}")
            return True
        return False
    
    def list_configs(self) -> list[str]:
        """List all modules with saved configurations."""
        return [f.stem for f in self.config_dir.glob("*.json")]
```

### 2. API Endpoints

```python
# src/api/config.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ..core.config_storage import ConfigStorage
from ..core.module_registry import ModuleRegistry

router = APIRouter()

class ConfigUpdate(BaseModel):
    parameters: dict

class ConfigResponse(BaseModel):
    module_id: str
    parameters: dict
    updated_at: str

@router.get("/modules/{module_id}/config", response_model=ConfigResponse)
async def get_module_config(
    module_id: str,
    storage: ConfigStorage = Depends(get_config_storage),
    registry: ModuleRegistry = Depends(get_module_registry)
):
    """
    Get saved configuration for a module.
    
    Returns saved parameters merged with defaults.
    """
    # Verify module exists
    module = registry.get_module(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Get saved config
    saved_params = storage.get_config(module_id)
    
    # Merge with defaults
    default_params = {
        param.name: param.default
        for param in module.parameters
        if param.default is not None
    }
    
    merged_params = {**default_params, **saved_params}
    
    return ConfigResponse(
        module_id=module_id,
        parameters=merged_params,
        updated_at=datetime.utcnow().isoformat()
    )

@router.post("/modules/{module_id}/config", response_model=ConfigResponse)
async def save_module_config(
    module_id: str,
    config: ConfigUpdate,
    storage: ConfigStorage = Depends(get_config_storage),
    registry: ModuleRegistry = Depends(get_module_registry)
):
    """
    Save configuration for a module.
    """
    # Verify module exists
    module = registry.get_module(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Validate parameters
    errors = validate_parameters(module, config.parameters)
    if errors:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameters: {', '.join(errors)}"
        )
    
    # Save configuration
    success = storage.save_config(module_id, config.parameters)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to save configuration"
        )
    
    return ConfigResponse(
        module_id=module_id,
        parameters=config.parameters,
        updated_at=datetime.utcnow().isoformat()
    )

@router.delete("/modules/{module_id}/config")
async def delete_module_config(
    module_id: str,
    storage: ConfigStorage = Depends(get_config_storage)
):
    """
    Delete saved configuration for a module (reset to defaults).
    """
    success = storage.delete_config(module_id)
    if not success:
        return {"message": "No configuration to delete"}
    return {"message": "Configuration deleted successfully"}

def validate_parameters(module, parameters: dict) -> list[str]:
    """Validate parameters against module schema."""
    errors = []
    
    for param_def in module.parameters:
        param_name = param_def.name
        
        # Check required parameters
        if param_def.required and param_name not in parameters:
            errors.append(f"{param_name} is required")
            continue
        
        if param_name not in parameters:
            continue
        
        value = parameters[param_name]
        
        # Type validation
        if param_def.type == "number":
            if not isinstance(value, (int, float)):
                errors.append(f"{param_name} must be a number")
            elif param_def.min is not None and value < param_def.min:
                errors.append(f"{param_name} must be >= {param_def.min}")
            elif param_def.max is not None and value > param_def.max:
                errors.append(f"{param_name} must be <= {param_def.max}")
        
        elif param_def.type == "select":
            if value not in param_def.options:
                errors.append(f"{param_name} must be one of: {param_def.options}")
        
        elif param_def.type == "checkbox":
            if not isinstance(value, bool):
                errors.append(f"{param_name} must be a boolean")
    
    return errors
```

### 3. Integration with Module Runner

Update module execution to automatically save configuration:

```python
# Update in src/core/module_runner.py

async def execute_module(
    self,
    module_id: str,
    script_path: Path,
    parameters: Dict,
    save_config: bool = True,
    run_id: Optional[str] = None
) -> Run:
    """Execute a module with optional config saving."""
    
    # ... existing code ...
    
    # Save configuration if requested
    if save_config:
        self.config_storage.save_config(module_id, parameters)
    
    # ... rest of execution ...
```

### 4. Frontend Integration

Update launch modal to save config option:

```typescript
// src/services/modules.ts

async saveConfig(moduleId: string, parameters: Record<string, any>): Promise<void> {
  await axios.post(`${API_BASE}/modules/${moduleId}/config`, {
    parameters
  })
}

async deleteConfig(moduleId: string): Promise<void> {
  await axios.delete(`${API_BASE}/modules/${moduleId}/config`)
}
```

Update modal component to load and save config:

```vue
<!-- In ModuleLaunchModal.vue -->

<template>
  <div class="form-actions">
    <label>
      <input type="checkbox" v-model="saveConfig" />
      Remember these parameters
    </label>
    
    <button 
      type="button" 
      @click="resetToDefaults" 
      class="btn-text"
    >
      Reset to defaults
    </button>
  </div>
</template>

<script setup>
async function resetToDefaults() {
  await moduleService.deleteConfig(props.module.id)
  await loadConfiguration()
}
</script>
```

---

## Configuration File Format

### Example: `youtube-shorts.json`

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

---

## Tasks

### Backend
- [ ] Implement `ConfigStorage` service
- [ ] Create config directory structure
- [ ] Implement GET `/api/modules/{id}/config`
- [ ] Implement POST `/api/modules/{id}/config`
- [ ] Implement DELETE `/api/modules/{id}/config`
- [ ] Add parameter validation
- [ ] Integrate with module runner (auto-save)

### Frontend
- [ ] Update launch modal to load saved config
- [ ] Add "Remember parameters" checkbox
- [ ] Add "Reset to defaults" button
- [ ] Update API service with config methods
- [ ] Show indication of saved vs default values

### Testing
- [ ] Unit tests for `ConfigStorage`
- [ ] API endpoint tests
- [ ] Test parameter validation
- [ ] Test default merging logic
- [ ] Frontend component tests

### Documentation
- [ ] Document configuration file format
- [ ] Document API endpoints
- [ ] Add usage examples

---

## Acceptance Criteria

- [x] Configurations saved to JSON files
- [x] Saved parameters loaded when opening module form
- [x] Parameters merged with defaults correctly
- [x] "Save config" option in launch modal
- [x] Reset to defaults functionality works
- [x] Parameter validation enforced
- [x] Invalid parameters rejected with clear errors
- [x] Config persists across server restarts

## Security Considerations

- **Sensitive Data**: Mask API keys/passwords in UI
- **File Permissions**: Restrict config directory to user only
- **Validation**: Always validate parameters before saving
- **Backup**: Consider periodic config backups

## Related Issues

- **Depends on**: #103 (Backend Module Runner)
- **Parallel**: #105 (Frontend UI)
- **Related**: #102 (API Design)

## References

- [JSON Configuration Best Practices](https://www.json.org/)
- [Python json module](https://docs.python.org/3/library/json.html)
