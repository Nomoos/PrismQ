"""Basic tests for ToneReview model."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
from T.Review.Tone import (
    ToneReview,
    ToneIssue,
    ToneIssueType,
    ToneSeverity
)


class TestToneReviewBasic:
    """Test basic ToneReview functionality."""
    
    def test_create_basic_review(self):
        """Test creating a basic ToneReview instance."""
        review = ToneReview(
            script_id="script-001",
            script_version="v3",
            overall_score=88,
            target_tone="dark suspense",
            target_audience="US female 14-29"
        )
        
        assert review.script_id == "script-001"
        assert review.script_version == "v3"
        assert review.overall_score == 88
        assert review.pass_threshold == 80
        assert review.passes is True
        assert len(review.issues) == 0
        assert review.critical_count == 0
        assert review.high_count == 0
        assert review.reviewer_id == "AI-ToneReviewer-001"
        assert review.reviewed_at is not None
        assert review.confidence_score == 85
        assert review.target_tone == "dark suspense"
        assert review.target_audience == "US female 14-29"
    
    def test_create_failing_review(self):
        """Test creating a review that fails."""
        review = ToneReview(
            script_id="script-002",
            script_version="v3",
            overall_score=70  # Below threshold
        )
        
        assert review.passes is False
    
    def test_tone_metrics_initialization(self):
        """Test tone-specific metrics are initialized."""
        review = ToneReview(
            script_id="script-001",
            emotional_intensity_score=85,
            style_alignment_score=90,
            voice_consistency_score=88,
            audience_fit_score=82
        )
        
        assert review.emotional_intensity_score == 85
        assert review.style_alignment_score == 90
        assert review.voice_consistency_score == 88
        assert review.audience_fit_score == 82


class TestToneIssue:
    """Test ToneIssue functionality."""
    
    def test_create_tone_issue(self):
        """Test creating a tone issue."""
        issue = ToneIssue(
            issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
            severity=ToneSeverity.MEDIUM,
            line_number=42,
            text="This is really fun and exciting!",
            suggestion="This unsettling discovery changed everything.",
            explanation="Too upbeat for dark suspense tone"
        )
        
        assert issue.issue_type == ToneIssueType.EMOTIONAL_INTENSITY
        assert issue.severity == ToneSeverity.MEDIUM
        assert issue.line_number == 42
        assert issue.text == "This is really fun and exciting!"
        assert issue.suggestion == "This unsettling discovery changed everything."
        assert issue.confidence == 85
    
    def test_tone_issue_types(self):
        """Test all tone issue types."""
        issue_types = [
            ToneIssueType.EMOTIONAL_INTENSITY,
            ToneIssueType.STYLE_ALIGNMENT,
            ToneIssueType.VOICE_CONSISTENCY,
            ToneIssueType.TONE_APPROPRIATENESS,
            ToneIssueType.AUDIENCE_MISMATCH,
            ToneIssueType.TONAL_SHIFT,
            ToneIssueType.MOOD_INCONSISTENCY
        ]
        
        for issue_type in issue_types:
            issue = ToneIssue(
                issue_type=issue_type,
                severity=ToneSeverity.LOW,
                line_number=1,
                text="test",
                suggestion="test",
                explanation="test"
            )
            assert issue.issue_type == issue_type


class TestToneReviewMethods:
    """Test ToneReview methods."""
    
    def test_add_issue(self):
        """Test adding issues to review."""
        review = ToneReview(
            script_id="script-001",
            overall_score=88
        )
        
        issue = ToneIssue(
            issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
            severity=ToneSeverity.HIGH,
            line_number=42,
            text="This is fun!",
            suggestion="This is unsettling.",
            explanation="Wrong emotional tone"
        )
        
        review.add_issue(issue)
        
        assert len(review.issues) == 1
        assert review.high_count == 1
        assert review.critical_count == 0
    
    def test_add_critical_issue_fails_review(self):
        """Test that adding critical issue fails review."""
        review = ToneReview(
            script_id="script-001",
            overall_score=88  # Good score
        )
        
        assert review.passes is True
        
        critical_issue = ToneIssue(
            issue_type=ToneIssueType.STYLE_ALIGNMENT,
            severity=ToneSeverity.CRITICAL,
            line_number=10,
            text="This comedy scene is hilarious!",
            suggestion="This dark revelation chilled her to the bone.",
            explanation="Complete style mismatch - comedy in horror script"
        )
        
        review.add_issue(critical_issue)
        
        assert review.passes is False
        assert review.critical_count == 1
    
    def test_get_issues_by_severity(self):
        """Test filtering issues by severity."""
        review = ToneReview(script_id="script-001")
        
        review.add_issue(ToneIssue(
            issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
            severity=ToneSeverity.HIGH,
            line_number=15,
            text="Happy text",
            suggestion="Dark text",
            explanation="Wrong intensity"
        ))
        
        review.add_issue(ToneIssue(
            issue_type=ToneIssueType.VOICE_CONSISTENCY,
            severity=ToneSeverity.MEDIUM,
            line_number=20,
            text="We are going",
            suggestion="I am going",
            explanation="POV shift"
        ))
        
        high_issues = review.get_issues_by_severity(ToneSeverity.HIGH)
        assert len(high_issues) == 1
        assert high_issues[0].issue_type == ToneIssueType.EMOTIONAL_INTENSITY
        
        medium_issues = review.get_issues_by_severity(ToneSeverity.MEDIUM)
        assert len(medium_issues) == 1
        assert medium_issues[0].issue_type == ToneIssueType.VOICE_CONSISTENCY
    
    def test_get_issues_by_type(self):
        """Test filtering issues by type."""
        review = ToneReview(script_id="script-001")
        
        review.add_issue(ToneIssue(
            issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
            severity=ToneSeverity.HIGH,
            line_number=15,
            text="Too happy",
            suggestion="More somber",
            explanation="Intensity issue"
        ))
        
        review.add_issue(ToneIssue(
            issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
            severity=ToneSeverity.MEDIUM,
            line_number=25,
            text="Too excited",
            suggestion="More subdued",
            explanation="Another intensity issue"
        ))
        
        intensity_issues = review.get_issues_by_type(ToneIssueType.EMOTIONAL_INTENSITY)
        assert len(intensity_issues) == 2
    
    def test_get_critical_issues(self):
        """Test getting critical issues."""
        review = ToneReview(script_id="script-001")
        
        review.add_issue(ToneIssue(
            issue_type=ToneIssueType.STYLE_ALIGNMENT,
            severity=ToneSeverity.CRITICAL,
            line_number=10,
            text="Comedy scene",
            suggestion="Horror scene",
            explanation="Critical style mismatch"
        ))
        
        review.add_issue(ToneIssue(
            issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
            severity=ToneSeverity.HIGH,
            line_number=15,
            text="Too happy",
            suggestion="More dark",
            explanation="Intensity issue"
        ))
        
        critical = review.get_critical_issues()
        assert len(critical) == 1
        assert critical[0].severity == ToneSeverity.CRITICAL
    
    def test_get_high_priority_issues(self):
        """Test getting high priority issues."""
        review = ToneReview(script_id="script-001")
        
        review.add_issue(ToneIssue(
            issue_type=ToneIssueType.STYLE_ALIGNMENT,
            severity=ToneSeverity.CRITICAL,
            line_number=10,
            text="Comedy",
            suggestion="Horror",
            explanation="Critical mismatch"
        ))
        
        review.add_issue(ToneIssue(
            issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
            severity=ToneSeverity.HIGH,
            line_number=15,
            text="Happy",
            suggestion="Dark",
            explanation="Intensity issue"
        ))
        
        review.add_issue(ToneIssue(
            issue_type=ToneIssueType.VOICE_CONSISTENCY,
            severity=ToneSeverity.MEDIUM,
            line_number=20,
            text="We",
            suggestion="I",
            explanation="POV issue"
        ))
        
        high_priority = review.get_high_priority_issues()
        assert len(high_priority) == 2  # Critical + High


class TestToneReviewSerialization:
    """Test serialization functionality."""
    
    def test_to_dict(self):
        """Test converting review to dictionary."""
        review = ToneReview(
            script_id="script-001",
            script_version="v3",
            overall_score=88,
            target_tone="dark suspense",
            target_audience="US female 14-29"
        )
        
        review.add_issue(ToneIssue(
            issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
            severity=ToneSeverity.HIGH,
            line_number=42,
            text="Too happy",
            suggestion="More somber",
            explanation="Wrong intensity"
        ))
        
        data = review.to_dict()
        
        assert data["script_id"] == "script-001"
        assert data["script_version"] == "v3"
        assert data["overall_score"] == 88
        assert data["target_tone"] == "dark suspense"
        assert data["target_audience"] == "US female 14-29"
        assert len(data["issues"]) == 1
        assert data["issues"][0]["issue_type"] == "emotional_intensity"
        assert data["issues"][0]["severity"] == "high"
    
    def test_from_dict(self):
        """Test creating review from dictionary."""
        data = {
            "script_id": "script-001",
            "script_version": "v3",
            "overall_score": 88,
            "target_tone": "dark suspense",
            "target_audience": "US female 14-29",
            "issues": [
                {
                    "issue_type": "emotional_intensity",
                    "severity": "high",
                    "line_number": 42,
                    "text": "Too happy",
                    "suggestion": "More somber",
                    "explanation": "Wrong intensity",
                    "confidence": 85
                }
            ],
            "high_count": 1
        }
        
        review = ToneReview.from_dict(data)
        
        assert review.script_id == "script-001"
        assert review.script_version == "v3"
        assert review.overall_score == 88
        assert review.target_tone == "dark suspense"
        assert review.target_audience == "US female 14-29"
        assert len(review.issues) == 1
        assert review.issues[0].issue_type == ToneIssueType.EMOTIONAL_INTENSITY
        assert review.issues[0].severity == ToneSeverity.HIGH
    
    def test_round_trip_serialization(self):
        """Test that serialization preserves all data."""
        original = ToneReview(
            script_id="script-001",
            overall_score=85,
            emotional_intensity_score=82,
            style_alignment_score=88,
            voice_consistency_score=86,
            audience_fit_score=84,
            target_tone="dark mystery",
            target_audience="Adults 25-45"
        )
        
        original.add_issue(ToneIssue(
            issue_type=ToneIssueType.VOICE_CONSISTENCY,
            severity=ToneSeverity.MEDIUM,
            line_number=10,
            text="We are going",
            suggestion="I am going",
            explanation="POV shift"
        ))
        
        # Convert to dict and back
        data = original.to_dict()
        restored = ToneReview.from_dict(data)
        
        assert restored.script_id == original.script_id
        assert restored.overall_score == original.overall_score
        assert restored.emotional_intensity_score == original.emotional_intensity_score
        assert restored.style_alignment_score == original.style_alignment_score
        assert restored.voice_consistency_score == original.voice_consistency_score
        assert restored.audience_fit_score == original.audience_fit_score
        assert restored.target_tone == original.target_tone
        assert restored.target_audience == original.target_audience
        assert len(restored.issues) == len(original.issues)
        assert restored.issues[0].text == original.issues[0].text


class TestToneReviewAcceptanceCriteria:
    """Test acceptance criteria from MVP-015."""
    
    def test_emotional_intensity_checking(self):
        """Test checking emotional intensity."""
        review = ToneReview(
            script_id="script-001",
            emotional_intensity_score=85
        )
        
        issue = ToneIssue(
            issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
            severity=ToneSeverity.MEDIUM,
            line_number=10,
            text="This is amazing and wonderful!",
            suggestion="This discovery was unsettling.",
            explanation="Emotional intensity too high for somber tone"
        )
        
        review.add_issue(issue)
        
        intensity_issues = review.get_issues_by_type(ToneIssueType.EMOTIONAL_INTENSITY)
        assert len(intensity_issues) == 1
    
    def test_style_alignment_checking(self):
        """Test evaluating style alignment."""
        review = ToneReview(
            script_id="script-001",
            style_alignment_score=78
        )
        
        issue = ToneIssue(
            issue_type=ToneIssueType.STYLE_ALIGNMENT,
            severity=ToneSeverity.HIGH,
            line_number=20,
            text="This comedy bit is hilarious!",
            suggestion="The shadows grew longer as night approached.",
            explanation="Comedy style doesn't align with dark suspense"
        )
        
        review.add_issue(issue)
        
        style_issues = review.get_issues_by_type(ToneIssueType.STYLE_ALIGNMENT)
        assert len(style_issues) == 1
    
    def test_voice_consistency_checking(self):
        """Test checking voice consistency."""
        review = ToneReview(
            script_id="script-001",
            voice_consistency_score=82
        )
        
        issue = ToneIssue(
            issue_type=ToneIssueType.VOICE_CONSISTENCY,
            severity=ToneSeverity.MEDIUM,
            line_number=30,
            text="We decided to investigate further.",
            suggestion="I decided to investigate further.",
            explanation="POV shift from first person singular to plural"
        )
        
        review.add_issue(issue)
        
        voice_issues = review.get_issues_by_type(ToneIssueType.VOICE_CONSISTENCY)
        assert len(voice_issues) == 1
    
    def test_tone_appropriateness_evaluation(self):
        """Test evaluating tone appropriateness for content type."""
        review = ToneReview(
            script_id="script-001",
            target_tone="dark suspense",
            target_audience="US female 14-29"
        )
        
        issue = ToneIssue(
            issue_type=ToneIssueType.TONE_APPROPRIATENESS,
            severity=ToneSeverity.HIGH,
            line_number=40,
            text="Let's have fun at the party!",
            suggestion="The gathering felt wrong, somehow threatening.",
            explanation="Upbeat tone inappropriate for dark suspense horror"
        )
        
        review.add_issue(issue)
        
        appropriateness_issues = review.get_issues_by_type(ToneIssueType.TONE_APPROPRIATENESS)
        assert len(appropriateness_issues) == 1
    
    def test_pass_proceed_to_mvp_016(self):
        """Test that passing review proceeds to MVP-016."""
        review = ToneReview(
            script_id="script-001",
            overall_score=88
        )
        
        assert review.passes is True
        assert review.overall_score >= review.pass_threshold
    
    def test_fail_return_to_script_refinement(self):
        """Test that failing review returns to script refinement."""
        review = ToneReview(
            script_id="script-001",
            overall_score=75  # Below threshold
        )
        
        assert review.passes is False
        assert review.overall_score < review.pass_threshold
    
    def test_output_json_format(self):
        """Test output as JSON with tone analysis."""
        review = ToneReview(
            script_id="script-001",
            script_version="v3",
            overall_score=88,
            emotional_intensity_score=85,
            style_alignment_score=90,
            voice_consistency_score=88,
            audience_fit_score=87,
            target_tone="dark suspense",
            target_audience="US female 14-29"
        )
        
        review.add_issue(ToneIssue(
            issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
            severity=ToneSeverity.MEDIUM,
            line_number=42,
            text="So exciting!",
            suggestion="Unsettling discovery.",
            explanation="Too upbeat"
        ))
        
        data = review.to_dict()
        
        # Verify JSON-serializable structure
        assert isinstance(data, dict)
        assert "script_id" in data
        assert "overall_score" in data
        assert "emotional_intensity_score" in data
        assert "style_alignment_score" in data
        assert "voice_consistency_score" in data
        assert "audience_fit_score" in data
        assert "target_tone" in data
        assert "target_audience" in data
        assert "issues" in data
        assert "passes" in data
        
        # All enum values should be strings
        for issue in data["issues"]:
            assert isinstance(issue["issue_type"], str)
            assert isinstance(issue["severity"], str)
    
    def test_various_tone_styles(self):
        """Test with various tone styles as per acceptance criteria."""
        tone_styles = [
            "dark suspense",
            "horror",
            "mystery",
            "dramatic thriller",
            "creepy psychological",
            "dark comedy"
        ]
        
        for tone_style in tone_styles:
            review = ToneReview(
                script_id=f"script-{tone_style}",
                target_tone=tone_style,
                overall_score=85
            )
            
            assert review.target_tone == tone_style
            assert review.passes is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
