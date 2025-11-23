"""Category Classifier module for PrismQ.T.Publishing.SEO.Taxonomy.

This module provides category classification for content using
keyword matching, semantic analysis, and confidence scoring.
"""

import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import Counter

from .taxonomy_config import TaxonomyConfig, DEFAULT_TAXONOMY


@dataclass
class CategoryClassificationResult:
    """Result of category classification operation.
    
    Attributes:
        categories: List of assigned category paths
        confidence_scores: Dictionary mapping categories to confidence scores (0-1)
        hierarchy: Hierarchical representation of categories
        classification_method: Method used for classification
    """
    
    categories: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    hierarchy: Dict[str, List[str]] = field(default_factory=dict)
    classification_method: str = "keyword_matching"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CategoryClassificationResult("
            f"categories={len(self.categories)}, "
            f"method={self.classification_method})"
        )


class CategoryClassifier:
    """Classify content into categories with confidence scoring.
    
    This class implements category classification using multiple strategies:
    - Keyword matching: Match content against category keywords
    - Tag-based: Use generated tags to infer categories
    - Semantic: Analyze content semantically for category relevance
    - Hierarchical: Support parent/child category relationships
    """
    
    def __init__(self, config: Optional[TaxonomyConfig] = None):
        """Initialize the category classifier.
        
        Args:
            config: TaxonomyConfig instance (uses default if not provided)
        """
        self.config = config or DEFAULT_TAXONOMY
    
    def classify_categories(
        self,
        title: str,
        script: str,
        tags: Optional[List[str]] = None
    ) -> CategoryClassificationResult:
        """Classify content into categories.
        
        Args:
            title: Content title
            script: Content script/body text
            tags: Optional list of generated tags
        
        Returns:
            CategoryClassificationResult with categories and confidence scores
        """
        # Combine all text for analysis (weight title 3x)
        content = f"{title} {title} {title} {script}"
        content_lower = content.lower()
        tags_lower = [tag.lower() for tag in (tags or [])]
        
        # Calculate category scores
        category_scores: Dict[str, float] = {}
        
        for parent_category, subcategories in self.config.categories.items():
            parent_lower = parent_category.lower()
            
            # Calculate parent category score
            parent_score = self._calculate_category_score(
                parent_lower,
                content_lower,
                tags_lower
            )
            
            # Check subcategories
            subcategory_scores = {}
            for subcat in subcategories:
                subcat_lower = subcat.lower()
                subcat_score = self._calculate_category_score(
                    subcat_lower,
                    content_lower,
                    tags_lower
                )
                
                if subcat_score > 0:
                    subcategory_scores[subcat] = subcat_score
            
            # If any subcategory matches, boost parent score
            if subcategory_scores:
                max_subcat_score = max(subcategory_scores.values())
                parent_score = max(parent_score, max_subcat_score * 0.9)
                
                # Store parent category with score
                if parent_score >= self.config.min_category_score:
                    category_scores[parent_category] = parent_score
                
                # Store top subcategories with full paths
                for subcat, score in subcategory_scores.items():
                    if score >= self.config.min_subcategory_score:
                        category_path = f"{parent_category}/{subcat}"
                        category_scores[category_path] = score
            else:
                # Only parent category (no matching subcategories)
                if parent_score >= self.config.min_category_score:
                    category_scores[parent_category] = parent_score
        
        # Sort by confidence and limit to max_categories
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.config.max_categories]
        
        categories = [cat for cat, score in sorted_categories]
        confidence_scores = dict(sorted_categories)
        
        # Build hierarchy
        hierarchy = self._build_hierarchy(categories)
        
        return CategoryClassificationResult(
            categories=categories,
            confidence_scores=confidence_scores,
            hierarchy=hierarchy,
            classification_method="keyword_matching"
        )
    
    def _calculate_category_score(
        self,
        category: str,
        content: str,
        tags: List[str]
    ) -> float:
        """Calculate relevance score for a category.
        
        Args:
            category: Category name (lowercase)
            content: Content text (lowercase)
            tags: List of tags (lowercase)
        
        Returns:
            Relevance score (0-1)
        """
        score = 0.0
        
        # 1. Direct category name match in content (40% weight)
        # Split category into words for matching
        category_words = category.split()
        content_words = content.split()
        
        # Count occurrences of category words
        matches = 0
        for cat_word in category_words:
            if cat_word in content_words:
                matches += content_words.count(cat_word)
        
        if matches > 0:
            # More matches = higher score (up to 0.40)
            score += min(0.40, matches * 0.10)
        
        # 2. Category appears in tags (35% weight)
        for tag in tags:
            # Check if category is in tag or tag is in category
            if category in tag or tag in category:
                score += 0.35
                break
            
            # Also check word-level overlap
            tag_words = tag.split()
            overlap = len(set(category_words) & set(tag_words))
            if overlap > 0:
                score += min(0.25, overlap * 0.10)
                break
        
        # 3. Semantic keywords matching (25% weight)
        # Define keyword mappings for common categories
        category_keywords = self._get_category_keywords(category)
        
        keyword_matches = 0
        for keyword in category_keywords:
            if keyword in content:
                keyword_matches += 1
        
        if keyword_matches > 0:
            score += min(0.25, keyword_matches * 0.05)
        
        # Normalize to 0-1 range
        return min(1.0, score)
    
    def _get_category_keywords(self, category: str) -> List[str]:
        """Get semantic keywords for a category.
        
        Args:
            category: Category name
        
        Returns:
            List of relevant keywords
        """
        # Define keyword mappings for major categories
        keyword_map = {
            "technology": ["software", "hardware", "tech", "digital", "computer", "internet", "app", "system"],
            "ai": ["artificial intelligence", "machine learning", "neural", "deep learning", "algorithm", "model"],
            "web development": ["website", "web app", "frontend", "backend", "html", "css", "javascript", "react", "framework"],
            "mobile": ["app", "android", "ios", "smartphone", "mobile app", "application"],
            "cloud": ["aws", "azure", "gcp", "cloud computing", "saas", "paas", "serverless"],
            "programming": ["code", "coding", "developer", "software", "language", "python", "java", "programming"],
            "data science": ["data", "analytics", "analysis", "dataset", "statistics", "visualization"],
            "business": ["company", "enterprise", "corporate", "market", "business", "industry"],
            "marketing": ["advertisement", "promotion", "brand", "campaign", "seo", "social media", "content"],
            "finance": ["money", "investment", "financial", "banking", "stock", "trading", "revenue"],
            "entrepreneurship": ["startup", "founder", "business", "entrepreneur", "venture", "innovation"],
            "health": ["medical", "wellness", "healthcare", "fitness", "nutrition", "healthy"],
            "lifestyle": ["living", "life", "personal", "daily", "routine", "habit"],
            "education": ["learning", "teaching", "student", "course", "training", "tutorial", "lesson"],
            "science": ["research", "scientific", "study", "experiment", "discovery", "theory"],
            "creative": ["design", "art", "creative", "visual", "artistic", "graphic"],
            "entertainment": ["fun", "enjoy", "entertainment", "media", "content", "show"],
            "sports": ["sport", "game", "player", "team", "athletic", "competition"],
            "news": ["news", "report", "update", "event", "breaking", "announcement"],
        }
        
        return keyword_map.get(category, [])
    
    def _build_hierarchy(self, categories: List[str]) -> Dict[str, List[str]]:
        """Build hierarchical representation of categories.
        
        Args:
            categories: List of category paths
        
        Returns:
            Dictionary representing hierarchy
        """
        hierarchy = {}
        
        for category in categories:
            if "/" in category:
                # Split parent/child
                parts = category.split("/")
                parent = parts[0]
                child = parts[1] if len(parts) > 1 else None
                
                if parent not in hierarchy:
                    hierarchy[parent] = []
                
                if child and child not in hierarchy[parent]:
                    hierarchy[parent].append(child)
            else:
                # Top-level category
                if category not in hierarchy:
                    hierarchy[category] = []
        
        return hierarchy
    
    def get_category_suggestions(
        self,
        title: str,
        script: str,
        min_confidence: float = 0.5
    ) -> List[Tuple[str, float]]:
        """Get category suggestions with confidence scores.
        
        Args:
            title: Content title
            script: Content script
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of (category, confidence) tuples
        """
        result = self.classify_categories(title, script)
        
        suggestions = [
            (cat, score)
            for cat, score in result.confidence_scores.items()
            if score >= min_confidence
        ]
        
        return sorted(suggestions, key=lambda x: x[1], reverse=True)


def classify_categories(
    title: str,
    script: str,
    tags: Optional[List[str]] = None,
    config: Optional[TaxonomyConfig] = None
) -> CategoryClassificationResult:
    """Convenience function to classify categories.
    
    Args:
        title: Content title
        script: Content script/body text
        tags: Optional list of tags
        config: Optional TaxonomyConfig
    
    Returns:
        CategoryClassificationResult with categories and scores
    
    Example:
        >>> result = classify_categories(
        ...     title="Building Web Apps with React",
        ...     script="React is a popular JavaScript library for building user interfaces...",
        ...     tags=["react", "javascript", "web development"]
        ... )
        >>> print(result.categories)
        ['Technology/Web Development', 'Technology']
    """
    classifier = CategoryClassifier(config=config)
    return classifier.classify_categories(title, script, tags)


__all__ = [
    'CategoryClassifier',
    'CategoryClassificationResult',
    'classify_categories',
]
