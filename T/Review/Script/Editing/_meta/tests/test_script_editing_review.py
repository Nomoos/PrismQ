"""Comprehensive tests for Script Editing Review (MVP-018).

Tests the editing review functionality including:
- Well-edited scripts (should PASS)
- Scripts with editing issues (should FAIL with specific issues)
- Line reference accuracy
- JSON output format
- Issue detection and categorization
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

import pytest
from T.Review.Script.Editing import (
    ScriptEditingChecker,
    review_script_editing,
    review_script_editing_to_json,
    get_editing_feedback
)
from T.Review.Model import (
    EditingReview,
    EditingIssue,
    EditingIssueType,
    EditingSeverity
)


class TestWellEditedScripts:
    """Test that well-edited scripts PASS the review."""
    
    def test_perfect_script_passes(self):
        """Test that a well-edited, clear script passes."""
        script = """The sun rises over the distant mountains.
Birds sing their morning songs.
A gentle breeze flows through the trees.
Nature awakens to a new day."""
        
        review = review_script_editing(script, script_id="perfect-001")
        
        assert review.passes is True
        assert review.overall_score >= 85
        assert len(review.issues) == 0
        assert review.critical_count == 0
        assert "Excellent" in review.summary or "passes" in review.summary.lower()
    
    def test_concise_active_voice_script_passes(self):
        """Test that concise, active voice script passes."""
        script = """The hero grabs the sword.
He charges forward.
The battle begins at dawn.
Victory requires courage and skill."""
        
        review = review_script_editing(script, script_id="active-001")
        
        assert review.passes is True
        assert review.overall_score >= 85
        assert review.critical_count == 0
    
    def test_well_structured_dialogue_passes(self):
        """Test that well-structured dialogue script passes."""
        script = """INT. COFFEE SHOP - DAY

Sarah walks into the bustling coffee shop.
She spots her friend waiting at a corner table.

SARAH
Hey! Sorry I'm late.

MICHAEL
No worries. I just got here.

They sit down and begin their conversation.
The ambient noise creates a cozy atmosphere."""
        
        review = review_script_editing(script, script_id="dialogue-001")
        
        # Should pass with minimal or no issues
        assert review.overall_score >= 75


class TestScriptsWithEditingIssues:
    """Test that scripts with editing issues FAIL with specific feedback."""
    
    def test_wordiness_detected(self):
        """Test that wordy phrases are detected with suggestions."""
        script = """In order to complete the task, we need to proceed.
At this point in time, the situation is unclear.
Due to the fact that the weather is bad, we postpone the event."""
        
        review = review_script_editing(script, script_id="wordy-001")
        
        # Should detect wordiness issues
        wordiness_issues = review.get_issues_by_type(EditingIssueType.WORDINESS)
        assert len(wordiness_issues) >= 3
        
        # Check that suggestions are provided
        for issue in wordiness_issues:
            assert issue.suggestion != issue.text
            assert issue.severity in [EditingSeverity.MEDIUM, EditingSeverity.LOW]
            assert issue.line_number > 0
    
    def test_redundancy_detected(self):
        """Test that redundant phrases are detected."""
        script = """This is a very unique opportunity.
We need to review the past history of events.
The close proximity to the building is convenient.
The exact same result occurred occurred again."""
        
        review = review_script_editing(script, script_id="redundant-001")
        
        # Should detect redundancy issues
        redundancy_issues = review.get_issues_by_type(EditingIssueType.REDUNDANCY)
        assert len(redundancy_issues) >= 2
        
        # Check severity
        for issue in redundancy_issues:
            assert issue.severity in [EditingSeverity.HIGH, EditingSeverity.MEDIUM]
    
    def test_passive_voice_detected(self):
        """Test that passive voice is detected in longer sentences."""
        script = """The decision was made by the committee after careful consideration.
The project was completed by the team ahead of schedule.
The message was delivered by the courier yesterday."""
        
        review = review_script_editing(script, script_id="passive-001")
        
        # Should detect clarity issues (passive voice)
        clarity_issues = review.get_issues_by_type(EditingIssueType.CLARITY)
        assert len(clarity_issues) >= 1
        
        for issue in clarity_issues:
            assert "active voice" in issue.explanation.lower()
            assert issue.severity == EditingSeverity.MEDIUM
    
    def test_weak_transitions_detected(self):
        """Test that weak transitions are flagged."""
        script = """The hero enters the room.
And then he sees the villain.
And so the battle begins.
Also there is a sword on the table."""
        
        review = review_script_editing(script, script_id="transition-001")
        
        # Should detect transition issues
        transition_issues = review.get_issues_by_type(EditingIssueType.TRANSITION)
        assert len(transition_issues) >= 1
        
        for issue in transition_issues:
            assert issue.severity == EditingSeverity.LOW
            assert "transition" in issue.explanation.lower()
    
    def test_long_sentences_detected(self):
        """Test that overly long sentences are flagged."""
        script = """The protagonist walks through the ancient forest, past the towering trees and over the mossy rocks, while thinking about the journey ahead and wondering if the destination would provide the answers to all the questions that have been haunting the mind for years."""
        
        review = review_script_editing(script, script_id="long-001")
        
        # Should detect clarity issue for long sentence
        clarity_issues = review.get_issues_by_type(EditingIssueType.CLARITY)
        assert len(clarity_issues) >= 1
        
        # Check that it flags the length
        long_sentence_issue = [i for i in clarity_issues if "long" in i.explanation.lower()]
        assert len(long_sentence_issue) > 0


class TestScoreCategorization:
    """Test that scripts are scored appropriately."""
    
    def test_multiple_issues_lower_score(self):
        """Test that multiple issues result in lower score."""
        bad_script = """In order to make a decision, we gave consideration to all options.
The choice was made by the team at this point in time.
Due to the fact that the weather is bad, the event is postponed postponed.
In close proximity to the building, there is a very unique statue."""
        
        review = review_script_editing(bad_script, script_id="bad-001")
        
        # Should have low score
        assert review.overall_score < 70
        assert review.passes is False
        assert len(review.issues) >= 5
    
    def test_high_severity_issues_fail_review(self):
        """Test that high severity issues cause failure."""
        script = """The close proximity is very convenient.
The past history shows clear patterns."""
        
        review = review_script_editing(script, script_id="high-severity-001")
        
        # Should have high severity issues
        high_issues = review.get_issues_by_severity(EditingSeverity.HIGH)
        assert len(high_issues) >= 1
        
        # May fail depending on number of issues
        if review.high_count >= 3:
            assert review.passes is False


class TestJSONOutput:
    """Test JSON serialization and deserialization."""
    
    def test_json_output_format(self):
        """Test that JSON output is properly formatted."""
        script = """In order to complete this task, we proceed carefully."""
        
        json_output = review_script_editing_to_json(script, script_id="json-001")
        
        # Should be valid JSON
        data = json.loads(json_output)
        
        # Check required fields
        assert "script_id" in data
        assert "overall_score" in data
        assert "passes" in data
        assert "issues" in data
        assert "summary" in data
        
        # Check score is valid
        assert 0 <= data["overall_score"] <= 100
    
    def test_json_contains_issue_details(self):
        """Test that JSON output contains detailed issue information."""
        script = """Due to the fact that the weather is bad, we postpone."""
        
        json_output = review_script_editing_to_json(script, script_id="json-002")
        data = json.loads(json_output)
        
        # Should have issues
        assert len(data["issues"]) > 0
        
        # Check issue structure
        issue = data["issues"][0]
        assert "issue_type" in issue
        assert "severity" in issue
        assert "line_number" in issue
        assert "text" in issue
        assert "suggestion" in issue
        assert "explanation" in issue
        assert "confidence" in issue


class TestFeedbackGeneration:
    """Test feedback generation for script refinement."""
    
    def test_feedback_structure(self):
        """Test that feedback has proper structure."""
        script = """In order to proceed, we give consideration to all factors."""
        
        review = review_script_editing(script, script_id="feedback-001")
        feedback = get_editing_feedback(review)
        
        # Check required feedback fields
        assert "script_id" in feedback
        assert "passes" in feedback
        assert "overall_score" in feedback
        assert "summary" in feedback
        assert "primary_concerns" in feedback
        assert "quick_fixes" in feedback
        assert "next_action" in feedback
    
    def test_feedback_identifies_issue_types(self):
        """Test that feedback categorizes issues by type."""
        script = """In order to complete this, we give consideration to options.
The very unique statue statue is beautiful."""
        
        review = review_script_editing(script, script_id="feedback-002")
        feedback = get_editing_feedback(review)
        
        # Should have quick fixes
        assert len(feedback["quick_fixes"]) > 0
        
        # Quick fixes should mention issue types
        quick_fixes_text = " ".join(feedback["quick_fixes"])
        # At least one type should be mentioned
        assert any(word in quick_fixes_text.lower() for word in ["wordy", "redundant", "clarity", "transition"])


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_empty_script(self):
        """Test that empty script passes without errors."""
        script = ""
        
        review = review_script_editing(script, script_id="empty-001")
        
        # Should pass with perfect score
        assert review.passes is True
        assert review.overall_score == 100
        assert len(review.issues) == 0
    
    def test_short_script(self):
        """Test that short script is handled correctly."""
        script = "The hero runs."
        
        review = review_script_editing(script, script_id="short-001")
        
        # Should handle without errors
        assert review.overall_score >= 0
    
    def test_dialogue_only_script(self):
        """Test that dialogue-only script doesn't trigger false positives."""
        script = """SARAH
"I can't believe this is happening!"

MICHAEL
"We need to stay calm."

SARAH
"But what if we're too late?"
"""
        
        review = review_script_editing(script, script_id="dialogue-002")
        
        # Should not flag dialogue lines as errors
        # Passive voice checks should skip dialogue
        assert review.overall_score >= 80
    
    def test_screenplay_formatting_ignored(self):
        """Test that screenplay formatting is not flagged as errors."""
        script = """INT. WAREHOUSE - NIGHT

EXT. CITY STREET - DAY

The hero walks down the empty street.
"""
        
        review = review_script_editing(script, script_id="format-001")
        
        # Formatting lines should be ignored
        # Should pass or have minimal issues
        assert review.overall_score >= 85


class TestReviewerBehavior:
    """Test the ScriptEditingChecker behavior."""
    
    def test_custom_threshold(self):
        """Test that custom pass threshold is respected."""
        script = """In order to proceed, we continue."""
        
        # Low threshold
        review_low = review_script_editing(script, script_id="threshold-001", pass_threshold=50)
        
        # High threshold
        review_high = review_script_editing(script, script_id="threshold-002", pass_threshold=95)
        
        # Same issues
        assert len(review_low.issues) == len(review_high.issues)
        
        # Low threshold should pass with score of 95
        if review_low.overall_score >= 50:
            assert review_low.passes is True
        
        # High threshold should pass/fail based on score vs threshold
        if review_high.overall_score >= 95:
            assert review_high.passes is True
        else:
            assert review_high.passes is False
    
    def test_checker_initialization(self):
        """Test that checker can be initialized with custom parameters."""
        checker = ScriptEditingChecker(pass_threshold=90)
        
        assert checker.pass_threshold == 90
        assert len(checker.wordy_phrases) > 0
        assert len(checker.redundant_pairs) > 0
    
    def test_issue_confidence_scores(self):
        """Test that issues have appropriate confidence scores."""
        script = """In order to proceed, the decision was made made."""
        
        review = review_script_editing(script, script_id="confidence-001")
        
        # All issues should have confidence scores
        for issue in review.issues:
            assert 0 <= issue.confidence <= 100
            # Most should be reasonably confident
            assert issue.confidence >= 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
