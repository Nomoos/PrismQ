"""Task claiming strategies for Scoring Worker.

Implements Strategy pattern (Open/Closed Principle) for flexible task claiming behavior.
Each strategy defines how tasks are ordered when claiming from the queue.
"""

from abc import ABC, abstractmethod
from typing import Dict


class ClaimingStrategy(ABC):
    """Abstract base class for task claiming strategies."""
    
    @abstractmethod
    def get_order_by_clause(self) -> str:
        """Return SQL ORDER BY clause for task selection.
        
        Returns:
            SQL ORDER BY clause (without 'ORDER BY' keyword)
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return strategy name.
        
        Returns:
            Human-readable strategy name
        """
        pass


class FIFOStrategy(ClaimingStrategy):
    """First In, First Out - Process oldest tasks first.
    
    Ensures tasks are processed in the order they were created.
    Good for maintaining fairness and predictable processing order.
    """
    
    def get_order_by_clause(self) -> str:
        """Order by creation time (oldest first), then priority."""
        return "created_at ASC, priority DESC"
    
    def get_name(self) -> str:
        return "FIFO"


class LIFOStrategy(ClaimingStrategy):
    """Last In, First Out - Process newest tasks first.
    
    Processes most recent tasks first, which can be useful when newer
    tasks represent more current/relevant data or higher user priority.
    """
    
    def get_order_by_clause(self) -> str:
        """Order by creation time (newest first), then priority."""
        return "created_at DESC, priority DESC"
    
    def get_name(self) -> str:
        return "LIFO"


class PriorityStrategy(ClaimingStrategy):
    """Priority-based - Process high-priority tasks first.
    
    Ensures important tasks are processed before lower-priority ones.
    Within same priority, uses FIFO ordering.
    """
    
    def get_order_by_clause(self) -> str:
        """Order by priority (highest first), then creation time."""
        return "priority DESC, created_at ASC"
    
    def get_name(self) -> str:
        return "PRIORITY"


# Strategy registry
_STRATEGIES: Dict[str, ClaimingStrategy] = {
    "FIFO": FIFOStrategy(),
    "LIFO": LIFOStrategy(),
    "PRIORITY": PriorityStrategy(),
}


def get_strategy(name: str) -> ClaimingStrategy:
    """Get claiming strategy by name.
    
    Args:
        name: Strategy name (case-insensitive)
        
    Returns:
        ClaimingStrategy instance
        
    Raises:
        ValueError: If strategy not found
    """
    strategy = _STRATEGIES.get(name.upper())
    if strategy is None:
        available = ", ".join(_STRATEGIES.keys())
        raise ValueError(
            f"Unknown claiming strategy: {name}. "
            f"Available strategies: {available}"
        )
    return strategy


def list_strategies() -> list[str]:
    """List all available strategy names.
    
    Returns:
        List of strategy names
    """
    return list(_STRATEGIES.keys())


__all__ = [
    "ClaimingStrategy",
    "FIFOStrategy",
    "LIFOStrategy",
    "PriorityStrategy",
    "get_strategy",
    "list_strategies",
]
