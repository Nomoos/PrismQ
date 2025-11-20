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
    
    This enum defines the complete state machine for producing stories with
    granular review and quality control stages:
    - One Idea generates one Story
    - Story progresses through detailed quality gates
    - Each state represents a specific review or refinement phase
    
    State Machine Flow:
        Idea → IdeaReview → Outline → TitleDraft →
        ScriptDraft → ContentReview → Editing →
        GrammarReview → ConsistencyCheck → ToneCheck → ReadabilityReview →
        Finalization → TitleOptimization → Publishing
    
    ScriptImprovements serves as a central hub for revisions,
    allowing loops back to Editing or TitleRefinement.
    """
    
    # Concept Phase (4 states)
    IDEA = "idea"                          # Initial concept
    IDEA_REVIEW = "idea_review"            # Review and validate concept
    OUTLINE = "outline"                    # Create structured outline
    TITLE_DRAFT = "title_draft"            # Draft initial title
    
    # Script Creation Phase (2 states)
    SCRIPT_DRAFT = "script_draft"          # Write initial script
    CONTENT_REVIEW = "content_review"      # Review content structure and flow
    
    # Editing Phase (1 state)
    EDITING = "editing"                    # Edit for clarity and coherence
    
    # Quality Review Pipeline (4 states)
    GRAMMAR_REVIEW = "grammar_review"      # Check grammar, spelling, punctuation
    CONSISTENCY_CHECK = "consistency_check" # Verify consistency (names, facts, timeline)
    TONE_CHECK = "tone_check"              # Validate tone and style match
    READABILITY_REVIEW = "readability_review" # Ensure suitable for voiceover
    
    # Improvement Hub (1 state)
    SCRIPT_IMPROVEMENTS = "script_improvements" # Central hub for revisions
    
    # Title Refinement (2 states)
    TITLE_REFINEMENT = "title_refinement"  # Align title with final script
    TITLE_OPTIMIZATION = "title_optimization" # Optimize for engagement/SEO
    
    # Final Phase (2 states)
    FINALIZATION = "finalization"          # Final preparation
    PUBLISHING = "publishing"              # Publish to platform
    
    # Terminal State
    ARCHIVED = "archived"                  # Completed or terminated


# Define valid state transitions for the state machine
VALID_TRANSITIONS: Dict[StoryState, List[StoryState]] = {
    # Concept Phase transitions
    StoryState.IDEA: [
        StoryState.IDEA_REVIEW,
        StoryState.ARCHIVED  # Can cancel at any time
    ],
    StoryState.IDEA_REVIEW: [
        StoryState.OUTLINE,
        StoryState.IDEA,  # Revise concept
        StoryState.ARCHIVED
    ],
    StoryState.OUTLINE: [
        StoryState.TITLE_DRAFT,
        StoryState.ARCHIVED
    ],
    StoryState.TITLE_DRAFT: [
        StoryState.SCRIPT_DRAFT,
        StoryState.ARCHIVED
    ],
    
    # Script Creation transitions
    StoryState.SCRIPT_DRAFT: [
        StoryState.CONTENT_REVIEW,
        StoryState.TITLE_REFINEMENT,  # Can refine title during draft
        StoryState.ARCHIVED
    ],
    StoryState.CONTENT_REVIEW: [
        StoryState.EDITING,
        StoryState.ARCHIVED
    ],
    
    # Editing Phase
    StoryState.EDITING: [
        StoryState.GRAMMAR_REVIEW,
        StoryState.ARCHIVED
    ],
    
    # Quality Review Pipeline
    StoryState.GRAMMAR_REVIEW: [
        StoryState.CONSISTENCY_CHECK,
        StoryState.SCRIPT_IMPROVEMENTS,  # Major language issues
        StoryState.ARCHIVED
    ],
    StoryState.CONSISTENCY_CHECK: [
        StoryState.TONE_CHECK,
        StoryState.SCRIPT_IMPROVEMENTS,  # Inconsistencies found
        StoryState.ARCHIVED
    ],
    StoryState.TONE_CHECK: [
        StoryState.READABILITY_REVIEW,
        StoryState.SCRIPT_IMPROVEMENTS,  # Tone mismatch
        StoryState.ARCHIVED
    ],
    StoryState.READABILITY_REVIEW: [
        StoryState.FINALIZATION,
        StoryState.SCRIPT_IMPROVEMENTS,  # Not suitable for voiceover
        StoryState.ARCHIVED
    ],
    
    # Improvement Hub (central point for revisions)
    StoryState.SCRIPT_IMPROVEMENTS: [
        StoryState.EDITING,  # Re-edit after improvements
        StoryState.TITLE_REFINEMENT,  # Refine title
        StoryState.ARCHIVED
    ],
    
    # Title Refinement
    StoryState.TITLE_REFINEMENT: [
        StoryState.FINALIZATION,  # Title aligned with script
        StoryState.ARCHIVED
    ],
    
    # Final Phase
    StoryState.FINALIZATION: [
        StoryState.TITLE_OPTIMIZATION,
        StoryState.ARCHIVED
    ],
    StoryState.TITLE_OPTIMIZATION: [
        StoryState.PUBLISHING,
        StoryState.ARCHIVED
    ],
    StoryState.PUBLISHING: [
        StoryState.ARCHIVED  # End of workflow
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
        >>> story.transition_to(StoryState.IDEA_REVIEW)
        >>> story.transition_to(StoryState.OUTLINE)
        >>> story.transition_to(StoryState.TITLE_DRAFT)
        >>> story.transition_to(StoryState.SCRIPT_DRAFT)
        >>> story.script_text = "Last night I woke up... but my body kept sleeping."
        >>> 
        >>> # Continue through review pipeline
        >>> story.transition_to(StoryState.CONTENT_REVIEW)
        >>> story.transition_to(StoryState.EDITING)
        >>> story.transition_to(StoryState.GRAMMAR_REVIEW)
        >>> story.transition_to(StoryState.CONSISTENCY_CHECK)
        >>> story.transition_to(StoryState.TONE_CHECK)
        >>> story.transition_to(StoryState.READABILITY_REVIEW)
        >>> story.transition_to(StoryState.FINALIZATION)
        >>> story.transition_to(StoryState.TITLE_OPTIMIZATION)
        >>> story.published_text_url = "https://reddit.com/r/nosleep/..."
        >>> story.transition_to(StoryState.PUBLISHING)
    """
    
    # Core identification
    title: str
    idea_id: str  # Required - exactly one Idea per Story
    
    # State machine
    state: StoryState = StoryState.IDEA
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
        if self.state in [StoryState.IDEA, StoryState.IDEA_REVIEW, StoryState.OUTLINE, StoryState.TITLE_DRAFT]:
            self.status = StoryStatus.DRAFT
        elif self.state in [StoryState.SCRIPT_DRAFT, StoryState.CONTENT_REVIEW, StoryState.EDITING]:
            self.status = StoryStatus.IN_DEVELOPMENT
        elif self.state in [StoryState.GRAMMAR_REVIEW, StoryState.CONSISTENCY_CHECK, 
                           StoryState.TONE_CHECK, StoryState.READABILITY_REVIEW,
                           StoryState.SCRIPT_IMPROVEMENTS]:
            self.status = StoryStatus.READY_FOR_REVIEW
        elif self.state in [StoryState.TITLE_REFINEMENT, StoryState.FINALIZATION, 
                           StoryState.TITLE_OPTIMIZATION]:
            self.status = StoryStatus.APPROVED
        elif self.state == StoryState.PUBLISHING:
            self.status = StoryStatus.IN_PRODUCTION
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
