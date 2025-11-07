"""
Tests for TaskHandlerRegistry.

Tests Worker 10 Issue #339: Ensure Client takes only registered task handlers.
"""

import pytest
from unittest.mock import Mock

from src.queue import (
    TaskHandlerRegistry,
    TaskHandlerInfo,
    TaskHandlerNotRegisteredError,
    TaskHandlerAlreadyRegisteredError,
    get_global_registry,
    reset_global_registry,
    Task,
)


class TestTaskHandlerRegistry:
    """Test TaskHandlerRegistry functionality."""
    
    def setup_method(self):
        """Create a fresh registry for each test."""
        self.registry = TaskHandlerRegistry()
    
    def test_register_handler_basic(self):
        """Test basic handler registration."""
        def my_handler(task: Task):
            pass
        
        self.registry.register_handler("test_task", my_handler)
        
        assert self.registry.is_registered("test_task")
        assert "test_task" in self.registry.get_registered_types()
    
    def test_register_handler_with_metadata(self):
        """Test handler registration with description and version."""
        def my_handler(task: Task):
            pass
        
        self.registry.register_handler(
            "test_task",
            my_handler,
            description="Test handler for testing",
            version="2.0.0"
        )
        
        info = self.registry.get_handler_info("test_task")
        assert info is not None
        assert info.task_type == "test_task"
        assert info.description == "Test handler for testing"
        assert info.version == "2.0.0"
    
    def test_register_duplicate_handler_raises_error(self):
        """Test that registering duplicate handler raises error."""
        def handler1(task: Task):
            pass
        
        def handler2(task: Task):
            pass
        
        self.registry.register_handler("test_task", handler1)
        
        with pytest.raises(TaskHandlerAlreadyRegisteredError) as exc_info:
            self.registry.register_handler("test_task", handler2)
        
        assert "already registered" in str(exc_info.value)
    
    def test_register_duplicate_with_override(self):
        """Test that allow_override allows replacing handlers."""
        def handler1(task: Task):
            return "handler1"
        
        def handler2(task: Task):
            return "handler2"
        
        self.registry.register_handler("test_task", handler1)
        
        # Override should succeed
        self.registry.register_handler("test_task", handler2, allow_override=True)
        
        handler = self.registry.get_handler("test_task")
        # Should get the second handler
        assert handler is handler2
    
    def test_register_empty_task_type_raises_error(self):
        """Test that empty task type raises ValueError."""
        def my_handler(task: Task):
            pass
        
        with pytest.raises(ValueError) as exc_info:
            self.registry.register_handler("", my_handler)
        
        assert "cannot be empty" in str(exc_info.value)
    
    def test_register_non_callable_raises_error(self):
        """Test that non-callable handler raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            self.registry.register_handler("test_task", "not_a_function")
        
        assert "must be callable" in str(exc_info.value)
    
    def test_get_handler_success(self):
        """Test getting a registered handler."""
        def my_handler(task: Task):
            pass
        
        self.registry.register_handler("test_task", my_handler)
        
        handler = self.registry.get_handler("test_task")
        assert handler is my_handler
    
    def test_get_handler_not_registered_raises_error(self):
        """Test that getting unregistered handler raises error."""
        with pytest.raises(TaskHandlerNotRegisteredError) as exc_info:
            self.registry.get_handler("unknown_task")
        
        assert "No handler registered" in str(exc_info.value)
        assert "unknown_task" in str(exc_info.value)
    
    def test_unregister_handler(self):
        """Test unregistering a handler."""
        def my_handler(task: Task):
            pass
        
        self.registry.register_handler("test_task", my_handler)
        assert self.registry.is_registered("test_task")
        
        result = self.registry.unregister_handler("test_task")
        assert result is True
        assert not self.registry.is_registered("test_task")
    
    def test_unregister_nonexistent_handler(self):
        """Test unregistering a handler that doesn't exist."""
        result = self.registry.unregister_handler("unknown_task")
        assert result is False
    
    def test_is_registered(self):
        """Test checking if handler is registered."""
        def my_handler(task: Task):
            pass
        
        assert not self.registry.is_registered("test_task")
        
        self.registry.register_handler("test_task", my_handler)
        assert self.registry.is_registered("test_task")
    
    def test_get_registered_types(self):
        """Test getting all registered types."""
        def handler1(task: Task):
            pass
        
        def handler2(task: Task):
            pass
        
        def handler3(task: Task):
            pass
        
        self.registry.register_handler("task1", handler1)
        self.registry.register_handler("task2", handler2)
        self.registry.register_handler("task3", handler3)
        
        types = self.registry.get_registered_types()
        assert types == {"task1", "task2", "task3"}
    
    def test_get_handler_info_registered(self):
        """Test getting handler info for registered handler."""
        def my_handler(task: Task):
            pass
        
        self.registry.register_handler(
            "test_task",
            my_handler,
            description="Test handler",
            version="1.5.0"
        )
        
        info = self.registry.get_handler_info("test_task")
        assert info is not None
        assert isinstance(info, TaskHandlerInfo)
        assert info.task_type == "test_task"
        assert info.handler is my_handler
        assert info.description == "Test handler"
        assert info.version == "1.5.0"
    
    def test_get_handler_info_not_registered(self):
        """Test getting handler info for unregistered handler."""
        info = self.registry.get_handler_info("unknown_task")
        assert info is None
    
    def test_clear_handlers(self):
        """Test clearing all handlers."""
        def handler1(task: Task):
            pass
        
        def handler2(task: Task):
            pass
        
        self.registry.register_handler("task1", handler1)
        self.registry.register_handler("task2", handler2)
        
        assert len(self.registry.get_registered_types()) == 2
        
        self.registry.clear()
        
        assert len(self.registry.get_registered_types()) == 0
        assert not self.registry.is_registered("task1")
        assert not self.registry.is_registered("task2")
    
    def test_validate_task_with_registered_handler(self):
        """Test validating task with registered handler."""
        def my_handler(task: Task):
            pass
        
        self.registry.register_handler("test_task", my_handler)
        
        task = Task(id=1, type="test_task")
        
        # Should not raise
        self.registry.validate_task(task)
    
    def test_validate_task_without_registered_handler(self):
        """Test validating task without registered handler."""
        task = Task(id=1, type="unknown_task")
        
        with pytest.raises(TaskHandlerNotRegisteredError) as exc_info:
            self.registry.validate_task(task)
        
        assert "Cannot process task #1" in str(exc_info.value)
        assert "unknown_task" in str(exc_info.value)
    
    def test_multiple_registrations(self):
        """Test registering multiple handlers."""
        handlers = {}
        for i in range(10):
            task_type = f"task_{i}"
            handler = Mock()
            handlers[task_type] = handler
            self.registry.register_handler(task_type, handler)
        
        # Verify all registered
        registered_types = self.registry.get_registered_types()
        assert len(registered_types) == 10
        
        # Verify each handler can be retrieved
        for task_type, expected_handler in handlers.items():
            actual_handler = self.registry.get_handler(task_type)
            assert actual_handler is expected_handler


class TestGlobalRegistry:
    """Test global registry singleton."""
    
    def test_get_global_registry(self):
        """Test getting global registry singleton."""
        registry1 = get_global_registry()
        registry2 = get_global_registry()
        
        # Should be the same instance
        assert registry1 is registry2
    
    def test_reset_global_registry(self):
        """Test resetting global registry."""
        registry1 = get_global_registry()
        
        def my_handler(task: Task):
            pass
        
        registry1.register_handler("test_task", my_handler)
        assert registry1.is_registered("test_task")
        
        # Reset
        reset_global_registry()
        
        registry2 = get_global_registry()
        
        # Should be a new instance with no handlers
        assert not registry2.is_registered("test_task")
        assert len(registry2.get_registered_types()) == 0


class TestThreadSafety:
    """Test thread safety of registry."""
    
    def test_concurrent_registration(self):
        """Test that concurrent registration is thread-safe."""
        import threading
        
        registry = TaskHandlerRegistry()
        errors = []
        
        def register_handler(task_type):
            try:
                def handler(task: Task):
                    pass
                registry.register_handler(task_type, handler)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads registering different handlers
        threads = []
        for i in range(20):
            thread = threading.Thread(target=register_handler, args=(f"task_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Should have no errors
        assert len(errors) == 0
        
        # Should have all 20 handlers registered
        assert len(registry.get_registered_types()) == 20
