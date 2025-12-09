"""Review script v1 against title v1 and idea.

This module implements MVP-005: Script review that evaluates how well
a script aligns with its title and the core idea it's based on.

The reviewer provides:
- Title-script alignment assessment
- Idea-script alignment assessment
- Content quality scoring
- Actionable improvement recommendations

Workflow Position:
    Idea + Title v1 → Script v1 → ByTitleAndIdea Review → Feedback/Approval
"""

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from T.Review.Script.script_review import (
    CategoryScore,
    ContentLength,
    ImprovementPoint,
    ReviewCategory,
    ScriptReview,
)

# Use TYPE_CHECKING to avoid runtime import issues
if TYPE_CHECKING:
    from src.idea import Idea
else:
    # At runtime, we'll accept any object with the right attributes
    Idea = Any


# Constants for scoring and analysis
WORDS_PER_SECOND_SPEAKING = 2.5  # Average speaking rate: 150 words per minute
WORDS_PER_MINUTE_SPEAKING = 150

# Common stopwords to filter out in analysis
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

# Genre indicators for content analysis
GENRE_INDICATORS = {
    "horror": ["fear", "scared", "dark", "terror", "nightmare", "scream", "shadow"],
    "mystery": ["clue", "secret", "discover", "mystery", "hidden", "reveal", "puzzle"],
    "science_fiction": ["future", "technology", "space", "science", "alien", "robot"],
    "educational": ["learn", "understand", "explain", "teach", "knowledge", "how", "why"],
}

# Emotional words for impact scoring
EMOTIONAL_WORDS = [
    "fear",
    "love",
    "hope",
    "terror",
    "joy",
    "pain",
    "realize",
    "discover",
    "wonder",
    "amazed",
    "shocked",
    "surprised",
    "angry",
    "sad",
    "happy",
    "excited",
    "worried",
    "anxious",
    "proud",
    "ashamed",
    "grateful",
]


@dataclass
class AlignmentScore:
    """Score for title or idea alignment."""

    score: int  # 0-100
    matches: List[str]  # What aligns well
    mismatches: List[str]  # What doesn't align
    reasoning: str


def review_script_by_title_and_idea(
    script_text: str,
    title: str,
    idea: Idea,
    script_id: Optional[str] = None,
    target_length_seconds: Optional[int] = None,
    reviewer_id: str = "AI-ScriptReviewer-ByTitleAndIdea-001",
) -> ScriptReview:
    """Review script v1 against title v1 and idea.

    This function evaluates how well a script aligns with its title and
    the core idea it's based on. It provides comprehensive feedback on:
    - Title-script alignment
    - Idea-script alignment
    - Content quality across multiple categories
    - Specific improvement recommendations

    Args:
        script_text: The script text to review
        title: The title v1 for the script
        idea: The Idea model object containing the core concept
        script_id: Optional identifier for the script
        target_length_seconds: Optional target duration in seconds
        reviewer_id: Identifier for this reviewer

    Returns:
        ScriptReview object with scores, feedback, and improvement points

    Example:
        >>> from T.Idea.Model import Idea, ContentGenre
        >>> idea = Idea(
        ...     title="The Echo",
        ...     concept="A girl hears her own future voice warning her",
        ...     premise="A girl discovers she can hear her future self...",
        ...     genre=ContentGenre.HORROR
        ... )
        >>> title = "The Voice That Knows Tomorrow"
        >>> script = "Last night I heard a whisper..."
        >>> review = review_script_by_title_and_idea(script, title, idea)
        >>> print(f"Overall score: {review.overall_score}%")
    """
    # Generate script ID if not provided
    if script_id is None:
        script_id = f"script-{idea.title.lower().replace(' ', '-')}-v1"

    # Analyze title-script alignment
    title_alignment = _analyze_title_alignment(script_text, title)

    # Analyze idea-script alignment
    idea_alignment = _analyze_idea_alignment(script_text, idea)

    # Calculate content quality scores
    content_scores = _calculate_content_scores(script_text, title, idea)

    # Determine target length category
    target_length = _determine_target_length(idea, target_length_seconds)

    # Estimate script length
    current_length = _estimate_script_length(script_text)

    # Calculate overall score
    overall_score = _calculate_overall_score(
        title_alignment.score, idea_alignment.score, content_scores
    )

    # Generate improvement points
    improvement_points = _generate_improvement_points(
        title_alignment, idea_alignment, content_scores, overall_score
    )

    # Create category scores
    category_scores = _create_category_scores(content_scores)

    # Determine if major revision needed
    needs_major_revision = overall_score < 60

    # Create and return ScriptReview
    review = ScriptReview(
        script_id=script_id,
        script_title=title,
        overall_score=overall_score,
        category_scores=category_scores,
        improvement_points=improvement_points,
        target_audience=idea.target_audience or "General audience",
        audience_alignment_score=idea_alignment.score,
        target_length=target_length,
        current_length_seconds=current_length,
        optimal_length_seconds=target_length_seconds,
        is_youtube_short=(
            target_length in [ContentLength.YOUTUBE_SHORT, ContentLength.YOUTUBE_SHORT_EXTENDED]
        ),
        reviewer_id=reviewer_id,
        needs_major_revision=needs_major_revision,
        strengths=title_alignment.matches + idea_alignment.matches,
        primary_concern=_identify_primary_concern(title_alignment, idea_alignment, content_scores),
        quick_wins=_identify_quick_wins(improvement_points),
        metadata={
            "title_alignment_score": str(title_alignment.score),
            "idea_alignment_score": str(idea_alignment.score),
            "idea_genre": idea.genre.value,
            "idea_version": str(idea.version),
        },
    )

    return review


def _analyze_title_alignment(script_text: str, title: str) -> AlignmentScore:
    """Analyze how well the script aligns with the title.

    Args:
        script_text: The script text
        title: The title

    Returns:
        AlignmentScore with title-script alignment metrics
    """
    matches = []
    mismatches = []

    # Extract key words from title (using word boundaries)
    title_words = set(word.lower() for word in re.findall(r"\b\w+\b", title))
    # Filter out stopwords
    title_words = title_words - COMMON_STOPWORDS

    script_lower = script_text.lower()

    # Check for title word presence in script with word boundaries
    if title_words:
        words_present = sum(
            1 for word in title_words if re.search(r"\b" + re.escape(word) + r"\b", script_lower)
        )
        word_coverage = words_present / len(title_words) * 100
    else:
        word_coverage = 0

    # Basic alignment scoring
    if word_coverage >= 50:
        matches.append("Title keywords well-represented in script")
        score = min(85, 60 + int(word_coverage / 2))
    elif word_coverage >= 30:
        matches.append("Some title keywords present in script")
        mismatches.append("Limited title keyword coverage")
        score = 60
    else:
        mismatches.append("Title not well reflected in script content")
        score = 45

    # Check script length appropriateness for title
    if len(script_text) < 100:
        mismatches.append("Script too short to fully develop title concept")
        score = max(40, score - 10)
    elif len(script_text) > 10000:
        mismatches.append("Script may be too long for the title concept")
        score = max(50, score - 5)
    else:
        matches.append("Script length appropriate for title")

    reasoning = (
        f"Title-script alignment: {score}%. "
        f"{len(matches)} strengths, {len(mismatches)} areas for improvement."
    )

    return AlignmentScore(score=score, matches=matches, mismatches=mismatches, reasoning=reasoning)


def _analyze_idea_alignment(script_text: str, idea: Idea) -> AlignmentScore:
    """Analyze how well the script aligns with the core idea.

    Args:
        script_text: The script text
        idea: The Idea model

    Returns:
        AlignmentScore with idea-script alignment metrics
    """
    matches = []
    mismatches = []
    score = 70  # Start with baseline

    script_lower = script_text.lower()

    # Check concept alignment
    if idea.concept:
        concept_words = set(idea.concept.lower().split())
        concept_present = sum(1 for word in concept_words if word in script_lower)
        concept_coverage = (concept_present / len(concept_words) * 100) if concept_words else 0

        if concept_coverage >= 40:
            matches.append("Core concept well-reflected in script")
            score += 10
        else:
            mismatches.append("Core concept not clearly present in script")
            score -= 10

    # Check premise alignment
    if idea.premise:
        premise_words = set(word.lower() for word in re.findall(r"\b\w+\b", idea.premise))
        # Filter out common words
        premise_words = premise_words - COMMON_STOPWORDS

        if premise_words:
            premise_present = sum(
                1
                for word in premise_words
                if re.search(r"\b" + re.escape(word) + r"\b", script_lower)
            )
            premise_coverage = premise_present / len(premise_words) * 100

            if premise_coverage >= 30:
                matches.append("Premise elements present in script")
                score += 5
            else:
                mismatches.append("Premise not clearly developed in script")
                score -= 5

    # Check hook/logline alignment
    if idea.hook:
        hook_words = set(idea.hook.lower().split())
        hook_present = any(word in script_lower for word in hook_words if len(word) > 3)

        if hook_present:
            matches.append("Opening hook aligns with idea")
            score += 5
        else:
            mismatches.append("Hook from idea not reflected in script")

    # Check genre consistency
    if idea.genre.value in GENRE_INDICATORS:
        indicators = GENRE_INDICATORS[idea.genre.value]
        has_indicators = any(
            re.search(r"\b" + re.escape(indicator) + r"\b", script_lower)
            for indicator in indicators
        )

        if has_indicators:
            matches.append(f"Script tone matches {idea.genre.value} genre")
            score += 5
        else:
            mismatches.append(f"Script may not match {idea.genre.value} genre expectations")
            score -= 5

    # Ensure score is in valid range
    score = max(30, min(95, score))

    reasoning = (
        f"Idea-script alignment: {score}%. "
        f"Script {'well' if score >= 70 else 'somewhat'} reflects the core idea."
    )

    return AlignmentScore(score=score, matches=matches, mismatches=mismatches, reasoning=reasoning)


def _calculate_content_scores(script_text: str, title: str, idea: Idea) -> Dict[str, int]:
    """Calculate content quality scores across categories.

    Args:
        script_text: The script text
        title: The title
        idea: The Idea model

    Returns:
        Dictionary mapping category names to scores (0-100)
    """
    scores = {}

    # ENGAGEMENT score
    # Check for strong opening
    opening = script_text[:200] if len(script_text) >= 200 else script_text
    has_strong_opening = any(
        indicator in opening.lower()
        for indicator in ["imagine", "what if", "last night", "suddenly", "?", "!"]
    )
    engagement_score = 70 + (15 if has_strong_opening else 0)
    scores["engagement"] = engagement_score

    # PACING score
    # Estimate based on paragraph structure
    paragraphs = [p.strip() for p in script_text.split("\n\n") if p.strip()]
    avg_para_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0

    if 100 <= avg_para_length <= 500:
        pacing_score = 80
    elif 50 <= avg_para_length < 100 or 500 < avg_para_length <= 800:
        pacing_score = 70
    else:
        pacing_score = 60
    scores["pacing"] = pacing_score

    # CLARITY score
    # Estimate based on sentence structure
    sentences = script_text.count(".") + script_text.count("!") + script_text.count("?")
    words = len(script_text.split())
    avg_words_per_sentence = words / sentences if sentences > 0 else 0

    if 10 <= avg_words_per_sentence <= 25:
        clarity_score = 80
    elif 8 <= avg_words_per_sentence < 10 or 25 < avg_words_per_sentence <= 35:
        clarity_score = 70
    else:
        clarity_score = 60
    scores["clarity"] = clarity_score

    # STRUCTURE score
    # Check for basic story structure
    has_beginning = len(opening) >= 100
    has_ending = len(script_text) >= 200
    has_paragraphs = len(paragraphs) >= 3

    structure_score = 60
    if has_beginning:
        structure_score += 10
    if has_ending:
        structure_score += 10
    if has_paragraphs:
        structure_score += 10
    scores["structure"] = structure_score

    # IMPACT score
    # Check for emotional words and powerful endings
    emotion_count = sum(
        1
        for word in EMOTIONAL_WORDS
        if re.search(r"\b" + re.escape(word) + r"\b", script_text.lower())
    )

    impact_score = 60 + min(20, emotion_count * 3)
    scores["impact"] = impact_score

    return scores


def _determine_target_length(idea: Idea, target_length_seconds: Optional[int]) -> ContentLength:
    """Determine appropriate content length category.

    Args:
        idea: The Idea model
        target_length_seconds: Optional target duration

    Returns:
        ContentLength enum value
    """
    # Check idea's length_target first
    if idea.length_target:
        length_lower = idea.length_target.lower()
        if "short" in length_lower or "60" in length_lower or "90" in length_lower:
            return ContentLength.YOUTUBE_SHORT_EXTENDED
        elif "3 min" in length_lower or "brief" in length_lower:
            return ContentLength.SHORT_FORM

    # Check target_length_seconds
    if target_length_seconds:
        if target_length_seconds <= 60:
            return ContentLength.YOUTUBE_SHORT
        elif target_length_seconds <= 180:
            return ContentLength.YOUTUBE_SHORT_EXTENDED
        elif target_length_seconds <= 300:
            return ContentLength.SHORT_FORM

    # Check platforms
    if any(platform.lower() in ["tiktok", "youtube shorts"] for platform in idea.target_platforms):
        return ContentLength.YOUTUBE_SHORT

    # Default
    return ContentLength.SHORT_FORM


def _estimate_script_length(script_text: str) -> int:
    """Estimate script duration in seconds.

    Uses average speaking rate defined in WORDS_PER_SECOND_SPEAKING constant.

    Args:
        script_text: The script text

    Returns:
        Estimated duration in seconds
    """
    words = len(script_text.split())
    seconds = int(words / WORDS_PER_SECOND_SPEAKING)
    return seconds


def _calculate_overall_score(
    title_alignment: int, idea_alignment: int, content_scores: Dict[str, int]
) -> int:
    """Calculate overall review score.

    Weights:
    - Title alignment: 25%
    - Idea alignment: 30%
    - Content quality: 45%

    Args:
        title_alignment: Title alignment score
        idea_alignment: Idea alignment score
        content_scores: Dictionary of content quality scores

    Returns:
        Overall score (0-100)
    """
    # Calculate average content score
    avg_content_score = sum(content_scores.values()) / len(content_scores) if content_scores else 0

    # Calculate weighted overall score
    overall = int((title_alignment * 0.25) + (idea_alignment * 0.30) + (avg_content_score * 0.45))

    return max(0, min(100, overall))


def _generate_improvement_points(
    title_alignment: AlignmentScore,
    idea_alignment: AlignmentScore,
    content_scores: Dict[str, int],
    overall_score: int,
) -> List[ImprovementPoint]:
    """Generate prioritized improvement recommendations.

    Args:
        title_alignment: Title alignment analysis
        idea_alignment: Idea alignment analysis
        content_scores: Content quality scores
        overall_score: Overall review score

    Returns:
        List of ImprovementPoint objects
    """
    improvements = []

    # Title alignment improvements
    if title_alignment.score < 70:
        improvements.append(
            ImprovementPoint(
                category=ReviewCategory.AUDIENCE_FIT,
                title="Improve title-script alignment",
                description="Better reflect title concepts in script content",
                priority="high",
                impact_score=20,
                specific_example="; ".join(title_alignment.mismatches[:2]),
                suggested_fix="Incorporate key title elements into opening and throughout script",
            )
        )

    # Idea alignment improvements
    if idea_alignment.score < 70:
        improvements.append(
            ImprovementPoint(
                category=ReviewCategory.STRUCTURE,
                title="Strengthen idea-script alignment",
                description="Ensure script clearly reflects the core idea and premise",
                priority="high",
                impact_score=25,
                specific_example="; ".join(idea_alignment.mismatches[:2]),
                suggested_fix="Reference key idea elements and develop premise more clearly",
            )
        )

    # Content quality improvements
    for category, score in content_scores.items():
        if score < 70:
            category_enum = _category_name_to_enum(category)
            impact = 15 if score < 60 else 10

            improvements.append(
                ImprovementPoint(
                    category=category_enum,
                    title=f"Improve {category}",
                    description=f"{category.capitalize()} score is {score}%, needs enhancement",
                    priority="high" if score < 60 else "medium",
                    impact_score=impact,
                    suggested_fix=_get_category_suggestion(category, score),
                )
            )

    # Sort by impact score (descending)
    improvements.sort(key=lambda x: x.impact_score, reverse=True)

    return improvements


def _create_category_scores(content_scores: Dict[str, int]) -> List[CategoryScore]:
    """Create CategoryScore objects from content scores.

    Args:
        content_scores: Dictionary of content quality scores

    Returns:
        List of CategoryScore objects
    """
    category_scores = []

    for category_name, score in content_scores.items():
        category_enum = _category_name_to_enum(category_name)

        strengths = []
        weaknesses = []

        if score >= 75:
            strengths.append(f"Strong {category_name}")
        elif score < 65:
            weaknesses.append(f"{category_name.capitalize()} needs improvement")

        reasoning = _get_category_reasoning(category_name, score)

        category_scores.append(
            CategoryScore(
                category=category_enum,
                score=score,
                reasoning=reasoning,
                strengths=strengths,
                weaknesses=weaknesses,
            )
        )

    return category_scores


def _category_name_to_enum(category_name: str) -> ReviewCategory:
    """Convert category name string to ReviewCategory enum.

    Args:
        category_name: Category name string

    Returns:
        ReviewCategory enum value
    """
    mapping = {
        "engagement": ReviewCategory.ENGAGEMENT,
        "pacing": ReviewCategory.PACING,
        "clarity": ReviewCategory.CLARITY,
        "structure": ReviewCategory.STRUCTURE,
        "impact": ReviewCategory.IMPACT,
        "audience_fit": ReviewCategory.AUDIENCE_FIT,
    }
    return mapping.get(category_name, ReviewCategory.STRUCTURE)


def _get_category_reasoning(category: str, score: int) -> str:
    """Generate reasoning for a category score.

    Args:
        category: Category name
        score: Score value

    Returns:
        Reasoning text
    """
    if score >= 80:
        return f"{category.capitalize()} is strong with good execution"
    elif score >= 70:
        return f"{category.capitalize()} is adequate but could be enhanced"
    elif score >= 60:
        return f"{category.capitalize()} needs improvement for better impact"
    else:
        return f"{category.capitalize()} requires significant work"


def _get_category_suggestion(category: str, score: int) -> str:
    """Get improvement suggestion for a category.

    Args:
        category: Category name
        score: Score value

    Returns:
        Suggestion text
    """
    suggestions = {
        "engagement": "Add stronger hooks, emotional moments, or compelling questions",
        "pacing": "Adjust paragraph length and rhythm for better flow",
        "clarity": "Simplify sentence structure and ensure clear communication",
        "structure": "Develop clear beginning, middle, and end with proper transitions",
        "impact": "Add more emotional depth and memorable moments",
    }
    return suggestions.get(category, "Review and enhance this aspect of the script")


def _identify_primary_concern(
    title_alignment: AlignmentScore, idea_alignment: AlignmentScore, content_scores: Dict[str, int]
) -> str:
    """Identify the primary concern to address.

    Args:
        title_alignment: Title alignment analysis
        idea_alignment: Idea alignment analysis
        content_scores: Content quality scores

    Returns:
        Description of primary concern
    """
    # Find lowest score
    all_scores = {
        "title_alignment": title_alignment.score,
        "idea_alignment": idea_alignment.score,
        **content_scores,
    }

    min_category = min(all_scores, key=all_scores.get)
    min_score = all_scores[min_category]

    if min_category == "title_alignment":
        return "Script doesn't strongly reflect the title"
    elif min_category == "idea_alignment":
        return "Script doesn't clearly develop the core idea"
    else:
        return f"Content {min_category} needs improvement"


def _identify_quick_wins(improvement_points: List[ImprovementPoint]) -> List[str]:
    """Identify quick wins from improvement points.

    Args:
        improvement_points: List of improvement points

    Returns:
        List of quick win descriptions
    """
    quick_wins = []

    # Take top 3 highest impact improvements
    for point in improvement_points[:3]:
        if point.impact_score >= 15:
            quick_wins.append(f"{point.title} (+{point.impact_score}% impact)")

    return quick_wins
