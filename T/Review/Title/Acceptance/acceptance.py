"""Title Acceptance Gate for PrismQ MVP workflow.

This module implements the acceptance gate for titles in the iterative
co-improvement workflow. The acceptance gate determines whether a title
(at any version - v3, v4, v5, etc.) is ready to proceed to the script
acceptance stage or needs further refinement.

The acceptance gate evaluates:
- Clarity: Title is clear and understandable
- Engagement: Title is compelling and attention-grabbing
- Alignment with script: Title accurately reflects script content

Workflow Position:
    Title (vN) + Script (vN) → Acceptance Gate (MVP-012) → {
        ACCEPTED: Proceed to Script Acceptance (MVP-013)
        NOT ACCEPTED: Loop back to Title Review (MVP-008) → Title Refinement → v(N+1)
    }

Stage 12 in the MVP workflow (Acceptance Gates).
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from enum import Enum


class AcceptanceCriteria(Enum):
    """Criteria for title acceptance evaluation."""
    
    CLARITY = "clarity"
    ENGAGEMENT = "engagement"
    SCRIPT_ALIGNMENT = "script_alignment"


@dataclass
class AcceptanceCriterionResult:
    """Result for a single acceptance criterion."""
    
    criterion: AcceptanceCriteria
    score: int  # 0-100
    passed: bool
    reasoning: str
    threshold: int = 70


@dataclass
class TitleAcceptanceResult:
    """Result of title acceptance gate evaluation.
    
    The acceptance result determines whether the title is ready to proceed
    to the next stage (script acceptance) or needs further refinement.
    
    Attributes:
        title_text: The title being evaluated
        title_version: Version of the title (v3, v4, v5, etc.)
        accepted: Whether the title passes the acceptance gate
        overall_score: Overall acceptance score (0-100)
        reason: Primary reason for acceptance or rejection
        criteria_results: Detailed results for each criterion
        script_version: Version of the script being evaluated against
        script_summary: Brief summary of script content
        recommendations: Recommendations if not accepted
        timestamp: When the evaluation was performed
        metadata: Additional metadata
    
    Example:
        >>> result = TitleAcceptanceResult(
        ...     title_text="The Echo Mystery Unveiled",
        ...     title_version="v3",
        ...     accepted=True,
        ...     overall_score=85,
        ...     reason="Title meets all acceptance criteria",
        ...     criteria_results=[...],
        ...     script_version="v3"
        ... )
    """
    
    title_text: str
    title_version: str
    accepted: bool
    overall_score: int  # 0-100
    reason: str
    criteria_results: List[AcceptanceCriterionResult]
    script_version: str = ""
    script_summary: str = ""
    recommendations: List[str] = None
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.recommendations is None:
            self.recommendations = []
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary containing all fields with Enums converted to strings
        """
        data = asdict(self)
        data["criteria_results"] = [
            {
                **asdict(cr),
                "criterion": cr.criterion.value
            }
            for cr in self.criteria_results
        ]
        return data
    
    def get_criterion_result(self, criterion: AcceptanceCriteria) -> Optional[AcceptanceCriterionResult]:
        """Get result for a specific criterion.
        
        Args:
            criterion: The criterion to retrieve
            
        Returns:
            AcceptanceCriterionResult if found, None otherwise
        """
        for cr in self.criteria_results:
            if cr.criterion == criterion:
                return cr
        return None
    
    def __repr__(self) -> str:
        """String representation of acceptance result."""
        status = "ACCEPTED" if self.accepted else "NOT ACCEPTED"
        return (
            f"TitleAcceptanceResult(title='{self.title_text}', "
            f"version={self.title_version}, "
            f"status={status}, "
            f"score={self.overall_score}%)"
        )


# Acceptance thresholds
CLARITY_THRESHOLD = 70  # Minimum clarity score to pass
ENGAGEMENT_THRESHOLD = 70  # Minimum engagement score to pass
ALIGNMENT_THRESHOLD = 75  # Minimum alignment score to pass
OVERALL_THRESHOLD = 75  # Minimum overall score to accept


def evaluate_clarity(title_text: str) -> AcceptanceCriterionResult:
    """Evaluate title clarity.
    
    Clarity assessment includes:
    - Title length appropriateness
    - Word choice simplicity
    - Structure and grammar
    - Absence of ambiguity
    
    Args:
        title_text: The title to evaluate
        
    Returns:
        AcceptanceCriterionResult with clarity score and reasoning
    """
    score = 100
    issues = []
    
    # Check length (optimal: 30-75 characters)
    length = len(title_text)
    if length < 20:
        score -= 20
        issues.append("Title is too short (< 20 chars)")
    elif length < 30:
        score -= 10
        issues.append("Title is somewhat short")
    elif length > 100:
        score -= 25
        issues.append("Title is too long (> 100 chars)")
    elif length > 75:
        score -= 10
        issues.append("Title is slightly long")
    
    # Check for empty or whitespace-only title
    if not title_text or not title_text.strip():
        score = 0
        issues.append("Title is empty or whitespace only")
    
    # Check for excessive punctuation
    punct_count = sum(1 for c in title_text if c in '!?.:;,-')
    if punct_count > len(title_text) * 0.2:
        score -= 15
        issues.append("Excessive punctuation may reduce clarity")
    
    # Check for unclear patterns (multiple consecutive punctuation)
    import re
    if re.search(r'[!?]{3,}', title_text):
        score -= 10
        issues.append("Multiple exclamation/question marks reduce clarity")
    
    # Check for all caps (generally less clear)
    if title_text.isupper() and len(title_text) > 10:
        score -= 15
        issues.append("All caps format may reduce readability")
    
    # Check for unclear abbreviations or excessive acronyms
    words = title_text.split()
    acronym_count = sum(1 for w in words if w.isupper() and len(w) > 1)
    if acronym_count > 2:
        score -= 10
        issues.append("Multiple acronyms may reduce clarity")
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    passed = score >= CLARITY_THRESHOLD
    
    if issues:
        reasoning = "Clarity issues found: " + "; ".join(issues)
    else:
        reasoning = "Title is clear and well-structured"
    
    return AcceptanceCriterionResult(
        criterion=AcceptanceCriteria.CLARITY,
        score=score,
        passed=passed,
        reasoning=reasoning,
        threshold=CLARITY_THRESHOLD
    )


def evaluate_engagement(title_text: str, script_summary: str = "") -> AcceptanceCriterionResult:
    """Evaluate title engagement potential.
    
    Engagement assessment includes:
    - Curiosity generation
    - Emotional resonance
    - Use of compelling words
    - Question or intrigue elements
    
    Args:
        title_text: The title to evaluate
        script_summary: Optional script summary for context
        
    Returns:
        AcceptanceCriterionResult with engagement score and reasoning
    """
    score = 70  # Start with a baseline
    
    # Engagement boosters
    engaging_words = [
        'mystery', 'secret', 'hidden', 'revealed', 'shocking', 'amazing',
        'incredible', 'unbelievable', 'discover', 'reveal', 'truth',
        'untold', 'forbidden', 'haunting', 'dark', 'epic', 'ultimate'
    ]
    
    title_lower = title_text.lower()
    
    # Check for engaging words
    found_engaging = [w for w in engaging_words if w in title_lower]
    if found_engaging:
        score += min(15, len(found_engaging) * 5)
    
    # Check for question format (inherently engaging)
    if '?' in title_text:
        score += 10
    
    # Check for numbers (often engaging)
    import re
    if re.search(r'\d+', title_text):
        score += 5
    
    # Check for colon structure (often used for intrigue)
    if ':' in title_text:
        parts = title_text.split(':')
        if len(parts) == 2 and len(parts[0].strip()) > 0 and len(parts[1].strip()) > 0:
            score += 5
    
    # Penalize generic or boring titles
    boring_patterns = ['a story', 'the story', 'a tale', 'something']
    if any(pattern in title_lower for pattern in boring_patterns):
        score -= 10
    
    # Penalize overly simple titles (single word, very short)
    words = title_text.split()
    if len(words) == 1 and len(title_text) < 10:
        score -= 15
    elif len(words) == 2 and len(title_text) < 15:
        score -= 10
    
    # Check for emotional words
    emotional_words = ['fear', 'love', 'hope', 'terror', 'joy', 'pain', 'death', 'life']
    if any(w in title_lower for w in emotional_words):
        score += 5
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    passed = score >= ENGAGEMENT_THRESHOLD
    
    if passed:
        reasoning = f"Title is engaging (found: {', '.join(found_engaging) if found_engaging else 'compelling structure'})"
    else:
        reasoning = "Title needs more engaging elements to capture audience attention"
    
    return AcceptanceCriterionResult(
        criterion=AcceptanceCriteria.ENGAGEMENT,
        score=score,
        passed=passed,
        reasoning=reasoning,
        threshold=ENGAGEMENT_THRESHOLD
    )


def evaluate_script_alignment(
    title_text: str,
    script_text: str,
    script_summary: str = ""
) -> AcceptanceCriterionResult:
    """Evaluate title-script alignment.
    
    Alignment assessment includes:
    - Key words from script appear in title
    - Title theme matches script theme
    - Title accurately represents script content
    - Title sets appropriate expectations
    
    Args:
        title_text: The title to evaluate
        script_text: The script content
        script_summary: Optional script summary
        
    Returns:
        AcceptanceCriterionResult with alignment score and reasoning
    """
    score = 75  # Start with a baseline
    
    # Extract keywords from title and script
    import re
    
    # Common stopwords to ignore
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # Extract title keywords
    title_words = set(
        word.lower() 
        for word in re.findall(r'\b\w+\b', title_text)
        if word.lower() not in stopwords and len(word) > 2
    )
    
    # Extract script keywords
    script_words = set(
        word.lower()
        for word in re.findall(r'\b\w+\b', script_text)
        if word.lower() not in stopwords and len(word) > 2
    )
    
    # Calculate keyword overlap
    common_keywords = title_words & script_words
    if len(title_words) > 0:
        overlap_ratio = len(common_keywords) / len(title_words)
    else:
        overlap_ratio = 0
    
    # Score based on overlap
    if overlap_ratio >= 0.5:
        score += 15
    elif overlap_ratio >= 0.3:
        score += 10
    elif overlap_ratio >= 0.15:
        score += 5
    else:
        score -= 10
    
    # Check if script is empty or too short
    if len(script_text.strip()) < 50:
        score = 60  # Default score for minimal script
    
    # Penalize if no keywords match at all
    if len(common_keywords) == 0 and len(title_words) > 0 and len(script_text.strip()) > 50:
        score -= 20
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    passed = score >= ALIGNMENT_THRESHOLD
    
    if passed:
        reasoning = f"Title aligns well with script ({len(common_keywords)} key words match: {', '.join(list(common_keywords)[:3])})"
    else:
        reasoning = f"Title-script alignment needs improvement (only {len(common_keywords)} key words match)"
    
    return AcceptanceCriterionResult(
        criterion=AcceptanceCriteria.SCRIPT_ALIGNMENT,
        score=score,
        passed=passed,
        reasoning=reasoning,
        threshold=ALIGNMENT_THRESHOLD
    )


def check_title_acceptance(
    title_text: str,
    title_version: str = "v3",
    script_text: str = "",
    script_version: str = "v3",
    script_summary: str = ""
) -> TitleAcceptanceResult:
    """Check if title meets acceptance criteria for MVP-012.
    
    This is the main acceptance gate function that evaluates whether a title
    (at any version) is ready to proceed to script acceptance or needs
    further refinement.
    
    Acceptance requires:
    - Clarity score >= 70
    - Engagement score >= 70
    - Script alignment score >= 75
    - Overall score >= 75
    
    Args:
        title_text: The title to evaluate
        title_version: Version of the title (e.g., "v3", "v4")
        script_text: The script content to evaluate against
        script_version: Version of the script
        script_summary: Brief summary of script content
        
    Returns:
        TitleAcceptanceResult indicating acceptance status and detailed feedback
        
    Example:
        >>> result = check_title_acceptance(
        ...     title_text="The Echo Mystery: Dark Secrets Revealed",
        ...     title_version="v3",
        ...     script_text="A mysterious echo in an old house reveals dark secrets...",
        ...     script_version="v3"
        ... )
        >>> print(result.accepted)  # True or False
        >>> print(result.reason)  # Explanation
    """
    # Evaluate each criterion
    clarity_result = evaluate_clarity(title_text)
    engagement_result = evaluate_engagement(title_text, script_summary)
    alignment_result = evaluate_script_alignment(title_text, script_text, script_summary)
    
    criteria_results = [
        clarity_result,
        engagement_result,
        alignment_result
    ]
    
    # Calculate overall score (weighted average)
    overall_score = int(
        clarity_result.score * 0.30 +
        engagement_result.score * 0.30 +
        alignment_result.score * 0.40
    )
    
    # Determine acceptance
    all_criteria_passed = all(cr.passed for cr in criteria_results)
    overall_passed = overall_score >= OVERALL_THRESHOLD
    accepted = all_criteria_passed and overall_passed
    
    # Generate reason and recommendations
    if accepted:
        reason = "Title meets all acceptance criteria and is ready to proceed to script acceptance"
        recommendations = []
    else:
        failed_criteria = [cr for cr in criteria_results if not cr.passed]
        if failed_criteria:
            criteria_names = ", ".join(cr.criterion.value for cr in failed_criteria)
            reason = f"Title does not meet acceptance criteria: {criteria_names}"
            recommendations = [
                f"Improve {cr.criterion.value}: {cr.reasoning}"
                for cr in failed_criteria
            ]
        else:
            reason = f"Overall score ({overall_score}) is below threshold ({OVERALL_THRESHOLD})"
            recommendations = [
                "Enhance overall quality across all criteria",
                "Consider refinement to improve clarity, engagement, and alignment"
            ]
    
    return TitleAcceptanceResult(
        title_text=title_text,
        title_version=title_version,
        accepted=accepted,
        overall_score=overall_score,
        reason=reason,
        criteria_results=criteria_results,
        script_version=script_version,
        script_summary=script_summary,
        recommendations=recommendations
    )
