"""PrismQ.T.Publishing.SEO.Keywords - Keyword Research & SEO Optimization.

This module provides automated SEO keyword extraction and metadata generation
for published content. It includes:

- Keyword extraction using NLP techniques (TF-IDF, frequency analysis)
- SEO metadata generation (meta descriptions, title tags)
- Keyword density analysis
- Related keyword suggestions

Main Classes:
    - KeywordExtractor: Extract keywords from content
    - MetadataGenerator: Generate SEO-optimized metadata
    - KeywordExtractionResult: Result of keyword extraction
    - SEOMetadata: Complete SEO metadata package

Convenience Functions:
    - extract_keywords(): Quick keyword extraction
    - generate_seo_metadata(): Quick metadata generation
    - process_content_seo(): Complete end-to-end SEO processing

Example:
    >>> from T.Publishing.SEO.Keywords import process_content_seo
    >>> 
    >>> result = process_content_seo(
    ...     title="How to Learn Python Programming",
    ...     script="Python is a versatile programming language..."
    ... )
    >>> 
    >>> print(f"Primary Keywords: {result['primary_keywords']}")
    >>> print(f"Meta Description: {result['meta_description']}")
    >>> print(f"Title Tag: {result['title_tag']}")
"""

from .keyword_extractor import (
    KeywordExtractor,
    KeywordExtractionResult,
    extract_keywords
)

from .metadata_generator import (
    MetadataGenerator,
    SEOMetadata,
    generate_seo_metadata
)

from typing import Dict, Optional, Any


def process_content_seo(
    title: str,
    script: str,
    extraction_method: str = "tfidf",
    primary_count: int = 5,
    secondary_count: int = 10,
    brand_name: Optional[str] = None,
    include_related: bool = True
) -> Dict[str, Any]:
    """Process content for complete SEO optimization.
    
    This is the main entry point for SEO keyword extraction and metadata
    generation. It performs end-to-end processing:
    
    1. Extract keywords from title and script
    2. Calculate keyword density
    3. Generate related keyword suggestions
    4. Create SEO metadata (meta description, title tag, etc.)
    5. Calculate quality score and recommendations
    
    Args:
        title: Content title
        script: Content script/body text
        extraction_method: Keyword extraction method ('tfidf', 'frequency', 'hybrid')
        primary_count: Number of primary keywords to extract
        secondary_count: Number of secondary keywords to extract
        brand_name: Optional brand name for title tags
        include_related: Whether to generate related keyword suggestions
    
    Returns:
        Dictionary containing:
            - primary_keywords: List of primary keywords
            - secondary_keywords: List of secondary keywords
            - meta_description: SEO meta description (150-160 chars)
            - title_tag: Optimized title tag (<60 chars)
            - keyword_density: Keyword density analysis
            - keyword_scores: Relevance scores for all keywords
            - related_keywords: Related keyword suggestions
            - og_title: Open Graph title
            - og_description: Open Graph description
            - quality_score: SEO quality score (0-100)
            - recommendations: List of SEO recommendations
            - extraction_method: Method used for extraction
    
    Example:
        >>> result = process_content_seo(
        ...     title="The Ultimate Guide to Python Programming",
        ...     script="Python is a powerful programming language that's perfect for beginners...",
        ...     brand_name="CodeAcademy"
        ... )
        >>> 
        >>> print(f"Keywords: {', '.join(result['primary_keywords'])}")
        >>> print(f"Description: {result['meta_description']}")
        >>> print(f"SEO Score: {result['quality_score']}/100")
    """
    # Step 1: Extract keywords
    extractor = KeywordExtractor(
        primary_count=primary_count,
        secondary_count=secondary_count
    )
    
    extraction_result = extractor.extract_keywords(
        title=title,
        script=script,
        method=extraction_method
    )
    
    # Step 2: Generate related keyword suggestions (if requested)
    related_keywords = []
    if include_related:
        related_keywords = extractor.suggest_related_keywords(
            keywords=extraction_result.primary_keywords,
            original_text=f"{title} {script}",
            max_suggestions=10
        )
    
    # Step 3: Generate SEO metadata
    generator = MetadataGenerator(brand_name=brand_name)
    
    metadata = generator.generate_metadata(
        title=title,
        script=script,
        primary_keywords=extraction_result.primary_keywords,
        secondary_keywords=extraction_result.secondary_keywords,
        keyword_density=extraction_result.keyword_density,
        related_keywords=related_keywords
    )
    
    # Step 4: Compile complete result
    result = {
        # Keywords
        'primary_keywords': metadata.primary_keywords,
        'secondary_keywords': metadata.secondary_keywords,
        'keyword_scores': extraction_result.keyword_scores,
        'keyword_density': metadata.keyword_density,
        'related_keywords': metadata.related_keywords,
        
        # SEO Metadata
        'meta_description': metadata.meta_description,
        'title_tag': metadata.title_tag,
        'og_title': metadata.og_title,
        'og_description': metadata.og_description,
        
        # Quality Metrics
        'quality_score': metadata.quality_score,
        'recommendations': metadata.recommendations,
        
        # Processing Info
        'extraction_method': extraction_result.extraction_method,
        'total_words': extraction_result.total_words,
        'generation_timestamp': metadata.generation_timestamp
    }
    
    return result


# Export main classes and functions
__all__ = [
    # Classes
    'KeywordExtractor',
    'KeywordExtractionResult',
    'MetadataGenerator',
    'SEOMetadata',
    
    # Functions
    'extract_keywords',
    'generate_seo_metadata',
    'process_content_seo',
]
