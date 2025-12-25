# PrismQ.T.Content.Formatter.Social - Social Media Format Optimizer

Transform scripts into platform-optimized social media content for Twitter/X, LinkedIn, Instagram, and Facebook.

## Overview

The Social Media Formatter is part of PrismQ's Text Pipeline (T module) and provides intelligent transformation of long-form scripts into engaging, platform-specific social media content.

**Workflow Position**: POST-004 - Social Media Format Adaptation  
**Pipeline**: Published Script → Social Formatter → Platform-Ready Social Content

## Features

### ✨ Core Capabilities

- **Multi-Platform Support**: Twitter/X, LinkedIn, Instagram, Facebook
- **Character Limit Validation**: Strict enforcement per platform
- **Intelligent Content Adaptation**: Context-aware formatting
- **Engagement Optimization**: Hooks, CTAs, and best practices
- **A/B Testing Support**: Multiple variants per platform

### 🎯 Platform-Specific Features

#### Twitter/X
- Thread generation with 280-char limit
- Natural sentence breaks
- Thread numbering (1/n, 2/n)
- Hook optimization
- CTA in final tweet

#### LinkedIn
- Professional structure
- 140-char preview optimization
- Bullet points with arrows (→)
- 3-5 relevant hashtags
- Key takeaways section

#### Instagram
- 125-char preview optimization
- Line break separators (\n.\n.\n)
- 10-20 hashtags
- Emoji integration
- Engagement prompts

#### Facebook
- 400-char preview optimization
- Paragraph formatting
- Engagement questions
- Emoji enhancement

## Installation

The module is part of the PrismQ T pipeline. No additional installation required.

```python
from T.Script.Formatter.Social import (
    format_twitter_thread,
    format_linkedin_post,
    format_instagram_caption,
    format_facebook_post
)
```

## Quick Start

### Twitter/X Thread

```python
from T.Script.Formatter.Social import format_twitter_thread

script = """
Your long-form script content here...
"""

result = format_twitter_thread(
    script=script,
    content_id="twitter-001",
    hook_type="statement",  # or "question", "stat"
    add_cta=True,
    add_emojis=True
)

if result.success:
    print(result.formatted_content)
    print(f"Engagement score: {result.metadata.estimated_engagement_score}")
```

### LinkedIn Post

```python
from T.Script.Formatter.Social import format_linkedin_post

result = format_linkedin_post(
    script=script,
    content_id="linkedin-001",
    hook_type="statement",
    add_hashtags=True,
    num_hashtags=5,
    add_cta=True
)

if result.success:
    print(result.formatted_content)
```

### Instagram Caption

```python
from T.Script.Formatter.Social import format_instagram_caption

result = format_instagram_caption(
    script=script,
    content_id="instagram-001",
    add_hashtags=True,
    num_hashtags=15,
    add_emojis=True,
    add_engagement_prompt=True
)

if result.success:
    print(result.formatted_content)
```

### Facebook Post

```python
from T.Script.Formatter.Social import format_facebook_post

result = format_facebook_post(
    script=script,
    content_id="facebook-001",
    add_engagement_question=True,
    use_emojis=True,
    optimize_preview=True
)

if result.success:
    print(result.formatted_content)
```

## API Reference

### Convenience Functions

#### `format_twitter_thread()`

Transform script into Twitter/X thread.

**Parameters**:
- `script` (str): Script content to format
- `content_id` (str): Unique identifier
- `hook_type` (str): Hook style - "question", "statement", "stat" (default: "statement")
- `add_cta` (bool): Add call-to-action (default: True)
- `cta_text` (str, optional): Custom CTA text
- `add_emojis` (bool): Add relevant emojis (default: False)

**Returns**: `SocialMediaContent`

#### `format_linkedin_post()`

Transform script into LinkedIn post.

**Parameters**:
- `script` (str): Script content
- `content_id` (str): Unique identifier
- `hook_type` (str): Hook style (default: "statement")
- `add_hashtags` (bool): Include hashtags (default: True)
- `num_hashtags` (int): Number of hashtags, 3-5 (default: 5)
- `add_cta` (bool): Add call-to-action (default: True)
- `cta_text` (str, optional): Custom CTA text

**Returns**: `SocialMediaContent`

#### `format_instagram_caption()`

Transform script into Instagram caption.

**Parameters**:
- `script` (str): Script content
- `content_id` (str): Unique identifier
- `add_hashtags` (bool): Include hashtags (default: True)
- `num_hashtags` (int): Number of hashtags, 10-20 (default: 15)
- `add_emojis` (bool): Add emojis (default: True)
- `add_engagement_prompt` (bool): Add engagement question (default: True)

**Returns**: `SocialMediaContent`

#### `format_facebook_post()`

Transform script into Facebook post.

**Parameters**:
- `script` (str): Script content
- `content_id` (str): Unique identifier
- `add_engagement_question` (bool): Add engagement question (default: True)
- `use_emojis` (bool): Add relevant emojis (default: True)
- `optimize_preview` (bool): Optimize for preview (default: True)

**Returns**: `SocialMediaContent`

### Data Classes

#### `SocialMediaContent`

Result of social media formatting operation.

**Attributes**:
- `content_id` (str): Unique identifier
- `platform` (str): Target platform
- `formatted_content` (str): Platform-formatted content
- `metadata` (SocialMediaMetadata): Content metadata
- `variant_id` (int): Variant identifier for A/B testing
- `timestamp` (str): ISO timestamp
- `success` (bool): Whether formatting succeeded
- `errors` (list[str]): Error messages if any

#### `SocialMediaMetadata`

Metadata for social media content.

**Attributes**:
- `platform` (str): Target platform
- `character_count` (int): Total character count
- `word_count` (int): Total word count
- `estimated_engagement_score` (int): Engagement score (0-100)
- `suggested_posting_time` (str): Optimal posting times
- `hashtags` (list[str]): List of hashtags
- `variant_count` (int): Number of variants

### Formatter Classes

#### `TwitterFormatter`

Core Twitter/X thread formatter class.

```python
from T.Script.Formatter.Social import TwitterFormatter

formatter = TwitterFormatter()
result = formatter.format_twitter_thread(
    script="...",
    content_id="twitter-001",
    hook_type="statement",
    add_cta=True
)
```

#### `LinkedInFormatter`

Core LinkedIn post formatter class.

```python
from T.Script.Formatter.Social import LinkedInFormatter

formatter = LinkedInFormatter()
result = formatter.format_linkedin_post(
    script="...",
    content_id="linkedin-001"
)
```

#### `InstagramFormatter`

Core Instagram caption formatter class.

```python
from T.Script.Formatter.Social import InstagramFormatter

formatter = InstagramFormatter()
result = formatter.format_instagram_caption(
    script="...",
    content_id="instagram-001"
)
```

#### `FacebookFormatter`

Core Facebook post formatter class.

```python
from T.Script.Formatter.Social import FacebookFormatter

formatter = FacebookFormatter()
result = formatter.format_facebook_post(
    script="...",
    content_id="facebook-001"
)
```

## Platform Character Limits

| Platform | Total Limit | Preview Limit | Notes |
|----------|-------------|---------------|-------|
| Twitter/X | 280 chars | N/A | Per tweet in thread |
| LinkedIn | 3,000 chars | 140 chars | First 140 shown in feed |
| Instagram | 2,200 chars | 125 chars | First 125 shown in feed |
| Facebook | 5,000 chars* | 400 chars | *Practical limit, theoretical is 63K |

## Best Practices

### Twitter/X Threads
- Keep threads to 3-10 tweets for optimal engagement
- Use strong hook in first tweet
- End with engagement question or CTA
- Use line breaks for readability
- Add emoji sparingly (1-2 per thread)

### LinkedIn Posts
- Optimize first 140 characters (preview)
- Use professional tone
- Include 3-5 relevant hashtags
- Use arrows (→) for bullet points
- Length: 500-1500 characters ideal

### Instagram Captions
- Make first 125 characters engaging (preview)
- Use line breaks with dots (\n.\n.\n)
- Include 10-20 relevant hashtags
- Add emojis for visual appeal
- End with engagement prompt

### Facebook Posts
- Optimize first 400 characters (preview)
- Use paragraph breaks (2-3 sentences each)
- Ask questions to drive engagement
- Moderate emoji use (1-5 per post)
- Length: 500-2000 characters ideal

## Examples

See `_meta/examples/example_usage.py` for comprehensive examples including:
- Basic formatting for each platform
- A/B testing variants
- Custom hooks and CTAs
- Batch processing multiple scripts
- Error handling

## Testing

Run the test suite:

```bash
pytest T/Content/Formatter/Social/_meta/tests/test_social_formatter.py -v
```

**Test Coverage**: 43 tests covering:
- Base formatter utilities
- All platform formatters
- Character limit validation
- Metadata generation
- Edge cases and error handling

## Performance

- **Processing Speed**: <1 second per platform
- **Memory Usage**: Minimal (no external dependencies)
- **Concurrent Processing**: Supported

## Dependencies

- **Python**: 3.12+
- **External Libraries**: None (uses standard library only)
- **Internal Dependencies**: None (standalone module)

## Integration with PrismQ Pipeline

```
T.Publishing.ContentExport
    ↓ (Published Script)
T.Script.Formatter.Social
    ↓ (Platform-Formatted Content)
Platform Publishing
    → Twitter, LinkedIn, Instagram, Facebook
```

## Limitations

### Current Limitations

1. **Hashtag Generation**: Basic keyword extraction
   - Recommendation: For advanced hashtag strategy, use SEO module

2. **Sentence Splitting**: Uses regex (may not handle all edge cases)
   - Known issues: Abbreviations (Dr., Mr.), decimals (3.14)
   - Future: Consider NLP library for complex content

3. **Content-Aware Formatting**: Generic section headings
   - Future: Implement semantic analysis for better structure

4. **Image Handling**: Not supported
   - Future: Add image placement suggestions

## Future Enhancements

Planned improvements:

1. **Advanced NLP Integration**
   - Better sentence detection
   - Content-aware hook generation
   - Automatic keyword extraction

2. **A/B Testing Framework**
   - Generate multiple variants
   - Track performance metrics
   - Optimize based on engagement data

3. **Hashtag Research**
   - Trending hashtag detection
   - Competitor analysis
   - Performance-based recommendations

4. **Emoji Optimization**
   - Context-aware emoji selection
   - Engagement-driven placement
   - Cultural considerations

5. **Multi-Language Support**
   - Internationalization
   - RTL language support
   - Language-specific best practices

## Troubleshooting

### Common Issues

**Issue**: Content exceeds character limit  
**Solution**: Module automatically truncates. For better results, provide shorter script or use summary.

**Issue**: Poor engagement scores  
**Solution**: Experiment with different hook types and add CTAs.

**Issue**: Hashtags not relevant  
**Solution**: Module uses basic extraction. For better results, manually specify hashtags or use SEO module.

## Contributing

This module follows PrismQ development standards:
- Type hints for all public APIs
- Comprehensive test coverage (>90%)
- Docstrings for all classes and methods
- Security scanning with CodeQL

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

For issues or questions:
- Documentation: See this README and code docstrings
- Examples: Check `_meta/examples/example_usage.py`
- Tests: Review test cases for usage patterns

---

**Version**: 1.0.0  
**Author**: Worker12 (Content Specialist)  
**Status**: Production Ready  
**Last Updated**: 2025-11-23
