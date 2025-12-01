"""PrismQ.T.Script.Formatter.Blog - Blog Format Optimizer.

This module transforms scripts into blog-optimized format with proper heading
hierarchy, sections, and formatting for various blog platforms.

Public API:
    - BlogFormatter: Main formatter class
    - format_blog: Convenience function for blog formatting
    - export_for_platform: Platform-specific export function
    - BlogFormattedContent: Result dataclass
    - BlogMetadata: Metadata dataclass
"""

from .blog_formatter import (
    BlogFormatter,
    BlogFormattedContent,
    BlogMetadata,
    format_blog
)

from .platform_adapters import (
    PlatformAdapterFactory,
    MediumAdapter,
    WordPressAdapter,
    GhostAdapter,
    export_for_platform
)

__all__ = [
    # Main formatter
    'BlogFormatter',
    'format_blog',
    
    # Platform adapters
    'PlatformAdapterFactory',
    'MediumAdapter',
    'WordPressAdapter',
    'GhostAdapter',
    'export_for_platform',
    
    # Data classes
    'BlogFormattedContent',
    'BlogMetadata',
]

__version__ = '1.0.0'
__author__ = 'Worker12 (Content Specialist)'
