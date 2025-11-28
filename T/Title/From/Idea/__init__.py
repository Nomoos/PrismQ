"""PrismQ.T.Title.From.Idea - Initial Title Draft from Idea

This module generates the first version (v1) of title options based solely
on the original idea, before any script content exists.

Workflow Position: Stage 2 in MVP workflow
"""

from .src.title_generator import (
    TitleGenerator,
    TitleVariant,
    TitleConfig,
    generate_titles_from_idea
)

__all__ = [
    'TitleGenerator',
    'TitleVariant',
    'TitleConfig',
    'generate_titles_from_idea'
]

__version__ = '1.0.0'
__author__ = 'PrismQ Team'
