# Field Reference

Complete reference for all Idea model fields.

## Core Identity

### `title` (str, required)
Clear, compelling title for the idea.

**Example:** `"Digital Detectives: Internet Cold Cases"`

### `concept` (str, required)
Core concept or hook—what the content is about.

**Example:** `"Using modern forensics to solve internet mysteries"`

### `purpose` (str, optional)
Problem solved or value provided to audience.

**Example:** `"Engage true crime audience with unique digital angle"`

## Content Description

### `synopsis` (str, optional)
Short summary (1-3 paragraphs) for quick context. Useful for AI generation.

**Example:**
```python
synopsis = """
A deep dive into the most puzzling unsolved mysteries of the internet age.
Each episode examines a different case, from lost websites to mysterious 
online personas that vanished without a trace.
"""
```

### `story_premise` (str, optional)
Core narrative foundation. Provides deeper context than synopsis.

**Example:**
```python
story_premise = """
In an era where everything is documented online, some mysteries remain unsolved.
This series explores how digital forensics, community investigation, and modern
technology can shed light on cases that traditional methods couldn't crack.
"""
```

### `emotional_quality` (str, optional)
Emotional tone and impact of the content.

**Example:** `"mysterious, suspenseful, intriguing, thought-provoking"`

### `style` (str, optional)
Content style or approach.

**Example:** `"narrative investigation with documentary elements"`

## Target Audience

### `target_audience` (str, optional)
Intended audience description.

**Example:** `"True crime enthusiasts aged 18-35, tech-savvy"`

### `target_demographics` (dict, optional)
Detailed demographic targeting data.

**Example:**
```python
target_demographics = {
    "age_range": "18-35",
    "interests": "true_crime,technology,investigation",
    "regions": "US,UK,CA,AU",
    "education": "college+"
}
```

## Distribution

### `target_platforms` (list[str], required)
List of target platforms. Supports universal multi-platform distribution.

**Example:** `["youtube", "spotify", "medium", "tiktok"]`

**Common values:** `youtube`, `tiktok`, `spotify`, `podcast`, `blog`, `medium`, `instagram`, `twitter`

### `target_formats` (list[str], required)
List of output formats for universal content generation.

**Example:** `["text", "audio", "video"]`

**Values:**
- `text` - Blog posts, articles, ebooks
- `audio` - Podcasts, audiobooks
- `video` - YouTube, TikTok, documentaries

### `genre` (ContentGenre, required)
Content genre classification.

**Available genres:**
- `ContentGenre.TRUE_CRIME`
- `ContentGenre.MYSTERY`
- `ContentGenre.HORROR`
- `ContentGenre.SCIENCE_FICTION`
- `ContentGenre.DOCUMENTARY`
- `ContentGenre.EDUCATIONAL`
- `ContentGenre.ENTERTAINMENT`
- `ContentGenre.LIFESTYLE`
- `ContentGenre.TECHNOLOGY`
- `ContentGenre.OTHER`

## Content Structure

### `keywords` (list[str], optional)
Tags/keywords for categorization and search. Auto-aggregated from inspirations.

**Example:** `["mystery", "unsolved", "internet", "investigation", "digital"]`

### `themes` (list[str], optional)
Core thematic elements to explore. Auto-aggregated from inspirations.

**Example:** `["digital privacy", "online identity", "modern detective work", "technology ethics"]`

### `outline` (str, optional)
Structured content outline or section breakdown.

**Example:**
```python
outline = """
1. Hook - Present the mystery
2. Case Introduction - Background and context
3. Investigation - Evidence and analysis
4. Theory - Possible explanations
5. Conclusion - Current status and takeaways
"""
```

### `skeleton` (str, optional)
High-level structural framework or template.

**Example:** `"Mystery → Evidence → Analysis → Resolution"`

**Common patterns:**
- YouTube: `"Hook → Intro → Body → CTA → Outro"`
- Three-act: `"Setup → Confrontation → Resolution"`
- Educational: `"Intro → Theory → Practice → Challenge"`

## AI Generation Fields

### `character_notes` (str, optional)
Character descriptions, roles, and relationships. Helps AI maintain consistency.

**Example:**
```python
character_notes = """
Host: Alex Rivera, 32, former cybersecurity analyst turned investigator
- Background in digital forensics and ethical hacking
- Calm, analytical demeanor with subtle humor
- Passionate about internet history and digital rights

Recurring Expert: Dr. Sarah Kim, forensic psychologist specializing in online behavior
"""
```

### `setting_notes` (str, optional)
Setting, world-building, and environmental details.

**Example:**
```python
setting_notes = """
Primary: Modern investigation studio with multiple monitors displaying archives
Secondary: Various online communities and forums (Reddit, 4chan, specialized sites)
Atmosphere: Clean, tech-focused aesthetic with undertones of mystery
Era: Present day with flashbacks to internet eras (2000s-2010s)
"""
```

### `tone_guidance` (str, optional)
Detailed guidance on tone, mood, and atmosphere across story arcs.

**Example:**
```python
tone_guidance = """
Opening: Mysterious and intriguing, hook with unsettling detail
Investigation: Suspenseful but methodical, build tension gradually
Analysis: Thoughtful and analytical, explain complex concepts clearly
Resolution: Satisfying but realistic, acknowledge unknowns
Overall: Balance intrigue with respect for subjects, avoid sensationalism
"""
```

### `length_target` (str, optional)
Target length specification for all formats.

**Example:** `"15-20 minute episodes / 3000-5000 word articles / 8-10 episode season"`

## Relationships

### `inspiration_ids` (list[str], optional)
List of linked IdeaInspiration source IDs. Tracks M:N relationship.

**Example:** `["insp-123", "insp-456", "insp-789"]`

**Note:** Empty list `[]` for standalone ideas created without inspirations.

## Workflow

### `version` (int, default: 1)
Version number for iteration tracking. Auto-incremented by `create_new_version()`.

### `status` (IdeaStatus, default: DRAFT)
Current workflow status.

**Available statuses:**
- `IdeaStatus.DRAFT` - Initial concept
- `IdeaStatus.VALIDATED` - Reviewed and validated
- `IdeaStatus.APPROVED` - Approved for production
- `IdeaStatus.IN_PRODUCTION` - Being developed into content
- `IdeaStatus.ARCHIVED` - No longer active

### `notes` (str, optional)
Development notes, feedback, or internal comments.

### `created_by` (str, optional)
Creator identifier for accountability.

**Example:** `"AI-Agent-001"` or `"user@example.com"`

## Scoring

### `potential_scores` (dict, optional)
Potential scores for different contexts (platform, region, demographic).

**Example:**
```python
potential_scores = {
    "platform:youtube": 85,
    "platform:tiktok": 72,
    "platform:podcast": 90,
    "region:us": 88,
    "region:uk": 82,
    "region:ca": 85,
    "age:18-24": 75,
    "age:25-34": 92,
    "age:35-44": 78,
    "language:english": 95
}
```

## Metadata

### `metadata` (dict, optional)
Additional custom metadata.

**Example:**
```python
metadata = {
    "production_budget": "medium",
    "research_required": "high",
    "collaboration_needed": ["researcher", "animator"],
    "custom_tags": ["series_potential", "viral_candidate"]
}
```

## Timestamps

### `created_at` (str, auto)
ISO 8601 timestamp of creation. Auto-generated.

### `updated_at` (str, auto)
ISO 8601 timestamp of last update. Auto-updated on modification.

## See Also

- **[Quick Start](QUICK_START.md)** - Get started quickly
- **[AI Generation](AI_GENERATION.md)** - Using AI fields effectively
- **[Database Guide](DATABASE.md)** - Storing and querying ideas
