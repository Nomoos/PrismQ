#!/usr/bin/env python
"""Example usage of generalized text classification with IdeaInspiration.

This script demonstrates the new IdeaInspiration model, Extract and Builder patterns,
and the TextClassifier for generalized content classification across text, video, and audio.
"""

from prismq.idea.classification import (
    IdeaInspiration,
    IdeaInspirationExtractor,
    IdeaInspirationBuilder,
    TextClassifier,
    CategoryClassifier,
    StoryDetector
)


def main():
    """Demonstrate generalized text classification capabilities."""
    print("=" * 80)
    print("PrismQ.IdeaInspiration.Classification - Generalized Text Classification")
    print("=" * 80)
    print()
    
    # Initialize components
    extractor = IdeaInspirationExtractor()
    builder = IdeaInspirationBuilder()
    text_classifier = TextClassifier()
    
    print("📝 EXAMPLE 1: Extract from Text Content")
    print("-" * 80)
    
    text_inspiration = extractor.extract_from_text(
        title="How to Build Better Software",
        description="A comprehensive guide to software development best practices",
        body="Software development requires careful planning, testing, and iteration...",
        tags=["tutorial", "programming", "software"]
    )
    
    print(f"Title: {text_inspiration.title}")
    print(f"Source Type: {text_inspiration.source_type}")
    print(f"Keywords: {text_inspiration.keywords}")
    print(f"Has Content: {text_inspiration.has_content}")
    print()
    
    print("🎥 EXAMPLE 2: Extract from Video with Subtitles")
    print("-" * 80)
    
    video_inspiration = extractor.extract_from_video(
        title="My True Story - AITA for Telling the Truth?",
        description="This is my personal experience and I need your opinion",
        subtitle_text="So let me tell you what happened last week. I was at a family dinner...",
        tags=["story", "aita", "confession", "drama"]
    )
    
    print(f"Title: {video_inspiration.title}")
    print(f"Source Type: {video_inspiration.source_type}")
    print(f"Keywords: {video_inspiration.keywords}")
    print(f"Content Preview: {video_inspiration.content[:50]}...")
    print()
    
    print("🎧 EXAMPLE 3: Extract from Audio with Transcription")
    print("-" * 80)
    
    audio_inspiration = extractor.extract_from_audio(
        title="Episode 42: The Future of AI",
        description="In this episode, we discuss artificial intelligence trends",
        transcription="Welcome to the podcast. Today we're talking about AI and machine learning...",
        tags=["podcast", "ai", "technology"]
    )
    
    print(f"Title: {audio_inspiration.title}")
    print(f"Source Type: {audio_inspiration.source_type}")
    print(f"Keywords: {audio_inspiration.keywords}")
    print()
    
    print("🏗️  EXAMPLE 4: Build IdeaInspiration with Builder Pattern")
    print("-" * 80)
    
    built_inspiration = (builder
        .set_title("Epic Gaming Montage")
        .set_description("Best moments from today's stream")
        .set_content("Here's a compilation of epic gameplay highlights...")
        .add_keyword("gaming")
        .add_keyword("highlights")
        .add_keyword("fortnite")
        .set_source_type("video")
        .add_metadata("platform", "youtube")
        .extract_keywords_from_content(max_keywords=5, merge_with_existing=True)
        .build())
    
    print(f"Title: {built_inspiration.title}")
    print(f"Keywords: {built_inspiration.keywords}")
    print(f"Metadata: {built_inspiration.metadata}")
    print()
    
    print("🔍 EXAMPLE 5: Classify with TextClassifier")
    print("-" * 80)
    
    inspirations = [text_inspiration, video_inspiration, audio_inspiration, built_inspiration]
    
    for i, inspiration in enumerate(inspirations, 1):
        result = text_classifier.classify(inspiration)
        
        print(f"\n{i}. {inspiration.title}")
        print(f"   Category: {result.category.value}")
        print(f"   Is Story: {'✓ Yes' if result.is_story else '✗ No'}")
        print(f"   Story Confidence: {result.story_confidence:.2%}")
        print(f"   Combined Score: {result.combined_score:.2%}")
        print(f"   Field Scores:")
        for field, score in result.field_scores.items():
            print(f"      - {field}: {score:.2f}")
    
    print()
    print("=" * 80)
    print()
    print("📊 EXAMPLE 6: Batch Classification")
    print("-" * 80)
    
    # Create multiple inspirations from metadata
    metadata_batch = [
        {
            'title': 'Funny Cat Video Compilation',
            'description': 'Hilarious cats doing silly things',
            'subtitle_text': 'Watch these cats be adorable and funny',
            'tags': ['funny', 'comedy', 'cats']
        },
        {
            'title': 'Morning Routine - Get Ready With Me',
            'description': 'My daily morning routine for a productive day',
            'subtitle_text': 'First I wake up at 6am, then I...',
            'tags': ['vlog', 'grwm', 'lifestyle']
        },
        {
            'title': 'Viral Dance Challenge',
            'description': 'Trying the latest trending dance',
            'subtitle_text': 'Here we go with the dance challenge',
            'tags': ['challenge', 'trending', 'dance']
        }
    ]
    
    batch_inspirations = [extractor.extract_from_metadata(m) for m in metadata_batch]
    batch_results = text_classifier.classify_batch(batch_inspirations)
    
    print(f"\nClassified {len(batch_results)} items:")
    for insp, result in zip(batch_inspirations, batch_results):
        print(f"  • {insp.title[:50]:<50} → {result.category.value}")
    
    print()
    print("=" * 80)
    print()
    print("✅ EXAMPLE 7: Direct Field Classification")
    print("-" * 80)
    
    # Classify text fields directly without creating IdeaInspiration
    result = text_classifier.classify_text_fields(
        title="Tutorial: Python for Beginners",
        description="Learn Python programming from scratch",
        content="In this tutorial we'll cover variables, loops, and functions...",
        keywords=["tutorial", "python", "education", "programming"]
    )
    
    print(f"Category: {result.category.value}")
    print(f"Is Story: {result.is_story}")
    print(f"Combined Score: {result.combined_score:.2%}")
    
    print()
    print("=" * 80)
    print()
    print("🔄 EXAMPLE 8: Convert IdeaInspiration to/from Dictionary")
    print("-" * 80)
    
    # Create inspiration
    original = IdeaInspiration(
        title="Test Content",
        description="Test description",
        keywords=["test", "example"]
    )
    
    # Convert to dict
    data_dict = original.to_dict()
    print(f"Dictionary keys: {list(data_dict.keys())}")
    
    # Convert back from dict
    restored = IdeaInspiration.from_dict(data_dict)
    print(f"Restored title: {restored.title}")
    print(f"Restored keywords: {restored.keywords}")
    
    print()
    print("=" * 80)
    print()
    print("✨ All examples completed successfully!")
    print()


if __name__ == "__main__":
    main()
