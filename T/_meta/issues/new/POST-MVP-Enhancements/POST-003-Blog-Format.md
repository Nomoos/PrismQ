# POST-003: T.Script.MultiFormat - Blog Format Optimization

**Type**: Post-MVP Enhancement  
**Worker**: Worker12 (Content Specialist)  
**Priority**: High  
**Effort**: 2 days  
**Module**: `PrismQ.T.Content.Formatter.Blog`  
**Sprint**: Sprint 4 (Weeks 9-10)  
**Status**: 🎯 PLANNED

---

## Description

Transform scripts into blog-optimized format with proper heading hierarchy, sections, and formatting.

This formatter will convert narrative scripts into well-structured blog posts suitable for platforms like Medium, WordPress, Ghost, and others, with appropriate HTML/Markdown formatting.

---

## Acceptance Criteria

- [ ] Convert script to blog structure with H1, H2, H3 hierarchy
- [ ] Add paragraph breaks for readability (max 3-4 sentences per paragraph)
- [ ] Insert call-to-action (CTA) sections at strategic points
- [ ] Optimize for readability (shorter paragraphs, bullet points where appropriate)
- [ ] Generate blog-specific metadata (excerpt, reading time)
- [ ] Support multiple output formats (Markdown, HTML)
- [ ] Platform-specific optimizations (Medium, WordPress, Ghost)
- [ ] Preserve formatting marks (bold, italic, quotes)

---

## Input/Output

**Input**:
- Published script content
- Target platform (Medium/WordPress/Ghost/Generic)
- Formatting preferences (optional)

**Output**:
- Blog-formatted content (Markdown or HTML)
- Blog metadata:
  - Excerpt (150-200 chars)
  - Reading time estimate
  - Word count
  - Suggested featured image placement
- Platform-specific export file

---

## Dependencies

- **MVP-024**: Publishing.Finalization module (provides published script)

---

## Technical Notes

### Blog Structure Template
```
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

### Platform-Specific Features

**Medium**:
- Optimize for Medium's typography
- Use Medium-style section dividers (---)
- Ensure proper quote formatting

**WordPress**:
- Generate WordPress blocks format
- Include shortcode support
- Add meta fields for Gutenberg

**Ghost**:
- Use Ghost-flavored Markdown
- Add Ghost card formatting
- Include bookmark cards for links

### Files to Create
- `T/Content/Formatter/Blog/blog_formatter.py` (new)
- `T/Content/Formatter/Blog/platform_adapters.py` (new)
- `T/Content/Formatter/Blog/templates/` (new directory with templates)
- `T/Content/Formatter/Blog/__init__.py` (new)

### Reading Time Calculation
```python
def calculate_reading_time(word_count: int) -> str:
    # Average reading speed: 200-250 words/minute
    minutes = word_count / 225
    return f"{int(minutes)} min read"
```

### Testing Requirements
- [ ] Test with various script lengths (500, 1000, 2000+ words)
- [ ] Validate heading hierarchy (H1 > H2 > H3)
- [ ] Test CTA insertion points
- [ ] Verify reading time calculation accuracy
- [ ] Test platform-specific exports (Medium, WordPress, Ghost)
- [ ] Ensure formatting preservation

---

## Blog Formatting Rules

1. **Paragraphs**: 3-4 sentences max
2. **Lists**: Convert enumerations to bullet points
3. **Headings**: Insert H2 every 300-400 words
4. **CTA Placement**: After introduction, mid-content, end
5. **Quotes**: Format as blockquotes with attribution
6. **Code blocks**: Preserve with syntax highlighting markers

---

## Example Output

**Input Script**:
```
This is a story about innovation. First we discuss the problem. 
Then we explore solutions. Finally we conclude with action steps.
```

**Output Blog**:
```markdown
# Innovation in Action

## The Problem We Face

This is a story about innovation that tackles real-world challenges.

## Exploring Solutions

First we discuss the problem from multiple angles...

## Taking Action

Finally we conclude with these action steps:
- Step 1
- Step 2
- Step 3

---
*5 min read*
```

---

## Success Metrics

- Blog structure validation 100% pass rate
- Reading time accuracy within ±10%
- Support for 3+ blog platforms
- Formatting preservation 100%
- Processing time <3 seconds per 1000 words

---

**Created**: 2025-11-23  
**Owner**: Worker12 (Content Specialist)
