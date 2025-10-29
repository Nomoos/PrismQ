"""PrismQ.IdeaInspiration.Scoring Package

Scoring engine for enriching IdeaInspiration objects with detailed scoring.

This module acts as a classifier/scorer that enriches existing IdeaInspiration
objects (from PrismQ.IdeaCollector or similar) with comprehensive scoring data.

Target Platform:
    - OS: Windows
    - GPU: NVIDIA RTX 5090
    - CPU: AMD Ryzen
    - RAM: 64GB

Usage:
    from mod.scoring import ScoringEngine
    from src.models import ScoreBreakdown
    
    engine = ScoringEngine()
    # Assume idea_inspiration comes from PrismQ.IdeaCollector
    score_breakdown = engine.score_idea_inspiration(idea_inspiration)
"""

__version__ = "0.1.0"
__author__ = "PrismQ"

from mod.scoring import ScoringEngine
from src.models import ScoreBreakdown

__all__ = ['ScoringEngine', 'ScoreBreakdown']
