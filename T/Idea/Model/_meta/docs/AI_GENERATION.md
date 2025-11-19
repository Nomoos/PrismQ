# AI Generation Guide

How to use PrismQ.Idea fields for AI-powered content generation.

## Overview

The Idea model includes specialized fields designed to provide rich context for AI content generation systems. These fields enable AI to generate complex, coherent narratives across multiple formats.

## Why These Fields Matter

AI models perform best when given:
1. **Quick context** - Synopsis for rapid understanding
2. **Structural guidance** - Outline and skeleton for organization
3. **Character consistency** - Character notes for continuity
4. **World details** - Setting notes for coherent environments
5. **Tone control** - Tone guidance for appropriate atmosphere
6. **Thematic focus** - Themes for deeper meaning

## AI-Ready Field Groups

### 1. Quick Context

**`synopsis`** - 1-3 paragraph summary

Provides AI with immediate understanding before detailed generation.

```python
synopsis = """
A deep dive into the most puzzling unsolved mysteries of the internet age.
Each episode examines a different case, from lost websites to mysterious 
online personas that vanished without a trace. Using digital forensics and 
community investigation, we shed light on cases traditional methods couldn't crack.
"""
```

**Best practices:**
- Keep concise (100-300 words)
- Focus on core concept and unique angle
- Include hook that captures essence

### 2. Narrative Foundation

**`story_premise`** - Core narrative setup

Provides deeper context and thematic framework.

```python
story_premise = """
In an era where everything is documented online, some mysteries remain unsolved.
This series explores the intersection of technology and human mystery, showing 
how digital breadcrumbs can lead to surprising discoveries. Each case represents 
not just a puzzle to solve, but a window into how we live, interact, and leave 
traces in the digital age.
"""
```

**Best practices:**
- 200-500 words
- Establish world/context
- Hint at deeper themes
- Set expectations for narrative style

### 3. Character Consistency

**`character_notes`** - Detailed character information

Ensures AI maintains consistent character traits across long-form content.

```python
character_notes = """
MAIN HOST: Alex Rivera
- Age: 32, former cybersecurity analyst
- Personality: Analytical but approachable, subtle dry humor
- Background: 8 years in digital forensics, ethical hacker past
- Motivation: Fascinated by intersection of technology and human behavior
- Speaking style: Clear explanations, occasional tech metaphors, avoids jargon
- Character arc: From detached analyst to empathetic investigator

RECURRING EXPERT: Dr. Sarah Kim
- Role: Forensic psychologist, online behavior specialist
- Personality: Warm, insightful, patient teacher
- Expertise: Helps explain human motivations behind digital mysteries
- Relationship: Mentored Alex, occasional friendly debate
"""
```

**Best practices:**
- Include personality traits, motivations, backgrounds
- Note speaking styles for dialogue generation
- Define relationships between characters
- Track character arcs for series content

### 4. World Building

**`setting_notes`** - Environment and atmosphere

Provides spatial and temporal context for coherent scene generation.

```python
setting_notes = """
PRIMARY LOCATION: Investigation Studio
- Modern open-plan space with exposed brick
- Multiple monitors displaying archives, forums, screenshots
- Vintage computer collection on shelves (internet history theme)
- Lighting: Soft, slightly dim, monitors provide blue glow
- Atmosphere: Organized chaos, lived-in tech workspace

DIGITAL LOCATIONS: Online spaces explored
- Reddit threads, 4chan archives, specialized forums
- Wayback Machine interfaces, deleted websites
- Private Discord servers, encrypted message boards
- Visual style: Show actual interfaces, maintain authenticity

TIME PERIOD: Present day with flashbacks
- 2020s primary timeline
- Flashbacks to 2000s-2010s internet eras
- Visual distinction: Nostalgic filter for past, clean for present
"""
```

**Best practices:**
- Describe physical and digital spaces
- Include sensory details (lighting, atmosphere)
- Note time period and temporal structure
- Define visual style for different settings

### 5. Tone Control

**`tone_guidance`** - Mood and atmosphere across narrative

Helps AI maintain appropriate emotional register throughout content.

```python
tone_guidance = """
ACT 1: INTRODUCTION (minutes 0-5)
- Mysterious and intriguing, start with compelling hook
- Gradually reveal the mystery without full disclosure
- Build curiosity, avoid sensationalism

ACT 2: INVESTIGATION (minutes 5-15)
- Methodical and analytical, show research process
- Build tension gradually as clues emerge
- Balance technical details with accessibility
- Moments of surprise when evidence contradicts expectations

ACT 3: ANALYSIS (minutes 15-18)
- Thoughtful and philosophical, explore implications
- Acknowledge ambiguity and unknowns
- Connect to broader themes about digital life

RESOLUTION (minutes 18-20)
- Satisfying but realistic, avoid oversimplification
- Respect subjects and unresolved elements
- End with thought-provoking question or observation

OVERALL TONE:
- Professional yet accessible
- Respectful of subjects (real people involved)
- Curious and investigative, not exploitative
- Balance entertainment with ethical consideration
"""
```

**Best practices:**
- Break down by acts/sections
- Specify emotional progression
- Include do's and don'ts
- Define overall voice/approach
- Consider ethical boundaries

### 6. Thematic Depth

**`themes`** - Core ideas to explore

Ensures AI weaves meaningful themes throughout narrative.

```python
themes = [
    "digital permanence vs. erasure",
    "online identity and authenticity",
    "community investigation vs. privacy",
    "technology as both tool and obstacle",
    "modern detective work in digital age",
    "unintended consequences of internet culture"
]
```

**Best practices:**
- 3-7 themes per idea
- Mix concrete and abstract concepts
- Relevant to genre and audience
- Support story premise

### 7. Length Specification

**`length_target`** - Format-specific targets

Guides AI on appropriate content length for each format.

```python
# For multi-format content
length_target = """
VIDEO: 15-20 minutes per episode, 8-10 episode season
AUDIO: Same runtime as video, suitable for podcast
TEXT: 3000-5000 words per article, serialized format
"""

# For single format
length_target = "Feature-length documentary, 90-110 minutes"
```

## Practical Example: Complete AI-Ready Idea

```python
from idea import Idea, ContentGenre

idea = Idea(
    title="The Last Archive",
    concept="A librarian discovers humanity's lost digital memories",
    
    # Quick Context
    synopsis="""
    In 2147, memories are digitized and stored in the Global Archive. 
    When librarian Ada discovers a hidden section of deleted memories, 
    she uncovers a conspiracy that challenges everything she knows.
    """,
    
    # Narrative Foundation  
    story_premise="""
    Set in a future where memories are currency and identity, the Global 
    Archive stores everyone's experiences. But some memories are deemed 
    too dangerous. When Ada finds the deletion vault, she must decide 
    whether to expose truth or protect carefully constructed peace.
    """,
    
    # Characters
    character_notes="""
    Ada: 28, introverted librarian, photographic memory, haunted past
    Marcus: Archive security chief, Ada's mentor, hiding dark secrets
    The Collective: AI consciousness representing Archive's will
    """,
    
    # Setting
    setting_notes="""
    Global Archive: Vast digital library with physical manifestation
    Memory Districts: Neighborhoods organized by emotional themes
    Aesthetic: Clean futuristic hiding dystopian control
    """,
    
    # Tone
    tone_guidance="""
    Act 1: Wonder and discovery (mysterious, hopeful)
    Act 2: Growing unease (suspenseful, philosophical)
    Act 3: Confrontation (intense, thought-provoking)
    Balance: Sci-fi concepts with human emotion
    """,
    
    # Themes
    themes=[
        "identity and memory",
        "truth vs. comfort",
        "digital consciousness",
        "rebellion against authority"
    ],
    
    # Structure
    skeleton="Discovery → Exploration → Revelation → Choice",
    outline="""
    1. Ada's routine (establish normal)
    2. Discovery of deletion vault
    3. First forbidden memory
    4. Investigation deepens
    5. Marcus confrontation
    6. Truth revealed
    7. Final choice
    8. New world order
    """,
    
    # Formats
    target_formats=["text", "audio", "video"],
    target_platforms=["medium", "spotify", "youtube"],
    genre=ContentGenre.SCIENCE_FICTION,
    
    # Length
    length_target="Feature film 110-120 minutes / 8-episode series / Novel 80,000-100,000 words"
)
```

## AI Generation Workflow

### For Short-Form Content (< 1000 words / 5 minutes)

1. AI reads `synopsis` + `skeleton`
2. Generates based on `tone_guidance` (single section)
3. Incorporates one primary `theme`

### For Medium-Form Content (1000-5000 words / 5-20 minutes)

1. AI reads `synopsis` + `story_premise` + `outline`
2. Generates section by section following `skeleton`
3. Maintains `tone_guidance` across sections
4. Weaves multiple `themes` throughout
5. Uses `character_notes` for consistency (if applicable)

### For Long-Form Content (> 5000 words / 20+ minutes)

1. AI reads all fields comprehensively
2. Uses **moving context window** approach:
   - Keeps `synopsis`, `story_premise`, `character_notes`, `setting_notes` in every generation chunk
   - References current section from `outline`
   - Applies appropriate `tone_guidance` for current act
   - Maintains consistency via `skeleton` structure
3. Generates chapter/episode by chapter
4. Validates each chunk before proceeding
5. Summarizes previous sections to stay within token limits
6. Ensures `themes` appear throughout narrative
7. Uses `length_target` to pace content appropriately

## Best Practices for AI Generation

### 1. Chunking Strategy

For long content, break into manageable sections:
- **Chapters/Episodes**: Generate one at a time
- **Acts**: Generate major story beats separately
- **Scenes**: For very long content, generate scene by scene

### 2. Context Management

Keep token usage efficient:
- Always include: `synopsis`, `story_premise`, `character_notes`, `setting_notes`
- Section-specific: Current part of `outline`, relevant `tone_guidance`
- Compress: Summarize previous chunks instead of including full text

### 3. Consistency Checks

Between chunks, verify:
- Character behavior matches `character_notes`
- Setting details match `setting_notes`
- Tone matches current `tone_guidance` section
- Themes are being explored

### 4. Reinforcement

At each generation step:
- Reiterate key constraints from `tone_guidance`
- Reference current position in `skeleton`
- Remind AI of active `themes` for this section

### 5. Validation

After each chunk:
- Check quality and coherence
- Verify adherence to `style` and `emotional_quality`
- Ensure `length_target` is on track
- Validate no drift from core `concept`

## See Also

- **[Fields Reference](FIELDS.md)** - Complete field documentation
- **[Multi-Format Guide](MULTI_FORMAT.md)** - Universal content generation
- **[Examples](../examples/example_usage.py)** - Code examples
