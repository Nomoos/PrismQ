"""SEO Metadata Generator module for PrismQ.T.Publishing.SEO.Keywords.

This module generates SEO-optimized metadata including meta descriptions,
title tags, and structured data for published content.

Workflow Position:
    Stage: SEO Optimization (POST-001)
    Input: Title + Script + Keywords → Generate Metadata → Output: SEO metadata
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class SEOMetadata:
    """SEO metadata for published content.
    
    Attributes:
        primary_keywords: Main focus keywords
        secondary_keywords: Supporting keywords
        meta_description: SEO meta description (150-160 chars)
        title_tag: Optimized title tag (<60 chars)
        keyword_density: Keyword density analysis
        related_keywords: Suggested related keywords
        og_title: Open Graph title (for social media)
        og_description: Open Graph description (for social media)
        generation_timestamp: When metadata was generated
        quality_score: Quality score (0-100) based on SEO best practices
        recommendations: List of SEO recommendations
    """
    
    primary_keywords: List[str] = field(default_factory=list)
    secondary_keywords: List[str] = field(default_factory=list)
    meta_description: str = ""
    title_tag: str = ""
    keyword_density: Dict[str, float] = field(default_factory=dict)
    related_keywords: List[str] = field(default_factory=list)
    og_title: str = ""
    og_description: str = ""
    generation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    quality_score: int = 0
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"SEOMetadata("
            f"primary={len(self.primary_keywords)}, "
            f"secondary={len(self.secondary_keywords)}, "
            f"quality={self.quality_score})"
        )


class MetadataGenerator:
    """Generate SEO-optimized metadata for published content.
    
    Creates meta descriptions, title tags, and structured data
    following SEO best practices.
    """
    
    # Character limits
    META_DESCRIPTION_MIN = 150
    META_DESCRIPTION_MAX = 160
    TITLE_TAG_MAX = 60
    OG_DESCRIPTION_MAX = 200
    
    def __init__(
        self,
        brand_name: Optional[str] = None,
        include_brand: bool = True
    ):
        """Initialize the metadata generator.
        
        Args:
            brand_name: Optional brand name to append to titles
            include_brand: Whether to include brand name in title tags
        """
        self.brand_name = brand_name
        self.include_brand = include_brand
    
    def generate_metadata(
        self,
        title: str,
        script: str,
        primary_keywords: List[str],
        secondary_keywords: List[str],
        keyword_density: Dict[str, float],
        related_keywords: Optional[List[str]] = None
    ) -> SEOMetadata:
        """Generate comprehensive SEO metadata.
        
        Args:
            title: Content title
            script: Content script/body
            primary_keywords: Primary keywords
            secondary_keywords: Secondary keywords
            keyword_density: Keyword density analysis
            related_keywords: Optional related keyword suggestions
        
        Returns:
            SEOMetadata object with all metadata fields
        """
        metadata = SEOMetadata(
            primary_keywords=primary_keywords,
            secondary_keywords=secondary_keywords,
            keyword_density=keyword_density,
            related_keywords=related_keywords or []
        )
        
        # Generate meta description
        metadata.meta_description = self._generate_meta_description(
            title, script, primary_keywords
        )
        
        # Generate title tag
        metadata.title_tag = self._generate_title_tag(title, primary_keywords)
        
        # Generate Open Graph metadata (for social media)
        metadata.og_title = self._generate_og_title(title)
        metadata.og_description = self._generate_og_description(
            metadata.meta_description, script
        )
        
        # Calculate quality score and recommendations
        metadata.quality_score = self._calculate_quality_score(metadata)
        metadata.recommendations = self._generate_recommendations(metadata, title, script)
        
        return metadata
    
    def _generate_meta_description(
        self,
        title: str,
        script: str,
        primary_keywords: List[str]
    ) -> str:
        """Generate SEO-optimized meta description.
        
        Args:
            title: Content title
            script: Content script
            primary_keywords: Primary keywords to include
        
        Returns:
            Meta description (150-160 characters)
        """
        # Extract first meaningful sentences
        sentences = self._extract_sentences(script)
        
        # Build description starting with title context
        description = ""
        
        # Try to create description from first sentences
        for sentence in sentences[:3]:
            test_description = f"{description} {sentence}".strip()
            if len(test_description) <= self.META_DESCRIPTION_MAX:
                description = test_description
            else:
                break
        
        # If too short, pad with more context
        if len(description) < self.META_DESCRIPTION_MIN and len(sentences) > 1:
            for sentence in sentences[1:5]:
                test_description = f"{description} {sentence}".strip()
                if len(test_description) <= self.META_DESCRIPTION_MAX:
                    description = test_description
                else:
                    break
        
        # Ensure it's within range
        if len(description) > self.META_DESCRIPTION_MAX:
            # Trim to last complete word before limit
            description = description[:self.META_DESCRIPTION_MAX].rsplit(' ', 1)[0] + "..."
        elif len(description) < self.META_DESCRIPTION_MIN:
            # If still too short, use title + first sentence
            description = f"{title}. {sentences[0] if sentences else ''}"
            if len(description) > self.META_DESCRIPTION_MAX:
                description = description[:self.META_DESCRIPTION_MAX].rsplit(' ', 1)[0] + "..."
        
        # Ensure at least one primary keyword is present
        description_lower = description.lower()
        has_keyword = any(kw in description_lower for kw in primary_keywords[:3])
        
        if not has_keyword and primary_keywords:
            # Try to naturally insert first keyword
            keyword = primary_keywords[0]
            if len(description) + len(keyword) + 10 < self.META_DESCRIPTION_MAX:
                description = f"{keyword.title()}: {description}"
        
        return description.strip()
    
    def _generate_title_tag(
        self,
        title: str,
        primary_keywords: List[str]
    ) -> str:
        """Generate SEO-optimized title tag.
        
        Args:
            title: Original title
            primary_keywords: Primary keywords
        
        Returns:
            Title tag (<60 characters)
        """
        # Calculate available space
        brand_suffix = f" | {self.brand_name}" if self.include_brand and self.brand_name else ""
        available_space = self.TITLE_TAG_MAX - len(brand_suffix)
        
        # If title fits, use it
        if len(title) <= available_space:
            title_tag = title + brand_suffix
        else:
            # Trim title to fit
            trimmed_title = title[:available_space].rsplit(' ', 1)[0]
            title_tag = trimmed_title + brand_suffix
        
        # Ensure primary keyword is present
        title_lower = title_tag.lower()
        if primary_keywords and primary_keywords[0] not in title_lower:
            # Try to insert keyword at beginning
            keyword = primary_keywords[0].title()
            test_title = f"{keyword}: {title}"
            if len(test_title) + len(brand_suffix) <= self.TITLE_TAG_MAX:
                title_tag = test_title + brand_suffix
        
        return title_tag.strip()
    
    def _generate_og_title(self, title: str) -> str:
        """Generate Open Graph title for social media.
        
        Args:
            title: Original title
        
        Returns:
            Open Graph title (similar to title tag)
        """
        # OG titles can be slightly longer (up to 70 chars)
        max_length = 70
        
        if len(title) <= max_length:
            return title
        
        # Trim to fit
        return title[:max_length].rsplit(' ', 1)[0]
    
    def _generate_og_description(
        self,
        meta_description: str,
        script: str
    ) -> str:
        """Generate Open Graph description for social media.
        
        Args:
            meta_description: Generated meta description
            script: Content script
        
        Returns:
            Open Graph description (up to 200 characters)
        """
        # OG descriptions can be longer than meta descriptions
        # Start with meta description
        og_desc = meta_description.replace("...", "")
        
        # If there's room, add more context
        if len(og_desc) < self.OG_DESCRIPTION_MAX:
            sentences = self._extract_sentences(script)
            for sentence in sentences:
                if sentence.lower() not in og_desc.lower():
                    test_desc = f"{og_desc} {sentence}"
                    if len(test_desc) <= self.OG_DESCRIPTION_MAX:
                        og_desc = test_desc
                    else:
                        break
        
        # Ensure within limit
        if len(og_desc) > self.OG_DESCRIPTION_MAX:
            og_desc = og_desc[:self.OG_DESCRIPTION_MAX].rsplit(' ', 1)[0] + "..."
        
        return og_desc.strip()
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract clean sentences from text.
        
        Args:
            text: Text content
        
        Returns:
            List of sentences
        """
        # Split by sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            # Keep sentences that are meaningful (5+ words)
            if sentence and len(sentence.split()) >= 5:
                clean_sentences.append(sentence)
        
        return clean_sentences
    
    def _calculate_quality_score(self, metadata: SEOMetadata) -> int:
        """Calculate SEO quality score (0-100).
        
        Args:
            metadata: SEO metadata to evaluate
        
        Returns:
            Quality score (0-100)
        """
        score = 0
        
        # Meta description length check (20 points)
        desc_len = len(metadata.meta_description)
        if self.META_DESCRIPTION_MIN <= desc_len <= self.META_DESCRIPTION_MAX:
            score += 20
        elif desc_len >= 140:  # Close enough
            score += 15
        elif desc_len >= 120:
            score += 10
        
        # Title tag length check (20 points)
        title_len = len(metadata.title_tag)
        if title_len <= self.TITLE_TAG_MAX:
            score += 20
        elif title_len <= 70:  # Slightly over but acceptable
            score += 15
        
        # Primary keywords present (30 points)
        if len(metadata.primary_keywords) >= 3:
            score += 30
        elif len(metadata.primary_keywords) >= 2:
            score += 20
        elif len(metadata.primary_keywords) >= 1:
            score += 10
        
        # Secondary keywords present (15 points)
        if len(metadata.secondary_keywords) >= 5:
            score += 15
        elif len(metadata.secondary_keywords) >= 3:
            score += 10
        elif len(metadata.secondary_keywords) >= 1:
            score += 5
        
        # Related keywords suggestions (10 points)
        if len(metadata.related_keywords) >= 5:
            score += 10
        elif len(metadata.related_keywords) >= 3:
            score += 5
        
        # Open Graph metadata present (5 points)
        if metadata.og_title and metadata.og_description:
            score += 5
        
        return min(score, 100)
    
    def _generate_recommendations(
        self,
        metadata: SEOMetadata,
        title: str,
        script: str
    ) -> List[str]:
        """Generate SEO improvement recommendations.
        
        Args:
            metadata: Generated SEO metadata
            title: Original title
            script: Content script
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check meta description length
        desc_len = len(metadata.meta_description)
        if desc_len < self.META_DESCRIPTION_MIN:
            recommendations.append(
                f"Meta description is too short ({desc_len} chars). "
                f"Aim for {self.META_DESCRIPTION_MIN}-{self.META_DESCRIPTION_MAX} characters."
            )
        elif desc_len > self.META_DESCRIPTION_MAX:
            recommendations.append(
                f"Meta description is too long ({desc_len} chars). "
                f"It will be truncated in search results."
            )
        
        # Check title tag length
        title_len = len(metadata.title_tag)
        if title_len > self.TITLE_TAG_MAX:
            recommendations.append(
                f"Title tag is too long ({title_len} chars). "
                f"It may be truncated in search results. Aim for <{self.TITLE_TAG_MAX} characters."
            )
        
        # Check keyword presence in meta description
        desc_lower = metadata.meta_description.lower()
        keywords_in_desc = sum(1 for kw in metadata.primary_keywords[:3] if kw in desc_lower)
        if keywords_in_desc == 0:
            recommendations.append(
                "Consider including at least one primary keyword in the meta description."
            )
        
        # Check keyword diversity
        if len(metadata.primary_keywords) < 3:
            recommendations.append(
                f"Only {len(metadata.primary_keywords)} primary keyword(s) found. "
                "Consider expanding content to include more diverse keywords."
            )
        
        # Check content length
        word_count = len(script.split())
        if word_count < 300:
            recommendations.append(
                f"Content is relatively short ({word_count} words). "
                "Longer content (500+ words) typically performs better in search results."
            )
        
        # Check related keywords
        if len(metadata.related_keywords) < 3:
            recommendations.append(
                "Consider incorporating suggested related keywords to improve topical relevance."
            )
        
        # If no recommendations, add positive feedback
        if not recommendations:
            recommendations.append("SEO metadata meets all best practice guidelines!")
        
        return recommendations


def generate_seo_metadata(
    title: str,
    script: str,
    primary_keywords: List[str],
    secondary_keywords: List[str],
    keyword_density: Dict[str, float],
    related_keywords: Optional[List[str]] = None,
    brand_name: Optional[str] = None
) -> SEOMetadata:
    """Convenience function to generate SEO metadata.
    
    Args:
        title: Content title
        script: Content script/body
        primary_keywords: Primary keywords
        secondary_keywords: Secondary keywords
        keyword_density: Keyword density analysis
        related_keywords: Optional related keyword suggestions
        brand_name: Optional brand name for title tags
    
    Returns:
        SEOMetadata object with all metadata fields
    
    Example:
        >>> metadata = generate_seo_metadata(
        ...     title="How to Learn Python",
        ...     script="Python is a great programming language...",
        ...     primary_keywords=["python", "programming", "learn"],
        ...     secondary_keywords=["beginner", "tutorial", "code"],
        ...     keyword_density={"python": 2.5, "programming": 1.8},
        ...     brand_name="TechEdu"
        ... )
        >>> print(metadata.meta_description)
        >>> print(metadata.title_tag)
    """
    generator = MetadataGenerator(brand_name=brand_name)
    return generator.generate_metadata(
        title,
        script,
        primary_keywords,
        secondary_keywords,
        keyword_density,
        related_keywords
    )
