#!/usr/bin/env python
"""Example usage of PrismQ.IdeaInspiration.Classification package.

This script demonstrates how to use both the CategoryClassifier and StoryDetector
to classify short-form video content.
"""

from prismq.idea.classification import (
    CategoryClassifier,
    StoryDetector,
    PrimaryCategory
)


def main():
    """Demonstrate classification capabilities."""
    print("=" * 80)
    print("PrismQ.IdeaInspiration.Classification - Example Usage")
    print("=" * 80)
    print()
    
    # Initialize classifiers
    category_classifier = CategoryClassifier()
    story_detector = StoryDetector(confidence_threshold=0.3)
    
    # Example videos to classify
    videos = [
        {
            'title': 'My AITA Story - Was I Wrong?',
            'description': 'Let me tell you about what happened yesterday. This is my true story.',
            'tags': ['storytime', 'aita', 'confession', 'true story'],
        },
        {
            'title': 'Funniest Meme Compilation 2024',
            'description': 'Watch these hilarious memes that will make you laugh!',
            'tags': ['comedy', 'funny', 'memes', 'entertainment'],
        },
        {
            'title': 'How to Learn Python in 60 Seconds',
            'description': 'Quick tutorial on Python programming basics for beginners.',
            'tags': ['tutorial', 'education', 'programming', 'python'],
        },
        {
            'title': 'Get Ready With Me - Morning Routine',
            'description': 'Follow my morning routine and see how I get ready for the day.',
            'tags': ['vlog', 'grwm', 'lifestyle', 'morning routine'],
        },
        {
            'title': 'Fortnite Epic Victory Royale',
            'description': 'Watch this amazing gaming highlight and clutch moment!',
            'tags': ['gaming', 'fortnite', 'gameplay', 'victory'],
        },
        {
            'title': 'Trying the Viral TikTok Challenge',
            'description': 'This trending challenge is everywhere, let me try it!',
            'tags': ['challenge', 'trending', 'viral', 'tiktok'],
        },
        {
            'title': 'iPhone 15 Unboxing and Review',
            'description': 'My honest opinion and first impressions of the new iPhone.',
            'tags': ['review', 'unboxing', 'tech', 'iphone'],
        },
        {
            'title': 'ASMR Relaxation Sounds',
            'description': 'Satisfying ASMR sounds for relaxation and sleep.',
            'tags': ['asmr', 'relaxation', 'satisfying'],
        },
    ]
    
    print("📊 CATEGORY CLASSIFICATION")
    print("-" * 80)
    for i, video in enumerate(videos, 1):
        result = category_classifier.classify_from_metadata(video)
        
        print(f"\n{i}. {video['title']}")
        print(f"   Category: {result.category.value}")
        print(f"   Confidence: {result.confidence:.2%}")
        print(f"   Usable for stories: {'✓' if result.category.is_usable_for_stories else '✗'}")
        print(f"   Top indicators: {', '.join(result.indicators[:3])}")
    
    print()
    print("=" * 80)
    print()
    print("📖 STORY DETECTION")
    print("-" * 80)
    
    for i, video in enumerate(videos, 1):
        is_story, confidence, indicators = story_detector.detect_from_metadata(video)
        
        print(f"\n{i}. {video['title']}")
        print(f"   Is Story: {'✓ Yes' if is_story else '✗ No'}")
        print(f"   Confidence: {confidence:.2%}")
        if is_story:
            print(f"   Story indicators: {', '.join(indicators[:3])}")
    
    print()
    print("=" * 80)
    print()
    print("📈 CATEGORY DISTRIBUTION")
    print("-" * 80)
    
    # Count categories
    category_counts = {}
    for video in videos:
        result = category_classifier.classify_from_metadata(video)
        cat_name = result.category.value
        category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
    
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {category}: {count}")
    
    print()
    print("=" * 80)
    print()
    print("✅ All categories defined in taxonomy:")
    for category in PrimaryCategory:
        status = "✓" if category.is_usable_for_stories else "✗"
        print(f"   {status} {category.value}")
        print(f"      {category.description}")
        print()
    
    print("=" * 80)


if __name__ == "__main__":
    main()
