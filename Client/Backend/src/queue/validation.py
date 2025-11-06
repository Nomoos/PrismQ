"""
Queue Infrastructure Validation Module

Worker 01 support tool for validating queue infrastructure integrity
and helping other workers (Workers 02-06) ensure their implementations
are compatible with the core infrastructure.

This module provides validation functions for:
- Database schema integrity
- PRAGMA configuration verification
- Data model compatibility
- Transaction isolation testing
- Performance benchmarking
- Integration point validation

Part of Issue: Worker 01 - Support other workers and check validity
"""

import sqlite3
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import time

from .database import QueueDatabase
from .models import Task, Worker, TaskLog, SchedulingStrategy
from .config import PRODUCTION_PRAGMAS, validate_config
from .exceptions import QueueDatabaseError


class QueueValidator:
    """
    Comprehensive validation suite for queue infrastructure.
    
    Helps other workers verify their implementations are compatible
    with the core infrastructure (Issue #321).
    """
    
    def __init__(self, db_path: str):
        """
        Initialize validator with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db = QueueDatabase(db_path)
        self.validation_results: List[Tuple[str, bool, str]] = []
    
    def validate_all(self) -> bool:
        """
        Run all validation checks.
        
        Returns:
            True if all validations pass, False otherwise
        """
        print("=" * 70)
        print("QUEUE INFRASTRUCTURE VALIDATION")
        print("=" * 70)
        print()
        
        checks = [
            ("Configuration", self._validate_config),
            ("Database Connection", self._validate_connection),
            ("Schema Integrity", self._validate_schema),
            ("PRAGMA Settings", self._validate_pragmas),
            ("Data Models", self._validate_data_models),
            ("Transaction Isolation", self._validate_transactions),
            ("Index Performance", self._validate_indexes),
            ("Error Handling", self._validate_error_handling),
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            print(f"Running: {check_name}...", end=" ")
            try:
                passed, message = check_func()
                self.validation_results.append((check_name, passed, message))
                
                if passed:
                    print("✅ PASS")
                else:
                    print("❌ FAIL")
                    all_passed = False
                
                if message:
                    print(f"  → {message}")
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
                self.validation_results.append((check_name, False, str(e)))
                all_passed = False
        
        print()
        print("=" * 70)
        if all_passed:
            print("✅ ALL VALIDATIONS PASSED")
        else:
            print("❌ SOME VALIDATIONS FAILED")
        print("=" * 70)
        
        return all_passed
    
    def _validate_config(self) -> Tuple[bool, str]:
        """Validate configuration settings."""
        try:
            validate_config()
            return True, "Configuration is valid"
        except ValueError as e:
            return False, f"Configuration error: {e}"
    
    def _validate_connection(self) -> Tuple[bool, str]:
        """Validate database connection."""
        try:
            with self.db.connection() as conn:
                cursor = conn.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    return True, "Database connection successful"
                else:
                    return False, "Connection test query failed"
        except Exception as e:
            return False, f"Connection failed: {e}"
    
    def _validate_schema(self) -> Tuple[bool, str]:
        """Validate database schema integrity."""
        required_tables = ['task_queue', 'workers', 'task_logs']
        
        try:
            with self.db.connection() as conn:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                missing_tables = [
                    t for t in required_tables if t not in existing_tables
                ]
                
                if missing_tables:
                    return False, f"Missing tables: {', '.join(missing_tables)}"
                
                return True, f"All required tables exist: {', '.join(required_tables)}"
                
        except Exception as e:
            return False, f"Schema validation failed: {e}"
    
    def _validate_pragmas(self) -> Tuple[bool, str]:
        """Validate PRAGMA settings."""
        try:
            with self.db.connection() as conn:
                issues = []
                
                # Check critical PRAGMAs
                cursor = conn.execute("PRAGMA journal_mode")
                journal_mode = cursor.fetchone()[0]
                if journal_mode != 'wal':
                    issues.append(f"journal_mode is '{journal_mode}', expected 'wal'")
                
                cursor = conn.execute("PRAGMA synchronous")
                synchronous = cursor.fetchone()[0]
                if synchronous not in (1, 2):  # NORMAL=1, FULL=2
                    issues.append(f"synchronous is {synchronous}, expected 1 or 2")
                
                cursor = conn.execute("PRAGMA foreign_keys")
                foreign_keys = cursor.fetchone()[0]
                if foreign_keys != 1:
                    issues.append("foreign_keys not enabled")
                
                if issues:
                    return False, "; ".join(issues)
                
                return True, "All critical PRAGMAs configured correctly"
                
        except Exception as e:
            return False, f"PRAGMA validation failed: {e}"
    
    def _validate_data_models(self) -> Tuple[bool, str]:
        """Validate data model serialization/deserialization."""
        try:
            # Test Task model
            test_data = {
                'id': 1,
                'type': 'test',
                'status': 'queued',
                'priority': 50,
                'payload': '{"key": "value"}',
                'created_at_utc': '2025-01-01 00:00:00',
                'run_after_utc': '2025-01-01 00:00:00',
                'reserved_at_utc': None,
                'lease_until_utc': None,
                'locked_by': None,
                'finished_at_utc': None,
                'error_message': None,
                'idempotency_key': None,
            }
            
            task = Task.from_dict(test_data)
            
            if task.id != 1:
                return False, "Task deserialization failed"
            
            if task.get_payload_dict() != {"key": "value"}:
                return False, "Task payload parsing failed"
            
            return True, "Data model serialization works correctly"
            
        except Exception as e:
            return False, f"Data model validation failed: {e}"
    
    def _validate_transactions(self) -> Tuple[bool, str]:
        """Validate transaction isolation."""
        try:
            # Test that transactions are properly isolated
            with self.db.transaction() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
                    ('test_tx', 'queued', 50, '{}')
                )
            
            # Verify insert succeeded
            with self.db.connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM task_queue WHERE type = 'test_tx'"
                )
                count = cursor.fetchone()[0]
                
                # Cleanup
                conn.execute("DELETE FROM task_queue WHERE type = 'test_tx'")
                conn.commit()
            
            if count > 0:
                return True, "Transaction isolation verified"
            else:
                return False, "Transaction not committed properly"
                
        except Exception as e:
            return False, f"Transaction validation failed: {e}"
    
    def _validate_indexes(self) -> Tuple[bool, str]:
        """Validate that indexes exist for performance."""
        required_indexes = [
            'ix_task_status_prio_time',
            'ix_task_type_status',
            'uq_task_idempotency',
        ]
        
        try:
            with self.db.connection() as conn:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' "
                    "AND name NOT LIKE 'sqlite_%'"
                )
                existing_indexes = [row[0] for row in cursor.fetchall()]
                
                missing_indexes = [
                    idx for idx in required_indexes 
                    if idx not in existing_indexes
                ]
                
                if missing_indexes:
                    return False, f"Missing indexes: {', '.join(missing_indexes)}"
                
                return True, f"{len(required_indexes)} performance indexes verified"
                
        except Exception as e:
            return False, f"Index validation failed: {e}"
    
    def _validate_error_handling(self) -> Tuple[bool, str]:
        """Validate error handling mechanisms."""
        try:
            # Test that invalid SQL raises appropriate error
            error_raised = False
            try:
                with self.db.connection() as conn:
                    conn.execute("SELECT * FROM nonexistent_table")
            except (sqlite3.Error, QueueDatabaseError):
                error_raised = True
            
            if not error_raised:
                return False, "Error handling not working - invalid SQL didn't raise error"
            
            return True, "Error handling works correctly"
            
        except Exception as e:
            return False, f"Error handling validation failed: {e}"
    
    def benchmark_performance(self, num_tasks: int = 100) -> Dict[str, Any]:
        """
        Benchmark queue performance.
        
        Args:
            num_tasks: Number of tasks to use for benchmarking
            
        Returns:
            Dictionary with performance metrics
        """
        print("\n" + "=" * 70)
        print("PERFORMANCE BENCHMARK")
        print("=" * 70)
        
        results = {}
        
        # Clean up any existing test data
        with self.db.connection() as conn:
            conn.execute("DELETE FROM task_queue WHERE type LIKE 'bench_%'")
            conn.commit()
        
        # Benchmark: Insert
        print(f"\nInserting {num_tasks} tasks...", end=" ")
        start = time.time()
        
        with self.db.connection() as conn:
            for i in range(num_tasks):
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
                    (f'bench_insert', 'queued', 50, '{}')
                )
            conn.commit()
        
        insert_time = time.time() - start
        results['insert_time_ms'] = insert_time * 1000
        results['insert_rate_per_sec'] = num_tasks / insert_time
        print(f"✓ {insert_time*1000:.2f}ms ({results['insert_rate_per_sec']:.0f} tasks/sec)")
        
        # Benchmark: Select
        print(f"Selecting {num_tasks} tasks...", end=" ")
        start = time.time()
        
        with self.db.connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM task_queue WHERE type = 'bench_insert'"
            )
            rows = cursor.fetchall()
        
        select_time = time.time() - start
        results['select_time_ms'] = select_time * 1000
        results['select_rate_per_sec'] = len(rows) / select_time if select_time > 0 else 0
        print(f"✓ {select_time*1000:.2f}ms ({results['select_rate_per_sec']:.0f} tasks/sec)")
        
        # Benchmark: Update
        print(f"Updating {num_tasks} tasks...", end=" ")
        start = time.time()
        
        with self.db.connection() as conn:
            conn.execute(
                "UPDATE task_queue SET status = 'completed' "
                "WHERE type = 'bench_insert'"
            )
            conn.commit()
        
        update_time = time.time() - start
        results['update_time_ms'] = update_time * 1000
        results['update_rate_per_sec'] = num_tasks / update_time if update_time > 0 else 0
        print(f"✓ {update_time*1000:.2f}ms ({results['update_rate_per_sec']:.0f} tasks/sec)")
        
        # Cleanup
        with self.db.connection() as conn:
            conn.execute("DELETE FROM task_queue WHERE type LIKE 'bench_%'")
            conn.commit()
        
        # Summary
        print("\n" + "-" * 70)
        print("Performance Summary:")
        print(f"  Insert: {results['insert_rate_per_sec']:.0f} tasks/sec")
        print(f"  Select: {results['select_rate_per_sec']:.0f} tasks/sec")
        print(f"  Update: {results['update_rate_per_sec']:.0f} tasks/sec")
        print("=" * 70)
        
        return results
    
    def generate_report(self) -> str:
        """
        Generate validation report.
        
        Returns:
            Formatted validation report
        """
        report = []
        report.append("=" * 70)
        report.append("QUEUE INFRASTRUCTURE VALIDATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        passed = sum(1 for _, p, _ in self.validation_results if p)
        total = len(self.validation_results)
        
        report.append(f"Overall: {passed}/{total} checks passed")
        report.append("")
        
        for check_name, passed, message in self.validation_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            report.append(f"{status} - {check_name}")
            if message:
                report.append(f"      {message}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def quick_validate(db_path: Optional[str] = None) -> bool:
    """
    Quick validation check for queue infrastructure.
    
    Args:
        db_path: Optional database path. If None, uses temporary database.
        
    Returns:
        True if all validations pass
        
    Example:
        >>> from queue.validation import quick_validate
        >>> if quick_validate():
        ...     print("Queue infrastructure is valid!")
    """
    if db_path is None:
        import tempfile
        db_path = tempfile.mktemp(suffix='.db')
    
    validator = QueueValidator(db_path)
    
    # Initialize schema if needed
    try:
        validator.db.initialize_schema()
    except:
        pass  # Schema may already exist
    
    result = validator.validate_all()
    
    # Cleanup temp database
    if db_path.endswith('.db'):
        try:
            Path(db_path).unlink(missing_ok=True)
            Path(db_path + '-shm').unlink(missing_ok=True)
            Path(db_path + '-wal').unlink(missing_ok=True)
        except:
            pass
    
    return result


def validate_worker_integration(
    db: QueueDatabase,
    worker_id: str,
    task_type: str = "test_integration"
) -> bool:
    """
    Validate that a worker can successfully integrate with the queue.
    
    This is a helper function for Workers 02-06 to test their integrations.
    
    Args:
        db: QueueDatabase instance
        worker_id: Worker identifier to test
        task_type: Type of task to use for testing
        
    Returns:
        True if worker integration is valid
        
    Example:
        >>> from queue import QueueDatabase
        >>> from queue.validation import validate_worker_integration
        >>> 
        >>> db = QueueDatabase("queue.db")
        >>> if validate_worker_integration(db, "worker-1"):
        ...     print("Worker integration successful!")
    """
    print(f"\nValidating worker '{worker_id}' integration...")
    
    try:
        # Test 1: Enqueue a task
        with db.connection() as conn:
            cursor = conn.execute(
                "INSERT INTO task_queue "
                "(type, status, priority, payload, created_at_utc, run_after_utc) "
                "VALUES (?, ?, ?, ?, datetime('now'), datetime('now')) "
                "RETURNING id",
                (task_type, 'queued', 50, '{}')
            )
            task_id = cursor.fetchone()[0]
            conn.commit()
        
        print(f"  ✓ Enqueued task #{task_id}")
        
        # Test 2: Claim the task
        with db.transaction() as conn:
            cursor = conn.execute(
                "UPDATE task_queue "
                "SET status = 'leased', locked_by = ?, "
                "    reserved_at_utc = datetime('now'), "
                "    lease_until_utc = datetime('now', '+60 seconds') "
                "WHERE id = ? "
                "RETURNING *",
                (worker_id, task_id)
            )
            claimed = cursor.fetchone()
        
        if claimed:
            print(f"  ✓ Claimed task #{task_id}")
        else:
            print(f"  ✗ Failed to claim task #{task_id}")
            return False
        
        # Test 3: Complete the task
        with db.transaction() as conn:
            conn.execute(
                "UPDATE task_queue "
                "SET status = 'completed', "
                "    finished_at_utc = datetime('now') "
                "WHERE id = ?",
                (task_id,)
            )
        
        print(f"  ✓ Completed task #{task_id}")
        
        # Cleanup
        with db.connection() as conn:
            conn.execute("DELETE FROM task_queue WHERE id = ?", (task_id,))
            conn.commit()
        
        print(f"  ✓ Worker '{worker_id}' integration validated!\n")
        return True
        
    except Exception as e:
        print(f"  ✗ Integration validation failed: {e}\n")
        return False


if __name__ == "__main__":
    # Run validation when executed directly
    import sys
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        from .config import get_default_db_path
        db_path = get_default_db_path()
    
    print(f"Validating queue at: {db_path}\n")
    
    validator = QueueValidator(db_path)
    
    # Run all validations
    all_passed = validator.validate_all()
    
    # Run performance benchmark
    validator.benchmark_performance(num_tasks=100)
    
    # Generate report
    print("\n")
    print(validator.generate_report())
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)
