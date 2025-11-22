"""Title Review model for PrismQ AI-powered title evaluation.

This module defines the TitleReview data model for AI-powered title evaluation
against script content and original idea intent. The review assesses whether the
title accurately represents the script, reflects the idea's purpose, and sets
appropriate audience expectations.

The TitleReview model enables:
- Title-to-script alignment evaluation
- Title-to-idea intent verification
- Audience engagement assessment
- Expectation setting validation
- Feedback for title improvement iterations

Workflow Position:
    Title v1 + Script v1 + Idea → TitleReview (AI Reviewer) → Title v2 (with feedback)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class TitleReviewCategory(Enum):
    """Categories for title review evaluation."""
    
    SCRIPT_ALIGNMENT = "script_alignment"  # Title matches script content
    IDEA_ALIGNMENT = "idea_alignment"  # Title reflects original idea intent
    ENGAGEMENT = "engagement"  # Title is compelling and attention-grabbing
    EXPECTATION_SETTING = "expectation_setting"  # Title sets correct expectations
    CLARITY = "clarity"  # Title is clear and understandable
    SEO_OPTIMIZATION = "seo_optimization"  # SEO keywords and searchability
    AUDIENCE_FIT = "audience_fit"  # Target audience appropriateness
    LENGTH = "length"  # Title length optimization


@dataclass
class TitleImprovementPoint:
    """Individual improvement recommendation for title."""
    
    category: TitleReviewCategory
    title: str
    description: str
    priority: str  # "high", "medium", "low"
    impact_score: int  # 0-100, estimated improvement impact
    specific_example: str = ""
    suggested_fix: str = ""


@dataclass
class TitleCategoryScore:
    """Score for a specific title review category."""
    
    category: TitleReviewCategory
    score: int  # 0-100
    reasoning: str
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


@dataclass
class TitleReview:
    """AI-powered title review with scoring and improvement recommendations.
    
    TitleReview provides comprehensive evaluation of titles against script content
    and original idea intent with:
    - Overall quality score (0-100%)
    - Category-specific scores and analysis
    - Prioritized improvement recommendations
    - Script alignment assessment
    - Idea intent verification
    - Audience engagement evaluation
    
    The review serves as input for title improvement iterations, enabling
    refinement based on AI evaluation of title-script-idea alignment.
    
    Attributes:
        title_id: Identifier of the reviewed title
        title_text: The actual title text being reviewed
        title_version: Version number of the title (v1, v2, etc.)
        overall_score: Overall quality score (0-100)
        category_scores: Scores for each evaluation category
        improvement_points: Prioritized list of improvements
        
        Script Context:
            script_id: Identifier of the associated script
            script_title: Title of the script for reference
            script_summary: Brief summary of script content
            script_version: Version of script being reviewed against
            script_alignment_score: How well title matches script (0-100)
            key_script_elements: Key elements from script that title should reflect
            
        Idea Context:
            idea_id: Identifier of the original idea
            idea_summary: Summary of the original idea concept
            idea_intent: Core intent/purpose of the idea
            idea_alignment_score: How well title reflects idea (0-100)
            target_audience: Target audience from idea
            
        Engagement Metrics:
            engagement_score: Predicted engagement level (0-100)
            clickthrough_potential: Estimated CTR potential (0-100)
            curiosity_score: How well title creates curiosity (0-100)
            expectation_accuracy: How well title sets expectations (0-100)
            
        SEO & Optimization:
            seo_score: SEO optimization score (0-100)
            keyword_relevance: Keyword relevance score (0-100)
            suggested_keywords: Keywords that could improve title
            length_score: Title length appropriateness (0-100)
            current_length_chars: Current title character count
            optimal_length_chars: Recommended character count
            
        Review Metadata:
            reviewer_id: AI reviewer identifier
            review_version: Review iteration number
            reviewed_at: Timestamp of review
            confidence_score: AI confidence in evaluation (0-100)
            
        Feedback Loop:
            needs_major_revision: Whether major rewrite needed
            iteration_number: Number of review-improvement iterations
            previous_review_id: ID of previous review (if iterative)
            improvement_trajectory: Score change over iterations
            
        Additional Context:
            strengths: Key strengths of the title
            primary_concern: Main issue to address
            quick_wins: Easy improvements with high impact
            notes: Additional reviewer notes
            metadata: Flexible metadata storage
    
    Example:
        >>> review = TitleReview(
        ...     title_id="title-001",
        ...     title_text="The Echo - A Haunting Discovery",
        ...     title_version="v1",
        ...     overall_score=78,
        ...     script_id="script-001",
        ...     script_title="The Echo",
        ...     script_summary="A horror short about mysterious echoes",
        ...     script_alignment_score=85,
        ...     idea_id="idea-001",
        ...     idea_summary="Horror story about sounds that repeat",
        ...     idea_alignment_score=82,
        ...     target_audience="Horror enthusiasts aged 18-35",
        ...     engagement_score=75,
        ...     clickthrough_potential=72,
        ...     seo_score=68
        ... )
    """
    
    title_id: str
    title_text: str
    title_version: str = "v1"
    overall_score: int = 0  # 0-100
    
    # Category Analysis
    category_scores: List[TitleCategoryScore] = field(default_factory=list)
    improvement_points: List[TitleImprovementPoint] = field(default_factory=list)
    
    # Script Context
    script_id: str = ""
    script_title: str = ""
    script_summary: str = ""
    script_version: str = "v1"
    script_alignment_score: int = 0  # 0-100
    key_script_elements: List[str] = field(default_factory=list)
    
    # Idea Context
    idea_id: str = ""
    idea_summary: str = ""
    idea_intent: str = ""
    idea_alignment_score: int = 0  # 0-100
    target_audience: str = ""
    
    # Engagement Metrics
    engagement_score: int = 0  # 0-100
    clickthrough_potential: int = 0  # 0-100
    curiosity_score: int = 0  # 0-100
    expectation_accuracy: int = 0  # 0-100
    
    # SEO & Optimization
    seo_score: int = 0  # 0-100
    keyword_relevance: int = 0  # 0-100
    suggested_keywords: List[str] = field(default_factory=list)
    length_score: int = 0  # 0-100
    current_length_chars: int = 0
    optimal_length_chars: int = 60  # Default optimal for most platforms
    
    # Review Metadata
    reviewer_id: str = "AI-TitleReviewer-001"
    review_version: int = 1
    reviewed_at: Optional[str] = None
    confidence_score: int = 85  # 0-100, AI confidence
    
    # Feedback Loop
    needs_major_revision: bool = False
    iteration_number: int = 1
    previous_review_id: Optional[str] = None
    improvement_trajectory: List[int] = field(default_factory=list)  # Score history
    
    # Additional Context
    strengths: List[str] = field(default_factory=list)
    primary_concern: str = ""
    quick_wins: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamps and computed fields if not provided."""
        if self.reviewed_at is None:
            self.reviewed_at = datetime.now().isoformat()
        
        # Add current score to trajectory
        if self.overall_score not in self.improvement_trajectory:
            self.improvement_trajectory.append(self.overall_score)
        
        # Auto-calculate current length if not set
        if self.current_length_chars == 0:
            self.current_length_chars = len(self.title_text)
    
    def get_category_score(self, category: TitleReviewCategory) -> Optional[TitleCategoryScore]:
        """Get score for a specific category.
        
        Args:
            category: The review category to retrieve
            
        Returns:
            TitleCategoryScore if found, None otherwise
        """
        for cat_score in self.category_scores:
            if cat_score.category == category:
                return cat_score
        return None
    
    def get_high_priority_improvements(self) -> List[TitleImprovementPoint]:
        """Get high-priority improvement points.
        
        Returns:
            List of high-priority improvements sorted by impact score
        """
        high_priority = [
            imp for imp in self.improvement_points
            if imp.priority == "high"
        ]
        return sorted(high_priority, key=lambda x: x.impact_score, reverse=True)
    
    def get_alignment_summary(self) -> Dict[str, Any]:
        """Get summary of title alignment with script and idea.
        
        Returns:
            Dictionary with alignment metrics and assessment
        """
        avg_alignment = (self.script_alignment_score + self.idea_alignment_score) / 2
        
        alignment_status = "poor"
        if avg_alignment >= 80:
            alignment_status = "excellent"
        elif avg_alignment >= 70:
            alignment_status = "good"
        elif avg_alignment >= 60:
            alignment_status = "fair"
        
        return {
            "script_alignment": self.script_alignment_score,
            "idea_alignment": self.idea_alignment_score,
            "average_alignment": int(avg_alignment),
            "alignment_status": alignment_status,
            "needs_improvement": avg_alignment < 70,
            "key_issues": [
                imp.title for imp in self.get_high_priority_improvements()
                if imp.category in [
                    TitleReviewCategory.SCRIPT_ALIGNMENT,
                    TitleReviewCategory.IDEA_ALIGNMENT
                ]
            ]
        }
    
    def get_engagement_summary(self) -> Dict[str, Any]:
        """Calculate engagement and clickthrough readiness.
        
        Returns:
            Dictionary with engagement metrics
        """
        # Calculate composite engagement score
        composite_engagement = int(
            (self.engagement_score * 0.3) +
            (self.clickthrough_potential * 0.3) +
            (self.curiosity_score * 0.2) +
            (self.expectation_accuracy * 0.2)
        )
        
        ready_for_publication = (
            composite_engagement >= 70 and
            self.expectation_accuracy >= 65 and
            self.overall_score >= 75
        )
        
        return {
            "composite_score": composite_engagement,
            "engagement": self.engagement_score,
            "clickthrough_potential": self.clickthrough_potential,
            "curiosity": self.curiosity_score,
            "expectation_accuracy": self.expectation_accuracy,
            "ready_for_publication": ready_for_publication,
            "recommendations": self.get_high_priority_improvements()[:3]
        }
    
    def get_length_assessment(self) -> Dict[str, Any]:
        """Assess title length and provide feedback.
        
        Returns:
            Dictionary with length assessment
        """
        length_diff = self.current_length_chars - self.optimal_length_chars
        
        status = "optimal"
        if abs(length_diff) <= 5:
            status = "optimal"
        elif abs(length_diff) <= 15:
            status = "acceptable"
        elif length_diff > 0:
            status = "too_long"
        else:
            status = "too_short"
        
        feedback = ""
        if status == "too_long":
            feedback = f"Title is {abs(length_diff)} characters too long. Consider shortening."
        elif status == "too_short":
            feedback = f"Title is {abs(length_diff)} characters too short. Consider expanding."
        else:
            feedback = "Title length is appropriate."
        
        return {
            "current_length": self.current_length_chars,
            "optimal_length": self.optimal_length_chars,
            "difference": length_diff,
            "status": status,
            "feedback": feedback,
            "length_score": self.length_score
        }
    
    def is_ready_for_improvement(self) -> bool:
        """Check if title is ready to move to improvement stage.
        
        Returns:
            True if review is complete and ready for title improvement
        """
        has_feedback = len(self.improvement_points) > 0
        has_scores = len(self.category_scores) > 0
        alignment_assessed = (
            self.script_alignment_score > 0 or
            self.idea_alignment_score > 0
        )
        
        return has_feedback and has_scores and alignment_assessed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TitleReview to dictionary representation.
        
        Returns:
            Dictionary containing all fields with Enums converted to strings
        """
        data = asdict(self)
        
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
    def from_dict(cls, data: Dict[str, Any]) -> "TitleReview":
        """Create TitleReview from dictionary.
        
        Args:
            data: Dictionary containing TitleReview fields
            
        Returns:
            TitleReview instance
        """
        # Convert category scores
        category_scores = []
        for cs_data in data.get("category_scores", []):
            category = TitleReviewCategory(cs_data["category"])
            category_scores.append(TitleCategoryScore(
                category=category,
                score=cs_data["score"],
                reasoning=cs_data["reasoning"],
                strengths=cs_data.get("strengths", []),
                weaknesses=cs_data.get("weaknesses", [])
            ))
        
        # Convert improvement points
        improvement_points = []
        for ip_data in data.get("improvement_points", []):
            category = TitleReviewCategory(ip_data["category"])
            improvement_points.append(TitleImprovementPoint(
                category=category,
                title=ip_data["title"],
                description=ip_data["description"],
                priority=ip_data["priority"],
                impact_score=ip_data["impact_score"],
                specific_example=ip_data.get("specific_example", ""),
                suggested_fix=ip_data.get("suggested_fix", "")
            ))
        
        return cls(
            title_id=data["title_id"],
            title_text=data["title_text"],
            title_version=data.get("title_version", "v1"),
            overall_score=data.get("overall_score", 0),
            category_scores=category_scores,
            improvement_points=improvement_points,
            script_id=data.get("script_id", ""),
            script_title=data.get("script_title", ""),
            script_summary=data.get("script_summary", ""),
            script_version=data.get("script_version", "v1"),
            script_alignment_score=data.get("script_alignment_score", 0),
            key_script_elements=data.get("key_script_elements", []),
            idea_id=data.get("idea_id", ""),
            idea_summary=data.get("idea_summary", ""),
            idea_intent=data.get("idea_intent", ""),
            idea_alignment_score=data.get("idea_alignment_score", 0),
            target_audience=data.get("target_audience", ""),
            engagement_score=data.get("engagement_score", 0),
            clickthrough_potential=data.get("clickthrough_potential", 0),
            curiosity_score=data.get("curiosity_score", 0),
            expectation_accuracy=data.get("expectation_accuracy", 0),
            seo_score=data.get("seo_score", 0),
            keyword_relevance=data.get("keyword_relevance", 0),
            suggested_keywords=data.get("suggested_keywords", []),
            length_score=data.get("length_score", 0),
            current_length_chars=data.get("current_length_chars", 0),
            optimal_length_chars=data.get("optimal_length_chars", 60),
            reviewer_id=data.get("reviewer_id", "AI-TitleReviewer-001"),
            review_version=data.get("review_version", 1),
            reviewed_at=data.get("reviewed_at"),
            confidence_score=data.get("confidence_score", 85),
            needs_major_revision=data.get("needs_major_revision", False),
            iteration_number=data.get("iteration_number", 1),
            previous_review_id=data.get("previous_review_id"),
            improvement_trajectory=data.get("improvement_trajectory", []),
            strengths=data.get("strengths", []),
            primary_concern=data.get("primary_concern", ""),
            quick_wins=data.get("quick_wins", []),
            notes=data.get("notes", ""),
            metadata=data.get("metadata", {})
        )
    
    def __repr__(self) -> str:
        """String representation of TitleReview."""
        return (
            f"TitleReview(title='{self.title_text}', "
            f"score={self.overall_score}%, "
            f"iteration={self.iteration_number}, "
            f"script_align={self.script_alignment_score}%, "
            f"idea_align={self.idea_alignment_score}%)"
        )
