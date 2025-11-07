"""TaskType CRUD API endpoints.

TaskType represents a registration of task types that microservices can perform.
It's not tied to workers or specific implementations.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query

from ..models.task_type import TaskTypeCreate, TaskTypeUpdate, TaskTypeResponse
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


@router.post("/task-types", response_model=TaskTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_task_type(
    task_type: TaskTypeCreate,
    db: APIDatabase = Depends(get_api_db)
) -> TaskTypeResponse:
    """Create a new task type.
    
    Register a new task type that microservices can use. This is just a registry
    entry and doesn't require any worker implementation.
    
    Args:
        task_type: Task type data
        db: Database instance (injected)
        
    Returns:
        Created task type
        
    Raises:
        HTTPException: If task type with same name already exists
    """
    try:
        # Check if task type with same name exists
        existing = db.get_task_type_by_name(task_type.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Task type with name '{task_type.name}' already exists"
            )
        
        result = db.create_task_type(task_type)
        logger.info(f"Created task type: {result.name} (ID: {result.id})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task type: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task type: {str(e)}"
        )


@router.get("/task-types", response_model=List[TaskTypeResponse])
async def list_task_types(
    include_inactive: bool = Query(False, description="Include inactive task types"),
    db: APIDatabase = Depends(get_api_db)
) -> List[TaskTypeResponse]:
    """List all task types.
    
    Retrieve all registered task types, optionally including inactive ones.
    
    Args:
        include_inactive: Whether to include inactive task types
        db: Database instance (injected)
        
    Returns:
        List of task types
    """
    try:
        return db.list_task_types(include_inactive=include_inactive)
    except Exception as e:
        logger.error(f"Error listing task types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list task types: {str(e)}"
        )


@router.get("/task-types/{task_type_id}", response_model=TaskTypeResponse)
async def get_task_type(
    task_type_id: int,
    db: APIDatabase = Depends(get_api_db)
) -> TaskTypeResponse:
    """Get a specific task type by ID.
    
    Args:
        task_type_id: Task type ID
        db: Database instance (injected)
        
    Returns:
        Task type details
        
    Raises:
        HTTPException: If task type not found
    """
    try:
        result = db.get_task_type(task_type_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task type {task_type_id} not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task type {task_type_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task type: {str(e)}"
        )


@router.put("/task-types/{task_type_id}", response_model=TaskTypeResponse)
async def update_task_type(
    task_type_id: int,
    update: TaskTypeUpdate,
    db: APIDatabase = Depends(get_api_db)
) -> TaskTypeResponse:
    """Update a task type.
    
    Update an existing task type's properties. Only provided fields will be updated.
    
    Args:
        task_type_id: Task type ID
        update: Update data
        db: Database instance (injected)
        
    Returns:
        Updated task type
        
    Raises:
        HTTPException: If task type not found
    """
    try:
        # Check if task type exists
        existing = db.get_task_type(task_type_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task type {task_type_id} not found"
            )
        
        result = db.update_task_type(task_type_id, update)
        logger.info(f"Updated task type {task_type_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task type {task_type_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task type: {str(e)}"
        )


@router.delete("/task-types/{task_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_type(
    task_type_id: int,
    db: APIDatabase = Depends(get_api_db)
) -> None:
    """Delete a task type (soft delete).
    
    Mark a task type as inactive. This is a soft delete - the task type remains
    in the database but is marked as inactive.
    
    Args:
        task_type_id: Task type ID
        db: Database instance (injected)
        
    Raises:
        HTTPException: If task type not found
    """
    try:
        success = db.delete_task_type(task_type_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task type {task_type_id} not found"
            )
        
        logger.info(f"Deleted task type {task_type_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task type {task_type_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task type: {str(e)}"
        )
