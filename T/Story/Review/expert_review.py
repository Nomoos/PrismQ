"""PrismQ.T.Story.Review - GPT-Based Expert Story Review

AI-powered expert-level review of complete story using GPT (Stage 21 / MVP-021).
Provides holistic assessment of title + script + audience context after all local
AI reviews have passed.

This module serves as a quality gate in the workflow:
- If READY FOR PUBLISHING: proceed to Stage 23 (Publishing)
- If NEEDS POLISH: proceed to Stage 22 (Polish) with improvement suggestions
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ComponentType(Enum):
    """Type of component for improvement suggestions."""

    TITLE = "title"
    SCRIPT = "script"
    BOTH = "both"


class Priority(Enum):
    """Priority level for improvement suggestions."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EffortLevel(Enum):
    """Estimated effort for implementing improvement."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class AlignmentLevel(Enum):
    """Alignment level between title and script."""

    PERFECT = "perfect"
    GOOD = "good"
    NEEDS_WORK = "needs_work"


class MatchLevel(Enum):
    """Match level for audience fit."""

    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_WORK = "needs_work"


class ReviewDecision(Enum):
    """Final decision from expert review."""

    PUBLISH = "publish"
    POLISH = "polish"


@dataclass
class ImprovementSuggestion:
    """Represents a specific improvement suggestion from expert review."""

    component: ComponentType
    priority: Priority
    suggestion: str
    impact: str
    estimated_effort: EffortLevel

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "component": self.component.value,
            "priority": self.priority.value,
            "suggestion": self.suggestion,
            "impact": self.impact,
            "estimated_effort": self.estimated_effort.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImprovementSuggestion":
        """Create from dictionary representation."""
        return cls(
            component=ComponentType(data["component"]),
            priority=Priority(data["priority"]),
            suggestion=data["suggestion"],
            impact=data["impact"],
            estimated_effort=EffortLevel(data["estimated_effort"]),
        )


@dataclass
class OverallAssessment:
    """Overall assessment of the story."""

    ready_for_publishing: bool
    quality_score: int  # 0-100
    confidence: int  # 0-100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "ready_for_publishing": self.ready_for_publishing,
            "quality_score": self.quality_score,
            "confidence": self.confidence,
        }


@dataclass
class StoryCoherence:
    """Assessment of story coherence and title-script alignment."""

    score: int  # 0-100
    feedback: str
    title_script_alignment: AlignmentLevel

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "score": self.score,
            "feedback": self.feedback,
            "title_script_alignment": self.title_script_alignment.value,
        }


@dataclass
class AudienceFit:
    """Assessment of fit for target audience."""

    score: int  # 0-100
    feedback: str
    demographic_match: MatchLevel

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "score": self.score,
            "feedback": self.feedback,
            "demographic_match": self.demographic_match.value,
        }


@dataclass
class ProfessionalQuality:
    """Assessment of professional production quality."""

    score: int  # 0-100
    feedback: str
    production_ready: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "score": self.score,
            "feedback": self.feedback,
            "production_ready": self.production_ready,
        }


@dataclass
class PlatformOptimization:
    """Assessment of platform-specific optimization."""

    score: int  # 0-100
    feedback: str
    platform_perfect: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "score": self.score,
            "feedback": self.feedback,
            "platform_perfect": self.platform_perfect,
        }


@dataclass
class ExpertReview:
    """Complete expert review of story (title + script + audience context)."""

    # Metadata
    story_id: str
    story_version: str
    reviewer_id: str = "GPT-ExpertReviewer-001"
    reviewed_at: datetime = field(default_factory=datetime.now)

    # Assessment components
    overall_assessment: Optional[OverallAssessment] = None
    story_coherence: Optional[StoryCoherence] = None
    audience_fit: Optional[AudienceFit] = None
    professional_quality: Optional[ProfessionalQuality] = None
    platform_optimization: Optional[PlatformOptimization] = None

    # Improvement suggestions
    improvement_suggestions: List[ImprovementSuggestion] = field(default_factory=list)

    # Decision
    decision: Optional[ReviewDecision] = None

    # Review context (inputs)
    title: str = ""
    script: str = ""
    audience_context: Dict[str, Any] = field(default_factory=dict)
    original_idea: str = ""
    local_review_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert review to dictionary representation."""
        result = {
            "story_id": self.story_id,
            "story_version": self.story_version,
            "reviewer_id": self.reviewer_id,
            "reviewed_at": self.reviewed_at.isoformat(),
            "title": self.title,
            "script": self.script,
            "audience_context": self.audience_context,
            "original_idea": self.original_idea,
            "local_review_summary": self.local_review_summary,
        }

        if self.overall_assessment:
            result["overall_assessment"] = self.overall_assessment.to_dict()

        if self.story_coherence:
            result["story_coherence"] = self.story_coherence.to_dict()

        if self.audience_fit:
            result["audience_fit"] = self.audience_fit.to_dict()

        if self.professional_quality:
            result["professional_quality"] = self.professional_quality.to_dict()

        if self.platform_optimization:
            result["platform_optimization"] = self.platform_optimization.to_dict()

        result["improvement_suggestions"] = [
            suggestion.to_dict() for suggestion in self.improvement_suggestions
        ]

        if self.decision:
            result["decision"] = self.decision.value

        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert review to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def get_high_priority_suggestions(self) -> List[ImprovementSuggestion]:
        """Get only high-priority improvement suggestions."""
        return [s for s in self.improvement_suggestions if s.priority == Priority.HIGH]

    def get_small_effort_suggestions(self) -> List[ImprovementSuggestion]:
        """Get improvement suggestions that require small effort."""
        return [s for s in self.improvement_suggestions if s.estimated_effort == EffortLevel.SMALL]

    def get_suggestions_by_component(self, component: ComponentType) -> List[ImprovementSuggestion]:
        """Get improvement suggestions for a specific component."""
        return [s for s in self.improvement_suggestions if s.component == component]


class StoryExpertReviewer:
    """Expert reviewer for complete stories using GPT."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gpt-4", publish_threshold: int = 95
    ):
        """Initialize expert reviewer.

        Args:
            api_key: OpenAI API key (optional, will use environment variable if not provided)
            model: GPT model to use (gpt-4 or gpt-4-turbo or gpt-3.5-turbo for testing)
            publish_threshold: Minimum quality score to recommend publishing without polish
        """
        self.api_key = api_key
        self.model = model
        self.publish_threshold = publish_threshold

    def review_story(
        self,
        title: str,
        script: str,
        audience_context: Dict[str, Any],
        original_idea: str = "",
        story_id: str = "story-001",
        story_version: str = "v3",
        local_review_summary: Optional[Dict[str, Any]] = None,
    ) -> ExpertReview:
        """Perform expert review of complete story.

        Args:
            title: Final title after all local reviews
            script: Final script after all local reviews
            audience_context: Target demographic, platform, style info
            original_idea: Original idea for intent verification
            story_id: Identifier for the story
            story_version: Version of the story
            local_review_summary: Summary of all local review results

        Returns:
            ExpertReview object with complete assessment
        """
        # Create review object
        review = ExpertReview(
            story_id=story_id,
            story_version=story_version,
            title=title,
            script=script,
            audience_context=audience_context,
            original_idea=original_idea,
            local_review_summary=local_review_summary or {},
        )

        # In a real implementation, this would call GPT API
        # For now, we'll provide a simulated expert review
        review = self._simulate_expert_review(review)

        return review

    def _simulate_expert_review(self, review: ExpertReview) -> ExpertReview:
        """Simulate expert review (placeholder for actual GPT integration).

        This is a simplified simulation. Real implementation would:
        1. Construct expert prompt with story context
        2. Call GPT API with structured output format
        3. Parse and validate GPT response
        4. Populate review object with results

        Args:
            review: Review object to populate

        Returns:
            Populated review object
        """
        # Simulate quality scores based on content length and structure
        title_length = len(review.title)
        script_length = len(review.script)
        has_audience = bool(review.audience_context)
        has_idea = bool(review.original_idea)

        # Calculate simulated scores
        base_score = 85
        if title_length > 10 and title_length < 100:
            base_score += 2
        if script_length > 200:
            base_score += 3
        if has_audience:
            base_score += 3
        if has_idea:
            base_score += 2

        quality_score = min(95, base_score)

        # Overall assessment
        review.overall_assessment = OverallAssessment(
            ready_for_publishing=(quality_score >= self.publish_threshold),
            quality_score=quality_score,
            confidence=90,
        )

        # Story coherence
        review.story_coherence = StoryCoherence(
            score=quality_score,
            feedback="Title and script align well. Story flows coherently from beginning to end.",
            title_script_alignment=(
                AlignmentLevel.GOOD if quality_score >= 90 else AlignmentLevel.NEEDS_WORK
            ),
        )

        # Audience fit
        review.audience_fit = AudienceFit(
            score=quality_score - 2,
            feedback="Content is appropriate for target demographic. Tone matches audience expectations.",
            demographic_match=MatchLevel.GOOD if quality_score >= 90 else MatchLevel.NEEDS_WORK,
        )

        # Professional quality
        review.professional_quality = ProfessionalQuality(
            score=quality_score - 3,
            feedback="Production quality meets professional standards. Script is ready for production.",
            production_ready=(quality_score >= self.publish_threshold),
        )

        # Platform optimization
        review.platform_optimization = PlatformOptimization(
            score=quality_score - 1,
            feedback="Content is well-optimized for target platform. Length and pacing are appropriate.",
            platform_perfect=(quality_score >= self.publish_threshold),
        )

        # Add improvement suggestions if score is below publish threshold
        if quality_score < self.publish_threshold:
            review.improvement_suggestions = [
                ImprovementSuggestion(
                    component=ComponentType.SCRIPT,
                    priority=Priority.HIGH,
                    suggestion="Enhance opening hook to immediately capture audience attention",
                    impact="Improves viewer retention in first 3 seconds",
                    estimated_effort=EffortLevel.SMALL,
                ),
                ImprovementSuggestion(
                    component=ComponentType.TITLE,
                    priority=Priority.MEDIUM,
                    suggestion="Consider making title more specific and intriguing",
                    impact="Increases click-through rate",
                    estimated_effort=EffortLevel.SMALL,
                ),
            ]

        # Make decision
        review.decision = (
            ReviewDecision.PUBLISH
            if quality_score >= self.publish_threshold
            else ReviewDecision.POLISH
        )

        return review


def review_story_with_gpt(
    title: str,
    script: str,
    audience_context: Dict[str, Any],
    original_idea: str = "",
    story_id: str = "story-001",
    story_version: str = "v3",
    local_review_summary: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    model: str = "gpt-4",
    publish_threshold: int = 95,
) -> ExpertReview:
    """Convenience function to perform expert story review.

    Args:
        title: Final title after all local reviews
        script: Final script after all local reviews
        audience_context: Target demographic, platform, style info
        original_idea: Original idea for intent verification
        story_id: Identifier for the story
        story_version: Version of the story
        local_review_summary: Summary of all local review results
        api_key: OpenAI API key (optional)
        model: GPT model to use
        publish_threshold: Minimum score to recommend publishing

    Returns:
        ExpertReview object with complete assessment

    Example:
        >>> review = review_story_with_gpt(
        ...     title="The House That Remembers",
        ...     script="A young woman explores an abandoned house...",
        ...     audience_context={"demographic": "US female 14-29", "platform": "YouTube shorts"},
        ...     original_idea="Horror story about time loops"
        ... )
        >>> print(f"Quality Score: {review.overall_assessment.quality_score}")
        >>> print(f"Decision: {review.decision.value}")
        >>> if review.decision == ReviewDecision.POLISH:
        ...     for suggestion in review.get_high_priority_suggestions():
        ...         print(f"- {suggestion.suggestion}")
    """
    reviewer = StoryExpertReviewer(
        api_key=api_key, model=model, publish_threshold=publish_threshold
    )
    return reviewer.review_story(
        title=title,
        script=script,
        audience_context=audience_context,
        original_idea=original_idea,
        story_id=story_id,
        story_version=story_version,
        local_review_summary=local_review_summary,
    )


def review_story_to_json(
    title: str,
    script: str,
    audience_context: Dict[str, Any],
    original_idea: str = "",
    story_id: str = "story-001",
    story_version: str = "v3",
    local_review_summary: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    model: str = "gpt-4",
    publish_threshold: int = 95,
) -> str:
    """Perform expert story review and return results as JSON string.

    Args:
        title: Final title after all local reviews
        script: Final script after all local reviews
        audience_context: Target demographic, platform, style info
        original_idea: Original idea for intent verification
        story_id: Identifier for the story
        story_version: Version of the story
        local_review_summary: Summary of all local review results
        api_key: OpenAI API key (optional)
        model: GPT model to use
        publish_threshold: Minimum score to recommend publishing

    Returns:
        JSON string containing the expert review results

    Example:
        >>> json_result = review_story_to_json(
        ...     title="The House That Remembers",
        ...     script="A young woman explores...",
        ...     audience_context={"demographic": "US female 14-29"}
        ... )
        >>> result = json.loads(json_result)
        >>> print(result['overall_assessment']['quality_score'])
        >>> print(result['decision'])
    """
    review = review_story_with_gpt(
        title=title,
        script=script,
        audience_context=audience_context,
        original_idea=original_idea,
        story_id=story_id,
        story_version=story_version,
        local_review_summary=local_review_summary,
        api_key=api_key,
        model=model,
        publish_threshold=publish_threshold,
    )
    return review.to_json()


def get_expert_feedback(review: ExpertReview) -> Dict[str, Any]:
    """Get formatted feedback from expert review for workflow decision.

    Args:
        review: ExpertReview object

    Returns:
        Dictionary with structured feedback for workflow coordination

    Example:
        >>> review = review_story_with_gpt(title, script, audience_context)
        >>> feedback = get_expert_feedback(review)
        >>> if feedback['decision'] == 'polish':
        ...     print("Sending to Polish with suggestions:")
        ...     for suggestion in feedback['high_priority_suggestions']:
        ...         print(f"  - {suggestion['suggestion']}")
        ... else:
        ...     print("Ready for publishing!")
    """
    return {
        "story_id": review.story_id,
        "story_version": review.story_version,
        "decision": review.decision.value if review.decision else "unknown",
        "quality_score": (
            review.overall_assessment.quality_score if review.overall_assessment else 0
        ),
        "ready_for_publishing": (
            review.overall_assessment.ready_for_publishing if review.overall_assessment else False
        ),
        "overall_assessment": (
            review.overall_assessment.to_dict() if review.overall_assessment else {}
        ),
        "story_coherence": (review.story_coherence.to_dict() if review.story_coherence else {}),
        "audience_fit": (review.audience_fit.to_dict() if review.audience_fit else {}),
        "professional_quality": (
            review.professional_quality.to_dict() if review.professional_quality else {}
        ),
        "platform_optimization": (
            review.platform_optimization.to_dict() if review.platform_optimization else {}
        ),
        "total_suggestions": len(review.improvement_suggestions),
        "high_priority_suggestions": [
            suggestion.to_dict() for suggestion in review.get_high_priority_suggestions()
        ],
        "small_effort_suggestions": [
            suggestion.to_dict() for suggestion in review.get_small_effort_suggestions()
        ],
        "next_action": (
            "Proceed to Stage 23 (Publishing.Finalization)"
            if review.decision == ReviewDecision.PUBLISH
            else "Proceed to Stage 22 (Story.Polish) with improvement suggestions"
        ),
    }


if __name__ == "__main__":
    # Example usage
    test_title = "The House That Remembers: and Hunts"
    test_script = """We've all driven past abandoned houses and wondered about their stories.
    
But what if the house remembered too?

Sarah inherits an old Victorian mansion from an aunt she never met.
The moment she steps inside, she feels it - a presence, watching, waiting.

At night, she hears whispers through the walls.
Names. Dates. Secrets.
The house is remembering.

She discovers old photographs in the attic.
In each one, the same figure appears in the background.
A woman in white. Her aunt.

The whispers grow louder.
"Leave now. Before you become part of the memory."

Sarah realizes the horrifying truth:
The house doesn't just remember its residents.
It keeps them.

Forever."""

    test_audience = {
        "demographic": "US female 14-29",
        "platform": "YouTube shorts",
        "style": "atmospheric horror",
        "duration": "60 seconds",
    }

    test_idea = "A horror story about a house with supernatural memory that traps its residents"

    print("=== Expert Story Review ===\n")
    print(f"Title: {test_title}")
    print(f"\nScript:\n{test_script}")
    print(f"\nAudience: {test_audience}")
    print("\n" + "=" * 70 + "\n")

    review = review_story_with_gpt(
        title=test_title,
        script=test_script,
        audience_context=test_audience,
        original_idea=test_idea,
        story_id="test-001",
        story_version="v3",
        publish_threshold=95,
    )

    print(f"Quality Score: {review.overall_assessment.quality_score}/100")
    print(f"Confidence: {review.overall_assessment.confidence}%")
    print(f"Ready for Publishing: {review.overall_assessment.ready_for_publishing}")
    print(f"Decision: {review.decision.value.upper()}")
    print(f"\nStory Coherence: {review.story_coherence.score}/100")
    print(f"  - {review.story_coherence.feedback}")
    print(f"\nAudience Fit: {review.audience_fit.score}/100")
    print(f"  - {review.audience_fit.feedback}")
    print(f"\nProfessional Quality: {review.professional_quality.score}/100")
    print(f"  - Production Ready: {review.professional_quality.production_ready}")
    print(f"\nPlatform Optimization: {review.platform_optimization.score}/100")
    print(f"  - Platform Perfect: {review.platform_optimization.platform_perfect}")

    if review.improvement_suggestions:
        print(f"\n{'='*70}")
        print(f"Improvement Suggestions ({len(review.improvement_suggestions)}):\n")
        for i, suggestion in enumerate(review.improvement_suggestions, 1):
            print(
                f"{i}. [{suggestion.priority.value.upper()}] {suggestion.component.value.upper()}"
            )
            print(f"   Suggestion: {suggestion.suggestion}")
            print(f"   Impact: {suggestion.impact}")
            print(f"   Effort: {suggestion.estimated_effort.value}")
            print()

    print("=" * 70)
    print("\nWorkflow Feedback:")
    feedback = get_expert_feedback(review)
    print(f"Next Action: {feedback['next_action']}")

    print("\n" + "=" * 70)
    print("\nJSON Output (first 800 chars):")
    json_output = review.to_json()
    print(json_output[:800] + "...")
