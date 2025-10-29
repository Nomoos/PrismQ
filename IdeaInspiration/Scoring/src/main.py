"""Main entry point for the PrismQ.IdeaInspiration.Scoring module."""

import logging
from pathlib import Path
import sys

# Add parent directory to path to import both ConfigLoad and local modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir.parent))  # For ConfigLoad
sys.path.insert(0, str(parent_dir))  # For mod

from ConfigLoad import Config, get_module_logger
from mod.scoring import ScoringEngine
from src.models import ScoreBreakdown

# Mock IdeaInspiration class for demonstration
# In production, this would be imported from PrismQ.IdeaCollector or similar
class MockIdeaInspiration:
    """Mock IdeaInspiration for demonstration purposes.
    
    In production, import from: from prismq.ideacollector import IdeaInspiration
    """
    def __init__(self, title, description, text_content, metadata=None):
        self.title = title
        self.description = description
        self.text_content = text_content
        self.metadata = metadata or {}
        self.content_type = 'text'  # Mock attribute

# Initialize configuration
config = Config(interactive=False)

# Configure logging using centralized ConfigLoad
logger = get_module_logger(
    module_name="PrismQ.IdeaInspiration.Scoring",
    module_version="0.1.0",
    module_path=str(Path(__file__).parent),
    log_startup=True
)


def main() -> None:
    """Main function for the PrismQ.IdeaInspiration.Scoring module.
    
    Demonstrates the usage of the ScoringEngine for evaluating content ideas.
    """
    logger.info("PrismQ.IdeaInspiration.Scoring - Starting")
    logger.info("Target: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM")
    
    # Initialize scoring engine
    engine = ScoringEngine()
    
    # Example: Calculate score for sample YouTube video
    sample_youtube_data = {
        'statistics': {
            'viewCount': '1000000',
            'likeCount': '50000',
            'commentCount': '1000'
        }
    }
    
    score, details = engine.calculate_youtube_score(sample_youtube_data)
    logger.info(f"YouTube Video Score: {score:.2f}")
    logger.info(f"Score Details: {details}")
    
    # Example: Calculate Universal Content Score
    sample_metrics = {
        'views': 1000000,
        'likes': 50000,
        'comments': 1000,
        'shares': 5000,
        'saves': 2000,
        'average_watch_time': 45,
        'video_length': 60,
        'channel_median_views': 500000,
        'conversions': 1000
    }
    
    ucs_results = engine.calculate_universal_content_score(sample_metrics)
    logger.info(f"Universal Content Score: {ucs_results['universal_content_score']:.2f}")
    logger.info(f"Engagement Rate: {ucs_results['engagement_rate']:.2f}%")
    logger.info(f"Watch-Through Rate: {ucs_results['watch_through_rate']:.2f}%")
    logger.info(f"RPI: {ucs_results['relative_performance_index']:.2f}%")
    
    # Example: Text-based scoring with IdeaInspiration
    logger.info("\n=== AI-Based Text Quality Scoring (Enrichment Pattern) ===")
    
    # Example 1: Plain text article
    # In production: text_idea = IdeaInspiration.from_text(...)
    text_idea = MockIdeaInspiration(
        title="Introduction to Machine Learning",
        description="A comprehensive guide to ML basics and fundamentals.",
        text_content="""
        Machine learning is a subset of artificial intelligence that enables systems
        to learn and improve from experience. This guide covers the fundamental concepts
        including supervised learning, unsupervised learning, and reinforcement learning.
        You'll discover how to apply these techniques to real-world problems and build
        intelligent applications. The field combines statistics, computer science, and
        domain expertise to create powerful predictive models.
        """
    )
    
    # Enrich the IdeaInspiration with detailed scoring
    score_breakdown = engine.score_idea_inspiration(text_idea)
    logger.info(f"Overall Score: {score_breakdown.overall_score:.2f}")
    logger.info(f"Title Score: {score_breakdown.title_score:.2f}")
    logger.info(f"Description Score: {score_breakdown.description_score:.2f}")
    logger.info(f"Text Quality Score: {score_breakdown.text_quality_score:.2f}")
    logger.info(f"Readability Score: {score_breakdown.readability_score:.2f}")
    logger.info(f"Sentiment Score: {score_breakdown.sentiment_score:.2f}")
    
    # Example 2: YouTube video with transcription and engagement metrics
    logger.info("\n=== Scoring YouTube Video with Engagement Metrics ===")
    
    # In production: video_idea = IdeaInspiration.from_youtube_video(...)
    video_idea = MockIdeaInspiration(
        title="Python Programming Tutorial for Beginners",
        description="Learn Python from scratch with hands-on examples.",
        text_content="""
        Welcome to this Python programming tutorial. In this video, we'll cover the basics
        of Python including variables, data types, and control structures. Python is an
        excellent language for beginners because of its simple syntax and readability.
        We'll also explore functions, loops, and how to write clean, maintainable code.
        """,
        metadata={
            'statistics': {
                'viewCount': '500000',
                'likeCount': '25000',
                'commentCount': '500'
            },
            'channel': 'CodeMaster',
            'published_at': '2024-01-01'
        }
    )
    
    # Enrich with comprehensive scoring including engagement
    video_score_breakdown = engine.score_idea_inspiration(video_idea)
    logger.info(f"Overall Score: {video_score_breakdown.overall_score:.2f}")
    logger.info(f"Title Score: {video_score_breakdown.title_score:.2f}")
    logger.info(f"Engagement Score: {video_score_breakdown.engagement_score:.2f}")
    logger.info(f"Text Quality Score: {video_score_breakdown.text_quality_score:.2f}")
    logger.info(f"Readability Score: {video_score_breakdown.readability_score:.2f}")
    
    logger.info("\nPrismQ.IdeaInspiration.Scoring - Complete")


if __name__ == "__main__":
    main()
