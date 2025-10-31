"""Module API endpoints."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends

from ..models.module import (
    Module,
    ModuleParameter,
    ModuleListResponse,
    ModuleConfig,
    ModuleConfigUpdate,
)
from ..core import get_config_storage, ConfigStorage
from ..core.exceptions import ModuleNotFoundException, ValidationException
from ..utils.module_loader import get_module_loader

router = APIRouter()


def _validate_parameters(module: Module, parameters: dict) -> List[str]:
    """
    Validate parameters against module parameter definitions.
    
    Args:
        module: Module with parameter definitions
        parameters: Dictionary of parameters to validate
        
    Returns:
        List of error messages (empty if valid)
    """
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
            if param_def.options and value not in param_def.options:
                errors.append(f"{param_name} must be one of: {', '.join(param_def.options)}")
        
        elif param_def.type == "checkbox":
            if not isinstance(value, bool):
                errors.append(f"{param_name} must be a boolean")
        
        elif param_def.type == "text" or param_def.type == "password":
            if not isinstance(value, str):
                errors.append(f"{param_name} must be a string")
    
    return errors


@router.get("/modules", response_model=ModuleListResponse)
async def list_modules():
    """
    Get list of all available PrismQ modules.
    
    Returns:
        ModuleListResponse: List of available modules
    """
    loader = get_module_loader()
    modules = loader.get_all_modules()
    return ModuleListResponse(
        modules=modules,
        total=len(modules),
    )


@router.get("/modules/{module_id}", response_model=Module)
async def get_module(module_id: str):
    """
    Get detailed information about a specific module.
    
    Args:
        module_id: Module identifier
        
    Returns:
        Module: Module details
        
    Raises:
        HTTPException: If module not found
    """
    loader = get_module_loader()
    module = loader.get_module(module_id)
    
    if module is None:
        raise ModuleNotFoundException(
            f"Module '{module_id}' not found",
            module_id=module_id
        )
    
    return module


@router.get("/modules/{module_id}/config", response_model=ModuleConfig)
async def get_module_config(
    module_id: str,
    storage: ConfigStorage = Depends(get_config_storage)
):
    """
    Retrieve saved configuration for a module.
    
    Args:
        module_id: Module identifier
        storage: Configuration storage service (injected)
        
    Returns:
        ModuleConfig: Module configuration with saved parameters merged with defaults
        
    Raises:
        HTTPException: If module not found
    """
    # Check if module exists
    module = await get_module(module_id)
    
    # Get saved config
    saved_params = storage.get_config(module_id)
    
    # Merge with defaults (saved params take precedence)
    default_params = {
        param.name: param.default
        for param in module.parameters
        if param.default is not None
    }
    merged_params = {**default_params, **saved_params}
    
    return ModuleConfig(
        module_id=module_id,
        parameters=merged_params,
        updated_at=datetime.now(timezone.utc),
    )


@router.post("/modules/{module_id}/config", response_model=ModuleConfig)
async def update_module_config(
    module_id: str,
    config_update: ModuleConfigUpdate,
    storage: ConfigStorage = Depends(get_config_storage)
):
    """
    Update saved configuration for a module.
    
    Args:
        module_id: Module identifier
        config_update: Configuration update
        storage: Configuration storage service (injected)
        
    Returns:
        ModuleConfig: Updated configuration
        
    Raises:
        HTTPException: If module not found or invalid parameters
    """
    # Check if module exists
    module = await get_module(module_id)
    
    # Validate parameters
    errors = _validate_parameters(module, config_update.parameters)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameters: {'; '.join(errors)}"
        )
    
    # Save configuration
    success = storage.save_config(module_id, config_update.parameters)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save configuration"
        )
    
    return ModuleConfig(
        module_id=module_id,
        parameters=config_update.parameters,
        updated_at=datetime.now(timezone.utc),
    )


@router.delete("/modules/{module_id}/config")
async def delete_module_config(
    module_id: str,
    storage: ConfigStorage = Depends(get_config_storage)
):
    """
    Delete saved configuration for a module (reset to defaults).
    
    Args:
        module_id: Module identifier
        storage: Configuration storage service (injected)
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If module not found
    """
    # Verify module exists
    await get_module(module_id)
    
    # Delete configuration
    success = storage.delete_config(module_id)
    
    if not success:
        return {"message": "No configuration to delete"}
    
    return {"message": "Configuration deleted successfully"}
