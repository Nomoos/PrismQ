#!/usr/bin/env python3
"""Demonstration of batch processing capabilities for Scoring and Classification.

⚠️ NOTE: This script is archived and was originally located in the repository root.
Path references have been updated for the archived location.

This script demonstrates the complete workflow:
1. Create a list of IdeaInspiration objects
2. Process through Classification to get categories
3. Process through Scoring to get scores
4. Display results
"""

import sys
from pathlib import Path

# Add paths - updated for archived location (was in repo root, now in _meta/docs/archive/validation/)
repo_root = Path(__file__).parent.parent.parent.parent.parent
model_dir = repo_root / 'Model'
scoring_src = repo_root / 'Scoring' / 'src'
classification_src = repo_root / 'Classification' / 'src'

sys.path.insert(0, str(model_dir))
sys.path.insert(0, str(repo_root / 'Scoring'))
sys.path.insert(0, str(repo_root / 'Classification'))

from idea_inspiration import IdeaInspiration, ContentType

# Import directly from source
sys.path.insert(0, str(scoring_src))
sys.path.insert(0, str(classification_src))

from scoring import ScoringEngine
from classification import TextClassifier


def create_sample_data():
    """Create sample IdeaInspiration objects for demonstration."""
    return [
        IdeaInspiration(
            title="My AITA Story - Was I Wrong About This?",
            description="Let me tell you about what happened at work yesterday...",
            content="""
            So I was in a meeting and my colleague said something that really bothered me.
            I decided to speak up and now everyone is upset. Was I the one in the wrong?
            This has been on my mind and I need to know if I should apologize.
            """,
            keywords=["aita", "workplace", "story", "confession"],
            source_type=ContentType.TEXT,
            source_platform="reddit"
        ),
        IdeaInspiration(
            title="Funny Cat Compilation 2024 - Best Moments",
            description="The funniest cat fails and moments from this year",
            content="Watch as these adorable cats get into hilarious situations...",
            keywords=["funny", "cats", "compilation", "meme"],
            source_type=ContentType.VIDEO,
            source_platform="youtube",
            metadata={
                'statistics': {
                    'viewCount': '250000',
                    'likeCount': '12000',
                    'commentCount': '350'
                }
            }
        ),
        IdeaInspiration(
            title="How to Build Your First PC - Complete Tutorial",
            description="Step-by-step guide for beginners building a gaming PC",
            content="""
            In this comprehensive tutorial, we'll walk through every step of building
            your first gaming PC. We'll cover component selection, assembly, cable
            management, and troubleshooting common issues.
            """,
            keywords=["tutorial", "pc building", "gaming", "tech", "how-to"],
            source_type=ContentType.VIDEO,
            source_platform="youtube",
            metadata={
                'statistics': {
                    'viewCount': '500000',
                    'likeCount': '35000',
                    'commentCount': '1200'
                }
            }
        ),
        IdeaInspiration(
            title="My Morning Routine as a Content Creator",
            description="Follow me through a typical day in my life",
            content="Good morning! Let me show you how I start my day as a YouTuber...",
            keywords=["vlog", "morning routine", "lifestyle", "daily life"],
            source_type=ContentType.VIDEO,
            source_platform="youtube"
        ),
        IdeaInspiration(
            title="Epic Fortnite Clutch Moments - Season 5",
            description="Insane last-second victories and gameplay highlights",
            content="Check out these incredible clutch moments from competitive Fortnite...",
            keywords=["gaming", "fortnite", "highlights", "clutch"],
            source_type=ContentType.VIDEO,
            source_platform="youtube",
            metadata={
                'statistics': {
                    'viewCount': '150000',
                    'likeCount': '8000',
                    'commentCount': '200'
                }
            }
        )
    ]


def main():
    """Main demonstration function."""
    print("=" * 80)
    print("PrismQ.IdeaInspiration - Batch Processing Demonstration")
    print("=" * 80)
    print()
    
    # Create sample data
    print("Step 1: Creating sample IdeaInspiration objects...")
    ideas = create_sample_data()
    print(f"  ✓ Created {len(ideas)} IdeaInspiration objects")
    print()
    
    # Step 2: Classification
    print("Step 2: Classifying content...")
    classifier = TextClassifier()
    enrichments = classifier.enrich_batch(ideas)
    
    # Update ideas with classifications
    for idea, enrichment in zip(ideas, enrichments):
        idea.category = enrichment.category.value
        for tag in enrichment.tags:
            idea.subcategory_relevance[tag] = int(enrichment.category_confidence * 100)
    
    print(f"  ✓ Classified {len(enrichments)} items")
    print()
    
    # Step 3: Scoring
    print("Step 3: Scoring content...")
    engine = ScoringEngine()
    score_breakdowns = engine.score_idea_inspiration_batch(ideas)
    
    # Update ideas with scores
    for idea, breakdown in zip(ideas, score_breakdowns):
        idea.score = int(breakdown.overall_score)
    
    print(f"  ✓ Scored {len(score_breakdowns)} items")
    print()
    
    # Step 4: Display results
    print("Step 4: Results Summary")
    print("-" * 80)
    print()
    
    for i, idea in enumerate(ideas, 1):
        print(f"{i}. {idea.title[:60]}...")
        print(f"   Platform: {idea.source_platform or 'N/A'}")
        print(f"   Category: {idea.category}")
        print(f"   Score: {idea.score}/100")
        print(f"   Subcategories: {', '.join(list(idea.subcategory_relevance.keys())[:5])}")
        print()
    
    # Statistics
    print("=" * 80)
    print("Statistics")
    print("=" * 80)
    print()
    
    # Category distribution
    from collections import Counter
    category_counts = Counter(idea.category for idea in ideas)
    print("Category Distribution:")
    for category, count in category_counts.most_common():
        print(f"  • {category}: {count}")
    print()
    
    # Score statistics
    scores = [idea.score for idea in ideas]
    avg_score = sum(scores) / len(scores)
    print("Score Statistics:")
    print(f"  • Average Score: {avg_score:.1f}")
    print(f"  • Highest Score: {max(scores)}")
    print(f"  • Lowest Score: {min(scores)}")
    print()
    
    print("=" * 80)
    print("Demonstration Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
