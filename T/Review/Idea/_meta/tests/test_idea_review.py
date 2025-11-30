"""Tests for Worker10 Idea Review Generator.

These tests verify the functionality of the IdeaReviewGenerator and
related classes for producing comprehensive idea reviews.
"""

import sys
import os
import pytest
from datetime import datetime

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
idea_review_dir = os.path.join(current_dir, '../../')
idea_creation_dir = os.path.join(current_dir, '../../../Idea/Creation/src')
sys.path.insert(0, idea_review_dir)
sys.path.insert(0, idea_creation_dir)

from idea_review import (
    IdeaReviewGenerator,
    IdeaReviewResult,
    IdeaVariantAnalysis,
    generate_idea_review,
)
from idea_variants import DEFAULT_IDEA_COUNT


class TestIdeaVariantAnalysis:
    """Tests for IdeaVariantAnalysis dataclass."""
    
    def test_create_analysis(self):
        """Test creating a basic variant analysis."""
        analysis = IdeaVariantAnalysis(
            variant_index=0,
            variant_type="emotion_first",
            variant_name="Emotion-First Hook",
            pros=["Clear hook", "Strong emotion"],
            cons=["Missing context"],
            gaps=["No platform specified"],
            similarity_score=75,
            key_themes=["emotion", "engagement"],
            unique_elements=["Hook: Something compelling..."]
        )
        
        assert analysis.variant_index == 0
        assert analysis.variant_type == "emotion_first"
        assert analysis.similarity_score == 75
        assert len(analysis.pros) == 2
        assert len(analysis.cons) == 1
    
    def test_analysis_to_dict(self):
        """Test converting analysis to dictionary."""
        analysis = IdeaVariantAnalysis(
            variant_index=1,
            variant_type="mystery",
            variant_name="Mystery/Curiosity Gap",
            similarity_score=80
        )
        
        result = analysis.to_dict()
        
        assert isinstance(result, dict)
        assert result["variant_index"] == 1
        assert result["variant_type"] == "mystery"
        assert result["similarity_score"] == 80
        assert result["pros"] == []
        assert result["cons"] == []
    
    def test_analysis_default_values(self):
        """Test that default values are properly set."""
        analysis = IdeaVariantAnalysis(
            variant_index=0,
            variant_type="test",
            variant_name="Test Variant"
        )
        
        assert analysis.pros == []
        assert analysis.cons == []
        assert analysis.gaps == []
        assert analysis.similarity_score == 0
        assert analysis.key_themes == []
        assert analysis.unique_elements == []


class TestIdeaReviewResult:
    """Tests for IdeaReviewResult dataclass."""
    
    def test_create_result(self):
        """Test creating a review result."""
        result = IdeaReviewResult(
            original_input="test input",
            input_type="keyword",
            total_variants=5,
            average_similarity_score=75.5
        )
        
        assert result.original_input == "test input"
        assert result.input_type == "keyword"
        assert result.total_variants == 5
        assert result.average_similarity_score == 75.5
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = IdeaReviewResult(
            original_input="test",
            input_type="phrase",
            total_variants=3,
            cross_variant_differences=["Difference 1", "Difference 2"],
            overall_gaps=["Gap 1"],
            overall_strengths=["Strength 1"],
            compatibility_summary="Good alignment",
            recommendations=["Recommendation 1"]
        )
        
        dict_result = result.to_dict()
        
        assert isinstance(dict_result, dict)
        assert dict_result["original_input"] == "test"
        assert dict_result["total_variants"] == 3
        assert len(dict_result["cross_variant_differences"]) == 2
        assert "generated_at" in dict_result
    
    def test_result_format_as_markdown(self):
        """Test formatting result as markdown."""
        result = IdeaReviewResult(
            original_input="test keyword",
            input_type="keyword",
            total_variants=2,
            overall_strengths=["Good hook"],
            overall_gaps=["Missing audience"],
            cross_variant_differences=["Different approaches"],
            compatibility_summary="Well aligned",
            recommendations=["Add more detail"],
            average_similarity_score=80.0
        )
        
        markdown = result.format_as_markdown()
        
        assert "# Idea Review Report" in markdown
        assert "test keyword" in markdown
        assert "Overall Strengths" in markdown
        assert "Overall Gaps" in markdown
        assert "Differences Across Variants" in markdown
        assert "Recommendations" in markdown
        assert "80.0%" in markdown


class TestIdeaReviewGenerator:
    """Tests for IdeaReviewGenerator class."""
    
    def test_generator_creation(self):
        """Test creating a generator with default settings."""
        generator = IdeaReviewGenerator()
        assert generator.num_ideas == 10
    
    def test_generator_custom_count(self):
        """Test creating a generator with custom idea count."""
        generator = IdeaReviewGenerator(num_ideas=5)
        assert generator.num_ideas == 5
    
    def test_classify_input_keyword(self):
        """Test input classification for keywords."""
        generator = IdeaReviewGenerator()
        
        assert generator._classify_input("robot") == "keyword"
        assert generator._classify_input("AI") == "keyword"
        assert generator._classify_input("skirts 2000") == "keyword"
    
    def test_classify_input_phrase(self):
        """Test input classification for phrases."""
        generator = IdeaReviewGenerator()
        
        assert generator._classify_input("A story about friendship") == "phrase"
        assert generator._classify_input("The mystery of the old house") == "phrase"
    
    def test_classify_input_longer_text(self):
        """Test input classification for longer text."""
        generator = IdeaReviewGenerator()
        
        long_text = "This is a much longer piece of text that contains many words and should be classified as longer text because it exceeds the phrase threshold significantly."
        assert generator._classify_input(long_text) == "longer text"
    
    def test_generate_review_empty_input(self):
        """Test that empty input raises ValueError."""
        generator = IdeaReviewGenerator()
        
        with pytest.raises(ValueError, match="cannot be empty"):
            generator.generate_review("")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            generator.generate_review("   ")
    
    def test_generate_review_keyword(self):
        """Test generating review from keyword input."""
        generator = IdeaReviewGenerator(num_ideas=3)
        result = generator.generate_review("skirts 2000", seed=42)
        
        assert isinstance(result, IdeaReviewResult)
        assert result.original_input == "skirts 2000"
        assert result.input_type == "keyword"
        assert result.total_variants == 3
        assert len(result.variant_analyses) == 3
        assert result.average_similarity_score > 0
    
    def test_generate_review_phrase(self):
        """Test generating review from phrase input."""
        generator = IdeaReviewGenerator(num_ideas=3)
        result = generator.generate_review("A mysterious night adventure", seed=42)
        
        assert result.input_type == "phrase"
        assert result.total_variants == 3
        assert result.compatibility_summary != ""
    
    def test_generate_review_longer_text_czech(self):
        """Test generating review from longer Czech text."""
        generator = IdeaReviewGenerator(num_ideas=3)
        czech_text = "když jsem se probudil sobotního rána po tahu"
        result = generator.generate_review(czech_text, seed=42)
        
        assert result.original_input == czech_text
        assert result.input_type == "phrase"
        assert result.total_variants == 3
        assert len(result.recommendations) > 0
    
    def test_generate_review_seed_reproducibility(self):
        """Test that same seed produces same results."""
        generator = IdeaReviewGenerator(num_ideas=3)
        
        result1 = generator.generate_review("test input", seed=123)
        result2 = generator.generate_review("test input", seed=123)
        
        assert result1.total_variants == result2.total_variants
        assert len(result1.variant_analyses) == len(result2.variant_analyses)
        
        for a1, a2 in zip(result1.variant_analyses, result2.variant_analyses):
            assert a1.variant_type == a2.variant_type
    
    def test_variant_analysis_has_required_fields(self):
        """Test that variant analyses have all required fields."""
        generator = IdeaReviewGenerator(num_ideas=2)
        result = generator.generate_review("test", seed=42)
        
        for analysis in result.variant_analyses:
            assert analysis.variant_type != ""
            assert analysis.variant_name != ""
            assert analysis.variant_index >= 0
            assert 0 <= analysis.similarity_score <= 100


class TestGenerateIdeaReview:
    """Tests for the convenience function generate_idea_review."""
    
    def test_generate_review_simple(self):
        """Test simple call to generate_idea_review."""
        result = generate_idea_review("test keyword", num_ideas=2, seed=42)
        
        assert isinstance(result, IdeaReviewResult)
        assert result.total_variants == 2
    
    def test_generate_review_with_defaults(self):
        """Test generate_idea_review with default parameters."""
        result = generate_idea_review("another test", seed=42)
        
        # Default is defined by DEFAULT_IDEA_COUNT constant
        assert result.total_variants == DEFAULT_IDEA_COUNT
    
    def test_generate_review_returns_complete_result(self):
        """Test that generate_idea_review returns a complete result."""
        result = generate_idea_review("complete test", num_ideas=3, seed=42)
        
        assert result.original_input == "complete test"
        assert result.generated_at is not None
        assert isinstance(result.generated_at, datetime)
        assert len(result.variant_analyses) == 3
        assert result.compatibility_summary != ""
        assert result.average_similarity_score >= 0


class TestReviewContent:
    """Tests for the content quality of reviews."""
    
    def test_review_identifies_pros(self):
        """Test that reviews identify pros for variants."""
        result = generate_idea_review("engaging story", num_ideas=5, seed=42)
        
        # At least some variants should have pros identified
        has_pros = any(len(a.pros) > 0 for a in result.variant_analyses)
        assert has_pros, "Review should identify at least some pros"
    
    def test_review_identifies_gaps(self):
        """Test that reviews identify gaps for variants."""
        result = generate_idea_review("simple test", num_ideas=5, seed=42)
        
        # Variants should have gaps identified (common for template-based generation)
        has_gaps = any(len(a.gaps) > 0 for a in result.variant_analyses)
        assert has_gaps, "Review should identify at least some gaps"
    
    def test_review_has_cross_variant_differences(self):
        """Test that reviews identify cross-variant differences."""
        result = generate_idea_review("test input", num_ideas=5, seed=42)
        
        assert len(result.cross_variant_differences) > 0
    
    def test_review_has_recommendations(self):
        """Test that reviews include recommendations."""
        result = generate_idea_review("test input", num_ideas=5, seed=42)
        
        assert len(result.recommendations) > 0
    
    def test_review_similarity_scores_in_range(self):
        """Test that similarity scores are within valid range."""
        result = generate_idea_review("test input", num_ideas=5, seed=42)
        
        for analysis in result.variant_analyses:
            assert 0 <= analysis.similarity_score <= 100
        
        assert 0 <= result.average_similarity_score <= 100


class TestIntegrationWithIdeaCreation:
    """Integration tests with the Idea.Creation module."""
    
    def test_integration_with_keyword_input(self):
        """Test integration with keyword input 'skirts 2000'."""
        result = generate_idea_review("skirts 2000", num_ideas=5, seed=42)
        
        assert result.total_variants == 5
        assert result.input_type == "keyword"
        
        # Verify variants were generated from Idea.Creation
        for analysis in result.variant_analyses:
            assert analysis.variant_type != ""
            # Variant types should be from the known templates
            known_types = [
                'emotion_first', 'mystery', 'skeleton', 'shortform', 'niche_blend',
                'minimal', '4point', 'hook_frame', 'shortform2', 'genre', 'scene_seed',
                'soft_supernatural', 'light_mystery', 'scifi_school', 'safe_survival',
                'emotional_drama', 'rivals_allies', 'identity_power', 'ai_companion',
                'urban_quest', 'magical_aesthetic', 'family_drama', 'social_home',
                'realistic_mystery', 'school_family', 'personal_voice'
            ]
            assert analysis.variant_type in known_types
    
    def test_integration_with_czech_text(self):
        """Test integration with Czech text input."""
        czech_text = "když jsem se probudil sobotního rána po tahu"
        result = generate_idea_review(czech_text, num_ideas=5, seed=42)
        
        assert result.original_input == czech_text
        assert result.total_variants == 5
        
        # Even with Czech text, variants should be generated
        assert len(result.variant_analyses) == 5
        
        # Markdown output should be valid
        markdown = result.format_as_markdown()
        assert czech_text in markdown


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
