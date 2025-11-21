# Summary and Translation Examples

Example usage of Idea summary generation and Czech translation features.

## Basic Summary Generation

```python
from T.Idea.Model.src import Idea, ContentGenre

# Create an idea
idea = Idea(
    title="The Future of Renewable Energy",
    concept="Exploring sustainable energy solutions for the 21st century",
    premise="As fossil fuels decline, renewable energy sources are becoming the dominant force in power generation",
    genre=ContentGenre.DOCUMENTARY,
    target_platforms=["youtube", "medium"],
    target_formats=["video", "text"]
)

# Generate summary
summary = idea.generate_summary()
print(summary)
```

Output:
```
Title: The Future of Renewable Energy
Concept: Exploring sustainable energy solutions for the 21st century
Premise: As fossil fuels decline, renewable energy sources are becoming the dominant force in power generation
Genre: documentary
Platforms: youtube, medium
Formats: video, text
```

## Summary with Maximum Length

```python
from T.Idea.Model.src import Idea, ContentGenre

# Create a detailed idea
idea = Idea(
    title="The Echo",
    concept="A psychological horror about hearing your own voice from the future",
    premise="A teenage girl starts hearing a voice that sounds identical to her own, giving warnings about the future",
    logline="A girl discovers she can hear her own future thoughts—and they're telling her to run",
    synopsis="An exploration of time paradoxes through intimate horror. The protagonist must determine if the voice is real or a manifestation of her fears, while the warnings become increasingly urgent and specific",
    genre=ContentGenre.HORROR,
    target_platforms=["youtube", "tiktok"],
    target_formats=["video", "audio"]
)

# Generate concise summary (max 200 characters)
short_summary = idea.generate_summary(max_length=200)
print(f"Short summary ({len(short_summary)} chars):\n{short_summary}")

# Generate longer summary (max 500 characters)
long_summary = idea.generate_summary(max_length=500)
print(f"\nLong summary ({len(long_summary)} chars):\n{long_summary}")
```

## Basic Czech Translation

```python
from T.Idea.Model.src import Idea, ContentGenre

# Create an idea
idea = Idea(
    title="Digital Privacy",
    concept="Protecting personal information in the digital age",
    genre=ContentGenre.EDUCATIONAL
)

# Translate summary to Czech
czech_summary = idea.translate_summary_to_czech()
print(czech_summary)
```

Output:
```
Název: Digital Privacy
Koncept: Protecting personal information in the digital age
Žánr: vzdělávací

[Poznámka: Pro produkční překlad použijte StoryTranslation model s AI překladačem]
```

## Complete Workflow: Generate → Translate

```python
from T.Idea.Model.src import Idea, ContentGenre

# Create a complete idea
idea = Idea(
    title="Blockchain Revolution",
    concept="How blockchain technology is transforming industries",
    premise="Blockchain offers transparent, decentralized solutions to age-old problems of trust and verification",
    logline="The technology that makes trust obsolete",
    synopsis="From cryptocurrencies to supply chains, blockchain is revolutionizing how we think about data, ownership, and trust in the digital age",
    genre=ContentGenre.TECHNOLOGY,
    target_platforms=["youtube", "medium", "linkedin"],
    target_formats=["video", "text", "audio"],
    length_target="15-20 minutes"
)

# Step 1: Generate English summary
english_summary = idea.generate_summary(max_length=400)
print("English Summary:")
print(english_summary)
print("\n" + "="*50 + "\n")

# Step 2: Translate to Czech
czech_summary = idea.translate_summary_to_czech(summary=english_summary)
print("Czech Summary:")
print(czech_summary)
```

## Translate Without Pre-Generation

```python
from T.Idea.Model.src import Idea, ContentGenre

# Create an idea
idea = Idea(
    title="Climate Action Now",
    concept="Urgent steps needed to address climate change",
    premise="With rising global temperatures, immediate action is required",
    genre=ContentGenre.DOCUMENTARY,
    target_platforms=["youtube"],
    target_formats=["video"]
)

# Translate directly (generates summary internally)
czech = idea.translate_summary_to_czech()
print(czech)
```

## Multiple Genres Translation

```python
from T.Idea.Model.src import Idea, ContentGenre

# Test different genre translations
genres = [
    (ContentGenre.HORROR, "horor"),
    (ContentGenre.EDUCATIONAL, "vzdělávací"),
    (ContentGenre.TECHNOLOGY, "technologie"),
    (ContentGenre.DOCUMENTARY, "dokumentární"),
    (ContentGenre.TRUE_CRIME, "skutečný zločin")
]

for genre, expected_czech in genres:
    idea = Idea(
        title="Test",
        concept="Test concept",
        genre=genre
    )
    
    czech = idea.translate_summary_to_czech()
    print(f"{genre.value} → {expected_czech}")
    assert expected_czech in czech
```

## Summary for Different Content Types

```python
from T.Idea.Model.src import Idea, ContentGenre

# YouTube Short
youtube_short = Idea(
    title="60 Second History Lesson",
    concept="Quick historical facts",
    premise="Learn history in bite-sized pieces",
    genre=ContentGenre.EDUCATIONAL,
    target_platforms=["youtube", "tiktok"],
    target_formats=["video"],
    length_target="60 seconds"
)

print("YouTube Short Summary:")
print(youtube_short.generate_summary(max_length=200))
print()

# Long-form Documentary
documentary = Idea(
    title="The Rise and Fall of Empires",
    concept="A comprehensive look at historical empires",
    premise="From Rome to the British Empire, explore the patterns of power",
    synopsis="This multi-part documentary series examines the life cycles of great empires throughout history",
    genre=ContentGenre.DOCUMENTARY,
    target_platforms=["youtube"],
    target_formats=["video"],
    length_target="45-60 minutes per episode"
)

print("Documentary Summary:")
print(documentary.generate_summary(max_length=500))
```

## Multi-Platform Idea Translation

```python
from T.Idea.Model.src import Idea, ContentGenre

# Create multi-platform idea
idea = Idea(
    title="Sustainable Living Tips",
    concept="Practical advice for eco-friendly lifestyle",
    premise="Small changes can make a big environmental impact",
    genre=ContentGenre.LIFESTYLE,
    target_platforms=["youtube", "tiktok", "instagram", "medium", "linkedin"],
    target_formats=["video", "text", "audio"],
    length_target="Variable: 60s for shorts, 10min for YouTube, 1500 words for articles"
)

# Generate and translate
summary = idea.generate_summary()
czech = idea.translate_summary_to_czech(summary)

print("Platform targeting:")
print(f"  Platforms: {', '.join(idea.target_platforms)}")
print(f"  Formats: {', '.join(idea.target_formats)}")
print(f"\nCzech version includes:")
print(f"  Platformy: {', '.join(idea.target_platforms)}")
print(f"  Formáty: {', '.join(idea.target_formats)}")
```

## Using with Story Translation Model

```python
from T.Idea.Model.src import Idea, ContentGenre
from T.Idea.Model.src.story_translation import StoryTranslation, TranslationStatus
from T.Idea.Model.src.idea_db import IdeaDatabase

# Create and save idea
idea = Idea(
    title="The Last Signal",
    concept="Sci-fi thriller about the last message from Earth",
    premise="After Earth goes silent, a deep space crew receives one final transmission",
    genre=ContentGenre.SCIENCE_FICTION,
    target_platforms=["youtube"],
    target_formats=["video", "audio"]
)

# Save to database
db = IdeaDatabase("stories.db")
db.connect()
story_id = db.insert_idea(idea.to_dict())

# Generate summary for translation reference
summary = idea.generate_summary()
print("English Summary:")
print(summary)

# Create proper translation using StoryTranslation model
# (This would use AI translation in production)
translation = StoryTranslation(
    story_id=story_id,
    language_code="cs",
    title="Poslední signál",
    text="Po tom, co Země zmlkla, posádka na hlubokém vesmíru obdrží jednu závěrečnou zprávu",
    translated_from="en",
    translator_id="AI-Translator",
    status=TranslationStatus.DRAFT
)

print("\nFormal Czech Translation:")
print(f"Title: {translation.title}")
print(f"Text: {translation.text}")

db.close()
```

## Summary Length Comparison

```python
from T.Idea.Model.src import Idea, ContentGenre

# Create detailed idea
idea = Idea(
    title="The Psychology of Decision Making",
    concept="Understanding how we make choices",
    premise="Our decisions are influenced by cognitive biases we're often unaware of",
    logline="The hidden forces that shape every choice we make",
    synopsis="A deep dive into behavioral economics and cognitive psychology, exploring how our brains process decisions, the role of emotions vs. logic, and practical strategies for better decision-making",
    genre=ContentGenre.EDUCATIONAL,
    target_platforms=["youtube", "medium"],
    target_formats=["video", "text"]
)

# Generate summaries of different lengths
lengths = [100, 200, 300, 500]
for length in lengths:
    summary = idea.generate_summary(max_length=length)
    print(f"\nSummary (max {length} chars): {len(summary)} chars")
    print(summary)
    print("-" * 50)
```
