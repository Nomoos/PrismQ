"""Tests for sentiment analyzer."""

import pytest
from src.core.sentiment_analyzer import SentimentAnalyzer, SentimentLabel


class TestSentimentAnalyzer:
    """Test cases for sentiment analyzer."""
    
    def test_positive_sentiment(self):
        """Test detection of positive sentiment."""
        analyzer = SentimentAnalyzer()
        
        text = "This is amazing! I love this video. Great work!"
        result = analyzer.analyze(text)
        
        assert result['sentiment'] == SentimentLabel.POSITIVE.value
        assert result['sentiment_score'] > 0
    
    def test_negative_sentiment(self):
        """Test detection of negative sentiment."""
        analyzer = SentimentAnalyzer()
        
        text = "This is terrible. I hate this. Worst video ever."
        result = analyzer.analyze(text)
        
        assert result['sentiment'] == SentimentLabel.NEGATIVE.value
        assert result['sentiment_score'] < 0
    
    def test_neutral_sentiment(self):
        """Test detection of neutral sentiment."""
        analyzer = SentimentAnalyzer()
        
        text = "This is a video about Python programming."
        result = analyzer.analyze(text)
        
        assert result['sentiment'] == SentimentLabel.NEUTRAL.value
    
    def test_empty_text(self):
        """Test handling of empty text."""
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze("")
        
        assert result['sentiment'] == SentimentLabel.NEUTRAL.value
        assert result['sentiment_score'] == 0.0
        assert result['confidence'] == 0.0
    
    def test_batch_analyze(self):
        """Test batch analysis."""
        analyzer = SentimentAnalyzer()
        
        texts = [
            "Great video!",
            "This is terrible.",
            "Just a normal comment."
        ]
        
        results = analyzer.batch_analyze(texts)
        
        assert len(results) == 3
        assert results[0]['sentiment'] == SentimentLabel.POSITIVE.value
        assert results[1]['sentiment'] == SentimentLabel.NEGATIVE.value
