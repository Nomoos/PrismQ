"""Variant Router - Assign users to variants using hash-based distribution."""

import hashlib
from typing import List, Optional, Any, TYPE_CHECKING

# Handle both relative and absolute imports
try:
    from .test_manager import TitleVariant
except ImportError:
    from test_manager import TitleVariant


def assign_variant(user_id: str, variants: List[Any]) -> Any:
    """Assign user to a variant based on hash-based distribution.
    
    Uses MD5 hash of user_id to ensure:
    1. Consistent assignment - same user always gets same variant
    2. Even distribution - variants receive traffic matching their percentages
    
    Note: MD5 is used here for non-cryptographic purposes (traffic distribution).
    The hash is used only to generate a deterministic number from user_id, not
    for security. MD5's speed and consistent output are suitable for this use case.
    
    Algorithm:
    1. Hash user_id to get deterministic number
    2. Convert to 0-100 range using modulo
    3. Map to variant based on cumulative traffic percentages
    
    Args:
        user_id: Unique user identifier (can be session ID, IP hash, etc.)
        variants: List of variants with traffic_percent defined
        
    Returns:
        Assigned TitleVariant
        
    Raises:
        ValueError: If variants list is empty or traffic doesn't sum to 100
        
    Example:
        >>> variants = [
        ...     TitleVariant("A", "Title A", 50),
        ...     TitleVariant("B", "Title B", 50)
        ... ]
        >>> variant = assign_variant("user123", variants)
        >>> print(variant.variant_id)  # Always returns same variant for "user123"
    """
    if not variants:
        raise ValueError("variants list cannot be empty")
    
    # Validate traffic distribution
    total_traffic = sum(v.traffic_percent for v in variants)
    if abs(total_traffic - 100.0) > 0.1:
        raise ValueError(f"Traffic percentages must sum to 100, got {total_traffic}")
    
    # Hash user_id to get consistent value
    hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
    
    # Convert to 0-100 range
    threshold = hash_val % 100
    
    # Map to variant based on cumulative percentages
    cumulative = 0.0
    for variant in variants:
        cumulative += variant.traffic_percent
        if threshold < cumulative:
            return variant
    
    # Fallback to first variant (should not reach here if traffic sums to 100)
    return variants[0]


class VariantRouter:
    """Manages variant assignment and tracking for A/B tests."""
    
    def __init__(self):
        """Initialize the variant router."""
        self._assignments = {}  # Track user->variant assignments for verification
    
    def assign(self, user_id: str, variants: List[Any]) -> Any:
        """Assign user to variant and track the assignment.
        
        Args:
            user_id: Unique user identifier
            variants: List of variants to choose from
            
        Returns:
            Assigned TitleVariant
        """
        variant = assign_variant(user_id, variants)
        
        # Store assignment for tracking/debugging
        self._assignments[user_id] = variant.variant_id
        
        return variant
    
    def get_assignment(self, user_id: str) -> Optional[str]:
        """Get previously assigned variant for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Variant ID or None if user hasn't been assigned yet
        """
        return self._assignments.get(user_id)
    
    def verify_consistency(
        self,
        user_id: str,
        variants: List[Any]
    ) -> bool:
        """Verify that user assignment is consistent with previous assignment.
        
        Args:
            user_id: User identifier
            variants: Current variant list
            
        Returns:
            True if assignment matches previous, False otherwise
        """
        previous = self._assignments.get(user_id)
        if previous is None:
            return True  # No previous assignment to compare
        
        current_variant = assign_variant(user_id, variants)
        return current_variant.variant_id == previous
    
    def get_distribution_stats(self, variants: List[Any]) -> dict:
        """Calculate actual traffic distribution from assignments.
        
        Useful for verifying that hash-based distribution matches
        expected traffic percentages.
        
        Args:
            variants: List of variants
            
        Returns:
            Dictionary mapping variant_id to percentage of assignments
        """
        if not self._assignments:
            return {v.variant_id: 0.0 for v in variants}
        
        # Count assignments per variant
        counts = {v.variant_id: 0 for v in variants}
        for variant_id in self._assignments.values():
            if variant_id in counts:
                counts[variant_id] += 1
        
        # Convert to percentages
        total = len(self._assignments)
        return {
            variant_id: (count / total) * 100
            for variant_id, count in counts.items()
        }
    
    def clear_assignments(self):
        """Clear all assignment tracking data."""
        self._assignments.clear()
