"""Unit tests for RunRegistry."""

import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta
import tempfile
import json

from src.core.run_registry import RunRegistry
from src.models.run import Run, RunStatus


def test_run_registry_initialization():
    """Test RunRegistry initialization."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        registry = RunRegistry(history_file=history_file)
        assert isinstance(registry.runs, dict)
        assert len(registry.runs) == 0
        assert registry.history_file == history_file
    finally:
        if history_file.exists():
            history_file.unlink()


def test_add_run():
    """Test adding a run to the registry."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        registry = RunRegistry(history_file=history_file)
        
        run = Run(
            run_id="test_run_1",
            module_id="test_module",
            module_name="Test Module",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={}
        )
        
        registry.add_run(run)
        
        assert len(registry.runs) == 1
        assert "test_run_1" in registry.runs
        assert registry.runs["test_run_1"].module_id == "test_module"
    finally:
        if history_file.exists():
            history_file.unlink()


def test_update_run():
    """Test updating a run in the registry."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        registry = RunRegistry(history_file=history_file)
        
        run = Run(
            run_id="test_run_1",
            module_id="test_module",
            module_name="Test Module",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={}
        )
        
        registry.add_run(run)
        
        # Update the run
        run.status = RunStatus.RUNNING
        registry.update_run(run)
        
        assert registry.runs["test_run_1"].status == RunStatus.RUNNING
    finally:
        if history_file.exists():
            history_file.unlink()


def test_get_run():
    """Test getting a run by ID."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        registry = RunRegistry(history_file=history_file)
        
        run = Run(
            run_id="test_run_1",
            module_id="test_module",
            module_name="Test Module",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={}
        )
        
        registry.add_run(run)
        
        retrieved_run = registry.get_run("test_run_1")
        assert retrieved_run is not None
        assert retrieved_run.run_id == "test_run_1"
        
        nonexistent = registry.get_run("nonexistent")
        assert nonexistent is None
    finally:
        if history_file.exists():
            history_file.unlink()


def test_get_active_runs():
    """Test getting active runs."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        registry = RunRegistry(history_file=history_file)
        
        # Add various runs
        runs = [
            Run(
                run_id=f"run_{i}",
                module_id="test_module",
                module_name="Test Module",
                status=status,
                created_at=datetime.now(timezone.utc),
                parameters={}
            )
            for i, status in enumerate([
                RunStatus.QUEUED,
                RunStatus.RUNNING,
                RunStatus.COMPLETED,
                RunStatus.FAILED,
                RunStatus.QUEUED,
            ])
        ]
        
        for run in runs:
            registry.add_run(run)
        
        active_runs = registry.get_active_runs()
        assert len(active_runs) == 3  # 2 QUEUED + 1 RUNNING
        assert all(r.status in [RunStatus.QUEUED, RunStatus.RUNNING] for r in active_runs)
    finally:
        if history_file.exists():
            history_file.unlink()


def test_get_runs_by_module():
    """Test getting runs by module ID."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        registry = RunRegistry(history_file=history_file)
        
        # Add runs for different modules
        for i in range(5):
            module_id = "module_a" if i < 3 else "module_b"
            run = Run(
                run_id=f"run_{i}",
                module_id=module_id,
                module_name=module_id.title(),
                status=RunStatus.COMPLETED,
                created_at=datetime.now(timezone.utc),
                parameters={}
            )
            registry.add_run(run)
        
        module_a_runs = registry.get_runs_by_module("module_a")
        assert len(module_a_runs) == 3
        assert all(r.module_id == "module_a" for r in module_a_runs)
        
        module_b_runs = registry.get_runs_by_module("module_b")
        assert len(module_b_runs) == 2
    finally:
        if history_file.exists():
            history_file.unlink()


def test_get_runs_by_status():
    """Test getting runs by status."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        registry = RunRegistry(history_file=history_file)
        
        statuses = [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.COMPLETED, RunStatus.RUNNING]
        for i, status in enumerate(statuses):
            run = Run(
                run_id=f"run_{i}",
                module_id="test_module",
                module_name="Test Module",
                status=status,
                created_at=datetime.now(timezone.utc),
                parameters={}
            )
            registry.add_run(run)
        
        completed_runs = registry.get_runs_by_status(RunStatus.COMPLETED)
        assert len(completed_runs) == 2
        
        failed_runs = registry.get_runs_by_status(RunStatus.FAILED)
        assert len(failed_runs) == 1
    finally:
        if history_file.exists():
            history_file.unlink()


def test_get_recent_runs():
    """Test getting recent runs."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        registry = RunRegistry(history_file=history_file)
        
        # Add runs with different timestamps
        base_time = datetime.now(timezone.utc)
        for i in range(10):
            run = Run(
                run_id=f"run_{i}",
                module_id="test_module",
                module_name="Test Module",
                status=RunStatus.COMPLETED,
                created_at=base_time - timedelta(minutes=i),
                parameters={}
            )
            registry.add_run(run)
        
        # Get most recent 5
        recent_runs = registry.get_recent_runs(limit=5)
        assert len(recent_runs) == 5
        
        # Should be sorted by created_at descending
        assert recent_runs[0].run_id == "run_0"  # Most recent
        assert recent_runs[-1].run_id == "run_4"
    finally:
        if history_file.exists():
            history_file.unlink()


def test_cleanup_old_runs():
    """Test cleaning up old runs."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        registry = RunRegistry(history_file=history_file)
        
        # Add old completed run
        old_run = Run(
            run_id="old_run",
            module_id="test_module",
            module_name="Test Module",
            status=RunStatus.COMPLETED,
            created_at=datetime.now(timezone.utc) - timedelta(days=60),
            completed_at=datetime.now(timezone.utc) - timedelta(days=60),
            parameters={}
        )
        
        # Add recent run
        recent_run = Run(
            run_id="recent_run",
            module_id="test_module",
            module_name="Test Module",
            status=RunStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            parameters={}
        )
        
        registry.add_run(old_run)
        registry.add_run(recent_run)
        
        assert len(registry.runs) == 2
        
        # Cleanup runs older than 30 days
        registry.cleanup_old_runs(days=30)
        
        # Old run should be removed
        assert len(registry.runs) == 1
        assert "recent_run" in registry.runs
        assert "old_run" not in registry.runs
    finally:
        if history_file.exists():
            history_file.unlink()


def test_persistence():
    """Test that runs are persisted to disk."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        # Create registry and add a run
        registry1 = RunRegistry(history_file=history_file)
        
        run = Run(
            run_id="test_run_1",
            module_id="test_module",
            module_name="Test Module",
            status=RunStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
            parameters={"key": "value"}
        )
        
        registry1.add_run(run)
        
        # Create a new registry instance (should load from disk)
        registry2 = RunRegistry(history_file=history_file)
        
        assert len(registry2.runs) == 1
        assert "test_run_1" in registry2.runs
        assert registry2.runs["test_run_1"].module_id == "test_module"
        assert registry2.runs["test_run_1"].parameters["key"] == "value"
    finally:
        if history_file.exists():
            history_file.unlink()


def test_load_history_with_timezone_naive_datetimes():
    """Test loading history with timezone-naive datetimes."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        # Create a history file with timezone-naive datetime
        naive_datetime = datetime.utcnow()
        data = {
            "test_run_1": {
                "run_id": "test_run_1",
                "module_id": "test_module",
                "module_name": "Test Module",
                "status": "completed",
                "created_at": naive_datetime.isoformat(),
                "started_at": None,
                "completed_at": None,
                "duration_seconds": None,
                "progress_percent": None,
                "items_processed": None,
                "items_total": None,
                "exit_code": 0,
                "error_message": None,
                "parameters": {}
            }
        }
        
        with open(history_file, 'w') as f:
            json.dump(data, f)
        
        # Load the registry
        registry = RunRegistry(history_file=history_file)
        
        # Should have loaded the run and converted to timezone-aware
        assert len(registry.runs) == 1
        run = registry.runs["test_run_1"]
        assert run.created_at.tzinfo is not None
    finally:
        if history_file.exists():
            history_file.unlink()
