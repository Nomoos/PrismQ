"""Tests for scoring engine module."""

import pytest
from mod.scoring import ScoringEngine
from src.models import ScoreBreakdown


# Mock IdeaInspiration for testing
class MockIdeaInspiration:
    """Mock IdeaInspiration object for testing."""
    def __init__(self, title="", description="", text_content="", metadata=None):
        self.title = title
        self.description = description
        self.text_content = text_content
        self.metadata = metadata or {}
        self.content_type = 'text'


class TestScoringEngine:
    """Test suite for ScoringEngine class."""

    def test_initialization_default_weights(self):
        """Test that ScoringEngine initializes with default weights."""
        engine = ScoringEngine()
        assert engine.weights == [1.0, 0.8, 0.6]

    def test_initialization_custom_weights(self):
        """Test that ScoringEngine initializes with custom weights."""
        custom_weights = [0.5, 0.3, 0.2]
        engine = ScoringEngine(weights=custom_weights)
        assert engine.weights == custom_weights

    def test_normalize_metric(self):
        """Test metric normalization."""
        # Test normal case
        assert ScoringEngine._normalize_metric(500, 1000) == 0.5
        
        # Test at max value
        assert ScoringEngine._normalize_metric(1000, 1000) == 1.0
        
        # Test above max value (should cap at 1.0)
        assert ScoringEngine._normalize_metric(1500, 1000) == 1.0
        
        # Test zero value
        assert ScoringEngine._normalize_metric(0, 1000) == 0.0
        
        # Test zero max_value
        assert ScoringEngine._normalize_metric(100, 0) == 0.0

    def test_calculate_score_basic(self):
        """Test basic score calculation."""
        engine = ScoringEngine()
        metrics = {
            'views': 100000,
            'likes': 5000,
            'comments': 100,
            'shares': 500,
            'saves': 200
        }
        
        score, score_dict = engine.calculate_score(metrics)
        
        # Check that score is within valid range
        assert 0 <= score <= 100
        
        # Check that all expected keys are in score_dict
        assert 'view_score' in score_dict
        assert 'like_score' in score_dict
        assert 'comment_score' in score_dict
        assert 'engagement_score' in score_dict
        assert 'final_score' in score_dict

    def test_calculate_score_zero_views(self):
        """Test score calculation with zero views."""
        engine = ScoringEngine()
        metrics = {
            'views': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'saves': 0
        }
        
        score, score_dict = engine.calculate_score(metrics)
        
        # With zero metrics, score should be 0
        assert score == 0.0
        assert score_dict['engagement_score'] == 0.0

    def test_calculate_reddit_score(self):
        """Test Reddit post score calculation."""
        engine = ScoringEngine()
        post_data = {
            'num_views': 50000,
            'score': 1000,
            'num_comments': 50
        }
        
        score, score_dict = engine.calculate_reddit_score(post_data)
        
        assert 0 <= score <= 100
        assert 'final_score' in score_dict

    def test_calculate_youtube_score(self):
        """Test YouTube video score calculation."""
        engine = ScoringEngine()
        video_data = {
            'statistics': {
                'viewCount': '1000000',
                'likeCount': '50000',
                'commentCount': '1000'
            }
        }
        
        score, score_dict = engine.calculate_youtube_score(video_data)
        
        assert 0 <= score <= 100
        assert 'final_score' in score_dict
        assert score_dict['view_score'] == 1.0  # 1M views normalized to 1M max

    def test_calculate_engagement_rate(self):
        """Test engagement rate calculation."""
        engine = ScoringEngine()
        
        # Test normal case
        metrics = {
            'views': 1000,
            'likes': 50,
            'comments': 10,
            'shares': 5,
            'saves': 5
        }
        
        engagement_rate = engine.calculate_engagement_rate(metrics)
        expected_rate = ((50 + 10 + 5 + 5) / 1000) * 100
        assert engagement_rate == expected_rate
        
        # Test with zero views
        metrics_zero = {
            'views': 0,
            'likes': 50,
            'comments': 10
        }
        assert engine.calculate_engagement_rate(metrics_zero) == 0.0

    def test_calculate_watch_through_rate(self):
        """Test watch-through rate calculation."""
        engine = ScoringEngine()
        
        # Test normal case (75% watch-through)
        metrics = {
            'average_watch_time': 45,
            'video_length': 60
        }
        
        watch_through_rate = engine.calculate_watch_through_rate(metrics)
        assert watch_through_rate == 75.0
        
        # Test 100% watch-through
        metrics_full = {
            'average_watch_time': 60,
            'video_length': 60
        }
        assert engine.calculate_watch_through_rate(metrics_full) == 100.0
        
        # Test over 100% (should cap at 100)
        metrics_over = {
            'average_watch_time': 90,
            'video_length': 60
        }
        assert engine.calculate_watch_through_rate(metrics_over) == 100.0
        
        # Test zero video length
        metrics_zero = {
            'average_watch_time': 30,
            'video_length': 0
        }
        assert engine.calculate_watch_through_rate(metrics_zero) == 0.0

    def test_calculate_conversion_rate(self):
        """Test conversion rate calculation."""
        engine = ScoringEngine()
        
        # Test normal case
        metrics = {
            'views': 10000,
            'conversions': 100
        }
        
        conversion_rate = engine.calculate_conversion_rate(metrics)
        assert conversion_rate == 1.0  # (100/10000) * 100
        
        # Test with zero views
        metrics_zero = {
            'views': 0,
            'conversions': 100
        }
        assert engine.calculate_conversion_rate(metrics_zero) == 0.0

    def test_calculate_relative_performance_index(self):
        """Test RPI calculation."""
        engine = ScoringEngine()
        
        # Test normal case (current views double the median)
        metrics = {
            'views': 200000,
            'channel_median_views': 100000
        }
        
        rpi = engine.calculate_relative_performance_index(metrics, 'views')
        assert rpi == 200.0
        
        # Test below median
        metrics_below = {
            'views': 50000,
            'channel_median_views': 100000
        }
        rpi_below = engine.calculate_relative_performance_index(metrics_below, 'views')
        assert rpi_below == 50.0
        
        # Test with zero median
        metrics_zero = {
            'views': 100000,
            'channel_median_views': 0
        }
        assert engine.calculate_relative_performance_index(metrics_zero, 'views') == 0.0

    def test_calculate_universal_content_score(self):
        """Test Universal Content Score calculation."""
        engine = ScoringEngine()
        metrics = {
            'views': 1000000,
            'likes': 50000,
            'comments': 1000,
            'shares': 5000,
            'saves': 2000,
            'average_watch_time': 45,
            'video_length': 60,
            'channel_median_views': 500000,
            'conversions': 1000
        }
        
        ucs_results = engine.calculate_universal_content_score(metrics)
        
        # Check all expected keys are present
        assert 'universal_content_score' in ucs_results
        assert 'engagement_rate' in ucs_results
        assert 'watch_through_rate' in ucs_results
        assert 'relative_performance_index' in ucs_results
        assert 'conversion_rate' in ucs_results
        
        # Check UCS is within valid range
        assert 0 <= ucs_results['universal_content_score'] <= 100
        
        # Verify individual components
        assert ucs_results['engagement_rate'] > 0
        assert ucs_results['watch_through_rate'] == 75.0
        assert ucs_results['relative_performance_index'] == 200.0

    def test_calculate_universal_content_score_capping(self):
        """Test that UCS is capped at 100."""
        engine = ScoringEngine()
        # Extreme metrics that would exceed 100
        metrics = {
            'views': 1000,
            'likes': 500,
            'comments': 300,
            'shares': 200,
            'saves': 100,
            'average_watch_time': 100,
            'video_length': 60,
            'channel_median_views': 100,
            'conversions': 500
        }
        
        ucs_results = engine.calculate_universal_content_score(metrics)
        
        # UCS should never exceed 100
        assert ucs_results['universal_content_score'] <= 100.0
    
    def test_score_text_content(self):
        """Test text content scoring method."""
        engine = ScoringEngine()
        
        title = "Introduction to Machine Learning"
        description = "A comprehensive guide to ML basics."
        text_content = """
        Machine learning is a subset of artificial intelligence. This guide covers
        the fundamental concepts and provides practical examples. You'll learn about
        supervised and unsupervised learning methods.
        """
        
        result = engine.score_text_content(title, description, text_content)
        
        assert 'composite_score' in result
        assert 'text_quality' in result
        assert 'title_quality' in result
        assert 'description_quality' in result
        assert 0 <= result['composite_score'] <= 100
    
    def test_score_idea_inspiration_text_only(self):
        """Test scoring IdeaInspiration with text content only."""
        engine = ScoringEngine()
        
        idea = MockIdeaInspiration(
            title="Test Article Title",
            description="This is a test article description.",
            text_content="This is the full text content of the article. It contains multiple sentences and provides information."
        )
        
        result = engine.score_idea_inspiration(idea)
        
        assert isinstance(result, ScoreBreakdown)
        assert result.overall_score > 0
        assert result.title_score > 0
        assert result.description_score > 0
        assert result.text_quality_score > 0
        assert result.engagement_score == 0.0  # No engagement metrics
        assert 'text_quality' in result.score_details
        assert 'title_quality' in result.score_details
    
    def test_score_idea_inspiration_youtube(self):
        """Test scoring IdeaInspiration from YouTube video."""
        engine = ScoringEngine()
        
        idea = MockIdeaInspiration(
            title="Amazing Python Tutorial",
            description="Learn Python programming in this comprehensive tutorial.",
            text_content="""
            Welcome to this Python programming tutorial. In this video, we'll cover the basics
            of Python including variables, functions, and object-oriented programming.
            """,
            metadata={
                'statistics': {
                    'viewCount': '100000',
                    'likeCount': '5000',
                    'commentCount': '250'
                }
            }
        )
        
        result = engine.score_idea_inspiration(idea)
        
        assert isinstance(result, ScoreBreakdown)
        assert result.overall_score > 0
        assert result.engagement_score > 0  # Has engagement metrics
        assert result.title_score > 0
        assert result.text_quality_score > 0
        assert 'engagement_details' in result.score_details
    
    def test_score_idea_inspiration_reddit(self):
        """Test scoring IdeaInspiration from Reddit post."""
        engine = ScoringEngine()
        
        idea = MockIdeaInspiration(
            title="Great Tips for Learning Python",
            description="Here are some excellent tips for learning Python programming.",
            text_content="Here are some excellent tips for learning Python programming. Start with the basics and practice regularly. Join communities and build projects.",
            metadata={
                'score': 1500,
                'num_comments': 75,
                'subreddit': 'python'
            }
        )
        
        result = engine.score_idea_inspiration(idea)
        
        assert isinstance(result, ScoreBreakdown)
        assert result.overall_score > 0
        assert result.engagement_score > 0  # Has engagement metrics
        assert result.title_score > 0
        assert result.text_quality_score > 0
    
    def test_text_scorer_integration(self):
        """Test that TextScorer is properly integrated in ScoringEngine."""
        engine = ScoringEngine()
        
        assert engine.text_scorer is not None
        assert hasattr(engine.text_scorer, 'score_text')
