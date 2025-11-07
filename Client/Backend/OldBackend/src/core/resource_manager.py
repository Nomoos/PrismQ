"""Resource management for concurrent module runs."""

import logging
from typing import Optional

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)


class ResourceManager:
    """
    Manage system resources for concurrent module runs.
    
    Responsibilities:
    - Monitor CPU usage
    - Monitor memory availability
    - Determine if resources are available for new runs
    
    This class follows SOLID principles:
    - Single Responsibility: Only handles resource monitoring
    - Open/Closed: Can be extended with GPU monitoring
    - Interface Segregation: Provides minimal, focused methods
    """
    
    def __init__(
        self,
        cpu_threshold_percent: float = 80.0,
        memory_required_gb: float = 4.0
    ):
        """
        Initialize resource manager.
        
        Args:
            cpu_threshold_percent: Maximum CPU usage (0-100) before rejecting new runs
            memory_required_gb: Minimum available memory in GB required for new runs
        """
        self.cpu_threshold_percent = cpu_threshold_percent
        self.memory_required_bytes = int(memory_required_gb * 1024 * 1024 * 1024)
        
        if psutil is None:
            logger.warning(
                "psutil not available - resource checks will always return True"
            )
    
    def check_resources_available(self) -> tuple[bool, Optional[str]]:
        """
        Check if system resources are available for a new run.
        
        Returns:
            Tuple of (available: bool, reason: Optional[str])
            - (True, None) if resources are available
            - (False, reason) if resources are insufficient
        """
        if psutil is None:
            # If psutil not available, allow run but log warning
            return True, None
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent > self.cpu_threshold_percent:
            reason = f"CPU usage too high: {cpu_percent:.1f}% (threshold: {self.cpu_threshold_percent}%)"
            logger.warning(reason)
            return False, reason
        
        # Check available memory
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024 * 1024 * 1024)
        required_gb = self.memory_required_bytes / (1024 * 1024 * 1024)
        
        if memory.available < self.memory_required_bytes:
            reason = f"Insufficient memory: {available_gb:.1f}GB available (required: {required_gb:.1f}GB)"
            logger.warning(reason)
            return False, reason
        
        logger.debug(
            f"Resources available - CPU: {cpu_percent:.1f}%, "
            f"Memory: {available_gb:.1f}GB available"
        )
        return True, None
    
    def get_system_stats(self) -> dict:
        """
        Get current system resource statistics.
        
        Returns:
            Dictionary with CPU and memory statistics
        """
        if psutil is None:
            return {
                "cpu_percent": 0.0,
                "memory_total_gb": 0.0,
                "memory_available_gb": 0.0,
                "memory_used_percent": 0.0,
                "psutil_available": False
            }
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return {
            "cpu_percent": cpu_percent,
            "memory_total_gb": memory.total / (1024 * 1024 * 1024),
            "memory_available_gb": memory.available / (1024 * 1024 * 1024),
            "memory_used_percent": memory.percent,
            "psutil_available": True
        }
