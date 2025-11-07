"""Module models for PrismQ Web Client."""

from datetime import datetime
from typing import List, Optional, Any, Literal, Dict
from pydantic import BaseModel, Field


class ConditionalDisplay(BaseModel):
    """Conditional display rule for parameters."""
    
    field: str = Field(..., description="Field name to check")
    value: str | int | bool = Field(..., description="Value that triggers display")


class ValidationRule(BaseModel):
    """Validation rule for parameters."""
    
    pattern: Optional[str] = Field(None, description="Regex pattern for validation")
    message: Optional[str] = Field(None, description="Error message if validation fails")


class ModuleParameter(BaseModel):
    """Module parameter definition."""
    
    name: str = Field(..., description="Parameter name")
    type: Literal["text", "number", "select", "checkbox", "password"] = Field(
        ..., description="Parameter type"
    )
    default: Optional[str | int | bool] = Field(None, description="Default value")
    options: Optional[List[str]] = Field(None, description="Options for select type parameters")
    required: bool = Field(False, description="Whether parameter is required")
    description: str = Field("", description="Parameter description")
    min: Optional[int] = Field(None, description="Minimum value for number type")
    max: Optional[int] = Field(None, description="Maximum value for number type")
    placeholder: Optional[str] = Field(None, description="Placeholder text for input fields")
    label: Optional[str] = Field(None, description="Human-readable label for the parameter")
    conditional_display: Optional[ConditionalDisplay] = Field(
        None, description="Conditional display rule based on another parameter"
    )
    validation: Optional[ValidationRule] = Field(
        None, description="Additional validation rules"
    )
    warning: Optional[str] = Field(None, description="Warning message to display for this parameter")


class Module(BaseModel):
    """PrismQ module definition."""
    
    id: str = Field(..., description="Unique module identifier")
    name: str = Field(..., description="Human-readable module name")
    description: str = Field(..., description="Module description")
    category: str = Field(..., description="Module category (e.g., Content/Shorts)")
    version: str = Field("1.0.0", description="Module version")
    script_path: str = Field(..., description="Path to module's main script")
    parameters: List[ModuleParameter] = Field(
        default_factory=list,
        description="Module parameters",
    )
    tags: List[str] = Field(default_factory=list, description="Module tags")
    status: Literal["active", "inactive", "maintenance"] = Field(
        "active", description="Module status"
    )
    enabled: bool = Field(True, description="Whether module can be launched")
    last_run: Optional[datetime] = Field(None, description="Timestamp of last run")
    total_runs: int = Field(0, description="Total number of runs")
    success_rate: float = Field(0.0, description="Success rate percentage")


class ModuleListResponse(BaseModel):
    """Response model for listing modules."""
    
    modules: List[Module] = Field(..., description="List of available modules")
    total: int = Field(..., description="Total number of modules")


class ModuleConfig(BaseModel):
    """Module configuration."""
    
    module_id: str = Field(..., description="Module identifier")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Configuration parameters"
    )
    updated_at: datetime = Field(..., description="Last update timestamp")


class ModuleConfigUpdate(BaseModel):
    """Module configuration update request."""
    
    parameters: Dict[str, Any] = Field(..., description="Configuration parameters to update")


class ModuleDetailResponse(BaseModel):
    """Response model for getting a single module with its details."""
    
    module: Module = Field(..., description="Module information")
