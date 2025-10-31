"""Sentiment analysis module for community sources."""

from typing import Dict, Any, Optional
from enum import Enum


class SentimentLabel(Enum):
    """Sentiment classification labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SentimentAnalyzer:
    """Analyzes sentiment of text content.
    
    Uses VADER sentiment analysis optimized for social media text.
    Follows Single Responsibility Principle by focusing only on sentiment analysis.
    """
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self._analyzer = None
        self._initialize_analyzer()
    
    def _initialize_analyzer(self):
        """Initialize VADER sentiment analyzer."""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self._analyzer = SentimentIntensityAnalyzer()
        except ImportError:
            # VADER not available, will use fallback
            self._analyzer = None
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment label and score:
                - sentiment: 'positive', 'negative', or 'neutral'
                - sentiment_score: Float between -1 (most negative) and 1 (most positive)
                - confidence: Float between 0 and 1 indicating confidence
        """
        if not text or not text.strip():
            return {
                'sentiment': SentimentLabel.NEUTRAL.value,
                'sentiment_score': 0.0,
                'confidence': 0.0
            }
        
        if self._analyzer:
            return self._analyze_with_vader(text)
        else:
            return self._analyze_with_fallback(text)
    
    def _analyze_with_vader(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        scores = self._analyzer.polarity_scores(text)
        
        # Extract compound score (ranges from -1 to 1)
        compound_score = scores['compound']
        
        # Determine sentiment label using VADER thresholds
        if compound_score >= 0.05:
            sentiment = SentimentLabel.POSITIVE.value
        elif compound_score <= -0.05:
            sentiment = SentimentLabel.NEGATIVE.value
        else:
            sentiment = SentimentLabel.NEUTRAL.value
        
        # Calculate confidence based on the magnitude of the compound score
        confidence = abs(compound_score)
        
        return {
            'sentiment': sentiment,
            'sentiment_score': compound_score,
            'confidence': confidence,
            'raw_scores': scores  # Include raw pos, neg, neu scores
        }
    
    def _analyze_with_fallback(self, text: str) -> Dict[str, Any]:
        """Simple fallback sentiment analysis without VADER.
        
        Uses basic keyword matching for sentiment detection.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        text_lower = text.lower()
        
        # Simple positive/negative word lists
        positive_words = [
            'good', 'great', 'awesome', 'excellent', 'amazing', 'love', 'like',
            'best', 'wonderful', 'fantastic', 'helpful', 'thanks', 'thank you',
            'appreciate', 'perfect', 'brilliant', 'outstanding'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'worst',
            'disappointing', 'poor', 'useless', 'waste', 'boring', 'annoying',
            'frustrated', 'frustrating', 'problem', 'issue', 'broken', 'error'
        ]
        
        # Count positive and negative words
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate simple score
        total_count = pos_count + neg_count
        if total_count == 0:
            sentiment_score = 0.0
            sentiment = SentimentLabel.NEUTRAL.value
            confidence = 0.0
        else:
            sentiment_score = (pos_count - neg_count) / max(total_count, 1)
            
            if sentiment_score > 0.2:
                sentiment = SentimentLabel.POSITIVE.value
            elif sentiment_score < -0.2:
                sentiment = SentimentLabel.NEGATIVE.value
            else:
                sentiment = SentimentLabel.NEUTRAL.value
            
            confidence = min(abs(sentiment_score), 1.0)
        
        return {
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'confidence': confidence
        }
    
    def batch_analyze(self, texts: list[str]) -> list[Dict[str, Any]]:
        """Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment analysis results
        """
        return [self.analyze(text) for text in texts]
