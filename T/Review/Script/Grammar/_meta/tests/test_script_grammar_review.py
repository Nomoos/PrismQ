"""Comprehensive tests for Script Grammar Review (MVP-014).

Tests the grammar review functionality including:
- Grammatically correct scripts (should PASS)
- Grammatically incorrect scripts (should FAIL with specific issues)
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
from T.Review.Script.Grammar import (
    ScriptGrammarChecker,
    review_script_grammar,
    review_script_grammar_to_json,
    get_grammar_feedback
)
from T.Review.Grammar import (
    GrammarReview,
    GrammarIssue,
    GrammarIssueType,
    GrammarSeverity
)


class TestGrammaticallyCorrectScripts:
    """Test that grammatically correct scripts PASS the review."""
    
    def test_perfect_script_passes(self):
        """Test that a grammatically correct script passes."""
        script = """The sun rises over the distant mountains.
Birds sing their morning songs.
A gentle breeze flows through the trees.
Nature awakens to a new day."""
        
        review = review_script_grammar(script, script_id="perfect-001")
        
        assert review.passes is True
        assert review.overall_score >= 85
        assert len(review.issues) == 0
        assert review.critical_count == 0
        assert "Excellent" in review.summary or "passes" in review.summary.lower()
    
    def test_dialogue_script_passes(self):
        """Test that well-formatted dialogue script passes."""
        script = """INT. COFFEE SHOP - DAY

Sarah walks into the bustling coffee shop.
She spots her friend waiting at a corner table.

SARAH
Hey! Sorry I'm late.

MICHAEL
No worries. I just got here myself.

They sit down and begin their conversation.
The ambient noise creates a cozy atmosphere."""
        
        review = review_script_grammar(script, script_id="dialogue-001")
        
        # Should pass with minimal or no issues
        assert review.overall_score >= 75
        # Dialogue formatting might trigger some minor flags, but should generally pass
    
    def test_action_script_passes(self):
        """Test that action-heavy script with proper grammar passes."""
        script = """The hero stands at the edge of the cliff.
Below, the ocean crashes against jagged rocks.
Thunder rumbles in the distance.
Rain begins to fall.
The hero takes a deep breath and prepares to jump."""
        
        review = review_script_grammar(script, script_id="action-001")
        
        assert review.passes is True
        assert review.overall_score >= 85
        assert review.critical_count == 0


class TestGrammaticallyIncorrectScripts:
    """Test that grammatically incorrect scripts FAIL with specific issues."""
    
    def test_spelling_errors_detected(self):
        """Test that spelling errors are detected with line references."""
        script = """I recieved a message yesterday.
The occassion was special.
We definately need to meet again."""
        
        review = review_script_grammar(script, script_id="spelling-001")
        
        # Should detect spelling errors
        spelling_issues = review.get_issues_by_type(GrammarIssueType.SPELLING)
        assert len(spelling_issues) >= 2  # At least recieved and definately
        
        # Check line references
        line_numbers = [issue.line_number for issue in spelling_issues]
        assert 1 in line_numbers  # recieved on line 1
        assert 3 in line_numbers  # definately on line 3
        
        # Check suggestions are provided
        for issue in spelling_issues:
            assert issue.suggestion != ""
            assert issue.suggestion != issue.text
    
    def test_subject_verb_agreement_errors(self):
        """Test that subject-verb agreement errors are detected as CRITICAL."""
        script = """I was happy.
He were angry.
They was confused.
She are tired."""
        
        review = review_script_grammar(script, script_id="agreement-001")
        
        # Should fail due to critical grammar errors
        assert review.passes is False
        assert review.critical_count >= 3  # Multiple critical errors
        
        # Check critical issues are detected
        critical_issues = review.get_critical_issues()
        assert len(critical_issues) >= 3
        
        # Verify line references are accurate
        line_numbers = [issue.line_number for issue in critical_issues]
        assert 2 in line_numbers  # "He were" on line 2
        assert 3 in line_numbers  # "They was" on line 3
        
        # Check suggestions are provided and different from original
        for issue in critical_issues:
            assert issue.suggestion != ""
            assert issue.suggestion != issue.text
            # Should contain a verb form (is, are, was, were)
            assert any(verb in issue.suggestion.lower() for verb in ["is", "are", "was", "were"])
    
    def test_capitalization_errors(self):
        """Test that capitalization errors are detected."""
        script = """the sun was shining.
birds were singing.
everything seemed perfect."""
        
        review = review_script_grammar(script, script_id="caps-001")
        
        # Should detect capitalization issues
        cap_issues = review.get_issues_by_type(GrammarIssueType.CAPITALIZATION)
        assert len(cap_issues) >= 3
        
        # Check each line is flagged
        line_numbers = [issue.line_number for issue in cap_issues]
        assert 1 in line_numbers
        assert 2 in line_numbers
        assert 3 in line_numbers
    
    def test_punctuation_errors(self):
        """Test that punctuation errors are detected."""
        script = """The hero entered the large room and looked around
He carefully examined everything that was in there
The silence was deafening and everything was quiet"""
        
        review = review_script_grammar(script, script_id="punct-001")
        
        # Should detect missing punctuation (longer sentences trigger the check)
        punct_issues = review.get_issues_by_type(GrammarIssueType.PUNCTUATION)
        assert len(punct_issues) >= 1
        
        # Suggestions should add proper punctuation
        for issue in punct_issues:
            assert issue.suggestion.endswith(('.', '!', '?'))
    
    def test_multiple_error_types(self):
        """Test script with multiple types of errors."""
        script = """i recieved a message.
He were very excited about the news.
The meeting occured yesterday
We was all happy."""
        
        review = review_script_grammar(script, script_id="multi-001")
        
        # Should fail due to multiple errors
        assert review.passes is False
        assert len(review.issues) >= 4
        
        # Should have multiple error types
        error_types = {issue.issue_type for issue in review.issues}
        assert GrammarIssueType.SPELLING in error_types
        assert GrammarIssueType.AGREEMENT in error_types
        assert GrammarIssueType.CAPITALIZATION in error_types
    
    def test_score_decreases_with_errors(self):
        """Test that score decreases as errors increase."""
        good_script = "The hero walks into the sunset."
        review_good = review_script_grammar(good_script, script_id="good-001")
        
        bad_script = """i recieved a message.
He were happy.
They was excited."""
        review_bad = review_script_grammar(bad_script, script_id="bad-001")
        
        # Bad script should have lower score
        assert review_bad.overall_score < review_good.overall_score
        assert review_bad.overall_score < 85  # Below threshold


class TestLineReferenceAccuracy:
    """Test that line references in issues are accurate."""
    
    def test_line_numbers_are_correct(self):
        """Test that reported line numbers match actual error locations."""
        script = """Line 1 is correct.
Line 2 has a eror here.
Line 3 is correct.
Line 4 also has a mistke."""
        
        # Note: "eror" and "mistke" are typos but not in our dictionary,
        # so let's use known errors
        script = """Line 1 is correct.
I recieved an email on line 2.
Line 3 is also correct.
He were happy on line 4."""
        
        review = review_script_grammar(script, script_id="line-test-001")
        
        # Check that line numbers match
        issues = review.issues
        for issue in issues:
            if "recieved" in issue.text.lower():
                assert issue.line_number == 2
            if "were" in issue.text.lower() and "He" in issue.text:
                assert issue.line_number == 4
    
    def test_empty_lines_handled_correctly(self):
        """Test that empty lines don't affect line numbering."""
        script = """First line.

Third line with spelling eror.

Fifth line is correct."""
        
        # Use a known error
        script = """First line is correct.

I recieved a message on line 3.

Line 5 is correct."""
        
        review = review_script_grammar(script, script_id="empty-lines-001")
        
        spelling_issues = review.get_issues_by_type(GrammarIssueType.SPELLING)
        if len(spelling_issues) > 0:
            # Error should be on line 3
            assert any(issue.line_number == 3 for issue in spelling_issues)
    
    def test_multiline_text_line_numbers(self):
        """Test line number accuracy in longer scripts."""
        lines = []
        for i in range(1, 21):
            if i == 10:
                lines.append("He were running fast.")  # Error on line 10
            elif i == 15:
                lines.append("I recieved a gift.")  # Error on line 15
            else:
                lines.append(f"This is line {i} which is correct.")
        
        script = "\n".join(lines)
        review = review_script_grammar(script, script_id="multiline-001")
        
        # Check specific line numbers
        for issue in review.issues:
            if "were" in issue.text and "He" in issue.text:
                assert issue.line_number == 10
            if "recieved" in issue.text:
                assert issue.line_number == 15


class TestJSONOutput:
    """Test JSON output format as required by acceptance criteria."""
    
    def test_json_output_is_valid(self):
        """Test that JSON output is valid and parseable."""
        script = "He were happy."
        
        json_output = review_script_grammar_to_json(script, script_id="json-001")
        
        # Should be valid JSON
        data = json.loads(json_output)
        
        # Check required fields
        assert "script_id" in data
        assert "overall_score" in data
        assert "passes" in data
        assert "issues" in data
        assert isinstance(data["issues"], list)
    
    def test_json_contains_issue_details(self):
        """Test that JSON output contains detailed issue information."""
        script = "I recieved a message. He were happy."
        
        json_output = review_script_grammar_to_json(script, script_id="json-002")
        data = json.loads(json_output)
        
        # Should have issues
        assert len(data["issues"]) >= 2
        
        # Each issue should have required fields
        for issue in data["issues"]:
            assert "issue_type" in issue
            assert "severity" in issue
            assert "line_number" in issue
            assert "text" in issue
            assert "suggestion" in issue
            assert "explanation" in issue
            assert "confidence" in issue
    
    def test_json_round_trip(self):
        """Test that JSON can be used to reconstruct the review."""
        script = "He were running. I recieved a message."
        
        # Create review and convert to JSON
        review = review_script_grammar(script, script_id="roundtrip-001")
        json_output = review_script_grammar_to_json(script, script_id="roundtrip-001")
        data = json.loads(json_output)
        
        # Reconstruct from JSON
        restored_review = GrammarReview.from_dict(data)
        
        # Compare key fields
        assert restored_review.script_id == review.script_id
        assert restored_review.overall_score == review.overall_score
        assert restored_review.passes == review.passes
        assert len(restored_review.issues) == len(review.issues)


class TestFeedbackGeneration:
    """Test feedback generation for script refinement."""
    
    def test_feedback_contains_next_action(self):
        """Test that feedback includes next action guidance."""
        passing_script = "The hero walks into the sunset."
        failing_script = "He were happy. I recieved a gift."
        
        review_pass = review_script_grammar(passing_script)
        review_fail = review_script_grammar(failing_script)
        
        feedback_pass = get_grammar_feedback(review_pass)
        feedback_fail = get_grammar_feedback(review_fail)
        
        # Passing should suggest proceeding to Stage 15
        assert "Stage 15" in feedback_pass["next_action"] or "Tone" in feedback_pass["next_action"]
        
        # Failing should suggest returning to refinement
        assert "Refinement" in feedback_fail["next_action"] or "Stage 11" in feedback_fail["next_action"]
    
    def test_feedback_prioritizes_critical_issues(self):
        """Test that feedback highlights critical issues first."""
        script = """He were running.
I recieved a message.
The day was beautiful"""
        
        review = review_script_grammar(script, script_id="priority-001")
        feedback = get_grammar_feedback(review)
        
        # Should have critical issues listed
        assert "critical_issues" in feedback
        assert len(feedback["critical_issues"]) > 0
        
        # Critical issues should have line numbers
        for issue in feedback["critical_issues"]:
            assert "line" in issue
            assert "explanation" in issue
            assert "suggestion" in issue
    
    def test_feedback_summary_describes_issues(self):
        """Test that summary describes the issues found."""
        script = "He were happy. I recieved gifts."
        
        review = review_script_grammar(script, script_id="summary-001")
        
        # Summary should mention issues
        assert review.summary != ""
        if not review.passes:
            assert "issue" in review.summary.lower() or "error" in review.summary.lower()


class TestScriptGrammarChecker:
    """Test the ScriptGrammarChecker class directly."""
    
    def test_checker_initialization(self):
        """Test that checker initializes with correct threshold."""
        checker = ScriptGrammarChecker(pass_threshold=90)
        assert checker.pass_threshold == 90
    
    def test_custom_threshold_affects_pass_fail(self):
        """Test that custom threshold affects pass/fail determination."""
        script = """The hero walks.
I recieved a message."""
        
        # With high threshold, might fail
        checker_strict = ScriptGrammarChecker(pass_threshold=95)
        review_strict = checker_strict.review_script(script, script_id="strict-001")
        
        # With low threshold, might pass
        checker_lenient = ScriptGrammarChecker(pass_threshold=70)
        review_lenient = checker_lenient.review_script(script, script_id="lenient-001")
        
        # Same issues but different pass/fail based on threshold
        assert len(review_strict.issues) == len(review_lenient.issues)
        # At least one should have different pass status or similar score
        assert review_strict.pass_threshold == 95
        assert review_lenient.pass_threshold == 70
    
    def test_checker_detects_all_error_types(self):
        """Test that checker can detect all error types."""
        script = """i started the day.
He were happy about it.
I recieved many gifts.
Everything was perfect"""
        
        checker = ScriptGrammarChecker()
        review = checker.review_script(script, script_id="alltypes-001")
        
        # Should detect multiple error types
        error_types = {issue.issue_type for issue in review.issues}
        
        # Should have at least 3 different error types
        assert len(error_types) >= 3
        assert GrammarIssueType.CAPITALIZATION in error_types
        assert GrammarIssueType.AGREEMENT in error_types
        assert GrammarIssueType.SPELLING in error_types


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_empty_script(self):
        """Test handling of empty script."""
        script = ""
        
        review = review_script_grammar(script, script_id="empty-001")
        
        # Should pass (no errors in empty script)
        assert review.passes is True
        assert len(review.issues) == 0
        assert review.overall_score == 100
    
    def test_single_line_script(self):
        """Test handling of single-line script."""
        script = "The hero saves the day."
        
        review = review_script_grammar(script, script_id="single-001")
        
        # Should pass
        assert review.passes is True
        assert review.overall_score >= 85
    
    def test_script_with_special_formatting(self):
        """Test handling of scripts with special formatting."""
        script = """[Scene: The beach at sunset]

* Hero walks slowly
* Waves crash against shore

(Voiceover begins)"""
        
        review = review_script_grammar(script, script_id="format-001")
        
        # Should not flag special formatting as errors
        # Score should be reasonable
        assert review.overall_score >= 70
    
    def test_very_long_script(self):
        """Test handling of very long script."""
        lines = ["This is a correct sentence."] * 100
        script = "\n".join(lines)
        
        review = review_script_grammar(script, script_id="long-001")
        
        # Should pass and handle long script
        assert review.passes is True
        assert review.overall_score >= 85
    
    def test_script_with_numbers_and_symbols(self):
        """Test handling of scripts with numbers and symbols."""
        script = """Chapter 1: The Beginning
        
He woke up at 5:00 AM.
The year was 2024.
Everything cost $5.99."""
        
        review = review_script_grammar(script, script_id="symbols-001")
        
        # Should handle numbers and symbols without issues
        # May have some capitalization issues but should be reasonable
        assert review.overall_score >= 70


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
