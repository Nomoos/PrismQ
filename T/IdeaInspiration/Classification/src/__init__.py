"""PrismQ.IdeaInspiration.Classification Package

Classification engine for enriching IdeaInspiration objects with detailed classification.

This module acts as a classifier that enriches existing IdeaInspiration
objects (from Model) with comprehensive classification data.

Target Platform:
    - OS: Windows
    - GPU: NVIDIA RTX 5090
    - CPU: AMD Ryzen
    - RAM: 64GB

Usage:
    from src.classification import (
        CategoryClassifier,
        StoryDetector,
        TextClassifier,
        PrimaryCategory
    )
    
    # Import IdeaInspiration from Model
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Model'))
    from idea_inspiration import IdeaInspiration
    
    # Use classifiers
    classifier = TextClassifier()
    enrichment = classifier.classify(idea_inspiration)
"""

__version__ = "2.1.0"
__author__ = "PrismQ"

from src.classification import (
    CategoryClassifier,
    StoryDetector,
    TextClassifier,
    PrimaryCategory,
    CategoryResult,
    ClassificationEnrichment,
    IdeaInspirationExtractor,
    IdeaInspirationBuilder,
    IdeaInspirationProtocol,
    IdeaInspirationDict,
    IdeaInspirationLike
)

# Re-export IdeaInspiration from Model for convenience
import sys
from pathlib import Path
_model_path = Path(__file__).parent.parent.parent / 'Model'
if str(_model_path) not in sys.path:
    sys.path.insert(0, str(_model_path))

from idea_inspiration import IdeaInspiration, ContentType

__all__ = [
    # Core classifiers
    'CategoryClassifier',
    'StoryDetector',
    'TextClassifier',
    # Category types
    'PrimaryCategory',
    'CategoryResult',
    # Classification enrichment
    'ClassificationEnrichment',
    # Helper utilities
    'IdeaInspirationExtractor',
    'IdeaInspirationBuilder',
    # Type hints
    'IdeaInspirationProtocol',
    'IdeaInspirationDict',
    'IdeaInspirationLike',
    # Model (re-exported from Model module)
    'IdeaInspiration',
    'ContentType',
]
