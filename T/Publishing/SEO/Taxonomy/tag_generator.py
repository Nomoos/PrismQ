"""Tag Generator module for PrismQ.T.Publishing.SEO.Taxonomy.

This module provides intelligent tag generation from content and keywords
with relevance scoring, semantic analysis, and deduplication.
"""

import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import Counter
import difflib

from .taxonomy_config import TaxonomyConfig, DEFAULT_TAXONOMY


@dataclass
class TagGenerationResult:
    """Result of tag generation operation.
    
    Attributes:
        tags: List of generated tags
        relevance_scores: Dictionary mapping tags to relevance scores (0-1)
        source_breakdown: Dictionary showing tag sources (keywords, content, etc.)
        duplicates_removed: Number of duplicate tags removed
        generation_method: Method used for generation
    """
    
    tags: List[str] = field(default_factory=list)
    relevance_scores: Dict[str, float] = field(default_factory=dict)
    source_breakdown: Dict[str, int] = field(default_factory=dict)
    duplicates_removed: int = 0
    generation_method: str = "semantic"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TagGenerationResult("
            f"tags={len(self.tags)}, "
            f"duplicates_removed={self.duplicates_removed}, "
            f"method={self.generation_method})"
        )


class TagGenerator:
    """Generate tags from content with relevance scoring.
    
    This class implements tag generation using multiple strategies:
    - Keyword-based: Extract tags from provided SEO keywords
    - Content-based: Extract tags from title and script
    - Semantic: Expand tags using semantic relationships
    - Deduplication: Remove similar/duplicate tags
    """
    
    def __init__(self, config: Optional[TaxonomyConfig] = None):
        """Initialize the tag generator.
        
        Args:
            config: TaxonomyConfig instance (uses default if not provided)
        """
        self.config = config or DEFAULT_TAXONOMY
        
        # Common stopwords for tag filtering
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'again', 'further', 'then', 'once',
            'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 'can', 'will', 'just', 'should'
        }
    
    def generate_tags(
        self,
        title: str,
        script: str,
        base_keywords: Optional[List[str]] = None
    ) -> TagGenerationResult:
        """Generate tags from content and keywords.
        
        Args:
            title: Content title
            script: Content script/body text
            base_keywords: Optional list of SEO keywords from POST-001
        
        Returns:
            TagGenerationResult with tags and relevance scores
        """
        # Normalize keywords
        keywords = base_keywords or []
        
        # Initialize tracking
        all_tags: Dict[str, float] = {}
        source_breakdown = {"keywords": 0, "content": 0, "semantic": 0}
        
        # Step 1: Extract tags from keywords
        if keywords:
            keyword_tags = self._extract_from_keywords(keywords)
            for tag, score in keyword_tags.items():
                all_tags[tag] = max(all_tags.get(tag, 0), score)
                source_breakdown["keywords"] += 1
        
        # Step 2: Extract tags from content
        content_tags = self._extract_from_content(title, script)
        for tag, score in content_tags.items():
            # Boost score if tag also appears in keywords
            boost = 1.2 if tag in keywords else 1.0
            all_tags[tag] = max(all_tags.get(tag, 0), score * boost)
            if tag not in keywords:
                source_breakdown["content"] += 1
        
        # Step 3: Semantic expansion (related terms)
        semantic_tags = self._semantic_expansion(all_tags, title, script)
        for tag, score in semantic_tags.items():
            if tag not in all_tags:
                all_tags[tag] = score
                source_breakdown["semantic"] += 1
        
        # Step 4: Filter by minimum relevance
        filtered_tags = {
            tag: score for tag, score in all_tags.items()
            if score >= self.config.min_relevance
        }
        
        # Step 5: Deduplicate similar tags
        deduplicated_tags, duplicates_removed = self._deduplicate_tags(filtered_tags)
        
        # Step 6: Sort by relevance and limit to max_tags
        sorted_tags = sorted(
            deduplicated_tags.items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.config.max_tags]
        
        tags = [tag for tag, score in sorted_tags]
        relevance_scores = dict(sorted_tags)
        
        return TagGenerationResult(
            tags=tags,
            relevance_scores=relevance_scores,
            source_breakdown=source_breakdown,
            duplicates_removed=duplicates_removed,
            generation_method="semantic"
        )
    
    def _extract_from_keywords(self, keywords: List[str]) -> Dict[str, float]:
        """Extract tags from provided keywords.
        
        Args:
            keywords: List of SEO keywords
        
        Returns:
            Dictionary of tags with relevance scores
        """
        tags = {}
        
        for keyword in keywords:
            # Clean and normalize
            tag = self._normalize_tag(keyword)
            
            # Skip if invalid
            if not self._is_valid_tag(tag):
                continue
            
            # Assign high relevance (0.9) for keyword-based tags
            tags[tag] = 0.9
            
            # Also extract individual words from multi-word keywords
            words = tag.split()
            if len(words) > 1:
                for word in words:
                    if self._is_valid_tag(word) and word not in self.stop_words:
                        # Lower score for individual words
                        tags[word] = max(tags.get(word, 0), 0.75)
        
        return tags
    
    def _extract_from_content(self, title: str, script: str) -> Dict[str, float]:
        """Extract tags from content text.
        
        Args:
            title: Content title
            script: Content script/body text
        
        Returns:
            Dictionary of tags with relevance scores
        """
        # Combine text (weight title 3x)
        combined = f"{title} {title} {title} {script}"
        
        # Clean and tokenize
        cleaned = self._clean_text(combined)
        words = cleaned.split()
        
        # Count frequencies
        word_freq = Counter(words)
        
        # Filter and score
        tags = {}
        max_freq = max(word_freq.values()) if word_freq else 1
        
        for word, count in word_freq.items():
            # Normalize
            tag = self._normalize_tag(word)
            
            # Skip if invalid
            if not self._is_valid_tag(tag):
                continue
            
            # Calculate relevance based on frequency
            # More frequent = more relevant (up to 0.85)
            relevance = min(0.85, (count / max_freq) * 0.85)
            
            tags[tag] = relevance
        
        # Also extract bigrams (two-word phrases)
        bigrams = self._extract_bigrams(words)
        max_bigram_freq = max(bigrams.values()) if bigrams else 1
        
        for bigram, count in bigrams.items():
            if self._is_valid_tag(bigram):
                relevance = min(0.80, (count / max_bigram_freq) * 0.80)
                tags[bigram] = relevance
        
        return tags
    
    def _semantic_expansion(
        self,
        base_tags: Dict[str, float],
        title: str,
        script: str
    ) -> Dict[str, float]:
        """Expand tags using semantic relationships.
        
        Args:
            base_tags: Dictionary of base tags
            title: Content title
            script: Content script
        
        Returns:
            Dictionary of expanded tags with scores
        """
        # For now, implement simple expansion based on category matching
        # In a production system, this could use word embeddings or LLMs
        
        expanded = {}
        content_lower = f"{title} {script}".lower()
        
        # Check which categories appear in content
        for category, subcategories in self.config.categories.items():
            category_lower = category.lower()
            
            # If category or subcategory appears in content
            if category_lower in content_lower:
                # Add category as tag with moderate relevance
                if self._is_valid_tag(category):
                    expanded[category.lower()] = 0.72
            
            # Check subcategories
            for subcat in subcategories:
                subcat_lower = subcat.lower()
                if subcat_lower in content_lower:
                    if self._is_valid_tag(subcat):
                        expanded[subcat_lower] = 0.73
        
        return expanded
    
    def _extract_bigrams(self, words: List[str]) -> Counter:
        """Extract two-word phrases from text.
        
        Args:
            words: List of words
        
        Returns:
            Counter of bigrams and their frequencies
        """
        bigrams = []
        
        for i in range(len(words) - 1):
            word1 = words[i]
            word2 = words[i + 1]
            
            # Skip if either word is a stop word
            if word1 in self.stop_words or word2 in self.stop_words:
                continue
            
            # Create bigram
            bigram = f"{word1} {word2}"
            if len(bigram) <= 30:  # Reasonable length limit
                bigrams.append(bigram)
        
        return Counter(bigrams)
    
    def _deduplicate_tags(
        self,
        tags: Dict[str, float]
    ) -> Tuple[Dict[str, float], int]:
        """Remove similar/duplicate tags.
        
        Args:
            tags: Dictionary of tags with scores
        
        Returns:
            Tuple of (deduplicated tags, number of duplicates removed)
        """
        if not tags:
            return {}, 0
        
        # Sort by score (keep higher scored tags)
        sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
        
        deduplicated = {}
        removed_count = 0
        
        for tag, score in sorted_tags:
            # Check similarity with existing tags
            is_duplicate = False
            
            for existing_tag in deduplicated.keys():
                similarity = self._calculate_similarity(tag, existing_tag)
                
                if similarity >= self.config.tag_similarity_threshold:
                    is_duplicate = True
                    removed_count += 1
                    break
            
            if not is_duplicate:
                deduplicated[tag] = score
        
        return deduplicated, removed_count
    
    def _calculate_similarity(self, tag1: str, tag2: str) -> float:
        """Calculate similarity between two tags.
        
        Args:
            tag1: First tag
            tag2: Second tag
        
        Returns:
            Similarity score (0-1)
        """
        # Use SequenceMatcher for string similarity
        return difflib.SequenceMatcher(None, tag1.lower(), tag2.lower()).ratio()
    
    def _normalize_tag(self, text: str) -> str:
        """Normalize tag text.
        
        Args:
            text: Raw tag text
        
        Returns:
            Normalized tag
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters (keep alphanumeric, spaces, hyphens)
        text = re.sub(r'[^a-z0-9\s\-]', '', text)
        
        return text.strip()
    
    def _clean_text(self, text: str) -> str:
        """Clean text for processing.
        
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
    
    def _is_valid_tag(self, tag: str) -> bool:
        """Check if a tag is valid.
        
        Args:
            tag: Tag to validate
        
        Returns:
            True if tag is valid
        """
        if not tag or not tag.strip():
            return False
        
        # Check length (min 2 chars, max 30 chars)
        if len(tag) < 2 or len(tag) > 30:
            return False
        
        # Check if it's a stop word
        if tag in self.stop_words:
            return False
        
        # Must contain at least one letter
        if not any(c.isalpha() for c in tag):
            return False
        
        return True


def generate_tags(
    title: str,
    script: str,
    keywords: Optional[List[str]] = None,
    config: Optional[TaxonomyConfig] = None
) -> TagGenerationResult:
    """Convenience function to generate tags.
    
    Args:
        title: Content title
        script: Content script/body text
        keywords: Optional list of SEO keywords
        config: Optional TaxonomyConfig
    
    Returns:
        TagGenerationResult with tags and scores
    
    Example:
        >>> result = generate_tags(
        ...     title="Introduction to Machine Learning",
        ...     script="Machine learning is a subset of AI...",
        ...     keywords=["machine learning", "AI", "python"]
        ... )
        >>> print(result.tags)
        ['machine learning', 'ai', 'python', 'data', 'algorithms']
    """
    generator = TagGenerator(config=config)
    return generator.generate_tags(title, script, keywords)


__all__ = [
    'TagGenerator',
    'TagGenerationResult',
    'generate_tags',
]
