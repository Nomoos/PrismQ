"""Story Translation model for multi-language content support.

This module defines the StoryTranslation data model for managing multiple language
versions of the same story. It implements best practices for multi-language content
management with translation feedback loop tracking.

Design Pattern:
    - One Story ID (from Idea) with multiple language rows
    - Composite key: (story_id, language_code)
    - Original language designated in parent Idea/Story
    - Translation feedback loop tracking for quality assurance

Translation Workflow:
    1. AI Translator creates initial translation from original
    2. AI Reviewer compares translation to original for meaning fidelity
    3. Feedback loop: Reviewer flags issues → Translator revises
    4. Loop continues until meaning aligns (with max iteration limit)
    5. Translation marked as approved once review passes

Language Code Standard:
    Uses ISO 639-1 language codes (e.g., 'en', 'cs', 'es', 'de', 'fr')
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class TranslationStatus(Enum):
    """Status of a translation in the review workflow."""
    
    DRAFT = "draft"  # Initial translation in progress
    PENDING_REVIEW = "pending_review"  # Submitted for review
    REVISION_NEEDED = "revision_needed"  # Reviewer found issues
    APPROVED = "approved"  # Review passed, translation faithful to original
    PUBLISHED = "published"  # Translation published and live


@dataclass
class TranslationFeedback:
    """Feedback from AI Reviewer to AI Translator.
    
    Captures specific issues found during review to guide revision.
    """
    
    reviewer_id: str  # AI Reviewer identifier
    iteration: int  # Which review iteration (1, 2, etc.)
    timestamp: str  # When feedback was given
    issues: List[str]  # List of specific issues found
    suggestions: List[str]  # Suggestions for improvement
    meaning_score: Optional[int] = None  # 0-100 score for meaning fidelity
    notes: str = ""  # Additional reviewer notes


@dataclass
class StoryTranslation:
    """Translation of a story into a specific language.
    
    Represents one language version of a story, linked to the original via story_id.
    All translations of the same story share the same story_id but have different
    language codes.
    
    Attributes:
        story_id: ID of the original story/idea (links all translations)
        language_code: ISO 639-1 language code (e.g., 'en', 'cs', 'es')
        title: Translated title
        text: Translated story text/script
        
        Translation Quality:
            status: Current workflow status
            iteration_count: Number of translation revision iterations
            max_iterations: Maximum allowed revisions (default 2)
            translator_id: AI Translator identifier
            reviewer_id: AI Reviewer identifier (if reviewed)
            
        Feedback Loop:
            feedback_history: List of all feedback from reviews
            last_feedback: Most recent feedback summary
            meaning_verified: Whether meaning matches original
            
        Metadata:
            translated_from: Source language code (typically original language)
            version: Translation version number
            created_at: When translation was created
            updated_at: When last modified
            approved_at: When approved by reviewer
            published_at: When published
            notes: Translation notes
    
    Example:
        >>> # Original English story
        >>> original_story_id = 42
        >>> 
        >>> # Czech translation
        >>> czech = StoryTranslation(
        ...     story_id=42,
        ...     language_code="cs",
        ...     title="Echo",
        ...     text="Včera v noci jsem se probudila... ale mé tělo dál spalo.",
        ...     translated_from="en",
        ...     translator_id="AI-Translator-GPT4",
        ...     status=TranslationStatus.PENDING_REVIEW
        ... )
        >>> 
        >>> # Spanish translation
        >>> spanish = StoryTranslation(
        ...     story_id=42,
        ...     language_code="es",
        ...     title="El Eco",
        ...     text="Anoche me desperté... pero mi cuerpo siguió durmiendo.",
        ...     translated_from="en",
        ...     translator_id="AI-Translator-GPT4"
        ... )
    """
    
    # Core Identity
    story_id: int  # Links to parent story/idea
    language_code: str  # ISO 639-1 code (en, cs, es, etc.)
    
    # Content
    title: str
    text: str
    
    # Translation Process
    status: TranslationStatus = TranslationStatus.DRAFT
    iteration_count: int = 0
    max_iterations: int = 2  # Limit feedback loop
    translator_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    
    # Feedback Loop
    feedback_history: List[Dict[str, Any]] = field(default_factory=list)
    last_feedback: str = ""
    meaning_verified: bool = False
    
    # Metadata
    translated_from: str = "en"  # Source language
    version: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    approved_at: Optional[str] = None
    published_at: Optional[str] = None
    notes: str = ""
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
    
    def add_feedback(
        self,
        reviewer_id: str,
        issues: List[str],
        suggestions: List[str],
        meaning_score: Optional[int] = None,
        notes: str = ""
    ) -> None:
        """Add feedback from AI Reviewer.
        
        Args:
            reviewer_id: Identifier of the reviewer
            issues: List of specific issues found
            suggestions: List of improvement suggestions
            meaning_score: Optional 0-100 score for meaning fidelity
            notes: Additional notes
        """
        self.iteration_count += 1
        
        feedback = {
            "reviewer_id": reviewer_id,
            "iteration": self.iteration_count,
            "timestamp": datetime.now().isoformat(),
            "issues": issues,
            "suggestions": suggestions,
            "meaning_score": meaning_score,
            "notes": notes
        }
        
        self.feedback_history.append(feedback)
        self.reviewer_id = reviewer_id
        
        # Update last feedback summary
        self.last_feedback = f"Iteration {self.iteration_count}: {len(issues)} issues found"
        
        # Update status
        if len(issues) == 0 and meaning_score and meaning_score >= 85:
            self.status = TranslationStatus.APPROVED
            self.meaning_verified = True
            self.approved_at = datetime.now().isoformat()
        else:
            self.status = TranslationStatus.REVISION_NEEDED
        
        self.updated_at = datetime.now().isoformat()
    
    def can_request_revision(self) -> bool:
        """Check if another revision iteration is allowed.
        
        Returns:
            True if iteration count is below max_iterations
        """
        return self.iteration_count < self.max_iterations
    
    def submit_for_review(self) -> None:
        """Mark translation as ready for review."""
        self.status = TranslationStatus.PENDING_REVIEW
        self.updated_at = datetime.now().isoformat()
    
    def approve(self, reviewer_id: str) -> None:
        """Approve translation without further revision.
        
        Args:
            reviewer_id: Identifier of the reviewer
        """
        self.status = TranslationStatus.APPROVED
        self.meaning_verified = True
        self.reviewer_id = reviewer_id
        self.approved_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def publish(self) -> None:
        """Mark translation as published."""
        if self.status != TranslationStatus.APPROVED:
            raise ValueError("Cannot publish translation that is not approved")
        
        self.status = TranslationStatus.PUBLISHED
        self.published_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def update_content(self, title: str = None, text: str = None) -> None:
        """Update translation content (typically after feedback).
        
        Args:
            title: New translated title (optional)
            text: New translated text (optional)
        """
        if title is not None:
            self.title = title
        if text is not None:
            self.text = text
        
        self.version += 1
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert StoryTranslation to dictionary representation.
        
        Returns:
            Dictionary containing all fields with Enums converted to strings
        """
        data = asdict(self)
        data["status"] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoryTranslation":
        """Create StoryTranslation from dictionary.
        
        Args:
            data: Dictionary containing StoryTranslation fields
            
        Returns:
            StoryTranslation instance
        """
        # Handle enum conversion
        status = data.get("status", "draft")
        if isinstance(status, str):
            try:
                status = TranslationStatus(status)
            except ValueError:
                status = TranslationStatus.DRAFT
        
        return cls(
            story_id=data.get("story_id"),
            language_code=data.get("language_code"),
            title=data.get("title", ""),
            text=data.get("text", ""),
            status=status,
            iteration_count=data.get("iteration_count", 0),
            max_iterations=data.get("max_iterations", 2),
            translator_id=data.get("translator_id"),
            reviewer_id=data.get("reviewer_id"),
            feedback_history=data.get("feedback_history", []),
            last_feedback=data.get("last_feedback", ""),
            meaning_verified=data.get("meaning_verified", False),
            translated_from=data.get("translated_from", "en"),
            version=data.get("version", 1),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            approved_at=data.get("approved_at"),
            published_at=data.get("published_at"),
            notes=data.get("notes", "")
        )
    
    def __repr__(self) -> str:
        """String representation of StoryTranslation."""
        return (
            f"StoryTranslation(story_id={self.story_id}, "
            f"lang={self.language_code}, "
            f"status={self.status.value}, "
            f"iterations={self.iteration_count}/{self.max_iterations}, "
            f"verified={self.meaning_verified})"
        )
