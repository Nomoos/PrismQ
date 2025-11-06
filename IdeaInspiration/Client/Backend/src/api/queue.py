"""Queue management API endpoints."""

import json
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Query, Depends

from ..models.queue import (
    EnqueueTaskRequest,
    EnqueueTaskResponse,
    TaskStatusResponse,
    CancelTaskResponse,
    QueueStatsResponse,
)
from ..queue import QueueDatabase, Task, QueueDatabaseError, QueueBusyError

router = APIRouter()
logger = logging.getLogger(__name__)

# Module-level database instance (singleton pattern)
_db_instance: Optional[QueueDatabase] = None


def get_queue_db() -> QueueDatabase:
    """
    Get queue database instance using dependency injection.
    
    Returns:
        QueueDatabase: Singleton database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = QueueDatabase()
        _db_instance.initialize_schema()
    return _db_instance


def parse_utc_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """
    Parse UTC datetime string to datetime object.
    
    Args:
        dt_str: ISO format datetime string
        
    Returns:
        datetime object or None
    """
    if not dt_str:
        return None
    
    # Handle ISO format with T separator
    if "T" in dt_str:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    else:
        # SQLite datetime format: YYYY-MM-DD HH:MM:SS
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


@router.post("/queue/enqueue", response_model=EnqueueTaskResponse, status_code=status.HTTP_201_CREATED)
async def enqueue_task(request: EnqueueTaskRequest, db: QueueDatabase = Depends(get_queue_db)):
    """
    Enqueue a new task.
    
    Creates a new task in the queue with the specified parameters.
    Supports idempotency keys to prevent duplicate task creation.
    
    Args:
        request: Task enqueue request
        db: Queue database instance (injected)
        
    Returns:
        EnqueueTaskResponse: Created task information
        
    Raises:
        HTTPException: If task creation fails or idempotency conflict
    """
    try:
        # Check for existing task with same idempotency key
        if request.idempotency_key:
            cursor = db.execute(
                "SELECT id, status, created_at_utc FROM task_queue WHERE idempotency_key = ?",
                (request.idempotency_key,)
            )
            existing = cursor.fetchone()
            if existing:
                task_dict = dict(existing)
                logger.info(
                    f"Idempotency key '{request.idempotency_key}' already exists, "
                    f"returning existing task {task_dict['id']}"
                )
                return EnqueueTaskResponse(
                    task_id=task_dict["id"],
                    status=task_dict["status"],
                    created_at_utc=parse_utc_datetime(task_dict["created_at_utc"]),
                    message="Task already exists (idempotency key match)",
                )
        
        # Prepare task data
        payload_json = json.dumps(request.payload)
        compatibility_json = json.dumps(request.compatibility)
        run_after = request.run_after_utc or datetime.now(timezone.utc)
        
        # Insert task with transaction
        with db.transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO task_queue (
                    type, priority, payload, compatibility,
                    max_attempts, run_after_utc, idempotency_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.type,
                    request.priority,
                    payload_json,
                    compatibility_json,
                    request.max_attempts,
                    run_after.isoformat(),
                    request.idempotency_key,
                )
            )
            task_id = cursor.lastrowid
            
            # Fetch created task to get timestamps
            cursor = conn.execute(
                "SELECT status, created_at_utc FROM task_queue WHERE id = ?",
                (task_id,)
            )
            row = cursor.fetchone()
            task_dict = dict(row)
        
        logger.info(f"Enqueued task {task_id} of type '{request.type}' with priority {request.priority}")
        
        return EnqueueTaskResponse(
            task_id=task_id,
            status=task_dict["status"],
            created_at_utc=parse_utc_datetime(task_dict["created_at_utc"]),
            message="Task enqueued successfully",
        )
        
    except QueueBusyError as e:
        logger.error(f"Queue database busy: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Queue is currently busy, please retry",
        )
    except QueueDatabaseError as e:
        logger.error(f"Database error while enqueuing task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue task: {str(e)}",
        )


@router.get("/queue/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: int, db: QueueDatabase = Depends(get_queue_db)):
    """
    Get task status and details.
    
    Retrieves the current status and metadata for a specific task.
    
    Args:
        task_id: Unique task identifier
        db: Queue database instance (injected)
        
    Returns:
        TaskStatusResponse: Task status and details
        
    Raises:
        HTTPException: If task not found or database error
    """
    try:
        cursor = db.execute(
            """
            SELECT id, type, status, priority, attempts, max_attempts, payload,
                   compatibility, error_message, created_at_utc, processing_started_utc,
                   finished_at_utc, locked_by, run_after_utc, lease_until_utc,
                   reserved_at_utc, idempotency_key, updated_at_utc
            FROM task_queue WHERE id = ?
            """,
            (task_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        
        task = Task.from_dict(dict(row))
        return TaskStatusResponse.from_task(task)
        
    except HTTPException:
        raise
    except QueueDatabaseError as e:
        logger.error(f"Database error while fetching task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task status: {str(e)}",
        )


@router.post("/queue/tasks/{task_id}/cancel", response_model=CancelTaskResponse)
async def cancel_task(task_id: int, db: QueueDatabase = Depends(get_queue_db)):
    """
    Cancel a queued or processing task.
    
    Attempts to cancel a task. Only tasks in 'queued' or 'processing' status
    can be cancelled. Completed or failed tasks cannot be cancelled.
    
    Args:
        task_id: Unique task identifier
        db: Queue database instance (injected)
        
    Returns:
        CancelTaskResponse: Cancellation result
        
    Raises:
        HTTPException: If task not found, already completed, or database error
    """
    try:
        # Check current status
        cursor = db.execute(
            "SELECT status FROM task_queue WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        
        current_status = dict(row)["status"]
        
        # Only allow cancellation of queued or processing tasks
        if current_status in ("completed", "failed"):
            return CancelTaskResponse(
                task_id=task_id,
                status=current_status,
                message=f"Task already {current_status}, cannot cancel",
            )
        
        # Update status to failed with cancellation message
        with db.transaction() as conn:
            conn.execute(
                """
                UPDATE task_queue
                SET status = 'failed',
                    error_message = 'Cancelled by user',
                    finished_at_utc = datetime('now', 'utc'),
                    updated_at_utc = datetime('now', 'utc')
                WHERE id = ?
                """,
                (task_id,)
            )
        
        logger.info(f"Cancelled task {task_id} (was {current_status})")
        
        return CancelTaskResponse(
            task_id=task_id,
            status="failed",
            message="Task cancelled successfully",
        )
        
    except HTTPException:
        raise
    except QueueDatabaseError as e:
        logger.error(f"Database error while cancelling task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}",
        )


@router.get("/queue/stats", response_model=QueueStatsResponse)
async def get_queue_stats(db: QueueDatabase = Depends(get_queue_db)):
    """
    Get queue statistics.
    
    Provides aggregate statistics about the task queue including
    counts by status and age of oldest queued task.
    
    Args:
        db: Queue database instance (injected)
    
    Returns:
        QueueStatsResponse: Queue statistics
        
    Raises:
        HTTPException: If database error
    """
    try:
        # Get counts by status and oldest queued task age in single query
        cursor = db.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'queued' THEN 1 ELSE 0 END) as queued,
                SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                (
                    SELECT (julianday('now') - julianday(created_at_utc)) * 86400
                    FROM task_queue
                    WHERE status = 'queued'
                    ORDER BY created_at_utc ASC
                    LIMIT 1
                ) as oldest_queued_age_seconds
            FROM task_queue
            """
        )
        row = cursor.fetchone()
        stats = dict(row)
        
        return QueueStatsResponse(
            total_tasks=stats["total"] or 0,
            queued_tasks=stats["queued"] or 0,
            processing_tasks=stats["processing"] or 0,
            completed_tasks=stats["completed"] or 0,
            failed_tasks=stats["failed"] or 0,
            oldest_queued_age_seconds=stats["oldest_queued_age_seconds"],
        )
        
    except QueueDatabaseError as e:
        logger.error(f"Database error while fetching queue stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch queue stats: {str(e)}",
        )


@router.get("/queue/tasks", response_model=List[TaskStatusResponse])
async def list_tasks(
    db: QueueDatabase = Depends(get_queue_db),
    status: Optional[str] = Query(None, description="Filter by status"),
    type: Optional[str] = Query(None, description="Filter by task type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks to return"),
):
    """
    List tasks in the queue.
    
    Retrieves a list of tasks with optional filtering by status and type.
    
    Args:
        db: Queue database instance (injected)
        status: Optional status filter (queued, processing, completed, failed)
        type: Optional task type filter
        limit: Maximum number of tasks to return (default: 100, max: 1000)
        
    Returns:
        List[TaskStatusResponse]: List of tasks
        
    Raises:
        HTTPException: If database error
    """
    try:
        # Build query with explicit column selection
        query = """
            SELECT id, type, status, priority, attempts, max_attempts, payload,
                   compatibility, error_message, created_at_utc, processing_started_utc,
                   finished_at_utc, locked_by, run_after_utc, lease_until_utc,
                   reserved_at_utc, idempotency_key, updated_at_utc
            FROM task_queue WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if type:
            query += " AND type = ?"
            params.append(type)
        
        query += " ORDER BY created_at_utc DESC LIMIT ?"
        params.append(limit)
        
        cursor = db.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        tasks = [Task.from_dict(dict(row)) for row in rows]
        return [TaskStatusResponse.from_task(task) for task in tasks]
        
    except QueueDatabaseError as e:
        logger.error(f"Database error while listing tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}",
        )
