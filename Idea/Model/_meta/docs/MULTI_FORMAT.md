# Multi-Format Content Guide

How to use PrismQ.Idea for universal content generation across text, audio, and video.

## Universal Content Philosophy

Each Idea in PrismQ is designed for **universal content generation**—the same core concept can be adapted and released simultaneously as:
- **Text** - Blog posts, articles, ebooks, social media
- **Audio** - Podcasts, audiobooks, audio essays
- **Video** - YouTube, TikTok, documentaries, courses

This approach maximizes reach and accommodates different audience preferences.

## Multi-Format Fields

### `target_platforms` (list)
List of platforms where content will be distributed.

```python
target_platforms = ["youtube", "spotify", "medium", "tiktok", "instagram"]
```

**Common platforms:**
- Video: `youtube`, `tiktok`, `instagram`, `vimeo`
- Audio: `spotify`, `apple_podcasts`, `audible`, `soundcloud`
- Text: `medium`, `substack`, `blog`, `twitter`, `linkedin`

### `target_formats` (list)
Output formats for the content.

```python
target_formats = ["text", "audio", "video"]
```

**Format types:**
- `text` - Written content
- `audio` - Audio-only content
- `video` - Visual content with or without audio

## Example: Universal Content Idea

```python
from idea import Idea, ContentGenre

idea = Idea(
    title="The Psychology of Procrastination",
    concept="Understanding why we delay and how to overcome it",
    synopsis="A science-based exploration of procrastination psychology",
    
    # Universal targeting
    target_platforms=["youtube", "spotify", "medium"],
    target_formats=["text", "audio", "video"],
    
    # Content structure works for all formats
    skeleton="Problem → Science → Solutions → Action Steps",
    outline="""
    1. Opening hook with relatable scenario
    2. What procrastination really is (science)
    3. Common misconceptions debunked
    4. Practical strategies that work
    5. Action plan for viewers/readers/listeners
    """,
    
    # Format-agnostic description
    genre=ContentGenre.EDUCATIONAL,
    keywords=["psychology", "productivity", "self-improvement"],
    themes=["behavioral science", "personal growth", "practical wisdom"],
    
    # Length specification for each format
    length_target="""
    VIDEO: 12-15 minutes (YouTube standard)
    AUDIO: Same content, 12-15 minutes (podcast format)
    TEXT: 2500-3000 words (Medium article / blog post)
    """
)
```

## Format Adaptation Strategies

### Text Format

**Strengths:**
- Detailed explanations
- Easy to reference and quote
- Searchable content
- Can include links and resources

**Adaptation:**
- Use subheadings from `outline`
- Expand concepts with detailed examples
- Include hyperlinks to sources
- Add pull quotes for visual interest
- Include infographics or diagrams

**Example structure:**
```
# Title
## Introduction (Hook from skeleton)
### Problem presentation
## Main Content (Science section)
### Key concept 1
### Key concept 2
## Solutions
### Strategy 1
### Strategy 2
## Conclusion (Action steps)
```

### Audio Format

**Strengths:**
- Passive consumption (commute, exercise)
- Personal, intimate tone
- Natural for storytelling
- Multi-tasking friendly

**Adaptation:**
- Conversational delivery of `concept`
- Use `tone_guidance` for vocal pacing
- Clear verbal transitions between `outline` sections
- Repeat key points for retention (audio has no rewind culture)
- Audio cues for section changes

**Script considerations:**
```python
# Audio-specific notes in tone_guidance
tone_guidance = """
Opening: Warm, conversational, like talking to a friend
Science section: Clear, patient, use analogies
Solutions: Energetic, empowering
Pacing: Moderate speed, brief pauses for emphasis
"""
```

### Video Format

**Strengths:**
- Visual demonstrations
- Engaging for visual learners
- High share potential
- Multiple retention mechanisms

**Adaptation:**
- Visual representation of `setting_notes`
- B-roll matches current `outline` section
- On-screen text for key points
- Graphics/animations for complex concepts
- Facial expressions convey `emotional_quality`

**Visual elements:**
```python
# Video-specific notes
setting_notes = """
Primary: Clean, professional home office setup
B-roll needs: 
- Relatable procrastination scenarios (watching phone)
- Brain diagrams for science sections
- Success montages for solutions
Visual style: Bright, modern, accessible
"""
```

## Content That Works Across Formats

### Story Structure

Use a universal narrative structure from `skeleton`:

```python
skeleton = "Hook → Context → Core Content → Application → Takeaway"
```

This structure works for:
- **Text**: Section headings
- **Audio**: Natural conversation flow
- **Video**: Scene progression

### Modular Content

Design `outline` with self-contained segments:

```python
outline = """
1. Hook (2 min / 300 words / standalone section)
2. Problem exploration (4 min / 800 words / standalone)
3. Solution framework (4 min / 800 words / standalone)
4. Implementation (3 min / 600 words / standalone)
5. Call to action (1 min / 200 words / standalone)
"""
```

Each section can be:
- Reordered for different platforms
- Shortened for short-form (TikTok)
- Expanded for long-form (blog)
- Combined or split as needed

### Platform-Specific Adjustments

While content core remains same, adjust for platform culture:

```python
# Same idea, different emphasis
idea = Idea(
    title="The Psychology of Procrastination",
    target_platforms=["youtube", "tiktok", "medium"],
    target_formats=["video", "text"],
    
    # Platform notes in metadata
    metadata={
        "youtube_approach": "12-min deep dive, educational style",
        "tiktok_approach": "60-sec hook + cliffhanger CTA to full video",
        "medium_approach": "2500-word article, research citations"
    }
)
```

## Multi-Format Production Workflow

### 1. Create Master Idea
Define complete idea with all AI generation fields filled.

### 2. Generate Master Script
Use AI generation with all fields to create comprehensive script/content.

### 3. Format-Specific Adaptation

**For Video:**
- Add visual directions
- Mark B-roll insertion points
- Note on-screen text
- Plan thumbnail/title optimization

**For Audio:**
- Convert to conversational script
- Add vocal direction notes
- Mark music/sound effect cues
- Plan intro/outro music

**For Text:**
- Add section headers
- Insert links and citations
- Plan visual break-up (pull quotes, images)
- Optimize for SEO (based on `keywords`)

### 4. Platform-Specific Optimization

**YouTube Video:**
- Timestamps in description (from `outline`)
- Thumbnail with key visual
- Title optimized for search
- Tags from `keywords`

**Podcast Audio:**
- Episode description with `synopsis`
- Show notes with key points
- Chapter markers (from `outline`)
- Transcript link

**Medium Article:**
- Compelling headline (from `title`)
- Subheadings (from `outline`)
- Featured image
- Tags from `keywords` and `themes`

## Example: True Crime Multi-Format

```python
idea = Idea(
    title="The Vanishing of TechnoMage",
    concept="The mysterious disappearance of an influential forum moderator",
    synopsis="""
    In 2010, TechnoMage—a beloved moderator on a popular tech forum—
    vanished without a trace. No final post, no goodbye, no explanation.
    A decade later, we investigate what happened.
    """,
    
    # Universal distribution
    target_platforms=["youtube", "spotify", "medium", "substack"],
    target_formats=["text", "audio", "video"],
    genre=ContentGenre.TRUE_CRIME,
    
    # Works across all formats
    skeleton="Mystery → Investigation → Clues → Theory → Status",
    outline="""
    1. Introduce TechnoMage and their influence (2 min / 400 words)
    2. The day they disappeared (3 min / 600 words)
    3. Community investigation efforts (4 min / 800 words)
    4. Key clues and red herrings (4 min / 800 words)
    5. Current theories (3 min / 600 words)
    6. Where the case stands today (2 min / 400 words)
    """,
    
    # Format-specific length targets
    length_target="""
    VIDEO: 18-minute documentary-style YouTube video
    AUDIO: Same 18-minute content as podcast episode
    TEXT: 3600-word investigative article for Medium/Substack
    SHORT: 60-second TikTok teaser covering just the hook
    """,
    
    # Rich context for all formats
    character_notes="TechnoMage: enigmatic, helpful, respected, private",
    setting_notes="Online forums of 2000s-2010s, digital detective work",
    tone_guidance="Mysterious but respectful, investigative not exploitative",
    themes=["online communities", "digital identity", "unsolved mysteries"]
)
```

**Output:**
- **YouTube**: 18-minute mini-documentary with forum screenshots, interviews
- **Podcast**: Same narration, audio-friendly pacing, sound design
- **Medium**: Long-form article with embedded images, forum quotes
- **TikTok**: 60-second teaser driving to full video

## Best Practices

### 1. Core Content Stays Same
The central narrative (from `concept`, `story_premise`, `synopsis`) remains consistent.

### 2. Format Plays to Strengths
- Video: Visual demonstrations, facial expressions
- Audio: Conversational tone, sound design
- Text: Detailed citations, links, formatted for skimming

### 3. Platform Respects Culture
- YouTube: Longer, in-depth
- TikTok: Quick hooks, entertainment-first
- Medium: Thoughtful, well-researched
- Spotify: Conversational, personal

### 4. Cross-Promotion
Each format promotes the others:
- Video description links to article
- Article embeds video
- Podcast mentions blog post
- All share same `keywords` for discovery

### 5. Repurposing
Use `outline` sections independently:
- Section 1 → Twitter thread
- Section 3 → Instagram carousel
- Section 5 → LinkedIn post
- Full content → Main platform

## See Also

- **[AI Generation Guide](AI_GENERATION.md)** - Using AI for content creation
- **[Fields Reference](FIELDS.md)** - Complete field documentation
- **[Quick Start](QUICK_START.md)** - Get started quickly
