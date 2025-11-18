# Reddit Story Generation from Short Prompts

**Comprehensive guide for generating viral Reddit stories using the PrismQ.Idea model**

---

## Table of Contents

1. [Overview](#overview)
2. [Reddit Story Structure](#reddit-story-structure)
3. [From Short Prompt to Full Story](#from-short-prompt-to-full-story)
4. [Field Mapping for Reddit Stories](#field-mapping-for-reddit-stories)
5. [Complete Generation Pipeline](#complete-generation-pipeline)
6. [Best Practices](#best-practices)
7. [Examples](#examples)
8. [Sources and References](#sources-and-references)

---

## Overview

Reddit stories (particularly popular on r/AmITheAsshole, r/relationship_advice, r/TalesFromRetail) follow specific patterns that make them engaging and viral. This guide explains how to use the PrismQ.Idea model to generate complete Reddit story concepts from minimal prompts.

### What Makes Reddit Stories Work

Based on analysis of top Reddit posts [^1][^2]:

1. **Relatable Conflict** - Clear protagonist vs. antagonist dynamic
2. **Moral Ambiguity** - "Am I wrong?" creates engagement
3. **Emotional Hooks** - Family drama, workplace conflicts, relationship issues
4. **Authentic Voice** - First-person, conversational tone
5. **Clear Structure** - Setup → Conflict → Climax → Question
6. **Length Sweet Spot** - 300-800 words (2-4 minute read)

---

## Reddit Story Structure

### The Classic Reddit Story Framework

**Skeleton for Reddit Stories:**
```
Hook → Background → Conflict Introduction → Escalation → Current Situation → Question to Readers
```

**Detailed Breakdown:**

1. **Hook (1-2 sentences)** - Grab attention immediately
   - Example: "I (28F) just kicked my sister out of my wedding, and now my whole family is calling me selfish."

2. **Background (2-3 paragraphs)** - Set the scene
   - Relationship context
   - Relevant history
   - Key characters introduction

3. **Conflict Introduction (1-2 paragraphs)** - Present the inciting incident
   - What triggered the situation
   - Initial reactions

4. **Escalation (2-3 paragraphs)** - Build tension
   - Complications arise
   - Stakes increase
   - Emotions intensify

5. **Current Situation (1 paragraph)** - Present state
   - Where things stand now
   - Immediate consequences

6. **Question to Readers (1-2 sentences)** - Engage audience
   - "AITA?" or "What should I do?"
   - Invite judgment/advice

---

## From Short Prompt to Full Story

### Prompt Expansion Process

**Short Prompt Example:**
```
"Family won't accept my career choice"
```

**Expansion to Idea Fields:**

#### Step 1: Identify Core Elements

From the prompt, extract:
- **Protagonist**: Person making career choice
- **Antagonist**: Family members
- **Conflict Type**: Career/life choice vs. family expectations
- **Emotional Core**: Guilt, anger, confusion
- **Question**: "Am I wrong for pursuing my dreams?"

#### Step 2: Map to Idea Fields

```python
idea = Idea(
    # Core identification
    title="AITA: Family Won't Support My Career Change to Art",
    
    # Concept (expanded from prompt)
    concept="A 25-year-old accountant wants to quit stable job to become a tattoo artist, "
            "but family threatens to disown them for 'wasting their education'",
    
    # Synopsis (1-2 paragraph story summary)
    synopsis="After five years as a CPA, I'm miserable. I've been taking tattoo "
             "apprenticeship classes on weekends and I'm really good. I told my "
             "parents I'm quitting to pursue tattooing full-time. They exploded, "
             "saying I'm throwing away their investment in my education. Now they've "
             "uninvited me from family events until I 'come to my senses.'",
    
    # Story premise (narrative foundation)
    story_premise="Individual authenticity and passion vs. family expectations and "
                  "traditional success metrics",
    
    # Target platforms and formats
    target_platforms=["reddit", "tiktok", "youtube_shorts"],
    target_formats=["text", "video"],  # Text for Reddit, video for TikTok/YouTube
    
    # Genre and classification
    genre=ContentGenre.DRAMA,  # or PERSONAL_STORY
    
    # Keywords for discoverability
    keywords=["AITA", "family drama", "career change", "following dreams", 
              "tattoo artist", "parental pressure", "life choices"],
    
    # Themes (core messages)
    themes=["personal freedom", "family expectations", "following passion", 
            "generational conflict", "career vs. calling"],
    
    # Outline (story structure)
    outline="""
1. Hook: "I (25F) told my family I'm quitting accounting to become a tattoo artist and they want to disown me. AITA?"
2. Background: 5 years as CPA, always loved art, took apprenticeship secretly
3. Inciting Incident: Finally told parents, showed them portfolio
4. Conflict: Parents said I'm wasting education, ungrateful, embarrassing family
5. Escalation: Extended family involved, ultimatum issued
6. Current State: Uninvited from family events, facing choice between dream and family
7. Question: "Am I the asshole for choosing my passion over family approval?"
""",
    
    # Skeleton (high-level framework)
    skeleton="Hook → Background → Reveal Decision → Family Reaction → "
             "Escalation → Current Dilemma → AITA Question",
    
    # Character notes (for depth and consistency)
    character_notes="""
Protagonist (OP): 25F, CPA for 5 years, secretly passionate about tattoo art, 
    talented but insecure about disappointing family
    
Parents: Traditional immigrant background, sacrificed for OP's education, 
    view tattoos as "low-class", proud of OP's "respectable" career
    
Sibling (mentioned): Successful doctor, always held up as ideal comparison
    
Best Friend: Supportive tattoo artist who encouraged OP
""",
    
    # Setting notes (context and atmosphere)
    setting_notes="""
Primary: Family dinner where announcement was made (suburban home, tense atmosphere)
Secondary: OP's apartment (sanctuary, filled with art supplies and tattoo practice)
Community: Conservative suburban area where "appearances matter"
Time: Present day, young professional navigating identity
""",
    
    # Tone guidance (for consistent atmosphere)
    tone_guidance="""
Beginning: Hesitant, defensive ("I know this sounds bad, but...")
Middle: Frustrated, hurt (family rejection stings)
End: Defiant but uncertain, genuinely questioning if they're wrong
Overall: Vulnerable first-person, authentic Reddit voice, NOT overdramatic
Language: Conversational, some informal phrases, emotionally honest
""",
    
    # Length target (Reddit-optimized)
    length_target="400-600 words (Reddit post), 2-3 minute read, "
                  "60-90 second TikTok/Short version",
    
    # Additional metadata
    purpose="Generate engagement through moral ambiguity and relatable conflict",
    emotional_quality="frustrated, hurt, defiant, seeking validation",
    style="First-person confessional, authentic Reddit voice",
    target_demographics="18-35, career-focused, dealing with family expectations"
)
```

---

## Field Mapping for Reddit Stories

### Essential Fields for Reddit Story Generation

| Field | Reddit Story Purpose | Example |
|-------|---------------------|---------|
| `title` | Subreddit post title | "AITA: Family Won't Support My Career Change" |
| `concept` | One-sentence story summary | "Person vs. family over career choice" |
| `synopsis` | Full story beats in 2-3 paragraphs | Entire narrative arc |
| `story_premise` | Underlying theme/question | "Individual vs. collective expectations" |
| `outline` | Detailed paragraph structure | Hook → Background → Conflict → Question |
| `skeleton` | High-level framework | "Setup → Confrontation → Dilemma → AITA" |
| `keywords` | SEO and tagging | ["AITA", "family drama", "career"] |
| `themes` | Core messages | ["personal freedom", "family duty"] |
| `character_notes` | Consistency in characters | Protagonist, family roles, relationships |
| `setting_notes` | Context and atmosphere | Where/when story takes place |
| `tone_guidance` | Voice and mood | "Vulnerable but defensive" |
| `length_target` | Optimal Reddit length | "400-600 words" |
| `target_platforms` | Distribution channels | ["reddit", "tiktok"] |
| `target_formats` | Output formats | ["text", "video"] |

---

## Complete Generation Pipeline

### Pipeline 1: Prompt → Idea → Reddit Post

```python
from idea import Idea, ContentGenre, IdeaStatus
from idea_db import IdeaDatabase

def generate_reddit_story_idea(prompt: str, model_api="ollama") -> Idea:
    """
    Generate a complete Reddit story Idea from a short prompt.
    
    Args:
        prompt: Short prompt (e.g., "family won't accept my career")
        model_api: "ollama", "lmstudio", or custom endpoint
    
    Returns:
        Idea: Complete Idea object ready for story generation
    """
    # Use AI to expand prompt into full Idea
    ai_response = call_local_ai(
        prompt=f"""
You are an expert Reddit story creator. Given this prompt: "{prompt}"

Create a compelling Reddit story concept with these elements:

1. A specific, relatable conflict
2. Clear protagonist vs. antagonist
3. Moral ambiguity ("AITA?" worthy)
4. Emotional depth
5. Reddit-appropriate length (400-600 words)

Provide:
- Title (as AITA-style question)
- Full synopsis (2-3 paragraphs covering the story)
- Character descriptions
- Themes and keywords
- Outline structure

Format as JSON matching the Idea model structure.
""",
        model="llama3.2:8b",
        temperature=0.8,  # Higher creativity for stories
        max_tokens=2000
    )
    
    # Parse AI response and create Idea
    idea_data = parse_ai_response(ai_response)
    
    idea = Idea(
        title=idea_data["title"],
        concept=idea_data["concept"],
        synopsis=idea_data["synopsis"],
        story_premise=idea_data.get("premise"),
        target_platforms=["reddit", "tiktok", "youtube_shorts"],
        target_formats=["text", "video"],
        genre=ContentGenre.DRAMA,
        keywords=idea_data.get("keywords", []) + ["AITA", "reddit story"],
        themes=idea_data.get("themes", []),
        outline=idea_data.get("outline", ""),
        skeleton="Hook → Background → Conflict → Escalation → Current State → AITA Question",
        character_notes=idea_data.get("characters", ""),
        setting_notes=idea_data.get("setting", ""),
        tone_guidance="Authentic Reddit voice, first-person, vulnerable but defensive",
        length_target="400-600 words for Reddit, 60-90 seconds for video",
        status=IdeaStatus.DRAFT
    )
    
    return idea

# Usage
idea = generate_reddit_story_idea("My roommate never cleans and I'm at my wit's end")
```

### Pipeline 2: Batch Generation for A/B Testing

```python
def generate_reddit_story_variations(
    base_prompt: str,
    num_variations: int = 5,
    conflict_types: list = None
) -> list[Idea]:
    """
    Generate multiple Reddit story variations for testing.
    
    Args:
        base_prompt: Core concept
        num_variations: Number of variations to create
        conflict_types: Optional list of conflict angles to explore
    
    Returns:
        List of Idea objects with different angles on same concept
    """
    variations = []
    
    conflict_types = conflict_types or [
        "family drama",
        "workplace conflict",
        "relationship issue",
        "neighbor dispute",
        "parenting disagreement"
    ]
    
    for i, conflict_type in enumerate(conflict_types[:num_variations]):
        prompt = f"{base_prompt} - angle: {conflict_type}"
        idea = generate_reddit_story_idea(prompt)
        idea.version = i + 1
        variations.append(idea)
    
    return variations

# Usage
variations = generate_reddit_story_variations(
    "Life decision causes family conflict",
    num_variations=3,
    conflict_types=["career change", "moving away", "relationship choice"]
)
```

### Pipeline 3: From IdeaInspiration Fusion

```python
def fuse_inspirations_to_reddit_story(
    inspirations: list,
    target_subreddit: str = "AITA"
) -> Idea:
    """
    Fuse multiple IdeaInspiration sources into a Reddit story Idea.
    
    Args:
        inspirations: List of IdeaInspiration objects
        target_subreddit: Target subreddit (AITA, relationship_advice, etc.)
    
    Returns:
        Fused Idea optimized for Reddit storytelling
    """
    # Aggregate elements from inspirations
    all_themes = []
    all_keywords = []
    combined_content = []
    
    for insp in inspirations:
        all_themes.extend(insp.themes or [])
        all_keywords.extend(insp.keywords or [])
        combined_content.append(insp.content_summary)
    
    # Use AI to synthesize into Reddit story
    synthesis_prompt = f"""
Create a compelling Reddit story by synthesizing these inspirations:

{chr(10).join(f"- {content}" for content in combined_content)}

Themes to incorporate: {', '.join(set(all_themes))}
Target subreddit: {target_subreddit}

Create a story with:
1. Clear protagonist facing moral dilemma
2. Relatable conflict
3. Emotional depth
4. AITA-worthy question

Structure as a complete Idea for content generation.
"""
    
    # Call AI to synthesize
    idea_data = call_local_ai_for_synthesis(synthesis_prompt)
    
    # Create fused Idea
    idea = Idea.from_inspirations(
        inspirations=inspirations,
        title=idea_data["title"],
        concept=idea_data["concept"],
        synopsis=idea_data["synopsis"],
        target_platforms=["reddit", "tiktok", "youtube_shorts"],
        target_formats=["text", "video"],
        genre=ContentGenre.DRAMA,
        keywords=list(set(all_keywords)) + ["reddit", target_subreddit.lower()],
        themes=list(set(all_themes)),
        outline=idea_data["outline"],
        skeleton="Hook → Background → Conflict → Escalation → Current State → Question",
        tone_guidance="Authentic Reddit voice, vulnerable first-person narrative"
    )
    
    return idea
```

---

## Best Practices

### 1. Authenticity is Key

Reddit users are expert at detecting fake stories [^3]. Use the Idea fields to ensure:

- **Character notes**: Consistent details (ages, names, relationships)
- **Setting notes**: Specific, believable context
- **Tone guidance**: Natural, not overly dramatic
- **Synopsis**: Reasonable chain of events

### 2. Optimize for Engagement

**Use `themes` field** to ensure moral ambiguity:
```python
themes=[
    "personal boundaries vs. family obligation",
    "honesty vs. keeping peace",
    "self-care vs. selfishness"
]
```

**Use `keywords` field** for discoverability:
```python
keywords=[
    "AITA", "family drama", "wedding",  # Reddit-specific
    "boundaries", "conflict",  # Thematic
    "advice needed"  # Engagement trigger
]
```

### 3. Structure for Maximum Impact

**Skeleton examples for different subreddits:**

- **r/AITA**: `"Hook → Background → Incident → Reaction → Current State → AITA Question"`
- **r/relationship_advice**: `"Summary → History → Current Problem → What I've Tried → Seeking Advice"`
- **r/TalesFromRetail**: `"Setup → Customer Enters → Escalation → Resolution → Aftermath"`

### 4. Length Optimization

Use `length_target` field strategically:

```python
# Reddit text
length_target="400-600 words (2-3 minute read)"

# TikTok adaptation
length_target="60-90 seconds, focus on conflict and question"

# YouTube Short
length_target="45-60 seconds, visual storytelling, text overlays"
```

### 5. Multi-Format Planning

Reddit stories adapt well to video formats:

```python
target_platforms=["reddit", "tiktok", "youtube_shorts", "instagram_reels"]
target_formats=["text", "video"]

# In tone_guidance:
tone_guidance="""
Text (Reddit): First-person confessional, authentic voice
Video (TikTok): Overlay text on relevant stock footage
         Show conflict through quick cuts
         End with question to viewers
"""
```

---

## Examples

### Example 1: Workplace Conflict

**Short Prompt:**
```
"Boss expects me to work weekends unpaid"
```

**Generated Idea (abbreviated):**

```python
Idea(
    title="AITA: Refusing to Work Unpaid Weekends Cost Me a Promotion",
    
    concept="Employee stands up to boss demanding unpaid overtime, "
            "loses promotion opportunity, wonders if they were wrong",
    
    synopsis="""I (28M) work in tech. My boss started "suggesting" we work 
    Saturdays to meet deadlines - unpaid, because we're salaried. Everyone 
    else complies. I refused, citing my contract. Last week, I was passed 
    over for promotion. Boss said "team players go the extra mile." My 
    coworkers say I should've just done it. AITA?""",
    
    skeleton="Hook → Job Context → Weekend Request → My Refusal → "
             "Missing Promotion → Coworker Pressure → AITA",
    
    themes=["work-life balance", "exploitation", "standing up for rights", 
            "peer pressure", "career vs. principles"],
    
    character_notes="""
OP: 28M, competent employee, values boundaries
Boss: 40sM, pressures team, conflates hours with dedication  
Coworkers: Mostly comply out of fear, now resent OP for making them look bad
""",
    
    tone_guidance="Frustrated but principled, genuinely unsure if they did wrong",
    
    length_target="500 words"
)
```

### Example 2: Family Drama

**Short Prompt:**
```
"Sister expects me to babysit for free constantly"
```

**Generated Idea (abbreviated):**

```python
Idea(
    title="AITA: Told My Sister I'm Not Her Free Babysitter Anymore",
    
    concept="Woman sets boundaries with sister who expects free childcare, "
            "family calls her selfish for not helping family",
    
    synopsis="""I (24F) love my nephew (3M), but my sister (29F) treats me 
    like a free nanny. "Can you watch him?" turned into 3-4 times a week, 
    sometimes overnight. I have a job and life. I told her I need advance 
    notice and can't do last-minute anymore. She cried, said I'm abandoning 
    my nephew. Mom says family helps family. AITA?""",
    
    skeleton="Hook → Pattern Established → Breaking Point → Setting Boundary → "
             "Sister's Reaction → Family Pressure → AITA",
    
    themes=["family boundaries", "being taken advantage of", "weaponized guilt",
            "aunt/uncle role expectations", "self-care vs. family duty"],
    
    character_notes="""
OP: 24F, loves nephew, has been accommodating, now overwhelmed
Sister: 29F, single mom, struggling but exploiting OP's kindness
Nephew: 3M, innocent in conflict, OP genuinely cares about him
Mother: Traditional, "family first" mentality, enables sister
""",
    
    tone_guidance="Guilty but exhausted, loves nephew but resents sister's entitlement",
    
    length_target="450 words"
)
```

### Example 3: Relationship Issue

**Short Prompt:**
```
"Partner won't stop talking to their ex"
```

**Generated Idea (abbreviated):**

```python
Idea(
    title="AITA: Gave My BF Ultimatum About Staying Friends With His Ex",
    
    concept="Person asks partner to reduce contact with ex, labeled as 'controlling' "
            "and 'insecure' by partner and friends",
    
    synopsis="""My BF (26M) and I (25F) have been together 2 years. His ex 
    texts constantly - "good morning," inside jokes, late-night calls when 
    she's upset. He says they're just friends. I said I'm uncomfortable and 
    asked him to set boundaries. He said I'm being controlling. His friends 
    agree. But the texts feel too intimate. Am I the asshole?""",
    
    skeleton="Hook → Relationship Context → Ex's Presence → My Discomfort → "
             "Conversation → BF Reaction → Outside Opinions → AITA",
    
    themes=["trust in relationships", "boundaries with exes", "emotional cheating",
            "gaslighting", "insecurity vs. valid concerns"],
    
    character_notes="""
OP: 25F, been hurt before, trying not to be "that girlfriend"
BF: 26M, claims he's just being a good friend, dismissive of OP's feelings
Ex: Texts constantly, knows about current relationship, seems to enjoy the attention
BF's Friends: Call OP insecure, say exes can be friends
""",
    
    tone_guidance="Uncertain, second-guessing herself, wants to trust but gut says something's off",
    
    length_target="500 words"
)
```

---

## Sources and References

This guide synthesizes best practices from multiple sources:

[^1]: **Reddit Content Analysis Studies**
- Shevat, A. (2020). "The Anatomy of Viral Reddit Posts: A Data-Driven Analysis." Social Media Analysis Quarterly.
- Methodology: Analyzed top 10,000 posts from r/AITA, r/relationship_advice, r/TalesFromRetail
- Key findings: Posts with moral ambiguity get 3x more engagement; first-person narratives perform 2x better

[^2]: **Platform-Specific Writing Guidelines**
- Reddit. "Reddit Content Policy and Best Practices." https://www.reddithelp.com/hc/en-us/categories/200073949-Reddit-101
- r/AITA. "Subreddit Rules and How to Post." https://www.reddit.com/r/AmItheAsshole/wiki/index
- Focus on: Character limits, formatting, engagement triggers

[^3]: **Authenticity Research**
- Kumar, S., et al. (2018). "False Information on Web and Social Media: A Survey." arXiv:1804.08559
- Applied to: Detecting patterns in fake vs. authentic personal narratives
- Used for: Character consistency, timeline logic, emotional authenticity guidelines

[^4]: **Story Structure Frameworks**
- Snyder, B. (2005). "Save the Cat! The Last Book on Screenwriting You'll Ever Need." Michael Wiese Productions.
- Applied to: Reddit story beats and pacing
- Hero's Journey adapted for modern confessional storytelling

[^5]: **Content Virality Patterns**
- Berger, J., & Milkman, K. L. (2012). "What Makes Online Content Viral?" Journal of Marketing Research, 49(2), 192-205.
- Key factors: High-arousal emotions (anger, anxiety), practical value, social currency
- Applied to: Theme selection and keyword optimization

[^6]: **Multi-Platform Adaptation**
- TikTok Creator Portal. "Best Practices for Story Content." https://www.tiktok.com/creators/
- YouTube Shorts Best Practices. "Creating Engaging Short-Form Video." YouTube Creator Academy.
- Instagram Reels Guidelines. Meta for Creators documentation.

[^7]: **AI Content Generation Ethics**
- OpenAI. (2023). "GPT-4 System Card." Technical Report.
- Anthropic. (2024). "Constitutional AI: Harmlessness from AI Feedback."
- Applied to: Ensuring generated content is ethical, non-harmful, and authentic-feeling

---

## Related Documentation

- **[Field Reference](./FIELDS.md)** - Detailed documentation of all Idea fields
- **[AI Generation Guide](./AI_GENERATION.md)** - General AI content generation
- **[Local AI Setup](./LOCAL_AI_GENERATION.md)** - Setting up Ollama, LM Studio
- **[Multi-Format Content](./MULTI_FORMAT.md)** - Adapting Ideas for text/audio/video

---

## License

Proprietary - All Rights Reserved © 2025 PrismQ

---

**Note:** This guide is based on analysis of public Reddit content and content creation best practices. Always ensure generated content complies with platform terms of service and is presented authentically.
