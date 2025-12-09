"""Shared core utilities for all Source modules.

This module provides base classes and common utilities that can be reused
across all source implementations (YouTube, Reddit, HackerNews, etc.).

Design Pattern: Template Method Pattern with Progressive Enrichment
- BaseWorker: General task processing
- BaseSourceWorker: Adds configuration and storage
- Media-specific workers: Add media operations
- Platform-specific workers: Add platform operations
"""

from .base_source_worker import BaseSourceWorker

# Worker hierarchy - Progressive Enrichment Pattern
from .base_worker import BaseWorker, Task, TaskResult
from .content_funnel import (
    AudioExtractor,
    AudioTranscriber,
    ContentFunnel,
    SubtitleExtractor,
    TransformationMetadata,
    TransformationStage,
)

__all__ = [
    # Content Funnel
    "ContentFunnel",
    "TransformationStage",
    "TransformationMetadata",
    "AudioExtractor",
    "AudioTranscriber",
    "SubtitleExtractor",
    # Worker Hierarchy
    "BaseWorker",
    "Task",
    "TaskResult",
    "BaseSourceWorker",
]
