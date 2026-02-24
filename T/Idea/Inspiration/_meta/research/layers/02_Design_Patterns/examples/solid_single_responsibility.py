#!/usr/bin/env python3
"""
Single Responsibility Principle (SRP) - Examples

PRINCIPLE: A class should have one, and only one, reason to change.

Each class should focus on a single responsibility or concern.
This makes code easier to understand, test, and maintain.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# =============================================================================
# Example 1: Good SRP - Separated Responsibilities
# =============================================================================


@dataclass
class IdeaInspiration:
    """Data model - only responsible for holding data."""

    id: str
    title: str
    source: str
    created_at: datetime

    # No business logic here - pure data


class IdeaValidator:
    """Single responsibility: Validate idea data."""

    def validate(self, idea: IdeaInspiration) -> bool:
        """Validate that idea has required fields."""
        if not idea.title or len(idea.title.strip()) == 0:
            raise ValueError("Title cannot be empty")

        if not idea.source or len(idea.source.strip()) == 0:
            raise ValueError("Source cannot be empty")

        return True


class IdeaRepository:
    """Single responsibility: Persist and retrieve ideas."""

    def __init__(self, db_path: str):
        self._db_path = db_path

    def save(self, idea: IdeaInspiration) -> str:
        """Save idea to database."""
        # Database persistence logic only
        print(f"Saving idea {idea.id} to database at {self._db_path}")
        return idea.id

    def find_by_id(self, idea_id: str) -> Optional[IdeaInspiration]:
        """Retrieve idea from database."""
        print(f"Fetching idea {idea_id} from database")
        # Database retrieval logic only
        return None


class IdeaNotifier:
    """Single responsibility: Send notifications about ideas."""

    def notify_new_idea(self, idea: IdeaInspiration) -> None:
        """Send notification about new idea."""
        # Notification logic only
        print(f"Sending notification: New idea '{idea.title}' from {idea.source}")


class IdeaService:
    """Orchestrates operations - delegates to specialized classes."""

    def __init__(
        self, validator: IdeaValidator, repository: IdeaRepository, notifier: IdeaNotifier
    ):
        self._validator = validator
        self._repository = repository
        self._notifier = notifier

    def create_idea(self, title: str, source: str) -> str:
        """Create and save a new idea."""
        # Orchestrates, but doesn't implement validation/persistence/notification
        idea = IdeaInspiration(
            id=self._generate_id(), title=title, source=source, created_at=datetime.now()
        )

        self._validator.validate(idea)
        idea_id = self._repository.save(idea)
        self._notifier.notify_new_idea(idea)

        return idea_id

    @staticmethod
    def _generate_id() -> str:
        """Generate unique ID."""
        return f"idea-{datetime.now().timestamp()}"


# =============================================================================
# Example 2: Testing Benefits of SRP
# =============================================================================


def test_validator_independently():
    """
    ✅ With SRP, we can test validator in isolation.
    No need to mock database, notifications, etc.
    """
    validator = IdeaValidator()

    # Valid idea
    valid_idea = IdeaInspiration(
        id="test-1", title="Valid Title", source="youtube", created_at=datetime.now()
    )
    assert validator.validate(valid_idea) is True

    # Invalid idea
    invalid_idea = IdeaInspiration(
        id="test-2", title="", source="youtube", created_at=datetime.now()  # Empty title
    )
    try:
        validator.validate(invalid_idea)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


# =============================================================================
# Demonstration
# =============================================================================


def demonstrate_srp():
    """Demonstrate SRP with real-world scenario."""
    print("\n" + "=" * 70)
    print("DEMONSTRATING SINGLE RESPONSIBILITY PRINCIPLE")
    print("=" * 70)

    # Create specialized components (each with single responsibility)
    validator = IdeaValidator()
    repository = IdeaRepository(db_path="ideas.db")
    notifier = IdeaNotifier()

    # Create service that orchestrates them
    service = IdeaService(validator=validator, repository=repository, notifier=notifier)

    # Use the service
    print("\n1. Creating a new idea:")
    idea_id = service.create_idea(title="Amazing Python Tutorial", source="YouTube")
    print(f"   Created idea with ID: {idea_id}")

    # Benefits of SRP:
    print("\n2. Benefits of Single Responsibility Principle:")
    print("   ✅ Each class is easy to understand")
    print("   ✅ Each class is easy to test in isolation")
    print("   ✅ Changes to one responsibility don't affect others")
    print("   ✅ Easy to replace implementations (e.g., swap database)")
    print("   ✅ Code is more maintainable and flexible")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run demonstration
    demonstrate_srp()

    # Run tests
    print("\nRunning tests...")
    test_validator_independently()
    print("✅ All tests passed!")
