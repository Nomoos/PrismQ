"""Content Improvement module for generating improved script versions.

This module implements script improvement using feedback from reviews.
It takes original script, title, and reviews to generate improved versions.

Workflow Position:
    Content vN + Title vN + Reviews → Content v(N+1) (improved)
"""

import hashlib
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Configure module logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Constants for validation
MAX_TEXT_LENGTH = 1_000_000  # 1MB of text
MAX_TITLE_LENGTH = 500
MIN_TEXT_LENGTH = 10
MIN_TITLE_LENGTH = 3

# Performance thresholds
LARGE_TEXT_WARNING_SIZE = 50_000  # Characters


def timing_decorator(func: Callable) -> Callable:
    """Decorator to log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.debug(f"Starting {func.__name__}")
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"{func.__name__} completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed:.2f}s: {e}")
            raise
    return wrapper


def sanitize_text(text: str, max_length: int = MAX_TEXT_LENGTH) -> str:
    """Sanitize user input text.
    
    Args:
        text: Raw text input
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
        
    Raises:
        ValueError: If text is invalid
    """
    if not isinstance(text, str):
        raise ValueError(f"Text must be string, got {type(text)}")
    
    # Remove null bytes that can break databases
    text = text.replace('\x00', '')
    
    # Limit length
    if len(text) > max_length:
        logger.warning(f"Text truncated from {len(text)} to {max_length} characters")
        text = text[:max_length]
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def validate_text_input(text: str, min_length: int = MIN_TEXT_LENGTH, 
                       max_length: int = MAX_TEXT_LENGTH, 
                       field_name: str = "text") -> None:
    """Validate text input parameters.
    
    Args:
        text: Text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        field_name: Name of field for error messages
        
    Raises:
        ValueError: If validation fails
    """
    if text is None:
        raise ValueError(f"{field_name} cannot be None")
    
    if not isinstance(text, str):
        raise ValueError(f"{field_name} must be string, got {type(text)}")
    
    if not text or not text.strip():
        raise ValueError(f"{field_name} cannot be empty")
    
    text_len = len(text.strip())
    
    if text_len < min_length:
        raise ValueError(
            f"{field_name} too short: {text_len} chars (minimum: {min_length})"
        )
    
    if text_len > max_length:
        raise ValueError(
            f"{field_name} too long: {text_len} chars (maximum: {max_length})"
        )
    
    logger.debug(f"{field_name} validation passed: {text_len} chars")


def validate_score(score: int, field_name: str = "score") -> None:
    """Validate score is in valid range.
    
    Args:
        score: Score value to validate
        field_name: Name of field for error messages
        
    Raises:
        ValueError: If score is invalid
    """
    if not isinstance(score, (int, float)):
        raise ValueError(f"{field_name} must be numeric, got {type(score)}")
    
    if not 0 <= score <= 100:
        raise ValueError(f"{field_name} must be 0-100, got {score}")
    
    logger.debug(f"{field_name} validation passed: {score}")


def generate_deterministic_id(content: str, title: str, version: str) -> str:
    """Generate deterministic SHA256-based ID for idempotency.
    
    Args:
        content: Script content
        title: Title text
        version: Version number
        
    Returns:
        Deterministic hex ID
    """
    combined = f"{content}|{title}|{version}"
    hash_obj = hashlib.sha256(combined.encode('utf-8'))
    return hash_obj.hexdigest()[:16]  # 16 chars is sufficient


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, avoiding division by zero.
    
    Args:
        numerator: Number to divide
        denominator: Number to divide by
        default: Default value if division fails
        
    Returns:
        Result of division or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (ZeroDivisionError, TypeError):
        return default

# Add parent directories to path for imports
current_file = Path(__file__)
t_module_dir = current_file.parent.parent.parent.parent.parent.parent  # T

# Import review models
sys.path.insert(0, str(t_module_dir / "Review" / "Content"))
sys.path.insert(0, str(t_module_dir / "Review" / "Title" / "From" / "Content" / "Idea"))
sys.path.insert(0, str(t_module_dir / "Idea" / "Model" / "src"))

try:
    from script_review import ImprovementPoint, ReviewCategory, ScriptReview

    SCRIPT_REVIEW_AVAILABLE = True
except ImportError:
    SCRIPT_REVIEW_AVAILABLE = False

try:
    from title_review import TitleReview

    TITLE_REVIEW_AVAILABLE = True
except ImportError:
    TITLE_REVIEW_AVAILABLE = False


@dataclass
class ScriptVersion:
    """Represents a version of a script with metadata."""

    version_number: str
    text: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "AI-ScriptImprover-001"
    changes_from_previous: str = ""
    review_score: Optional[int] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version_number": self.version_number,
            "text": self.text[:500] + "..." if len(self.text) > 500 else self.text,
            "full_text_length": len(self.text),
            "created_at": self.created_at,
            "created_by": self.created_by,
            "changes_from_previous": self.changes_from_previous,
            "review_score": self.review_score,
            "notes": self.notes,
        }


@dataclass
class ImprovedScript:
    """Result of script improvement process."""

    new_version: ScriptVersion
    original_version: ScriptVersion
    rationale: str
    addressed_improvements: List[str] = field(default_factory=list)
    title_alignment_notes: str = ""
    structure_notes: str = ""
    version_history: List[ScriptVersion] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "new_version": self.new_version.to_dict(),
            "original_version": self.original_version.to_dict(),
            "rationale": self.rationale,
            "addressed_improvements": self.addressed_improvements,
            "title_alignment_notes": self.title_alignment_notes,
            "structure_notes": self.structure_notes,
            "version_history": [v.to_dict() for v in self.version_history],
        }


class ScriptImprover:
    """Generate improved script versions based on review feedback."""

    def __init__(self):
        """Initialize ScriptImprover."""
        logger.info("ScriptImprover initialized")

    @timing_decorator
    def improve_content(
        self,
        original_content: str,
        title_text: str,
        script_review: "ScriptReview",
        title_review: Optional["TitleReview"] = None,
        original_version_number: str = "v1",
        new_version_number: str = "v2",
    ) -> ImprovedScript:
        """Generate improved script based on review feedback.

        Args:
            original_content: The original script text
            title_text: The title text
            script_review: Review of script
            title_review: Optional title review
            original_version_number: Version number of original
            new_version_number: Version number of new version

        Returns:
            ImprovedScript with new version and improvement details
            
        Raises:
            ValueError: If validation fails
        """
        logger.info(
            f"Starting content improvement: {original_version_number} -> {new_version_number}"
        )
        
        # Validate inputs
        try:
            validate_text_input(
                original_content, 
                min_length=MIN_TEXT_LENGTH, 
                max_length=MAX_TEXT_LENGTH,
                field_name="original_content"
            )
            validate_text_input(
                title_text,
                min_length=MIN_TITLE_LENGTH,
                max_length=MAX_TITLE_LENGTH,
                field_name="title_text"
            )
            
            if script_review is None:
                raise ValueError("script_review is required")
            
            if not isinstance(original_version_number, str) or not original_version_number:
                raise ValueError("original_version_number must be non-empty string")
            
            if not isinstance(new_version_number, str) or not new_version_number:
                raise ValueError("new_version_number must be non-empty string")
            
            # Validate review score
            if hasattr(script_review, 'overall_score'):
                validate_score(script_review.overall_score, "script_review.overall_score")
                
        except ValueError as e:
            logger.error(f"Input validation failed: {e}")
            raise
        
        # Sanitize inputs
        original_content = sanitize_text(original_content, MAX_TEXT_LENGTH)
        title_text = sanitize_text(title_text, MAX_TITLE_LENGTH)
        
        # Warn about large content
        if len(original_content) > LARGE_TEXT_WARNING_SIZE:
            logger.warning(
                f"Processing large content: {len(original_content)} chars. "
                "This may be slow."
            )

        try:
            # Create original version object
            original_version = ScriptVersion(
                version_number=original_version_number,
                text=original_content,
                review_score=script_review.overall_score,
                notes="Original script version",
            )
            
            logger.debug(f"Original version created: {original_version_number}")

            # Extract improvement points
            improvements = self._extract_improvements(script_review)
            logger.info(f"Extracted {len(improvements)} improvement points")

            # Generate improved script
            improved_text = self._generate_improved_content(
                original_content=original_content,
                title_text=title_text,
                improvements=improvements,
                script_review=script_review,
            )
            
            logger.debug(
                f"Content improved: {len(original_content)} -> {len(improved_text)} chars"
            )

            # Create rationale
            rationale = self._create_rationale(
                original_content=original_content,
                improved_content=improved_text,
                improvements=improvements,
            )

            # Create new version object
            new_version = ScriptVersion(
                version_number=new_version_number,
                text=improved_text,
                changes_from_previous=rationale,
                notes=f"Improved based on feedback from {original_version_number} reviews",
            )

            # Create result
            result = ImprovedScript(
                new_version=new_version,
                original_version=original_version,
                rationale=rationale,
                addressed_improvements=[imp["title"] for imp in improvements[:5]],
                title_alignment_notes=self._create_title_alignment_notes(
                    title_text, improved_text
                ),
                structure_notes=self._create_structure_notes(improved_text),
                version_history=[original_version, new_version],
            )
            
            logger.info(
                f"Content improvement completed: "
                f"{len(improvements)} improvements addressed"
            )

            return result
            
        except Exception as e:
            logger.exception(f"Content improvement failed: {e}")
            raise

    def _extract_improvements(self, script_review: "ScriptReview") -> List[Dict[str, Any]]:
        """Extract prioritized improvement points from script review.
        
        Args:
            script_review: Review object with improvement points
            
        Returns:
            List of improvement dictionaries sorted by priority
        """
        logger.debug("Extracting improvement points from review")
        improvements = []

        try:
            for point in script_review.improvement_points:
                improvements.append(
                    {
                        "category": (
                            point.category.value
                            if hasattr(point.category, "value")
                            else str(point.category)
                        ),
                        "title": point.title,
                        "description": point.description,
                        "priority": point.priority,
                        "impact_score": point.impact_score,
                        "suggested_fix": point.suggested_fix,
                    }
                )

            # Sort by priority and impact
            priority_order = {"high": 0, "medium": 1, "low": 2}
            improvements.sort(
                key=lambda x: (priority_order.get(x["priority"], 3), -x["impact_score"])
            )
            
            logger.debug(f"Extracted {len(improvements)} improvement points")
            return improvements
            
        except Exception as e:
            logger.error(f"Error extracting improvements: {e}")
            return []  # Return empty list on error

    def _generate_improved_content(
        self,
        original_content: str,
        title_text: str,
        improvements: List[Dict[str, Any]],
        script_review: "ScriptReview",
    ) -> str:
        """Generate the improved script text.

        This is where the core improvement logic lives.
        In production, this would use AI to rewrite sections.
        For MVP, we apply rule-based improvements.
        
        Args:
            original_content: Original script text
            title_text: Title text
            improvements: List of improvement points
            script_review: Review object
            
        Returns:
            Improved script text
        """
        logger.debug("Generating improved content")
        
        try:
            improved = original_content

            # Strategy 1: Address high-priority improvements
            high_priority = [imp for imp in improvements if imp["priority"] == "high"]
            logger.debug(f"Addressing {len(high_priority)} high-priority improvements")

            for imp in high_priority[:3]:  # Handle top 3 high-priority issues
                category = imp["category"]
                suggested_fix = imp.get("suggested_fix", "")

                try:
                    if "opening" in imp["description"].lower() or "hook" in imp["description"].lower():
                        # Improve opening/hook
                        improved = self._improve_opening(improved, title_text, suggested_fix)

                    elif (
                        "conclusion" in imp["description"].lower() 
                        or "ending" in imp["description"].lower()
                    ):
                        # Improve conclusion
                        improved = self._improve_conclusion(improved, suggested_fix)

                    elif "title" in imp["description"].lower() or "promise" in imp["description"].lower():
                        # Improve title alignment
                        improved = self._improve_title_alignment(improved, title_text)
                        
                except Exception as e:
                    logger.warning(f"Failed to apply improvement '{imp['title']}': {e}")
                    continue  # Skip this improvement and continue with others

            # Ensure script maintains good structure
            improved = self._ensure_structure(improved)
            
            logger.debug("Content improvement generation completed")
            return improved
            
        except Exception as e:
            logger.error(f"Error generating improved content: {e}")
            # Return original on failure
            return original_content

    def _improve_opening(self, script: str, title: str, suggested_fix: str) -> str:
        """Improve the opening of the script.
        
        Args:
            script: Script text
            title: Title text
            suggested_fix: Suggested improvement
            
        Returns:
            Script with improved opening
        """
        try:
            lines = script.split("\n")

            if lines:
                # Add stronger opening that references title
                enhanced_opening = (
                    f"What if I told you about {title.lower()}? "
                    "This is a story that will change how you think about everything."
                )

                # Prepend if opening seems weak
                if len(lines[0]) < 50:
                    lines[0] = enhanced_opening + "\n\n" + lines[0]

            return "\n".join(lines)
        except Exception as e:
            logger.warning(f"Failed to improve opening: {e}")
            return script  # Return original on error

    def _improve_conclusion(self, script: str, suggested_fix: str) -> str:
        """Improve the conclusion of the script.
        
        Args:
            script: Script text
            suggested_fix: Suggested improvement
            
        Returns:
            Script with improved conclusion
        """
        try:
            lines = script.split("\n")

            # Add stronger conclusion if ending seems weak
            if lines and len(lines[-1]) < 30:
                lines.append(
                    "\n\nAnd that's the story you needed to hear today. "
                    "What do you think? Let me know in the comments."
                )

            return "\n".join(lines)
        except Exception as e:
            logger.warning(f"Failed to improve conclusion: {e}")
            return script  # Return original on error

    def _improve_title_alignment(self, script: str, title: str) -> str:
        """Improve alignment between script and title.
        
        Args:
            script: Script text
            title: Title text
            
        Returns:
            Script with improved title alignment
        """
        try:
            # Extract key words from title
            title_words = [w.lower() for w in title.split() if len(w) > 3]

            # Check if any key title words are missing from script
            script_lower = script.lower()
            missing_words = [w for w in title_words if w not in script_lower]

            if missing_words:
                # Add reference to missing key words
                addition = f"\n\nThis is all connected to {' and '.join(missing_words[:2])}."
                script += addition

            return script
        except Exception as e:
            logger.warning(f"Failed to improve title alignment: {e}")
            return script  # Return original on error

    def _ensure_structure(self, script: str) -> str:
        """Ensure script has good structure.
        
        Args:
            script: Script text
            
        Returns:
            Script with cleaned structure
        """
        try:
            # Clean up multiple blank lines
            while "\n\n\n" in script:
                script = script.replace("\n\n\n", "\n\n")

            return script.strip()
        except Exception as e:
            logger.warning(f"Failed to ensure structure: {e}")
            return script  # Return original on error

    def _create_rationale(
        self, original_content: str, improved_content: str, improvements: List[Dict[str, Any]]
    ) -> str:
        """Create explanation of changes made.
        
        Args:
            original_content: Original script text
            improved_content: Improved script text
            improvements: List of improvements applied
            
        Returns:
            Rationale text explaining changes
        """
        try:
            rationale_parts = []

            original_len = len(original_content)
            improved_len = len(improved_content)

            rationale_parts.append(f"Content length: {original_len} → {improved_len} characters")

            if improvements:
                high_priority = [imp for imp in improvements if imp["priority"] == "high"]
                if high_priority:
                    rationale_parts.append(
                        f"Addressed {len(high_priority)} high-priority improvements:"
                    )
                    for imp in high_priority[:3]:
                        rationale_parts.append(f"  - {imp['title']}")

            return "\n".join(rationale_parts)
        except Exception as e:
            logger.warning(f"Failed to create rationale: {e}")
            return "Content improved based on review feedback"

    def _create_title_alignment_notes(self, title: str, script: str) -> str:
        """Create notes on title alignment.
        
        Args:
            title: Title text
            script: Script text
            
        Returns:
            Notes on title-script alignment
        """
        try:
            title_words = [w.lower() for w in title.split() if len(w) > 3]
            script_lower = script.lower()

            present_words = [w for w in title_words if w in script_lower]
            missing_words = [w for w in title_words if w not in script_lower]

            notes = []
            notes.append(f"Title: '{title}'")
            if present_words:
                notes.append(f"Title words present in script: {', '.join(present_words)}")
            if missing_words:
                notes.append(f"Title words not in script: {', '.join(missing_words)}")

            return "\n".join(notes)
        except Exception as e:
            logger.warning(f"Failed to create title alignment notes: {e}")
            return f"Title: '{title}'"

    def _create_structure_notes(self, script: str) -> str:
        """Create notes on script structure.
        
        Args:
            script: Script text
            
        Returns:
            Notes on script structure
        """
        try:
            paragraphs = script.split("\n\n")
            word_count = len(script.split())
            estimated_minutes = safe_divide(word_count, 150, 0)

            notes = []
            notes.append(f"Total paragraphs: {len(paragraphs)}")
            notes.append(f"Total words: {word_count}")
            notes.append(f"Estimated duration: {int(estimated_minutes)} minutes (at 150 wpm)")

            return "\n".join(notes)
        except Exception as e:
            logger.warning(f"Failed to create structure notes: {e}")
            return "Structure analysis unavailable"


def improve_content_from_reviews(
    original_content: str,
    title_text: str,
    script_review: "ScriptReview",
    title_review: Optional["TitleReview"] = None,
    original_version: str = "v1",
    new_version: str = "v2",
) -> ImprovedScript:
    """Convenience function to improve script from reviews.

    Args:
        original_content: Original script text
        title_text: Title text
        script_review: Content review feedback
        title_review: Optional title review
        original_version: Version number of original
        new_version: Version number of new version

    Returns:
        ImprovedScript with new version and details
    """
    improver = ScriptImprover()
    return improver.improve_content(
        original_content=original_content,
        title_text=title_text,
        script_review=script_review,
        title_review=title_review,
        original_version_number=original_version,
        new_version_number=new_version,
    )
