"""Database module for API task management.

Provides SQLite database operations for TaskType and TaskList.
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from .models.task_type import TaskTypeCreate, TaskTypeUpdate, TaskTypeResponse
from .models.task_list import TaskListCreate, TaskListUpdate, TaskListResponse, TaskStatus


class APIDatabase:
    """Database manager for API task types and task lists."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.
        
        Args:
            db_path: Path to database file. If None, uses default path.
        """
        if db_path is None:
            # Use same data directory as main queue database
            import os
            if os.name == "nt":  # Windows
                db_path = r"C:\Data\PrismQ\api\api.db"
            else:  # Linux/macOS
                db_path = "/tmp/prismq/api/api.db"
        
        self.db_path = Path(db_path)
        self._ensure_directory_exists()
        self._connection: Optional[sqlite3.Connection] = None
        
    def _ensure_directory_exists(self) -> None:
        """Create database directory if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get the active connection, creating it if necessary."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
            )
            self._connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def initialize_schema(self) -> None:
        """Create tables if they don't exist."""
        conn = self.get_connection()
        
        # TaskType table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                parameters_schema TEXT,
                metadata TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        
        # TaskList table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                parameters TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 100,
                metadata TEXT,
                result TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (task_type_id) REFERENCES task_types(id)
            )
        """)
        
        # Indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_types_name 
            ON task_types(name)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_list_type_status 
            ON task_list(task_type_id, status)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_list_created 
            ON task_list(created_at DESC)
        """)
        
        conn.commit()
    
    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    # TaskType CRUD operations
    
    def create_task_type(self, task_type: TaskTypeCreate) -> TaskTypeResponse:
        """Create a new task type."""
        now = datetime.now(timezone.utc).isoformat()
        
        with self.transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO task_types (name, description, parameters_schema, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    task_type.name,
                    task_type.description,
                    json.dumps(task_type.parameters_schema),
                    json.dumps(task_type.metadata),
                    now,
                )
            )
            task_id = cursor.lastrowid
        
        return self.get_task_type(task_id)
    
    def get_task_type(self, task_type_id: int) -> Optional[TaskTypeResponse]:
        """Get a task type by ID."""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM task_types WHERE id = ?",
            (task_type_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_task_type_response(row)
    
    def get_task_type_by_name(self, name: str) -> Optional[TaskTypeResponse]:
        """Get a task type by name."""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM task_types WHERE name = ?",
            (name,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_task_type_response(row)
    
    def list_task_types(self, include_inactive: bool = False) -> List[TaskTypeResponse]:
        """List all task types."""
        conn = self.get_connection()
        
        if include_inactive:
            cursor = conn.execute("SELECT * FROM task_types ORDER BY name")
        else:
            cursor = conn.execute("SELECT * FROM task_types WHERE is_active = 1 ORDER BY name")
        
        rows = cursor.fetchall()
        return [self._row_to_task_type_response(row) for row in rows]
    
    def update_task_type(self, task_type_id: int, update: TaskTypeUpdate) -> Optional[TaskTypeResponse]:
        """Update a task type."""
        now = datetime.now(timezone.utc).isoformat()
        
        # Build update query dynamically based on provided fields
        updates = []
        params = []
        
        if update.description is not None:
            updates.append("description = ?")
            params.append(update.description)
        
        if update.parameters_schema is not None:
            updates.append("parameters_schema = ?")
            params.append(json.dumps(update.parameters_schema))
        
        if update.metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(update.metadata))
        
        if update.is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if update.is_active else 0)
        
        if not updates:
            return self.get_task_type(task_type_id)
        
        updates.append("updated_at = ?")
        params.append(now)
        params.append(task_type_id)
        
        with self.transaction() as conn:
            # Note: Column names in updates list are safe - they are hardcoded strings, not user input
            # Only the parameter values are from user input and properly parameterized with ?
            query = f"UPDATE task_types SET {', '.join(updates)} WHERE id = ?"
            conn.execute(query, tuple(params))
        
        return self.get_task_type(task_type_id)
    
    def delete_task_type(self, task_type_id: int) -> bool:
        """Delete a task type (soft delete by marking inactive)."""
        with self.transaction() as conn:
            cursor = conn.execute(
                "UPDATE task_types SET is_active = 0, updated_at = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), task_type_id)
            )
            return cursor.rowcount > 0
    
    def _row_to_task_type_response(self, row: sqlite3.Row) -> TaskTypeResponse:
        """Convert database row to TaskTypeResponse."""
        return TaskTypeResponse(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            parameters_schema=json.loads(row["parameters_schema"]) if row["parameters_schema"] else {},
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )
    
    # TaskList CRUD operations
    
    def create_task(self, task: TaskListCreate) -> TaskListResponse:
        """Create a new task."""
        now = datetime.now(timezone.utc).isoformat()
        
        with self.transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO task_list (task_type_id, status, parameters, priority, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    task.task_type_id,
                    TaskStatus.PENDING.value,
                    json.dumps(task.parameters),
                    task.priority,
                    json.dumps(task.metadata),
                    now,
                )
            )
            task_id = cursor.lastrowid
        
        return self.get_task(task_id)
    
    def get_task(self, task_id: int) -> Optional[TaskListResponse]:
        """Get a task by ID."""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM task_list WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_task_list_response(row)
    
    def list_tasks(
        self,
        task_type_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> List[TaskListResponse]:
        """List tasks with optional filters."""
        conn = self.get_connection()
        
        query = "SELECT * FROM task_list WHERE 1=1"
        params = []
        
        if task_type_id is not None:
            query += " AND task_type_id = ?"
            params.append(task_type_id)
        
        if status is not None:
            query += " AND status = ?"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        return [self._row_to_task_list_response(row) for row in rows]
    
    def update_task(self, task_id: int, update: TaskListUpdate) -> Optional[TaskListResponse]:
        """Update a task."""
        now = datetime.now(timezone.utc).isoformat()
        
        # Build update query dynamically
        updates = []
        params = []
        
        if update.status is not None:
            updates.append("status = ?")
            params.append(update.status.value)
            
            # Update timestamps based on status
            if update.status == TaskStatus.RUNNING:
                updates.append("started_at = ?")
                params.append(now)
            elif update.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                updates.append("completed_at = ?")
                params.append(now)
        
        if update.priority is not None:
            updates.append("priority = ?")
            params.append(update.priority)
        
        if update.parameters is not None:
            updates.append("parameters = ?")
            params.append(json.dumps(update.parameters))
        
        if update.metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(update.metadata))
        
        if update.result is not None:
            updates.append("result = ?")
            params.append(json.dumps(update.result))
        
        if update.error_message is not None:
            updates.append("error_message = ?")
            params.append(update.error_message)
        
        if not updates:
            return self.get_task(task_id)
        
        updates.append("updated_at = ?")
        params.append(now)
        params.append(task_id)
        
        with self.transaction() as conn:
            # Note: Column names in updates list are safe - they are hardcoded strings, not user input
            # Only the parameter values are from user input and properly parameterized with ?
            query = f"UPDATE task_list SET {', '.join(updates)} WHERE id = ?"
            conn.execute(query, tuple(params))
        
        return self.get_task(task_id)
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        with self.transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM task_list WHERE id = ?",
                (task_id,)
            )
            return cursor.rowcount > 0
    
    def _row_to_task_list_response(self, row: sqlite3.Row) -> TaskListResponse:
        """Convert database row to TaskListResponse."""
        return TaskListResponse(
            id=row["id"],
            task_type_id=row["task_type_id"],
            status=TaskStatus(row["status"]),
            parameters=json.loads(row["parameters"]) if row["parameters"] else {},
            priority=row["priority"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            result=json.loads(row["result"]) if row["result"] else None,
            error_message=row["error_message"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
        )
