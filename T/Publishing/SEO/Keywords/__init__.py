"""PrismQ.T.Publishing.SEO.Keywords - Keyword Research & SEO Optimization.

This module provides automated SEO keyword extraction and metadata generation
for published content. It includes:

- Keyword extraction using NLP techniques (TF-IDF, frequency analysis)
- SEO metadata generation (meta descriptions, title tags)
- AI-powered metadata generation using GPT/LLM (POST-001)
- Keyword density analysis
- Related keyword suggestions

Main Classes:
    - KeywordExtractor: Extract keywords from content
    - MetadataGenerator: Generate SEO-optimized metadata (rule-based)
    - AIMetadataGenerator: Generate AI-powered SEO metadata (GPT-based)
    - KeywordExtractionResult: Result of keyword extraction
    - SEOMetadata: Complete SEO metadata package
    - AIConfig: Configuration for AI-powered generation

Convenience Functions:
    - extract_keywords(): Quick keyword extraction
    - generate_seo_metadata(): Quick metadata generation (rule-based)
    - generate_ai_seo_metadata(): AI-powered metadata generation
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
    
    >>> # Using AI-powered generation
    >>> from T.Publishing.SEO.Keywords import process_content_seo
    >>> 
    >>> result = process_content_seo(
    ...     title="How to Learn Python Programming",
    ...     script="Python is a versatile programming language...",
    ...     use_ai=True,  # Enable AI-powered metadata generation
    ...     brand_name="TechEdu"
    ... )
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

from .ai_metadata_generator import (
    AIMetadataGenerator,
    AIConfig,
    generate_ai_seo_metadata
)

from typing import Dict, Optional, Any


def process_content_seo(
    title: str,
    script: str,
    extraction_method: str = "tfidf",
    primary_count: int = 5,
    secondary_count: int = 10,
    brand_name: Optional[str] = None,
    include_related: bool = True,
    use_ai: bool = False,
    ai_config: Optional[AIConfig] = None
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
        use_ai: Whether to use AI-powered metadata generation (POST-001)
        ai_config: Optional AI configuration for GPT-based generation
    
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
            - ai_generated: Whether AI was used for metadata generation
    
    Example:
        >>> # Rule-based generation
        >>> result = process_content_seo(
        ...     title="The Ultimate Guide to Python Programming",
        ...     script="Python is a powerful programming language that's perfect for beginners...",
        ...     brand_name="CodeAcademy"
        ... )
        >>> 
        >>> print(f"Keywords: {', '.join(result['primary_keywords'])}")
        >>> print(f"Description: {result['meta_description']}")
        >>> print(f"SEO Score: {result['quality_score']}/100")
        
        >>> # AI-powered generation (POST-001)
        >>> result = process_content_seo(
        ...     title="The Ultimate Guide to Python Programming",
        ...     script="Python is a powerful programming language that's perfect for beginners...",
        ...     brand_name="CodeAcademy",
        ...     use_ai=True  # Enable AI-powered metadata generation
        ... )
        >>> print(f"AI-Generated Description: {result['meta_description']}")
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
    
    # Step 2: Generate related keyword suggestions
    # Note: When using AI, related keywords are generated by AI within metadata generation
    # For rule-based generation, we use the traditional context-based approach
    related_keywords = []
    if include_related and not use_ai:
        # Use rule-based related keywords only when NOT using AI
        # (AI generation includes its own related keyword suggestions)
        related_keywords = extractor.suggest_related_keywords(
            keywords=extraction_result.primary_keywords,
            original_text=f"{title} {script}",
            max_suggestions=10
        )
    
    # Step 3: Generate SEO metadata
    if use_ai:
        # Use AI-powered metadata generation (POST-001)
        # AI will generate its own related keyword suggestions if include_related is True
        metadata = generate_ai_seo_metadata(
            title=title,
            script=script,
            primary_keywords=extraction_result.primary_keywords,
            secondary_keywords=extraction_result.secondary_keywords,
            keyword_density=extraction_result.keyword_density,
            config=ai_config,
            brand_name=brand_name,
            generate_related=include_related  # AI handles related keywords
        )
    else:
        # Use rule-based metadata generation
        generator = MetadataGenerator(brand_name=brand_name)
        
        metadata = generator.generate_metadata(
            title=title,
            script=script,
            primary_keywords=extraction_result.primary_keywords,
            secondary_keywords=extraction_result.secondary_keywords,
            keyword_density=extraction_result.keyword_density,
            related_keywords=related_keywords  # Use rule-based related keywords
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
        'generation_timestamp': metadata.generation_timestamp,
        'ai_generated': use_ai  # Flag indicating if AI was used
    }
    
    return result


# Export main classes and functions
__all__ = [
    # Classes
    'KeywordExtractor',
    'KeywordExtractionResult',
    'MetadataGenerator',
    'AIMetadataGenerator',
    'SEOMetadata',
    'AIConfig',
    
    # Functions
    'extract_keywords',
    'generate_seo_metadata',
    'generate_ai_seo_metadata',
    'process_content_seo',
]
