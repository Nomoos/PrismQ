"""Database models for PrismQ.

This package contains the database model implementations following
the Dependency Inversion Principle - depending on abstractions (IModel)
rather than concrete implementations.
"""

from .base import IModel
from .script import Script

__all__ = ["IModel", "Script"]
