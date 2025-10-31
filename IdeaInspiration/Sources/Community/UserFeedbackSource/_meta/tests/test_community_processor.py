"""Tests for community processor."""

import pytest
from datetime import datetime
from src.core.sentiment_analyzer import SentimentAnalyzer
from src.core.community_processor import CommunityProcessor


class TestCommunityProcessor:
    """Test cases for community processor."""
    
    def test_process_comment(self):
        """Test comment processing."""
        analyzer = SentimentAnalyzer()
        processor = CommunityProcessor(analyzer)
        
        result = processor.process_comment(
            text="Great video! Very helpful tutorial.",
            author="testuser",
            source="user_feedback",
            source_id="comment123",
            platform="youtube",
            parent_content="video123",
            upvotes=10,
            replies=2,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            category="tutorial"
        )
        
        assert result['source'] == 'user_feedback'
        assert result['source_id'] == 'comment123'
        assert result['content']['type'] == 'comment'
        assert result['content']['text'] == "Great video! Very helpful tutorial."
        assert result['content']['author'] == 'testuser'
        assert result['context']['platform'] == 'youtube'
        assert result['context']['parent_content'] == 'video123'
        assert result['metrics']['upvotes'] == 10
        assert result['metrics']['replies'] == 2
        assert 'sentiment' in result['analysis']
        assert 'topics' in result['analysis']
        assert 'intent' in result['analysis']
        assert 'engagement_score' in result['universal_metrics']
        assert 'relevance_score' in result['universal_metrics']
        assert 'actionability' in result['universal_metrics']
    
    def test_process_question(self):
        """Test question processing."""
        analyzer = SentimentAnalyzer()
        processor = CommunityProcessor(analyzer)
        
        result = processor.process_question(
            text="How do I implement this feature?",
            title="Question about feature implementation",
            author="testuser",
            source="qa",
            source_id="q123",
            platform="stackoverflow",
            upvotes=5,
            answers=3,
            views=100,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            tags=["python", "programming"],
            category="technology"
        )
        
        assert result['source'] == 'qa'
        assert result['content']['type'] == 'question'
        assert result['content']['title'] == 'Question about feature implementation'
        assert result['analysis']['topics'] == ['python', 'programming']
        assert result['analysis']['intent'] == 'question'
    
    def test_intent_detection(self):
        """Test intent detection."""
        analyzer = SentimentAnalyzer()
        processor = CommunityProcessor(analyzer)
        
        # Question
        assert processor._detect_intent("How do I do this?") == 'question'
        
        # Suggestion
        assert processor._detect_intent("You should add this feature") == 'suggestion'
        
        # Complaint
        assert processor._detect_intent("This is broken and terrible") == 'complaint'
        
        # Praise
        assert processor._detect_intent("Great work! Amazing video!") == 'praise'
    
    def test_topic_extraction(self):
        """Test topic extraction."""
        analyzer = SentimentAnalyzer()
        processor = CommunityProcessor(analyzer)
        
        text = "Python programming tutorial about machine learning and data science"
        topics = processor._extract_topics(text, max_topics=5)
        
        assert isinstance(topics, list)
        assert len(topics) <= 5
        # Should extract relevant keywords
        assert 'python' in topics or 'programming' in topics
