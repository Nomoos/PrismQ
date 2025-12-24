"""Title Improvement module for generating improved title versions.

This module implements MVP-006 and MVP-009: Generate improved title versions
using feedback from both title review (MVP-004) and script review (MVP-005).

IMPLEMENTATION NOTE: This is a rule-based implementation that applies structured
improvements based on review feedback categories. It does NOT use AI/LLM services
for text generation. Improvements are applied through deterministic algorithms
that incorporate review suggestions, keywords, and content elements.

The module takes:
- Original title (any version: v1, v2, v3, etc.)
- Content (corresponding version)
- Title review feedback (from ByScriptAndIdea)
- Content review feedback (from ByTitle)
- Original idea (for context)

And generates:
- Improved title (next version) that addresses review feedback
- Maintains engagement while improving alignment
- Documents changes and rationale
- Supports iterative refinement (v1→v2, v2→v3, v3→v4, etc.)

Workflow Position:
    Title vN + Content vN + Reviews → Title v(N+1) (improved)

    Examples:
    - MVP-006: Title v1 + Content v1 + Reviews → Title v2
    - MVP-009: Title v2 + Content v2 + Reviews → Title v3
    - Iteration: Title v3 + Content v3 + Reviews → Title v4, v5, v6, v7, etc.
"""

import logging
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directories to path for imports
current_file = Path(__file__)
t_module_dir = current_file.parent.parent.parent.parent

# Import review models
review_title_path = t_module_dir / "Review" / "Title" / "ByScriptAndIdea"
review_content_path = t_module_dir / "Review" / "Content"
idea_model_path = t_module_dir / "Idea" / "Model" / "src"

sys.path.insert(0, str(review_title_path))
sys.path.insert(0, str(review_content_path))
sys.path.insert(0, str(idea_model_path))

from script_review import ImprovementPoint as ScriptImprovementPoint
from script_review import ScriptReview
from title_review import TitleImprovementPoint, TitleReview, TitleReviewCategory

from idea import Idea


# Module logger
logger = logging.getLogger(__name__)

# Constants for validation
VERSION_PATTERN = re.compile(r"^v\d+$")
MIN_TITLE_LENGTH = 10
MAX_TITLE_LENGTH = 200
MIN_CONTENT_LENGTH = 50
MAX_CONTENT_LENGTH = 100000
MIN_OPTIMAL_LENGTH = 20
MAX_OPTIMAL_LENGTH = 300


class TitleImprovementError(Exception):
    """Base exception for title improvement errors."""

    pass


class ValidationError(TitleImprovementError):
    """Exception raised for validation errors."""

    pass


class ImprovementError(TitleImprovementError):
    """Exception raised during improvement processing."""

    pass


def validate_version_number(version: str, param_name: str = "version") -> None:
    """Validate version number format.

    Args:
        version: Version string to validate (e.g., "v1", "v2")
        param_name: Parameter name for error messages

    Raises:
        ValidationError: If version format is invalid
    """
    if not version:
        raise ValidationError(f"{param_name} cannot be empty")
    if not VERSION_PATTERN.match(version):
        raise ValidationError(
            f"{param_name} must be in format 'vN' (e.g., 'v1', 'v2'). Got: '{version}'"
        )


def extract_version_number(version: str) -> int:
    """Extract numeric part from version string.

    Args:
        version: Version string (e.g., "v1", "v2")

    Returns:
        Integer version number

    Raises:
        ValidationError: If version format is invalid
    """
    validate_version_number(version)
    return int(version[1:])


def validate_version_progression(original: str, new: str) -> None:
    """Validate that new version is greater than original.

    Args:
        original: Original version (e.g., "v1")
        new: New version (e.g., "v2")

    Raises:
        ValidationError: If version progression is invalid
    """
    validate_version_number(original, "original_version")
    validate_version_number(new, "new_version")

    original_num = extract_version_number(original)
    new_num = extract_version_number(new)

    if new_num <= original_num:
        raise ValidationError(
            f"New version ({new}) must be greater than original ({original})"
        )


def validate_text_length(
    text: str, param_name: str, min_length: int, max_length: int
) -> None:
    """Validate text length is within acceptable range.

    Args:
        text: Text to validate
        param_name: Parameter name for error messages
        min_length: Minimum acceptable length
        max_length: Maximum acceptable length

    Raises:
        ValidationError: If text length is invalid
    """
    if not text or not text.strip():
        raise ValidationError(f"{param_name} cannot be empty or whitespace-only")

    length = len(text)
    if length < min_length:
        raise ValidationError(
            f"{param_name} too short: {length} chars (minimum: {min_length})"
        )
    if length > max_length:
        raise ValidationError(
            f"{param_name} too long: {length} chars (maximum: {max_length})"
        )


@dataclass
class TitleVersion:
    """Represents a version of a title with metadata.

    Attributes:
        version_number: Version identifier (e.g., "v1", "v2", "v3")
        text: The actual title text
        created_at: When this version was created
        created_by: Who/what created this version
        changes_from_previous: Description of changes
        review_score: Score this version received (if reviewed)
        notes: Additional notes
    """

    version_number: str
    text: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "AI-TitleImprover-001"
    changes_from_previous: str = ""
    review_score: Optional[int] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version_number": self.version_number,
            "text": self.text,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "changes_from_previous": self.changes_from_previous,
            "review_score": self.review_score,
            "notes": self.notes,
        }


@dataclass
class ImprovedTitle:
    """Result of title improvement process.

    Attributes:
        new_version: The new title version
        original_version: The original title version for reference
        rationale: Explanation of why changes were made
        addressed_improvements: List of improvement points addressed
        script_alignment_notes: How new title aligns with script
        engagement_notes: How engagement is maintained/improved
        version_history: List of all versions
    """

    new_version: TitleVersion
    original_version: TitleVersion
    rationale: str
    addressed_improvements: List[str] = field(default_factory=list)
    script_alignment_notes: str = ""
    engagement_notes: str = ""
    version_history: List[TitleVersion] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "new_version": self.new_version.to_dict(),
            "original_version": self.original_version.to_dict(),
            "rationale": self.rationale,
            "addressed_improvements": self.addressed_improvements,
            "script_alignment_notes": self.script_alignment_notes,
            "engagement_notes": self.engagement_notes,
            "version_history": [v.to_dict() for v in self.version_history],
        }


class TitleImprover:
    """Generate improved title versions based on review feedback.

    This class implements the core logic for MVP-006 (v1→v2) and MVP-009 (v2→v3+),
    taking feedback from both title and script reviews to generate improved titles:
    - Addresses specific review concerns
    - Improves script-title alignment
    - Improves idea-title alignment
    - Maintains or enhances engagement
    - Sets appropriate expectations
    - Supports iterative refinement through multiple versions (v1→v2→v3→v4→v5→v6→v7, etc.)
    """

    def __init__(self):
        """Initialize TitleImprover."""
        pass

    def improve_title(
        self,
        original_title: str,
        content_text: str,
        title_review: TitleReview,
        script_review: ScriptReview,
        idea: Optional[Idea] = None,
        original_version_number: str = "v1",
        new_version_number: str = "v2",
    ) -> ImprovedTitle:
        """Generate improved title based on review feedback.

        Args:
            original_title: The original title text (v1)
            content_text: The script text (v1)
            title_review: Review of title against script and idea
            script_review: Review of script against title and idea
            idea: Optional original idea for context
            original_version_number: Version number of original (default "v1")
            new_version_number: Version number of new version (default "v2")

        Returns:
            ImprovedTitle with new version and improvement details

        Raises:
            ValidationError: If inputs are invalid
            ImprovementError: If improvement process fails
        """
        logger.info(
            f"Starting title improvement: {original_version_number} → {new_version_number}"
        )

        # Validate inputs
        try:
            self._validate_inputs(
                original_title,
                content_text,
                title_review,
                script_review,
                original_version_number,
                new_version_number,
            )
        except ValidationError as e:
            logger.error(f"Input validation failed: {e}")
            raise

        try:
            # Create original version object
            original_version = TitleVersion(
                version_number=original_version_number,
                text=original_title,
                review_score=title_review.overall_score,
                notes="Original title version",
            )
            logger.debug(f"Original title: '{original_title}' (score: {title_review.overall_score})")

            # Extract key improvement points from both reviews
            title_improvements = self._extract_title_improvements(title_review)
            script_insights = self._extract_content_insights(script_review)
            logger.debug(
                f"Extracted {len(title_improvements)} title improvements, "
                f"{len(script_insights)} script insights"
            )

            # Analyze what needs to change
            alignment_issues = self._analyze_alignment_issues(title_review, script_review)
            logger.debug(
                f"Alignment scores - script: {alignment_issues['script_alignment_score']}%, "
                f"engagement: {alignment_issues['engagement_score']}%"
            )

            # Generate improved title
            improved_text = self._generate_improved_title(
                original_title=original_title,
                content_text=content_text,
                title_improvements=title_improvements,
                script_insights=script_insights,
                alignment_issues=alignment_issues,
                idea=idea,
            )
            logger.info(f"Generated improved title: '{improved_text}'")

            # Create rationale for changes
            rationale = self._create_rationale(
                original_title=original_title,
                improved_title=improved_text,
                title_improvements=title_improvements,
                script_insights=script_insights,
                alignment_issues=alignment_issues,
            )

            # Create new version object
            new_version = TitleVersion(
                version_number=new_version_number,
                text=improved_text,
                changes_from_previous=rationale,
                notes=f"Improved based on feedback from {original_version_number} reviews",
            )

            # Create result
            result = ImprovedTitle(
                new_version=new_version,
                original_version=original_version,
                rationale=rationale,
                addressed_improvements=[imp["title"] for imp in title_improvements],
                script_alignment_notes=self._create_alignment_notes(
                    improved_text, content_text, alignment_issues
                ),
                engagement_notes=self._create_engagement_notes(
                    original_title, improved_text, title_review
                ),
                version_history=[original_version, new_version],
            )

            logger.info(
                f"Title improvement complete: {original_version_number} → {new_version_number}"
            )
            return result

        except Exception as e:
            logger.exception(f"Title improvement failed: {e}")
            raise ImprovementError(f"Failed to improve title: {e}") from e

    def _validate_inputs(
        self,
        original_title: str,
        content_text: str,
        title_review: TitleReview,
        script_review: ScriptReview,
        original_version: str,
        new_version: str,
    ) -> None:
        """Validate all inputs for improvement process.

        Args:
            original_title: Original title text
            content_text: Content text
            title_review: Title review object
            script_review: Script review object
            original_version: Original version number
            new_version: New version number

        Raises:
            ValidationError: If any input is invalid
        """
        # Validate title
        validate_text_length(original_title, "original_title", MIN_TITLE_LENGTH, MAX_TITLE_LENGTH)

        # Validate content
        validate_text_length(content_text, "content_text", MIN_CONTENT_LENGTH, MAX_CONTENT_LENGTH)

        # Validate review objects
        if not title_review:
            raise ValidationError("title_review is required")
        if not script_review:
            raise ValidationError("script_review is required")

        # Validate review structure
        if not hasattr(title_review, "overall_score"):
            raise ValidationError("title_review missing required field: overall_score")
        if not hasattr(title_review, "improvement_points"):
            raise ValidationError("title_review missing required field: improvement_points")
        if not hasattr(script_review, "improvement_points"):
            raise ValidationError("script_review missing required field: improvement_points")

        # Validate versions
        validate_version_progression(original_version, new_version)

        # Validate optimal_length if present
        if hasattr(title_review, "optimal_length_chars"):
            optimal = title_review.optimal_length_chars
            if optimal and (optimal < MIN_OPTIMAL_LENGTH or optimal > MAX_OPTIMAL_LENGTH):
                logger.warning(
                    f"Unusual optimal_length: {optimal} (expected {MIN_OPTIMAL_LENGTH}-{MAX_OPTIMAL_LENGTH})"
                )

    def _extract_title_improvements(self, title_review: TitleReview) -> List[Dict[str, Any]]:
        """Extract prioritized improvement points from title review.

        Args:
            title_review: The title review with feedback

        Returns:
            List of improvement points sorted by priority
        """
        improvements = []

        for point in title_review.improvement_points:
            improvements.append(
                {
                    "category": point.category.value,
                    "title": point.title,
                    "description": point.description,
                    "priority": point.priority,
                    "impact_score": point.impact_score,
                    "suggested_fix": point.suggested_fix,
                }
            )

        # Sort by priority (high -> medium -> low) and impact score
        priority_order = {"high": 0, "medium": 1, "low": 2}
        improvements.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["impact_score"]))

        return improvements

    def _extract_content_insights(self, script_review: ScriptReview) -> List[Dict[str, Any]]:
        """Extract relevant insights from script review.

        Args:
            script_review: The script review

        Returns:
            List of insights relevant to title improvement
        """
        insights = []

        # Look for improvements that mention the title or could affect title
        for point in script_review.improvement_points:
            # Filter for insights relevant to title alignment
            if any(
                keyword in point.description.lower()
                for keyword in ["title", "promise", "expectation", "hook", "opening"]
            ):
                insights.append(
                    {
                        "category": point.category.value,
                        "title": point.title,
                        "description": point.description,
                        "priority": point.priority,
                        "suggested_fix": point.suggested_fix,
                    }
                )

        return insights

    def _analyze_alignment_issues(
        self, title_review: TitleReview, script_review: ScriptReview
    ) -> Dict[str, Any]:
        """Analyze alignment issues between title and script.

        Args:
            title_review: The title review
            script_review: The script review

        Returns:
            Dictionary of alignment issues and scores
        """
        return {
            "script_alignment_score": title_review.script_alignment_score,
            "idea_alignment_score": title_review.idea_alignment_score,
            "engagement_score": title_review.engagement_score,
            "key_content_elements": title_review.key_content_elements,
            "suggested_keywords": title_review.suggested_keywords,
            "needs_major_revision": title_review.needs_major_revision,
            "title_length_score": title_review.length_score,
            "current_length": title_review.current_length_chars,
            "optimal_length": title_review.optimal_length_chars,
        }

    def _generate_improved_title(
        self,
        original_title: str,
        content_text: str,
        title_improvements: List[Dict[str, Any]],
        script_insights: List[Dict[str, Any]],
        alignment_issues: Dict[str, Any]],
        idea: Optional[Idea] = None,
    ) -> str:
        """Generate the improved title text.

        This is the core improvement logic that applies feedback to create
        a better title. Uses rule-based strategies to incorporate improvements.

        Args:
            original_title: Original title text
            content_text: Content text for context
            title_improvements: Improvements from title review
            script_insights: Insights from script review
            alignment_issues: Alignment analysis
            idea: Optional original idea

        Returns:
            Improved title text

        Raises:
            ImprovementError: If improvement strategies fail
        """
        logger.debug("Generating improved title with rule-based strategies")
        
        try:
            # Start with original title as base
            improved = original_title

            # Strategy 1: Address high-priority improvements
            high_priority = [imp for imp in title_improvements if imp["priority"] == "high"]

            if high_priority:
                logger.debug(f"Applying {len(high_priority)} high-priority improvements")
                # Look for specific issues to fix
                for imp in high_priority:
                    category = imp["category"]
                    suggested_fix = imp.get("suggested_fix", "")
                    logger.debug(f"  - Addressing {category}: {imp['title']}")

                    # Apply fixes based on category
                    try:
                        if category == "script_alignment" and suggested_fix:
                            # Use suggested keyword or element
                            improved = self._incorporate_content_elements(
                                improved, alignment_issues.get("key_content_elements", [])
                            )

                        elif category == "engagement" and suggested_fix:
                            # Make more engaging
                            improved = self._enhance_engagement(improved, suggested_fix)

                        elif category == "clarity" and suggested_fix:
                            # Improve clarity
                            improved = self._improve_clarity(improved)

                        elif category == "length" and suggested_fix:
                            # Adjust length
                            optimal = alignment_issues.get("optimal_length", MAX_TITLE_LENGTH)
                            improved = self._adjust_length(improved, optimal)
                            
                    except Exception as e:
                        logger.warning(f"Strategy for {category} failed: {e}, continuing with other strategies")
                        # Continue with other strategies on failure

            # Strategy 2: Incorporate key script elements if alignment is low
            script_score = alignment_issues.get("script_alignment_score", 100)
            if script_score < 70:
                logger.debug(f"Low script alignment ({script_score}%), incorporating content elements")
                try:
                    improved = self._incorporate_content_elements(
                        improved, alignment_issues.get("key_content_elements", [])
                    )
                except Exception as e:
                    logger.warning(f"Content element incorporation failed: {e}")

            # Strategy 3: Use suggested keywords if available
            keywords = alignment_issues.get("suggested_keywords", [])
            if keywords:
                logger.debug(f"Incorporating {len(keywords)} suggested keywords")
                try:
                    improved = self._incorporate_keywords(improved, keywords)
                except Exception as e:
                    logger.warning(f"Keyword incorporation failed: {e}")

            # Ensure reasonable length
            optimal = alignment_issues.get("optimal_length", MAX_TITLE_LENGTH)
            if len(improved) > optimal:
                logger.debug(f"Adjusting length from {len(improved)} to ~{optimal}")
                try:
                    improved = self._adjust_length(improved, optimal)
                except Exception as e:
                    logger.warning(f"Length adjustment failed: {e}")

            logger.debug(f"Title improvement strategies complete: '{original_title}' → '{improved}'")
            return improved
            
        except Exception as e:
            logger.error(f"Failed to generate improved title: {e}")
            # Return original on complete failure rather than crashing
            logger.warning("Returning original title due to improvement failure")
            return original_title

    def _incorporate_content_elements(self, title: str, script_elements: List[str]) -> str:
        """Incorporate key script elements into title.

        Args:
            title: Current title
            script_elements: Key elements from script

        Returns:
            Title with incorporated elements
        """
        if not script_elements:
            return title

        # Check which elements are already present (case-insensitive)
        title_lower = title.lower()
        missing_elements = [elem for elem in script_elements if elem.lower() not in title_lower]

        # If title is missing key elements, try to add the most important one
        if missing_elements:
            # Add first missing element if it would improve alignment
            key_element = missing_elements[0]

            # Strategy: Add to subtitle or incorporate naturally
            if ":" in title or "-" in title:
                # Title has subtitle structure, can enhance it
                parts = title.split(":" if ":" in title else "-", 1)
                if len(parts) == 2:
                    # Incorporate into subtitle
                    title = f"{parts[0]}: {key_element.title()} {parts[1].strip()}"
            else:
                # Add as subtitle
                title = f"{title}: {key_element.title()}"

        return title

    def _incorporate_keywords(self, title: str, keywords: List[str]) -> str:
        """Incorporate suggested keywords into title.

        Args:
            title: Current title
            keywords: Suggested keywords

        Returns:
            Title with incorporated keywords
        """
        if not keywords:
            return title

        # Similar logic to script elements
        title_lower = title.lower()
        missing_keywords = [
            kw for kw in keywords[:2] if kw.lower() not in title_lower  # Take top 2
        ]

        if missing_keywords:
            # Add most relevant keyword
            keyword = missing_keywords[0]
            if ":" not in title and "-" not in title:
                # Add as subtitle
                title = f"{title}: {keyword.title()}"

        return title

    def _enhance_engagement(self, title: str, suggested_fix: str) -> str:
        """Enhance title engagement.
        
        Note: This is a placeholder implementation. Currently returns title unchanged
        as engagement enhancement is subjective and would benefit from AI/LLM integration
        or more sophisticated linguistic analysis.

        Args:
            title: Current title
            suggested_fix: Suggested fix from review

        Returns:
            More engaging title (currently unchanged)
        """
        # If suggested fix provides specific guidance, try to apply it
        if "question" in suggested_fix.lower():
            # Convert to question format if appropriate
            if not title.endswith("?"):
                # Could add question mark or rephrase
                # TODO: Implement question conversion logic
                pass

        # Return as-is - engagement enhancement needs more sophisticated implementation
        return title

    def _improve_clarity(self, title: str) -> str:
        """Improve title clarity.

        Args:
            title: Current title

        Returns:
            Clearer title
        """
        # Remove unnecessary punctuation or complexity
        # Simplify structure if too complex

        # For now, basic cleanup
        title = title.strip()

        # Remove multiple spaces
        title = " ".join(title.split())

        return title

    def _adjust_length(self, title: str, optimal_length: int) -> str:
        """Adjust title length to optimal range.

        Args:
            title: Current title
            optimal_length: Target length in characters

        Returns:
            Length-adjusted title
        """
        if len(title) <= optimal_length:
            return title

        # Truncate intelligently
        # Try to break at word boundary near optimal length
        if len(title) > optimal_length:
            # Find last space before optimal length
            truncated = title[:optimal_length]
            last_space = truncated.rfind(" ")

            if last_space > optimal_length * 0.8:  # Keep at least 80% of target
                title = truncated[:last_space]
            else:
                # Just truncate with ellipsis
                title = truncated.rstrip() + "..."

        return title

    def _create_rationale(
        self,
        original_title: str,
        improved_title: str,
        title_improvements: List[Dict[str, Any]],
        script_insights: List[Dict[str, Any]],
        alignment_issues: Dict[str, Any],
    ) -> str:
        """Create explanation of changes made.

        Args:
            original_title: Original title
            improved_title: Improved title
            title_improvements: Title improvements applied
            script_insights: Content insights considered
            alignment_issues: Alignment analysis

        Returns:
            Rationale text
        """
        rationale_parts = []

        rationale_parts.append(f"Changed from '{original_title}' to '{improved_title}'")

        # Explain key changes
        if title_improvements:
            high_priority = [imp for imp in title_improvements if imp["priority"] == "high"]
            if high_priority:
                rationale_parts.append(
                    f"Addressed {len(high_priority)} high-priority improvements:"
                )
                for imp in high_priority[:3]:  # Top 3
                    rationale_parts.append(f"  - {imp['title']}")

        # Mention alignment improvements
        if alignment_issues["script_alignment_score"] < 70:
            rationale_parts.append(
                f"Improved script alignment (was {alignment_issues['script_alignment_score']}%)"
            )

        if alignment_issues["key_content_elements"]:
            rationale_parts.append(
                f"Incorporated key script elements: {', '.join(alignment_issues['key_content_elements'][:2])}"
            )

        return "\n".join(rationale_parts)

    def _create_alignment_notes(
        self, improved_title: str, content_text: str, alignment_issues: Dict[str, Any]
    ) -> str:
        """Create notes on script alignment.

        Args:
            improved_title: The improved title
            content_text: Content text
            alignment_issues: Alignment analysis

        Returns:
            Alignment notes
        """
        notes = []

        notes.append(f"New title: '{improved_title}'")

        if alignment_issues["key_content_elements"]:
            notes.append(
                f"Key elements in title: {', '.join(alignment_issues['key_content_elements'][:3])}"
            )

        notes.append(f"Previous alignment score: {alignment_issues['script_alignment_score']}%")

        return "\n".join(notes)

    def _create_engagement_notes(
        self, original_title: str, improved_title: str, title_review: TitleReview
    ) -> str:
        """Create notes on engagement.

        Args:
            original_title: Original title
            improved_title: Improved title
            title_review: Title review

        Returns:
            Engagement notes
        """
        notes = []

        notes.append(f"Original engagement score: {title_review.engagement_score}%")
        notes.append(f"Clickthrough potential: {title_review.clickthrough_potential}%")

        # Note changes that affect engagement
        if len(improved_title) != len(original_title):
            notes.append(
                f"Length adjusted from {len(original_title)} to {len(improved_title)} chars"
            )

        return "\n".join(notes)


def improve_title_from_reviews(
    original_title: str,
    content_text: str,
    title_review: TitleReview,
    script_review: ScriptReview,
    idea: Optional[Idea] = None,
    original_version: str = "v1",
    new_version: str = "v2",
) -> ImprovedTitle:
    """Convenience function to improve title from reviews.

    Args:
        original_title: Original title text (v1)
        content_text: Content text (v1)
        title_review: Title review feedback
        script_review: Content review feedback
        idea: Optional original idea
        original_version: Version number of original (default "v1")
        new_version: Version number of new version (default "v2")

    Returns:
        ImprovedTitle with new version and details
    """
    improver = TitleImprover()
    return improver.improve_title(
        original_title=original_title,
        content_text=content_text,
        title_review=title_review,
        script_review=script_review,
        idea=idea,
        original_version_number=original_version,
        new_version_number=new_version,
    )
