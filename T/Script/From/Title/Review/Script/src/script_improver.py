"""Script Improvement module for generating improved script versions.

This module implements script improvement using feedback from reviews.
It takes original script, title, and reviews to generate improved versions.

Workflow Position:
    Script vN + Title vN + Reviews → Script v(N+1) (improved)
"""

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directories to path for imports
current_file = Path(__file__)
t_module_dir = current_file.parent.parent.parent.parent.parent.parent  # T

# Import review models
sys.path.insert(0, str(t_module_dir / "Review" / "Script"))
sys.path.insert(0, str(t_module_dir / "Review" / "Title" / "From" / "Script" / "Idea"))
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
        pass

    def improve_script(
        self,
        original_script: str,
        title_text: str,
        script_review: "ScriptReview",
        title_review: Optional["TitleReview"] = None,
        original_version_number: str = "v1",
        new_version_number: str = "v2",
    ) -> ImprovedScript:
        """Generate improved script based on review feedback.

        Args:
            original_script: The original script text
            title_text: The title text
            script_review: Review of script
            title_review: Optional title review
            original_version_number: Version number of original
            new_version_number: Version number of new version

        Returns:
            ImprovedScript with new version and improvement details
        """
        if not original_script:
            raise ValueError("Original script cannot be empty")
        if not title_text:
            raise ValueError("Title text cannot be empty")
        if not script_review:
            raise ValueError("Script review is required")

        # Create original version object
        original_version = ScriptVersion(
            version_number=original_version_number,
            text=original_script,
            review_score=script_review.overall_score,
            notes="Original script version",
        )

        # Extract improvement points
        improvements = self._extract_improvements(script_review)

        # Generate improved script
        improved_text = self._generate_improved_script(
            original_script=original_script,
            title_text=title_text,
            improvements=improvements,
            script_review=script_review,
        )

        # Create rationale
        rationale = self._create_rationale(
            original_script=original_script,
            improved_script=improved_text,
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
            title_alignment_notes=self._create_title_alignment_notes(title_text, improved_text),
            structure_notes=self._create_structure_notes(improved_text),
            version_history=[original_version, new_version],
        )

        return result

    def _extract_improvements(self, script_review: "ScriptReview") -> List[Dict[str, Any]]:
        """Extract prioritized improvement points from script review."""
        improvements = []

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
        improvements.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["impact_score"]))

        return improvements

    def _generate_improved_script(
        self,
        original_script: str,
        title_text: str,
        improvements: List[Dict[str, Any]],
        script_review: "ScriptReview",
    ) -> str:
        """Generate the improved script text.

        This is where the core improvement logic lives.
        In production, this would use AI to rewrite sections.
        For MVP, we apply rule-based improvements.
        """
        improved = original_script

        # Strategy 1: Address high-priority improvements
        high_priority = [imp for imp in improvements if imp["priority"] == "high"]

        for imp in high_priority[:3]:  # Handle top 3 high-priority issues
            category = imp["category"]
            suggested_fix = imp.get("suggested_fix", "")

            if "opening" in imp["description"].lower() or "hook" in imp["description"].lower():
                # Improve opening/hook
                improved = self._improve_opening(improved, title_text, suggested_fix)

            elif (
                "conclusion" in imp["description"].lower() or "ending" in imp["description"].lower()
            ):
                # Improve conclusion
                improved = self._improve_conclusion(improved, suggested_fix)

            elif "title" in imp["description"].lower() or "promise" in imp["description"].lower():
                # Improve title alignment
                improved = self._improve_title_alignment(improved, title_text)

        # Ensure script maintains good structure
        improved = self._ensure_structure(improved)

        return improved

    def _improve_opening(self, script: str, title: str, suggested_fix: str) -> str:
        """Improve the opening of the script."""
        lines = script.split("\n")

        if lines:
            # Add stronger opening that references title
            enhanced_opening = f"What if I told you about {title.lower()}? This is a story that will change how you think about everything."

            # Prepend if opening seems weak
            if len(lines[0]) < 50:
                lines[0] = enhanced_opening + "\n\n" + lines[0]

        return "\n".join(lines)

    def _improve_conclusion(self, script: str, suggested_fix: str) -> str:
        """Improve the conclusion of the script."""
        lines = script.split("\n")

        # Add stronger conclusion if ending seems weak
        if lines and len(lines[-1]) < 30:
            lines.append(
                "\n\nAnd that's the story you needed to hear today. What do you think? Let me know in the comments."
            )

        return "\n".join(lines)

    def _improve_title_alignment(self, script: str, title: str) -> str:
        """Improve alignment between script and title."""
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

    def _ensure_structure(self, script: str) -> str:
        """Ensure script has good structure."""
        # Clean up multiple blank lines
        while "\n\n\n" in script:
            script = script.replace("\n\n\n", "\n\n")

        return script.strip()

    def _create_rationale(
        self, original_script: str, improved_script: str, improvements: List[Dict[str, Any]]
    ) -> str:
        """Create explanation of changes made."""
        rationale_parts = []

        original_len = len(original_script)
        improved_len = len(improved_script)

        rationale_parts.append(f"Script length: {original_len} → {improved_len} characters")

        if improvements:
            high_priority = [imp for imp in improvements if imp["priority"] == "high"]
            if high_priority:
                rationale_parts.append(
                    f"Addressed {len(high_priority)} high-priority improvements:"
                )
                for imp in high_priority[:3]:
                    rationale_parts.append(f"  - {imp['title']}")

        return "\n".join(rationale_parts)

    def _create_title_alignment_notes(self, title: str, script: str) -> str:
        """Create notes on title alignment."""
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

    def _create_structure_notes(self, script: str) -> str:
        """Create notes on script structure."""
        paragraphs = script.split("\n\n")
        word_count = len(script.split())

        notes = []
        notes.append(f"Total paragraphs: {len(paragraphs)}")
        notes.append(f"Total words: {word_count}")
        notes.append(f"Estimated duration: {word_count // 150} minutes (at 150 wpm)")

        return "\n".join(notes)


def improve_script_from_reviews(
    original_script: str,
    title_text: str,
    script_review: "ScriptReview",
    title_review: Optional["TitleReview"] = None,
    original_version: str = "v1",
    new_version: str = "v2",
) -> ImprovedScript:
    """Convenience function to improve script from reviews.

    Args:
        original_script: Original script text
        title_text: Title text
        script_review: Script review feedback
        title_review: Optional title review
        original_version: Version number of original
        new_version: Version number of new version

    Returns:
        ImprovedScript with new version and details
    """
    improver = ScriptImprover()
    return improver.improve_script(
        original_script=original_script,
        title_text=title_text,
        script_review=script_review,
        title_review=title_review,
        original_version_number=original_version,
        new_version_number=new_version,
    )
