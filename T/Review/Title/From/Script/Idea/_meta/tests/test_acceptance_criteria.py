"""Validation tests for acceptance criteria.

This test suite validates that the implementation meets all acceptance criteria
specified in the problem statement for Worker10.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import json

import pytest

from T.Review.Title.ByScriptAndIdea import (
    TitleReview,
    TitleReviewCategory,
    review_title_by_script_and_idea,
)


class TestAcceptanceCriteria:
    """Test acceptance criteria for Worker10 implementation."""

    def test_ac1_review_title_against_script_and_idea(self):
        """AC1: Review title v1 against script v1 and idea."""
        title = "The Mysterious Echo"
        script = """
        In the old house, a mysterious echo reveals hidden secrets.
        Every sound carries a message from the past.
        The echo grows stronger as the mystery deepens.
        """
        idea = "Mystery story about echoes revealing secrets in an old house"

        # Should be able to review title against both script and idea
        review = review_title_by_script_and_idea(
            title_text=title, script_text=script, idea_summary=idea
        )

        assert isinstance(review, TitleReview)
        assert review.title_text == title

        # Should have both alignment scores
        assert review.script_alignment_score >= 0
        assert review.script_alignment_score <= 100
        assert review.idea_alignment_score >= 0
        assert review.idea_alignment_score <= 100

        # Should reference the script and idea
        assert review.script_id is not None
        assert review.idea_id is not None

        print("✓ AC1: Reviews title v1 against script v1 and idea")

    def test_ac2_generate_structured_feedback(self):
        """AC2: Generate structured feedback (alignment, clarity, engagement)."""
        review = review_title_by_script_and_idea(
            title_text="The Echo Mystery",
            script_text="A mystery about echoes in a haunted house",
            idea_summary="Mystery horror with echoes",
        )

        # Should have structured category scores
        assert len(review.category_scores) > 0

        # Should include alignment categories
        categories = [cs.category for cs in review.category_scores]
        assert TitleReviewCategory.SCRIPT_ALIGNMENT in categories
        assert TitleReviewCategory.IDEA_ALIGNMENT in categories
        assert TitleReviewCategory.ENGAGEMENT in categories

        # Each category should have structured data
        for cat_score in review.category_scores:
            assert cat_score.score >= 0
            assert cat_score.score <= 100
            assert cat_score.reasoning != ""
            assert isinstance(cat_score.strengths, list)
            assert isinstance(cat_score.weaknesses, list)

        # Should have clarity feedback via length assessment
        length_assessment = review.get_length_assessment()
        assert "status" in length_assessment
        assert "feedback" in length_assessment

        print("✓ AC2: Generates structured feedback (alignment, clarity, engagement)")

    def test_ac3_identify_mismatches(self):
        """AC3: Identify mismatches between title and script."""
        # Create a title with obvious mismatches
        title = "Space Adventure Mission to Mars"
        script = """
        In the haunted house, echoes reveal dark secrets.
        The mystery deepens with every sound.
        """
        idea = "Horror mystery about echoes"

        review = review_title_by_script_and_idea(
            title_text=title, script_text=script, idea_summary=idea
        )

        # Should identify poor alignment (mismatches)
        assert review.script_alignment_score < 60  # Poor alignment

        # Should have improvement points addressing the mismatches
        assert len(review.improvement_points) > 0

        # Should identify script alignment as an issue
        script_alignment_issues = [
            imp
            for imp in review.improvement_points
            if imp.category == TitleReviewCategory.SCRIPT_ALIGNMENT
        ]
        assert len(script_alignment_issues) > 0

        # The improvement point should mention alignment or script-related issues
        assert any(
            "alignment" in imp.description.lower()
            or "script" in imp.description.lower()
            or "match" in imp.description.lower()
            or "reflect" in imp.description.lower()
            for imp in script_alignment_issues
        )

        print("✓ AC3: Identifies mismatches between title and script")

    def test_ac4_suggest_improvements(self):
        """AC4: Suggest improvements for title."""
        review = review_title_by_script_and_idea(
            title_text="A Title",  # Intentionally weak title
            script_text="A complex story about echoes revealing mysteries",
            idea_summary="Mystery with echoes",
        )

        # Should generate improvement points
        assert len(review.improvement_points) > 0

        # Each improvement should have required fields
        for imp in review.improvement_points:
            assert imp.title != ""
            assert imp.description != ""
            assert imp.priority in ["high", "medium", "low"]
            assert imp.impact_score > 0
            assert imp.category in TitleReviewCategory

        # Should have suggested fixes
        improvements_with_fixes = [imp for imp in review.improvement_points if imp.suggested_fix]
        assert len(improvements_with_fixes) > 0

        # Should prioritize improvements
        high_priority = review.get_high_priority_improvements()
        assert len(high_priority) > 0

        # High priority items should be sorted by impact
        if len(high_priority) > 1:
            for i in range(len(high_priority) - 1):
                assert high_priority[i].impact_score >= high_priority[i + 1].impact_score

        print("✓ AC4: Suggests improvements for title with prioritization")

    def test_ac5_json_output_format(self):
        """AC5: Output JSON format with feedback categories."""
        review = review_title_by_script_and_idea(
            title_text="The Echo Mystery",
            script_text="A mysterious echo in an old house reveals secrets",
            idea_summary="Mystery about echoes and secrets",
        )

        # Should be convertible to dictionary (JSON-compatible)
        review_dict = review.to_dict()
        assert isinstance(review_dict, dict)

        # Should have all key fields
        assert "title_id" in review_dict
        assert "title_text" in review_dict
        assert "overall_score" in review_dict
        assert "script_alignment_score" in review_dict
        assert "idea_alignment_score" in review_dict
        assert "engagement_score" in review_dict
        assert "seo_score" in review_dict

        # Should have structured feedback categories
        assert "category_scores" in review_dict
        assert isinstance(review_dict["category_scores"], list)
        assert len(review_dict["category_scores"]) > 0

        # Each category should be JSON-serializable
        for cat in review_dict["category_scores"]:
            assert isinstance(cat, dict)
            assert "category" in cat
            assert "score" in cat
            assert "reasoning" in cat
            assert "strengths" in cat
            assert "weaknesses" in cat

        # Should have improvement points
        assert "improvement_points" in review_dict
        assert isinstance(review_dict["improvement_points"], list)

        # Should be fully JSON-serializable
        json_str = json.dumps(review_dict)
        assert isinstance(json_str, str)
        assert len(json_str) > 0

        # Should be able to reconstruct from JSON
        restored_dict = json.loads(json_str)
        assert restored_dict["title_text"] == review.title_text
        assert restored_dict["overall_score"] == review.overall_score

        print("✓ AC5: Outputs JSON format with feedback categories")

    def test_ac6_sample_title_script_pairs(self):
        """AC6: Tests review sample title/script pairs."""

        # Sample 1: Well-aligned title and script
        sample1 = {
            "title": "The Haunting Echo - Mystery of the Old House",
            "script": """
            The old house on Elm Street holds a dark secret.
            A haunting echo fills the rooms, revealing clues to a mystery.
            Each sound brings us closer to the truth hidden in the walls.
            """,
            "idea": "Mystery horror about echoes revealing secrets in an old house",
        }

        review1 = review_title_by_script_and_idea(
            title_text=sample1["title"], script_text=sample1["script"], idea_summary=sample1["idea"]
        )

        # Should score reasonably well (good alignment)
        assert review1.overall_score >= 50
        assert review1.script_alignment_score >= 50

        # Sample 2: Poorly aligned title and script
        sample2 = {
            "title": "Space Adventure",
            "script": "A ghost haunts an abandoned mansion",
            "idea": "Horror story about ghosts",
        }

        review2 = review_title_by_script_and_idea(
            title_text=sample2["title"], script_text=sample2["script"], idea_summary=sample2["idea"]
        )

        # Should score poorly (bad alignment)
        assert review2.overall_score < review1.overall_score
        assert len(review2.improvement_points) > 0

        # Sample 3: Engagement-focused title
        sample3 = {
            "title": "5 Shocking Secrets: What's Hidden in the House?",
            "script": "The house holds five shocking secrets waiting to be discovered",
            "idea": "Discovery story about hidden secrets",
        }

        review3 = review_title_by_script_and_idea(
            title_text=sample3["title"], script_text=sample3["script"], idea_summary=sample3["idea"]
        )

        # Should have high engagement scores
        assert review3.engagement_score >= 60
        assert review3.curiosity_score >= 60

        print("✓ AC6: Successfully tests multiple title/script pairs with varying quality")


class TestWorkflowIntegration:
    """Test that the implementation fits into the expected workflow."""

    def test_mvp_003_workflow(self):
        """Test integration with MVP-003 workflow (title v1 + script v1)."""
        # Simulating MVP-003: We have title v1 and script v1
        title_v1 = "The Echo Mystery"
        script_v1_text = "A mysterious echo reveals secrets in an old house"
        idea_summary = "Mystery about echoes revealing secrets"

        # Review should work with v1 versions
        review = review_title_by_script_and_idea(
            title_text=title_v1,
            script_text=script_v1_text,
            idea_summary=idea_summary,
            title_version="v1",
            script_version="v1",
        )

        assert review.title_version == "v1"
        assert review.script_version == "v1"
        assert review.is_ready_for_improvement()

        print("✓ Integrates with MVP-003 workflow")

    def test_feedback_for_title_v2(self):
        """Test that review provides feedback suitable for generating title v2."""
        review = review_title_by_script_and_idea(
            title_text="The House",
            script_text="Echoes in an abandoned house reveal dark secrets and mysteries",
            idea_summary="Horror mystery with echoes revealing secrets",
        )

        # Should provide comprehensive feedback for improvements
        assert len(review.improvement_points) > 0
        assert len(review.category_scores) > 0

        # Should have quick wins for easy improvements
        assert len(review.quick_wins) > 0

        # Should identify primary concern
        assert review.primary_concern != ""

        # Should be ready for improvement stage (title v2 generation)
        assert review.is_ready_for_improvement()

        print("✓ Provides feedback suitable for title v2 generation")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
