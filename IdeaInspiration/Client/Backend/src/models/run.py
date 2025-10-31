"""Run models for PrismQ Web Client."""

from datetime import datetime
from typing import Optional, Dict, Any, List, Literal, Type
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class RunStatus(str, Enum):
    """Run execution status."""
    
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunCreate(BaseModel):
    """Request model for creating a module run."""
    
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Module parameters",
    )
    save_config: bool = Field(True, description="Whether to save configuration")

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls: Type["RunCreate"], v: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters dictionary.
        
        Args:
            v: Parameters dictionary
            
        Returns:
            Validated parameters
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(v, dict):
            raise ValueError("Parameters must be a dictionary")
        if len(v) > 100:
            raise ValueError("Too many parameters (maximum 100 allowed)")
        
        # Check for forbidden parameter names
        forbidden_keys = ["__internal__", "__system__", "__private__"]
        for key in v.keys():
            if key in forbidden_keys:
                raise ValueError(f"Cannot use forbidden parameter name: {key}")
            if not isinstance(key, str):
                raise ValueError("Parameter keys must be strings")
        
        return v


class Run(BaseModel):
    """Module run information."""
    
    run_id: str = Field(..., description="Unique run identifier")
    module_id: str = Field(..., description="Module ID")
    module_name: str = Field(..., description="Module name")
    status: RunStatus = Field(..., description="Run status")
    created_at: datetime = Field(..., description="Run creation time")
    started_at: Optional[datetime] = Field(None, description="Run start time")
    completed_at: Optional[datetime] = Field(None, description="Run completion time")
    duration_seconds: Optional[int] = Field(None, description="Run duration in seconds")
    progress_percent: Optional[int] = Field(None, description="Progress percentage (0-100)")
    items_processed: Optional[int] = Field(None, description="Number of items processed")
    items_total: Optional[int] = Field(None, description="Total number of items")
    exit_code: Optional[int] = Field(None, description="Process exit code")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Run parameters",
    )


class RunListResponse(BaseModel):
    """Response model for listing runs."""
    
    runs: List[Run] = Field(..., description="List of runs")
    total: int = Field(..., description="Total number of runs")
    limit: int = Field(..., description="Results per page")
    offset: int = Field(..., description="Pagination offset")


class LogEntry(BaseModel):
    """Log entry model."""
    
    timestamp: datetime = Field(..., description="Log timestamp")
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        ..., description="Log level"
    )
    message: str = Field(..., description="Log message")


class LogResponse(BaseModel):
    """Response model for logs."""
    
    run_id: str = Field(..., description="Run identifier")
    logs: List[LogEntry] = Field(..., description="Log entries")
    total_lines: int = Field(..., description="Total number of log lines")
    truncated: bool = Field(..., description="Whether logs are truncated")


class OutputFile(BaseModel):
    """Output file information."""
    
    filename: str = Field(..., description="File name")
    path: str = Field(..., description="File path")
    size_bytes: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(..., description="File creation timestamp")


class ResultsSummary(BaseModel):
    """Run results summary."""
    
    items_collected: int = Field(0, description="Number of items collected")
    items_saved: int = Field(0, description="Number of items saved")
    errors: int = Field(0, description="Number of errors")
    duration_seconds: int = Field(0, description="Duration in seconds")


class ResultsResponse(BaseModel):
    """Response model for run results."""
    
    run_id: str = Field(..., description="Run identifier")
    status: RunStatus = Field(..., description="Run status")
    summary: ResultsSummary = Field(..., description="Results summary")
    output_files: List[OutputFile] = Field(
        default_factory=list, description="Output files"
    )
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Additional metrics")
