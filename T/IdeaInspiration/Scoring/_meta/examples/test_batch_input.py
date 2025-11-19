#!/usr/bin/env python3
"""Test script for Scoring CLI batch processing."""

import json
import sys
from pathlib import Path

# Add Model to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'Model'))

from idea_inspiration import IdeaInspiration, ContentType

# Create test data - list of IdeaInspiration objects
test_ideas = [
    IdeaInspiration(
        title="Introduction to Machine Learning",
        description="A comprehensive guide to ML basics and fundamentals.",
        content="""
        Machine learning is a subset of artificial intelligence that enables systems
        to learn and improve from experience. This guide covers the fundamental concepts
        including supervised learning, unsupervised learning, and reinforcement learning.
        """,
        keywords=["machine learning", "AI", "tutorial"],
        source_type=ContentType.TEXT,
        metadata={},
        score=None  # No score yet
    ),
    IdeaInspiration(
        title="Python Programming Tutorial for Beginners",
        description="Learn Python from scratch with hands-on examples.",
        content="""
        Welcome to this Python programming tutorial. In this video, we'll cover the basics
        of Python including variables, data types, and control structures.
        """,
        keywords=["python", "programming", "tutorial"],
        source_type=ContentType.VIDEO,
        metadata={
            'statistics': {
                'viewCount': '500000',
                'likeCount': '25000',
                'commentCount': '500'
            }
        },
        score=None  # No score yet
    ),
    IdeaInspiration(
        title="Quick Recipe: Chocolate Chip Cookies",
        description="Easy 15-minute recipe for delicious cookies",
        content="Mix flour, sugar, butter, and chocolate chips...",
        keywords=["recipe", "baking", "cookies"],
        source_type=ContentType.TEXT,
        score=None  # No score yet
    )
]

# Convert to JSON format
test_data = [idea.to_dict() for idea in test_ideas]

# Print JSON to stdout for CLI to consume
print(json.dumps(test_data, indent=2))
