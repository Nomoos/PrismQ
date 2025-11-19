#!/usr/bin/env python3
"""
Dependency Inversion Principle (DIP) - Examples

PRINCIPLE: Depend on abstractions, not concretions.
- High-level modules should not depend on low-level modules. Both should depend on abstractions.
- Abstractions should not depend on details. Details should depend on abstractions.

Use dependency injection and protocols to achieve loose coupling.
"""

from typing import Protocol, List, Optional
from dataclasses import dataclass
from datetime import datetime


# =============================================================================
# Example 1: Good DIP - Protocol-Based Dependencies
# =============================================================================

@dataclass
class IdeaInspiration:
    """Domain model."""
    id: str
    title: str
    source: str
    created_at: datetime


class IdeaRepository(Protocol):
    """
    ✅ ABSTRACTION: Protocol defines what operations are needed.
    No dependency on concrete database implementation.
    """
    
    def save(self, idea: IdeaInspiration) -> str:
        """Save idea and return ID."""
        ...
    
    def find_by_id(self, idea_id: str) -> Optional[IdeaInspiration]:
        """Find idea by ID."""
        ...


class Logger(Protocol):
    """✅ ABSTRACTION: Protocol for logging."""
    
    def info(self, message: str) -> None:
        """Log info message."""
        ...
    
    def error(self, message: str) -> None:
        """Log error message."""
        ...


class IdeaService:
    """
    ✅ HIGH-LEVEL MODULE: Depends on abstractions (Protocols), not concrete classes.
    This is the Dependency Inversion Principle in action.
    """
    
    def __init__(self, repository: IdeaRepository, logger: Logger):
        # Dependencies injected as abstractions
        self._repository = repository
        self._logger = logger
    
    def create_idea(self, title: str, source: str) -> str:
        """Create new idea - business logic."""
        self._logger.info(f"Creating idea: {title}")
        
        idea = IdeaInspiration(
            id=f"idea-{datetime.now().timestamp()}",
            title=title,
            source=source,
            created_at=datetime.now()
        )
        
        idea_id = self._repository.save(idea)
        self._logger.info(f"Idea created: {idea_id}")
        
        return idea_id


# =============================================================================
# Low-Level Implementations (Details)
# =============================================================================

class SqliteRepository:
    """
    ✅ LOW-LEVEL MODULE: Concrete implementation depends on abstraction.
    Implements IdeaRepository protocol.
    """
    
    def __init__(self, db_path: str):
        self._db_path = db_path
    
    def save(self, idea: IdeaInspiration) -> str:
        """Save to SQLite database."""
        print(f"[SQLite] Saving idea {idea.id} to {self._db_path}")
        return idea.id
    
    def find_by_id(self, idea_id: str) -> Optional[IdeaInspiration]:
        """Find in SQLite database."""
        print(f"[SQLite] Finding idea {idea_id}")
        return None


class PostgresRepository:
    """
    ✅ ANOTHER IMPLEMENTATION: Can swap without changing IdeaService.
    This demonstrates the power of DIP.
    """
    
    def __init__(self, connection_string: str):
        self._connection_string = connection_string
    
    def save(self, idea: IdeaInspiration) -> str:
        """Save to PostgreSQL database."""
        print(f"[PostgreSQL] Saving idea {idea.id}")
        return idea.id
    
    def find_by_id(self, idea_id: str) -> Optional[IdeaInspiration]:
        """Find in PostgreSQL database."""
        print(f"[PostgreSQL] Finding idea {idea_id}")
        return None


class ConsoleLogger:
    """✅ Concrete logger implementation."""
    
    def info(self, message: str) -> None:
        """Log to console."""
        print(f"[INFO] {message}")
    
    def error(self, message: str) -> None:
        """Log to console."""
        print(f"[ERROR] {message}")


class FileLogger:
    """✅ Another logger implementation - easily swappable."""
    
    def __init__(self, file_path: str):
        self._file_path = file_path
    
    def info(self, message: str) -> None:
        """Log to file."""
        print(f"[FILE INFO] {message} -> {self._file_path}")
    
    def error(self, message: str) -> None:
        """Log to file."""
        print(f"[FILE ERROR] {message} -> {self._file_path}")


# =============================================================================
# Example 2: Dependency Injection Container (Advanced)
# =============================================================================

class Container:
    """
    Simple dependency injection container.
    Manages object creation and dependency wiring.
    """
    
    def __init__(self):
        self._singletons = {}
        self._factories = {}
    
    def register_singleton(self, key: str, instance: any):
        """Register singleton instance."""
        self._singletons[key] = instance
    
    def register_factory(self, key: str, factory):
        """Register factory function."""
        self._factories[key] = factory
    
    def resolve(self, key: str):
        """Resolve dependency."""
        if key in self._singletons:
            return self._singletons[key]
        
        if key in self._factories:
            return self._factories[key]()
        
        raise ValueError(f"No registration found for {key}")


# =============================================================================
# Demonstration
# =============================================================================

def demonstrate_dip():
    """Demonstrate Dependency Inversion Principle."""
    print("\n" + "="*70)
    print("DEMONSTRATING DEPENDENCY INVERSION PRINCIPLE")
    print("="*70)
    
    print("\n1. Using SQLite + Console Logger:")
    sqlite_repo = SqliteRepository(db_path="ideas.db")
    console_logger = ConsoleLogger()
    service1 = IdeaService(repository=sqlite_repo, logger=console_logger)
    service1.create_idea("Python Tutorial", "YouTube")
    
    print("\n2. Swapping to PostgreSQL + File Logger:")
    print("   ✅ No changes to IdeaService needed!")
    postgres_repo = PostgresRepository(connection_string="postgresql://localhost")
    file_logger = FileLogger(file_path="app.log")
    service2 = IdeaService(repository=postgres_repo, logger=file_logger)
    service2.create_idea("Advanced Python", "YouTube")
    
    print("\n3. Using Dependency Injection Container:")
    container = Container()
    container.register_singleton("repository", SqliteRepository("ideas.db"))
    container.register_singleton("logger", ConsoleLogger())
    
    # Resolve dependencies
    repo = container.resolve("repository")
    logger = container.resolve("logger")
    service3 = IdeaService(repository=repo, logger=logger)
    service3.create_idea("DI Container Example", "YouTube")
    
    print("\n" + "="*70)
    print("KEY TAKEAWAYS:")
    print("✅ High-level modules depend on abstractions (Protocols)")
    print("✅ Low-level modules implement abstractions")
    print("✅ Easy to swap implementations without changing high-level code")
    print("✅ Enables testing with mocks")
    print("✅ Loose coupling between components")
    print("="*70 + "\n")


if __name__ == "__main__":
    demonstrate_dip()
