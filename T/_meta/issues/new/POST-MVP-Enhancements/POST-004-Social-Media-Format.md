# POST-004: T.Script.MultiFormat - Social Media Adaptation

**Type**: Post-MVP Enhancement  
**Worker**: Worker12 (Content Specialist)  
**Priority**: High  
**Effort**: 2 days  
**Module**: `PrismQ.T.Content.Formatter.Social`  
**Sprint**: Sprint 4 (Weeks 9-10)  
**Status**: 🎯 PLANNED

---

## Description

Adapt scripts for social media platforms including Twitter/X threads, LinkedIn posts, and Instagram captions.

This formatter will intelligently break down long-form content into platform-optimized formats while maintaining the key message, tone, and call-to-action across all variants.

---

## Acceptance Criteria

- [ ] Generate Twitter/X thread with optimal tweet breaks (280 char limit)
- [ ] Create LinkedIn post format with hook, body, and CTA structure
- [ ] Generate Instagram caption with hashtags and formatting
- [ ] Character limit validation per platform (strict enforcement)
- [ ] Maintain key message consistency across all formats
- [ ] Include platform-specific best practices (hooks, emojis, hashtags)
- [ ] Generate multiple variants (A/B testing options)
- [ ] Preserve core narrative flow

---

## Input/Output

**Input**:
- Published script content
- Target platforms (Twitter, LinkedIn, Instagram, Facebook)
- Brand voice guidelines (optional)
- Hashtag preferences (optional)

**Output**:
- Platform-specific formatted content:
  - **Twitter/X**: Thread (array of tweets)
  - **LinkedIn**: Post with formatting
  - **Instagram**: Caption + suggested hashtags
  - **Facebook**: Formatted post
- Metadata for each platform:
  - Character count
  - Estimated engagement score
  - Suggested posting time

---

## Dependencies

- **MVP-024**: Publishing.Finalization module

---

## Technical Notes

### Platform Character Limits
- **Twitter/X**: 280 characters per tweet
- **LinkedIn**: 3,000 characters (first 140 visible)
- **Instagram**: 2,200 characters caption (first 125 visible)
- **Facebook**: 63,206 characters (first 400 visible)

### Twitter/X Thread Generation
```python
def create_twitter_thread(script: str) -> list[str]:
    """
    Break script into optimal tweet-sized chunks.
    - Use natural sentence breaks
    - Add thread numbering (1/n, 2/n, etc.)
    - Ensure hook in first tweet
    - End with CTA in final tweet
    """
    pass
```

### LinkedIn Post Structure
```
[Hook - Attention grabbing first line]

[Problem/Context - 2-3 lines]

[Main Content - Core message]

[Key Takeaways]
→ Point 1
→ Point 2
→ Point 3

[CTA - Clear next step]

#Hashtag1 #Hashtag2 #Hashtag3
```

### Instagram Caption Format
```
[Engaging first line that shows in preview]

[Content - Use line breaks for readability]

.
.
.
[Key message]

[CTA + Engagement prompt]

#Hashtag1 #Hashtag2 #Hashtag3...
```

### Files to Create
- `T/Content/Formatter/Social/twitter_formatter.py` (new)
- `T/Content/Formatter/Social/linkedin_formatter.py` (new)
- `T/Content/Formatter/Social/instagram_formatter.py` (new)
- `T/Content/Formatter/Social/facebook_formatter.py` (new)
- `T/Content/Formatter/Social/base_formatter.py` (new - shared logic)
- `T/Content/Formatter/Social/__init__.py` (new)

### Social Media Best Practices

**Twitter/X**:
- Hook in first 30 characters
- Use line breaks for readability
- Add relevant emoji (sparingly)
- Include call-to-action in last tweet

**LinkedIn**:
- Strong hook (first 140 chars shown)
- Professional tone
- Use bullet points with → or •
- 3-5 relevant hashtags

**Instagram**:
- Engaging preview (first 125 chars)
- Line breaks for readability (...\n.\n.\n...)
- 10-20 relevant hashtags
- Emojis for visual appeal
- Engagement prompts (questions, polls)

**Facebook**:
- First 400 chars most important
- Paragraph breaks every 2-3 sentences
- Use questions to drive engagement
- Include link preview optimization

### Testing Requirements
- [ ] Validate character limits for each platform
- [ ] Test thread coherence (Twitter)
- [ ] Verify hook effectiveness (first line impact)
- [ ] Test hashtag relevance
- [ ] Validate formatting preservation
- [ ] Test with various content lengths
- [ ] Ensure CTA clarity across all formats

---

## Example Transformations

### Original Script (200 words)
"Innovation drives progress. Here's how we transformed our approach..."

### Twitter Thread Output
```
1/5 Innovation drives progress 🚀

Here's how we transformed our approach to solve real problems.

2/5 The Challenge:
Traditional methods weren't scaling. We needed a fresh perspective.

3/5 Our Solution:
→ Rethink the fundamentals
→ Build incrementally
→ Test relentlessly

4/5 The Results:
10x improvement in efficiency
85% cost reduction
Team satisfaction through the roof

5/5 Key Takeaway:
Innovation isn't about big leaps—it's about consistent, smart iteration.

What's your approach to innovation? 💭
```

### LinkedIn Post Output
```
Innovation isn't about big leaps—it's about smart iteration 🎯

Traditional approaches weren't scaling. We needed a fresh perspective.

Here's what we learned:

→ Rethink fundamentals before building
→ Build incrementally, not in one shot
→ Test relentlessly, fail fast

The Results:
✓ 10x efficiency improvement
✓ 85% cost reduction
✓ Team satisfaction soared

Innovation is a mindset, not a moment.

What's your approach to driving change?

#Innovation #Leadership #Strategy
```

### Instagram Caption Output
```
Innovation isn't about big leaps 🚀

It's about smart iteration, consistent effort, and learning from every step.

.
.
.
We transformed our approach and saw:
✓ 10x efficiency
✓ 85% cost savings
✓ Happier team

The secret? 
Think fundamentally. Build incrementally. Test relentlessly.

What's driving your innovation? Drop a comment 👇

#Innovation #BusinessGrowth #Entrepreneur #StartupLife #Leadership #Success #Mindset #Strategy #GrowthMindset #BusinessTips
```

---

## A/B Testing Variants

Generate 2-3 variants per platform with different:
- Hook approaches (question vs statement vs stat)
- CTA strategies (direct vs soft)
- Emoji usage (minimal vs moderate)

---

## Success Metrics

- Character limit compliance: 100%
- Hook engagement estimation accuracy: >70%
- Message consistency across platforms: >90%
- Processing time: <5 seconds per platform
- A/B variant generation: 2-3 variants per platform

---

**Created**: 2025-11-23  
**Owner**: Worker12 (Content Specialist)
