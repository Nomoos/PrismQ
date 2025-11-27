"""PrismQ.Database - Core database models for PrismQ.

This package provides database models following SOLID principles:
- Interface Segregation: Small, focused IModel interface
- Dependency Inversion: Models depend on IModel abstraction
- Single Responsibility: Each model handles one entity
"""

try:
    from .models.base import IModel
    from .models.title import Title
except ImportError:
    # Allow importing when not installed as package
    pass

__all__ = [
    "IModel",
    "Title",
]

__version__ = "0.1.0"
