"""Review title v1 against script v1 and idea.

This module implements the AI-powered title review function that evaluates
how well a title aligns with its script and the core idea it's based on.

The reviewer provides:
- Title-script alignment assessment
- Title-idea alignment assessment
- Engagement and clarity scoring
- Actionable improvement recommendations
- Structured JSON-compatible feedback

Workflow Position:
    Idea + Title v1 + Content v1 → ByScriptAndIdea Review → TitleReview Feedback → Title v2
"""

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

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

    # Calculate match percentage
    if title_keywords:
        match_percentage = (len(matches) / len(title_keywords)) * 100
    else:
        match_percentage = 0

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

    # Calculate match percentage
    if title_keywords:
        match_percentage = (len(matches) / len(title_keywords)) * 100
    else:
        match_percentage = 0

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


def analyze_engagement(title_text: str) -> Dict[str, Any]:
    """Analyze title engagement potential.

    Args:
        title_text: The title to analyze

    Returns:
        Dictionary with engagement metrics
    """
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


def analyze_seo(title_text: str, script_keywords: List[str]) -> Dict[str, Any]:
    """Analyze SEO optimization of title.

    Args:
        title_text: The title to analyze
        script_keywords: Keywords from script for relevance checking

    Returns:
        Dictionary with SEO metrics
    """
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


def generate_improvement_points(
    title_text: str,
    script_alignment: AlignmentAnalysis,
    idea_alignment: AlignmentAnalysis,
    engagement_data: Dict[str, Any],
    seo_data: Dict[str, Any],
) -> List[TitleImprovementPoint]:
    """Generate prioritized improvement recommendations.

    Args:
        title_text: The title being reviewed
        script_alignment: Content alignment analysis
        idea_alignment: Idea alignment analysis
        engagement_data: Engagement metrics
        seo_data: SEO metrics

    Returns:
        List of TitleImprovementPoint objects
    """
    improvements = []

    # Content alignment improvements
    if script_alignment.score < 75:
        if script_alignment.mismatches:
            improvements.append(
                TitleImprovementPoint(
                    category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                    title="Strengthen script alignment",
                    description=f"Title keywords '{', '.join(script_alignment.mismatches[:2])}' don't appear in script",
                    priority="high",
                    impact_score=25,
                    suggested_fix=f"Consider incorporating script elements: {', '.join(script_alignment.key_elements[:3])}",
                )
            )
        else:
            improvements.append(
                TitleImprovementPoint(
                    category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                    title="Improve title-script connection",
                    description="Title doesn't strongly reflect script content",
                    priority="high",
                    impact_score=20,
                    suggested_fix=f"Reference key script elements: {', '.join(script_alignment.key_elements[:3])}",
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


def review_title_by_content_and_idea(
    title_text: str,
    content_text: str,
    idea_summary: str,
    title_id: Optional[str] = None,
    content_id: Optional[str] = None,
    idea_id: Optional[str] = None,
    script_summary: Optional[str] = None,
    idea_intent: Optional[str] = None,
    target_audience: Optional[str] = None,
    title_version: str = "v1",
    script_version: str = "v1",
    reviewer_id: str = "AI-TitleReviewer-001",
) -> TitleReview:
    """Review title v1 against script v1 and idea.

    This function evaluates how well a title aligns with its script and
    the core idea it's based on. It provides comprehensive feedback on:
    - Title-script alignment
    - Title-idea alignment
    - Engagement and clarity
    - SEO optimization
    - Specific improvement recommendations

    Args:
        title_text: The title text to review
        content_text: The full script text
        idea_summary: Summary of the core idea
        title_id: Optional identifier for the title
        content_id: Optional identifier for the script
        idea_id: Optional identifier for the idea
        script_summary: Optional summary of script (if not provided, extracted from content_text)
        idea_intent: Optional intent/purpose of the idea
        target_audience: Optional target audience description
        title_version: Version of title being reviewed (default: "v1")
        script_version: Version of script (default: "v1")
        reviewer_id: Identifier for this reviewer

    Returns:
        TitleReview object with comprehensive scores, feedback, and improvement points

    Example:
        >>> review = review_title_by_content_and_idea(
        ...     title_text="The Echo - A Haunting Discovery",
        ...     content_text="In the abandoned house, echoes reveal dark secrets...",
        ...     idea_summary="Horror story about mysterious echoes",
        ...     idea_intent="Create suspense through auditory elements"
        ... )
        >>> print(f"Overall score: {review.overall_score}%")
        >>> print(f"Content alignment: {review.script_alignment_score}%")
    """
    # Generate IDs if not provided (using absolute value to ensure positive IDs)
    title_id = title_id or f"title-{abs(hash(title_text)) % 10000:04d}"
    content_id = content_id or f"script-{abs(hash(content_text)) % 10000:04d}"
    idea_id = idea_id or f"idea-{abs(hash(idea_summary)) % 10000:04d}"

    # Extract script summary if not provided
    if not script_summary:
        # Use first DEFAULT_SCRIPT_SUMMARY_LENGTH characters as summary
        if len(content_text) > DEFAULT_SCRIPT_SUMMARY_LENGTH:
            script_summary = content_text[:DEFAULT_SCRIPT_SUMMARY_LENGTH] + "..."
        else:
            script_summary = content_text

    # Analyze alignments
    script_alignment = analyze_title_content_alignment(title_text, content_text, script_summary)
    idea_alignment = analyze_title_idea_alignment(title_text, idea_summary, idea_intent)

    # Analyze engagement
    engagement_data = analyze_engagement(title_text)

    # Analyze SEO
    script_keywords = extract_keywords(content_text, max_keywords=20)
    seo_data = analyze_seo(title_text, script_keywords)

    # Calculate overall score (weighted average)
    overall_score = int(
        script_alignment.score * 0.30  # 30% weight to script alignment
        + idea_alignment.score * 0.25  # 25% weight to idea alignment
        + engagement_data["engagement_score"] * 0.25  # 25% weight to engagement
        + seo_data["seo_score"] * 0.20  # 20% weight to SEO
    )

    # Create category scores
    category_scores = [
        TitleCategoryScore(
            category=TitleReviewCategory.SCRIPT_ALIGNMENT,
            score=script_alignment.score,
            reasoning=script_alignment.reasoning,
            strengths=[
                (
                    f"Matches: {', '.join(script_alignment.matches)}"
                    if script_alignment.matches
                    else "Title keywords present"
                )
            ],
            weaknesses=[
                (
                    f"Missing: {', '.join(script_alignment.mismatches)}"
                    if script_alignment.mismatches
                    else "Could reference more script elements"
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
    improvement_points = generate_improvement_points(
        title_text, script_alignment, idea_alignment, engagement_data, seo_data
    )

    # Determine if major revision needed
    needs_major_revision = overall_score < 65

    # Create review object
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
        script_summary=script_summary,
        script_version=script_version,
        script_alignment_score=script_alignment.score,
        key_content_elements=script_alignment.key_elements,
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
            f"Strong {'script' if script_alignment.score >= 80 else 'idea'} alignment",
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

    return review
