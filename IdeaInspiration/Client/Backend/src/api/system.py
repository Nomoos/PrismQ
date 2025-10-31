"""System health and statistics API endpoints."""

import time
from fastapi import APIRouter, Depends

from ..models.system import (
    HealthResponse,
    SystemStats,
    RunStats,
    ModuleStats,
    SystemResources,
)
from ..models.run import RunStatus
from ..core import get_module_runner, get_resource_manager, ModuleRunner, ResourceManager
from ..utils.module_loader import get_module_loader

router = APIRouter()

# Track server start time
START_TIME = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check(runner: ModuleRunner = Depends(get_module_runner)):
    """
    Health check endpoint.
    
    Args:
        runner: Module runner service (injected)
    
    Returns:
        HealthResponse: Health status information
    """
    active_runs = len(runner.registry.get_active_runs())
    uptime = int(time.time() - START_TIME)
    loader = get_module_loader()
    modules = loader.get_all_modules()
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=uptime,
        active_runs=active_runs,
        total_modules=len(modules),
    )


@router.get("/system/stats", response_model=SystemStats)
async def system_stats(
    runner: ModuleRunner = Depends(get_module_runner),
    resource_manager: ResourceManager = Depends(get_resource_manager)
):
    """
    System statistics and metrics.
    
    Args:
        runner: Module runner service (injected)
        resource_manager: Resource manager service (injected)
    
    Returns:
        SystemStats: System statistics
    """
    # Calculate run statistics
    all_runs = runner.registry.get_recent_runs(limit=10000)
    total_runs = len(all_runs)
    successful_runs = len(runner.registry.get_runs_by_status(RunStatus.COMPLETED))
    failed_runs = len(runner.registry.get_runs_by_status(RunStatus.FAILED))
    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0.0
    
    run_stats = RunStats(
        total=total_runs,
        successful=successful_runs,
        failed=failed_runs,
        success_rate=success_rate,
    )
    
    # Calculate module statistics
    loader = get_module_loader()
    modules = loader.get_all_modules()
    active_modules = len([m for m in modules if m.status == "active"])
    total_modules = len(modules)
    idle_modules = total_modules - active_modules
    
    module_stats = ModuleStats(
        total=total_modules,
        active=active_modules,
        idle=idle_modules,
    )
    
    # Get real system resources from ResourceManager
    stats = resource_manager.get_system_stats()
    system_resources = SystemResources(
        cpu_percent=stats["cpu_percent"],
        memory_percent=stats["memory_used_percent"],
        disk_free_gb=0.0,  # Not tracked yet
    )
    
    return SystemStats(
        runs=run_stats,
        modules=module_stats,
        system=system_resources,
    )
