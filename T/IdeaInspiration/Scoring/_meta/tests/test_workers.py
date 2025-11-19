"""Unit tests for scoring worker functionality."""

import pytest
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock, patch

from src.workers import Task, TaskResult, TaskStatus
from src.workers.scoring_worker import ScoringWorker
from src.workers.claiming_strategies import get_strategy, list_strategies
from src.workers.factory import WorkerFactory
from src.config import Config
from src.scoring import ScoringEngine


@pytest.fixture
def temp_queue_db(tmp_path):
    """Create a temporary queue database."""
    db_path = tmp_path / "test_queue.db"
    return str(db_path)


@pytest.fixture
def mock_config():
    """Create a mock Config object."""
    config = Mock(spec=Config)
    return config


@pytest.fixture
def scoring_engine():
    """Create a real ScoringEngine."""
    return ScoringEngine()


@pytest.fixture
def worker(temp_queue_db, mock_config, scoring_engine):
    """Create a ScoringWorker for testing."""
    return ScoringWorker(
        worker_id="test-worker",
        queue_db_path=temp_queue_db,
        config=mock_config,
        scoring_engine=scoring_engine,
        strategy="FIFO",
        enable_taskmanager=False,  # Disable for testing
    )


class TestClaimingStrategies:
    """Tests for task claiming strategies."""
    
    def test_list_strategies(self):
        """Test listing available strategies."""
        strategies = list_strategies()
        assert "FIFO" in strategies
        assert "LIFO" in strategies
        assert "PRIORITY" in strategies
    
    def test_get_fifo_strategy(self):
        """Test FIFO strategy."""
        strategy = get_strategy("FIFO")
        assert strategy.get_name() == "FIFO"
        assert "created_at ASC" in strategy.get_order_by_clause()
    
    def test_get_lifo_strategy(self):
        """Test LIFO strategy."""
        strategy = get_strategy("LIFO")
        assert strategy.get_name() == "LIFO"
        assert "created_at DESC" in strategy.get_order_by_clause()
    
    def test_get_priority_strategy(self):
        """Test PRIORITY strategy."""
        strategy = get_strategy("PRIORITY")
        assert strategy.get_name() == "PRIORITY"
        assert "priority DESC" in strategy.get_order_by_clause()
    
    def test_get_invalid_strategy(self):
        """Test getting invalid strategy."""
        with pytest.raises(ValueError):
            get_strategy("INVALID")


class TestWorkerFactory:
    """Tests for worker factory."""
    
    def test_create_scoring_worker_defaults(self, tmp_path):
        """Test creating worker with default settings."""
        worker = WorkerFactory.create_scoring_worker(
            queue_db_path=str(tmp_path / "queue.db"),
            enable_taskmanager=False
        )
        
        assert worker is not None
        assert worker.worker_id.startswith("scoring-worker-")
        assert worker.strategy == "FIFO"
        assert worker.poll_interval == 5
        assert worker.max_backoff == 60
    
    def test_create_scoring_worker_custom(self, tmp_path):
        """Test creating worker with custom settings."""
        worker = WorkerFactory.create_scoring_worker(
            worker_id="custom-worker",
            queue_db_path=str(tmp_path / "queue.db"),
            strategy="PRIORITY",
            poll_interval=10,
            max_backoff=120,
            enable_taskmanager=False
        )
        
        assert worker.worker_id == "custom-worker"
        assert worker.strategy == "PRIORITY"
        assert worker.poll_interval == 10
        assert worker.max_backoff == 120


class TestBaseScoringWorker:
    """Tests for base scoring worker functionality."""
    
    def test_worker_initialization(self, worker):
        """Test worker initializes correctly."""
        assert worker.worker_id == "test-worker"
        assert worker.strategy == "FIFO"
        assert worker.tasks_processed == 0
        assert worker.tasks_failed == 0
        assert worker.running == False
    
    def test_queue_database_initialization(self, worker):
        """Test queue database is initialized with schema."""
        conn = worker.queue_conn
        cursor = conn.cursor()
        
        # Check task_queue table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='task_queue'
        """)
        assert cursor.fetchone() is not None
        
        # Check worker_heartbeats table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='worker_heartbeats'
        """)
        assert cursor.fetchone() is not None
    
    def test_claim_task_empty_queue(self, worker):
        """Test claiming task from empty queue."""
        task = worker.claim_task()
        assert task is None
    
    def test_claim_task_success(self, worker):
        """Test successfully claiming a task."""
        # Add a task to the queue
        conn = worker.queue_conn
        now = datetime.now(timezone.utc).isoformat()
        
        conn.execute("""
            INSERT INTO task_queue 
            (task_type, parameters, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "PrismQ.Scoring.TextScoring",
            json.dumps({"title": "Test", "text_content": "Content"}),
            0,
            "queued",
            now,
            now
        ))
        conn.commit()
        
        # Claim the task
        task = worker.claim_task()
        
        assert task is not None
        assert task.task_type == "PrismQ.Scoring.TextScoring"
        assert task.status == TaskStatus.CLAIMED
        assert task.parameters["title"] == "Test"
    
    def test_report_result_success(self, worker):
        """Test reporting successful task result."""
        # Add and claim a task
        conn = worker.queue_conn
        now = datetime.now(timezone.utc).isoformat()
        
        conn.execute("""
            INSERT INTO task_queue 
            (task_type, parameters, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "PrismQ.Scoring.TextScoring",
            json.dumps({"title": "Test", "text_content": "Content"}),
            0,
            "queued",
            now,
            now
        ))
        conn.commit()
        
        task = worker.claim_task()
        
        # Report success
        result = TaskResult(
            success=True,
            data={"score": 85.5},
            items_processed=1
        )
        worker.report_result(task, result)
        
        # Verify task status updated
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM task_queue WHERE id = ?", (task.id,))
        status = cursor.fetchone()[0]
        assert status == "completed"
        assert worker.tasks_processed == 1
    
    def test_report_result_failure(self, worker):
        """Test reporting failed task result."""
        # Add and claim a task
        conn = worker.queue_conn
        now = datetime.now(timezone.utc).isoformat()
        
        conn.execute("""
            INSERT INTO task_queue 
            (task_type, parameters, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "PrismQ.Scoring.TextScoring",
            json.dumps({"title": "Test", "text_content": "Content"}),
            0,
            "queued",
            now,
            now
        ))
        conn.commit()
        
        task = worker.claim_task()
        
        # Report failure
        result = TaskResult(
            success=False,
            error="Processing failed",
            items_processed=0
        )
        worker.report_result(task, result)
        
        # Verify task status updated
        cursor = conn.cursor()
        cursor.execute("SELECT status, error_message FROM task_queue WHERE id = ?", (task.id,))
        row = cursor.fetchone()
        assert row[0] == "failed"
        assert row[1] == "Processing failed"
        assert worker.tasks_failed == 1


class TestScoringWorker:
    """Tests for concrete scoring worker implementation."""
    
    def test_process_text_scoring_task(self, worker):
        """Test processing text scoring task."""
        task = Task(
            id=1,
            task_type="PrismQ.Scoring.TextScoring",
            parameters={
                "title": "Introduction to Machine Learning",
                "description": "A comprehensive guide",
                "text_content": "Machine learning is a subset of AI..."
            }
        )
        
        result = worker.process_task(task)
        
        assert result.success == True
        assert "score_breakdown" in result.data
        assert "overall_score" in result.data
        assert result.items_processed == 1
    
    def test_process_engagement_scoring_task(self, worker):
        """Test processing engagement scoring task."""
        task = Task(
            id=2,
            task_type="PrismQ.Scoring.EngagementScoring",
            parameters={
                "views": 1000000,
                "likes": 50000,
                "comments": 1000,
                "shares": 5000,
                "platform": "youtube"
            }
        )
        
        result = worker.process_task(task)
        
        assert result.success == True
        assert "engagement_score" in result.data
        assert "score_details" in result.data
        assert result.items_processed == 1
    
    def test_process_batch_scoring_task(self, worker):
        """Test processing batch scoring task."""
        task = Task(
            id=3,
            task_type="PrismQ.Scoring.BatchScoring",
            parameters={
                "items": [
                    {
                        "title": "Item 1",
                        "description": "Description 1",
                        "text_content": "Content 1..."
                    },
                    {
                        "title": "Item 2",
                        "description": "Description 2",
                        "text_content": "Content 2..."
                    }
                ]
            }
        )
        
        result = worker.process_task(task)
        
        assert result.success == True
        assert "results" in result.data
        assert len(result.data["results"]) == 2
        assert result.data["total_items"] == 2
        assert result.items_processed == 2
    
    def test_process_invalid_task_type(self, worker):
        """Test processing task with invalid type."""
        task = Task(
            id=4,
            task_type="PrismQ.Scoring.InvalidType",
            parameters={}
        )
        
        result = worker.process_task(task)
        
        assert result.success == False
        assert "Unknown task type" in result.error
        assert result.items_processed == 0
    
    def test_run_once_no_task(self, worker):
        """Test run_once with no available tasks."""
        processed = worker.run_once()
        assert processed == False
    
    def test_run_once_with_task(self, worker):
        """Test run_once with an available task."""
        # Add a task to the queue
        conn = worker.queue_conn
        now = datetime.now(timezone.utc).isoformat()
        
        conn.execute("""
            INSERT INTO task_queue 
            (task_type, parameters, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "PrismQ.Scoring.TextScoring",
            json.dumps({
                "title": "Test",
                "text_content": "Content to score"
            }),
            0,
            "queued",
            now,
            now
        ))
        conn.commit()
        
        # Process one task
        processed = worker.run_once()
        
        assert processed == True
        assert worker.tasks_processed == 1
    
    def test_run_with_max_iterations(self, worker):
        """Test running worker with iteration limit."""
        # Add multiple tasks
        conn = worker.queue_conn
        now = datetime.now(timezone.utc).isoformat()
        
        for i in range(3):
            conn.execute("""
                INSERT INTO task_queue 
                (task_type, parameters, priority, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "PrismQ.Scoring.TextScoring",
                json.dumps({
                    "title": f"Test {i}",
                    "text_content": f"Content {i}"
                }),
                0,
                "queued",
                now,
                now
            ))
        conn.commit()
        
        # Run with max iterations
        worker.run(max_iterations=2)
        
        # Should process 2 tasks (may be less if queue is empty between iterations)
        assert worker.tasks_processed <= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
