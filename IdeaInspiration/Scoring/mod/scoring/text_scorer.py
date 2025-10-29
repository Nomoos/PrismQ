"""AI-based text quality scoring for content evaluation."""

from typing import Dict, Any, Optional
import re
import math


class TextScorer:
    """Scores text quality using various metrics and local AI models.
    
    This class provides methods to evaluate text quality including:
    - Readability (Flesch Reading Ease, Flesch-Kincaid Grade Level)
    - Text length and structure
    - Sentiment analysis (basic implementation, can be enhanced with AI models)
    - Coherence and clarity metrics
    """
    
    def __init__(self):
        """Initialize text scorer."""
        self._sentiment_positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'awesome', 'best', 'love', 'perfect', 'beautiful', 'brilliant',
            'happy', 'joy', 'success', 'win', 'incredible', 'outstanding'
        }
        self._sentiment_negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'poor',
            'fail', 'failed', 'disappointing', 'angry', 'sad', 'wrong', 'problem',
            'issue', 'negative', 'difficult', 'hard'
        }
    
    def score_text(self, text: str, title: Optional[str] = None) -> Dict[str, float]:
        """Calculate comprehensive text quality score.
        
        Args:
            text: The text content to score
            title: Optional title for additional context
            
        Returns:
            Dictionary containing various text quality metrics
        """
        if not text:
            return self._get_empty_scores()
        
        readability = self.calculate_readability(text)
        length_score = self.calculate_length_score(text)
        structure_score = self.calculate_structure_score(text)
        sentiment = self.calculate_sentiment(text)
        
        # Title relevance score if title is provided
        title_relevance = 0.0
        if title:
            title_relevance = self.calculate_title_relevance(title, text)
        
        # Calculate overall text quality score (0-100)
        overall_score = (
            readability['normalized_score'] * 0.25 +
            length_score * 0.15 +
            structure_score * 0.20 +
            (sentiment['normalized_score'] + 50) / 100 * 0.20 +  # Convert -50 to 50 range to 0-1
            title_relevance * 0.20
        )
        
        return {
            'overall_text_score': min(overall_score * 100, 100.0),
            'readability_score': readability['flesch_reading_ease'],
            'readability_grade': readability['flesch_kincaid_grade'],
            'length_score': length_score,
            'structure_score': structure_score,
            'sentiment_score': sentiment['score'],
            'sentiment_category': sentiment['category'],
            'title_relevance': title_relevance,
            'word_count': self._count_words(text),
            'sentence_count': self._count_sentences(text)
        }
    
    def calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate readability scores using Flesch metrics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with readability metrics
        """
        words = self._count_words(text)
        sentences = self._count_sentences(text)
        syllables = self._count_syllables(text)
        
        if words == 0 or sentences == 0:
            return {'flesch_reading_ease': 0.0, 'flesch_kincaid_grade': 0.0, 'normalized_score': 0.0}
        
        # Flesch Reading Ease: 206.835 - 1.015(words/sentences) - 84.6(syllables/words)
        flesch_reading_ease = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        flesch_reading_ease = max(0.0, min(100.0, flesch_reading_ease))  # Clamp to 0-100
        
        # Flesch-Kincaid Grade Level: 0.39(words/sentences) + 11.8(syllables/words) - 15.59
        flesch_kincaid_grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
        flesch_kincaid_grade = max(0.0, flesch_kincaid_grade)
        
        # Normalize Flesch Reading Ease to 0-1 scale (higher is better)
        normalized_score = flesch_reading_ease / 100.0
        
        return {
            'flesch_reading_ease': flesch_reading_ease,
            'flesch_kincaid_grade': flesch_kincaid_grade,
            'normalized_score': normalized_score
        }
    
    def calculate_length_score(self, text: str) -> float:
        """Calculate score based on text length (optimal length ranges).
        
        Args:
            text: Text to analyze
            
        Returns:
            Length score between 0 and 1
        """
        word_count = self._count_words(text)
        
        # Optimal range: 300-1000 words for general content
        if word_count < 100:
            # Too short
            return word_count / 100.0
        elif word_count <= 300:
            # Growing to optimal
            return 0.7 + (word_count - 100) / 200 * 0.3
        elif word_count <= 1000:
            # Optimal range
            return 1.0
        elif word_count <= 2000:
            # Still good but declining
            return 1.0 - (word_count - 1000) / 1000 * 0.2
        else:
            # Too long
            return max(0.5, 0.8 - (word_count - 2000) / 3000 * 0.3)
    
    def calculate_structure_score(self, text: str) -> float:
        """Calculate score based on text structure (paragraphs, sentences).
        
        Args:
            text: Text to analyze
            
        Returns:
            Structure score between 0 and 1
        """
        if not text:
            return 0.0
        
        sentences = self._count_sentences(text)
        words = self._count_words(text)
        paragraphs = len([p for p in text.split('\n\n') if p.strip()])
        
        if sentences == 0:
            return 0.0
        
        # Average sentence length (optimal: 15-20 words)
        avg_sentence_length = words / sentences if sentences > 0 else 0
        sentence_score = 1.0 - abs(avg_sentence_length - 17.5) / 17.5 * 0.5
        sentence_score = max(0.0, min(1.0, sentence_score))
        
        # Paragraph structure (optimal: 1 paragraph per 3-5 sentences)
        paragraph_score = 1.0
        if paragraphs > 0:
            sentences_per_paragraph = sentences / paragraphs
            if sentences_per_paragraph < 2:
                paragraph_score = sentences_per_paragraph / 2
            elif sentences_per_paragraph <= 6:
                paragraph_score = 1.0
            else:
                paragraph_score = max(0.5, 1.0 - (sentences_per_paragraph - 6) / 10 * 0.5)
        
        return (sentence_score * 0.6 + paragraph_score * 0.4)
    
    def calculate_sentiment(self, text: str) -> Dict[str, Any]:
        """Calculate sentiment score using word matching.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment score and category
        """
        if not text:
            return {'score': 0.0, 'category': 'neutral', 'normalized_score': 0.0}
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in self._sentiment_positive_words)
        negative_count = sum(1 for word in words if word in self._sentiment_negative_words)
        
        # Calculate sentiment score (-50 to 50)
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            score = 0.0
        else:
            score = ((positive_count - negative_count) / total_sentiment_words) * 50
        
        # Categorize sentiment
        if score > 10:
            category = 'positive'
        elif score < -10:
            category = 'negative'
        else:
            category = 'neutral'
        
        return {
            'score': score,
            'category': category,
            'normalized_score': score  # Already in -50 to 50 range
        }
    
    def calculate_title_relevance(self, title: str, text: str) -> float:
        """Calculate how relevant the title is to the text content.
        
        Args:
            title: Title of the content
            text: Full text content
            
        Returns:
            Relevance score between 0 and 1
        """
        if not title or not text:
            return 0.0
        
        # Extract keywords from title (remove common words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        title_words = set(re.findall(r'\b\w+\b', title.lower())) - stop_words
        
        if not title_words:
            return 0.5  # Neutral if no meaningful words
        
        # Count how many title keywords appear in text
        text_lower = text.lower()
        matches = sum(1 for word in title_words if word in text_lower)
        
        # Calculate relevance score
        relevance = matches / len(title_words)
        return min(relevance, 1.0)
    
    def score_title_quality(self, title: str) -> Dict[str, float]:
        """Score the quality of a title specifically.
        
        Args:
            title: Title to score
            
        Returns:
            Dictionary with title quality metrics
        """
        if not title:
            return {'title_quality_score': 0.0, 'title_length_score': 0.0, 'title_word_count': 0}
        
        word_count = self._count_words(title)
        char_count = len(title)
        
        # Optimal title length: 50-70 characters, 6-12 words
        char_score = 1.0
        if char_count < 30:
            char_score = char_count / 30
        elif char_count <= 70:
            char_score = 1.0
        elif char_count <= 100:
            char_score = 1.0 - (char_count - 70) / 30 * 0.3
        else:
            char_score = max(0.4, 0.7 - (char_count - 100) / 50 * 0.3)
        
        word_score = 1.0
        if word_count < 4:
            word_score = word_count / 4 * 0.7
        elif word_count <= 12:
            word_score = 1.0
        else:
            word_score = max(0.5, 1.0 - (word_count - 12) / 8 * 0.5)
        
        overall_score = (char_score * 0.5 + word_score * 0.5) * 100
        
        return {
            'title_quality_score': overall_score,
            'title_length_score': char_score,
            'title_word_count': word_count,
            'title_char_count': char_count
        }
    
    def score_description_quality(self, description: str) -> Dict[str, float]:
        """Score the quality of a description specifically.
        
        Args:
            description: Description to score
            
        Returns:
            Dictionary with description quality metrics
        """
        if not description:
            return {'description_quality_score': 0.0, 'description_length_score': 0.0}
        
        word_count = self._count_words(description)
        sentence_count = self._count_sentences(description)
        
        # Optimal description: 20-50 words, 1-3 sentences
        length_score = 1.0
        if word_count < 10:
            length_score = word_count / 10
        elif word_count <= 50:
            length_score = 1.0
        elif word_count <= 100:
            length_score = 1.0 - (word_count - 50) / 50 * 0.3
        else:
            length_score = max(0.4, 0.7 - (word_count - 100) / 100 * 0.3)
        
        sentence_score = 1.0
        if sentence_count == 0:
            sentence_score = 0.0
        elif sentence_count <= 3:
            sentence_score = 1.0
        else:
            sentence_score = max(0.5, 1.0 - (sentence_count - 3) / 5 * 0.5)
        
        overall_score = (length_score * 0.6 + sentence_score * 0.4) * 100
        
        return {
            'description_quality_score': overall_score,
            'description_length_score': length_score,
            'description_word_count': word_count,
            'description_sentence_count': sentence_count
        }
    
    # Helper methods
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(re.findall(r'\b\w+\b', text))
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def _count_syllables(self, text: str) -> int:
        """Estimate syllable count (simple heuristic)."""
        words = re.findall(r'\b\w+\b', text.lower())
        syllable_count = 0
        
        for word in words:
            # Simple syllable counting heuristic
            word = word.rstrip('e')  # Remove trailing 'e'
            vowels = 'aeiouy'
            syllables = 0
            prev_was_vowel = False
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    syllables += 1
                prev_was_vowel = is_vowel
            
            # Ensure at least one syllable per word
            syllables = max(1, syllables)
            syllable_count += syllables
        
        return syllable_count
    
    def _get_empty_scores(self) -> Dict[str, float]:
        """Return empty scores for invalid input."""
        return {
            'overall_text_score': 0.0,
            'readability_score': 0.0,
            'readability_grade': 0.0,
            'length_score': 0.0,
            'structure_score': 0.0,
            'sentiment_score': 0.0,
            'sentiment_category': 'neutral',
            'title_relevance': 0.0,
            'word_count': 0,
            'sentence_count': 0
        }
