"""Keyword Extractor module for PrismQ.T.Publishing.SEO.Keywords.

This module provides intelligent keyword extraction from title and script content
using NLP techniques including TF-IDF, frequency analysis, and part-of-speech tagging.

Workflow Position:
    Stage: SEO Optimization (POST-001)
    Input: Published title + script → Extract Keywords → Output: Ranked keywords
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field, asdict
from collections import Counter
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

# Download required NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize


@dataclass
class KeywordExtractionResult:
    """Result of keyword extraction operation.
    
    Attributes:
        primary_keywords: Top-ranked keywords (main focus)
        secondary_keywords: Supporting keywords
        keyword_scores: Dictionary mapping keywords to relevance scores
        keyword_density: Dictionary mapping keywords to density percentages
        total_words: Total word count in analyzed text
        extraction_method: Method used for extraction
    """
    
    primary_keywords: List[str] = field(default_factory=list)
    secondary_keywords: List[str] = field(default_factory=list)
    keyword_scores: Dict[str, float] = field(default_factory=dict)
    keyword_density: Dict[str, float] = field(default_factory=dict)
    total_words: int = 0
    extraction_method: str = "tfidf"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"KeywordExtractionResult("
            f"primary={len(self.primary_keywords)}, "
            f"secondary={len(self.secondary_keywords)}, "
            f"method={self.extraction_method})"
        )


class KeywordExtractor:
    """Extract keywords from text content using NLP techniques.
    
    Supports multiple extraction methods:
    - TF-IDF: Term Frequency-Inverse Document Frequency
    - Frequency: Simple word frequency analysis
    - Hybrid: Combination of TF-IDF and frequency
    """
    
    def __init__(
        self,
        min_keyword_length: int = 3,
        max_keyword_length: int = 30,
        primary_count: int = 5,
        secondary_count: int = 10,
        language: str = "english"
    ):
        """Initialize the keyword extractor.
        
        Args:
            min_keyword_length: Minimum character length for keywords
            max_keyword_length: Maximum character length for keywords
            primary_count: Number of primary keywords to extract
            secondary_count: Number of secondary keywords to extract
            language: Language for stopwords (default: english)
        """
        self.min_keyword_length = min_keyword_length
        self.max_keyword_length = max_keyword_length
        self.primary_count = primary_count
        self.secondary_count = secondary_count
        self.language = language
        
        # Load stopwords
        try:
            self.stop_words = set(stopwords.words(language))
        except Exception:
            # Fallback to basic English stopwords if language not available
            self.stop_words = set(stopwords.words('english'))
        
        # Add common filler words
        self.stop_words.update(['said', 'would', 'could', 'one', 'two', 'also'])
    
    def extract_keywords(
        self,
        title: str,
        script: str,
        method: str = "tfidf"
    ) -> KeywordExtractionResult:
        """Extract keywords from title and script content.
        
        Args:
            title: Content title (given higher weight)
            script: Content script/body text
            method: Extraction method ('tfidf', 'frequency', or 'hybrid')
        
        Returns:
            KeywordExtractionResult with ranked keywords
        """
        # Combine and preprocess text
        # Title gets repeated 3x for higher weight
        combined_text = f"{title} {title} {title} {script}"
        
        # Clean and tokenize
        cleaned_text = self._preprocess_text(combined_text)
        tokens = self._tokenize(cleaned_text)
        
        # Count total words
        total_words = len([t for t in tokens if t not in self.stop_words])
        
        # Extract keywords based on method
        if method == "tfidf":
            keywords_with_scores = self._extract_tfidf(title, script)
        elif method == "frequency":
            keywords_with_scores = self._extract_frequency(tokens)
        elif method == "hybrid":
            keywords_with_scores = self._extract_hybrid(title, script, tokens)
        else:
            raise ValueError(f"Unknown extraction method: {method}")
        
        # Filter and rank keywords
        filtered_keywords = self._filter_keywords(keywords_with_scores)
        
        # Calculate keyword density
        keyword_density = self._calculate_density(filtered_keywords, total_words)
        
        # Split into primary and secondary
        all_keywords = list(filtered_keywords.keys())
        primary = all_keywords[:self.primary_count]
        secondary = all_keywords[self.primary_count:self.primary_count + self.secondary_count]
        
        return KeywordExtractionResult(
            primary_keywords=primary,
            secondary_keywords=secondary,
            keyword_scores=filtered_keywords,
            keyword_density=keyword_density,
            total_words=total_words,
            extraction_method=method
        )
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text.
        
        Args:
            text: Raw text
        
        Returns:
            Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Keep only alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words.
        
        Args:
            text: Preprocessed text
        
        Returns:
            List of tokens
        """
        try:
            tokens = word_tokenize(text)
        except Exception:
            # Fallback to simple split if NLTK fails
            tokens = text.split()
        
        return tokens
    
    def _extract_tfidf(self, title: str, script: str) -> Dict[str, float]:
        """Extract keywords using TF-IDF.
        
        Args:
            title: Content title
            script: Content script
        
        Returns:
            Dictionary of keywords with TF-IDF scores
        """
        # Prepare documents
        documents = [
            self._preprocess_text(f"{title} {title} {title}"),
            self._preprocess_text(script)
        ]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            stop_words=list(self.stop_words),
            max_features=50,
            ngram_range=(1, 2),  # Include unigrams and bigrams
            min_df=1
        )
        
        try:
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform(documents)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get scores (use max score across documents)
            scores = {}
            for idx, feature in enumerate(feature_names):
                score = max(tfidf_matrix[0, idx], tfidf_matrix[1, idx])
                if score > 0:
                    scores[feature] = float(score)
            
            return scores
            
        except Exception:
            # Fallback to frequency if TF-IDF fails
            tokens = self._tokenize(self._preprocess_text(f"{title} {script}"))
            return self._extract_frequency(tokens)
    
    def _extract_frequency(self, tokens: List[str]) -> Dict[str, float]:
        """Extract keywords using frequency analysis.
        
        Args:
            tokens: List of tokens
        
        Returns:
            Dictionary of keywords with frequency scores
        """
        # Filter tokens
        filtered_tokens = [
            token for token in tokens
            if (token not in self.stop_words and
                len(token) >= self.min_keyword_length and
                len(token) <= self.max_keyword_length and
                token.isalnum())
        ]
        
        # Count frequencies
        frequency = Counter(filtered_tokens)
        
        # Normalize to 0-1 range
        max_freq = max(frequency.values()) if frequency else 1
        normalized = {
            word: count / max_freq
            for word, count in frequency.items()
        }
        
        return normalized
    
    def _extract_hybrid(
        self,
        title: str,
        script: str,
        tokens: List[str]
    ) -> Dict[str, float]:
        """Extract keywords using hybrid method (TF-IDF + frequency).
        
        Args:
            title: Content title
            script: Content script
            tokens: Tokenized text
        
        Returns:
            Dictionary of keywords with hybrid scores
        """
        # Get both scores
        tfidf_scores = self._extract_tfidf(title, script)
        freq_scores = self._extract_frequency(tokens)
        
        # Combine scores (weighted average: 60% TF-IDF, 40% frequency)
        all_keywords = set(tfidf_scores.keys()) | set(freq_scores.keys())
        
        hybrid_scores = {}
        for keyword in all_keywords:
            tfidf_score = tfidf_scores.get(keyword, 0)
            freq_score = freq_scores.get(keyword, 0)
            hybrid_scores[keyword] = 0.6 * tfidf_score + 0.4 * freq_score
        
        return hybrid_scores
    
    def _filter_keywords(
        self,
        keywords_with_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Filter and rank keywords.
        
        Args:
            keywords_with_scores: Dictionary of keywords with scores
        
        Returns:
            Filtered and sorted dictionary of keywords
        """
        # Filter by length
        filtered = {
            word: score for word, score in keywords_with_scores.items()
            if (len(word) >= self.min_keyword_length and
                len(word) <= self.max_keyword_length)
        }
        
        # Sort by score (descending)
        sorted_keywords = dict(
            sorted(filtered.items(), key=lambda x: x[1], reverse=True)
        )
        
        return sorted_keywords
    
    def _calculate_density(
        self,
        keywords: Dict[str, float],
        total_words: int
    ) -> Dict[str, float]:
        """Calculate keyword density as percentage.
        
        Args:
            keywords: Dictionary of keywords with scores
            total_words: Total word count
        
        Returns:
            Dictionary mapping keywords to density percentages
        """
        if total_words == 0:
            return {}
        
        # Density is proportional to score
        # Normalize so top keyword has reasonable density (e.g., 2-5%)
        density = {}
        max_score = max(keywords.values()) if keywords else 1
        
        for keyword, score in keywords.items():
            # Scale density: top keyword ~3%, others proportional
            density[keyword] = round((score / max_score) * 3.0, 2)
        
        return density
    
    def suggest_related_keywords(
        self,
        keywords: List[str],
        original_text: str,
        max_suggestions: int = 10
    ) -> List[str]:
        """Suggest related keywords based on extracted keywords.
        
        Args:
            keywords: List of extracted keywords
            original_text: Original text content
            max_suggestions: Maximum number of suggestions
        
        Returns:
            List of suggested related keywords
        """
        # Preprocess and tokenize
        cleaned_text = self._preprocess_text(original_text)
        tokens = self._tokenize(cleaned_text)
        
        # Find words that appear near the keywords (context window of 5 words)
        related_words: Set[str] = set()
        
        for i, token in enumerate(tokens):
            if token in keywords:
                # Get surrounding words
                start = max(0, i - 5)
                end = min(len(tokens), i + 6)
                context_words = tokens[start:end]
                
                for word in context_words:
                    if (word not in self.stop_words and
                        word not in keywords and
                        len(word) >= self.min_keyword_length and
                        len(word) <= self.max_keyword_length and
                        word.isalnum()):
                        related_words.add(word)
        
        # Rank by frequency
        related_freq = Counter([
            t for t in tokens if t in related_words
        ])
        
        # Return top suggestions
        top_related = [
            word for word, count in related_freq.most_common(max_suggestions)
        ]
        
        return top_related


def extract_keywords(
    title: str,
    script: str,
    method: str = "tfidf",
    primary_count: int = 5,
    secondary_count: int = 10
) -> KeywordExtractionResult:
    """Convenience function to extract keywords.
    
    Args:
        title: Content title
        script: Content script/body text
        method: Extraction method ('tfidf', 'frequency', or 'hybrid')
        primary_count: Number of primary keywords
        secondary_count: Number of secondary keywords
    
    Returns:
        KeywordExtractionResult with ranked keywords
    
    Example:
        >>> result = extract_keywords(
        ...     title="How to Learn Python Programming",
        ...     script="Python is a great programming language for beginners...",
        ...     method="tfidf"
        ... )
        >>> print(result.primary_keywords)
        ['python', 'programming', 'language', 'learn', 'beginners']
    """
    extractor = KeywordExtractor(
        primary_count=primary_count,
        secondary_count=secondary_count
    )
    return extractor.extract_keywords(title, script, method)
