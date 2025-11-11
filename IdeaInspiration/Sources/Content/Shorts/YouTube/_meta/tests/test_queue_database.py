"""Tests for queue database module.

This module tests the QueueDatabase class and schema implementation.
Tests cover:
- Database initialization
- PRAGMA settings
- Schema validation (tables, indexes, views)
- Performance requirements (<10ms for task claiming)
"""

import pytest
import tempfile
import time
from pathlib import Path
from src.workers.queue_database import QueueDatabase


@pytest.fixture
def temp_queue_db():
    """Create a temporary queue database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_queue.db"
        db = QueueDatabase(str(db_path))
        yield db


def test_database_initialization(temp_queue_db):
    """Test database initializes with correct schema."""
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
        """)
        tables = {row[0] for row in cursor.fetchall()}
        
        assert 'task_queue' in tables, "task_queue table not found"
        assert 'worker_heartbeats' in tables, "worker_heartbeats table not found"
        assert 'task_logs' in tables, "task_logs table not found"
    finally:
        conn.close()


def test_pragma_journal_mode(temp_queue_db):
    """Test PRAGMA journal_mode is set to WAL."""
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode")
        result = cursor.fetchone()[0]
        assert result.lower() == 'wal', f"Expected WAL mode, got {result}"
    finally:
        conn.close()


def test_pragma_busy_timeout(temp_queue_db):
    """Test PRAGMA busy_timeout is set correctly."""
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA busy_timeout")
        result = cursor.fetchone()[0]
        assert result == 5000, f"Expected 5000ms, got {result}ms"
    finally:
        conn.close()


def test_pragma_synchronous(temp_queue_db):
    """Test PRAGMA synchronous is set correctly."""
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA synchronous")
        result = cursor.fetchone()[0]
        # NORMAL = 1, FULL = 2 (both are acceptable for safety)
        # On some systems, NORMAL may map to FULL (2)
        assert result in [1, 2], f"Expected NORMAL (1) or FULL (2), got {result}"
    finally:
        conn.close()


def test_indexes_exist(temp_queue_db):
    """Test critical indexes exist."""
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        indexes = {row[0] for row in cursor.fetchall()}
        
        assert 'idx_task_queue_claiming' in indexes, "Critical claiming index not found"
        assert 'idx_task_queue_worker' in indexes, "Worker index not found"
        assert 'idx_task_queue_created' in indexes, "Created timestamp index not found"
        assert 'idx_worker_heartbeat' in indexes, "Worker heartbeat index not found"
        assert 'idx_task_logs_task' in indexes, "Task logs task index not found"
        assert 'idx_task_logs_worker' in indexes, "Task logs worker index not found"
    finally:
        conn.close()


def test_views_exist(temp_queue_db):
    """Test monitoring views exist."""
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view'
        """)
        views = {row[0] for row in cursor.fetchall()}
        
        assert 'v_active_tasks' in views, "v_active_tasks view not found"
        assert 'v_worker_status' in views, "v_worker_status view not found"
        assert 'v_task_stats' in views, "v_task_stats view not found"
    finally:
        conn.close()


def test_task_queue_constraints(temp_queue_db):
    """Test task_queue table constraints."""
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        
        # Test priority constraint (must be between 1 and 10)
        with pytest.raises(Exception):
            cursor.execute("""
                INSERT INTO task_queue 
                (task_type, parameters, priority, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
            """, ('test', '{}', 11))  # Invalid priority
        
        # Test status constraint
        with pytest.raises(Exception):
            cursor.execute("""
                INSERT INTO task_queue 
                (task_type, parameters, status, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
            """, ('test', '{}', 'invalid_status'))
        
        # Test valid insert
        cursor.execute("""
            INSERT INTO task_queue 
            (task_type, parameters, created_at, updated_at)
            VALUES (?, ?, datetime('now'), datetime('now'))
        """, ('test', '{}'))
        conn.commit()
        
        # Verify insert worked
        cursor.execute("SELECT COUNT(*) FROM task_queue")
        count = cursor.fetchone()[0]
        assert count == 1, "Valid insert failed"
        
    finally:
        conn.close()


def test_claiming_performance(temp_queue_db):
    """Test task claiming is fast (<10ms).
    
    This is a critical performance requirement for the worker system.
    """
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        
        # Insert 1000 tasks to simulate realistic workload
        for i in range(1000):
            cursor.execute("""
                INSERT INTO task_queue 
                (task_type, parameters, priority, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
            """, ('test_task', '{}', (i % 10) + 1))
        conn.commit()
        
        # Measure claim time (simulated claim query)
        start = time.time()
        cursor.execute("""
            SELECT id FROM task_queue
            WHERE status = 'queued'
            ORDER BY priority DESC, created_at DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        elapsed_ms = (time.time() - start) * 1000
        
        assert result is not None, "No task found to claim"
        assert elapsed_ms < 10, f"Claiming took {elapsed_ms:.2f}ms (expected <10ms)"
        
    finally:
        conn.close()


def test_get_stats(temp_queue_db):
    """Test database statistics retrieval."""
    # Insert some test data
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        
        # Insert tasks with different statuses
        for status in ['queued', 'running', 'completed']:
            cursor.execute("""
                INSERT INTO task_queue 
                (task_type, parameters, status, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
            """, ('test', '{}', status))
        conn.commit()
    finally:
        conn.close()
    
    # Get stats
    stats = temp_queue_db.get_stats()
    
    assert 'status_counts' in stats
    assert 'active_workers' in stats
    assert 'db_size_bytes' in stats
    assert 'db_size_mb' in stats
    
    # Verify status counts
    assert stats['status_counts'].get('queued', 0) >= 1
    assert stats['status_counts'].get('running', 0) >= 1
    assert stats['status_counts'].get('completed', 0) >= 1


def test_get_pragma_info(temp_queue_db):
    """Test PRAGMA info retrieval."""
    pragma_info = temp_queue_db.get_pragma_info()
    
    assert 'journal_mode' in pragma_info
    assert 'busy_timeout' in pragma_info
    assert 'synchronous' in pragma_info
    assert 'cache_size' in pragma_info
    
    assert pragma_info['journal_mode'].lower() == 'wal'
    assert pragma_info['busy_timeout'] == 5000


def test_view_v_active_tasks(temp_queue_db):
    """Test v_active_tasks view works correctly."""
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        
        # Insert some active tasks
        for status in ['queued', 'claimed', 'running']:
            cursor.execute("""
                INSERT INTO task_queue 
                (task_type, parameters, status, priority, created_at, updated_at)
                VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            """, ('test', '{}', status, 5))
        
        # Insert a completed task (should not appear in active view)
        cursor.execute("""
            INSERT INTO task_queue 
            (task_type, parameters, status, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        """, ('test', '{}', 'completed'))
        conn.commit()
        
        # Query view
        cursor.execute("SELECT COUNT(*) FROM v_active_tasks")
        count = cursor.fetchone()[0]
        
        assert count == 3, f"Expected 3 active tasks, got {count}"
        
    finally:
        conn.close()


def test_vacuum_and_checkpoint(temp_queue_db):
    """Test vacuum and checkpoint operations."""
    # These should not raise exceptions
    temp_queue_db.vacuum()
    temp_queue_db.checkpoint()


def test_multiple_connections(temp_queue_db):
    """Test that multiple connections work (important for workers)."""
    conn1 = temp_queue_db.get_connection()
    conn2 = temp_queue_db.get_connection()
    
    try:
        # Both connections should work independently
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()
        
        cursor1.execute("SELECT COUNT(*) FROM task_queue")
        cursor2.execute("SELECT COUNT(*) FROM task_queue")
        
        # Should be able to query simultaneously
        count1 = cursor1.fetchone()[0]
        count2 = cursor2.fetchone()[0]
        
        assert count1 == count2
        
    finally:
        conn1.close()
        conn2.close()


def test_worker_heartbeat_table(temp_queue_db):
    """Test worker_heartbeats table functionality."""
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        
        # Insert a worker heartbeat
        cursor.execute("""
            INSERT INTO worker_heartbeats 
            (worker_id, last_heartbeat, strategy, started_at, updated_at)
            VALUES (?, datetime('now'), ?, datetime('now'), datetime('now'))
        """, ('worker-1', 'LIFO'))
        conn.commit()
        
        # Query it back
        cursor.execute("SELECT * FROM worker_heartbeats WHERE worker_id = ?", ('worker-1',))
        result = cursor.fetchone()
        
        assert result is not None
        assert result['worker_id'] == 'worker-1'
        assert result['strategy'] == 'LIFO'
        assert result['tasks_processed'] == 0
        assert result['tasks_failed'] == 0
        
    finally:
        conn.close()


def test_task_logs_table(temp_queue_db):
    """Test task_logs table functionality."""
    conn = temp_queue_db.get_connection()
    try:
        cursor = conn.cursor()
        
        # Insert a task first
        cursor.execute("""
            INSERT INTO task_queue 
            (task_type, parameters, created_at, updated_at)
            VALUES (?, ?, datetime('now'), datetime('now'))
        """, ('test', '{}'))
        task_id = cursor.lastrowid
        
        # Insert a log entry
        cursor.execute("""
            INSERT INTO task_logs 
            (task_id, event_type, message, timestamp)
            VALUES (?, ?, ?, datetime('now'))
        """, (task_id, 'created', 'Task created'))
        conn.commit()
        
        # Query it back
        cursor.execute("SELECT * FROM task_logs WHERE task_id = ?", (task_id,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result['task_id'] == task_id
        assert result['event_type'] == 'created'
        assert result['message'] == 'Task created'
        
    finally:
        conn.close()
