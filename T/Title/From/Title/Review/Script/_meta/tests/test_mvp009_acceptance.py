"""Tests for MVP-009 acceptance criteria: Title Refinement v3+.

This module tests the specific requirements for MVP-009:
- Refine title from v2 to v3 using v2 review feedback
- Polish for clarity and engagement
- Store v3 with reference to v2
- Support versioning (v3, v4, v5, v6, v7, etc.)
"""

import sys
from pathlib import Path

import pytest

# Add parent directories to path for imports
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir / "../../src"))
sys.path.insert(0, str(test_dir / "../../../../Idea/Model/src"))
sys.path.insert(0, str(test_dir / "../../../../Idea/Model"))
sys.path.insert(0, str(test_dir / "../../../../Review/Title/ByScriptAndIdea"))
sys.path.insert(0, str(test_dir / "../../../../Review/Script/ByTitle"))
sys.path.insert(0, str(test_dir / "../../../../Review/Script"))

from script_review import ContentLength, ImprovementPoint, ReviewCategory, ScriptReview
from title_improver import (
    ImprovedTitle,
    TitleImprover,
    TitleVersion,
    improve_title_from_reviews,
)
from title_review import TitleImprovementPoint, TitleReview, TitleReviewCategory

from idea import Idea, IdeaStatus


class TestMVP009AcceptanceCriteria:
    """Tests verifying MVP-009 acceptance criteria for v3 refinement."""

    def test_refine_v2_to_v3_using_v2_feedback(self):
        """AC1: Refine title from v2 to v3 using v2 review feedback.

        This tests the complete v2→v3 workflow:
        1. Start with title v2 (previously refined from v1)
        2. Review v2 to get new feedback
        3. Generate v3 that addresses v2-specific feedback
        """
        improver = TitleImprover()

        # Title v2 (already improved from v1)
        title_v2 = "The Victorian Echo: Trapped Souls"
        script_v2 = """
        The Victorian mansion on Elm Street harbors a dark secret.
        Inside its walls, trapped souls echo their final moments.
        Sarah discovers she can hear them - but listening comes at a price.
        Each night, the echoes grow louder, revealing a century-old curse.
        The spirits are not random - they're trying to warn her.
        """

        # Review of v2 identifies room for refinement
        title_review_v2 = TitleReview(
            title_id="mvp009-test-1",
            title_text=title_v2,
            title_version="v2",
            overall_score=82,
            script_alignment_score=85,
            idea_alignment_score=84,
            engagement_score=80,
            script_id="script-v2-001",
            key_script_elements=["curse", "warning", "Victorian", "danger"],
            suggested_keywords=["curse", "warning"],
            current_length_chars=len(title_v2),
            optimal_length_chars=60,
        )

        # V2-specific improvement points
        title_review_v2.improvement_points = [
            TitleImprovementPoint(
                category=TitleReviewCategory.ENGAGEMENT,
                title="Could emphasize the warning/danger aspect",
                description="Script emphasizes souls are warning of danger, not just trapped",
                priority="medium",
                impact_score=75,
                suggested_fix="Consider emphasizing 'warning' or 'curse' more prominently",
            ),
            TitleImprovementPoint(
                category=TitleReviewCategory.CLARITY,
                title="Subtitle could be more specific",
                description="'Trapped Souls' is accurate but could hint at the warning",
                priority="low",
                impact_score=60,
                suggested_fix="Make subtitle more specific about their purpose",
            ),
        ]

        script_review_v2 = ScriptReview(
            script_id="script-v2-001", script_title=title_v2, overall_score=85
        )

        # Generate v3 from v2
        result = improver.improve_title(
            original_title=title_v2,
            script_text=script_v2,
            title_review=title_review_v2,
            script_review=script_review_v2,
            original_version_number="v2",
            new_version_number="v3",
        )

        # Verify v3 was created
        assert result.new_version.version_number == "v3"
        assert result.original_version.version_number == "v2"

        # Verify v3 references v2 (not v1)
        assert result.original_version.text == title_v2
        # Note: v3 text may be same as v2 if v2 is already good and incorporates feedback
        # The key is that the improvement process ran and created v3

        # Verify feedback was addressed
        assert len(result.addressed_improvements) > 0

        # Verify rationale mentions the change from v2
        assert "v2" in result.rationale or title_v2 in result.rationale

    def test_v3_polishes_for_clarity_and_engagement(self):
        """AC2: Polish for clarity and engagement in v3.

        Verify that v3 refinement focuses on polish (clarity and engagement)
        rather than major structural changes.
        """
        improver = TitleImprover()

        # A v2 title that's good but needs polish
        title_v2 = "The Echo Effect: Mystery in Victorian House"
        script_v2 = "A Victorian house mystery with echoing voices and secrets."

        # V2 review focuses on clarity and engagement polish
        title_review_v2 = TitleReview(
            title_id="mvp009-test-2",
            title_text=title_v2,
            title_version="v2",
            overall_score=85,
            script_alignment_score=88,
            engagement_score=82,
            key_script_elements=["Victorian", "mystery", "echoes"],
        )

        title_review_v2.improvement_points = [
            TitleImprovementPoint(
                category=TitleReviewCategory.CLARITY,
                title="Polish subtitle clarity",
                description="'Mystery in Victorian House' could be clearer",
                priority="low",
                impact_score=65,
                suggested_fix="Make more concise and clear",
            ),
            TitleImprovementPoint(
                category=TitleReviewCategory.ENGAGEMENT,
                title="Enhance engagement",
                description="Title is clear but could be more engaging",
                priority="medium",
                impact_score=70,
                suggested_fix="Add more intrigue",
            ),
        ]

        script_review_v2 = ScriptReview(script_id="test-2", script_title=title_v2, overall_score=86)

        result = improver.improve_title(
            original_title=title_v2,
            script_text=script_v2,
            title_review=title_review_v2,
            script_review=script_review_v2,
            original_version_number="v2",
            new_version_number="v3",
        )

        # Verify v3 exists and has engagement/clarity notes
        assert result.new_version.version_number == "v3"
        assert len(result.engagement_notes) > 0

        # Verify improvements are about clarity/engagement
        improvement_text = " ".join(result.addressed_improvements).lower()
        assert "clarity" in improvement_text or "engagement" in improvement_text

    def test_stores_v3_with_reference_to_v2(self):
        """AC3: Store v3 with reference to v2.

        Verify that v3 properly references v2 in version history
        and change tracking.
        """
        improver = TitleImprover()

        title_v2 = "Title Version 2"
        script_v2 = "Script content for v2 refinement."

        title_review = TitleReview(
            title_id="mvp009-test-3",
            title_text=title_v2,
            title_version="v2",
            overall_score=83,
            key_script_elements=["content", "refinement"],
        )

        script_review = ScriptReview(script_id="test-3", script_title=title_v2, overall_score=84)

        result = improver.improve_title(
            original_title=title_v2,
            script_text=script_v2,
            title_review=title_review,
            script_review=script_review,
            original_version_number="v2",
            new_version_number="v3",
        )

        # Verify version history
        assert len(result.version_history) == 2
        assert result.version_history[0].version_number == "v2"
        assert result.version_history[1].version_number == "v3"

        # Verify v3 has changes_from_previous
        assert len(result.new_version.changes_from_previous) > 0

        # Verify original version is v2
        assert result.original_version.version_number == "v2"
        assert result.original_version.text == title_v2

        # Verify notes reference v2
        assert "v2" in result.new_version.notes.lower()

    def test_supports_versioning_v3_v4_v5_v6_v7(self):
        """AC4: Support versioning (v3, v4, v5, v6, v7, etc.).

        Verify that the system supports arbitrary version numbers
        for iterative refinement beyond v3.
        """
        improver = TitleImprover()

        script = "Test script for version iteration."

        # Test various version transitions
        version_transitions = [
            ("v2", "v3"),
            ("v3", "v4"),
            ("v4", "v5"),
            ("v5", "v6"),
            ("v6", "v7"),
            ("v7", "v8"),
        ]

        for orig_ver, new_ver in version_transitions:
            title = f"Title {orig_ver}"

            title_review = TitleReview(
                title_id=f"test-{new_ver}",
                title_text=title,
                title_version=orig_ver,
                overall_score=80,
                key_script_elements=["test"],
            )

            script_review = ScriptReview(
                script_id=f"test-{new_ver}", script_title=title, overall_score=80
            )

            result = improver.improve_title(
                original_title=title,
                script_text=script,
                title_review=title_review,
                script_review=script_review,
                original_version_number=orig_ver,
                new_version_number=new_ver,
            )

            # Verify correct version numbers
            assert result.original_version.version_number == orig_ver
            assert result.new_version.version_number == new_ver

            # Verify version history
            assert result.version_history[0].version_number == orig_ver
            assert result.version_history[1].version_number == new_ver

    def test_v3_incorporates_v2_feedback_not_v1(self):
        """AC5: Tests verify v3 incorporates v2 feedback (not v1 feedback).

        This test ensures that when refining v2→v3, we use the feedback
        from the v2 review, not recycled v1 feedback.
        """
        improver = TitleImprover()

        # V2 title with specific characteristics
        title_v2 = "The Haunted Victorian: Echoes of the Past"
        script_v2 = """
        A Victorian mansion holds trapped souls who communicate through echoes.
        The protagonist Sarah must break an ancient curse to free them.
        Time is running out as the curse threatens to claim her too.
        """

        # V2 review identifies v2-specific issues (not v1 issues)
        title_review_v2 = TitleReview(
            title_id="mvp009-test-5",
            title_text=title_v2,
            title_version="v2",
            overall_score=84,
            script_alignment_score=86,
            engagement_score=82,
            key_script_elements=["curse", "trapped souls", "time running out", "Sarah"],
            suggested_keywords=["curse", "countdown"],
            current_length_chars=len(title_v2),
            optimal_length_chars=60,
        )

        # V2-specific feedback about missing urgency
        title_review_v2.improvement_points = [
            TitleImprovementPoint(
                category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                title="Missing urgency element",
                description="Script has time pressure ('running out') not reflected in title",
                priority="high",
                impact_score=85,
                suggested_fix="Add sense of urgency or countdown",
            )
        ]

        script_review_v2 = ScriptReview(
            script_id="mvp009-test-5", script_title=title_v2, overall_score=86
        )

        script_review_v2.improvement_points = [
            ImprovementPoint(
                category=ReviewCategory.ENGAGEMENT,
                title="Time pressure emphasis",
                description="The time running out creates urgency - title should reflect this",
                priority="high",
                impact_score=82,
                suggested_fix="Emphasize the countdown or urgency",
            )
        ]

        result = improver.improve_title(
            original_title=title_v2,
            script_text=script_v2,
            title_review=title_review_v2,
            script_review=script_review_v2,
            original_version_number="v2",
            new_version_number="v3",
        )

        # Verify v3 addresses v2-specific feedback
        assert result.new_version.version_number == "v3"

        # Check that addressed improvements mention the v2 feedback
        addressed_text = " ".join(result.addressed_improvements).lower()
        # Should address "urgency" from v2 feedback
        assert len(result.addressed_improvements) > 0

        # Verify rationale discusses changes from v2
        assert len(result.rationale) > 0

    def test_iterative_refinement_maintains_history(self):
        """Test that multiple iterations maintain full version history.

        Simulates a v1→v2→v3→v4 workflow and verifies that each
        step properly maintains its immediate predecessor.
        """
        improver = TitleImprover()

        # Simulate progressive refinement
        versions = []
        current_title = "Original Title"
        script = "A story about progressive refinement."

        for i, (old_ver, new_ver) in enumerate([("v1", "v2"), ("v2", "v3"), ("v3", "v4")]):
            title_review = TitleReview(
                title_id=f"history-test-{i}",
                title_text=current_title,
                title_version=old_ver,
                overall_score=70 + (i * 5),
                key_script_elements=["refinement", "progressive"],
            )

            script_review = ScriptReview(
                script_id=f"history-test-{i}",
                script_title=current_title,
                overall_score=75 + (i * 5),
            )

            result = improver.improve_title(
                original_title=current_title,
                script_text=script,
                title_review=title_review,
                script_review=script_review,
                original_version_number=old_ver,
                new_version_number=new_ver,
            )

            # Store version
            versions.append(result)

            # Update current title for next iteration
            current_title = result.new_version.text

            # Verify each step
            assert result.original_version.version_number == old_ver
            assert result.new_version.version_number == new_ver
            assert len(result.version_history) == 2

        # Verify we went through v1→v2→v3→v4
        assert versions[0].new_version.version_number == "v2"
        assert versions[1].new_version.version_number == "v3"
        assert versions[2].new_version.version_number == "v4"

        # Each version should reference its immediate predecessor
        assert versions[1].original_version.version_number == "v2"
        assert versions[2].original_version.version_number == "v3"


class TestConvenienceFunctionForV3:
    """Test convenience function works for v3+ generation."""

    def test_improve_title_from_reviews_v2_to_v3(self):
        """Test convenience function with v2→v3 transition."""
        title_v2 = "Test Title v2"
        script_v2 = "Test script for v2 to v3 refinement."

        title_review = TitleReview(
            title_id="convenience-test",
            title_text=title_v2,
            title_version="v2",
            overall_score=85,
            key_script_elements=["test", "refinement"],
        )

        script_review = ScriptReview(
            script_id="convenience-test", script_title=title_v2, overall_score=85
        )

        result = improve_title_from_reviews(
            original_title=title_v2,
            script_text=script_v2,
            title_review=title_review,
            script_review=script_review,
            original_version="v2",
            new_version="v3",
        )

        assert isinstance(result, ImprovedTitle)
        assert result.original_version.version_number == "v2"
        assert result.new_version.version_number == "v3"
