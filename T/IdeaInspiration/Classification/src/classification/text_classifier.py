"""Classification enrichment for IdeaInspiration content.

This module enriches IdeaInspiration objects with classification metadata including
category, flags/tags, and confidence scores. It works with external IdeaInspiration
models and focuses on scoring and classification logic.

The TextClassifier integrates with existing CategoryClassifier and StoryDetector
to provide comprehensive classification enrichment.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from .idea_inspiration import IdeaInspirationLike, get_text_fields, get_keywords
from .category_classifier import CategoryClassifier
from .story_detector import StoryDetector
from .categories import CategoryResult, PrimaryCategory


@dataclass
class ClassificationEnrichment:
    """Classification enrichment data for IdeaInspiration.
    
    This data structure enriches an IdeaInspiration object with classification
    metadata. It contains the top category and classification flags/tags.
    
    Attributes:
        category: Primary category classification
        category_confidence: Confidence score for category (0.0 to 1.0)
        flags: Binary classification flags (e.g., is_story, is_usable)
        tags: Classification tags derived from indicators
        field_scores: Scores for individual text fields
        combined_score: Overall classification confidence
    """
    category: PrimaryCategory
    category_confidence: float
    flags: Dict[str, bool] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    field_scores: Dict[str, float] = field(default_factory=dict)
    combined_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization.
        
        Returns:
            Dictionary representation of classification enrichment
        """
        return {
            'category': self.category.value,
            'category_confidence': self.category_confidence,
            'flags': self.flags,
            'tags': self.tags,
            'field_scores': self.field_scores,
            'combined_score': self.combined_score
        }


class TextClassifier:
    """Classification enrichment for IdeaInspiration content.
    
    This classifier enriches IdeaInspiration objects with classification metadata
    including top category, flags, and tags. It works with external IdeaInspiration
    models that are passed in for scoring.
    
    Features:
        - Determines top category with confidence
        - Sets classification flags (is_story, is_usable, etc.)
        - Generates classification tags from indicators
        - Scores multiple text fields
        - Returns enrichment data to attach to IdeaInspiration
    """
    
    def __init__(
        self,
        category_classifier: Optional[CategoryClassifier] = None,
        story_detector: Optional[StoryDetector] = None
    ):
        """Initialize the classification enrichment classifier.
        
        Args:
            category_classifier: Optional custom CategoryClassifier instance
            story_detector: Optional custom StoryDetector instance
        """
        self.category_classifier = category_classifier or CategoryClassifier()
        self.story_detector = story_detector or StoryDetector()
    
    def enrich(self, inspiration: IdeaInspirationLike) -> ClassificationEnrichment:
        """Enrich an IdeaInspiration object with classification metadata.
        
        This method scores the content and returns classification enrichment
        data including top category, flags, and tags.
        
        Args:
            inspiration: IdeaInspiration object or dict to classify
            
        Returns:
            ClassificationEnrichment with category, flags, tags, and scores
        """
        # Extract text fields
        text_fields = get_text_fields(inspiration)
        keywords = get_keywords(inspiration)
        
        # Perform category classification
        category_result = self.category_classifier.classify(
            title=text_fields['title'],
            description=text_fields['description'],
            tags=keywords,
            subtitle_text=text_fields['content']
        )
        
        # Perform story detection
        is_story, story_confidence, story_indicators = self.story_detector.detect(
            title=text_fields['title'],
            description=text_fields['description'],
            tags=keywords,
            subtitle_text=text_fields['content']
        )
        
        # Calculate field scores
        field_scores = self._calculate_field_scores(text_fields)
        
        # Calculate combined score
        combined_score = self._calculate_combined_score(
            category_result.confidence,
            story_confidence,
            field_scores
        )
        
        # Build flags
        flags = {
            'is_story': is_story,
            'is_usable': category_result.category.is_usable_for_stories,
            'has_high_confidence': combined_score > 0.7
        }
        
        # Build tags from indicators
        tags = self._build_tags(category_result.indicators, story_indicators)
        
        return ClassificationEnrichment(
            category=category_result.category,
            category_confidence=category_result.confidence,
            flags=flags,
            tags=tags,
            field_scores=field_scores,
            combined_score=combined_score
        )
    
    # Backward compatibility alias
    def classify(self, inspiration: IdeaInspirationLike) -> ClassificationEnrichment:
        """Classify an IdeaInspiration object (alias for enrich).
        
        Args:
            inspiration: IdeaInspiration object or dict to classify
            
        Returns:
            ClassificationEnrichment with classification metadata
        """
        return self.enrich(inspiration)
    
    def enrich_batch(
        self,
        inspirations: List[IdeaInspirationLike]
    ) -> List[ClassificationEnrichment]:
        """Enrich multiple IdeaInspiration objects.
        
        Args:
            inspirations: List of IdeaInspiration objects or dicts
            
        Returns:
            List of ClassificationEnrichment objects
        """
        return [self.enrich(inspiration) for inspiration in inspirations]
    
    def classify_batch(
        self,
        inspirations: List[IdeaInspirationLike]
    ) -> List[ClassificationEnrichment]:
        """Classify multiple IdeaInspiration objects (alias for enrich_batch).
        
        Args:
            inspirations: List of IdeaInspiration objects or dicts
            
        Returns:
            List of ClassificationEnrichment objects
        """
        return self.enrich_batch(inspirations)
    
    def classify_text_fields(
        self,
        title: str = "",
        description: str = "",
        content: str = "",
        keywords: Optional[List[str]] = None
    ) -> ClassificationEnrichment:
        """Classify individual text fields without an IdeaInspiration object.
        
        Args:
            title: Title text
            description: Description text
            content: Content text
            keywords: List of keywords
            
        Returns:
            ClassificationEnrichment
        """
        keywords = keywords or []
        
        # Create temporary dict for classification
        inspiration_dict = {
            'title': title,
            'description': description,
            'content': content,
            'keywords': keywords
        }
        
        return self.enrich(inspiration_dict)
    
    def _calculate_field_scores(
        self,
        text_fields: Dict[str, str]
    ) -> Dict[str, float]:
        """Calculate scores for individual text fields.
        
        Args:
            text_fields: Dictionary with text field values
            
        Returns:
            Dictionary mapping field names to scores (0.0 to 1.0)
        """
        scores = {}
        
        # Score title (higher weight)
        title = text_fields.get('title', '')
        if title:
            scores['title'] = self._score_text_field(title, weight=1.5)
        else:
            scores['title'] = 0.0
        
        # Score description
        description = text_fields.get('description', '')
        if description:
            scores['description'] = self._score_text_field(
                description,
                weight=1.0
            )
        else:
            scores['description'] = 0.0
        
        # Score content
        content = text_fields.get('content', '')
        if content:
            scores['content'] = self._score_text_field(
                content,
                weight=0.8
            )
        else:
            scores['content'] = 0.0
        
        # Score keywords
        keywords_str = text_fields.get('keywords_str', '')
        if keywords_str:
            keyword_count = len(keywords_str.split())
            scores['keywords'] = min(keyword_count / 10.0, 1.0)
        else:
            scores['keywords'] = 0.0
        
        return scores
    
    def _score_text_field(self, text: str, weight: float = 1.0) -> float:
        """Score a single text field based on quality indicators.
        
        Args:
            text: Text to score
            weight: Weight multiplier
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not text:
            return 0.0
        
        score = 0.0
        
        # Length score (normalized)
        length = len(text)
        if length > 10:
            score += 0.3
        if length > 50:
            score += 0.2
        if length > 100:
            score += 0.2
        
        # Word count
        word_count = len(text.split())
        if word_count > 5:
            score += 0.15
        if word_count > 10:
            score += 0.15
        
        # Apply weight and cap at 1.0
        return min(score * weight, 1.0)
    
    def _calculate_combined_score(
        self,
        category_confidence: float,
        story_confidence: float,
        field_scores: Dict[str, float]
    ) -> float:
        """Calculate overall combined classification score.
        
        Args:
            category_confidence: Category classification confidence
            story_confidence: Story detection confidence
            field_scores: Individual field scores
            
        Returns:
            Combined score between 0.0 and 1.0
        """
        # Weight different components
        category_weight = 0.4
        story_weight = 0.3
        field_weight = 0.3
        
        # Calculate average field score
        avg_field_score = (
            sum(field_scores.values()) / len(field_scores)
            if field_scores else 0.0
        )
        
        # Combine scores
        combined = (
            category_confidence * category_weight +
            story_confidence * story_weight +
            avg_field_score * field_weight
        )
        
        return min(combined, 1.0)
    
    def _build_tags(
        self,
        category_indicators: List[str],
        story_indicators: List[str]
    ) -> List[str]:
        """Build classification tags from indicators.
        
        Tags are derived from matched classification indicators and can be used
        to enrich the IdeaInspiration model with classification metadata.
        
        Args:
            category_indicators: Indicators from category classification
            story_indicators: Indicators from story detection
            
        Returns:
            List of unique tags
        """
        tags = set()
        
        # Extract keywords from category indicators
        for indicator in category_indicators:
            # Format: "title: keyword" or "description: keyword"
            if ':' in indicator:
                parts = indicator.split(':', 1)
                if len(parts) == 2:
                    tag = parts[1].strip()
                    tags.add(tag)
        
        # Extract keywords from story indicators  
        for indicator in story_indicators:
            if ':' in indicator:
                parts = indicator.split(':', 1)
                if len(parts) == 2:
                    tag = parts[1].strip()
                    tags.add(tag)
        
        return sorted(list(tags))
