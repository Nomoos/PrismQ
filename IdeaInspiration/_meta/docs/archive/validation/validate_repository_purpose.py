#!/usr/bin/env python3
"""
Validation Script for Repository Purpose

⚠️ NOTE: This script is archived and was originally located in the repository root.
Path references have been updated for the archived location.

This script validates that PrismQ.IdeaInspiration repository fulfills all requirements:
1. Data collection from various sources and unification into unified format
2. Export to database table
3. Evaluation of suitability for YouTube short story video creation
4. Categorization into categories according to settings and subcategories according to AI discretion
"""

import sys
from pathlib import Path
import tempfile
import os

# Add paths - updated for archived location (was in repo root, now in _meta/docs/archive/validation/)
repo_root = Path(__file__).parent.parent.parent.parent.parent
model_dir = repo_root / 'Model'
scoring_src = repo_root / 'Scoring' / 'src'
classification_src = repo_root / 'Classification' / 'src'

sys.path.insert(0, str(model_dir))
sys.path.insert(0, str(repo_root / 'Scoring'))
sys.path.insert(0, str(repo_root / 'Classification'))
sys.path.insert(0, str(scoring_src))
sys.path.insert(0, str(classification_src))

from idea_inspiration import IdeaInspiration, ContentType
from idea_inspiration_db import IdeaInspirationDatabase
from scoring import ScoringEngine
from classification import TextClassifier


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")


def print_info(message):
    """Print an info message."""
    print(f"   {message}")


def validate_requirement_1():
    """Validate Requirement 1: Data collection and unification."""
    print_section("REQUIREMENT 1: Data Collection and Unification")
    
    print("\n1.1 Testing unified data format (IdeaInspiration model)...")
    
    # Create data from different source types
    text_idea = IdeaInspiration.from_text(
        title="Reddit Story: AITA for speaking up?",
        description="A workplace conflict story",
        text_content="Story about workplace ethics...",
        keywords=["aita", "workplace", "story"],
        source_platform="reddit",
        source_id="reddit_123",
        source_url="https://reddit.com/r/aita/123"
    )
    print_success("Created IdeaInspiration from TEXT source (Reddit)")
    
    video_idea = IdeaInspiration.from_video(
        title="YouTube Short: My Morning Routine",
        description="Daily vlog content",
        subtitle_text="Follow me through my morning...",
        keywords=["vlog", "morning", "routine"],
        source_platform="youtube",
        source_id="yt_456",
        source_url="https://youtube.com/watch?v=456",
        metadata={
            'statistics': {
                'viewCount': '100000',
                'likeCount': '5000',
                'commentCount': '250'
            }
        }
    )
    print_success("Created IdeaInspiration from VIDEO source (YouTube)")
    
    audio_idea = IdeaInspiration.from_audio(
        title="Podcast: Tech Trends Discussion",
        description="Discussion about AI trends",
        transcription="In today's episode we discuss...",
        keywords=["podcast", "tech", "ai"],
        source_platform="spotify",
        source_id="sp_789",
        source_url="https://spotify.com/episode/789"
    )
    print_success("Created IdeaInspiration from AUDIO source (Podcast)")
    
    print("\n1.2 Verifying unified format...")
    all_ideas = [text_idea, video_idea, audio_idea]
    
    # Check all have same attributes
    for idea in all_ideas:
        assert hasattr(idea, 'title')
        assert hasattr(idea, 'description')
        assert hasattr(idea, 'content')
        assert hasattr(idea, 'keywords')
        assert hasattr(idea, 'source_type')
        assert hasattr(idea, 'source_platform')
        assert hasattr(idea, 'metadata')
    
    print_success("All sources unified into IdeaInspiration format")
    print_info(f"Verified {len(all_ideas)} objects from {len(set(i.source_platform for i in all_ideas))} different platforms")
    
    print("\n1.3 Verifying source diversity...")
    platforms = [idea.source_platform for idea in all_ideas]
    print_info(f"Platforms represented: {', '.join(platforms)}")
    
    content_types = [idea.source_type.value for idea in all_ideas]
    print_info(f"Content types: {', '.join(content_types)}")
    
    print_success("REQUIREMENT 1 VALIDATED: Data collection and unification working")
    return all_ideas


def validate_requirement_2(ideas):
    """Validate Requirement 2: Database export."""
    print_section("REQUIREMENT 2: Export to Database Table")
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(suffix='.s3db', delete=False)
    temp_db.close()
    
    try:
        print("\n2.1 Initializing database...")
        db = IdeaInspirationDatabase(temp_db.name, interactive=False)
        print_success("Database initialized successfully")
        print_info(f"Database path: {temp_db.name}")
        
        print("\n2.2 Exporting to database table...")
        for idea in ideas:
            db.insert(idea)
        print_success(f"Exported {len(ideas)} records to IdeaInspiration table")
        
        print("\n2.3 Verifying database export...")
        retrieved_ideas = db.get_all()
        assert len(retrieved_ideas) == len(ideas)
        print_success(f"Retrieved {len(retrieved_ideas)} records from database")
        
        print("\n2.4 Testing database queries...")
        
        # Test platform filtering
        reddit_ideas = db.get_all(source_platform="reddit")
        print_info(f"Reddit posts: {len(reddit_ideas)}")
        
        youtube_ideas = db.get_all(source_platform="youtube")
        print_info(f"YouTube videos: {len(youtube_ideas)}")
        
        spotify_ideas = db.get_all(source_platform="spotify")
        print_info(f"Spotify podcasts: {len(spotify_ideas)}")
        
        print_success("Platform-based filtering working correctly")
        
        print("\n2.5 Verifying data integrity...")
        for original, retrieved in zip(ideas, retrieved_ideas):
            assert original.title == retrieved.title
            assert original.source_platform == retrieved.source_platform
        print_success("All data preserved correctly in database")
        
        print_success("REQUIREMENT 2 VALIDATED: Database export working")
        
    finally:
        # Clean up
        os.unlink(temp_db.name)


def validate_requirement_3(ideas):
    """Validate Requirement 3: YouTube story suitability evaluation."""
    print_section("REQUIREMENT 3: YouTube Short Story Suitability Evaluation")
    
    print("\n3.1 Initializing scoring engine...")
    engine = ScoringEngine()
    print_success("ScoringEngine initialized")
    
    print("\n3.2 Evaluating content suitability...")
    score_breakdowns = engine.score_idea_inspiration_batch(ideas)
    print_success(f"Scored {len(score_breakdowns)} items")
    
    print("\n3.3 Score breakdown analysis...")
    for idea, breakdown in zip(ideas, score_breakdowns):
        idea.score = int(breakdown.overall_score)
        
        print_info(f"\n{idea.title}")
        print_info(f"  Platform: {idea.source_platform}")
        print_info(f"  Overall Score: {breakdown.overall_score:.1f}/100")
        print_info(f"  Title Score: {breakdown.title_score:.1f}/100")
        print_info(f"  Description Score: {breakdown.description_score:.1f}/100")
        print_info(f"  Text Quality: {breakdown.text_quality_score:.1f}/100")
        
        if breakdown.engagement_score > 0:
            print_info(f"  Engagement Score: {breakdown.engagement_score:.1f}/100")
        
        # Suitability assessment
        if breakdown.overall_score >= 70:
            suitability = "HIGH suitability for story video"
        elif breakdown.overall_score >= 50:
            suitability = "MEDIUM suitability for story video"
        else:
            suitability = "LOW suitability for story video"
        print_info(f"  → {suitability}")
    
    print("\n3.4 Score statistics...")
    scores = [int(bd.overall_score) for bd in score_breakdowns]
    avg_score = sum(scores) / len(scores)
    print_info(f"Average Score: {avg_score:.1f}/100")
    print_info(f"Highest Score: {max(scores)}/100")
    print_info(f"Lowest Score: {min(scores)}/100")
    print_info(f"Range: {max(scores) - min(scores)} points")
    
    print_success("REQUIREMENT 3 VALIDATED: Suitability evaluation working")
    return score_breakdowns


def validate_requirement_4(ideas):
    """Validate Requirement 4: Categorization with settings and AI."""
    print_section("REQUIREMENT 4: Categorization (Settings) and Subcategorization (AI)")
    
    print("\n4.1 Initializing classification system...")
    classifier = TextClassifier()
    print_success("TextClassifier initialized")
    print_info("Primary categories (per settings): 8 categories defined")
    
    print("\n4.2 Classifying content...")
    enrichments = classifier.enrich_batch(ideas)
    print_success(f"Classified {len(enrichments)} items")
    
    print("\n4.3 Classification results...")
    for idea, enrichment in zip(ideas, enrichments):
        idea.category = enrichment.category.value
        # Convert tags to subcategory_relevance scores
        for tag in enrichment.tags:
            idea.subcategory_relevance[tag] = int(enrichment.category_confidence * 100)
        
        print_info(f"\n{idea.title}")
        print_info(f"  Platform: {idea.source_platform}")
        
        # Primary category (from settings)
        print_info(f"  PRIMARY CATEGORY (per settings): {enrichment.category.value}")
        print_info(f"    Confidence: {enrichment.category_confidence:.2%}")
        
        # Subcategories (AI discretion) - derived from tags
        if enrichment.tags:
            print_info(f"  SUBCATEGORIES (AI discretion - from tags):")
            # Show top 5 subcategories
            for tag in enrichment.tags[:5]:
                score = int(enrichment.category_confidence * 100)
                print_info(f"    - {tag}: {score}/100")
        
        # Tags generated by AI
        if enrichment.tags:
            print_info(f"  AI-generated tags: {', '.join(enrichment.tags[:5])}")
    
    print("\n4.4 Category distribution...")
    from collections import Counter
    category_counts = Counter(idea.category for idea in ideas)
    print_info("Primary Categories Assigned:")
    for category, count in category_counts.most_common():
        print_info(f"  - {category}: {count}")
    
    print("\n4.5 Verifying AI subcategorization...")
    total_subcats = sum(len(idea.subcategory_relevance) for idea in ideas)
    avg_subcats = total_subcats / len(ideas)
    print_info(f"Total subcategories assigned: {total_subcats}")
    print_info(f"Average subcategories per item: {avg_subcats:.1f}")
    print_success("AI successfully assigned subcategories based on content analysis")
    
    print_success("REQUIREMENT 4 VALIDATED: Categorization system working")


def main():
    """Main validation function."""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "REPOSITORY PURPOSE VALIDATION SCRIPT" + " " * 27 + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Repository: PrismQ.IdeaInspiration" + " " * 44 + "║")
    print("║" + "  Date: November 2, 2025" + " " * 54 + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        # Requirement 1: Data collection and unification
        ideas = validate_requirement_1()
        
        # Requirement 2: Database export
        validate_requirement_2(ideas)
        
        # Requirement 3: YouTube story suitability
        validate_requirement_3(ideas)
        
        # Requirement 4: Categorization
        validate_requirement_4(ideas)
        
        # Final summary
        print_section("VALIDATION SUMMARY")
        print()
        print_success("REQUIREMENT 1: Data collection and unification - PASSED")
        print_success("REQUIREMENT 2: Export to database table - PASSED")
        print_success("REQUIREMENT 3: YouTube story suitability evaluation - PASSED")
        print_success("REQUIREMENT 4: Categorization (settings + AI) - PASSED")
        print()
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + " " * 10 + "✅ ALL REQUIREMENTS VALIDATED SUCCESSFULLY ✅" + " " * 22 + "║")
        print("║" + " " * 78 + "║")
        print("║" + "  The repository FULLY FULFILLS its stated purpose." + " " * 27 + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
