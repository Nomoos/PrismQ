"""Database module for PrismQ.

This module contains database models and interfaces following SOLID principles:
- Single Responsibility: Each model handles only its own data
- Interface Segregation: Small, focused IModel interface
- Dependency Inversion: Depend on abstractions (IModel) not implementations
"""

from .models import IModel, Script

__all__ = ["IModel", "Script"]
