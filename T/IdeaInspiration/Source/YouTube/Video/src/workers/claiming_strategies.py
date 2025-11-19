"""Claiming strategies for task queue.

This module implements different strategies for claiming tasks from the queue,
following the Strategy Pattern and SOLID principles.

Following Interface Segregation Principle (ISP) - minimal, focused interface.
Following Open/Closed Principle (OCP) - easily extensible with new strategies.
"""

from typing import Protocol
from abc import ABC, abstractmethod


class ClaimingStrategy(Protocol):
    """Protocol for task claiming strategies.
    
    Following Interface Segregation Principle - minimal interface.
    Only the essential method needed for strategy selection.
    """
    
    def get_order_by_clause(self) -> str:
        """Get SQL ORDER BY clause for this strategy.
        
        Returns:
            SQL ORDER BY clause (without 'ORDER BY' keyword)
        """
        ...


class BaseClaimStrategy(ABC):
    """Base class for claiming strategies with common functionality.
    
    Following Single Responsibility Principle (SRP):
    - Each strategy defines its own ordering logic
    - Base class provides common interface and utilities
    """
    
    @abstractmethod
    def get_order_by_clause(self) -> str:
        """Get SQL ORDER BY clause - must be implemented by subclass.
        
        Returns:
            SQL ORDER BY clause string (without 'ORDER BY' keyword)
        """
        pass
    
    def __str__(self) -> str:
        """String representation of the strategy."""
        return self.__class__.__name__
    
    def __repr__(self) -> str:
        """Developer representation of the strategy."""
        return f"<{self.__class__.__name__}>"


class FIFOStrategy(BaseClaimStrategy):
    """First-In-First-Out: Oldest tasks first.
    
    Use case: 
    - Background jobs
    - Batch processing
    - Fair task distribution
    
    Characteristics:
    - Fairness: High (no starvation)
    - Predictability: High (deterministic order)
    - Latency: Variable (depends on queue depth)
    """
    
    def get_order_by_clause(self) -> str:
        """Order by creation time ascending, then priority descending.
        
        Returns oldest tasks first, with priority as tiebreaker.
        """
        return "created_at ASC, priority DESC"


class LIFOStrategy(BaseClaimStrategy):
    """Last-In-First-Out: Newest tasks first.
    
    Use case:
    - User-initiated actions
    - Interactive work
    - Real-time responsiveness
    
    Characteristics:
    - Fairness: Low (old tasks may starve)
    - Predictability: Medium (recent tasks processed fast)
    - Latency: Low for new tasks, high for old tasks
    """
    
    def get_order_by_clause(self) -> str:
        """Order by creation time descending, then priority descending.
        
        Returns newest tasks first, with priority as tiebreaker.
        """
        return "created_at DESC, priority DESC"


class PriorityStrategy(BaseClaimStrategy):
    """Priority-based: Highest priority first, then FIFO.
    
    Use case:
    - Time-sensitive tasks
    - SLA requirements
    - Critical path optimization
    
    Characteristics:
    - Fairness: None (low priority may starve)
    - Predictability: High (priority-based)
    - Latency: Low for high priority, potentially infinite for low priority
    """
    
    def get_order_by_clause(self) -> str:
        """Order by priority descending, then creation time ascending.
        
        Returns highest priority tasks first, with FIFO as tiebreaker.
        """
        return "priority DESC, created_at ASC"


class WeightedRandomStrategy(BaseClaimStrategy):
    """Weighted random selection based on priority.
    
    Use case:
    - Load balancing across priority levels
    - Preventing priority starvation
    - Introducing controlled randomness
    
    Characteristics:
    - Fairness: Medium (probabilistic fairness)
    - Predictability: Low (random but weighted)
    - Latency: Variable but bounded
    
    Algorithm:
    - Higher priority tasks have higher probability of selection
    - Random factor prevents complete starvation
    - Still respects priority weights
    """
    
    def get_order_by_clause(self) -> str:
        """Order by weighted random with priority influence.
        
        Uses SQLite's RANDOM() function with priority weighting.
        Higher priority = more likely to be selected, but not guaranteed.
        
        Formula: priority * (1.0 + 0.1 * (10 - RANDOM() % 10))
        - Base weight from priority (1-10)
        - Random multiplier adds 0-90% variation
        - Higher priorities still dominate statistically
        """
        return "priority * (1.0 + 0.1 * (10 - ABS(RANDOM()) % 10)) DESC"


# Strategy registry for easy lookup
STRATEGIES = {
    'FIFO': FIFOStrategy(),
    'LIFO': LIFOStrategy(),
    'PRIORITY': PriorityStrategy(),
    'WEIGHTED_RANDOM': WeightedRandomStrategy(),
}


def get_strategy(name: str) -> BaseClaimStrategy:
    """Get a claiming strategy by name.
    
    Args:
        name: Strategy name (FIFO, LIFO, PRIORITY, WEIGHTED_RANDOM)
        
    Returns:
        Strategy instance
        
    Raises:
        ValueError: If strategy name is unknown
        
    Example:
        >>> strategy = get_strategy('FIFO')
        >>> print(strategy.get_order_by_clause())
        created_at ASC, priority DESC
    """
    name_upper = name.upper()
    if name_upper not in STRATEGIES:
        raise ValueError(
            f"Unknown strategy: {name}. "
            f"Valid strategies: {', '.join(STRATEGIES.keys())}"
        )
    return STRATEGIES[name_upper]


def get_available_strategies() -> list[str]:
    """Get list of available strategy names.
    
    Returns:
        List of strategy names in uppercase
        
    Example:
        >>> strategies = get_available_strategies()
        >>> print(strategies)
        ['FIFO', 'LIFO', 'PRIORITY', 'WEIGHTED_RANDOM']
    """
    return list(STRATEGIES.keys())


__all__ = [
    'ClaimingStrategy',
    'BaseClaimStrategy',
    'FIFOStrategy',
    'LIFOStrategy',
    'PriorityStrategy',
    'WeightedRandomStrategy',
    'get_strategy',
    'get_available_strategies',
    'STRATEGIES',
]
