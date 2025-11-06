"""
Integration Tests for Queue Infrastructure

Tests validation tools and integration patterns to ensure
Worker 01's infrastructure properly supports other workers.

Part of: Worker 01 Phase 2 - Support other workers and check validity
"""

import pytest
import tempfile
import os
from pathlib import Path

# Import from queue module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.queue import (
    QueueDatabase,
    Task,
    SchedulingStrategy,
    TaskClaimerFactory,
    QueueValidator,
    quick_validate,
    validate_worker_integration,
)


class TestQueueValidator:
    """Test suite for QueueValidator class."""
    
    def test_quick_validate_success(self):
        """Test quick validation with valid database."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # Initialize database
            db = QueueDatabase(db_path)
            db.initialize_schema()
            
            # Run quick validation
            result = quick_validate(db_path)
            
            assert result is True, "Quick validation should pass"
            
        finally:
            # Cleanup
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass
    
    def test_validator_all_checks(self):
        """Test that all validation checks run."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # Initialize database
            db = QueueDatabase(db_path)
            db.initialize_schema()
            
            # Create validator
            validator = QueueValidator(db_path)
            
            # Run all validations
            result = validator.validate_all()
            
            # Should pass
            assert result is True
            
            # Check that we have validation results
            assert len(validator.validation_results) > 0
            
            # Check specific validations
            check_names = [name for name, _, _ in validator.validation_results]
            assert "Configuration" in check_names
            assert "Database Connection" in check_names
            assert "Schema Integrity" in check_names
            assert "PRAGMA Settings" in check_names
            
        finally:
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass
    
    def test_validator_report_generation(self):
        """Test validation report generation."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = QueueDatabase(db_path)
            db.initialize_schema()
            
            validator = QueueValidator(db_path)
            validator.validate_all()
            
            # Generate report
            report = validator.generate_report()
            
            # Check report content
            assert "VALIDATION REPORT" in report
            assert "PASS" in report or "FAIL" in report
            assert len(report) > 100, "Report should have meaningful content"
            
        finally:
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass
    
    def test_validator_performance_benchmark(self):
        """Test performance benchmarking."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = QueueDatabase(db_path)
            db.initialize_schema()
            
            validator = QueueValidator(db_path)
            
            # Run benchmark with small number of tasks
            results = validator.benchmark_performance(num_tasks=10)
            
            # Check results structure
            assert 'insert_time_ms' in results
            assert 'select_time_ms' in results
            assert 'update_time_ms' in results
            assert 'insert_rate_per_sec' in results
            
            # All operations should be reasonably fast
            assert results['insert_time_ms'] < 1000, "Insert should be fast"
            assert results['select_time_ms'] < 1000, "Select should be fast"
            assert results['update_time_ms'] < 1000, "Update should be fast"
            
        finally:
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass


class TestWorkerIntegration:
    """Test suite for worker integration validation."""
    
    def test_validate_worker_integration_success(self):
        """Test successful worker integration."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = QueueDatabase(db_path)
            db.initialize_schema()
            
            # Test worker integration
            result = validate_worker_integration(db, "test-worker-1")
            
            assert result is True, "Worker integration should succeed"
            
        finally:
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass
    
    def test_worker_enqueue_claim_complete_flow(self):
        """Test complete worker flow: enqueue -> claim -> complete."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = QueueDatabase(db_path)
            db.initialize_schema()
            
            # Step 1: Enqueue task (simulating Worker 02 - Client API)
            with db.transaction() as conn:
                cursor = conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now')) "
                    "RETURNING id",
                    ('test_task', 'queued', 50, '{"test": true}')
                )
                task_id = cursor.fetchone()[0]
            
            # Step 2: Claim task (simulating Worker 03 - Worker Engine)
            claimer = TaskClaimerFactory.create(SchedulingStrategy.FIFO, db)
            task = claimer.claim_task("worker-1", {}, 60)
            
            assert task is not None, "Should claim a task"
            assert task.id == task_id, "Should claim the enqueued task"
            assert task.status == 'leased', "Task should be leased"
            
            # Step 3: Complete task (simulating Worker 03 - Worker Engine)
            with db.transaction() as conn:
                conn.execute(
                    "UPDATE task_queue "
                    "SET status = 'completed', "
                    "    completed_at_utc = datetime('now'), "
                    "    result = ? "
                    "WHERE id = ?",
                    ('{"success": true}', task_id)
                )
            
            # Step 4: Verify task is completed
            with db.connection() as conn:
                cursor = conn.execute(
                    "SELECT status FROM task_queue WHERE id = ?",
                    (task_id,)
                )
                status = cursor.fetchone()[0]
            
            assert status == 'completed', "Task should be completed"
            
        finally:
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass


class TestSchedulingStrategyIntegration:
    """Test integration of different scheduling strategies."""
    
    def test_all_strategies_work(self):
        """Test that all scheduling strategies work correctly."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = QueueDatabase(db_path)
            db.initialize_schema()
            
            # Enqueue test tasks
            with db.connection() as conn:
                for i in range(5):
                    conn.execute(
                        "INSERT INTO task_queue "
                        "(type, status, priority, payload, created_at_utc, run_after_utc) "
                        "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
                        (f'task_{i}', 'queued', i * 10, '{}')
                    )
                conn.commit()
            
            # Test each strategy
            strategies = [
                SchedulingStrategy.FIFO,
                SchedulingStrategy.LIFO,
                SchedulingStrategy.PRIORITY,
                SchedulingStrategy.WEIGHTED_RANDOM,
            ]
            
            for strategy in strategies:
                # Reset tasks to queued
                with db.connection() as conn:
                    conn.execute("UPDATE task_queue SET status = 'queued'")
                    conn.commit()
                
                # Claim with strategy
                claimer = TaskClaimerFactory.create(strategy, db)
                task = claimer.claim_task(f"worker-{strategy.value}", {}, 60)
                
                assert task is not None, f"Strategy {strategy.value} should claim a task"
                assert task.status == 'leased', f"Task should be leased with {strategy.value}"
            
        finally:
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass


class TestConcurrentWorkerIntegration:
    """Test integration with multiple concurrent workers."""
    
    def test_multiple_workers_no_duplicate_claims(self):
        """Test that multiple workers don't claim the same task."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = QueueDatabase(db_path)
            db.initialize_schema()
            
            # Enqueue 10 tasks
            with db.connection() as conn:
                for i in range(10):
                    conn.execute(
                        "INSERT INTO task_queue "
                        "(type, status, priority, payload, created_at_utc, run_after_utc) "
                        "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
                        ('test_task', 'queued', 50, '{}')
                    )
                conn.commit()
            
            # Simulate 3 workers claiming tasks
            claimed_ids = set()
            claimer = TaskClaimerFactory.create(SchedulingStrategy.FIFO, db)
            
            for worker_num in range(3):
                task = claimer.claim_task(f"worker-{worker_num}", {}, 60)
                
                if task:
                    assert task.id not in claimed_ids, "No duplicate claims"
                    claimed_ids.add(task.id)
            
            # Should have claimed 3 different tasks
            assert len(claimed_ids) == 3, "Should claim 3 different tasks"
            
            # Verify no duplicate leases in database
            with db.connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(DISTINCT locked_by) FROM task_queue "
                    "WHERE status = 'leased'"
                )
                distinct_workers = cursor.fetchone()[0]
            
            assert distinct_workers == 3, "Should have 3 distinct workers"
            
        finally:
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass


class TestObservabilityIntegration:
    """Test observability and metrics queries (Worker 05 support)."""
    
    def test_queue_statistics_query(self):
        """Test queue statistics query pattern."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = QueueDatabase(db_path)
            db.initialize_schema()
            
            # Create mixed task states
            with db.connection() as conn:
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
                    ('task1', 'queued', 50, '{}')
                )
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
                    ('task2', 'queued', 50, '{}')
                )
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc, "
                    " completed_at_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), datetime('now'))",
                    ('task3', 'completed', 50, '{}')
                )
                conn.commit()
            
            # Query statistics (pattern for Worker 05)
            with db.connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT 
                        status,
                        COUNT(*) as count
                    FROM task_queue
                    GROUP BY status
                    """
                )
                stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Verify statistics
            assert stats.get('queued', 0) == 2, "Should have 2 queued tasks"
            assert stats.get('completed', 0) == 1, "Should have 1 completed task"
            
        finally:
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass


class TestMaintenanceIntegration:
    """Test maintenance operations (Worker 06 support)."""
    
    def test_cleanup_completed_tasks(self):
        """Test cleanup pattern for completed tasks."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = QueueDatabase(db_path)
            db.initialize_schema()
            
            # Create old completed tasks
            with db.connection() as conn:
                # Recent completed task
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc, "
                    " completed_at_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), datetime('now'))",
                    ('recent', 'completed', 50, '{}')
                )
                
                # Old completed task (simulate 8 days ago)
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc, "
                    " completed_at_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now', '-8 days'), "
                    "        datetime('now', '-8 days'), datetime('now', '-8 days'))",
                    ('old', 'completed', 50, '{}')
                )
                conn.commit()
            
            # Cleanup old tasks (pattern for Worker 06)
            with db.transaction() as conn:
                cursor = conn.execute(
                    """
                    DELETE FROM task_queue
                    WHERE status = 'completed'
                        AND completed_at_utc < datetime('now', '-7 days')
                    """
                )
                deleted = cursor.rowcount
            
            # Should have deleted 1 old task
            assert deleted == 1, "Should delete 1 old completed task"
            
            # Verify recent task still exists
            with db.connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM task_queue WHERE type = 'recent'"
                )
                count = cursor.fetchone()[0]
            
            assert count == 1, "Recent task should still exist"
            
        finally:
            for ext in ['', '-shm', '-wal']:
                try:
                    os.unlink(db_path + ext)
                except:
                    pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
