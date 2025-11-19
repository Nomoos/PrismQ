"""Story model for PrismQ story production workflow.

This module defines the Story model that serves as the central coordinator
for the story production state machine. A Story represents the complete
production lifecycle from Idea through Script to publication.

Key Concepts:
- Story is the state machine coordinator
- Each Story is linked to exactly ONE Idea
- Story tracks production state (Idea → Script → Publication)
- State determines which components are active (Idea, Script, etc.)
- Supports Reddit-style story production workflow

Workflow Position:
    IdeaInspiration → Idea → Story (manages) → Script → Publishing → Published
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class StoryStatus(Enum):
    """Status values for Story production.
    
    These are simplified status values distinct from StoryState.
    Status indicates current production phase.
    """
    
    # Development statuses
    DRAFT = "draft"
    IN_DEVELOPMENT = "in_development"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    
    # Production statuses
    IN_PRODUCTION = "in_production"
    PUBLISHED = "published"
    
    # Terminal statuses
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


class StoryState(Enum):
    """State machine states for story production workflow.
    
    This enum defines the complete state machine for producing stories,
    particularly optimized for Reddit-style story production where:
    - One Idea generates one Story
    - Story progresses through clear stages
    - Each state has specific outputs
    
    State Machine Flow for Reddit Stories:
        IDEA_OUTLINE → IDEA_SKELETON → IDEA_TITLE →
        SCRIPT_DRAFT → SCRIPT_REVIEW → SCRIPT_APPROVED →
        TEXT_PUBLISHING → TEXT_PUBLISHED →
        (optional) AUDIO_PRODUCTION → AUDIO_PUBLISHED →
        (optional) VIDEO_PRODUCTION → VIDEO_PUBLISHED →
        ARCHIVED
    
    Each state represents a specific phase in story development:
    - IDEA states: Concept development and structure
    - SCRIPT states: Writing and refinement
    - PUBLISHING states: Platform-specific publication
    - PRODUCTION states: Multi-format production (audio/video)
    """
    
    # Idea Development Phase (3 states)
    IDEA_OUTLINE = "idea_outline"      # Detailed content outline and structure
    IDEA_SKELETON = "idea_skeleton"    # Core story framework (3-6 points)
    IDEA_TITLE = "idea_title"          # Finalized title and hook
    
    # Script Development Phase (3 states)
    SCRIPT_DRAFT = "script_draft"      # Initial script writing
    SCRIPT_REVIEW = "script_review"    # Editorial review and revision
    SCRIPT_APPROVED = "script_approved" # Final approved script
    
    # Text Publishing Phase (2 states)
    TEXT_PUBLISHING = "text_publishing" # Preparing for text publication
    TEXT_PUBLISHED = "text_published"   # Live text content (Reddit, Medium, etc.)
    
    # Audio Production Phase (optional - 3 states)
    AUDIO_RECORDING = "audio_recording"     # Voice recording/synthesis
    AUDIO_REVIEW = "audio_review"           # Audio quality review
    AUDIO_PUBLISHED = "audio_published"     # Live audio content (Spotify, etc.)
    
    # Video Production Phase (optional - 4 states)
    VIDEO_PLANNING = "video_planning"       # Scene and visual planning
    VIDEO_PRODUCTION = "video_production"   # Video assembly and editing
    VIDEO_REVIEW = "video_review"           # Video quality review
    VIDEO_PUBLISHED = "video_published"     # Live video content (YouTube, TikTok)
    
    # Analytics and Learning (3 states)
    TEXT_ANALYTICS = "text_analytics"      # Text performance analysis
    AUDIO_ANALYTICS = "audio_analytics"    # Audio performance analysis
    VIDEO_ANALYTICS = "video_analytics"    # Video performance analysis
    
    # Terminal State
    ARCHIVED = "archived"                  # Completed or terminated


# Define valid state transitions for the state machine
VALID_TRANSITIONS: Dict[StoryState, List[StoryState]] = {
    # Idea Development transitions
    StoryState.IDEA_OUTLINE: [
        StoryState.IDEA_SKELETON,
        StoryState.ARCHIVED  # Can cancel during outline
    ],
    StoryState.IDEA_SKELETON: [
        StoryState.IDEA_TITLE,
        StoryState.IDEA_OUTLINE,  # Can revise outline
        StoryState.ARCHIVED
    ],
    StoryState.IDEA_TITLE: [
        StoryState.SCRIPT_DRAFT,
        StoryState.IDEA_SKELETON,  # Can revise skeleton
        StoryState.ARCHIVED
    ],
    
    # Script Development transitions
    StoryState.SCRIPT_DRAFT: [
        StoryState.SCRIPT_REVIEW,
        StoryState.IDEA_TITLE,  # Major revisions needed
        StoryState.ARCHIVED
    ],
    StoryState.SCRIPT_REVIEW: [
        StoryState.SCRIPT_APPROVED,
        StoryState.SCRIPT_DRAFT,  # Needs rewriting
        StoryState.IDEA_TITLE,    # Fundamental concept change
        StoryState.ARCHIVED
    ],
    StoryState.SCRIPT_APPROVED: [
        StoryState.TEXT_PUBLISHING,
        StoryState.SCRIPT_REVIEW,  # Found issues after approval
        StoryState.ARCHIVED
    ],
    
    # Text Publishing transitions
    StoryState.TEXT_PUBLISHING: [
        StoryState.TEXT_PUBLISHED,
        StoryState.SCRIPT_APPROVED,  # Issues with publication prep
        StoryState.ARCHIVED
    ],
    StoryState.TEXT_PUBLISHED: [
        StoryState.TEXT_ANALYTICS,  # Analyze performance
        StoryState.AUDIO_RECORDING,  # Continue to audio
        StoryState.ARCHIVED  # Text-only release
    ],
    
    # Audio Production transitions (optional path)
    StoryState.AUDIO_RECORDING: [
        StoryState.AUDIO_REVIEW,
        StoryState.TEXT_PUBLISHED,  # Issues with source text
        StoryState.ARCHIVED
    ],
    StoryState.AUDIO_REVIEW: [
        StoryState.AUDIO_PUBLISHED,
        StoryState.AUDIO_RECORDING,  # Re-record needed
        StoryState.ARCHIVED
    ],
    StoryState.AUDIO_PUBLISHED: [
        StoryState.AUDIO_ANALYTICS,  # Analyze performance
        StoryState.VIDEO_PLANNING,    # Continue to video
        StoryState.ARCHIVED  # Audio-only release
    ],
    
    # Video Production transitions (optional path)
    StoryState.VIDEO_PLANNING: [
        StoryState.VIDEO_PRODUCTION,
        StoryState.AUDIO_PUBLISHED,  # Issues with audio source
        StoryState.ARCHIVED
    ],
    StoryState.VIDEO_PRODUCTION: [
        StoryState.VIDEO_REVIEW,
        StoryState.VIDEO_PLANNING,  # Need to revise plan
        StoryState.ARCHIVED
    ],
    StoryState.VIDEO_REVIEW: [
        StoryState.VIDEO_PUBLISHED,
        StoryState.VIDEO_PRODUCTION,  # Needs more work
        StoryState.ARCHIVED
    ],
    StoryState.VIDEO_PUBLISHED: [
        StoryState.VIDEO_ANALYTICS,
        StoryState.ARCHIVED
    ],
    
    # Analytics transitions (feed back to learning)
    StoryState.TEXT_ANALYTICS: [
        StoryState.ARCHIVED  # Analytics complete
    ],
    StoryState.AUDIO_ANALYTICS: [
        StoryState.ARCHIVED
    ],
    StoryState.VIDEO_ANALYTICS: [
        StoryState.ARCHIVED
    ],
    
    # Terminal state - no exits
    StoryState.ARCHIVED: []
}


@dataclass
class Story:
    """Story model for managing story production workflow.
    
    Story serves as the state machine coordinator for story production.
    Each Story is linked to exactly one Idea and manages the progression
    through Script development to publication.
    
    Key Relationships:
    - 1 Story : 1 Idea (required)
    - 1 Story : 0..1 Script (created during SCRIPT_DRAFT state)
    - 1 Story : 0..* PublishedContent (text/audio/video)
    
    State Machine:
        The Story's state field determines the current phase of production
        and which operations are valid. State transitions are enforced
        through the transition_to() method.
    
    Attributes:
        title: Story title (may differ from Idea title after refinement)
        idea_id: ID of the Idea this Story is based on (required, exactly one)
        state: Current state in the production state machine
        status: Simplified status indicator for high-level tracking
        
        script_id: ID of the Script (populated when state >= SCRIPT_DRAFT)
        script_text: Full script text (populated during script states)
        script_title: Final script title
        
        published_text_url: URL of published text (Reddit, Medium, etc.)
        published_audio_url: URL of published audio (Spotify, etc.)
        published_video_url: URL of published video (YouTube, etc.)
        
        metadata: Flexible metadata storage
        tags: Story tags for categorization
        target_platforms: Target publication platforms
        target_formats: Target output formats (text, audio, video)
        
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        created_by: Creator identifier
        
        state_history: History of state transitions
        notes: Production notes and comments
    
    Example:
        >>> from idea import Idea
        >>> idea = Idea(title="The Echo", concept="Girl hears her own voice")
        >>> 
        >>> # Create Story from Idea
        >>> story = Story.from_idea(
        ...     idea=idea,
        ...     created_by="writer_1"
        ... )
        >>> 
        >>> # Progress through states
        >>> story.transition_to(StoryState.IDEA_SKELETON)
        >>> story.transition_to(StoryState.IDEA_TITLE)
        >>> story.transition_to(StoryState.SCRIPT_DRAFT)
        >>> story.script_text = "Last night I woke up... but my body kept sleeping."
        >>> 
        >>> # Continue to publication
        >>> story.transition_to(StoryState.SCRIPT_REVIEW)
        >>> story.transition_to(StoryState.SCRIPT_APPROVED)
        >>> story.transition_to(StoryState.TEXT_PUBLISHING)
        >>> story.published_text_url = "https://reddit.com/r/nosleep/..."
        >>> story.transition_to(StoryState.TEXT_PUBLISHED)
    """
    
    # Core identification
    title: str
    idea_id: str  # Required - exactly one Idea per Story
    
    # State machine
    state: StoryState = StoryState.IDEA_OUTLINE
    status: StoryStatus = StoryStatus.DRAFT
    
    # Script information (populated during script phase)
    script_id: Optional[str] = None
    script_text: str = ""
    script_title: str = ""
    
    # Publication URLs (populated when published)
    published_text_url: Optional[str] = None
    published_audio_url: Optional[str] = None
    published_video_url: Optional[str] = None
    
    # Metadata and configuration
    metadata: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    target_platforms: List[str] = field(default_factory=list)
    target_formats: List[str] = field(default_factory=list)
    
    # Timestamps and tracking
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    
    # State history and notes
    state_history: List[Dict[str, Any]] = field(default_factory=list)
    notes: str = ""
    
    def __post_init__(self):
        """Initialize timestamps and state history."""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        
        # Initialize state history if empty
        if not self.state_history:
            self.state_history = [{
                "state": self.state.value,
                "entered_at": self.created_at,
                "notes": "Initial state"
            }]
    
    def transition_to(self, new_state: StoryState, notes: str = "") -> bool:
        """Transition to a new state in the state machine.
        
        Args:
            new_state: The target state to transition to
            notes: Optional notes about the transition
            
        Returns:
            True if transition was successful, False otherwise
            
        Raises:
            ValueError: If the transition is not valid
        """
        # Check if transition is valid
        if new_state not in VALID_TRANSITIONS.get(self.state, []):
            valid_states = VALID_TRANSITIONS.get(self.state, [])
            valid_names = [s.value for s in valid_states]
            raise ValueError(
                f"Invalid state transition from {self.state.value} to {new_state.value}. "
                f"Valid transitions: {valid_names}"
            )
        
        # Record the transition
        old_state = self.state
        self.state = new_state
        self.updated_at = datetime.now().isoformat()
        
        # Add to state history
        self.state_history.append({
            "state": new_state.value,
            "previous_state": old_state.value,
            "entered_at": self.updated_at,
            "notes": notes
        })
        
        # Update status based on state
        self._update_status()
        
        return True
    
    def _update_status(self) -> None:
        """Update the simplified status based on current state."""
        if self.state in [StoryState.IDEA_OUTLINE, StoryState.IDEA_SKELETON, StoryState.IDEA_TITLE]:
            self.status = StoryStatus.DRAFT
        elif self.state in [StoryState.SCRIPT_DRAFT, StoryState.SCRIPT_REVIEW]:
            self.status = StoryStatus.IN_DEVELOPMENT
        elif self.state == StoryState.SCRIPT_APPROVED:
            self.status = StoryStatus.READY_FOR_REVIEW
        elif self.state in [StoryState.TEXT_PUBLISHING, StoryState.AUDIO_RECORDING, 
                           StoryState.AUDIO_REVIEW, StoryState.VIDEO_PLANNING,
                           StoryState.VIDEO_PRODUCTION, StoryState.VIDEO_REVIEW]:
            self.status = StoryStatus.IN_PRODUCTION
        elif self.state in [StoryState.TEXT_PUBLISHED, StoryState.AUDIO_PUBLISHED, 
                           StoryState.VIDEO_PUBLISHED, StoryState.TEXT_ANALYTICS,
                           StoryState.AUDIO_ANALYTICS, StoryState.VIDEO_ANALYTICS]:
            self.status = StoryStatus.PUBLISHED
        elif self.state == StoryState.ARCHIVED:
            self.status = StoryStatus.ARCHIVED
    
    def get_valid_transitions(self) -> List[StoryState]:
        """Get list of valid states that can be transitioned to from current state.
        
        Returns:
            List of valid target states
        """
        return VALID_TRANSITIONS.get(self.state, [])
    
    def can_transition_to(self, target_state: StoryState) -> bool:
        """Check if transition to target state is valid.
        
        Args:
            target_state: The state to check
            
        Returns:
            True if transition is valid, False otherwise
        """
        return target_state in VALID_TRANSITIONS.get(self.state, [])
    
    @classmethod
    def from_idea(
        cls,
        idea: Any,  # Idea object from idea.py
        title: Optional[str] = None,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        created_by: Optional[str] = None,
    ) -> "Story":
        """Create a Story from an Idea.
        
        This is the primary way to create a Story - from an existing Idea.
        The Story inherits relevant metadata from the Idea.
        
        Args:
            idea: The Idea object this Story is based on
            title: Story title (defaults to Idea title)
            target_platforms: Target platforms (defaults to Idea's)
            target_formats: Target formats (defaults to Idea's)
            created_by: Creator identifier
            
        Returns:
            New Story instance linked to the Idea
        """
        # Extract Idea ID
        idea_id = getattr(idea, 'id', None) or str(id(idea))
        
        # Use Idea's title if not specified
        if title is None:
            title = getattr(idea, 'title', 'Untitled Story')
        
        # Use Idea's platforms if not specified
        if target_platforms is None:
            target_platforms = getattr(idea, 'target_platforms', [])
        
        # Use Idea's formats if not specified
        if target_formats is None:
            target_formats = getattr(idea, 'target_formats', [])
        
        # Extract tags from Idea keywords
        tags = getattr(idea, 'keywords', [])
        
        return cls(
            title=title,
            idea_id=idea_id,
            target_platforms=target_platforms,
            target_formats=target_formats,
            tags=tags,
            created_by=created_by,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Story to dictionary representation.
        
        Returns:
            Dictionary containing all fields with Enums converted to strings
        """
        data = asdict(self)
        data["state"] = self.state.value
        data["status"] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Story":
        """Create Story from dictionary.
        
        Args:
            data: Dictionary containing Story fields
            
        Returns:
            Story instance
        """
        # Handle enum conversions
        state = data.get("state", "idea_outline")
        if isinstance(state, str):
            try:
                state = StoryState(state)
            except ValueError:
                state = StoryState.IDEA_OUTLINE
        
        status = data.get("status", "draft")
        if isinstance(status, str):
            try:
                status = StoryStatus(status)
            except ValueError:
                status = StoryStatus.DRAFT
        
        return cls(
            title=data.get("title", ""),
            idea_id=data.get("idea_id", ""),
            state=state,
            status=status,
            script_id=data.get("script_id"),
            script_text=data.get("script_text", ""),
            script_title=data.get("script_title", ""),
            published_text_url=data.get("published_text_url"),
            published_audio_url=data.get("published_audio_url"),
            published_video_url=data.get("published_video_url"),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            target_platforms=data.get("target_platforms", []),
            target_formats=data.get("target_formats", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            created_by=data.get("created_by"),
            state_history=data.get("state_history", []),
            notes=data.get("notes", ""),
        )
    
    def __repr__(self) -> str:
        """String representation of Story."""
        return (
            f"Story(title='{self.title[:50]}...', "
            f"state={self.state.value}, "
            f"status={self.status.value}, "
            f"idea_id={self.idea_id})"
        )
