"""Tests for ScoreBreakdown data models."""

import pytest
from src.models import ScoreBreakdown


class TestScoreBreakdown:
    """Test ScoreBreakdown data model."""
    
    def test_initialization_basic(self):
        """Test basic ScoreBreakdown initialization."""
        score = ScoreBreakdown(
            overall_score=85.5,
            title_score=90.0,
            description_score=80.0,
            text_quality_score=85.0
        )
        
        assert score.overall_score == 85.5
        assert score.title_score == 90.0
        assert score.description_score == 80.0
        assert score.text_quality_score == 85.0
        assert score.engagement_score == 0.0  # Default
        assert score.readability_score == 0.0  # Default
    
    def test_initialization_with_all_fields(self):
        """Test ScoreBreakdown with all fields."""
        score_details = {'key': 'value', 'data': [1, 2, 3]}
        score = ScoreBreakdown(
            overall_score=90.0,
            title_score=95.0,
            description_score=85.0,
            text_quality_score=88.0,
            engagement_score=75.0,
            readability_score=80.0,
            sentiment_score=10.0,
            seo_score=70.0,
            tags_score=65.0,
            similarity_score=60.0,
            score_details=score_details
        )
        
        assert score.overall_score == 90.0
        assert score.engagement_score == 75.0
        assert score.seo_score == 70.0
        assert score.tags_score == 65.0
        assert score.similarity_score == 60.0
        assert score.score_details == score_details
    
    def test_initialization_defaults(self):
        """Test ScoreBreakdown default values."""
        score = ScoreBreakdown(overall_score=75.0)
        
        assert score.overall_score == 75.0
        assert score.title_score == 0.0
        assert score.description_score == 0.0
        assert score.text_quality_score == 0.0
        assert score.engagement_score == 0.0
        assert score.readability_score == 0.0
        assert score.sentiment_score == 0.0
        assert score.seo_score == 0.0
        assert score.tags_score == 0.0
        assert score.similarity_score == 0.0
        assert score.score_details == {}
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        score = ScoreBreakdown(
            overall_score=85.0,
            title_score=90.0,
            description_score=80.0,
            text_quality_score=85.0,
            engagement_score=70.0,
            score_details={'test': 'data'}
        )
        
        result = score.to_dict()
        
        assert result['overall_score'] == 85.0
        assert result['title_score'] == 90.0
        assert result['description_score'] == 80.0
        assert result['text_quality_score'] == 85.0
        assert result['engagement_score'] == 70.0
        assert result['score_details'] == {'test': 'data'}
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'overall_score': 88.0,
            'title_score': 92.0,
            'description_score': 85.0,
            'text_quality_score': 87.0,
            'engagement_score': 75.0,
            'readability_score': 80.0,
            'sentiment_score': 15.0,
            'seo_score': 70.0,
            'tags_score': 65.0,
            'similarity_score': 60.0,
            'score_details': {'key': 'value'}
        }
        
        score = ScoreBreakdown.from_dict(data)
        
        assert score.overall_score == 88.0
        assert score.title_score == 92.0
        assert score.engagement_score == 75.0
        assert score.seo_score == 70.0
        assert score.score_details == {'key': 'value'}
    
    def test_from_dict_with_missing_fields(self):
        """Test creation from dictionary with missing optional fields."""
        data = {
            'overall_score': 75.0
        }
        
        score = ScoreBreakdown.from_dict(data)
        
        assert score.overall_score == 75.0
        assert score.title_score == 0.0
        assert score.description_score == 0.0
        assert score.score_details == {}
