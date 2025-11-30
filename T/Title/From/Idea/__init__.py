"""PrismQ.T.Title.From.Idea - Initial Title Draft from Idea

This module generates the first version (v0) of title options based solely
on the original idea, before any script content exists.

Workflow Position: Stage 2 in MVP workflow

This module provides two main capabilities:
1. TitleGenerator: Generate title variants from an Idea (3-10 variants)
2. StoryTitleService: Create 10 Story objects with first Titles from an Idea

The Story creation workflow:
1. Takes an Idea as input
2. Creates 10 Story objects, each referencing the Idea (FK relationship)
3. Generates first Title (v0) for each Story from Idea content
4. Returns Stories and Titles ready for next workflow stage
"""

from .src.title_generator import (
    TitleGenerator,
    TitleVariant,
    TitleConfig,
    generate_titles_from_idea
)
from .src.story_title_service import (
    StoryTitleService,
    StoryTitleResult,
    create_stories_from_idea
)

__all__ = [
    # Title generation
    'TitleGenerator',
    'TitleVariant',
    'TitleConfig',
    'generate_titles_from_idea',
    # Story + Title creation
    'StoryTitleService',
    'StoryTitleResult',
    'create_stories_from_idea',
]

__version__ = '1.0.0'
__author__ = 'PrismQ Team'
