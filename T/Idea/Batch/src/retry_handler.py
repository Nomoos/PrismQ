"""Retry handler with exponential backoff for batch processing.

This module provides retry logic for handling transient failures during
batch idea processing. It implements exponential backoff with configurable
retry attempts and delay factors.
"""

import asyncio
import logging
from typing import Callable, Any, Optional, TypeVar, Awaitable
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry logic.
    
    Attributes:
        max_attempts: Maximum number of retry attempts (default: 3)
        backoff_factor: Multiplier for exponential backoff (default: 2.0)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
    """
    max_attempts: int = 3
    backoff_factor: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0


class RetryHandler:
    """Handler for retry logic with exponential backoff."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize retry handler.
        
        Args:
            config: Optional retry configuration
        """
        self.config = config or RetryConfig()
    
    async def execute_with_retry(
        self,
        func: Callable[..., Awaitable[T]],
        *args,
        **kwargs
    ) -> tuple[T, int, Optional[str]]:
        """Execute an async function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Tuple of (result, attempts_used, error_message)
            On success: (result, attempts, None)
            On failure: (None, attempts, error_message)
        """
        last_error = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                logger.debug(f"Attempt {attempt}/{self.config.max_attempts}")
                result = await func(*args, **kwargs)
                
                if attempt > 1:
                    logger.info(f"Success on attempt {attempt}")
                
                return result, attempt, None
                
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Attempt {attempt}/{self.config.max_attempts} failed: {e}"
                )
                
                if attempt < self.config.max_attempts:
                    delay = self._calculate_delay(attempt)
                    logger.debug(f"Waiting {delay:.2f}s before retry")
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"All {self.config.max_attempts} attempts failed: {last_error}"
                    )
        
        return None, self.config.max_attempts, last_error
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for next retry using exponential backoff.
        
        Args:
            attempt: Current attempt number (1-indexed)
            
        Returns:
            Delay in seconds
        """
        delay = self.config.initial_delay * (self.config.backoff_factor ** (attempt - 1))
        return min(delay, self.config.max_delay)


async def retry_on_exception(
    func: Callable[..., Awaitable[T]],
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    *args,
    **kwargs
) -> T:
    """Convenience function to retry an async function.
    
    Args:
        func: Async function to execute
        max_attempts: Maximum retry attempts
        backoff_factor: Exponential backoff multiplier
        *args: Function positional arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
        
    Raises:
        Exception: Last exception if all retries fail
    """
    config = RetryConfig(max_attempts=max_attempts, backoff_factor=backoff_factor)
    handler = RetryHandler(config)
    result, attempts, error = await handler.execute_with_retry(func, *args, **kwargs)
    
    if error:
        raise Exception(f"Failed after {attempts} attempts: {error}")
    
    return result


__all__ = ["RetryHandler", "RetryConfig", "retry_on_exception"]
