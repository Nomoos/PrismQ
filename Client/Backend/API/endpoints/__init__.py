"""API endpoints initialization."""

from .task_types import router as task_types_router
from .task_list import router as task_list_router

__all__ = ["task_types_router", "task_list_router"]
