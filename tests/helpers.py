"""Test helpers for PrismQ iterative workflow and version tracking.

This module provides utilities for testing the 26-stage iterative co-improvement 
workflow, particularly focusing on version tracking, iteration validation, and 
cross-module integration testing.

Key Features:
- Version tracking assertions
- Iteration path validation
- Mock data generation for workflow stages
- Integration test helpers

Note: Idea model imports are optional and gracefully handled if unavailable.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# Optional imports - Idea model may not be available in all test contexts
try:
    import sys
    _current_dir = Path(__file__).parent.parent
    _idea_model_path = _current_dir / "T" / "Idea" / "Model"
    if str(_idea_model_path) not in sys.path:
        sys.path.insert(0, str(_idea_model_path))
    
    from src.idea import Idea, IdeaStatus, ContentGenre
    IDEA_MODEL_AVAILABLE = True
except ImportError:
    # Fallback when Idea model not available
    Idea = None
    IdeaStatus = None
    ContentGenre = None
    IDEA_MODEL_AVAILABLE = False


@dataclass
class VersionTracker:
    """Helper class for tracking versions through iterative workflow.
    
    Tracks versions of content (Idea, Title, Script) through the co-improvement
    cycle, validating that versions increment correctly and maintaining
    the relationship between different versions.
    
    Attributes:
        entity_type: Type of entity being tracked (e.g., 'Idea', 'Title', 'Script')
        versions: List of version numbers tracked
        history: History of changes made in each version
    """
    
    entity_type: str
    versions: List[int] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_version(self, version_num: int, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a new version to tracking.
        
        Args:
            version_num: Version number to add
            metadata: Optional metadata about this version
            
        Raises:
            ValueError: If version number is not sequential
        """
        if self.versions:
            expected = self.versions[-1] + 1
            if version_num != expected:
                raise ValueError(
                    f"Expected version {expected} but got {version_num}. "
                    f"Versions must be sequential."
                )
        elif version_num != 1:
            raise ValueError(f"First version must be 1, got {version_num}")
        
        self.versions.append(version_num)
        self.history.append({
            'version': version_num,
            'metadata': metadata or {},
        })
    
    def get_current_version(self) -> Optional[int]:
        """Get the current (latest) version number.
        
        Returns:
            Current version number or None if no versions tracked
        """
        return self.versions[-1] if self.versions else None
    
    def get_version_count(self) -> int:
        """Get the total number of versions tracked.
        
        Returns:
            Number of versions
        """
        return len(self.versions)
    
    def validate_sequence(self) -> bool:
        """Validate that version sequence is correct (1, 2, 3, ...).
        
        Returns:
            True if sequence is valid, False otherwise
        """
        if not self.versions:
            return True
        
        expected = list(range(1, len(self.versions) + 1))
        return self.versions == expected
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get complete version history.
        
        Returns:
            List of version history entries
        """
        return self.history.copy()


class WorkflowStageValidator:
    """Validator for workflow stage transitions.
    
    Validates that content moves through the correct stages of the workflow
    and that version increments happen at appropriate points.
    """
    
    # Define valid stage transitions for the workflow
    VALID_TRANSITIONS = {
        'idea_creation': ['title_v1'],
        'title_v1': ['script_v1', 'title_v2'],
        'script_v1': ['title_review', 'script_v2', 'script_review'],
        'title_review': ['title_v2'],
        'script_review': ['script_v2'],
        'title_v2': ['script_v2', 'script_review', 'title_v3'],
        'script_v2': ['title_v2', 'title_review', 'script_v3', 'title_v3'],
        'title_v3': ['script_v3', 'script_review', 'refinement'],
        'script_v3': ['title_v3', 'title_review', 'refinement'],
    }
    
    def __init__(self):
        """Initialize the validator."""
        self.current_stage: Optional[str] = None
        self.stage_history: List[str] = []
    
    def transition_to(self, stage: str) -> bool:
        """Attempt to transition to a new stage.
        
        Args:
            stage: Target stage to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """
        if self.current_stage is None:
            # First stage must be idea_creation
            if stage == 'idea_creation':
                self.current_stage = stage
                self.stage_history.append(stage)
                return True
            return False
        
        valid_next = self.VALID_TRANSITIONS.get(self.current_stage, [])
        if stage in valid_next:
            self.current_stage = stage
            self.stage_history.append(stage)
            return True
        
        return False
    
    def get_stage_history(self) -> List[str]:
        """Get the history of stage transitions.
        
        Returns:
            List of stages in order of transition
        """
        return self.stage_history.copy()
    
    def is_valid_path(self) -> bool:
        """Check if the current path through stages is valid.
        
        Returns:
            True if all transitions have been valid
        """
        if not self.stage_history:
            return True
        
        for i in range(len(self.stage_history) - 1):
            current = self.stage_history[i]
            next_stage = self.stage_history[i + 1]
            valid_next = self.VALID_TRANSITIONS.get(current, [])
            if next_stage not in valid_next:
                return False
        
        return True


def create_test_idea(
    title: str = "Test Idea",
    concept: str = "Test concept for workflow",
    version: int = 1,
    status: Optional[Any] = None,
    **kwargs
) -> Optional[Any]:
    """Create a test Idea instance for testing.
    
    Args:
        title: Title of the idea
        concept: Concept description
        version: Version number
        status: IdeaStatus value (if None, uses DRAFT)
        **kwargs: Additional fields to set on the Idea
        
    Returns:
        Idea instance or None if Idea model not available
        
    Raises:
        RuntimeError: If Idea model is not available
    """
    if not IDEA_MODEL_AVAILABLE:
        raise RuntimeError(
            "Idea model not available. Ensure T/Idea/Model is accessible "
            "or skip tests that require Idea instances."
        )
    
    status = status or IdeaStatus.DRAFT
    
    return Idea(
        id="test-id",
        title=title,
        concept=concept,
        version=version,
        status=status,
        **kwargs
    )


def assert_version_increment(old_version: int, new_version: int) -> None:
    """Assert that version has incremented correctly.
    
    Args:
        old_version: Previous version number
        new_version: New version number
        
    Raises:
        AssertionError: If version did not increment by exactly 1
    """
    assert new_version == old_version + 1, (
        f"Version should increment by 1. Expected {old_version + 1}, got {new_version}"
    )


def assert_version_sequence(versions: List[int]) -> None:
    """Assert that a list of versions forms a valid sequence.
    
    Args:
        versions: List of version numbers
        
    Raises:
        AssertionError: If sequence is not valid (1, 2, 3, ...)
    """
    if not versions:
        return
    
    assert versions[0] == 1, f"First version should be 1, got {versions[0]}"
    
    for i in range(1, len(versions)):
        expected = versions[i - 1] + 1
        actual = versions[i]
        assert actual == expected, (
            f"Version sequence broken at index {i}. "
            f"Expected {expected}, got {actual}"
        )


def create_version_history(
    entity_type: str,
    num_versions: int = 3,
    metadata_fn: Optional[callable] = None
) -> VersionTracker:
    """Create a VersionTracker with a history of versions.
    
    Args:
        entity_type: Type of entity being tracked
        num_versions: Number of versions to create
        metadata_fn: Optional function to generate metadata for each version.
                     Should take version number and return dict.
        
    Returns:
        VersionTracker with populated history
    """
    tracker = VersionTracker(entity_type=entity_type)
    
    for v in range(1, num_versions + 1):
        metadata = metadata_fn(v) if metadata_fn else None
        tracker.add_version(v, metadata)
    
    return tracker


class IntegrationTestHelper:
    """Helper class for integration testing across modules.
    
    Provides utilities for testing the interaction between different modules
    in the workflow, such as Idea → Title → Script → Review cycles.
    """
    
    def __init__(self):
        """Initialize the integration test helper."""
        self.idea_tracker: Optional[VersionTracker] = None
        self.title_tracker: Optional[VersionTracker] = None
        self.script_tracker: Optional[VersionTracker] = None
        self.stage_validator = WorkflowStageValidator()
    
    def start_workflow(self, entity_type: str = "Idea") -> VersionTracker:
        """Start a new workflow and return a tracker for the entity.
        
        Args:
            entity_type: Type of entity to track
            
        Returns:
            VersionTracker for the entity
        """
        tracker = VersionTracker(entity_type=entity_type)
        
        if entity_type == "Idea":
            self.idea_tracker = tracker
        elif entity_type == "Title":
            self.title_tracker = tracker
        elif entity_type == "Script":
            self.script_tracker = tracker
        
        return tracker
    
    def validate_cross_version_alignment(
        self,
        idea_version: int,
        title_version: int,
        script_version: int
    ) -> bool:
        """Validate that versions are properly aligned across modules.
        
        In the co-improvement workflow, versions should generally be in sync
        or within reasonable range. Idea version often stays at v1 while
        Title and Script iterate, so we check alignment of Title/Script separately.
        
        Args:
            idea_version: Current Idea version
            title_version: Current Title version
            script_version: Current Script version
            
        Returns:
            True if versions are properly aligned
        """
        # Title and Script should be within 1 version of each other
        title_script_aligned = abs(title_version - script_version) <= 1
        
        # Idea can be at v1 while others iterate, or should be close to others
        idea_aligned = (idea_version == 1) or (abs(idea_version - max(title_version, script_version)) <= 1)
        
        return title_script_aligned and idea_aligned
    
    def get_all_trackers(self) -> Dict[str, Optional[VersionTracker]]:
        """Get all active trackers.
        
        Returns:
            Dictionary mapping entity types to their trackers
        """
        return {
            'Idea': self.idea_tracker,
            'Title': self.title_tracker,
            'Script': self.script_tracker,
        }


# Export main classes and functions
__all__ = [
    'VersionTracker',
    'WorkflowStageValidator',
    'IntegrationTestHelper',
    'create_test_idea',
    'assert_version_increment',
    'assert_version_sequence',
    'create_version_history',
]
