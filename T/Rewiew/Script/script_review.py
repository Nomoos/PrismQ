"""Script Review model for PrismQ AI-powered script evaluation.

This module defines the ScriptReview data model for AI-powered script evaluation
with scoring system (0-100%) and detailed improvement recommendations for target
audience optimization.

The ScriptReview model enables:
- AI-driven script evaluation with numerical scoring
- Detailed improvement points for audience optimization
- YouTube short content optimization (< 3 minutes, variable length)
- Feedback loop integration with Script Writer

Workflow Position:
    ScriptDraft → ScriptReview (AI Reviewer) → ScriptWriter (with feedback) → ScriptApproved
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


@dataclass
class ScriptVersion:
    """Version of a script for comparison and research.
    
    Stores script text and metadata for each iteration to enable:
    - Side-by-side comparison of versions
    - Research on feedback loop effectiveness
    - Tracking what changed between iterations
    
    Attributes:
        version_number: Version number (1, 2, 3, ...)
        script_text: The actual script text content
        length_seconds: Duration in seconds
        created_at: When this version was created
        created_by: Who/what created this version (e.g., "AI-Writer-001", "human")
        changes_from_previous: Description of changes from previous version
        review_score: Score this version received (if reviewed)
        notes: Additional notes about this version
    """
    
    version_number: int
    script_text: str
    length_seconds: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = ""
    changes_from_previous: str = ""
    review_score: Optional[int] = None
    notes: str = ""


class ReviewCategory(Enum):
    """Categories for script review evaluation."""
    
    ENGAGEMENT = "engagement"  # Hook strength, audience retention
    PACING = "pacing"  # Timing, rhythm, flow
    CLARITY = "clarity"  # Message clarity, understandability
    AUDIENCE_FIT = "audience_fit"  # Target audience alignment
    STRUCTURE = "structure"  # Story structure, organization
    IMPACT = "impact"  # Emotional impact, memorability
    YOUTUBE_SHORT_OPTIMIZATION = "youtube_short_optimization"  # YouTube short specific
    LENGTH_OPTIMIZATION = "length_optimization"  # Duration optimization


class ContentLength(Enum):
    """Target content length categories."""
    
    YOUTUBE_SHORT = "youtube_short"  # < 60 seconds
    YOUTUBE_SHORT_EXTENDED = "youtube_short_extended"  # 60-180 seconds
    SHORT_FORM = "short_form"  # < 3 minutes
    MEDIUM_FORM = "medium_form"  # 3-10 minutes
    LONG_FORM = "long_form"  # > 10 minutes
    VARIABLE = "variable"  # Variable length


@dataclass
class ImprovementPoint:
    """Individual improvement recommendation."""
    
    category: ReviewCategory
    title: str
    description: str
    priority: str  # "high", "medium", "low"
    impact_score: int  # 0-100, estimated improvement impact
    specific_example: str = ""
    suggested_fix: str = ""


@dataclass
class CategoryScore:
    """Score for a specific review category."""
    
    category: ReviewCategory
    score: int  # 0-100
    reasoning: str
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


@dataclass
class ScriptReview:
    """AI-powered script review with scoring and improvement recommendations.
    
    ScriptReview provides comprehensive evaluation of scripts with:
    - Overall quality score (0-100%)
    - Category-specific scores and analysis
    - Prioritized improvement recommendations
    - YouTube short optimization guidance
    - Target audience alignment assessment
    
    The review serves as input for the Script Writer's feedback loop,
    enabling iterative optimization based on AI evaluation.
    
    Attributes:
        script_id: Identifier of the reviewed script
        script_title: Title of the reviewed script
        overall_score: Overall quality score (0-100)
        category_scores: Scores for each evaluation category
        improvement_points: Prioritized list of improvements
        
        Target Optimization:
            target_audience: Description of target audience
            audience_alignment_score: How well script fits audience (0-100)
            target_length: Target content length category
            current_length_seconds: Current script duration in seconds
            optimal_length_seconds: Recommended duration in seconds
            
        YouTube Short Optimization:
            is_youtube_short: Whether optimized for YouTube shorts
            hook_strength_score: Opening hook effectiveness (0-100)
            retention_score: Predicted audience retention (0-100)
            viral_potential_score: Estimated viral potential (0-100)
            
        Review Metadata:
            reviewer_id: AI reviewer identifier
            review_version: Review iteration number
            reviewed_at: Timestamp of review
            confidence_score: AI confidence in evaluation (0-100)
            
        Feedback Loop:
            needs_major_revision: Whether major rewrite needed
            iteration_number: Number of review-write iterations
            previous_review_id: ID of previous review (if iterative)
            improvement_trajectory: Score change over iterations
            
        Script Versioning:
            script_version: Current version of the script being reviewed
            script_versions_history: List of all script versions for comparison
            
        Additional Context:
            strengths: Key strengths of the script
            primary_concern: Main issue to address
            quick_wins: Easy improvements with high impact
            notes: Additional reviewer notes
            metadata: Flexible metadata storage
    
    Example:
        >>> review = ScriptReview(
        ...     script_id="script-001",
        ...     script_title="The Echo - Horror Short",
        ...     overall_score=72,
        ...     target_audience="Horror enthusiasts aged 18-35",
        ...     audience_alignment_score=85,
        ...     target_length=ContentLength.YOUTUBE_SHORT_EXTENDED,
        ...     current_length_seconds=145,
        ...     optimal_length_seconds=90,
        ...     is_youtube_short=True,
        ...     hook_strength_score=95,
        ...     retention_score=68,
        ...     viral_potential_score=78,
        ...     needs_major_revision=False,
        ...     iteration_number=1
        ... )
        >>> 
        >>> # Add category scores
        >>> review.category_scores.append(CategoryScore(
        ...     category=ReviewCategory.ENGAGEMENT,
        ...     score=85,
        ...     reasoning="Strong hook, needs better pacing in middle",
        ...     strengths=["Compelling opening", "Emotional impact"],
        ...     weaknesses=["Mid-section drag", "Predictable twist"]
        ... ))
        >>> 
        >>> # Add improvement points
        >>> review.improvement_points.append(ImprovementPoint(
        ...     category=ReviewCategory.PACING,
        ...     title="Reduce middle section length",
        ...     description="Cut 30-40 seconds from investigation sequence",
        ...     priority="high",
        ...     impact_score=25,
        ...     suggested_fix="Focus on 2-3 key moments instead of 5"
        ... ))
    """
    
    script_id: str
    script_title: str
    overall_score: int  # 0-100
    
    # Category Analysis
    category_scores: List[CategoryScore] = field(default_factory=list)
    improvement_points: List[ImprovementPoint] = field(default_factory=list)
    
    # Target Optimization
    target_audience: str = ""
    audience_alignment_score: int = 0  # 0-100
    target_length: ContentLength = ContentLength.VARIABLE
    current_length_seconds: Optional[int] = None
    optimal_length_seconds: Optional[int] = None
    
    # YouTube Short Optimization
    is_youtube_short: bool = False
    hook_strength_score: int = 0  # 0-100
    retention_score: int = 0  # 0-100, predicted retention
    viral_potential_score: int = 0  # 0-100
    
    # Review Metadata
    reviewer_id: str = "AI-ScriptReviewer-001"
    review_version: int = 1
    reviewed_at: Optional[str] = None
    confidence_score: int = 85  # 0-100, AI confidence
    
    # Feedback Loop
    needs_major_revision: bool = False
    iteration_number: int = 1
    previous_review_id: Optional[str] = None
    improvement_trajectory: List[int] = field(default_factory=list)  # Score history
    
    # Script Versioning (NEW for comparison and research)
    script_version: Optional[ScriptVersion] = None
    script_versions_history: List[ScriptVersion] = field(default_factory=list)
    
    # Additional Context
    strengths: List[str] = field(default_factory=list)
    primary_concern: str = ""
    quick_wins: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.reviewed_at is None:
            self.reviewed_at = datetime.now().isoformat()
        
        # Add current score to trajectory
        if self.overall_score not in self.improvement_trajectory:
            self.improvement_trajectory.append(self.overall_score)
    
    def get_category_score(self, category: ReviewCategory) -> Optional[CategoryScore]:
        """Get score for a specific category.
        
        Args:
            category: The review category to retrieve
            
        Returns:
            CategoryScore if found, None otherwise
        """
        for cat_score in self.category_scores:
            if cat_score.category == category:
                return cat_score
        return None
    
    def get_high_priority_improvements(self) -> List[ImprovementPoint]:
        """Get high-priority improvement points.
        
        Returns:
            List of high-priority improvements sorted by impact score
        """
        high_priority = [
            imp for imp in self.improvement_points
            if imp.priority == "high"
        ]
        return sorted(high_priority, key=lambda x: x.impact_score, reverse=True)
    
    def get_youtube_short_readiness(self) -> Dict[str, Any]:
        """Calculate YouTube short optimization readiness.
        
        Returns:
            Dictionary with readiness metrics
        """
        if not self.is_youtube_short:
            return {"ready": False, "reason": "Not configured for YouTube shorts"}
        
        # Check length compliance
        length_ok = False
        length_feedback = ""
        if self.current_length_seconds:
            if self.target_length == ContentLength.YOUTUBE_SHORT:
                length_ok = self.current_length_seconds <= 60
                length_feedback = f"Length: {self.current_length_seconds}s (target: ≤60s)"
            elif self.target_length == ContentLength.YOUTUBE_SHORT_EXTENDED:
                length_ok = self.current_length_seconds <= 180
                length_feedback = f"Length: {self.current_length_seconds}s (target: ≤180s)"
            else:
                length_ok = self.current_length_seconds <= 180
                length_feedback = f"Length: {self.current_length_seconds}s (target: <3min)"
        
        # Calculate readiness score (weighted average)
        readiness_score = int(
            (self.hook_strength_score * 0.3) +
            (self.retention_score * 0.3) +
            (self.viral_potential_score * 0.2) +
            (self.overall_score * 0.2)
        )
        
        # Determine readiness
        ready = (
            length_ok and
            self.hook_strength_score >= 70 and
            self.retention_score >= 65 and
            readiness_score >= 70
        )
        
        return {
            "ready": ready,
            "readiness_score": readiness_score,
            "length_compliant": length_ok,
            "length_feedback": length_feedback,
            "hook_strength": self.hook_strength_score,
            "retention_score": self.retention_score,
            "viral_potential": self.viral_potential_score,
            "recommendations": self.get_high_priority_improvements()[:3]
        }
    
    def add_script_version(
        self,
        script_text: str,
        length_seconds: Optional[int] = None,
        created_by: str = "",
        changes_from_previous: str = ""
    ) -> ScriptVersion:
        """Add a new script version for comparison and research.
        
        This method stores script versions to enable:
        - Side-by-side comparison of iterations
        - Research on feedback loop effectiveness
        - Tracking what changed between iterations
        
        Args:
            script_text: The script text content
            length_seconds: Duration in seconds
            created_by: Who/what created this version
            changes_from_previous: Description of changes
            
        Returns:
            The created ScriptVersion instance
        """
        version_number = len(self.script_versions_history) + 1
        
        version = ScriptVersion(
            version_number=version_number,
            script_text=script_text,
            length_seconds=length_seconds or self.current_length_seconds,
            created_by=created_by or self.reviewer_id,
            changes_from_previous=changes_from_previous,
            review_score=self.overall_score
        )
        
        self.script_versions_history.append(version)
        self.script_version = version
        
        return version
    
    def get_version_comparison(self) -> Dict[str, Any]:
        """Get comparison data for all script versions.
        
        Returns:
            Dictionary with version comparison metrics
        """
        if len(self.script_versions_history) < 2:
            return {
                "versions_count": len(self.script_versions_history),
                "comparison_available": False,
                "message": "Need at least 2 versions for comparison"
            }
        
        versions_data = []
        for v in self.script_versions_history:
            versions_data.append({
                "version": v.version_number,
                "length_seconds": v.length_seconds,
                "review_score": v.review_score,
                "created_at": v.created_at,
                "created_by": v.created_by,
                "changes": v.changes_from_previous,
                "text_length_chars": len(v.script_text)
            })
        
        # Calculate improvements
        first_version = self.script_versions_history[0]
        latest_version = self.script_versions_history[-1]
        
        length_change = None
        if first_version.length_seconds and latest_version.length_seconds:
            length_change = latest_version.length_seconds - first_version.length_seconds
        
        score_change = None
        if first_version.review_score and latest_version.review_score:
            score_change = latest_version.review_score - first_version.review_score
        
        return {
            "versions_count": len(self.script_versions_history),
            "comparison_available": True,
            "versions": versions_data,
            "improvements": {
                "length_change_seconds": length_change,
                "score_change": score_change,
                "iterations": len(self.script_versions_history) - 1
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ScriptReview to dictionary representation.
        
        Returns:
            Dictionary containing all fields with Enums converted to strings
        """
        data = asdict(self)
        
        # Convert enums to strings
        data["target_length"] = self.target_length.value
        
        # Convert category scores
        data["category_scores"] = [
            {
                **asdict(cs),
                "category": cs.category.value
            }
            for cs in self.category_scores
        ]
        
        # Convert improvement points
        data["improvement_points"] = [
            {
                **asdict(ip),
                "category": ip.category.value
            }
            for ip in self.improvement_points
        ]
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScriptReview":
        """Create ScriptReview from dictionary.
        
        Args:
            data: Dictionary containing ScriptReview fields
            
        Returns:
            ScriptReview instance
        """
        # Handle enum conversions
        target_length = data.get("target_length", "variable")
        if isinstance(target_length, str):
            try:
                target_length = ContentLength(target_length)
            except ValueError:
                target_length = ContentLength.VARIABLE
        
        # Convert category scores
        category_scores = []
        for cs_data in data.get("category_scores", []):
            category = ReviewCategory(cs_data["category"])
            category_scores.append(CategoryScore(
                category=category,
                score=cs_data["score"],
                reasoning=cs_data["reasoning"],
                strengths=cs_data.get("strengths", []),
                weaknesses=cs_data.get("weaknesses", [])
            ))
        
        # Convert improvement points
        improvement_points = []
        for ip_data in data.get("improvement_points", []):
            category = ReviewCategory(ip_data["category"])
            improvement_points.append(ImprovementPoint(
                category=category,
                title=ip_data["title"],
                description=ip_data["description"],
                priority=ip_data["priority"],
                impact_score=ip_data["impact_score"],
                specific_example=ip_data.get("specific_example", ""),
                suggested_fix=ip_data.get("suggested_fix", "")
            ))
        
        # Convert script versions
        script_version = None
        script_version_data = data.get("script_version")
        if script_version_data:
            script_version = ScriptVersion(
                version_number=script_version_data["version_number"],
                script_text=script_version_data["script_text"],
                length_seconds=script_version_data.get("length_seconds"),
                created_at=script_version_data.get("created_at", datetime.now().isoformat()),
                created_by=script_version_data.get("created_by", ""),
                changes_from_previous=script_version_data.get("changes_from_previous", ""),
                review_score=script_version_data.get("review_score"),
                notes=script_version_data.get("notes", "")
            )
        
        script_versions_history = []
        for sv_data in data.get("script_versions_history", []):
            script_versions_history.append(ScriptVersion(
                version_number=sv_data["version_number"],
                script_text=sv_data["script_text"],
                length_seconds=sv_data.get("length_seconds"),
                created_at=sv_data.get("created_at", datetime.now().isoformat()),
                created_by=sv_data.get("created_by", ""),
                changes_from_previous=sv_data.get("changes_from_previous", ""),
                review_score=sv_data.get("review_score"),
                notes=sv_data.get("notes", "")
            ))
        
        return cls(
            script_id=data["script_id"],
            script_title=data["script_title"],
            overall_score=data["overall_score"],
            category_scores=category_scores,
            improvement_points=improvement_points,
            target_audience=data.get("target_audience", ""),
            audience_alignment_score=data.get("audience_alignment_score", 0),
            target_length=target_length,
            current_length_seconds=data.get("current_length_seconds"),
            optimal_length_seconds=data.get("optimal_length_seconds"),
            is_youtube_short=data.get("is_youtube_short", False),
            hook_strength_score=data.get("hook_strength_score", 0),
            retention_score=data.get("retention_score", 0),
            viral_potential_score=data.get("viral_potential_score", 0),
            reviewer_id=data.get("reviewer_id", "AI-ScriptReviewer-001"),
            review_version=data.get("review_version", 1),
            reviewed_at=data.get("reviewed_at"),
            confidence_score=data.get("confidence_score", 85),
            needs_major_revision=data.get("needs_major_revision", False),
            iteration_number=data.get("iteration_number", 1),
            previous_review_id=data.get("previous_review_id"),
            improvement_trajectory=data.get("improvement_trajectory", []),
            script_version=script_version,
            script_versions_history=script_versions_history,
            strengths=data.get("strengths", []),
            primary_concern=data.get("primary_concern", ""),
            quick_wins=data.get("quick_wins", []),
            notes=data.get("notes", ""),
            metadata=data.get("metadata", {})
        )
    
    def __repr__(self) -> str:
        """String representation of ScriptReview."""
        return (
            f"ScriptReview(script='{self.script_title}', "
            f"score={self.overall_score}%, "
            f"iteration={self.iteration_number}, "
            f"improvements={len(self.improvement_points)})"
        )
