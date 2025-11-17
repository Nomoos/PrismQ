"""Tests for Classification Worker."""

import sys
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Import after path setup
from workers import Task, TaskStatus, TaskResult
from workers.classification_worker import ClassificationWorker


def test_classification_worker_initialization():
    """Test worker initialization."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        worker = ClassificationWorker(
            worker_id="test-worker-001",
            idea_db_path=tmp.name
        )
        
        assert worker.worker_id == "test-worker-001"
        assert worker.tasks_processed == 0
        assert worker.tasks_failed == 0
        assert worker.classifier is not None


def test_process_single_classification_with_data():
    """Test processing a single classification task with data."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        worker = ClassificationWorker(
            worker_id="test-worker-001",
            idea_db_path=tmp.name
        )
        
        # Create test task with idea data
        task = Task(
            id=1,
            task_type="classification_enrich",
            params={
                "idea_data": {
                    "title": "Amazing startup story",
                    "description": "A founder shares their journey",
                    "content": "This is a narrative about building a successful startup...",
                    "keywords": ["startup", "story", "business"],
                    "source_type": "text",
                    "source_platform": "reddit"
                },
                "save_to_db": False  # Don't save for test
            },
            status=TaskStatus.CLAIMED
        )
        
        result = worker.process_task(task)
        
        assert result.success is True
        assert 'category' in result.data
        assert 'category_confidence' in result.data
        assert 'flags' in result.data
        assert 'tags' in result.data
        assert worker.tasks_processed == 1


def test_process_unknown_task_type():
    """Test processing an unknown task type."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        worker = ClassificationWorker(
            worker_id="test-worker-001",
            idea_db_path=tmp.name
        )
        
        task = Task(
            id=1,
            task_type="unknown_task_type",
            params={},
            status=TaskStatus.CLAIMED
        )
        
        result = worker.process_task(task)
        
        assert result.success is False
        assert "Unknown task type" in result.error


def test_process_missing_parameters():
    """Test processing with missing required parameters."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        worker = ClassificationWorker(
            worker_id="test-worker-001",
            idea_db_path=tmp.name
        )
        
        task = Task(
            id=1,
            task_type="classification_enrich",
            params={},  # Missing required parameters
            status=TaskStatus.CLAIMED
        )
        
        result = worker.process_task(task)
        
        assert result.success is False
        assert "required" in result.error.lower()


def test_batch_classification():
    """Test batch classification processing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        worker = ClassificationWorker(
            worker_id="test-worker-001",
            idea_db_path=tmp.name
        )
        
        # Insert test data into database
        from classification import IdeaInspiration, ContentType
        
        idea1 = IdeaInspiration(
            title="Story 1",
            description="Description 1",
            content="Content 1",
            keywords=["test"],
            source_type=ContentType.TEXT,
            source_platform="test"
        )
        
        idea2 = IdeaInspiration(
            title="Story 2",
            description="Description 2",
            content="Content 2",
            keywords=["test"],
            source_type=ContentType.TEXT,
            source_platform="test"
        )
        
        # Insert ideas and get their IDs
        id1 = worker.idea_db.insert(idea1)
        id2 = worker.idea_db.insert(idea2)
        
        # Create batch task with actual IDs
        task = Task(
            id=1,
            task_type="classification_batch",
            params={
                "idea_inspiration_ids": [str(id1), str(id2)],
                "save_to_db": True
            },
            status=TaskStatus.CLAIMED
        )
        
        result = worker.process_task(task)
        
        assert result.success is True
        assert result.data['total'] == 2
        assert result.data['successful'] == 2  # Both should succeed
        assert result.data['failed'] == 0
        assert 'results' in result.data


if __name__ == '__main__':
    # Run tests
    test_classification_worker_initialization()
    print("✓ test_classification_worker_initialization")
    
    test_process_single_classification_with_data()
    print("✓ test_process_single_classification_with_data")
    
    test_process_unknown_task_type()
    print("✓ test_process_unknown_task_type")
    
    test_process_missing_parameters()
    print("✓ test_process_missing_parameters")
    
    test_batch_classification()
    print("✓ test_batch_classification")
    
    print("\nAll tests passed!")
