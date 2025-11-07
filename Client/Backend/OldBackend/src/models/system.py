"""System health and statistics models for PrismQ Web Client."""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    uptime_seconds: int = Field(..., description="Server uptime in seconds")
    active_runs: int = Field(0, description="Number of active runs")
    total_modules: int = Field(0, description="Total number of modules")


class RunStats(BaseModel):
    """Run statistics."""
    
    total: int = Field(0, description="Total number of runs")
    successful: int = Field(0, description="Number of successful runs")
    failed: int = Field(0, description="Number of failed runs")
    success_rate: float = Field(0.0, description="Success rate percentage")


class ModuleStats(BaseModel):
    """Module statistics."""
    
    total: int = Field(0, description="Total number of modules")
    active: int = Field(0, description="Number of active modules")
    idle: int = Field(0, description="Number of idle modules")


class SystemResources(BaseModel):
    """System resource usage."""
    
    cpu_percent: float = Field(0.0, description="CPU usage percentage")
    memory_percent: float = Field(0.0, description="Memory usage percentage")
    disk_free_gb: float = Field(0.0, description="Free disk space in GB")


class SystemStats(BaseModel):
    """System statistics response."""
    
    runs: RunStats = Field(..., description="Run statistics")
    modules: ModuleStats = Field(..., description="Module statistics")
    system: SystemResources = Field(..., description="System resource usage")


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Error timestamp"
    )
