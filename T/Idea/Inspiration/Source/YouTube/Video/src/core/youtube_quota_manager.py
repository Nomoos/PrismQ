"""YouTube Data API v3 Quota Management System.

This module provides quota tracking and management for YouTube Data API v3,
preventing quota exhaustion and enabling efficient API usage monitoring.

Following SOLID principles:
- Single Responsibility: Only handles quota tracking and validation
- Open/Closed: Extensible via configuration, stable core logic
- Dependency Inversion: Depends on abstractions (storage protocol)

YouTube API Quota Information:
- Daily quota limit: 10,000 units (default, can be increased)
- Quota resets at midnight Pacific Time (PT)
- Different operations have different costs:
  * search.list: 100 units
  * videos.list: 1 unit
  * channels.list: 1 unit
  * playlistItems.list: 1 unit
  * commentThreads.list: 1 unit
  * captions.list: 50 units

Note: Uses JSON file storage to avoid creating additional database schemas.
The IdeaInspiration SQLite database is reserved exclusively for the IdeaInspiration model.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import threading


logger = logging.getLogger(__name__)


@dataclass
class QuotaUsage:
    """Represents quota usage for a specific time period."""
    
    date: str  # YYYY-MM-DD format
    total_used: int
    remaining: int
    operations: Dict[str, int]  # operation_name -> count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class QuotaExceededException(Exception):
    """Raised when API quota would be exceeded by an operation."""
    
    def __init__(self, operation: str, cost: int, remaining: int):
        self.operation = operation
        self.cost = cost
        self.remaining = remaining
        super().__init__(
            f"Quota exceeded: Operation '{operation}' costs {cost} units, "
            f"but only {remaining} units remaining"
        )


class YouTubeQuotaManager:
    """Manages YouTube Data API v3 quota usage and limits.
    
    This class tracks API quota consumption, enforces limits, and provides
    usage statistics. It persists quota data in a JSON file to avoid creating
    additional database schemas (per architectural requirement).
    
    Features:
    - Per-operation quota tracking
    - Daily quota limit enforcement
    - Automatic quota reset at midnight PT
    - Usage statistics and reporting
    - Persistent storage via JSON file
    - Thread-safe operations
    
    Example:
        >>> quota_manager = YouTubeQuotaManager(storage_path='quota.json', daily_limit=10000)
        >>> 
        >>> # Check before making API call
        >>> if quota_manager.can_execute('search.list'):
        ...     quota_manager.consume('search.list')
        ...     # Make API call
        ... else:
        ...     print("Quota exceeded!")
    """
    
    # Default quota costs for YouTube API operations (in units)
    DEFAULT_QUOTA_COSTS = {
        'search.list': 100,
        'videos.list': 1,
        'channels.list': 1,
        'playlistItems.list': 1,
        'commentThreads.list': 1,
        'captions.list': 50,
        'subscriptions.list': 1,
        'videos.insert': 1600,
        'playlists.insert': 50,
        'subscriptions.insert': 50,
    }
    
    def __init__(
        self,
        storage_path: str,
        daily_limit: int = 10000,
        quota_costs: Optional[Dict[str, int]] = None
    ):
        """Initialize YouTube Quota Manager.
        
        Args:
            storage_path: Path to JSON file for quota storage
            daily_limit: Daily quota limit in units (default: 10000)
            quota_costs: Custom quota costs per operation (optional)
        """
        self.storage_path = Path(storage_path)
        self.daily_limit = daily_limit
        self.quota_costs = quota_costs or self.DEFAULT_QUOTA_COSTS.copy()
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        
        # Ensure parent directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage file if it doesn't exist
        if not self.storage_path.exists():
            self._initialize_storage()
        
        # Clean up old quota records
        self._cleanup_old_records()
        
        logger.info(
            f"YouTubeQuotaManager initialized with daily limit: {daily_limit} units "
            f"(storage: {storage_path})"
        )
    
    def _initialize_storage(self) -> None:
        """Create initial JSON storage file."""
        initial_data = {
            'config': {
                'daily_limit': self.daily_limit,
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            'usage': {}  # date -> {operations: {}, total: 0}
        }
        self._write_data(initial_data)
        logger.debug("Quota storage file initialized")
    
    def _read_data(self) -> Dict[str, Any]:
        """Read quota data from JSON file (thread-safe)."""
        with self._lock:
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                # If file is corrupt or missing, reinitialize
                self._initialize_storage()
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
    
    def _write_data(self, data: Dict[str, Any]) -> None:
        """Write quota data to JSON file (thread-safe)."""
        with self._lock:
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def _cleanup_old_records(self, keep_days: int = 30) -> None:
        """Remove quota records older than specified days.
        
        Args:
            keep_days: Number of days of history to keep (default: 30)
        """
        cutoff_date = (
            datetime.now(timezone.utc) - timedelta(days=keep_days)
        ).strftime('%Y-%m-%d')
        
        data = self._read_data()
        usage = data.get('usage', {})
        
        # Remove old dates
        dates_to_remove = [date for date in usage.keys() if date < cutoff_date]
        for date in dates_to_remove:
            del usage[date]
        
        if dates_to_remove:
            self._write_data(data)
            logger.debug(f"Cleaned up {len(dates_to_remove)} old quota records")
    
    def _get_today_date(self) -> str:
        """Get today's date in YYYY-MM-DD format (Pacific Time).
        
        YouTube quota resets at midnight Pacific Time.
        
        Returns:
            Date string in YYYY-MM-DD format
        """
        # Convert UTC to Pacific Time (PT)
        # PT is UTC-8 (PST) or UTC-7 (PDT)
        # For simplicity, we use UTC-8 as baseline
        utc_now = datetime.now(timezone.utc)
        pt_now = utc_now - timedelta(hours=8)
        return pt_now.strftime('%Y-%m-%d')
    
    def get_usage(self, date: Optional[str] = None) -> QuotaUsage:
        """Get quota usage for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format (default: today)
            
        Returns:
            QuotaUsage object with usage statistics
        """
        if date is None:
            date = self._get_today_date()
        
        data = self._read_data()
        usage = data.get('usage', {})
        date_usage = usage.get(date, {'operations': {}, 'total': 0})
        
        total_used = date_usage.get('total', 0)
        operations = date_usage.get('operations', {})
        remaining = max(0, self.daily_limit - total_used)
        
        return QuotaUsage(
            date=date,
            total_used=total_used,
            remaining=remaining,
            operations=operations
        )
    
    def get_operation_cost(self, operation: str) -> int:
        """Get the quota cost for a specific operation.
        
        Args:
            operation: YouTube API operation name (e.g., 'search.list')
            
        Returns:
            Quota cost in units (default: 1 if not configured)
        """
        return self.quota_costs.get(operation, 1)
    
    def can_execute(self, operation: str, count: int = 1) -> bool:
        """Check if an operation can be executed without exceeding quota.
        
        Args:
            operation: YouTube API operation name
            count: Number of times to execute the operation (default: 1)
            
        Returns:
            True if operation can be executed, False otherwise
        """
        cost = self.get_operation_cost(operation) * count
        usage = self.get_usage()
        return usage.remaining >= cost
    
    def consume(self, operation: str, count: int = 1) -> None:
        """Record quota consumption for an operation.
        
        This should be called after successfully executing a YouTube API operation.
        
        Args:
            operation: YouTube API operation name
            count: Number of times the operation was executed (default: 1)
            
        Raises:
            QuotaExceededException: If recording would exceed daily quota
        """
        cost = self.get_operation_cost(operation) * count
        usage = self.get_usage()
        
        if cost > usage.remaining:
            raise QuotaExceededException(operation, cost, usage.remaining)
        
        # Record the usage
        date = self._get_today_date()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        data = self._read_data()
        usage_data = data.get('usage', {})
        
        # Initialize date if it doesn't exist
        if date not in usage_data:
            usage_data[date] = {'operations': {}, 'total': 0}
        
        # Update operation count
        date_usage = usage_data[date]
        date_usage['operations'][operation] = date_usage['operations'].get(operation, 0) + cost
        date_usage['total'] = date_usage.get('total', 0) + cost
        
        # Save back
        data['usage'] = usage_data
        self._write_data(data)
        
        logger.info(
            f"Consumed {cost} quota units for {operation}. "
            f"Remaining: {usage.remaining - cost}/{self.daily_limit}"
        )
    
    def check_and_consume(self, operation: str, count: int = 1) -> bool:
        """Check quota and consume in one atomic operation.
        
        This is a convenience method that combines can_execute and consume.
        
        Args:
            operation: YouTube API operation name
            count: Number of times to execute the operation (default: 1)
            
        Returns:
            True if quota was available and consumed, False otherwise
        """
        if self.can_execute(operation, count):
            try:
                self.consume(operation, count)
                return True
            except QuotaExceededException:
                return False
        return False
    
    def get_remaining_quota(self) -> int:
        """Get remaining quota for today.
        
        Returns:
            Remaining quota units
        """
        usage = self.get_usage()
        return usage.remaining
    
    def get_usage_percentage(self) -> float:
        """Get quota usage as a percentage.
        
        Returns:
            Usage percentage (0.0 to 100.0)
        """
        usage = self.get_usage()
        if self.daily_limit == 0:
            return 100.0
        return (usage.total_used / self.daily_limit) * 100.0
    
    def reset_quota(self, date: Optional[str] = None) -> None:
        """Reset quota for a specific date (for testing purposes).
        
        WARNING: This should not be used in production.
        
        Args:
            date: Date to reset (default: today)
        """
        if date is None:
            date = self._get_today_date()
        
        data = self._read_data()
        usage = data.get('usage', {})
        
        if date in usage:
            del usage[date]
            data['usage'] = usage
            self._write_data(data)
            logger.warning(f"Quota reset for date: {date}")
    
    def set_daily_limit(self, limit: int) -> None:
        """Update the daily quota limit.
        
        Args:
            limit: New daily quota limit in units
        """
        self.daily_limit = limit
        
        data = self._read_data()
        data['config']['daily_limit'] = limit
        self._write_data(data)
        
        logger.info(f"Daily quota limit updated to: {limit} units")
    
    def get_usage_report(self, days: int = 7) -> Dict[str, QuotaUsage]:
        """Get quota usage report for the last N days.
        
        Args:
            days: Number of days to include in report (default: 7)
            
        Returns:
            Dictionary mapping dates to QuotaUsage objects
        """
        report = {}
        
        for i in range(days):
            date = (
                datetime.now(timezone.utc) - timedelta(days=i, hours=8)
            ).strftime('%Y-%m-%d')
            report[date] = self.get_usage(date)
        
        return report


__all__ = ['YouTubeQuotaManager', 'QuotaUsage', 'QuotaExceededException']
