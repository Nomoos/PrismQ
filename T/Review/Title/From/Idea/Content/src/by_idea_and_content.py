"""Review title v1 against idea and content v1.

This module implements the AI-powered title review function that evaluates
how well a title aligns with the core idea and the content it's based on.

The reviewer provides:
- Title-idea alignment assessment
- Title-content alignment assessment
- Engagement and clarity scoring
- Actionable improvement recommendations
- Structured JSON-compatible feedback

Workflow Position:
    Idea + Title v1 + Content v1 → Review → TitleReview Feedback → Title v2
"""

import hashlib
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# Configure module logger
logger = logging.getLogger(__name__)

from .title_review import (
    TitleCategoryScore,
    TitleImprovementPoint,
    TitleReview,
    TitleReviewCategory,
)

# Use TYPE_CHECKING to avoid runtime import issues
if TYPE_CHECKING:
    from T.Idea.Model.src.idea import Idea
    from T.Content.FromIdeaAndTitle.src.script_generator import ScriptV1
else:
    # At runtime, we'll accept any object with the right attributes
    Idea = Any
    ScriptV1 = Any


# Constants for analysis
COMMON_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "from",
    "by",
    "as",
    "is",
    "was",
    "are",
    "be",
    "been",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "should",
    "could",
    "may",
    "might",
    "can",
    "this",
    "that",
    "these",
    "those",
    "it",
}

# Emotional impact words for engagement scoring
ENGAGEMENT_WORDS = [
    "mystery",
    "discover",
    "reveal",
    "secret",
    "hidden",
    "shocking",
    "amazing",
    "unbelievable",
    "terrifying",
    "haunting",
    "surprising",
    "incredible",
    "ultimate",
    "powerful",
    "deadly",
    "forbidden",
    "lost",
    "forgotten",
]

# Words that may set unrealistic expectations
MISLEADING_WORDS = ["ultimate", "best", "perfect", "guaranteed"]

# SEO-friendly patterns
SEO_PATTERNS = {
    "question": r"\b(how|what|why|when|where|who)\b",
    "number": r"\b\d+\b",
    "action": r"\b(guide|tips|ways|methods|steps|secrets)\b",
}

# Content analysis constants
SCRIPT_INTRO_PERCENTAGE = 0.2  # First 20% of script considered as introduction
DEFAULT_SCRIPT_SUMMARY_LENGTH = 200  # Characters for auto-generated summary

# Input validation constants
MAX_TITLE_LENGTH = 200  # Maximum title length in characters
MAX_IDEA_LENGTH = 5000  # Maximum idea summary length
MAX_CONTENT_LENGTH = 100000  # Maximum content length (100KB)
MIN_TEXT_LENGTH = 1  # Minimum text length


def _safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: The numerator value
        denominator: The denominator value
        default: Default value to return if denominator is zero
        
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError) as e:
        logger.warning(f"Division error: {e}, returning default {default}")
        return default


def _sanitize_text_input(text: str, max_length: int, field_name: str = "text") -> str:
    """Sanitize text input by removing dangerous characters and normalizing.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        field_name: Name of field for error messages
        
    Returns:
        Sanitized text
        
    Raises:
        ValueError: If text is too long after sanitization
    """
    if not isinstance(text, str):
        raise TypeError(f"{field_name} must be a string, got {type(text).__name__}")
    
    # Remove null bytes (security risk)
    text = text.replace('\x00', '')
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Check length after sanitization
    if len(text) > max_length:
        raise ValueError(
            f"{field_name} exceeds maximum length of {max_length} characters "
            f"(got {len(text)} characters)"
        )
    
    return text


def _validate_text_input(
    text: str, 
    min_length: int, 
    max_length: int, 
    field_name: str = "text"
) -> None:
    """Validate text input parameters.
    
    Args:
        text: Text to validate
        min_length: Minimum required length
        max_length: Maximum allowed length
        field_name: Name of field for error messages
        
    Raises:
        TypeError: If text is not a string
        ValueError: If text is empty, too short, or too long
    """
    if not isinstance(text, str):
        raise TypeError(f"{field_name} must be a string, got {type(text).__name__}")
    
    if not text or not text.strip():
        raise ValueError(f"{field_name} cannot be empty")
    
    text_len = len(text.strip())
    
    if text_len < min_length:
        raise ValueError(
            f"{field_name} is too short: {text_len} characters "
            f"(minimum: {min_length})"
        )
    
    if text_len > max_length:
        raise ValueError(
            f"{field_name} is too long: {text_len} characters "
            f"(maximum: {max_length})"
        )


def _generate_deterministic_id(text: str, prefix: str) -> str:
    """Generate deterministic ID using SHA256 hash.
    
    This ensures idempotency - same input always produces same ID.
    
    Args:
        text: Text to hash
        prefix: Prefix for the ID
        
    Returns:
        Deterministic ID string
    """
    hash_hex = hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]
    return f"{prefix}-{hash_hex}"


@dataclass
class AlignmentAnalysis:
    """Analysis of title alignment with script or idea."""

    score: int  # 0-100
    matches: List[str]  # Elements that align well
    mismatches: List[str]  # Elements that don't align
    key_elements: List[str]  # Important elements found
    reasoning: str


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract meaningful keywords from text.

    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return

    Returns:
        List of keywords sorted by relevance
    """
    if not text:
        return []

    try:
        # Convert to lowercase and split into words
        words = re.findall(r"\b\w+\b", text.lower())

        # Filter stopwords and count frequency
        word_freq = {}
        for word in words:
            if word not in COMMON_STOPWORDS and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_keywords]]
    except (re.error, Exception) as e:
        logger.error(f"Error extracting keywords: {e}", exc_info=True)
        return []


def analyze_title_content_alignment(
    title_text: str, content_text: str, script_summary: Optional[str] = None
) -> AlignmentAnalysis:
    """Analyze how well title aligns with script content.

    Args:
        title_text: The title to analyze
        content_text: The script content
        script_summary: Optional summary of script

    Returns:
        AlignmentAnalysis with scores and feedback
    """
    try:
        title_lower = title_text.lower()
        script_lower = content_text.lower()

        # Extract keywords from title and script
        title_keywords = extract_keywords(title_text, max_keywords=5)
        script_keywords = extract_keywords(content_text, max_keywords=20)

        # Find matching keywords
        matches = []
        for keyword in title_keywords:
            if keyword in script_lower:
                matches.append(keyword)

        # Calculate match percentage using safe division
        match_percentage = _safe_divide(len(matches), len(title_keywords), default=0) * 100

        # Identify potential mismatches (title keywords not in script)
        mismatches = [kw for kw in title_keywords if kw not in matches]

        # Calculate base score from keyword matching
        base_score = int(match_percentage * 0.6)  # 60% weight to keyword matching

        # Bonus for title appearing in script summary or early in script
        if script_summary and any(kw in script_summary.lower() for kw in title_keywords):
            base_score += 15

        # Check if title concepts appear in first portion of script (hook/introduction)
        script_intro = script_lower[: int(len(script_lower) * SCRIPT_INTRO_PERCENTAGE)]
        intro_matches = sum(1 for kw in title_keywords if kw in script_intro)
        if intro_matches > 0:
            base_score += min(10, intro_matches * 5)

        # Cap at 100
        score = min(100, base_score)

        # Generate reasoning
        if score >= 85:
            reasoning = f"Title strongly aligns with script content. {len(matches)}/{len(title_keywords)} title keywords found in script."
        elif score >= 70:
            reasoning = f"Good title-script alignment. {len(matches)}/{len(title_keywords)} title keywords present in script."
        elif score >= 60:
            reasoning = f"Fair alignment but could be stronger. {len(matches)}/{len(title_keywords)} keywords match."
        else:
            reasoning = f"Weak title-script alignment. Only {len(matches)}/{len(title_keywords)} keywords found in script."

        return AlignmentAnalysis(
            score=score,
            matches=matches,
            mismatches=mismatches,
            key_elements=script_keywords[:5],
            reasoning=reasoning,
        )
    except Exception as e:
        logger.error(f"Error analyzing title-content alignment: {e}", exc_info=True)
        # Return minimal alignment with zero score on error
        return AlignmentAnalysis(
            score=0,
            matches=[],
            mismatches=[],
            key_elements=[],
            reasoning=f"Error during alignment analysis: {str(e)}"
        )


def analyze_title_idea_alignment(
    title_text: str, idea_summary: str, idea_intent: Optional[str] = None
) -> AlignmentAnalysis:
    """Analyze how well title aligns with original idea.

    Args:
        title_text: The title to analyze
        idea_summary: Summary of the core idea
        idea_intent: Optional intent/purpose of the idea

    Returns:
        AlignmentAnalysis with scores and feedback
    """
    try:
        title_lower = title_text.lower()
        idea_lower = idea_summary.lower()

        # Extract keywords
        title_keywords = extract_keywords(title_text, max_keywords=5)
        idea_keywords = extract_keywords(idea_summary, max_keywords=10)

        # Find matches
        matches = []
        for keyword in title_keywords:
            if keyword in idea_lower:
                matches.append(keyword)

        # Check intent alignment if provided
        intent_match = False
        if idea_intent:
            intent_lower = idea_intent.lower()
            intent_match = any(kw in intent_lower for kw in title_keywords)

        # Calculate match percentage using safe division
        match_percentage = _safe_divide(len(matches), len(title_keywords), default=0) * 100

        # Calculate score
        base_score = int(match_percentage * 0.7)  # 70% weight to keyword matching

        if intent_match:
            base_score += 20

        # Identify mismatches
        mismatches = [kw for kw in title_keywords if kw not in matches]

        score = min(100, base_score)

        # Generate reasoning
        if score >= 80:
            reasoning = f"Title excellently captures idea essence. {len(matches)}/{len(title_keywords)} keywords aligned."
        elif score >= 65:
            reasoning = (
                f"Title reflects idea well. {len(matches)}/{len(title_keywords)} keywords present."
            )
        else:
            reasoning = f"Title could better reflect idea. Only {len(matches)}/{len(title_keywords)} keywords aligned."

        return AlignmentAnalysis(
            score=score,
            matches=matches,
            mismatches=mismatches,
            key_elements=idea_keywords[:5],
            reasoning=reasoning,
        )
    except Exception as e:
        logger.error(f"Error analyzing title-idea alignment: {e}", exc_info=True)
        # Return minimal alignment with zero score on error
        return AlignmentAnalysis(
            score=0,
            matches=[],
            mismatches=[],
            key_elements=[],
            reasoning=f"Error during alignment analysis: {str(e)}"
        )


def analyze_engagement(title_text: str) -> Dict[str, Any]:
    """Analyze title engagement potential.

    Args:
        title_text: The title to analyze

    Returns:
        Dictionary with engagement metrics
    """
    try:
        title_lower = title_text.lower()

        # Check for engagement words
        engagement_count = sum(1 for word in ENGAGEMENT_WORDS if word in title_lower)

        # Check for engagement patterns
        has_question = bool(re.search(SEO_PATTERNS["question"], title_lower))
        has_number = bool(re.search(SEO_PATTERNS["number"], title_lower))
        has_action = bool(re.search(SEO_PATTERNS["action"], title_lower))

        # Calculate scores
        curiosity_score = min(100, 60 + (engagement_count * 10) + (20 if has_question else 0))
        clickthrough_potential = min(100, 55 + (engagement_count * 8) + (15 if has_number else 0))
        engagement_score = min(100, 60 + (engagement_count * 8) + (10 if has_action else 0))

        # Expectation accuracy - titles with misleading words score lower
        has_misleading = any(word in title_lower for word in MISLEADING_WORDS)
        expectation_accuracy = 85 if not has_misleading else 70

        return {
            "engagement_score": engagement_score,
            "curiosity_score": curiosity_score,
            "clickthrough_potential": clickthrough_potential,
            "expectation_accuracy": expectation_accuracy,
            "has_question": has_question,
            "has_number": has_number,
            "engagement_words": engagement_count,
        }
    except (re.error, Exception) as e:
        logger.error(f"Error analyzing engagement: {e}", exc_info=True)
        # Return minimal engagement data on error
        return {
            "engagement_score": 50,
            "curiosity_score": 50,
            "clickthrough_potential": 50,
            "expectation_accuracy": 50,
            "has_question": False,
            "has_number": False,
            "engagement_words": 0,
        }


def analyze_seo(title_text: str, script_keywords: List[str]) -> Dict[str, Any]:
    """Analyze SEO optimization of title.

    Args:
        title_text: The title to analyze
        script_keywords: Keywords from script for relevance checking

    Returns:
        Dictionary with SEO metrics
    """
    try:
        title_lower = title_text.lower()

        # Check for SEO patterns
        pattern_score = 0
        for pattern_name, pattern in SEO_PATTERNS.items():
            if re.search(pattern, title_lower):
                pattern_score += 15

        # Keyword relevance
        title_keywords = extract_keywords(title_text, max_keywords=5)
        keyword_overlap = len([kw for kw in title_keywords if kw in script_keywords])
        keyword_relevance = min(100, 50 + (keyword_overlap * 15))

        # Length scoring (optimal is 50-70 characters)
        title_length = len(title_text)
        if 50 <= title_length <= 70:
            length_score = 100
        elif 40 <= title_length <= 80:
            length_score = 85
        else:
            length_score = 70

        # Overall SEO score
        seo_score = int((pattern_score + keyword_relevance + length_score) / 3)

        # Suggest keywords not yet in title
        suggested_keywords = [kw for kw in script_keywords[:5] if kw not in title_lower]

        return {
            "seo_score": min(100, seo_score),
            "keyword_relevance": keyword_relevance,
            "length_score": length_score,
            "suggested_keywords": suggested_keywords[:3],
        }
    except (re.error, Exception) as e:
        logger.error(f"Error analyzing SEO: {e}", exc_info=True)
        # Return minimal SEO data on error
        return {
            "seo_score": 50,
            "keyword_relevance": 50,
            "length_score": 50,
            "suggested_keywords": [],
        }


def generate_improvement_points(
    title_text: str,
    content_alignment: AlignmentAnalysis,
    idea_alignment: AlignmentAnalysis,
    engagement_data: Dict[str, Any],
    seo_data: Dict[str, Any],
) -> List[TitleImprovementPoint]:
    """Generate prioritized improvement recommendations.

    Args:
        title_text: The title being reviewed
        content_alignment: Content alignment analysis
        idea_alignment: Idea alignment analysis
        engagement_data: Engagement metrics
        seo_data: SEO metrics

    Returns:
        List of TitleImprovementPoint objects
    """
    improvements = []

    # Content alignment improvements
    if content_alignment.score < 75:
        if content_alignment.mismatches:
            improvements.append(
                TitleImprovementPoint(
                    category=TitleReviewCategory.CONTENT_ALIGNMENT,
                    title="Strengthen content alignment",
                    description=f"Title keywords '{', '.join(content_alignment.mismatches[:2])}' don't appear in content",
                    priority="high",
                    impact_score=25,
                    suggested_fix=f"Consider incorporating content elements: {', '.join(content_alignment.key_elements[:3])}",
                )
            )
        else:
            improvements.append(
                TitleImprovementPoint(
                    category=TitleReviewCategory.CONTENT_ALIGNMENT,
                    title="Improve title-content connection",
                    description="Title doesn't strongly reflect content",
                    priority="high",
                    impact_score=20,
                    suggested_fix=f"Reference key content elements: {', '.join(content_alignment.key_elements[:3])}",
                )
            )

    # Idea alignment improvements
    if idea_alignment.score < 75:
        improvements.append(
            TitleImprovementPoint(
                category=TitleReviewCategory.IDEA_ALIGNMENT,
                title="Better reflect original idea",
                description=f"Title could better capture idea essence. Key idea concepts: {', '.join(idea_alignment.key_elements[:3])}",
                priority="high",
                impact_score=22,
                suggested_fix="Incorporate core idea concepts while maintaining engagement",
            )
        )

    # Engagement improvements
    if engagement_data["engagement_score"] < 70:
        improvements.append(
            TitleImprovementPoint(
                category=TitleReviewCategory.ENGAGEMENT,
                title="Increase engagement appeal",
                description="Title lacks strong engagement hooks",
                priority="high" if engagement_data["engagement_score"] < 60 else "medium",
                impact_score=20,
                suggested_fix="Add curiosity-inducing words or pose a question to spark interest",
            )
        )

    # Clarity improvements
    if len(title_text) > 80:
        improvements.append(
            TitleImprovementPoint(
                category=TitleReviewCategory.CLARITY,
                title="Shorten for clarity",
                description=f"Title is {len(title_text)} characters, which may be too long",
                priority="medium",
                impact_score=15,
                suggested_fix="Aim for 50-70 characters for optimal readability and platform compatibility",
            )
        )
    elif len(title_text) < 20:
        improvements.append(
            TitleImprovementPoint(
                category=TitleReviewCategory.CLARITY,
                title="Add context for clarity",
                description="Title is very short and may lack context",
                priority="medium",
                impact_score=12,
                suggested_fix="Expand title to provide more context while staying under 70 characters",
            )
        )

    # SEO improvements
    if seo_data["seo_score"] < 70:
        improvements.append(
            TitleImprovementPoint(
                category=TitleReviewCategory.SEO_OPTIMIZATION,
                title="Optimize for SEO",
                description="Title has limited SEO optimization",
                priority="medium",
                impact_score=18,
                suggested_fix=(
                    f"Consider adding keywords: {', '.join(seo_data['suggested_keywords'])}"
                    if seo_data["suggested_keywords"]
                    else "Add relevant keywords naturally"
                ),
            )
        )

    # Sort by impact score descending
    improvements.sort(key=lambda x: x.impact_score, reverse=True)

    return improvements


def review_title_by_idea_and_content(
    title_text: str,
    idea_summary: str,
    content_text: str,
    title_id: Optional[str] = None,
    idea_id: Optional[str] = None,
    content_id: Optional[str] = None,
    content_summary: Optional[str] = None,
    idea_intent: Optional[str] = None,
    target_audience: Optional[str] = None,
    title_version: str = "v1",
    content_version: str = "v1",
    reviewer_id: str = "AI-TitleReviewer-001",
) -> TitleReview:
    """Review title v1 against idea and content v1.

    This function evaluates how well a title aligns with the core idea and content.
    It provides comprehensive feedback on:
    - Title-idea alignment
    - Title-content alignment
    - Engagement and clarity
    - SEO optimization
    - Specific improvement recommendations

    Args:
        title_text: The title text to review
        idea_summary: Summary of the core idea
        content_text: The full content text
        title_id: Optional identifier for the title
        idea_id: Optional identifier for the idea
        content_id: Optional identifier for the content
        content_summary: Optional summary of content (if not provided, extracted from content_text)
        idea_intent: Optional intent/purpose of the idea
        target_audience: Optional target audience description
        title_version: Version of title being reviewed (default: "v1")
        content_version: Version of content (default: "v1")
        reviewer_id: Identifier for this reviewer

    Returns:
        TitleReview object with comprehensive scores, feedback, and improvement points
        
    Raises:
        TypeError: If inputs are not strings
        ValueError: If inputs are invalid (empty, too short, too long)

    Example:
        >>> review = review_title_by_idea_and_content(
        ...     title_text="The Echo - A Haunting Discovery",
        ...     idea_summary="Horror story about mysterious echoes",
        ...     content_text="In the abandoned house, echoes reveal dark secrets...",
        ...     idea_intent="Create suspense through auditory elements"
        ... )
        >>> print(f"Overall score: {review.overall_score}%")
        >>> print(f"Content alignment: {review.content_alignment_score}%")
    """
    logger.info("Starting title review", extra={
        "title_length": len(title_text) if isinstance(title_text, str) else 0,
        "idea_length": len(idea_summary) if isinstance(idea_summary, str) else 0,
        "content_length": len(content_text) if isinstance(content_text, str) else 0,
    })
    
    try:
        # Phase 1: Input Validation
        logger.debug("Validating inputs")
        _validate_text_input(title_text, MIN_TEXT_LENGTH, MAX_TITLE_LENGTH, "title_text")
        _validate_text_input(idea_summary, MIN_TEXT_LENGTH, MAX_IDEA_LENGTH, "idea_summary")
        _validate_text_input(content_text, 10, MAX_CONTENT_LENGTH, "content_text")
        
        # Optional parameters validation
        if idea_intent and not isinstance(idea_intent, str):
            raise TypeError(f"idea_intent must be a string, got {type(idea_intent).__name__}")
        if target_audience and not isinstance(target_audience, str):
            raise TypeError(f"target_audience must be a string, got {type(target_audience).__name__}")
        
        # Phase 2: Input Sanitization
        logger.debug("Sanitizing inputs")
        title_text = _sanitize_text_input(title_text, MAX_TITLE_LENGTH, "title_text")
        idea_summary = _sanitize_text_input(idea_summary, MAX_IDEA_LENGTH, "idea_summary")
        content_text = _sanitize_text_input(content_text, MAX_CONTENT_LENGTH, "content_text")
        
        # Warn about large inputs
        if len(content_text) > 50000:
            logger.warning(f"Large content detected: {len(content_text)} characters may slow analysis")
        
        # Phase 3: Generate Deterministic IDs (Idempotency)
        logger.debug("Generating deterministic IDs")
        title_id = title_id or _generate_deterministic_id(title_text, "title")
        idea_id = idea_id or _generate_deterministic_id(idea_summary, "idea")
        content_id = content_id or _generate_deterministic_id(content_text, "content")
        
        logger.info("Review IDs generated", extra={
            "title_id": title_id,
            "idea_id": idea_id,
            "content_id": content_id,
        })

        # Extract content summary if not provided
        if not content_summary:
            # Use first DEFAULT_SCRIPT_SUMMARY_LENGTH characters as summary
            if len(content_text) > DEFAULT_SCRIPT_SUMMARY_LENGTH:
                content_summary = content_text[:DEFAULT_SCRIPT_SUMMARY_LENGTH] + "..."
            else:
                content_summary = content_text

        # Phase 4: Analyze alignments
        logger.debug("Analyzing title-content alignment")
        content_alignment = analyze_title_content_alignment(title_text, content_text, content_summary)
        logger.info(f"Content alignment score: {content_alignment.score}")
        
        logger.debug("Analyzing title-idea alignment")
        idea_alignment = analyze_title_idea_alignment(title_text, idea_summary, idea_intent)
        logger.info(f"Idea alignment score: {idea_alignment.score}")

        # Phase 5: Analyze engagement
        logger.debug("Analyzing engagement")
        engagement_data = analyze_engagement(title_text)
        logger.info(f"Engagement score: {engagement_data['engagement_score']}")

        # Phase 6: Analyze SEO
        logger.debug("Analyzing SEO optimization")
        content_keywords = extract_keywords(content_text, max_keywords=20)
        seo_data = analyze_seo(title_text, content_keywords)
        logger.info(f"SEO score: {seo_data['seo_score']}")

        # Phase 7: Calculate overall score (weighted average)
        overall_score = int(
            content_alignment.score * 0.30  # 30% weight to content alignment
            + idea_alignment.score * 0.25  # 25% weight to idea alignment
            + engagement_data["engagement_score"] * 0.25  # 25% weight to engagement
            + seo_data["seo_score"] * 0.20  # 20% weight to SEO
        )
        logger.info(f"Overall review score: {overall_score}")

        # Create category scores
        category_scores = [
            TitleCategoryScore(
                category=TitleReviewCategory.CONTENT_ALIGNMENT,
                score=content_alignment.score,
                reasoning=content_alignment.reasoning,
                strengths=[
                    (
                        f"Matches: {', '.join(content_alignment.matches)}"
                        if content_alignment.matches
                        else "Title keywords present"
                    )
                ],
                weaknesses=[
                    (
                        f"Missing: {', '.join(content_alignment.mismatches)}"
                        if content_alignment.mismatches
                        else "Could reference more content elements"
                    )
                ],
            ),
            TitleCategoryScore(
                category=TitleReviewCategory.IDEA_ALIGNMENT,
                score=idea_alignment.score,
                reasoning=idea_alignment.reasoning,
                strengths=[
                    (
                        f"Aligned keywords: {', '.join(idea_alignment.matches)}"
                        if idea_alignment.matches
                        else "Reflects idea concept"
                    )
                ],
                weaknesses=[
                    (
                        f"Missing idea elements: {', '.join(idea_alignment.mismatches)}"
                    if idea_alignment.mismatches
                    else "Could strengthen idea connection"
                )
            ],
        ),
        TitleCategoryScore(
            category=TitleReviewCategory.ENGAGEMENT,
            score=engagement_data["engagement_score"],
            reasoning=f"Engagement score based on curiosity words and patterns. Has question: {engagement_data['has_question']}, Has number: {engagement_data['has_number']}",
            strengths=[
                (
                    "Creates curiosity"
                    if engagement_data["engagement_words"] > 0
                    else "Clear and direct"
                )
            ],
            weaknesses=[
                (
                    "Could use more engaging language"
                    if engagement_data["engagement_words"] == 0
                    else "Moderate engagement potential"
                )
            ],
        ),
        TitleCategoryScore(
            category=TitleReviewCategory.SEO_OPTIMIZATION,
            score=seo_data["seo_score"],
            reasoning=f"SEO score based on keyword relevance and length optimization",
            strengths=[
                "Good keyword usage" if seo_data["keyword_relevance"] > 70 else "Basic SEO elements"
            ],
            weaknesses=[
                (
                    f"Could add: {', '.join(seo_data['suggested_keywords'])}"
                    if seo_data["suggested_keywords"]
                    else "SEO could be improved"
                )
            ],
        ),
    ]

        # Generate improvement points
        logger.debug("Generating improvement recommendations")
        improvement_points = generate_improvement_points(
            title_text, content_alignment, idea_alignment, engagement_data, seo_data
        )

        # Determine if major revision needed
        needs_major_revision = overall_score < 65

        # Create review object
        logger.debug("Creating final TitleReview object")
        review = TitleReview(
            title_id=title_id,
            title_text=title_text,
            title_version=title_version,
            overall_score=overall_score,
            category_scores=category_scores,
            improvement_points=improvement_points,
            # Content context
            content_id=content_id,
            script_title=title_text,  # Often the title is used as script title
            script_summary=content_summary,
            script_version=content_version,
            script_alignment_score=content_alignment.score,
            key_content_elements=content_alignment.key_elements,
            # Idea context
            idea_id=idea_id,
            idea_summary=idea_summary,
            idea_intent=idea_intent or "",
            idea_alignment_score=idea_alignment.score,
            target_audience=target_audience or "",
            # Engagement metrics
            engagement_score=engagement_data["engagement_score"],
            clickthrough_potential=engagement_data["clickthrough_potential"],
            curiosity_score=engagement_data["curiosity_score"],
            expectation_accuracy=engagement_data["expectation_accuracy"],
            # SEO & Optimization
            seo_score=seo_data["seo_score"],
            keyword_relevance=seo_data["keyword_relevance"],
            suggested_keywords=seo_data["suggested_keywords"],
            length_score=seo_data["length_score"],
            # Review metadata
            reviewer_id=reviewer_id,
            confidence_score=85,  # Base confidence score
            needs_major_revision=needs_major_revision,
            # Strengths and concerns
            strengths=[
                f"Strong {'content' if content_alignment.score >= 80 else 'idea'} alignment",
                (
                    "Good engagement potential"
                    if engagement_data["engagement_score"] >= 70
                    else "Clear structure"
                ),
            ],
            primary_concern=(
                improvement_points[0].description if improvement_points else "No major concerns"
            ),
            quick_wins=[
                imp.title for imp in improvement_points[:3] if imp.priority in ["high", "medium"]
            ],
        )
        
        logger.info(
            "Title review completed successfully",
            extra={
                "title_id": title_id,
                "overall_score": overall_score,
                "needs_revision": needs_major_revision,
            }
        )

        return review
        
    except (TypeError, ValueError) as e:
        # Input validation errors - re-raise with context
        logger.error(f"Input validation error: {e}", exc_info=True)
        raise
    except Exception as e:
        # Unexpected error - log and return minimal review
        logger.error(f"Unexpected error during title review: {e}", exc_info=True)
        
        # Generate minimal IDs if we got this far without them
        try:
            if not title_id:
                title_id = _generate_deterministic_id(str(title_text)[:100], "title")
            if not idea_id:
                idea_id = _generate_deterministic_id(str(idea_summary)[:100], "idea")
            if not content_id:
                content_id = _generate_deterministic_id(str(content_text)[:100], "content")
        except:
            title_id = "title-error"
            idea_id = "idea-error"
            content_id = "content-error"
        
        # Return minimal review indicating error
        return TitleReview(
            title_id=title_id,
            title_text=str(title_text)[:200] if title_text else "ERROR",
            title_version=title_version,
            overall_score=0,
            category_scores=[],
            improvement_points=[
                TitleImprovementPoint(
                    category=TitleReviewCategory.CONTENT_ALIGNMENT,
                    title="Review Error",
                    description=f"An error occurred during review: {str(e)}",
                    priority="critical",
                    impact_score=100,
                    suggested_fix="Please contact support or try again with different inputs",
                )
            ],
            # Content context
            content_id=content_id,
            script_title=str(title_text)[:200] if title_text else "ERROR",
            script_summary="Error during processing",
            script_version=content_version,
            script_alignment_score=0,
            key_content_elements=[],
            # Idea context
            idea_id=idea_id,
            idea_summary=str(idea_summary)[:200] if idea_summary else "ERROR",
            idea_intent="",
            idea_alignment_score=0,
            target_audience="",
            # Engagement metrics
            engagement_score=0,
            clickthrough_potential=0,
            curiosity_score=0,
            expectation_accuracy=0,
            # SEO & Optimization
            seo_score=0,
            keyword_relevance=0,
            suggested_keywords=[],
            length_score=0,
            # Review metadata
            reviewer_id=reviewer_id,
            confidence_score=0,
            needs_major_revision=True,
            # Strengths and concerns
            strengths=[],
            primary_concern=f"Review failed: {str(e)}",
            quick_wins=[],
        )
