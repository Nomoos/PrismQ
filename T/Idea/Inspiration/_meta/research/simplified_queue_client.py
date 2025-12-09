"""
Simplified Queue Client - Research Prototype

This is a minimal implementation of the SQLite-based queue client API
that focuses on core operations: save, load, and priority-based retrieval.

This prototype demonstrates the simplified approach outlined in
client-api-simplified-queue.md research document.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


class SimplifiedQueueClient:
    """
    Minimal queue client for task persistence with priority-based ordering.

    Features:
    - Save tasks to SQLite database
    - Load tasks ordered by priority (max/increasing)
    - Atomic task claiming
    - Task status tracking
    - Idempotency support

    This follows SOLID principles:
    - Single Responsibility: Manages task queue operations only
    - Open/Closed: Can be extended with additional methods
    - Dependency Inversion: Uses database abstraction
    """

    def __init__(self, db_path: str):
        """
        Initialize queue client.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_db()

    def _ensure_db_directory(self) -> None:
        """Create database directory if it doesn't exist."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _init_db(self) -> None:
        """Initialize database with schema and optimizations."""
        conn = sqlite3.connect(self.db_path)
        try:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")

            # Set busy timeout to handle lock contention
            conn.execute("PRAGMA busy_timeout=5000")

            # Create main task queue table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS task_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    task_type TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'queued',
                    idempotency_key TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT
                )
            """
            )

            # Index for efficient priority-based retrieval
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_task_queue_status_priority 
                    ON task_queue(status, priority DESC, created_at ASC)
            """
            )

            # Unique index for idempotency
            conn.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_task_queue_idempotency 
                    ON task_queue(idempotency_key) 
                    WHERE idempotency_key IS NOT NULL
            """
            )

            conn.commit()
        finally:
            conn.close()

    async def enqueue_task(
        self,
        task_type: str,
        parameters: Dict[str, Any],
        priority: int = 0,
        idempotency_key: Optional[str] = None,
    ) -> str:
        """
        Save a task to the queue database.

        Args:
            task_type: Type of task (e.g., "module_run", "content_fetch")
            parameters: Task parameters as dict
            priority: Task priority (higher = more important, default 0)
            idempotency_key: Optional key for deduplication

        Returns:
            task_id: Unique identifier for the task

        Example:
            >>> queue = SimplifiedQueueClient("test.db")
            >>> task_id = await queue.enqueue_task(
            ...     "module_run",
            ...     {"module_id": "abc", "params": {}},
            ...     priority=50
            ... )
        """
        task_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()

        conn = sqlite3.connect(self.db_path)
        try:
            # Check for duplicate idempotency key
            if idempotency_key:
                cursor = conn.execute(
                    "SELECT task_id FROM task_queue WHERE idempotency_key = ?", (idempotency_key,)
                )
                existing = cursor.fetchone()
                if existing:
                    return existing[0]  # Return existing task_id

            # Insert new task
            conn.execute(
                """
                INSERT INTO task_queue 
                    (task_id, task_type, parameters, priority, idempotency_key, 
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (task_id, task_type, json.dumps(parameters), priority, idempotency_key, now, now),
            )
            conn.commit()
            return task_id
        finally:
            conn.close()

    async def get_next_task(
        self, task_types: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the next highest-priority queued task.

        Priority ordering:
        1. Higher priority number = higher importance
        2. Within same priority, use FIFO (oldest first)

        Args:
            task_types: Optional filter for specific task types

        Returns:
            Task dict with keys: task_id, task_type, parameters, priority, created_at
            Returns None if no tasks available

        Example:
            >>> task = await queue.get_next_task()
            >>> if task:
            ...     print(f"Next task: {task['task_id']} (priority {task['priority']})")
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            query = """
                SELECT task_id, task_type, parameters, priority, created_at
                FROM task_queue
                WHERE status = 'queued'
            """
            params = []

            # Add task type filter if provided
            if task_types:
                placeholders = ",".join("?" * len(task_types))
                query += f" AND task_type IN ({placeholders})"
                params.extend(task_types)

            # Order by priority DESC (highest first), then created_at ASC (oldest first)
            query += " ORDER BY priority DESC, created_at ASC LIMIT 1"

            cursor = conn.execute(query, params)
            row = cursor.fetchone()

            if not row:
                return None

            return {
                "task_id": row["task_id"],
                "task_type": row["task_type"],
                "parameters": json.loads(row["parameters"]),
                "priority": row["priority"],
                "created_at": row["created_at"],
            }
        finally:
            conn.close()

    async def claim_task(self, task_id: str) -> bool:
        """
        Atomically claim a task for processing.

        Uses IMMEDIATE transaction to ensure atomicity - only one worker
        can successfully claim a given task.

        Args:
            task_id: Task to claim

        Returns:
            True if claimed successfully, False if already claimed

        Example:
            >>> task = await queue.get_next_task()
            >>> if task and await queue.claim_task(task["task_id"]):
            ...     # Process the task
            ...     pass
        """
        conn = sqlite3.connect(self.db_path)
        try:
            now = datetime.now(timezone.utc).isoformat()

            # Use IMMEDIATE transaction for atomicity
            conn.execute("BEGIN IMMEDIATE")

            # Try to update if status is still 'queued'
            cursor = conn.execute(
                """
                UPDATE task_queue 
                SET status = 'running', 
                    started_at = ?,
                    updated_at = ?
                WHERE task_id = ? AND status = 'queued'
            """,
                (now, now, task_id),
            )

            success = cursor.rowcount > 0
            conn.commit()
            return success
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    async def complete_task(
        self, task_id: str, status: str, error_message: Optional[str] = None
    ) -> None:
        """
        Mark a task as completed or failed.

        Args:
            task_id: Task to complete
            status: Either "completed" or "failed"
            error_message: Optional error message if failed

        Raises:
            ValueError: If status is not "completed" or "failed"

        Example:
            >>> try:
            ...     # Process task
            ...     await queue.complete_task(task_id, "completed")
            ... except Exception as e:
            ...     await queue.complete_task(task_id, "failed", str(e))
        """
        if status not in ["completed", "failed"]:
            raise ValueError(f"Invalid status: {status}. Must be 'completed' or 'failed'")

        conn = sqlite3.connect(self.db_path)
        try:
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                """
                UPDATE task_queue
                SET status = ?,
                    completed_at = ?,
                    updated_at = ?,
                    error_message = ?
                WHERE task_id = ?
            """,
                (status, now, now, error_message, task_id),
            )
            conn.commit()
        finally:
            conn.close()

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status and details of a task.

        Args:
            task_id: Task to query

        Returns:
            Task dict with all fields, or None if not found

        Example:
            >>> status = await queue.get_task_status("task-123")
            >>> if status:
            ...     print(f"Task status: {status['status']}")
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                """
                SELECT task_id, task_type, parameters, priority, status,
                       created_at, started_at, completed_at, error_message
                FROM task_queue
                WHERE task_id = ?
            """,
                (task_id,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            return {
                "task_id": row["task_id"],
                "task_type": row["task_type"],
                "parameters": json.loads(row["parameters"]),
                "priority": row["priority"],
                "status": row["status"],
                "created_at": row["created_at"],
                "started_at": row["started_at"],
                "completed_at": row["completed_at"],
                "error_message": row["error_message"],
            }
        finally:
            conn.close()

    async def get_queue_stats(self) -> Dict[str, int]:
        """
        Get queue statistics.

        Returns:
            Dict with counts by status

        Example:
            >>> stats = await queue.get_queue_stats()
            >>> print(f"Queued: {stats['queued']}, Running: {stats['running']}")
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """
                SELECT status, COUNT(*) as count
                FROM task_queue
                GROUP BY status
            """
            )

            stats = {"queued": 0, "running": 0, "completed": 0, "failed": 0}

            for row in cursor:
                status, count = row
                stats[status] = count

            return stats
        finally:
            conn.close()


# Example usage and testing
async def example_usage():
    """Demonstrate simplified queue client usage."""
    import asyncio

    # Initialize queue
    queue = SimplifiedQueueClient("/tmp/test_queue.db")

    # Enqueue tasks with different priorities
    print("=== Enqueuing Tasks ===")
    task1 = await queue.enqueue_task("background_job", {"data": "cleanup"}, priority=0)
    print(f"Enqueued low priority task: {task1}")

    task2 = await queue.enqueue_task("module_run", {"module_id": "abc"}, priority=50)
    print(f"Enqueued normal priority task: {task2}")

    task3 = await queue.enqueue_task("emergency", {"action": "stop"}, priority=100)
    print(f"Enqueued high priority task: {task3}")

    # Check queue stats
    print("\n=== Queue Stats ===")
    stats = await queue.get_queue_stats()
    print(f"Queued: {stats['queued']}")

    # Process tasks in priority order
    print("\n=== Processing Tasks ===")
    while True:
        task = await queue.get_next_task()
        if not task:
            break

        print(f"\nNext task: {task['task_id']} (priority {task['priority']})")

        # Claim task
        if await queue.claim_task(task["task_id"]):
            print(f"  Claimed task {task['task_id']}")

            # Simulate processing
            await asyncio.sleep(0.1)

            # Complete task
            await queue.complete_task(task["task_id"], "completed")
            print(f"  Completed task {task['task_id']}")
        else:
            print(f"  Failed to claim task {task['task_id']}")

    # Final stats
    print("\n=== Final Stats ===")
    stats = await queue.get_queue_stats()
    print(f"Completed: {stats['completed']}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
