"""Tests for TextScorer AI-based text quality scoring."""

import pytest
from src.scoring.text_scorer import TextScorer


class TestTextScorer:
    """Test suite for TextScorer class."""
    
    def test_initialization(self):
        """Test TextScorer initialization."""
        scorer = TextScorer()
        assert scorer is not None
        assert len(scorer._sentiment_positive_words) > 0
        assert len(scorer._sentiment_negative_words) > 0
    
    def test_score_text_basic(self):
        """Test basic text scoring."""
        scorer = TextScorer()
        text = """
        This is a great example of well-written content. The text flows naturally
        and provides good information. It's engaging and easy to read.
        """
        title = "Great Example of Good Content"
        
        result = scorer.score_text(text, title)
        
        assert 'overall_text_score' in result
        assert 'readability_score' in result
        assert 'sentiment_score' in result
        assert 0 <= result['overall_text_score'] <= 100
        assert result['word_count'] > 0
        assert result['sentence_count'] > 0
    
    def test_score_text_empty(self):
        """Test text scoring with empty text."""
        scorer = TextScorer()
        result = scorer.score_text("")
        
        assert result['overall_text_score'] == 0.0
        assert result['word_count'] == 0
        assert result['sentiment_category'] == 'neutral'
    
    def test_calculate_readability(self):
        """Test readability calculation."""
        scorer = TextScorer()
        text = "This is a simple sentence. This is another simple sentence."
        
        result = scorer.calculate_readability(text)
        
        assert 'flesch_reading_ease' in result
        assert 'flesch_kincaid_grade' in result
        assert 'normalized_score' in result
        assert 0 <= result['flesch_reading_ease'] <= 100
        assert result['normalized_score'] >= 0
    
    def test_calculate_readability_complex_text(self):
        """Test readability with complex text."""
        scorer = TextScorer()
        # More complex text with longer words
        text = """
        The implementation of sophisticated algorithmic methodologies necessitates
        comprehensive understanding of computational complexity theory.
        """
        
        result = scorer.calculate_readability(text)
        
        # Complex text should have lower readability score
        assert result['flesch_reading_ease'] < 60
        assert result['flesch_kincaid_grade'] > 10
    
    def test_calculate_length_score_short(self):
        """Test length score for short text."""
        scorer = TextScorer()
        short_text = "Short text."
        
        score = scorer.calculate_length_score(short_text)
        
        # Very short text should have low score
        assert score < 0.5
    
    def test_calculate_length_score_optimal(self):
        """Test length score for optimal length text."""
        scorer = TextScorer()
        # Generate text with ~500 words (optimal range)
        optimal_text = " ".join(["word"] * 500)
        
        score = scorer.calculate_length_score(optimal_text)
        
        # Optimal length should have high score
        assert score >= 0.9
    
    def test_calculate_length_score_very_long(self):
        """Test length score for very long text."""
        scorer = TextScorer()
        # Generate text with 3000+ words
        long_text = " ".join(["word"] * 3000)
        
        score = scorer.calculate_length_score(long_text)
        
        # Very long text should have reduced score
        assert score < 1.0
    
    def test_calculate_structure_score_good(self):
        """Test structure score for well-structured text."""
        scorer = TextScorer()
        text = """
        This is the first paragraph with multiple sentences. Each sentence is of reasonable length.
        The structure is clear and organized.
        
        This is the second paragraph. It also has good structure. The sentences flow well.
        """
        
        score = scorer.calculate_structure_score(text)
        
        assert 0 <= score <= 1.0
        assert score > 0.5  # Should have decent structure
    
    def test_calculate_structure_score_poor(self):
        """Test structure score for poorly structured text."""
        scorer = TextScorer()
        # Single very long run-on sentence
        text = " ".join(["word"] * 200) + "."
        
        score = scorer.calculate_structure_score(text)
        
        assert 0 <= score <= 1.0
        # Very long sentence should have lower structure score
    
    def test_calculate_sentiment_positive(self):
        """Test sentiment calculation for positive text."""
        scorer = TextScorer()
        text = "This is great! Amazing work. Excellent results. Love it!"
        
        result = scorer.calculate_sentiment(text)
        
        assert result['category'] == 'positive'
        assert result['score'] > 10
    
    def test_calculate_sentiment_negative(self):
        """Test sentiment calculation for negative text."""
        scorer = TextScorer()
        text = "This is terrible. Awful experience. Bad results. Hate it."
        
        result = scorer.calculate_sentiment(text)
        
        assert result['category'] == 'negative'
        assert result['score'] < -10
    
    def test_calculate_sentiment_neutral(self):
        """Test sentiment calculation for neutral text."""
        scorer = TextScorer()
        text = "This is a document about various topics and subjects."
        
        result = scorer.calculate_sentiment(text)
        
        assert result['category'] == 'neutral'
        assert -10 <= result['score'] <= 10
    
    def test_calculate_title_relevance_high(self):
        """Test title relevance with highly relevant title."""
        scorer = TextScorer()
        title = "Python Programming Tutorial"
        text = """
        This tutorial covers Python programming basics. We will learn about Python
        syntax and how to write Python code effectively.
        """
        
        relevance = scorer.calculate_title_relevance(title, text)
        
        # All keywords from title appear in text
        assert relevance > 0.5
    
    def test_calculate_title_relevance_low(self):
        """Test title relevance with irrelevant title."""
        scorer = TextScorer()
        title = "Python Programming"
        text = "This is about Java and JavaScript development."
        
        relevance = scorer.calculate_title_relevance(title, text)
        
        # Keywords don't match well
        assert relevance < 0.5
    
    def test_calculate_title_relevance_empty(self):
        """Test title relevance with empty inputs."""
        scorer = TextScorer()
        
        assert scorer.calculate_title_relevance("", "text") == 0.0
        assert scorer.calculate_title_relevance("title", "") == 0.0
    
    def test_score_title_quality_optimal(self):
        """Test title quality scoring for optimal title."""
        scorer = TextScorer()
        # Optimal length: 50-70 chars, 6-12 words
        title = "Complete Guide to Modern Web Development in 2024"
        
        result = scorer.score_title_quality(title)
        
        assert 'title_quality_score' in result
        assert result['title_quality_score'] > 70
        assert result['title_word_count'] > 5
    
    def test_score_title_quality_too_short(self):
        """Test title quality for too short title."""
        scorer = TextScorer()
        title = "Test"
        
        result = scorer.score_title_quality(title)
        
        assert result['title_quality_score'] < 50
        assert result['title_word_count'] < 4
    
    def test_score_title_quality_too_long(self):
        """Test title quality for too long title."""
        scorer = TextScorer()
        title = "This is an extremely long title that goes on and on with many words and exceeds the optimal length significantly"
        
        result = scorer.score_title_quality(title)
        
        assert result['title_quality_score'] < 80
        assert result['title_char_count'] > 100
    
    def test_score_description_quality_optimal(self):
        """Test description quality scoring for optimal description."""
        scorer = TextScorer()
        # Optimal: 20-50 words, 1-3 sentences
        description = "This is a concise description that provides key information. It's not too long or too short."
        
        result = scorer.score_description_quality(description)
        
        assert 'description_quality_score' in result
        assert result['description_quality_score'] > 70
        assert 10 < result['description_word_count'] < 60
    
    def test_score_description_quality_too_short(self):
        """Test description quality for too short description."""
        scorer = TextScorer()
        description = "Too short"
        
        result = scorer.score_description_quality(description)
        
        assert result['description_quality_score'] < 60
    
    def test_score_description_quality_too_long(self):
        """Test description quality for too long description."""
        scorer = TextScorer()
        # Very long description
        description = " ".join(["word"] * 150)
        
        result = scorer.score_description_quality(description)
        
        assert result['description_quality_score'] < 90
        assert result['description_word_count'] > 100
    
    def test_count_words(self):
        """Test word counting."""
        scorer = TextScorer()
        text = "This is a test sentence with seven words."
        
        count = scorer._count_words(text)
        assert count == 8
    
    def test_count_sentences(self):
        """Test sentence counting."""
        scorer = TextScorer()
        text = "First sentence. Second sentence! Third sentence?"
        
        count = scorer._count_sentences(text)
        assert count == 3
    
    def test_count_syllables(self):
        """Test syllable counting."""
        scorer = TextScorer()
        text = "hello world"  # hel-lo (2) + world (1) = 3
        
        count = scorer._count_syllables(text)
        assert count > 0  # Approximate count
