"""TaskList CRUD API endpoints.

TaskList represents the current tasks in the system - the actual instances
of tasks that need to be or are being executed.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query

from ..models.task_list import TaskListCreate, TaskListUpdate, TaskListResponse, TaskStatus
from ..database import APIDatabase

router = APIRouter()
logger = logging.getLogger(__name__)

# Module-level database instance (singleton pattern)
_db_instance: Optional[APIDatabase] = None


def get_api_db() -> APIDatabase:
    """Get API database instance using dependency injection."""
    global _db_instance
    if _db_instance is None:
        _db_instance = APIDatabase()
        _db_instance.initialize_schema()
    return _db_instance


@router.post("/tasks", response_model=TaskListResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskListCreate,
    db: APIDatabase = Depends(get_api_db)
) -> TaskListResponse:
    """Create a new task.
    
    Create a new task instance for a registered task type.
    
    Args:
        task: Task data
        db: Database instance (injected)
        
    Returns:
        Created task
        
    Raises:
        HTTPException: If task type doesn't exist
    """
    try:
        # Verify task type exists
        task_type = db.get_task_type(task.task_type_id)
        if not task_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task type {task.task_type_id} not found"
            )
        
        if not task_type.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Task type {task.task_type_id} is not active"
            )
        
        result = db.create_task(task)
        logger.info(f"Created task {result.id} of type {task.task_type_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/tasks", response_model=List[TaskListResponse])
async def list_tasks(
    task_type_id: Optional[int] = Query(None, description="Filter by task type ID"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks to return"),
    db: APIDatabase = Depends(get_api_db)
) -> List[TaskListResponse]:
    """List tasks.
    
    Retrieve tasks with optional filtering by task type and status.
    
    Args:
        task_type_id: Optional task type filter
        status: Optional status filter
        limit: Maximum number of tasks to return
        db: Database instance (injected)
        
    Returns:
        List of tasks
    """
    try:
        return db.list_tasks(task_type_id=task_type_id, status=status, limit=limit)
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskListResponse)
async def get_task(
    task_id: int,
    db: APIDatabase = Depends(get_api_db)
) -> TaskListResponse:
    """Get a specific task by ID.
    
    Args:
        task_id: Task ID
        db: Database instance (injected)
        
    Returns:
        Task details
        
    Raises:
        HTTPException: If task not found
    """
    try:
        result = db.get_task(task_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task: {str(e)}"
        )


@router.put("/tasks/{task_id}", response_model=TaskListResponse)
async def update_task(
    task_id: int,
    update: TaskListUpdate,
    db: APIDatabase = Depends(get_api_db)
) -> TaskListResponse:
    """Update a task.
    
    Update an existing task's properties. Only provided fields will be updated.
    
    Args:
        task_id: Task ID
        update: Update data
        db: Database instance (injected)
        
    Returns:
        Updated task
        
    Raises:
        HTTPException: If task not found
    """
    try:
        # Check if task exists
        existing = db.get_task(task_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        result = db.update_task(task_id, update)
        logger.info(f"Updated task {task_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: APIDatabase = Depends(get_api_db)
) -> None:
    """Delete a task.
    
    Permanently delete a task from the system.
    
    Args:
        task_id: Task ID
        db: Database instance (injected)
        
    Raises:
        HTTPException: If task not found
    """
    try:
        success = db.delete_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        logger.info(f"Deleted task {task_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )
