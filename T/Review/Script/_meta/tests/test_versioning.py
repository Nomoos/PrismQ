"""Tests for script versioning functionality."""

import pytest
from T.Review.Script import ScriptReview, ScriptVersion, ContentLength
from T.Script.Writer import ScriptWriter


class TestScriptVersioning:
    """Test script versioning for comparison and research."""
    
    def test_add_script_version_to_review(self):
        """Test adding script version to review."""
        review = ScriptReview(
            script_id="script-001",
            script_title="Test",
            overall_score=75
        )
        
        # Add first version
        version1 = review.add_script_version(
            script_text="Original script text...",
            length_seconds=120,
            created_by="AI-Writer-001",
            changes_from_previous="Initial version"
        )
        
        assert version1.version_number == 1
        assert version1.script_text == "Original script text..."
        assert version1.length_seconds == 120
        assert version1.review_score == 75
        assert len(review.script_versions_history) == 1
        assert review.script_version == version1
    
    def test_multiple_script_versions(self):
        """Test adding multiple script versions."""
        review = ScriptReview(
            script_id="script-001",
            script_title="Test",
            overall_score=70
        )
        
        # Add versions
        v1 = review.add_script_version(
            script_text="Version 1 text...",
            length_seconds=145,
            changes_from_previous="Initial"
        )
        
        review.overall_score = 80
        v2 = review.add_script_version(
            script_text="Version 2 text improved...",
            length_seconds=120,
            changes_from_previous="Reduced length by 25s, improved pacing"
        )
        
        review.overall_score = 88
        v3 = review.add_script_version(
            script_text="Version 3 text optimized...",
            length_seconds=90,
            changes_from_previous="Further optimization for YouTube shorts"
        )
        
        assert len(review.script_versions_history) == 3
        assert v1.version_number == 1
        assert v2.version_number == 2
        assert v3.version_number == 3
        assert review.script_version == v3  # Latest version
    
    def test_get_version_comparison(self):
        """Test getting version comparison data."""
        review = ScriptReview(
            script_id="script-001",
            script_title="Test",
            overall_score=65
        )
        
        # Need at least 2 versions
        comparison = review.get_version_comparison()
        assert comparison["comparison_available"] is False
        assert "Need at least 2 versions" in comparison["message"]
        
        # Add versions
        review.add_script_version("V1", 145, changes_from_previous="Initial")
        review.overall_score = 80
        review.add_script_version("V2", 90, changes_from_previous="Optimized")
        
        comparison = review.get_version_comparison()
        assert comparison["comparison_available"] is True
        assert comparison["versions_count"] == 2
        assert comparison["improvements"]["length_change_seconds"] == -55
        assert comparison["improvements"]["score_change"] == 15
        assert comparison["improvements"]["iterations"] == 1
    
    def test_writer_stores_versions(self):
        """Test that writer stores script versions."""
        writer = ScriptWriter()
        
        original = "Original script..."
        review = ScriptReview(
            script_id="script-001",
            script_title="Test",
            overall_score=70,
            current_length_seconds=120,
            optimal_length_seconds=90
        )
        
        # Optimize
        result = writer.optimize_from_review(original, review)
        
        # Check version was stored
        assert len(writer.script_versions) == 1
        assert writer.script_versions[0]["version_number"] == 1
        assert writer.script_versions[0]["script_text"] == result.optimized_text
        assert writer.script_versions[0]["score"] > 0
    
    def test_writer_version_comparison(self):
        """Test writer version comparison."""
        from T.Review.Script import ImprovementPoint, ReviewCategory
        
        writer = ScriptWriter(target_score_threshold=85)
        
        # First iteration
        review1 = ScriptReview(
            script_id="script-001",
            script_title="Test",
            overall_score=65,
            current_length_seconds=145,
            optimal_length_seconds=90
        )
        review1.improvement_points.append(ImprovementPoint(
            category=ReviewCategory.PACING,
            title="Reduce length",
            description="Cut 30s",
            priority="high",
            impact_score=20
        ))
        
        result1 = writer.optimize_from_review("Script v1...", review1)
        
        # Second iteration
        review2 = ScriptReview(
            script_id="script-001",
            script_title="Test",
            overall_score=80,
            current_length_seconds=120,
            optimal_length_seconds=90
        )
        result2 = writer.optimize_from_review(result1.optimized_text, review2)
        
        # Get comparison
        comparison = writer.get_version_comparison()
        
        assert comparison["comparison_available"] is True
        assert comparison["versions_count"] == 2
        assert comparison["summary"]["iterations"] == 1
        assert comparison["summary"]["score_improvement"] > 0
        # First version score is after first optimization (not the input score)
        assert comparison["summary"]["first_version"]["score"] > 65
        assert comparison["summary"]["latest_version"]["score"] >= 80
    
    def test_version_serialization(self):
        """Test that versions are serialized correctly."""
        review = ScriptReview(
            script_id="script-001",
            script_title="Test",
            overall_score=75
        )
        
        review.add_script_version(
            "Script text v1",
            length_seconds=120,
            created_by="AI-Writer-001",
            changes_from_previous="Initial"
        )
        
        # Serialize and deserialize
        data = review.to_dict()
        restored = ScriptReview.from_dict(data)
        
        assert len(restored.script_versions_history) == 1
        assert restored.script_versions_history[0].version_number == 1
        assert restored.script_versions_history[0].script_text == "Script text v1"
        assert restored.script_version is not None
        assert restored.script_version.version_number == 1
