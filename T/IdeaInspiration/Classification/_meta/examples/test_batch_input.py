#!/usr/bin/env python3
"""Test script for Classification CLI batch processing."""

import json
import sys
from pathlib import Path

# Add Model to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'Model'))

from idea_inspiration import IdeaInspiration, ContentType

# Create test data - list of IdeaInspiration objects
test_ideas = [
    IdeaInspiration(
        title="My AITA Story - Was I Wrong?",
        description="Let me tell you about what happened yesterday...",
        content="So this happened to me at work. I was in a meeting and...",
        keywords=["storytime", "aita", "confession"],
        source_type=ContentType.TEXT,
        category=None,  # No category yet
        subcategory_relevance={}
    ),
    IdeaInspiration(
        title="Funny Meme Compilation 2024",
        description="Best memes of the year so far",
        content="Check out these hilarious memes...",
        keywords=["memes", "funny", "comedy"],
        source_type=ContentType.VIDEO,
        category=None,
        subcategory_relevance={}
    ),
    IdeaInspiration(
        title="How to Build a PC - Complete Guide",
        description="Step by step tutorial for building your first gaming PC",
        content="In this tutorial, we'll walk through every component...",
        keywords=["tutorial", "pc building", "tech"],
        source_type=ContentType.VIDEO,
        category=None,
        subcategory_relevance={}
    )
]

# Convert to JSON format
test_data = [idea.to_dict() for idea in test_ideas]

# Print JSON to stdout for CLI to consume
print(json.dumps(test_data, indent=2))
