"""Maintenance tasks for periodic background operations.

This module provides example maintenance tasks that can be run periodically:
- Cleanup of old run data
- System health checks
- Log rotation (if needed)
- Cache cleanup

These tasks demonstrate the use of the PeriodicTask pattern for common
maintenance operations.

Platform: Windows (primary), Linux/macOS (supported)
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


async def cleanup_old_runs(
    max_age_hours: int = 24,
    registry = None,
) -> int:
    """Clean up old run data from the registry.
    
    Removes completed runs that are older than the specified age to prevent
    the run registry from growing indefinitely.
    
    Args:
        max_age_hours: Maximum age of runs to keep (default: 24 hours)
        registry: RunRegistry instance (if None, imports and uses singleton)
        
    Returns:
        Number of runs cleaned up
    """
    logger.info(f"Starting cleanup of runs older than {max_age_hours} hours")
    
    try:
        # Import here to avoid circular dependencies
        if registry is None:
            from ..core.run_registry import RunRegistry
            registry = RunRegistry()
        
        from ..models.run import RunStatus
        from datetime import timezone
        
        # Calculate cutoff time
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        
        # Get all runs from the internal dict
        all_runs = list(registry.runs.values())
        
        # Filter old completed/failed runs
        runs_to_clean = [
            run for run in all_runs
            if run.completed_at and run.completed_at < cutoff_time
            and run.status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED]
        ]
        
        # Remove old runs
        cleanup_count = 0
        for run in runs_to_clean:
            try:
                del registry.runs[run.run_id]
                cleanup_count += 1
                logger.debug(f"Removed old run: {run.run_id} (status: {run.status})")
            except Exception as e:
                logger.warning(f"Failed to remove run {run.run_id}: {e}")
        
        # Save updated history if we removed any runs
        if cleanup_count > 0:
            registry._save_history()
        
        logger.info(f"Cleaned up {cleanup_count} old runs")
        return cleanup_count
        
    except Exception as e:
        logger.error(f"Error during run cleanup: {e}", exc_info=True)
        raise


async def check_system_health() -> dict:
    """Perform a system health check.
    
    Checks various system resources and logs warnings if any are concerning.
    This is a monitoring task that helps identify issues proactively.
    
    Returns:
        Dictionary with health check results
    """
    logger.debug("Performing system health check")
    
    health = {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "checks": {}
    }
    
    try:
        # Check memory usage
        import psutil
        
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        health["checks"]["memory"] = {
            "percent_used": memory_percent,
            "status": "ok" if memory_percent < 80 else "warning"
        }
        
        if memory_percent > 80:
            logger.warning(f"High memory usage: {memory_percent:.1f}%")
            health["status"] = "warning"
        
        # Check disk usage (platform-specific root path)
        disk_path = "C:\\" if sys.platform == "win32" else "/"
        disk = psutil.disk_usage(disk_path)
        disk_percent = disk.percent
        health["checks"]["disk"] = {
            "percent_used": disk_percent,
            "status": "ok" if disk_percent < 90 else "warning"
        }
        
        if disk_percent > 90:
            logger.warning(f"High disk usage: {disk_percent:.1f}%")
            health["status"] = "warning"
        
        # Check CPU usage (average over 1 second)
        cpu_percent = psutil.cpu_percent(interval=1)
        health["checks"]["cpu"] = {
            "percent_used": cpu_percent,
            "status": "ok" if cpu_percent < 90 else "warning"
        }
        
        if cpu_percent > 90:
            logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
            health["status"] = "warning"
        
        # Check active asyncio tasks
        tasks = asyncio.all_tasks()
        task_count = len(tasks)
        health["checks"]["asyncio_tasks"] = {
            "count": task_count,
            "status": "ok" if task_count < 100 else "warning"
        }
        
        if task_count > 100:
            logger.warning(f"Many active asyncio tasks: {task_count}")
            health["status"] = "warning"
        
        logger.debug(
            f"Health check: {health['status']} "
            f"(Memory: {memory_percent:.1f}%, Disk: {disk_percent:.1f}%, "
            f"CPU: {cpu_percent:.1f}%, Tasks: {task_count})"
        )
        
    except Exception as e:
        logger.error(f"Error during health check: {e}", exc_info=True)
        health["status"] = "error"
        health["error"] = str(e)
    
    return health


async def cleanup_temp_files(
    temp_dir: Optional[Path] = None,
    max_age_hours: int = 24
) -> int:
    """Clean up temporary files older than specified age.
    
    Args:
        temp_dir: Directory to clean (default: system temp dir)
        max_age_hours: Maximum age of files to keep (default: 24 hours)
        
    Returns:
        Number of files cleaned up
    """
    if temp_dir is None:
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "prismq"
    
    if not temp_dir.exists():
        logger.debug(f"Temp directory does not exist: {temp_dir}")
        return 0
    
    logger.info(f"Cleaning temp files in {temp_dir} older than {max_age_hours} hours")
    
    try:
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleanup_count = 0
        
        for file_path in temp_dir.rglob("*"):
            if not file_path.is_file():
                continue
            
            try:
                # Check file modification time
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if mtime < cutoff_time:
                    file_path.unlink()
                    cleanup_count += 1
                    logger.debug(f"Removed temp file: {file_path.name}")
                    
            except Exception as e:
                logger.warning(f"Failed to remove {file_path.name}: {e}")
        
        logger.info(f"Cleaned up {cleanup_count} temp files")
        return cleanup_count
        
    except Exception as e:
        logger.error(f"Error during temp file cleanup: {e}", exc_info=True)
        raise


async def log_statistics() -> dict:
    """Log statistics about the backend system.
    
    This is a monitoring task that periodically logs system state for
    observability and debugging.
    
    Returns:
        Dictionary with system statistics
    """
    logger.debug("Collecting system statistics")
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "asyncio": {},
        "system": {}
    }
    
    try:
        # Asyncio statistics
        tasks = asyncio.all_tasks()
        stats["asyncio"]["total_tasks"] = len(tasks)
        stats["asyncio"]["pending_tasks"] = len([t for t in tasks if not t.done()])
        
        # System statistics
        import psutil
        stats["system"]["memory_percent"] = psutil.virtual_memory().percent
        stats["system"]["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        
        # Disk usage (platform-specific)
        disk_path = "C:\\" if sys.platform == "win32" else "/"
        stats["system"]["disk_percent"] = psutil.disk_usage(disk_path).percent
        
        logger.info(
            f"System Stats - "
            f"Tasks: {stats['asyncio']['total_tasks']}, "
            f"Memory: {stats['system']['memory_percent']:.1f}%, "
            f"CPU: {stats['system']['cpu_percent']:.1f}%, "
            f"Disk: {stats['system']['disk_percent']:.1f}%"
        )
        
    except Exception as e:
        logger.error(f"Error collecting statistics: {e}", exc_info=True)
        stats["error"] = str(e)
    
    return stats


# Example periodic task configuration
# These can be imported and used in main.py to register tasks

MAINTENANCE_TASKS = [
    {
        "name": "cleanup_old_runs",
        "interval": timedelta(hours=1),
        "func": cleanup_old_runs,
        "kwargs": {"max_age_hours": 24},
        "description": "Clean up run data older than 24 hours"
    },
    {
        "name": "system_health_check",
        "interval": timedelta(minutes=5),
        "func": check_system_health,
        "description": "Monitor system resource usage"
    },
    {
        "name": "cleanup_temp_files",
        "interval": timedelta(hours=6),
        "func": cleanup_temp_files,
        "kwargs": {"max_age_hours": 24},
        "description": "Clean up temporary files older than 24 hours"
    },
    {
        "name": "log_statistics",
        "interval": timedelta(minutes=15),
        "func": log_statistics,
        "description": "Log system statistics for monitoring"
    },
]
