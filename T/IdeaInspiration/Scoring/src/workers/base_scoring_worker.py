"""Base worker implementation for Scoring tasks.

Follows SOLID principles:
- Single Responsibility: Manages task lifecycle for scoring operations
- Open/Closed: Extensible through subclassing
- Liskov Substitution: Can be used anywhere WorkerProtocol is expected
- Interface Segregation: Focused worker interface
- Dependency Inversion: Depends on abstractions (Config, ScoringEngine)

Uses TaskManager API (external service) for task coordination.
"""

import logging
import time
import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from abc import ABC, abstractmethod

from . import Task, TaskResult, TaskStatus, WorkerProtocol
from ..config import Config
from ..scoring import ScoringEngine

# Import TaskManager API Client for task coordination
try:
    from TaskManager import TaskManagerClient, ResourceNotFoundError
    _taskmanager_available = True
except ImportError:
    _taskmanager_available = False
    ResourceNotFoundError = Exception  # Fallback
    TaskManagerClient = None  # Fallback


logger = logging.getLogger(__name__)


class BaseScoringWorker(ABC):
    """Base worker class for scoring operations.
    
    Provides common functionality for task claiming, processing, and reporting.
    Subclasses implement specific scoring logic via process_task().
    
    Follows Dependency Inversion Principle:
    - Depends on abstractions (Config, ScoringEngine)
    - Dependencies injected via constructor
    """
    
    def __init__(
        self,
        worker_id: str,
        config: Config,
        scoring_engine: ScoringEngine,
        claiming_policy: str = "FIFO",
        poll_interval: int = 5,
        max_backoff: int = 60,
        backoff_multiplier: float = 1.5,
        enable_autoscore: bool = True,
        autoscore_db_path: Optional[str] = None,
        autoscore_batch_size: int = 10,
    ):
        """Initialize scoring worker with injected dependencies.
        
        Args:
            worker_id: Unique worker identifier
            config: Configuration object
            scoring_engine: Scoring engine for processing tasks
            claiming_policy: Task claiming strategy - "FIFO", "LIFO", or "PRIORITY"
            poll_interval: Base polling interval in seconds
            max_backoff: Maximum backoff time in seconds
            backoff_multiplier: Backoff multiplier for exponential backoff
            enable_autoscore: Enable automatic scoring of unscored IdeaInspiration items
            autoscore_db_path: Path to IdeaInspiration database (default: auto-detect)
            autoscore_batch_size: Number of unscored items to fetch at once
        """
        self.worker_id = worker_id
        self.config = config
        self.scoring_engine = scoring_engine
        self.claiming_policy = claiming_policy
        self.poll_interval = poll_interval
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        self.enable_autoscore = enable_autoscore
        self.autoscore_batch_size = autoscore_batch_size
        
        # Auto-detect IdeaInspiration database path if not provided
        if autoscore_db_path:
            self.autoscore_db_path = autoscore_db_path
        else:
            # Default: Model/data/idea_inspiration.db relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            self.autoscore_db_path = str(project_root / "Model" / "data" / "idea_inspiration.db")
        
        # State
        self.running = False
        self.current_task: Optional[Task] = None
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.autoscored_items = 0
        self.start_time = time.time()
        
        # Backoff state
        self._current_backoff = poll_interval
        
        # IdeaInspiration database connection (lazy initialization)
        self._idea_db_conn = None
        
        # TaskManager API client (required for this implementation)
        if not _taskmanager_available:
            raise ImportError(
                "TaskManager module not available. Install with: "
                "pip install -e Source/TaskManager"
            )
        
        try:
            self.taskmanager_client = TaskManagerClient()
            logger.info(f"TaskManager API client initialized for worker {worker_id}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize TaskManager client: {e}")
        
        # Task type IDs (populated during registration)
        self.task_type_ids: List[int] = []
        
        logger.info(
            f"Worker {self.worker_id} initialized "
            f"(policy: {self.claiming_policy}, poll_interval: {poll_interval}s, "
            f"max_backoff: {max_backoff}s, autoscore: {enable_autoscore})"
        )
    
    @property
    def idea_db_conn(self) -> Optional[sqlite3.Connection]:
        """Lazy IdeaInspiration database connection (one per worker)."""
        if not self.enable_autoscore:
            return None
        
        if self._idea_db_conn is None:
            # Check if database exists
            db_path = Path(self.autoscore_db_path)
            if not db_path.exists():
                logger.warning(
                    f"IdeaInspiration database not found: {self.autoscore_db_path}. "
                    "Auto-scoring disabled."
                )
                return None
            
            try:
                self._idea_db_conn = sqlite3.connect(
                    self.autoscore_db_path,
                    check_same_thread=False
                )
                self._idea_db_conn.row_factory = sqlite3.Row
                logger.info(f"Connected to IdeaInspiration database: {self.autoscore_db_path}")
            except Exception as e:
                logger.error(f"Failed to connect to IdeaInspiration database: {e}")
                return None
        
        return self._idea_db_conn
    
    def register_task_types(self) -> None:
        """Register task types with TaskManager API.
        
        Should be overridden by subclasses to register their specific task types.
        """
        if not self.taskmanager_client:
            return
        
        logger.info("No task types to register (override register_task_types() in subclass)")
    
    def claim_task(self) -> Optional[Task]:
        """Claim a task from TaskManager API using configured policy.
        
        Returns:
            Task if available and claimed, None otherwise
        """
        # Configure sort parameters based on claiming policy
        if self.claiming_policy == "FIFO":
            sort_by = "created_at"
            sort_order = "ASC"  # Oldest first
        elif self.claiming_policy == "LIFO":
            sort_by = "created_at"
            sort_order = "DESC"  # Newest first
        elif self.claiming_policy == "PRIORITY":
            sort_by = "priority"
            sort_order = "DESC"  # Highest priority first
        else:
            # Default to FIFO
            sort_by = "created_at"
            sort_order = "ASC"
        
        # Try to claim from each registered task type
        for task_type_id in self.task_type_ids:
            try:
                claimed_task = self.taskmanager_client.claim_task(
                    worker_id=self.worker_id,
                    task_type_id=task_type_id,
                    sort_by=sort_by,
                    sort_order=sort_order
                )
                
                # Convert API response to Task object
                task = Task(
                    id=claimed_task['id'],
                    task_type=claimed_task['type'],
                    parameters=claimed_task['params'],
                    priority=claimed_task.get('priority', 0),
                    status=TaskStatus.CLAIMED,
                    retry_count=claimed_task.get('retry_count', 0),
                    max_retries=claimed_task.get('max_retries', 3),
                    created_at=claimed_task.get('created_at'),
                    claimed_at=datetime.now(timezone.utc).isoformat()
                )
                
                self.current_task = task
                
                # Reset backoff on successful claim
                self._current_backoff = self.poll_interval
                
                logger.info(
                    f"Worker {self.worker_id} claimed task {task.id} "
                    f"(type: {task.task_type}, task_type_id: {task_type_id})"
                )
                return task
                
            except ResourceNotFoundError:
                # No tasks available for this type, try next
                continue
            except Exception as e:
                logger.error(f"Error claiming task from type {task_type_id}: {e}")
                continue
        
        # No tasks available from any type
        return None
    
    def fetch_unscored_items(self) -> list[Dict[str, Any]]:
        """Fetch IdeaInspiration items without scores from the database.
        
        Returns:
            List of unscored item dictionaries
        """
        if not self.enable_autoscore or not self.idea_db_conn:
            return []
        
        try:
            cursor = self.idea_db_conn.cursor()
            
            # Fetch items where score is NULL
            cursor.execute("""
                SELECT id, title, description, content, metadata
                FROM IdeaInspiration
                WHERE score IS NULL
                ORDER BY created_at ASC
                LIMIT ?
            """, (self.autoscore_batch_size,))
            
            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row['id'],
                    'title': row['title'],
                    'description': row['description'] or '',
                    'content': row['content'] or '',
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                })
            
            if items:
                logger.info(f"Found {len(items)} unscored IdeaInspiration items")
            
            return items
            
        except Exception as e:
            logger.error(f"Error fetching unscored items: {e}")
            return []
    
    def create_autoscore_task(self, item: Dict[str, Any]) -> Optional[int]:
        """Create a scoring task from an unscored IdeaInspiration item via TaskManager API.
        
        Args:
            item: Unscored item dictionary
            
        Returns:
            Task ID if created successfully, None otherwise
        """
        try:
            # Create task parameters
            parameters = {
                'title': item['title'],
                'description': item['description'],
                'text_content': item['content'],
                'metadata': item['metadata'],
                'idea_inspiration_id': item['id']  # Track which item this is for
            }
            
            # Find the TextScoring task type ID
            text_scoring_type_id = None
            for task_type_id in self.task_type_ids:
                # We need to check which ID corresponds to TextScoring
                # For now, assume first registered type is TextScoring
                # This should be improved by storing a mapping
                text_scoring_type_id = self.task_type_ids[0] if self.task_type_ids else None
                break
            
            if not text_scoring_type_id:
                logger.error("No TextScoring task type registered, cannot create auto-score task")
                return None
            
            # Create task via TaskManager API
            created_task = self.taskmanager_client.create_task(
                task_type_id=text_scoring_type_id,
                params=parameters,
                priority=0  # Normal priority
            )
            
            task_id = created_task['id']
            logger.debug(f"Created auto-scoring task {task_id} for IdeaInspiration item {item['id']}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating auto-score task for item {item.get('id')}: {e}")
            return None
    
    def update_idea_inspiration_score(self, idea_id: int, score: float) -> bool:
        """Update the score for an IdeaInspiration item.
        
        Args:
            idea_id: Database ID of the IdeaInspiration item
            score: Score value to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        if not self.idea_db_conn:
            return False
        
        try:
            cursor = self.idea_db_conn.cursor()
            cursor.execute("""
                UPDATE IdeaInspiration
                SET score = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (int(round(score)), idea_id))
            self.idea_db_conn.commit()
            
            logger.info(f"Updated IdeaInspiration item {idea_id} with score {score:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating score for IdeaInspiration item {idea_id}: {e}")
            return False
    
    def process_autoscore_mode(self) -> bool:
        """Process unscored items when in auto-score mode.
        
        Fetches unscored IdeaInspiration items and creates tasks for them.
        
        Returns:
            True if tasks were created, False otherwise
        """
        if not self.enable_autoscore:
            return False
        
        # Fetch unscored items
        unscored_items = self.fetch_unscored_items()
        if not unscored_items:
            return False
        
        # Create tasks for unscored items
        tasks_created = 0
        for item in unscored_items:
            if self.create_autoscore_task(item):
                tasks_created += 1
        
        if tasks_created > 0:
            logger.info(f"Created {tasks_created} auto-scoring tasks from unscored IdeaInspiration items")
            self.autoscored_items += tasks_created
            return True
        
        return False
    
    @abstractmethod
    def process_task(self, task: Task) -> TaskResult:
        """Process a claimed task - MUST be implemented by subclass.
        
        This is where the actual scoring logic goes.
        Subclasses implement specific scoring behavior.
        
        Args:
            task: The task to process
            
        Returns:
            TaskResult with success status and data
        """
        pass
    
    def report_result(self, task: Task, result: TaskResult) -> None:
        """Report task result to TaskManager API.
        
        Updates:
        1. TaskManager API with completion status
        2. IdeaInspiration database with calculated score (if auto-scored)
        
        Args:
            task: The completed task
            result: The execution result
        """
        try:
            # Update statistics
            if result.success:
                self.tasks_processed += 1
            else:
                self.tasks_failed += 1
            
            # Update IdeaInspiration database with score if this was an auto-score task
            if result.success and result.data and 'overall_score' in result.data:
                # Check if this task has an idea_inspiration_id
                idea_id = task.parameters.get('idea_inspiration_id')
                if idea_id and self.enable_autoscore:
                    score = result.data['overall_score']
                    self.update_idea_inspiration_score(idea_id, score)
            
            # Report completion to TaskManager API
            self._update_task_manager(task, result)
            
            status_str = "completed" if result.success else "failed"
            logger.info(
                f"Worker {self.worker_id} completed task {task.id} "
                f"(status: {status_str}, items: {result.items_processed})"
            )
            
        except Exception as e:
            logger.error(f"Error reporting result: {e}")
    
    def _update_task_manager(self, task: Task, result: TaskResult) -> None:
        """Update TaskManager API with task completion status.
        
        Reports task results to external TaskManager API.
        
        Args:
            task: The completed task
            result: The execution result
        """
        try:
            # Prepare result data for TaskManager API
            result_data = None
            if result.success and result.data:
                result_data = {
                    "items_processed": result.items_processed,
                    "data_summary": {
                        "total_items": result.items_processed,
                        "processed_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            
            # Report completion to TaskManager API
            self.taskmanager_client.complete_task(
                task_id=task.id,
                worker_id=self.worker_id,
                success=result.success,
                result=result_data,
                error=result.error
            )
            
            logger.debug(
                f"Task {task.id} status reported to TaskManager API "
                f"(success: {result.success})"
            )
            
        except Exception as e:
            # This is critical now since we don't have a local queue
            logger.error(
                f"CRITICAL: Failed to report task {task.id} to TaskManager API: {e}. "
                "Task result may be lost!"
            )
            raise  # Re-raise since this is now critical
    
    def run_once(self) -> bool:
        """Execute one iteration of the worker loop.
        
        Returns:
            True if a task was processed, False otherwise
        """
        # Try to claim a task
        task = self.claim_task()
        if not task:
            return False
        
        try:
            # Process the task
            result = self.process_task(task)
            
            # Report the result
            self.report_result(task, result)
            
            return True
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error processing task {task.id}: {e}")
            result = TaskResult(
                success=False,
                error=str(e)
            )
            self.report_result(task, result)
            return False
        
        finally:
            self.current_task = None
    
    def run(self, max_iterations: Optional[int] = None) -> None:
        """Run the worker loop with exponential backoff.
        
        Args:
            max_iterations: Maximum iterations (None = infinite)
        """
        # Register task types on startup
        self.register_task_types()
        
        self.running = True
        iteration = 0
        
        logger.info(f"Worker {self.worker_id} starting...")
        
        try:
            while self.running:
                # Check iteration limit
                if max_iterations and iteration >= max_iterations:
                    break
                
                # Process one task
                processed = self.run_once()
                
                # If no task was available, try auto-scoring mode
                if not processed and self.enable_autoscore:
                    # Check for unscored IdeaInspiration items
                    autoscore_created = self.process_autoscore_mode()
                    if autoscore_created:
                        # Reset backoff since we created tasks
                        self._current_backoff = self.poll_interval
                        # Don't increment iteration, let next loop process the new tasks
                        continue
                
                # Wait if no task was available with exponential backoff
                if not processed:
                    logger.debug(
                        f"Worker {self.worker_id} no task available, "
                        f"backing off for {self._current_backoff:.1f}s"
                    )
                    time.sleep(self._current_backoff)
                    self._increase_backoff()
                
                iteration += 1
                
        except KeyboardInterrupt:
            logger.info(f"Worker {self.worker_id} interrupted")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the worker gracefully."""
        self.running = False
        if self._idea_db_conn:
            self._idea_db_conn.close()
        
        # Log runtime statistics
        runtime = time.time() - self.start_time
        logger.info(
            f"Worker {self.worker_id} stopped "
            f"(runtime: {runtime:.1f}s, processed: {self.tasks_processed}, "
            f"failed: {self.tasks_failed}, autoscored: {self.autoscored_items})"
        )
    
    def _increase_backoff(self) -> None:
        """Increase backoff time exponentially up to max_backoff."""
        self._current_backoff = min(
            self._current_backoff * self.backoff_multiplier,
            self.max_backoff
        )
    



__all__ = ["BaseScoringWorker"]
