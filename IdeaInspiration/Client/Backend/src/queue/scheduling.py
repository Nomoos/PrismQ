"""
Task queue scheduling strategies.

Implements four different scheduling strategies for claiming tasks:
- FIFO: First-In-First-Out (oldest first)
- LIFO: Last-In-First-Out (newest first)
- Priority: Priority-based (lower number = higher priority)
- Weighted Random: Probabilistic selection weighted by priority

Part of Issue #327: Implement Queue Scheduling Strategies
"""

from typing import Optional, Dict, Any, Protocol
from abc import abstractmethod
import json

from .models import Task, SchedulingStrategy
from .database import QueueDatabase
from .exceptions import QueueDatabaseError


class TaskClaimer(Protocol):
    """
    Protocol for task claiming strategies.
    
    Follows SOLID Interface Segregation principle.
    Each strategy implements this interface to provide different
    task selection algorithms.
    """
    
    @abstractmethod
    def claim_task(
        self,
        worker_id: str,
        capabilities: Dict[str, Any],
        lease_seconds: int
    ) -> Optional[Task]:
        """
        Claim a single task based on strategy.
        
        Args:
            worker_id: Unique identifier for the worker
            capabilities: Worker capabilities for filtering compatible tasks
            lease_seconds: Duration to lease the task
            
        Returns:
            Task object if claimed, None if no tasks available
            
        Raises:
            QueueDatabaseError: If database operation fails
        """
        ...


class FIFOTaskClaimer:
    """
    First-In-First-Out task claiming strategy.
    
    Claims the oldest available task (lowest ID).
    Provides fair processing where submission order matters.
    """
    
    def __init__(self, db: QueueDatabase):
        """
        Initialize FIFO claimer.
        
        Args:
            db: QueueDatabase instance for database operations
        """
        self.db = db
    
    def claim_task(
        self,
        worker_id: str,
        capabilities: Dict[str, Any],
        lease_seconds: int
    ) -> Optional[Task]:
        """
        Claim oldest available task.
        
        Note: capabilities parameter is reserved for future capability filtering
        implementation but not currently used.
        
        Uses atomic transaction to ensure no duplicate claims.
        """
        # SQL query to claim oldest task (FIFO ordering by id ASC)
        claim_sql = """
        WITH candidate AS (
            SELECT id
            FROM task_queue
            WHERE status = 'queued'
                AND run_after_utc <= datetime('now')
            ORDER BY id ASC
            LIMIT 1
        )
        UPDATE task_queue
        SET status = 'leased',
            reserved_at_utc = datetime('now'),
            lease_until_utc = datetime('now', printf('+%d seconds', ?)),
            locked_by = ?
        WHERE id = (SELECT id FROM candidate)
        RETURNING *
        """
        
        try:
            with self.db.transaction() as conn:
                cursor = conn.execute(claim_sql, (lease_seconds, worker_id))
                row = cursor.fetchone()
                
                if row is None:
                    return None
                
                # Convert row to Task object
                task_dict = dict(row)
                return Task.from_dict(task_dict)
                
        except Exception as e:
            raise QueueDatabaseError(f"Failed to claim task: {e}") from e


class LIFOTaskClaimer:
    """
    Last-In-First-Out task claiming strategy.
    
    Claims the newest available task (highest ID).
    Useful for user-triggered operations where latest request should be prioritized.
    Warning: Can starve old tasks.
    """
    
    def __init__(self, db: QueueDatabase):
        """
        Initialize LIFO claimer.
        
        Args:
            db: QueueDatabase instance for database operations
        """
        self.db = db
    
    def claim_task(
        self,
        worker_id: str,
        capabilities: Dict[str, Any],
        lease_seconds: int
    ) -> Optional[Task]:
        """
        Claim newest available task.
        
        Note: capabilities parameter is reserved for future capability filtering
        implementation but not currently used.
        
        Uses atomic transaction to ensure no duplicate claims.
        """
        # SQL query to claim newest task (LIFO ordering by id DESC)
        claim_sql = """
        WITH candidate AS (
            SELECT id
            FROM task_queue
            WHERE status = 'queued'
                AND run_after_utc <= datetime('now')
            ORDER BY id DESC
            LIMIT 1
        )
        UPDATE task_queue
        SET status = 'leased',
            reserved_at_utc = datetime('now'),
            lease_until_utc = datetime('now', printf('+%d seconds', ?)),
            locked_by = ?
        WHERE id = (SELECT id FROM candidate)
        RETURNING *
        """
        
        try:
            with self.db.transaction() as conn:
                cursor = conn.execute(claim_sql, (lease_seconds, worker_id))
                row = cursor.fetchone()
                
                if row is None:
                    return None
                
                # Convert row to Task object
                task_dict = dict(row)
                return Task.from_dict(task_dict)
                
        except Exception as e:
            raise QueueDatabaseError(f"Failed to claim task: {e}") from e


class PriorityTaskClaimer:
    """
    Priority-based task claiming strategy.
    
    Claims the highest priority task (lowest priority number).
    Within same priority, uses FIFO ordering.
    Ideal for time-sensitive operations.
    """
    
    def __init__(self, db: QueueDatabase):
        """
        Initialize Priority claimer.
        
        Args:
            db: QueueDatabase instance for database operations
        """
        self.db = db
    
    def claim_task(
        self,
        worker_id: str,
        capabilities: Dict[str, Any],
        lease_seconds: int
    ) -> Optional[Task]:
        """
        Claim highest priority available task.
        
        Note: capabilities parameter is reserved for future capability filtering
        implementation but not currently used.
        
        Uses atomic transaction to ensure no duplicate claims.
        """
        # SQL query to claim highest priority task (priority ASC, then id ASC)
        claim_sql = """
        WITH candidate AS (
            SELECT id
            FROM task_queue
            WHERE status = 'queued'
                AND run_after_utc <= datetime('now')
            ORDER BY priority ASC, id ASC
            LIMIT 1
        )
        UPDATE task_queue
        SET status = 'leased',
            reserved_at_utc = datetime('now'),
            lease_until_utc = datetime('now', printf('+%d seconds', ?)),
            locked_by = ?
        WHERE id = (SELECT id FROM candidate)
        RETURNING *
        """
        
        try:
            with self.db.transaction() as conn:
                cursor = conn.execute(claim_sql, (lease_seconds, worker_id))
                row = cursor.fetchone()
                
                if row is None:
                    return None
                
                # Convert row to Task object
                task_dict = dict(row)
                return Task.from_dict(task_dict)
                
        except Exception as e:
            raise QueueDatabaseError(f"Failed to claim task: {e}") from e


class WeightedRandomTaskClaimer:
    """
    Weighted random task claiming strategy.
    
    Claims tasks probabilistically based on priority.
    Higher priority (lower number) has higher probability of being selected.
    
    Formula: RANDOM() * (1.0 / (priority + 1))
    - priority=1:   weight = 0.500  (highest)
    - priority=10:  weight = 0.091  (~5.5x less than p=1)
    - priority=100: weight = 0.010  (~50x less than p=1)
    
    Prevents complete starvation while still respecting priorities.
    """
    
    def __init__(self, db: QueueDatabase):
        """
        Initialize Weighted Random claimer.
        
        Args:
            db: QueueDatabase instance for database operations
        """
        self.db = db
    
    def claim_task(
        self,
        worker_id: str,
        capabilities: Dict[str, Any],
        lease_seconds: int
    ) -> Optional[Task]:
        """
        Claim task using weighted random selection.
        
        Note: capabilities parameter is reserved for future capability filtering
        implementation but not currently used.
        
        Uses atomic transaction to ensure no duplicate claims.
        """
        # SQL query with weighted random ordering
        claim_sql = """
        WITH candidate AS (
            SELECT id
            FROM task_queue
            WHERE status = 'queued'
                AND run_after_utc <= datetime('now')
            ORDER BY RANDOM() * (1.0 / (priority + 1)) DESC
            LIMIT 1
        )
        UPDATE task_queue
        SET status = 'leased',
            reserved_at_utc = datetime('now'),
            lease_until_utc = datetime('now', printf('+%d seconds', ?)),
            locked_by = ?
        WHERE id = (SELECT id FROM candidate)
        RETURNING *
        """
        
        try:
            with self.db.transaction() as conn:
                cursor = conn.execute(claim_sql, (lease_seconds, worker_id))
                row = cursor.fetchone()
                
                if row is None:
                    return None
                
                # Convert row to Task object
                task_dict = dict(row)
                return Task.from_dict(task_dict)
                
        except Exception as e:
            raise QueueDatabaseError(f"Failed to claim task: {e}") from e


class TaskClaimerFactory:
    """
    Factory for creating task claimers.
    
    Follows SOLID Open/Closed principle - can add strategies 
    without modifying existing code.
    """
    
    @staticmethod
    def create(
        strategy: SchedulingStrategy,
        db: QueueDatabase
    ) -> TaskClaimer:
        """
        Create task claimer based on strategy.
        
        Args:
            strategy: Scheduling strategy to use
            db: QueueDatabase instance
            
        Returns:
            TaskClaimer instance for the specified strategy
            
        Raises:
            ValueError: If strategy is unknown
        """
        if strategy == SchedulingStrategy.FIFO:
            return FIFOTaskClaimer(db)
        elif strategy == SchedulingStrategy.LIFO:
            return LIFOTaskClaimer(db)
        elif strategy == SchedulingStrategy.PRIORITY:
            return PriorityTaskClaimer(db)
        elif strategy == SchedulingStrategy.WEIGHTED_RANDOM:
            return WeightedRandomTaskClaimer(db)
        else:
            raise ValueError(f"Unknown scheduling strategy: {strategy}")
