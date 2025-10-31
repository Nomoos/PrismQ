"""Unit tests for ResourceManager."""

import pytest
from unittest.mock import Mock, patch

from src.core.resource_manager import ResourceManager


def test_resource_manager_initialization():
    """Test ResourceManager initialization with default values."""
    rm = ResourceManager()
    
    assert rm.cpu_threshold_percent == 80.0
    assert rm.memory_required_bytes == 4 * 1024 * 1024 * 1024  # 4 GB


def test_resource_manager_custom_thresholds():
    """Test ResourceManager initialization with custom thresholds."""
    rm = ResourceManager(cpu_threshold_percent=90.0, memory_required_gb=8.0)
    
    assert rm.cpu_threshold_percent == 90.0
    assert rm.memory_required_bytes == 8 * 1024 * 1024 * 1024  # 8 GB


@patch('src.core.resource_manager.psutil')
def test_check_resources_available_success(mock_psutil):
    """Test resource check when resources are available."""
    # Mock CPU and memory as available
    mock_psutil.cpu_percent.return_value = 50.0
    mock_memory = Mock()
    mock_memory.available = 10 * 1024 * 1024 * 1024  # 10 GB
    mock_psutil.virtual_memory.return_value = mock_memory
    
    rm = ResourceManager(cpu_threshold_percent=80.0, memory_required_gb=4.0)
    available, reason = rm.check_resources_available()
    
    assert available is True
    assert reason is None


@patch('src.core.resource_manager.psutil')
def test_check_resources_cpu_too_high(mock_psutil):
    """Test resource check when CPU usage is too high."""
    # Mock CPU as too high
    mock_psutil.cpu_percent.return_value = 85.0
    mock_memory = Mock()
    mock_memory.available = 10 * 1024 * 1024 * 1024  # 10 GB
    mock_psutil.virtual_memory.return_value = mock_memory
    
    rm = ResourceManager(cpu_threshold_percent=80.0, memory_required_gb=4.0)
    available, reason = rm.check_resources_available()
    
    assert available is False
    assert "CPU usage too high" in reason


@patch('src.core.resource_manager.psutil')
def test_check_resources_insufficient_memory(mock_psutil):
    """Test resource check when memory is insufficient."""
    # Mock CPU as ok, but memory as insufficient
    mock_psutil.cpu_percent.return_value = 50.0
    mock_memory = Mock()
    mock_memory.available = 2 * 1024 * 1024 * 1024  # 2 GB (less than required 4 GB)
    mock_psutil.virtual_memory.return_value = mock_memory
    
    rm = ResourceManager(cpu_threshold_percent=80.0, memory_required_gb=4.0)
    available, reason = rm.check_resources_available()
    
    assert available is False
    assert "Insufficient memory" in reason


@patch('src.core.resource_manager.psutil', None)
def test_check_resources_no_psutil():
    """Test resource check when psutil is not available."""
    rm = ResourceManager()
    available, reason = rm.check_resources_available()
    
    # Should allow run when psutil is not available
    assert available is True
    assert reason is None


@patch('src.core.resource_manager.psutil')
def test_get_system_stats(mock_psutil):
    """Test getting system statistics."""
    # Mock psutil values
    mock_psutil.cpu_percent.return_value = 45.0
    mock_memory = Mock()
    mock_memory.total = 64 * 1024 * 1024 * 1024  # 64 GB
    mock_memory.available = 32 * 1024 * 1024 * 1024  # 32 GB
    mock_memory.percent = 50.0
    mock_psutil.virtual_memory.return_value = mock_memory
    
    rm = ResourceManager()
    stats = rm.get_system_stats()
    
    assert stats["cpu_percent"] == 45.0
    assert stats["memory_total_gb"] == 64.0
    assert stats["memory_available_gb"] == 32.0
    assert stats["memory_used_percent"] == 50.0
    assert stats["psutil_available"] is True


@patch('src.core.resource_manager.psutil', None)
def test_get_system_stats_no_psutil():
    """Test getting system statistics when psutil is not available."""
    rm = ResourceManager()
    stats = rm.get_system_stats()
    
    assert stats["cpu_percent"] == 0.0
    assert stats["memory_total_gb"] == 0.0
    assert stats["memory_available_gb"] == 0.0
    assert stats["memory_used_percent"] == 0.0
    assert stats["psutil_available"] is False


@patch('src.core.resource_manager.psutil')
def test_check_resources_at_threshold(mock_psutil):
    """Test resource check when exactly at threshold."""
    # Mock CPU at exact threshold
    mock_psutil.cpu_percent.return_value = 80.0
    mock_memory = Mock()
    mock_memory.available = 10 * 1024 * 1024 * 1024  # 10 GB
    mock_psutil.virtual_memory.return_value = mock_memory
    
    rm = ResourceManager(cpu_threshold_percent=80.0, memory_required_gb=4.0)
    available, reason = rm.check_resources_available()
    
    # At threshold should still be available (not exceeding)
    assert available is True
    assert reason is None
