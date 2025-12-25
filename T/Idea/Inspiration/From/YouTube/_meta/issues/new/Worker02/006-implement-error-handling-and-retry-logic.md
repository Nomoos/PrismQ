# Issue #006: Implement Error Handling and Retry Logic

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 02 - Python Specialist  
**Language**: Python 3.10+  
**Status**: New  
**Priority**: High  
**Duration**: 2 days  
**Dependencies**: #002 (Worker Base Class), #005 (Plugin Architecture)

---

## Worker Details: Worker02 - Python Specialist

**Role**: Error Handling & Retry System Implementation  
**Expertise Required**:
- Exception handling patterns in Python
- Retry strategies and exponential backoff algorithms
- Error taxonomy and classification
- Logging and error context preservation
- Dead letter queue concepts

**Collaboration**:
- **Worker02** (self): Build on #002 and #005
- **Worker06** (Database): Coordinate on task status updates and DLQ storage
- **Worker01** (PM): Daily standup, error taxonomy review

**See**: `_meta/issues/new/Worker02/README.md` for complete role description

---

## Objective

Implement a robust error handling and retry system that classifies errors, manages retries with exponential backoff, preserves error context, and handles permanently failed tasks through a dead letter queue mechanism.

---

## Problem Statement

YouTube scraping can fail for various reasons:
- **Transient errors**: Network timeouts, rate limits, temporary API unavailability
- **Permanent errors**: Invalid URLs, deleted videos, API quota exhausted
- **Configuration errors**: Missing API keys, invalid parameters
- **System errors**: Out of memory, disk full

Currently:
- No standardized error classification
- No automatic retry mechanism
- No exponential backoff strategy
- No dead letter queue for failed tasks
- Limited error context preservation

We need:
1. **Error taxonomy** to classify errors as retryable or permanent
2. **Retry strategy** with exponential backoff and max attempts
3. **Error context preservation** for debugging
4. **Dead letter queue** for permanently failed tasks
5. **Metrics and logging** for error monitoring

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅

**RetryStrategy Responsibilities**:
- Determine if error should be retried
- Calculate retry delay (exponential backoff)
- Track retry attempts

**NOT Responsible For**:
- Error classification (ErrorClassifier)
- Task execution (Worker)
- Logging (separate logger)

**ErrorClassifier Responsibilities**:
- Classify errors as retryable or permanent
- Identify error categories (network, rate limit, etc.)
- Provide error metadata

**NOT Responsible For**:
- Retry logic (RetryStrategy)
- Task execution (Worker)
- Error logging (separate logger)

**ErrorHandler Responsibilities**:
- Coordinate error handling workflow
- Preserve error context
- Update task status
- Move failed tasks to DLQ

**NOT Responsible For**:
- Error classification (ErrorClassifier)
- Retry calculation (RetryStrategy)
- Task execution (Worker)

### Open/Closed Principle (OCP) ✅

**Open for Extension**:
- New error types can be added to classifier
- New retry strategies can be implemented
- Custom error handlers can be added

**Closed for Modification**:
- Core retry algorithm remains stable
- Error taxonomy interface is fixed
- Error context structure is standardized

### Liskov Substitution Principle (LSP) ✅

**Substitutability**:
- Different RetryStrategy implementations interchangeable
- ErrorClassifier implementations can be swapped
- No unexpected behavior changes

### Interface Segregation Principle (ISP) ✅

**Minimal Interfaces**:
```python
class RetryStrategy(Protocol):
    def should_retry(self, error: Exception, attempt: int) -> bool: ...
    def get_retry_delay(self, attempt: int) -> float: ...

class ErrorClassifier(Protocol):
    def is_retryable(self, error: Exception) -> bool: ...
    def get_error_category(self, error: Exception) -> str: ...
```

Only essential methods, no unnecessary dependencies.

### Dependency Inversion Principle (DIP) ✅

**Depend on Abstractions**:
- Workers depend on RetryStrategy protocol, not concrete implementations
- ErrorHandler depends on ErrorClassifier protocol
- Dependencies injected via constructor

---

## Proposed Solution

### Architecture Overview

```
Error Handling System
├── ErrorClassifier             # Error classification
│   ├── is_retryable()         # Check if error is retryable
│   ├── get_error_category()   # Categorize error
│   └── get_error_metadata()   # Extract error details
│
├── RetryStrategy               # Retry logic
│   ├── should_retry()         # Check if should retry
│   ├── get_retry_delay()      # Calculate backoff delay
│   └── increment_attempt()    # Track attempts
│
├── ErrorHandler                # Error handling coordinator
│   ├── handle_error()         # Main error handling
│   ├── log_error()            # Log with context
│   ├── update_task_status()   # Update in queue
│   └── move_to_dlq()          # Dead letter queue
│
└── Error Taxonomy
    ├── RetryableError         # Base for retryable errors
    ├── PermanentError         # Base for permanent errors
    └── Specific errors...     # NetworkError, RateLimitError, etc.
```

---

## Implementation Details

### File Structure

```
src/
├── workers/
│   ├── error_handler.py       # NEW: ErrorHandler coordinator
│   ├── retry_strategy.py      # NEW: Retry strategies
│   ├── error_classifier.py    # NEW: Error classification
│   ├── errors.py              # NEW: Custom exception classes
│   └── base_worker.py         # MODIFY: Integrate error handling
```

### 1. Error Taxonomy (Custom Exceptions)

**File**: `src/workers/errors.py`

```python
"""Custom exception classes for worker error handling.

This module defines the error taxonomy used throughout the worker system.
Errors are classified into retryable and permanent categories.
"""


class WorkerError(Exception):
    """Base exception for all worker errors."""
    pass


class RetryableError(WorkerError):
    """Base class for errors that can be retried.
    
    These errors are typically transient and may succeed on retry.
    """
    
    def __init__(self, message: str, retry_after: float = None):
        """Initialize retryable error.
        
        Args:
            message: Error message
            retry_after: Suggested retry delay in seconds (optional)
        """
        super().__init__(message)
        self.retry_after = retry_after


class PermanentError(WorkerError):
    """Base class for errors that should not be retried.
    
    These errors are permanent and will not succeed on retry.
    """
    pass


# Specific retryable errors

class NetworkError(RetryableError):
    """Network-related errors (timeouts, connection failures)."""
    pass


class RateLimitError(RetryableError):
    """Rate limit or quota exceeded errors."""
    pass


class TemporaryAPIError(RetryableError):
    """Temporary API unavailability."""
    pass


class DatabaseBusyError(RetryableError):
    """SQLite database is busy (SQLITE_BUSY)."""
    pass


# Specific permanent errors

class InvalidParametersError(PermanentError):
    """Invalid task parameters."""
    pass


class ResourceNotFoundError(PermanentError):
    """Resource not found (deleted video, invalid URL)."""
    pass


class AuthenticationError(PermanentError):
    """Authentication or authorization failures."""
    pass


class QuotaExhaustedError(PermanentError):
    """API quota exhausted for the day."""
    pass


class ConfigurationError(PermanentError):
    """Configuration errors (missing API keys, etc.)."""
    pass
```

### 2. Error Classifier

**File**: `src/workers/error_classifier.py`

```python
"""Error classifier for determining retry eligibility.

This module provides classification logic to determine if an error
is retryable or permanent, and to categorize errors.
"""

from typing import Dict, Any
import re

from .errors import (
    RetryableError, PermanentError, NetworkError, RateLimitError,
    TemporaryAPIError, DatabaseBusyError, InvalidParametersError,
    ResourceNotFoundError, AuthenticationError, QuotaExhaustedError
)


class ErrorClassifier:
    """Classifies errors as retryable or permanent.
    
    Analyzes exception type and message to determine:
    1. Whether the error is retryable
    2. The error category
    3. Recommended retry delay (if applicable)
    
    Example:
        >>> classifier = ErrorClassifier()
        >>> classifier.is_retryable(NetworkError("Timeout"))
        True
        >>> classifier.get_error_category(NetworkError("Timeout"))
        'network'
    """
    
    # Pattern matching for exception messages
    RETRYABLE_PATTERNS = [
        r'timeout',
        r'connection.*refused',
        r'connection.*reset',
        r'temporarily unavailable',
        r'rate limit',
        r'too many requests',
        r'503 service unavailable',
        r'502 bad gateway',
        r'504 gateway timeout',
        r'SQLITE_BUSY',
    ]
    
    PERMANENT_PATTERNS = [
        r'not found',
        r'404',
        r'invalid.*parameter',
        r'authentication failed',
        r'unauthorized',
        r'403 forbidden',
        r'quota exceeded',
        r'deleted',
        r'private video',
    ]
    
    def is_retryable(self, error: Exception) -> bool:
        """Determine if error is retryable.
        
        Args:
            error: Exception to classify
            
        Returns:
            True if error should be retried, False otherwise
        """
        # Check explicit error types
        if isinstance(error, RetryableError):
            return True
        if isinstance(error, PermanentError):
            return False
        
        # Check exception message patterns
        error_message = str(error).lower()
        
        # Check retryable patterns
        for pattern in self.RETRYABLE_PATTERNS:
            if re.search(pattern, error_message, re.IGNORECASE):
                return True
        
        # Check permanent patterns
        for pattern in self.PERMANENT_PATTERNS:
            if re.search(pattern, error_message, re.IGNORECASE):
                return False
        
        # Default: treat unknown errors as non-retryable
        # (conservative approach to avoid infinite retries)
        return False
    
    def get_error_category(self, error: Exception) -> str:
        """Get error category.
        
        Args:
            error: Exception to categorize
            
        Returns:
            Error category string
        """
        if isinstance(error, NetworkError):
            return 'network'
        elif isinstance(error, RateLimitError):
            return 'rate_limit'
        elif isinstance(error, TemporaryAPIError):
            return 'api_temporary'
        elif isinstance(error, DatabaseBusyError):
            return 'database_busy'
        elif isinstance(error, InvalidParametersError):
            return 'invalid_parameters'
        elif isinstance(error, ResourceNotFoundError):
            return 'not_found'
        elif isinstance(error, AuthenticationError):
            return 'authentication'
        elif isinstance(error, QuotaExhaustedError):
            return 'quota_exhausted'
        else:
            return 'unknown'
    
    def get_error_metadata(self, error: Exception) -> Dict[str, Any]:
        """Extract error metadata.
        
        Args:
            error: Exception to analyze
            
        Returns:
            Dictionary with error metadata
        """
        metadata = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'category': self.get_error_category(error),
            'retryable': self.is_retryable(error),
        }
        
        # Add retry_after if available
        if isinstance(error, RetryableError) and error.retry_after:
            metadata['retry_after'] = error.retry_after
        
        return metadata
```

### 3. Retry Strategy

**File**: `src/workers/retry_strategy.py`

```python
"""Retry strategies with exponential backoff.

This module provides retry strategy implementations for failed tasks.
"""

from typing import Protocol
import random


class RetryStrategyProtocol(Protocol):
    """Protocol for retry strategies."""
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Check if should retry.
        
        Args:
            error: The exception that occurred
            attempt: Current retry attempt number (1-indexed)
            
        Returns:
            True if should retry, False otherwise
        """
        ...
    
    def get_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay.
        
        Args:
            attempt: Current retry attempt number (1-indexed)
            
        Returns:
            Delay in seconds before next retry
        """
        ...


class ExponentialBackoffStrategy:
    """Exponential backoff retry strategy.
    
    Implements retry logic with exponential backoff:
    - Retry delay = base_delay * (2 ^ attempt)
    - Adds jitter to avoid thundering herd
    - Enforces max delay cap
    - Limits max retry attempts
    
    Attributes:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (default: 1.0)
        max_delay: Maximum delay cap in seconds (default: 300.0 = 5 min)
        jitter: Add random jitter to delay (default: True)
    
    Example:
        >>> strategy = ExponentialBackoffStrategy(max_retries=5)
        >>> strategy.should_retry(NetworkError("Timeout"), attempt=1)
        True
        >>> strategy.get_retry_delay(attempt=1)  # ~2 seconds
        2.1
        >>> strategy.get_retry_delay(attempt=5)  # ~32 seconds
        31.8
    """
    
    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 300.0,
        jitter: bool = True
    ):
        """Initialize exponential backoff strategy.
        
        Args:
            max_retries: Maximum retry attempts (default: 5)
            base_delay: Base delay in seconds (default: 1.0)
            max_delay: Maximum delay cap in seconds (default: 300.0)
            jitter: Add random jitter (default: True)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Check if should retry based on attempt count.
        
        Args:
            error: Exception that occurred (not used in this strategy)
            attempt: Current retry attempt number (1-indexed)
            
        Returns:
            True if attempt < max_retries, False otherwise
        """
        return attempt < self.max_retries
    
    def get_retry_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay.
        
        Formula: min(base_delay * (2 ^ attempt), max_delay) + jitter
        
        Args:
            attempt: Current retry attempt number (1-indexed)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff: 2^attempt
        delay = self.base_delay * (2 ** attempt)
        
        # Apply max delay cap
        delay = min(delay, self.max_delay)
        
        # Add jitter (±10% of delay)
        if self.jitter:
            jitter_amount = delay * 0.1
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0.0, delay)  # Ensure non-negative


class LinearBackoffStrategy:
    """Linear backoff retry strategy.
    
    Implements retry logic with linear backoff:
    - Retry delay = base_delay * attempt
    - Simpler than exponential, faster retries
    
    Attributes:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (default: 5.0)
    
    Example:
        >>> strategy = LinearBackoffStrategy(max_retries=3)
        >>> strategy.get_retry_delay(attempt=1)  # 5 seconds
        5.0
        >>> strategy.get_retry_delay(attempt=3)  # 15 seconds
        15.0
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 5.0):
        """Initialize linear backoff strategy.
        
        Args:
            max_retries: Maximum retry attempts (default: 3)
            base_delay: Base delay in seconds (default: 5.0)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Check if should retry."""
        return attempt < self.max_retries
    
    def get_retry_delay(self, attempt: int) -> float:
        """Calculate linear backoff delay."""
        return self.base_delay * attempt
```

### 4. Error Handler

**File**: `src/workers/error_handler.py`

```python
"""Error handler for managing task failures and retries.

This module coordinates error handling, retry logic, and dead letter
queue management.
"""

import logging
import traceback
from typing import Optional, Dict, Any
from datetime import datetime

from .error_classifier import ErrorClassifier
from .retry_strategy import ExponentialBackoffStrategy, RetryStrategyProtocol
from .errors import WorkerError


logger = logging.getLogger(__name__)


class ErrorHandler:
    """Handles errors, retries, and dead letter queue.
    
    Coordinates:
    1. Error classification (retryable vs permanent)
    2. Retry decision and delay calculation
    3. Error context preservation
    4. Task status updates
    5. Dead letter queue management
    
    Attributes:
        classifier: Error classifier instance
        retry_strategy: Retry strategy instance
        queue_db: Queue database connection
    
    Example:
        >>> handler = ErrorHandler(queue_db)
        >>> result = handler.handle_error(task, error, attempt=1)
        >>> if result['retry']:
        ...     time.sleep(result['delay'])
        ...     # Retry task
    """
    
    def __init__(
        self,
        queue_db,
        retry_strategy: Optional[RetryStrategyProtocol] = None
    ):
        """Initialize error handler.
        
        Args:
            queue_db: Queue database connection
            retry_strategy: Retry strategy (default: ExponentialBackoffStrategy)
        """
        self.queue_db = queue_db
        self.classifier = ErrorClassifier()
        self.retry_strategy = retry_strategy or ExponentialBackoffStrategy()
    
    def handle_error(
        self,
        task_id: int,
        error: Exception,
        attempt: int
    ) -> Dict[str, Any]:
        """Handle task error and determine retry action.
        
        Args:
            task_id: Task ID that failed
            error: Exception that occurred
            attempt: Current attempt number (1-indexed)
            
        Returns:
            Dictionary with:
                - retry: bool (should retry)
                - delay: float (retry delay in seconds, if retry=True)
                - category: str (error category)
                - metadata: dict (error metadata)
        """
        # Classify error
        is_retryable = self.classifier.is_retryable(error)
        category = self.classifier.get_error_category(error)
        metadata = self.classifier.get_error_metadata(error)
        
        # Determine if should retry
        should_retry = (
            is_retryable and
            self.retry_strategy.should_retry(error, attempt)
        )
        
        # Calculate retry delay
        retry_delay = 0.0
        if should_retry:
            retry_delay = self.retry_strategy.get_retry_delay(attempt)
        
        # Log error with context
        self._log_error(task_id, error, attempt, should_retry, category)
        
        # Update task status in database
        if should_retry:
            self._update_task_for_retry(task_id, attempt, retry_delay, metadata)
        else:
            self._mark_task_failed(task_id, metadata)
            if not is_retryable:
                self._move_to_dlq(task_id, error, metadata)
        
        return {
            'retry': should_retry,
            'delay': retry_delay,
            'category': category,
            'metadata': metadata,
        }
    
    def _log_error(
        self,
        task_id: int,
        error: Exception,
        attempt: int,
        should_retry: bool,
        category: str
    ) -> None:
        """Log error with full context.
        
        Args:
            task_id: Task ID
            error: Exception
            attempt: Attempt number
            should_retry: Whether will retry
            category: Error category
        """
        # Get full traceback
        tb = traceback.format_exc()
        
        log_message = (
            f"Task {task_id} failed (attempt {attempt}): "
            f"{type(error).__name__}: {error} "
            f"(category: {category}, retry: {should_retry})"
        )
        
        if should_retry:
            logger.warning(log_message)
            logger.debug(f"Traceback:\n{tb}")
        else:
            logger.error(log_message)
            logger.error(f"Traceback:\n{tb}")
    
    def _update_task_for_retry(
        self,
        task_id: int,
        attempt: int,
        retry_delay: float,
        metadata: Dict[str, Any]
    ) -> None:
        """Update task status for retry.
        
        Args:
            task_id: Task ID
            attempt: Next attempt number
            retry_delay: Retry delay in seconds
            metadata: Error metadata
        """
        cursor = self.queue_db.cursor()
        
        # Calculate next run time
        from datetime import datetime, timedelta
        next_run = datetime.utcnow() + timedelta(seconds=retry_delay)
        
        cursor.execute("""
            UPDATE task_queue
            SET status = 'QUEUED',
                retry_count = ?,
                last_error = ?,
                next_run_after = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (attempt, metadata.get('error_message'), next_run, task_id))
        
        self.queue_db.commit()
    
    def _mark_task_failed(
        self,
        task_id: int,
        metadata: Dict[str, Any]
    ) -> None:
        """Mark task as permanently failed.
        
        Args:
            task_id: Task ID
            metadata: Error metadata
        """
        cursor = self.queue_db.cursor()
        
        cursor.execute("""
            UPDATE task_queue
            SET status = 'FAILED',
                last_error = ?,
                failed_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (metadata.get('error_message'), task_id))
        
        self.queue_db.commit()
    
    def _move_to_dlq(
        self,
        task_id: int,
        error: Exception,
        metadata: Dict[str, Any]
    ) -> None:
        """Move permanently failed task to dead letter queue.
        
        Args:
            task_id: Task ID
            error: Exception
            metadata: Error metadata
        """
        cursor = self.queue_db.cursor()
        
        # Get task details
        cursor.execute("""
            SELECT task_type, parameters, created_at, retry_count
            FROM task_queue
            WHERE id = ?
        """, (task_id,))
        
        row = cursor.fetchone()
        if not row:
            logger.error(f"Task {task_id} not found for DLQ")
            return
        
        task_type, parameters, created_at, retry_count = row
        
        # Insert into dead letter queue (if table exists)
        try:
            cursor.execute("""
                INSERT INTO dead_letter_queue (
                    original_task_id,
                    task_type,
                    parameters,
                    error_type,
                    error_message,
                    error_category,
                    retry_count,
                    created_at,
                    moved_to_dlq_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                task_id,
                task_type,
                parameters,
                type(error).__name__,
                str(error),
                metadata.get('category'),
                retry_count,
                created_at
            ))
            
            self.queue_db.commit()
            logger.info(f"Task {task_id} moved to dead letter queue")
        
        except Exception as e:
            logger.error(f"Failed to move task {task_id} to DLQ: {e}")
```

### 5. Integration with BaseWorker

**File**: `src/workers/base_worker.py` (modifications)

```python
# Add error handling to BaseWorker

from .error_handler import ErrorHandler
from .errors import RetryableError, PermanentError

class BaseWorker(ABC):
    def __init__(self, worker_id, queue_db, config, results_db, metrics):
        self.worker_id = worker_id
        self.queue_db = queue_db
        self.config = config
        self.results_db = results_db
        self.metrics = metrics
        self.error_handler = ErrorHandler(queue_db)
        # ... rest of init ...
    
    def run(self):
        """Main worker loop with error handling."""
        while self.running:
            task = self.claim_task()
            
            if task is None:
                time.sleep(self.poll_interval)
                continue
            
            # Process with error handling
            try:
                result = self.process_task(task)
                self.report_result(task, result)
            
            except Exception as error:
                # Handle error
                error_result = self.error_handler.handle_error(
                    task_id=task.id,
                    error=error,
                    attempt=task.retry_count + 1
                )
                
                if error_result['retry']:
                    logger.info(
                        f"Task {task.id} will be retried after "
                        f"{error_result['delay']:.1f}s"
                    )
                else:
                    logger.error(
                        f"Task {task.id} permanently failed: "
                        f"{error_result['category']}"
                    )
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] Error taxonomy defined (RetryableError, PermanentError, specific errors)
- [ ] ErrorClassifier implemented with pattern matching
- [ ] ExponentialBackoffStrategy implemented
- [ ] LinearBackoffStrategy implemented (alternative)
- [ ] ErrorHandler coordinates classification, retry, DLQ
- [ ] BaseWorker integrated with error handling
- [ ] Dead letter queue population working
- [ ] Error context preserved (traceback, metadata)

### Non-Functional Requirements
- [ ] All SOLID principles verified
- [ ] Thread-safe error handling
- [ ] No performance degradation on happy path
- [ ] Logging provides debugging context

### Code Quality
- [ ] Type hints on all methods
- [ ] Docstrings (Google style)
- [ ] mypy type checking passes
- [ ] pylint score >8.5/10

### Testing Requirements
- [ ] Unit tests for all error classes
- [ ] Unit tests for ErrorClassifier
- [ ] Unit tests for retry strategies
- [ ] Unit tests for ErrorHandler
- [ ] Integration tests with BaseWorker
- [ ] Test exponential backoff calculation
- [ ] Test max retries enforcement
- [ ] Test DLQ population
- [ ] Test coverage >80%

---

## Testing Strategy

### Unit Tests

**File**: `_meta/tests/test_errors.py`

```python
def test_retryable_error():
    """Test RetryableError creation."""
    error = NetworkError("Connection timeout", retry_after=30.0)
    assert isinstance(error, RetryableError)
    assert error.retry_after == 30.0


def test_permanent_error():
    """Test PermanentError creation."""
    error = InvalidParametersError("Missing channel_url")
    assert isinstance(error, PermanentError)
```

**File**: `_meta/tests/test_error_classifier.py`

```python
def test_classify_retryable_error():
    """Test classification of retryable errors."""
    classifier = ErrorClassifier()
    
    error = NetworkError("Timeout")
    assert classifier.is_retryable(error) is True
    assert classifier.get_error_category(error) == 'network'


def test_classify_permanent_error():
    """Test classification of permanent errors."""
    classifier = ErrorClassifier()
    
    error = ResourceNotFoundError("Video not found")
    assert classifier.is_retryable(error) is False
    assert classifier.get_error_category(error) == 'not_found'


def test_pattern_matching():
    """Test error message pattern matching."""
    classifier = ErrorClassifier()
    
    # Retryable pattern
    error = Exception("Connection timeout occurred")
    assert classifier.is_retryable(error) is True
    
    # Permanent pattern
    error = Exception("404 not found")
    assert classifier.is_retryable(error) is False
```

**File**: `_meta/tests/test_retry_strategy.py`

```python
def test_exponential_backoff():
    """Test exponential backoff calculation."""
    strategy = ExponentialBackoffStrategy(
        max_retries=5,
        base_delay=1.0,
        jitter=False  # Disable jitter for deterministic test
    )
    
    # Test delay calculation
    assert strategy.get_retry_delay(1) == 2.0   # 2^1
    assert strategy.get_retry_delay(2) == 4.0   # 2^2
    assert strategy.get_retry_delay(3) == 8.0   # 2^3
    assert strategy.get_retry_delay(5) == 32.0  # 2^5


def test_max_retries():
    """Test max retries enforcement."""
    strategy = ExponentialBackoffStrategy(max_retries=3)
    
    assert strategy.should_retry(NetworkError("test"), 1) is True
    assert strategy.should_retry(NetworkError("test"), 2) is True
    assert strategy.should_retry(NetworkError("test"), 3) is False


def test_max_delay_cap():
    """Test max delay cap is enforced."""
    strategy = ExponentialBackoffStrategy(
        base_delay=1.0,
        max_delay=10.0,
        jitter=False
    )
    
    # 2^10 = 1024, but should be capped at 10
    delay = strategy.get_retry_delay(10)
    assert delay == 10.0
```

### Integration Tests

**File**: `_meta/tests/test_error_handler_integration.py`

```python
def test_error_handler_workflow():
    """Test complete error handling workflow."""
    # Setup
    queue_db = create_test_database()
    handler = ErrorHandler(queue_db)
    
    # Create test task
    task_id = create_test_task(queue_db)
    
    # Simulate error
    error = NetworkError("Connection timeout")
    
    # Handle error (first attempt)
    result = handler.handle_error(task_id, error, attempt=1)
    
    assert result['retry'] is True
    assert result['delay'] > 0
    assert result['category'] == 'network'
    
    # Verify task status updated
    task = get_task(queue_db, task_id)
    assert task['status'] == 'QUEUED'
    assert task['retry_count'] == 1
```

---

## Performance Targets

- [ ] Error classification: <1ms per error
- [ ] Retry delay calculation: <0.1ms
- [ ] Error context logging: <10ms
- [ ] No performance impact on successful tasks

---

## Dependencies

### Issue Dependencies
- **#002** (Worker Base Class): Integrate error handling
- **#005** (Plugin Architecture): Plugins throw appropriate errors

### External Dependencies
- Python standard library only (no new dependencies)

---

## Windows-Specific Considerations

- Exception handling works identically on Windows
- File paths in error messages use `pathlib`
- Traceback formatting cross-platform

---

## Risks & Mitigation

### Risk: Infinite Retry Loops
**Mitigation**: Enforce max_retries, default conservative classification

### Risk: Lost Error Context
**Mitigation**: Full traceback logging, error metadata preservation

### Risk: DLQ Grows Unbounded
**Mitigation**: Document DLQ cleanup strategy (not in this issue)

---

## Future Extensibility

This system enables:
- Custom retry strategies
- Error alerting and notifications
- Error analytics and reporting
- Automatic error recovery
- Circuit breaker patterns

---

## References

### Internal
- Issue #002: Worker Base Class
- Issue #005: Plugin Architecture
- Master Plan: #001

### External
- Exponential Backoff: https://en.wikipedia.org/wiki/Exponential_backoff
- Error Handling Best Practices: Python docs

---

**Status**: 📋 Ready for Assignment  
**Created**: 2025-11-11  
**Assigned To**: Worker02 - Python Specialist  
**Estimated Start**: After #002, #005 complete  
**Estimated Duration**: 2 days
