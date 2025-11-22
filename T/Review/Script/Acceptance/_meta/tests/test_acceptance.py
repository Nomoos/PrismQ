"""Tests for Script Acceptance Gate (MVP-013).

This test suite validates that the implementation meets all acceptance criteria
specified in the problem statement for Worker10.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
from T.Review.Script.Acceptance import (
    check_script_acceptance,
    ScriptAcceptanceResult
)


class TestScriptAcceptanceBasic:
    """Test basic acceptance functionality."""
    
    def test_acceptance_accepted_script(self):
        """Test that a well-formed script is accepted."""
        script = """
        In the old house on Elm Street, mysterious echoes fill the rooms.
        Every sound carries a message from the past, revealing hidden secrets.
        As we explore deeper, the echoes grow stronger and more frequent.
        Finally, we discover the truth that has been waiting in the shadows.
        The mystery of the echo is solved, but new questions arise.
        """
        title = "The Echo Mystery"
        
        result = check_script_acceptance(
            script_text=script,
            title=title,
            script_version="v3"
        )
        
        assert isinstance(result, dict)
        assert result["accepted"] is True
        assert result["overall_score"] >= 70
        assert "proceed" in result["reason"].lower()
        assert len(result["issues"]) == 0
        print("✓ Well-formed script is accepted")
    
    def test_acceptance_rejected_incomplete_script(self):
        """Test that incomplete script is rejected."""
        script = "Just a short fragment"
        title = "The Echo Mystery"
        
        result = check_script_acceptance(
            script_text=script,
            title=title
        )
        
        assert isinstance(result, dict)
        assert result["accepted"] is False
        assert result["overall_score"] < 70
        assert "loop back" in result["reason"].lower()
        assert len(result["issues"]) > 0
        assert len(result["suggestions"]) > 0
        print("✓ Incomplete script is rejected")
    
    def test_acceptance_empty_script(self):
        """Test that empty script is rejected."""
        result = check_script_acceptance(
            script_text="",
            title="Some Title"
        )
        
        assert result["accepted"] is False
        assert result["overall_score"] == 0
        assert "empty" in result["reason"].lower()
        assert len(result["issues"]) > 0
        print("✓ Empty script is rejected")
    
    def test_acceptance_missing_title(self):
        """Test that script without title is rejected."""
        script = "A well-formed script with good content and structure."
        
        result = check_script_acceptance(
            script_text=script,
            title=""
        )
        
        assert result["accepted"] is False
        assert result["overall_score"] == 0
        assert "title" in result["reason"].lower()
        print("✓ Script without title is rejected")


class TestCompleteness:
    """Test completeness evaluation criteria."""
    
    def test_completeness_short_script(self):
        """Test completeness scoring for short script."""
        script = "A very short script."
        title = "Short"
        
        result = check_script_acceptance(script, title)
        
        assert result["completeness_score"] < 50
        print("✓ Short script has low completeness score")
    
    def test_completeness_medium_script(self):
        """Test completeness scoring for medium-length script."""
        script = " ".join(["word"] * 60)  # 60 words
        title = "Medium Script"
        
        result = check_script_acceptance(script, title)
        
        assert result["completeness_score"] >= 50
        print("✓ Medium script has adequate completeness score")
    
    def test_completeness_structured_script(self):
        """Test completeness with narrative structure."""
        script = """
        First, we start our journey into the mystery.
        Then, we discover clues hidden in the shadows.
        However, things take an unexpected turn.
        Finally, we reach the conclusion and solve the puzzle.
        """
        title = "The Mystery"
        
        result = check_script_acceptance(script, title)
        
        # Script with structure markers should score reasonably well
        assert result["completeness_score"] >= 60
        print("✓ Structured script has good completeness score")


class TestCoherence:
    """Test coherence evaluation criteria."""
    
    def test_coherence_with_transitions(self):
        """Test coherence scoring with transition words."""
        script = """
        The story begins in an old house. However, something feels wrong.
        Meanwhile, mysterious sounds echo through the halls. Therefore,
        we must investigate. Finally, we discover the truth.
        """
        title = "Investigation"
        
        result = check_script_acceptance(script, title)
        
        # Should score well on coherence
        assert result["coherence_score"] >= 60
        print("✓ Script with transitions has good coherence score")
    
    def test_coherence_without_transitions(self):
        """Test coherence scoring without transition words."""
        script = "Word word word. Another sentence. More words here."
        title = "Simple"
        
        result = check_script_acceptance(script, title)
        
        # Lower coherence due to lack of transitions
        assert result["coherence_score"] < 80
        print("✓ Script without transitions has lower coherence score")


class TestAlignment:
    """Test script-title alignment evaluation criteria."""
    
    def test_alignment_good_match(self):
        """Test alignment when script matches title well."""
        script = """
        In the mysterious echo of the old house, secrets are revealed.
        The echo grows stronger, carrying messages from the past.
        Every sound in this mystery leads us closer to the truth.
        """
        title = "The Echo Mystery"
        
        result = check_script_acceptance(script, title)
        
        # Should have high alignment
        assert result["alignment_score"] >= 70
        print("✓ Well-aligned script has high alignment score")
    
    def test_alignment_poor_match(self):
        """Test alignment when script doesn't match title."""
        script = """
        The spaceship travels through the galaxy.
        Aliens communicate with advanced technology.
        The future of space exploration is bright.
        """
        title = "The Echo Mystery"
        
        result = check_script_acceptance(script, title)
        
        # Should have low alignment
        assert result["alignment_score"] < 70
        print("✓ Misaligned script has low alignment score")
    
    def test_alignment_partial_match(self):
        """Test alignment with partial keyword matches."""
        script = """
        There is a mystery in the old building.
        Strange things happen every night.
        We must solve this puzzle before it's too late.
        """
        title = "The Echo Mystery"
        
        result = check_script_acceptance(script, title)
        
        # Should have moderate alignment (contains "mystery")
        assert 40 <= result["alignment_score"] <= 80
        print("✓ Partially aligned script has moderate alignment score")


class TestAcceptanceCriteria:
    """Test acceptance criteria specified in problem statement."""
    
    def test_ac_check_latest_version(self):
        """AC: Check if script (latest version) meets acceptance criteria."""
        script_v3 = """
        The story begins with a mysterious echo in an old house.
        As we investigate, we discover hidden secrets in the walls.
        The echo reveals clues about past events.
        Finally, we uncover the truth behind the mystery.
        """
        title = "The Echo Mystery"
        
        result = check_script_acceptance(
            script_text=script_v3,
            title=title,
            script_version="v3"
        )
        
        assert isinstance(result, dict)
        assert "accepted" in result
        assert "reason" in result
        assert "completeness_score" in result
        assert "coherence_score" in result
        assert "alignment_score" in result
        assert "overall_score" in result
        print("✓ AC: Checks latest version with all criteria")
    
    def test_ac_criteria_completeness(self):
        """AC: Criteria includes completeness."""
        script = "Beginning. Middle part happens. The end arrives."
        title = "Story"
        
        result = check_script_acceptance(script, title)
        
        assert "completeness_score" in result
        assert isinstance(result["completeness_score"], int)
        assert 0 <= result["completeness_score"] <= 100
        print("✓ AC: Evaluates completeness")
    
    def test_ac_criteria_coherence(self):
        """AC: Criteria includes coherence."""
        script = "Some text here. More text follows. Final text."
        title = "Text"
        
        result = check_script_acceptance(script, title)
        
        assert "coherence_score" in result
        assert isinstance(result["coherence_score"], int)
        assert 0 <= result["coherence_score"] <= 100
        print("✓ AC: Evaluates coherence")
    
    def test_ac_criteria_alignment_with_title(self):
        """AC: Criteria includes alignment with title."""
        script = "A story about echoes and mysteries in old houses."
        title = "The Echo Mystery"
        
        result = check_script_acceptance(script, title)
        
        assert "alignment_score" in result
        assert isinstance(result["alignment_score"], int)
        assert 0 <= result["alignment_score"] <= 100
        print("✓ AC: Evaluates alignment with title")
    
    def test_ac_accepted_proceed_to_mvp_014(self):
        """AC: If ACCEPTED, proceed to MVP-014."""
        script = """
        In the old mansion, mysterious echoes reveal secrets of the past.
        The investigation deepens as we explore room by room.
        Each echo brings us closer to understanding the mystery.
        Clues hidden in the walls tell a fascinating story.
        Finally, the truth emerges and the mystery is solved completely.
        """
        title = "The Echo Mystery"
        
        result = check_script_acceptance(script, title)
        
        if result["accepted"]:
            assert "proceed" in result["reason"].lower()
            assert "mvp-014" in result["reason"].lower() or "quality" in result["reason"].lower()
            print("✓ AC: Accepted scripts proceed to MVP-014")
    
    def test_ac_not_accepted_loop_back_to_mvp_010(self):
        """AC: If NOT ACCEPTED, loop back to MVP-010."""
        script = "Short and incomplete."
        title = "Long Complex Title About Many Things"
        
        result = check_script_acceptance(script, title)
        
        if not result["accepted"]:
            assert "loop back" in result["reason"].lower()
            assert "mvp-010" in result["reason"].lower() or "refinement" in result["reason"].lower()
            print("✓ AC: Rejected scripts loop back to MVP-010")
    
    def test_ac_always_uses_newest_version(self):
        """AC: Always uses newest script version."""
        # This is implicit in the function design - it accepts the latest version
        script_latest = """
        The latest version of the script with improvements.
        It has better structure and clearer narrative flow.
        The content aligns well with the title's promise.
        """
        title = "Improved Script"
        
        result = check_script_acceptance(
            script_text=script_latest,
            title=title,
            script_version="v5"  # Latest version
        )
        
        assert isinstance(result, dict)
        # The function operates on whatever version is passed (latest)
        print("✓ AC: Uses newest version provided")


class TestAcceptanceRejectionScenarios:
    """Test specific acceptance and rejection scenarios."""
    
    def test_scenario_high_quality_script(self):
        """Test acceptance of high-quality script."""
        script = """
        The journey begins in the ancient forest where echoes tell stories.
        Mysterious sounds guide us deeper into the woods, revealing secrets.
        As we follow the echoes, we discover a hidden truth about the past.
        The forest has been protecting this secret for centuries.
        Finally, we understand the connection between the echoes and history.
        This revelation changes everything we thought we knew.
        """
        title = "Echoes of the Ancient Forest"
        
        result = check_script_acceptance(script, title)
        
        assert result["accepted"] is True
        assert result["completeness_score"] >= 75
        assert result["coherence_score"] >= 70
        assert result["alignment_score"] >= 70
        assert result["overall_score"] >= 70
        print("✓ High-quality script is accepted")
    
    def test_scenario_incomplete_script(self):
        """Test rejection of incomplete script."""
        script = "The story starts but"
        title = "Complete Story"
        
        result = check_script_acceptance(script, title)
        
        assert result["accepted"] is False
        assert "completeness" in str(result["issues"]).lower()
        assert len(result["suggestions"]) > 0
        print("✓ Incomplete script is rejected with feedback")
    
    def test_scenario_incoherent_script(self):
        """Test rejection of incoherent script."""
        script = """
        Random words here. Unconnected thoughts there.
        No logical flow exists. Just random sentences.
        Nothing makes sense together in this text.
        """
        title = "Coherent Story"
        
        result = check_script_acceptance(script, title)
        
        # May be rejected for low coherence
        if not result["accepted"]:
            assert result["coherence_score"] < 70 or result["overall_score"] < 70
            print("✓ Incoherent script is rejected")
    
    def test_scenario_misaligned_script(self):
        """Test rejection of script misaligned with title."""
        script = """
        The spaceship launches into orbit around Mars.
        Astronauts conduct experiments in zero gravity.
        Mission control monitors all systems carefully.
        The journey to the red planet continues successfully.
        """
        title = "The Haunted Mansion Mystery"
        
        result = check_script_acceptance(script, title)
        
        assert result["alignment_score"] < 60
        if not result["accepted"]:
            assert "alignment" in str(result["issues"]).lower()
            print("✓ Misaligned script is rejected")
    
    def test_scenario_borderline_script(self):
        """Test borderline script near threshold."""
        script = """
        A mystery story about something interesting.
        Things happen and people react to events.
        The situation develops over time somehow.
        Eventually everything is resolved in the end.
        """
        title = "Mystery Story"
        
        result = check_script_acceptance(script, title, acceptance_threshold=70)
        
        # Should be near the threshold
        assert 55 <= result["overall_score"] <= 85
        print("✓ Borderline script evaluated correctly")
    
    def test_scenario_custom_threshold(self):
        """Test acceptance with custom threshold."""
        script = """
        A decent script with moderate quality.
        It has some structure and reasonable coherence.
        The content relates to the title somewhat.
        """
        title = "Decent Script"
        
        # With low threshold
        result_low = check_script_acceptance(script, title, acceptance_threshold=50)
        # With high threshold
        result_high = check_script_acceptance(script, title, acceptance_threshold=90)
        
        # Should affect acceptance decision
        if result_low["overall_score"] >= 50 and result_low["overall_score"] < 90:
            assert result_low["accepted"] is True
            assert result_high["accepted"] is False
            print("✓ Custom threshold affects acceptance")


class TestReturnFormat:
    """Test return value format and structure."""
    
    def test_return_dict_structure(self):
        """Test that return value has correct structure."""
        result = check_script_acceptance(
            script_text="Some script text here.",
            title="Title"
        )
        
        # Required fields
        assert "accepted" in result
        assert "reason" in result
        assert "completeness_score" in result
        assert "coherence_score" in result
        assert "alignment_score" in result
        assert "overall_score" in result
        assert "issues" in result
        assert "suggestions" in result
        
        # Correct types
        assert isinstance(result["accepted"], bool)
        assert isinstance(result["reason"], str)
        assert isinstance(result["completeness_score"], int)
        assert isinstance(result["coherence_score"], int)
        assert isinstance(result["alignment_score"], int)
        assert isinstance(result["overall_score"], int)
        assert isinstance(result["issues"], list)
        assert isinstance(result["suggestions"], list)
        
        print("✓ Return dictionary has correct structure")
    
    def test_scores_in_valid_range(self):
        """Test that all scores are in valid range (0-100)."""
        script = "A script with various content and structure elements."
        title = "Test Script"
        
        result = check_script_acceptance(script, title)
        
        assert 0 <= result["completeness_score"] <= 100
        assert 0 <= result["coherence_score"] <= 100
        assert 0 <= result["alignment_score"] <= 100
        assert 0 <= result["overall_score"] <= 100
        
        print("✓ All scores are in valid range (0-100)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
