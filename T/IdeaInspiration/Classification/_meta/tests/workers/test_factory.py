"""Tests for Worker Factory."""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Import after path setup
from workers.factory import WorkerFactory, worker_factory


def test_factory_initialization():
    """Test factory initialization."""
    factory = WorkerFactory()
    assert factory is not None
    supported_types = factory.get_supported_types()
    assert len(supported_types) > 0


def test_get_supported_types():
    """Test getting supported task types."""
    supported_types = worker_factory.get_supported_types()
    assert 'classification_enrich' in supported_types
    assert 'classification_batch' in supported_types


def test_create_classification_worker():
    """Test creating a classification worker."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        worker = worker_factory.create(
            task_type='classification_enrich',
            worker_id='test-worker-001',
            idea_db_path=tmp.name
        )
        
        assert worker is not None
        assert worker.worker_id == 'test-worker-001'


def test_create_unknown_worker_type():
    """Test creating worker with unknown task type."""
    try:
        worker = worker_factory.create(
            task_type='unknown_type',
            worker_id='test-worker-001'
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown task type" in str(e)


def test_register_custom_worker():
    """Test registering a custom worker type."""
    factory = WorkerFactory()
    
    class CustomWorker:
        def __init__(self, worker_id, **kwargs):
            self.worker_id = worker_id
    
    factory.register('custom_task', CustomWorker)
    
    supported_types = factory.get_supported_types()
    assert 'custom_task' in supported_types
    
    worker = factory.create(
        task_type='custom_task',
        worker_id='custom-worker-001'
    )
    
    assert isinstance(worker, CustomWorker)
    assert worker.worker_id == 'custom-worker-001'


if __name__ == '__main__':
    # Run tests
    test_factory_initialization()
    print("✓ test_factory_initialization")
    
    test_get_supported_types()
    print("✓ test_get_supported_types")
    
    test_create_classification_worker()
    print("✓ test_create_classification_worker")
    
    test_create_unknown_worker_type()
    print("✓ test_create_unknown_worker_type")
    
    test_register_custom_worker()
    print("✓ test_register_custom_worker")
    
    print("\nAll tests passed!")
