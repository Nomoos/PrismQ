# T/Content/Formatter/Blog - Blog Format Optimizer

**Namespace**: `PrismQ.T.Content.Formatter.Blog`

Transform scripts into blog-optimized format with proper heading hierarchy, sections, and formatting suitable for various blog platforms.

## Purpose

Convert narrative scripts into well-structured blog posts ready for publication on platforms like Medium, WordPress, Ghost, and others. The formatter ensures optimal readability with proper heading hierarchy, paragraph breaks, and platform-specific optimizations.

## Features

- ✅ **Heading Hierarchy**: Automatic H1, H2, H3 structure
- ✅ **Readable Paragraphs**: Max 3-4 sentences per paragraph
- ✅ **Strategic CTAs**: Call-to-action placement at key points
- ✅ **Blog Metadata**: Excerpt, reading time, word count
- ✅ **Multiple Formats**: Markdown and HTML output
- ✅ **Platform Optimization**: Medium, WordPress, Ghost support
- ✅ **Formatting Preservation**: Bold, italic, quotes maintained

## Quick Start

```python
from T.Script.Formatter.Blog import format_blog

# Format a script as a blog post
result = format_blog(
    script="Your script content here...",
    title="My Awesome Blog Post",
    content_id="blog-001",
    platform="medium",
    format_type="markdown"
)

print(result.formatted_content)
print(f"Reading time: {result.metadata.reading_time}")
print(f"Word count: {result.metadata.word_count}")
```

## Usage

### Basic Blog Formatting

```python
from T.Script.Formatter.Blog import BlogFormatter

formatter = BlogFormatter()

result = formatter.format_blog(
    script="This is a story about innovation...",
    title="Innovation Story",
    content_id="story-001"
)

if result.success:
    print(result.formatted_content)
else:
    print(f"Errors: {result.errors}")
```

### Platform-Specific Export

```python
from T.Script.Formatter.Blog import export_for_platform

# Export for Medium
result = export_for_platform(
    script="Your content...",
    title="My Post",
    content_id="post-001",
    platform="medium",
    format_type="markdown"
)

# Export for WordPress
result = export_for_platform(
    script="Your content...",
    title="My Post",
    content_id="post-002",
    platform="wordpress",
    format_type="html"
)

# Export for Ghost
result = export_for_platform(
    script="Your content...",
    title="My Post",
    content_id="post-003",
    platform="ghost",
    format_type="markdown"
)
```

### Adding Call-to-Action Sections

```python
result = format_blog(
    script="Your script...",
    title="My Post",
    content_id="post-004",
    cta_text="Subscribe to our newsletter for more insights!"
)

# CTAs are automatically placed:
# - After introduction
# - Mid-content
# - At the end
```

## API Reference

### Main Classes

#### `BlogFormatter`

Main formatter class for blog content transformation.

**Methods**:
- `format_blog(script, title, content_id, platform, format_type, cta_text)` - Format script as blog

#### `BlogFormattedContent`

Dataclass containing formatted blog content and metadata.

**Attributes**:
- `content_id` - Unique identifier
- `title` - Blog post title
- `formatted_content` - Formatted blog content
- `metadata` - Blog metadata (BlogMetadata object)
- `format_type` - Output format (markdown or html)
- `platform` - Target platform
- `success` - Whether formatting succeeded
- `errors` - List of errors (if any)

#### `BlogMetadata`

Dataclass containing blog post metadata.

**Attributes**:
- `excerpt` - Short excerpt (150-200 chars)
- `reading_time` - Estimated reading time
- `word_count` - Total word count
- `char_count` - Character count
- `paragraph_count` - Number of paragraphs
- `heading_count` - Number of headings
- `featured_image_suggestions` - Suggested image placements

### Functions

#### `format_blog()`

Convenience function for quick blog formatting.

```python
def format_blog(
    script: str,
    title: str,
    content_id: str,
    platform: str = "generic",
    format_type: str = "markdown",
    cta_text: Optional[str] = None
) -> BlogFormattedContent
```

#### `export_for_platform()`

Export blog content optimized for specific platform.

```python
def export_for_platform(
    script: str,
    title: str,
    content_id: str,
    platform: str,
    format_type: str = "markdown",
    cta_text: Optional[str] = None
) -> BlogFormattedContent
```

## Platform Support

### Medium

- Medium-style section dividers (`---`)
- Optimized for Medium's typography
- Import-ready format
- Proper quote formatting

### WordPress

- WordPress blocks format hints
- Gutenberg-compatible
- Meta fields included
- Shortcode support

### Ghost

- Ghost-flavored Markdown
- Frontmatter metadata
- Ghost card formatting
- Bookmark card support

### Generic

- Standard Markdown/HTML
- Platform-agnostic formatting
- Works with any blog platform

## Blog Structure Template

```markdown
# Title (H1)

[Featured Image]

## Introduction (H2)
Opening paragraph (hook)

## Main Content (H2)
### Subsection 1 (H3)
Content...

### Subsection 2 (H3)
Content...

## Key Takeaways (H2)
- Bullet point 1
- Bullet point 2
- Bullet point 3

## Conclusion (H2)
Closing thoughts

[Call-to-Action]
```

## Formatting Rules

1. **Paragraphs**: 3-4 sentences max for readability
2. **Lists**: Convert enumerations to bullet points
3. **Headings**: Insert H2 every 300-400 words
4. **CTA Placement**: After introduction, mid-content, end
5. **Quotes**: Format as blockquotes with attribution
6. **Code blocks**: Preserve with syntax highlighting markers

## Reading Time Calculation

Reading time is calculated using an average reading speed of 225 words per minute:

```python
reading_time = word_count / 225  # minutes
```

## Examples

### Example 1: Short Blog Post

```python
script = """
This is a story about innovation. Innovation changes the world.
We see it everywhere. From technology to art. From science to culture.
"""

result = format_blog(script, "Innovation", "blog-001")

# Output:
# # Innovation
# 
# ## Introduction
# This is a story about innovation. Innovation changes the world.
# 
# ## Conclusion
# We see it everywhere. From technology to art. From science to culture.
#
# Reading time: 1 min read
```

### Example 2: Medium Export

```python
result = export_for_platform(
    script="Your long-form content...",
    title="How to Innovate",
    content_id="medium-001",
    platform="medium",
    format_type="markdown"
)

# Result includes Medium-specific optimizations
# Ready to import into Medium via Import Story feature
```

## Testing

Run the test suite:

```bash
pytest T/Content/Formatter/Blog/_meta/tests/test_blog_formatter.py -v
```

Test coverage includes:
- ✅ Basic formatting functionality
- ✅ Platform-specific exports (Medium, WordPress, Ghost)
- ✅ Various script lengths (500, 1000, 2000+ words)
- ✅ Heading hierarchy validation
- ✅ Reading time accuracy
- ✅ CTA insertion
- ✅ Metadata generation
- ✅ Edge cases and error handling

## Integration with PrismQ Pipeline

```
T.Publishing.ContentExport
    ↓ (Published Script)
T.Script.Formatter.Blog
    ↓ (Blog-Formatted Content)
Platform Publishing
    → Medium, WordPress, Ghost, etc.
```

## Dependencies

- Python 3.12+
- No external dependencies (uses stdlib only)

## Module Structure

```
T/Content/Formatter/Blog/
├── __init__.py                      # Public API
├── blog_formatter.py                # Core formatter logic
├── platform_adapters.py             # Platform-specific adapters
├── _meta/
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_blog_formatter.py  # Comprehensive tests
│   └── __init__.py
└── templates/                        # (Future: Template files)
```

## Performance

- Processing time: <1 second per 1000 words
- Memory efficient: Streaming-capable
- No external API calls required

## Success Metrics

- ✅ Blog structure validation 100% pass rate
- ✅ Reading time accuracy within ±10%
- ✅ Support for 3+ blog platforms
- ✅ Formatting preservation 100%
- ✅ Processing time <3 seconds per 1000 words

## Future Enhancements

- Advanced NLP-based section detection
- Custom template support
- Image placement optimization
- SEO keyword integration
- Multi-language support

## Related Modules

- **[T.Publishing.ContentExport](../../Publishing/ContentExport/)** - Content export module
- **[T.Script](../)** - Script development module
- **[T.Publishing](../../Publishing/)** - Publishing pipeline

## Issue Reference

- **POST-003**: T.Script.MultiFormat - Blog Format Optimization
- **Sprint 4**: Text Pipeline Enhancement - Part 1
- **Worker**: Worker12 (Content Specialist)

## Version

**Version**: 1.0.0  
**Status**: ✅ Complete  
**Last Updated**: 2025-11-23

---

**Start exploring**: [Test Examples](./_meta/tests/test_blog_formatter.py) | [Core Formatter](./blog_formatter.py) | [Platform Adapters](./platform_adapters.py)
