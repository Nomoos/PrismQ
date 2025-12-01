"""Platform-specific adapters for blog formatting.

This module provides platform-specific optimizations for different blog platforms
including Medium, WordPress, and Ghost.
"""

from typing import Dict, Any, Optional
from .blog_formatter import BlogFormattedContent, BlogFormatter


class MediumAdapter:
    """Adapter for Medium platform-specific formatting.
    
    Medium specifics:
    - Uses Medium-style section dividers (---)
    - Optimizes for Medium's typography
    - Proper quote formatting
    """
    
    @staticmethod
    def optimize(content: BlogFormattedContent) -> BlogFormattedContent:
        """Apply Medium-specific optimizations.
        
        Args:
            content: Blog formatted content
        
        Returns:
            Content optimized for Medium
        """
        # Medium uses --- for section breaks
        optimized_text = content.formatted_content
        
        # Add Medium-specific styling hints in comments
        if content.format_type == "markdown":
            # Medium quote formatting is already compatible with standard Markdown
            
            # Add note about importing to Medium
            optimized_text = (
                "<!-- Import this to Medium via Import Story feature -->\n\n" +
                optimized_text
            )
        
        content.formatted_content = optimized_text
        return content


class WordPressAdapter:
    """Adapter for WordPress platform-specific formatting.
    
    WordPress specifics:
    - Generates WordPress blocks format (when using Gutenberg)
    - Includes shortcode support hints
    - Adds meta fields for Gutenberg
    """
    
    @staticmethod
    def optimize(content: BlogFormattedContent) -> BlogFormattedContent:
        """Apply WordPress-specific optimizations.
        
        Args:
            content: Blog formatted content
        
        Returns:
            Content optimized for WordPress
        """
        optimized_text = content.formatted_content
        
        if content.format_type == "html":
            # WordPress-specific: Add Gutenberg block hints
            optimized_text = (
                "<!-- wp:paragraph -->\n" +
                optimized_text +
                "\n<!-- /wp:paragraph -->"
            )
            
            # Add WordPress metadata hints
            wp_meta = f"""
<!-- WordPress Metadata
Title: {content.title}
Excerpt: {content.metadata.excerpt}
Reading Time: {content.metadata.reading_time}
-->

"""
            optimized_text = wp_meta + optimized_text
        
        content.formatted_content = optimized_text
        return content


class GhostAdapter:
    """Adapter for Ghost platform-specific formatting.
    
    Ghost specifics:
    - Uses Ghost-flavored Markdown
    - Ghost card formatting
    - Bookmark cards for links
    """
    
    @staticmethod
    def optimize(content: BlogFormattedContent) -> BlogFormattedContent:
        """Apply Ghost-specific optimizations.
        
        Args:
            content: Blog formatted content
        
        Returns:
            Content optimized for Ghost
        """
        optimized_text = content.formatted_content
        
        if content.format_type == "markdown":
            # Ghost-specific: Add frontmatter
            ghost_frontmatter = f"""---
title: {content.title}
excerpt: {content.metadata.excerpt}
---

"""
            optimized_text = ghost_frontmatter + optimized_text
            
            # Convert simple image placeholders to Ghost cards
            optimized_text = optimized_text.replace(
                "[Featured Image]",
                "{{< figure src=\"/images/featured.jpg\" alt=\"Featured Image\" >}}"
            )
        
        content.formatted_content = optimized_text
        return content


class PlatformAdapterFactory:
    """Factory for creating platform-specific adapters."""
    
    _adapters = {
        'medium': MediumAdapter,
        'wordpress': WordPressAdapter,
        'ghost': GhostAdapter
    }
    
    @classmethod
    def get_adapter(cls, platform: str) -> Optional[Any]:
        """Get adapter for specified platform.
        
        Args:
            platform: Platform name (medium, wordpress, ghost)
        
        Returns:
            Adapter class or None for generic
        """
        return cls._adapters.get(platform.lower())
    
    @classmethod
    def optimize_for_platform(
        cls, 
        content: BlogFormattedContent, 
        platform: str
    ) -> BlogFormattedContent:
        """Optimize content for specific platform.
        
        Args:
            content: Blog formatted content
            platform: Target platform
        
        Returns:
            Platform-optimized content
        """
        adapter = cls.get_adapter(platform)
        
        if adapter:
            return adapter.optimize(content)
        
        # Return as-is for generic or unknown platforms
        return content


def export_for_platform(
    script: str,
    title: str,
    content_id: str,
    platform: str,
    format_type: str = "markdown",
    cta_text: Optional[str] = None
) -> BlogFormattedContent:
    """Export blog content optimized for specific platform.
    
    Args:
        script: The script content to format
        title: Blog post title
        content_id: Unique identifier for the content
        platform: Target platform (generic, medium, wordpress, ghost)
        format_type: Output format (markdown or html)
        cta_text: Optional custom CTA text
    
    Returns:
        Platform-optimized BlogFormattedContent
    
    Example:
        >>> result = export_for_platform(
        ...     script="This is a story...",
        ...     title="My Story",
        ...     content_id="story-001",
        ...     platform="medium",
        ...     format_type="markdown"
        ... )
        >>> # Content is optimized for Medium
    """
    # First, format as blog
    formatter = BlogFormatter()
    content = formatter.format_blog(
        script, title, content_id, platform, format_type, cta_text
    )
    
    # Then apply platform-specific optimizations
    optimized_content = PlatformAdapterFactory.optimize_for_platform(content, platform)
    
    return optimized_content
