"""PrismQ.T.Publishing.SEO.Taxonomy - Automatic Tag & Category Assignment.

This module provides automated tag generation and category assignment for content
classification. It includes:

- Tag generation from content analysis with relevance scoring
- Category classification with confidence scores
- Support for custom taxonomy definitions
- Hierarchical category structures
- Tag deduplication and validation

Main Classes:
    - TagGenerator: Generate tags from content with relevance scores
    - CategoryClassifier: Assign categories with confidence scores
    - TaxonomyConfig: Configuration for taxonomy rules and categories
    - TaxonomyResult: Complete result with tags and categories

Convenience Functions:
    - generate_tags(): Quick tag generation
    - classify_categories(): Quick category classification
    - process_taxonomy(): Complete end-to-end taxonomy processing

Example:
    >>> from T.Publishing.SEO.Taxonomy import process_taxonomy
    >>> 
    >>> result = process_taxonomy(
    ...     title="Machine Learning Basics for Beginners",
    ...     script="Machine learning is a subset of AI...",
    ...     keywords=["machine learning", "AI", "python"]
    ... )
    >>> 
    >>> print(f"Tags: {', '.join(result['tags'])}")
    >>> print(f"Categories: {result['categories']}")
"""

from .tag_generator import (
    TagGenerator,
    TagGenerationResult,
    generate_tags
)

from .category_classifier import (
    CategoryClassifier,
    CategoryClassificationResult,
    classify_categories
)

from .taxonomy_config import (
    TaxonomyConfig,
    load_taxonomy_config,
    create_custom_taxonomy,
    DEFAULT_TAXONOMY,
    TECH_FOCUSED_TAXONOMY,
    LIFESTYLE_FOCUSED_TAXONOMY
)

from typing import Dict, List, Optional, Any


def process_taxonomy(
    title: str,
    script: str,
    keywords: Optional[List[str]] = None,
    config: Optional[TaxonomyConfig] = None,
    include_scores: bool = True
) -> Dict[str, Any]:
    """Process content for complete taxonomy assignment.
    
    This is the main entry point for tag generation and category classification.
    It performs end-to-end processing:
    
    1. Generate tags from content and keywords
    2. Calculate relevance scores for each tag
    3. Classify content into categories
    4. Calculate confidence scores for categories
    5. Apply taxonomy rules (min relevance, max tags, etc.)
    
    Args:
        title: Content title
        script: Content script/body text
        keywords: Optional list of SEO keywords from POST-001
        config: Optional TaxonomyConfig (uses default if not provided)
        include_scores: Whether to include relevance/confidence scores
    
    Returns:
        Dictionary containing:
            - tags: List of generated tags
            - tag_scores: Dictionary mapping tags to relevance scores (if include_scores=True)
            - categories: List of assigned categories (paths)
            - category_scores: Dictionary mapping categories to confidence scores (if include_scores=True)
            - hierarchy: Hierarchical representation of categories
            - stats: Statistics about tag/category generation
    
    Example:
        >>> result = process_taxonomy(
        ...     title="Introduction to Python Programming",
        ...     script="Python is a versatile language used for web dev, AI, and more...",
        ...     keywords=["python", "programming", "beginners"]
        ... )
        >>> 
        >>> print(f"Tags: {', '.join(result['tags'][:5])}")
        >>> print(f"Categories: {', '.join(result['categories'])}")
        >>> print(f"Quality Score: {result['stats']['quality_score']}/100")
    """
    # Use default config if not provided
    if config is None:
        config = DEFAULT_TAXONOMY
    
    # Step 1: Generate tags
    tag_gen = TagGenerator(config=config)
    tag_result = tag_gen.generate_tags(
        title=title,
        script=script,
        base_keywords=keywords or []
    )
    
    # Step 2: Classify categories
    cat_classifier = CategoryClassifier(config=config)
    category_result = cat_classifier.classify_categories(
        title=title,
        script=script,
        tags=tag_result.tags
    )
    
    # Step 3: Build result dictionary
    result = {
        'tags': tag_result.tags,
        'categories': category_result.categories,
        'hierarchy': category_result.hierarchy,
        'stats': {
            'total_tags': len(tag_result.tags),
            'total_categories': len(category_result.categories),
            'avg_tag_relevance': sum(tag_result.relevance_scores.values()) / len(tag_result.relevance_scores) if tag_result.relevance_scores else 0,
            'avg_category_confidence': sum(category_result.confidence_scores.values()) / len(category_result.confidence_scores) if category_result.confidence_scores else 0,
            'quality_score': _calculate_quality_score(tag_result, category_result)
        }
    }
    
    # Include scores if requested
    if include_scores:
        result['tag_scores'] = tag_result.relevance_scores
        result['category_scores'] = category_result.confidence_scores
    
    return result


def _calculate_quality_score(
    tag_result: TagGenerationResult,
    category_result: CategoryClassificationResult
) -> int:
    """Calculate overall taxonomy quality score (0-100).
    
    Args:
        tag_result: Tag generation result
        category_result: Category classification result
    
    Returns:
        Quality score between 0 and 100
    """
    score = 0
    
    # Tag quality (40 points)
    if tag_result.tags:
        # Number of tags (0-10 points): 5-10 tags is optimal
        tag_count = len(tag_result.tags)
        if 5 <= tag_count <= 10:
            score += 10
        elif 3 <= tag_count < 5 or 10 < tag_count <= 15:
            score += 7
        else:
            score += 4
        
        # Average relevance (0-30 points): >0.7 is good
        avg_relevance = sum(tag_result.relevance_scores.values()) / len(tag_result.relevance_scores)
        score += int(avg_relevance * 30)
    
    # Category quality (40 points)
    if category_result.categories:
        # Number of categories (0-10 points): 1-3 categories is optimal
        cat_count = len(category_result.categories)
        if 1 <= cat_count <= 3:
            score += 10
        elif cat_count == 4:
            score += 7
        else:
            score += 4
        
        # Average confidence (0-30 points): >0.8 is good
        avg_confidence = sum(category_result.confidence_scores.values()) / len(category_result.confidence_scores)
        score += int(avg_confidence * 30)
    
    # Bonus (20 points)
    # Both tags and categories present
    if tag_result.tags and category_result.categories:
        score += 10
    
    # Hierarchical categories present
    if category_result.hierarchy:
        score += 10
    
    return min(score, 100)


# Export main classes and functions
__all__ = [
    # Classes
    'TagGenerator',
    'TagGenerationResult',
    'CategoryClassifier',
    'CategoryClassificationResult',
    'TaxonomyConfig',
    
    # Functions
    'generate_tags',
    'classify_categories',
    'process_taxonomy',
    'load_taxonomy_config',
    'create_custom_taxonomy',
    
    # Constants
    'DEFAULT_TAXONOMY',
    'TECH_FOCUSED_TAXONOMY',
    'LIFESTYLE_FOCUSED_TAXONOMY',
]
