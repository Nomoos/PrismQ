"""Task claiming strategies for worker queue.

Implements Strategy pattern for different task claiming behaviors.
Follows Open/Closed Principle - easily extensible for new strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict


class ClaimingStrategy(ABC):
    """Abstract base for task claiming strategies.
    
    Following Open/Closed Principle - open for extension, closed for modification.
    """
    
    @abstractmethod
    def get_order_by_clause(self) -> str:
        """Get SQL ORDER BY clause for this strategy.
        
        Returns:
            SQL ORDER BY clause (without 'ORDER BY' keyword)
        """
        pass


class FIFOStrategy(ClaimingStrategy):
    """First-In-First-Out: Process oldest tasks first."""
    
    def get_order_by_clause(self) -> str:
        return "created_at ASC, priority DESC"


class LIFOStrategy(ClaimingStrategy):
    """Last-In-First-Out: Process newest tasks first."""
    
    def get_order_by_clause(self) -> str:
        return "created_at DESC, priority DESC"


class PriorityStrategy(ClaimingStrategy):
    """Priority-based: Process highest priority tasks first."""
    
    def get_order_by_clause(self) -> str:
        return "priority DESC, created_at ASC"


# Strategy registry
_STRATEGIES: Dict[str, ClaimingStrategy] = {
    "FIFO": FIFOStrategy(),
    "LIFO": LIFOStrategy(),
    "PRIORITY": PriorityStrategy(),
}


def get_strategy(name: str) -> ClaimingStrategy:
    """Get claiming strategy by name.
    
    Args:
        name: Strategy name (FIFO, LIFO, PRIORITY)
        
    Returns:
        ClaimingStrategy instance
        
    Raises:
        ValueError: If strategy not found
    """
    strategy = _STRATEGIES.get(name.upper())
    if not strategy:
        raise ValueError(
            f"Unknown strategy '{name}'. "
            f"Available: {', '.join(_STRATEGIES.keys())}"
        )
    return strategy


__all__ = ["ClaimingStrategy", "get_strategy"]
