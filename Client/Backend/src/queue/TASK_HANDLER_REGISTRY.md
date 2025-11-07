# Task Handler Registry

**Worker 10 - Issue #339**: Ensure Client takes only registered task handlers  
**Status**: ✅ Implemented  
**Date**: 2025-11-06

## Overview

The Task Handler Registry system ensures that the PrismQ Client only processes tasks with **explicitly registered handlers**. This prevents automatic module discovery from the database and provides better control over which task types can be executed.

## Key Principles

1. **Explicit Registration**: All task handlers must be registered before tasks of that type can be processed
2. **No Auto-Discovery**: The system does NOT automatically discover task types from the database
3. **Fail Fast**: Tasks without registered handlers fail immediately (no retry)
4. **Type Safety**: Each task type is mapped to a specific handler function
5. **Thread Safe**: Registry operations are protected by locks for concurrent access

## Quick Start

### Basic Usage

```python
from src.queue import (
    TaskHandlerRegistry,
    WorkerEngine,
    QueueDatabase,
    Task
)

# Create a registry
registry = TaskHandlerRegistry()

# Define a task handler
def email_handler(task: Task):
    payload = task.get_payload_dict()
    send_email(
        to=payload['to'],
        subject=payload['subject'],
        body=payload['body']
    )

# Register the handler
registry.register_handler(
    task_type="send_email",
    handler=email_handler,
    description="Sends email notifications",
    version="1.0.0"
)

# Create worker with registry
worker = WorkerEngine(
    db=QueueDatabase(),
    worker_id="worker-01",
    handler_registry=registry  # ← Registry is passed here
)

# Worker will only process registered task types
worker.run_loop()  # Automatically routes tasks to correct handlers
```

### Using Global Registry

```python
from src.queue import get_global_registry

# Get the singleton global registry
registry = get_global_registry()

# Register handlers
registry.register_handler("task_type_1", handler_1)
registry.register_handler("task_type_2", handler_2)

# All workers can use the global registry
worker = WorkerEngine(
    db=db,
    worker_id="worker-01",
    handler_registry=registry
)
```

## API Reference

### TaskHandlerRegistry

Main class for managing task handlers.

#### Methods

##### `register_handler(task_type, handler, description="", version="1.0.0", allow_override=False)`

Register a new task handler.

**Parameters:**
- `task_type` (str): Unique identifier for the task type
- `handler` (Callable[[Task], None]): Function that processes the task
- `description` (str, optional): Human-readable description
- `version` (str, optional): Version string for tracking
- `allow_override` (bool, optional): Allow replacing existing handlers

**Raises:**
- `TaskHandlerAlreadyRegisteredError`: If handler exists and `allow_override=False`
- `ValueError`: If task_type is empty or handler is not callable

**Example:**
```python
def my_handler(task: Task):
    print(f"Processing {task.type}")

registry.register_handler("my_task", my_handler, "My custom handler", "1.0.0")
```

##### `get_handler(task_type) -> Callable[[Task], None]`

Get the registered handler for a task type.

**Parameters:**
- `task_type` (str): Task type to get handler for

**Returns:**
- Handler function for the task type

**Raises:**
- `TaskHandlerNotRegisteredError`: If no handler registered

**Example:**
```python
handler = registry.get_handler("send_email")
handler(task)
```

##### `is_registered(task_type) -> bool`

Check if a handler is registered for a task type.

**Example:**
```python
if registry.is_registered("send_email"):
    print("Email handler is registered")
```

##### `get_registered_types() -> Set[str]`

Get all registered task types.

**Example:**
```python
types = registry.get_registered_types()
print(f"Registered: {', '.join(types)}")
```

##### `unregister_handler(task_type) -> bool`

Remove a registered handler.

**Returns:**
- `True` if handler was removed, `False` if it didn't exist

##### `get_handler_info(task_type) -> Optional[TaskHandlerInfo]`

Get detailed information about a registered handler.

**Returns:**
- `TaskHandlerInfo` object with task_type, handler, description, version

##### `validate_task(task)`

Validate that a task has a registered handler.

**Raises:**
- `TaskHandlerNotRegisteredError`: If task type has no handler

##### `clear()`

Remove all registered handlers. Useful for testing.

### Global Registry Functions

#### `get_global_registry() -> TaskHandlerRegistry`

Get the global singleton registry instance.

#### `reset_global_registry() -> None`

Reset the global registry (creates a new empty instance). Useful for testing.

## Integration with WorkerEngine

### Legacy Behavior (Backward Compatible)

Workers can still use explicit handler functions:

```python
def my_handler(task: Task):
    print(f"Processing {task.type}")

# Pass handler explicitly
worker = WorkerEngine(db=db, worker_id="worker-01")
worker.claim_and_process(task_handler=my_handler)
```

### New Behavior (Registry-Based)

Workers use the registry to route tasks automatically:

```python
# Register handlers
registry = TaskHandlerRegistry()
registry.register_handler("email", email_handler)
registry.register_handler("report", report_handler)

# Worker automatically routes based on task type
worker = WorkerEngine(
    db=db,
    worker_id="worker-01",
    handler_registry=registry
)

# No need to specify handler - registry handles it
worker.claim_and_process()  # Routes to correct handler based on task.type
```

### Hybrid Approach

You can combine both approaches:

```python
worker = WorkerEngine(
    db=db,
    worker_id="worker-01",
    handler_registry=registry
)

# Use registry for most tasks
worker.claim_and_process()

# Override for specific cases
worker.claim_and_process(task_handler=special_handler)
```

## Error Handling

### Task Without Registered Handler

When a worker encounters a task type without a registered handler:

1. The task is **immediately failed** (no retry)
2. Error message indicates the missing handler
3. List of registered types is included in error message

```python
# If task type "unknown_task" is not registered:
# Error: "No handler registered for task type 'unknown_task'. 
#         Registered types: ['email', 'report', 'backup']"
```

### Handler Registration Errors

```python
# Duplicate registration without override
try:
    registry.register_handler("email", handler1)
    registry.register_handler("email", handler2)  # Raises error
except TaskHandlerAlreadyRegisteredError:
    # Use allow_override=True to replace
    registry.register_handler("email", handler2, allow_override=True)

# Invalid inputs
registry.register_handler("", handler)  # ValueError: cannot be empty
registry.register_handler("task", "not_callable")  # ValueError: must be callable
```

## Best Practices

### 1. Register All Handlers at Startup

```python
def setup_handlers():
    """Initialize all task handlers at application startup."""
    registry = get_global_registry()
    
    registry.register_handler("send_email", email_handler)
    registry.register_handler("generate_report", report_handler)
    registry.register_handler("backup_data", backup_handler)
    
    return registry

# In main.py or startup code
registry = setup_handlers()
```

### 2. Use Descriptive Handler Names

```python
# Good - clear what it does
def send_welcome_email_handler(task: Task):
    pass

# Better - follows naming convention
def handle_send_welcome_email(task: Task):
    pass
```

### 3. Version Your Handlers

```python
registry.register_handler(
    "process_payment",
    process_payment_v2,
    version="2.0.0",
    allow_override=True  # Override v1
)
```

### 4. Document Handler Requirements

```python
def payment_handler(task: Task):
    """
    Process payment transaction.
    
    Required payload fields:
    - amount (float): Transaction amount
    - currency (str): ISO currency code
    - customer_id (str): Customer identifier
    
    Optional payload fields:
    - description (str): Payment description
    """
    payload = task.get_payload_dict()
    # ... implementation
```

### 5. Use Type Hints

```python
from typing import Any, Dict

def typed_handler(task: Task) -> None:
    """Handler with explicit type hints."""
    payload: Dict[str, Any] = task.get_payload_dict()
    amount: float = payload.get('amount', 0.0)
    # ... process
```

## Testing

### Unit Tests

```python
def test_handler_registration():
    registry = TaskHandlerRegistry()
    
    def my_handler(task: Task):
        pass
    
    registry.register_handler("test_task", my_handler)
    
    assert registry.is_registered("test_task")
    assert registry.get_handler("test_task") is my_handler
```

### Integration Tests

```python
def test_worker_with_registry():
    db = QueueDatabase(":memory:")
    db.initialize_schema()
    
    registry = TaskHandlerRegistry()
    processed_tasks = []
    
    def test_handler(task: Task):
        processed_tasks.append(task.id)
    
    registry.register_handler("test_task", test_handler)
    
    # Enqueue task
    with db.transaction() as conn:
        conn.execute(
            "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
            ("test_task", "{}")
        )
    
    # Process with worker
    worker = WorkerEngine(
        db=db,
        worker_id="test-worker",
        handler_registry=registry
    )
    
    worker.claim_and_process()
    
    assert len(processed_tasks) == 1
```

### Reset Registry Between Tests

```python
def setup_method(self):
    """Reset global registry before each test."""
    reset_global_registry()
    self.registry = get_global_registry()
```

## Migration Guide

### From Unregistered Handlers

**Before (Legacy):**
```python
def process_all_tasks(task: Task):
    if task.type == "email":
        send_email(task)
    elif task.type == "report":
        generate_report(task)
    # etc...

worker.run_loop(task_handler=process_all_tasks)
```

**After (Registry-Based):**
```python
registry = TaskHandlerRegistry()
registry.register_handler("email", send_email_handler)
registry.register_handler("report", generate_report_handler)

worker = WorkerEngine(
    db=db,
    worker_id="worker-01",
    handler_registry=registry
)

worker.run_loop()  # No handler needed - registry routes automatically
```

### Gradual Migration

1. Keep legacy handler working
2. Create registry alongside
3. Register handlers one by one
4. Test each registration
5. Remove legacy handler when all types registered

## Security Considerations

### 1. Validate Task Payloads

```python
def secure_handler(task: Task):
    payload = task.get_payload_dict()
    
    # Validate required fields
    if 'user_id' not in payload:
        raise ValueError("Missing user_id")
    
    # Sanitize inputs
    user_id = str(payload['user_id']).strip()
    
    # Process safely
    process_user_data(user_id)
```

### 2. Prevent Handler Injection

The registry prevents dynamic handler registration from task payloads:

```python
# ✗ BAD - Don't do this
payload = task.get_payload_dict()
handler_name = payload['handler']  # User-controlled!
handler = eval(handler_name)  # DANGEROUS!

# ✓ GOOD - Use registry
handler = registry.get_handler(task.type)  # Type is validated
```

### 3. Limit Handler Permissions

```python
def restricted_handler(task: Task):
    """Handler with limited permissions."""
    # Only specific operations allowed
    allowed_operations = ['read', 'validate']
    
    payload = task.get_payload_dict()
    operation = payload.get('operation')
    
    if operation not in allowed_operations:
        raise PermissionError(f"Operation {operation} not allowed")
```

## Demo Script

Run the demo to see the registry in action:

```bash
cd Backend
python src/queue/demo_task_handler_registry.py
```

The demo shows:
- Basic handler registration
- Worker integration
- Global registry usage
- Handler override
- Error handling for unregistered types

## See Also

- [WorkerEngine Documentation](WORKER_SUPPORT.md)
- [Queue API Documentation](QUEUE_API.md)
- [Integration Guide](../../../_meta/docs/INTEGRATION_GUIDE.md)
- [Issue #339: Integration](../../../_meta/issues/done/queue-system/README.md)
