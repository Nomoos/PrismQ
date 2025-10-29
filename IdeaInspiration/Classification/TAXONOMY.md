# 📂 Content Taxonomy - Primary Categories

## Overview

This document describes the 8 primary content categories implemented in the PrismQ.IdeaInspiration.Classification package, optimized for short-form vertical video platforms (YouTube Shorts, TikTok, Instagram Reels, Facebook Reels).

## Design Goals

✅ **Broad and platform-agnostic** - Works across all short-form video platforms  
✅ **Covers all major content types** - Comprehensive taxonomy  
✅ **Single Unusable category** - Clear distinction for story generation relevance  
✅ **Local processing** - No external API calls, zero cost  
✅ **High accuracy** - Weighted keyword analysis with confidence scoring  

## Primary Categories

### 1. 📖 Storytelling
**Purpose**: Usable for story generation  
**Description**: Narratives, fictional or real  

**Examples**:
- Storytime videos
- POV (Point of View) content
- Creepypasta readings
- Confessional content
- True stories
- AITA (Am I The A-hole) stories
- TIFU (Today I F'd Up) stories
- Relationship stories
- Personal experiences

**Keywords**: story, storytime, narrative, aita, tifu, confession, pov, true story

---

### 2. 🎭 Entertainment
**Purpose**: Usable for story generation  
**Description**: Quick fun content - memes, comedy, pranks, fails, reactions, edits  

**Examples**:
- Meme compilations
- Comedy skits
- Pranks
- Fail compilations
- Reaction videos
- Roasts
- Parodies
- Funny moments

**Keywords**: meme, comedy, funny, prank, fail, reaction, roast, hilarious

---

### 3. 📚 Education / Informational
**Purpose**: Partially usable (depends on topic)  
**Description**: Explainers, tutorials, facts, productivity hacks, news bites  

**Examples**:
- Tutorials (how-to videos)
- Educational explainers
- Science facts
- Historical information
- Productivity tips
- Life hacks
- Study guides
- Quick lessons

**Keywords**: tutorial, how to, explained, learn, education, tips, tricks, facts

---

### 4. 🌟 Lifestyle / Vlog
**Purpose**: Usable for realism-based inspiration  
**Description**: Daily life, beauty, fashion, fitness, food, travel  

**Examples**:
- Daily vlogs
- Get Ready With Me (GRWM)
- Morning/night routines
- Beauty tutorials
- Fashion lookbooks
- Workout videos
- Recipe videos
- Travel content
- Lifestyle content

**Keywords**: vlog, daily life, grwm, routine, beauty, fashion, fitness, travel

---

### 5. 🎮 Gaming
**Purpose**: Sometimes usable  
**Description**: Gameplay clips, highlights, speedruns, walkthroughs  

**Examples**:
- Gameplay highlights
- Gaming montages
- Speedruns
- Let's Play clips
- Boss fight videos
- Clutch moments
- Walkthroughs
- Game reviews

**Keywords**: gameplay, gaming, speedrun, highlights, fortnite, minecraft

---

### 6. 🏆 Challenges & Trends
**Purpose**: Sometimes usable (seed for inspiration)  
**Description**: Social challenges, trending sounds, AR effects  

**Examples**:
- TikTok challenges
- Dance challenges
- Trending content
- Viral trends
- AR filter effects
- Duets
- Challenge accepted videos

**Keywords**: challenge, trend, trending, viral, tiktok challenge

---

### 7. 💬 Reviews & Commentary
**Purpose**: Sometimes usable (realistic POV inspiration)  
**Description**: Product reviews, reactions, opinion commentary  

**Examples**:
- Product reviews
- Unboxing videos
- First impressions
- Opinion pieces
- Commentary videos
- Analysis content
- Critique videos
- Rating videos

**Keywords**: review, unboxing, opinion, commentary, thoughts on, rating

---

### 8. ❌ Unusable
**Purpose**: NOT useful for story generation  
**Description**: Catch-all for content not relevant to story generation  

**Sub-categories**:

#### 🎵 Music & Performance
- Lip sync videos
- Cover songs
- Dance performances
- Music videos
- Singing content

#### 🎧 ASMR / Relaxation
- ASMR videos
- Satisfying loops
- Relaxation content
- Slime videos
- Whisper content

#### 📢 Promotional / Branded
- Advertisements
- Sponsored content
- Brand promotions
- Product launches
- Collaborations

#### 🐾 Pets & Animals
- Cute pet videos
- Animal tricks
- Pet compilations
- Wildlife content

#### ⚽ Sports & Highlights
- Sports clips
- Game highlights
- Training videos
- Match footage
- Goal compilations

#### 📰 News & Current Events
- Breaking news
- Political content
- Election coverage
- Current events
- News updates

#### 🎨 Memes & Edits (Non-story)
- Pure meme formats
- Audio remixes
- Video edits (non-narrative)

**Keywords**: music, asmr, sponsored, pet, sports, news, politics

---

## Usage

### Quick Classification

```python
from prismq.idea.classification import CategoryClassifier, PrimaryCategory

classifier = CategoryClassifier()
result = classifier.classify(
    title="My AITA Story - Was I Wrong?",
    description="Let me tell you what happened...",
    tags=['storytime', 'aita']
)

print(f"Category: {result.category.value}")
print(f"Usable: {result.category.is_usable_for_stories}")
print(f"Confidence: {result.confidence:.2%}")
```

### Check if Category is Usable

```python
if result.category.is_usable_for_stories:
    print("✓ This content can be used for story generation")
else:
    print("✗ This content is not suitable for story generation")
```

### Get Category Description

```python
for category in PrimaryCategory:
    print(f"{category.value}:")
    print(f"  {category.description}")
    print(f"  Usable: {category.is_usable_for_stories}")
```

## Confidence Scoring

The classifier provides a confidence score (0.0 to 1.0) based on:

- **Title matches** (1.5x weight) - Strongest signal
- **Tag matches** (1.2x weight) - Strong signal  
- **Description matches** (1.0x weight) - Medium signal
- **Subtitle matches** (0.8x weight) - Weak signal

Higher confidence indicates stronger category match.

## Secondary Matches

The classifier also returns secondary category matches, showing content that spans multiple categories:

```python
result = classifier.classify(...)
print(f"Primary: {result.category.value}")
print(f"Secondary matches: {result.secondary_matches}")
```

## Implementation Notes

- **100% local processing** - No external API calls
- **Zero external costs** - No AI service fees
- **Platform-agnostic** - Works with any content metadata
- **Minimal requirements** - Only needs title, description, tags, subtitles
- **High performance** - Pure Python, optimized for speed
- **Well tested** - 48 comprehensive tests

## Version

Current taxonomy version: **2.0.0**  
Last updated: October 2025

## References

- Problem Statement: See issue describing taxonomy requirements
- Implementation: `prismq/idea/classification/category_classifier.py`
- Tests: `tests/test_category_classifier.py`
- Example: `example.py`
