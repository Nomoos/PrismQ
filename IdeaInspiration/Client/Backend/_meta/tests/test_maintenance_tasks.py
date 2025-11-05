"""Integration tests for maintenance tasks."""

import asyncio
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile

from src.core.maintenance import (
    cleanup_old_runs,
    check_system_health,
    cleanup_temp_files,
    log_statistics,
    MAINTENANCE_TASKS,
)


class TestCleanupOldRuns:
    """Test suite for cleanup_old_runs maintenance task."""
    
    @pytest.mark.asyncio
    async def test_cleanup_old_runs_no_registry(self):
        """Test cleanup with default registry import."""
        # Mock the RunRegistry at the point it's imported
        with patch('src.core.run_registry.RunRegistry') as mock_registry_class:
            mock_registry = MagicMock()
            mock_registry_class.return_value = mock_registry
            
            from src.models.run import RunStatus
            from datetime import timezone
            
            # Create mock runs
            old_run = MagicMock()
            old_run.run_id = "old-run"
            old_run.status = RunStatus.COMPLETED
            old_run.completed_at = datetime.now(timezone.utc) - timedelta(hours=48)
            
            recent_run = MagicMock()
            recent_run.run_id = "recent-run"
            recent_run.status = RunStatus.COMPLETED
            recent_run.completed_at = datetime.now(timezone.utc) - timedelta(hours=1)
            
            running_run = MagicMock()
            running_run.run_id = "running-run"
            running_run.status = RunStatus.RUNNING
            running_run.completed_at = datetime.now(timezone.utc) - timedelta(hours=48)
            
            mock_registry.runs = {
                "old-run": old_run,
                "recent-run": recent_run,
                "running-run": running_run
            }
            mock_registry._save_history = MagicMock()
            
            # Run cleanup
            count = await cleanup_old_runs(max_age_hours=24)
            
            # Should have cleaned up only the old completed run
            assert count == 1
            assert "old-run" not in mock_registry.runs
            mock_registry._save_history.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_old_runs_with_registry(self):
        """Test cleanup with provided registry."""
        mock_registry = MagicMock()
        
        from src.models.run import RunStatus
        from datetime import timezone
        
        # Create mock runs
        old_completed = MagicMock()
        old_completed.run_id = "old-completed"
        old_completed.status = RunStatus.COMPLETED
        old_completed.completed_at = datetime.now(timezone.utc) - timedelta(hours=48)
        
        old_failed = MagicMock()
        old_failed.run_id = "old-failed"
        old_failed.status = RunStatus.FAILED
        old_failed.completed_at = datetime.now(timezone.utc) - timedelta(hours=36)
        
        old_cancelled = MagicMock()
        old_cancelled.run_id = "old-cancelled"
        old_cancelled.status = RunStatus.CANCELLED
        old_cancelled.completed_at = datetime.now(timezone.utc) - timedelta(hours=30)
        
        mock_registry.runs = {
            "old-completed": old_completed,
            "old-failed": old_failed,
            "old-cancelled": old_cancelled
        }
        mock_registry._save_history = MagicMock()
        
        # Run cleanup
        count = await cleanup_old_runs(max_age_hours=24, registry=mock_registry)
        
        # Should have cleaned up all three old runs
        assert count == 3
        assert len(mock_registry.runs) == 0
        mock_registry._save_history.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_old_runs_empty(self):
        """Test cleanup with no old runs."""
        mock_registry = MagicMock()
        mock_registry.runs = {}
        mock_registry._save_history = MagicMock()
        
        count = await cleanup_old_runs(max_age_hours=24, registry=mock_registry)
        
        assert count == 0
        # Should not save history if nothing was removed
        mock_registry._save_history.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cleanup_old_runs_partial_failure(self):
        """Test cleanup when some removals fail."""
        mock_registry = MagicMock()
        
        from src.models.run import RunStatus
        from datetime import timezone
        
        # Create mock runs
        runs = {}
        for i in range(3):
            run = MagicMock()
            run.run_id = f"run-{i}"
            run.status = RunStatus.COMPLETED
            run.completed_at = datetime.now(timezone.utc) - timedelta(hours=48)
            runs[f"run-{i}"] = run
        
        # Create a dict that raises error on second deletion
        class FailingDict(dict):
            def __delitem__(self, key):
                if key == "run-1":
                    raise Exception("Removal failed")
                super().__delitem__(key)
        
        mock_registry.runs = FailingDict(runs)
        mock_registry._save_history = MagicMock()
        
        # Run cleanup - should continue despite error
        count = await cleanup_old_runs(max_age_hours=24, registry=mock_registry)
        
        # Should have cleaned up 2 out of 3 (one failed)
        assert count == 2
        assert "run-1" in mock_registry.runs
        mock_registry._save_history.assert_called_once()


class TestCheckSystemHealth:
    """Test suite for check_system_health maintenance task."""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        with patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk, \
             patch('psutil.cpu_percent') as mock_cpu:
            # Mock healthy system
            mock_memory.return_value = MagicMock(percent=50.0)
            mock_disk.return_value = MagicMock(percent=60.0)
            mock_cpu.return_value = 30.0
            
            health = await check_system_health()
            
            assert health["status"] == "healthy"
            assert "checks" in health
            assert health["checks"]["memory"]["status"] == "ok"
            assert health["checks"]["disk"]["status"] == "ok"
            assert health["checks"]["cpu"]["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_health_check_high_memory(self):
        """Test health check with high memory usage."""
        with patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk, \
             patch('psutil.cpu_percent') as mock_cpu:
            # Mock high memory usage
            mock_memory.return_value = MagicMock(percent=85.0)
            mock_disk.return_value = MagicMock(percent=60.0)
            mock_cpu.return_value = 30.0
            
            health = await check_system_health()
            
            assert health["status"] == "warning"
            assert health["checks"]["memory"]["status"] == "warning"
            assert health["checks"]["disk"]["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_health_check_high_disk(self):
        """Test health check with high disk usage."""
        with patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk, \
             patch('psutil.cpu_percent') as mock_cpu:
            # Mock high disk usage
            mock_memory.return_value = MagicMock(percent=50.0)
            mock_disk.return_value = MagicMock(percent=95.0)
            mock_cpu.return_value = 30.0
            
            health = await check_system_health()
            
            assert health["status"] == "warning"
            assert health["checks"]["disk"]["status"] == "warning"
    
    @pytest.mark.asyncio
    async def test_health_check_many_tasks(self):
        """Test health check with many asyncio tasks."""
        with patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk, \
             patch('psutil.cpu_percent') as mock_cpu, \
             patch('src.core.maintenance.asyncio.all_tasks') as mock_all_tasks:
            
            # Mock healthy system but many tasks
            mock_memory.return_value = MagicMock(percent=50.0)
            mock_disk.return_value = MagicMock(percent=60.0)
            mock_cpu.return_value = 30.0
            
            # Create 150 mock tasks
            mock_all_tasks.return_value = [MagicMock() for _ in range(150)]
            
            health = await check_system_health()
            
            assert health["status"] == "warning"
            assert health["checks"]["asyncio_tasks"]["status"] == "warning"
            assert health["checks"]["asyncio_tasks"]["count"] == 150
    
    @pytest.mark.asyncio
    async def test_health_check_error(self):
        """Test health check when psutil fails."""
        with patch('psutil.virtual_memory') as mock_memory:
            # Make psutil raise an error
            mock_memory.side_effect = Exception("psutil error")
            
            health = await check_system_health()
            
            assert health["status"] == "error"
            assert "error" in health


class TestCleanupTempFiles:
    """Test suite for cleanup_temp_files maintenance task."""
    
    @pytest.mark.asyncio
    async def test_cleanup_temp_files(self):
        """Test cleaning up old temporary files."""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_dir = Path(tmpdir)
            
            # Create some old and new files
            old_file = temp_dir / "old_file.txt"
            old_file.write_text("old")
            
            new_file = temp_dir / "new_file.txt"
            new_file.write_text("new")
            
            # Manually set old file's mtime to simulate age
            import os
            old_time = (datetime.now() - timedelta(hours=48)).timestamp()
            os.utime(old_file, (old_time, old_time))
            
            # Run cleanup
            count = await cleanup_temp_files(temp_dir=temp_dir, max_age_hours=24)
            
            # Old file should be removed, new file should remain
            assert not old_file.exists()
            assert new_file.exists()
            assert count == 1
    
    @pytest.mark.asyncio
    async def test_cleanup_temp_files_nonexistent_dir(self):
        """Test cleanup when directory doesn't exist."""
        non_existent = Path("/tmp/nonexistent_prismq_temp")
        
        # Should return 0 without error
        count = await cleanup_temp_files(temp_dir=non_existent, max_age_hours=24)
        assert count == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_temp_files_nested(self):
        """Test cleanup of nested temporary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_dir = Path(tmpdir)
            
            # Create nested directory structure
            nested_dir = temp_dir / "subdir" / "nested"
            nested_dir.mkdir(parents=True)
            
            # Create old file in nested directory
            old_nested = nested_dir / "old_nested.txt"
            old_nested.write_text("old nested")
            
            # Set old time
            import os
            old_time = (datetime.now() - timedelta(hours=48)).timestamp()
            os.utime(old_nested, (old_time, old_time))
            
            # Run cleanup
            count = await cleanup_temp_files(temp_dir=temp_dir, max_age_hours=24)
            
            # Nested old file should be removed
            assert not old_nested.exists()
            assert count == 1


class TestLogStatistics:
    """Test suite for log_statistics maintenance task."""
    
    @pytest.mark.asyncio
    async def test_log_statistics(self):
        """Test statistics logging."""
        with patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk, \
             patch('psutil.cpu_percent') as mock_cpu:
            # Mock system stats
            mock_memory.return_value = MagicMock(percent=60.0)
            mock_cpu.return_value = 45.0
            mock_disk.return_value = MagicMock(percent=70.0)
            
            stats = await log_statistics()
            
            assert "timestamp" in stats
            assert "asyncio" in stats
            assert "system" in stats
            assert stats["system"]["memory_percent"] == 60.0
            assert stats["system"]["cpu_percent"] == 45.0
            assert stats["system"]["disk_percent"] == 70.0
    
    @pytest.mark.asyncio
    async def test_log_statistics_with_tasks(self):
        """Test statistics logging includes task count."""
        with patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk, \
             patch('psutil.cpu_percent') as mock_cpu, \
             patch('src.core.maintenance.asyncio.all_tasks') as mock_all_tasks:
            
            mock_memory.return_value = MagicMock(percent=60.0)
            mock_cpu.return_value = 45.0
            mock_disk.return_value = MagicMock(percent=70.0)
            
            # Create mock tasks (5 total, 2 done)
            mock_tasks = []
            for i in range(5):
                task = MagicMock()
                task.done.return_value = (i < 2)  # First 2 are done
                mock_tasks.append(task)
            mock_all_tasks.return_value = mock_tasks
            
            stats = await log_statistics()
            
            assert stats["asyncio"]["total_tasks"] == 5
            assert stats["asyncio"]["pending_tasks"] == 3
    
    @pytest.mark.asyncio
    async def test_log_statistics_error(self):
        """Test statistics logging when error occurs."""
        with patch('psutil.virtual_memory') as mock_memory:
            # Make psutil fail
            mock_memory.side_effect = Exception("psutil error")
            
            stats = await log_statistics()
            
            assert "error" in stats
            assert stats["error"] == "psutil error"


class TestMaintenanceTasks:
    """Test suite for MAINTENANCE_TASKS configuration."""
    
    def test_maintenance_tasks_structure(self):
        """Test that MAINTENANCE_TASKS is properly structured."""
        assert isinstance(MAINTENANCE_TASKS, list)
        assert len(MAINTENANCE_TASKS) > 0
        
        for task_config in MAINTENANCE_TASKS:
            assert "name" in task_config
            assert "interval" in task_config
            assert "func" in task_config
            assert "description" in task_config
            
            # Name should be a string
            assert isinstance(task_config["name"], str)
            
            # Interval should be a timedelta
            assert isinstance(task_config["interval"], timedelta)
            
            # Function should be callable
            assert callable(task_config["func"])
            
            # Description should be a string
            assert isinstance(task_config["description"], str)
    
    def test_maintenance_tasks_unique_names(self):
        """Test that all maintenance tasks have unique names."""
        names = [task["name"] for task in MAINTENANCE_TASKS]
        assert len(names) == len(set(names)), "Duplicate task names found"
    
    @pytest.mark.asyncio
    async def test_all_maintenance_tasks_callable(self):
        """Test that all maintenance task functions are actually callable."""
        for task_config in MAINTENANCE_TASKS:
            func = task_config["func"]
            kwargs = task_config.get("kwargs", {})
            
            # Should be able to call the function (we'll mock dependencies)
            assert asyncio.iscoroutinefunction(func)
