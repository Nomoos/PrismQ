"""Database utilities for LyricSnippetsSource using SQLAlchemy."""

import sys
from typing import Optional, List, Dict, Any
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from contextlib import contextmanager
import json
from datetime import datetime

Base = declarative_base()


class LyricSnippet(Base):
    """SQLAlchemy model for lyric snippet storage."""
    
    __tablename__ = 'lyric_snippets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False)  # genius, manual, etc
    source_id = Column(String(255), nullable=False)  # Unique ID from source
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=True)  # Lyric snippet text
    tags = Column(Text, nullable=True)  # Comma-separated tags
    score = Column(Float, default=0.0)
    score_dictionary = Column(Text, nullable=True)  # JSON metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    
    __table_args__ = (
        UniqueConstraint('source', 'source_id', name='uix_source_source_id'),
    )


@contextmanager
def get_connection(database_url: str):
    """Get a database connection context manager.
    
    Args:
        database_url: SQLAlchemy database URL
        
    Yields:
        SQLAlchemy connection
    """
    engine = create_engine(database_url)
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()
        engine.dispose()


@contextmanager
def get_session(database_url: str):
    """Get a database session context manager.
    
    Args:
        database_url: SQLAlchemy database URL
        
    Yields:
        SQLAlchemy session
    """
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def init_database(database_url: str):
    """Initialize database schema.
    
    Args:
        database_url: SQLAlchemy database URL
    """
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    engine.dispose()


def insert_resource(database_url: str, source: str, source_id: str, title: str,
                   content: Optional[str] = None, tags: Optional[str] = None,
                   score: Optional[float] = None, score_dictionary: Optional[str] = None) -> bool:
    """Insert or update a creative resource in the database.
    
    Args:
        database_url: SQLAlchemy database URL
        source: Source platform
        source_id: Unique identifier from source
        title: Resource title
        content: Creative content (lyrics, narrative, etc.)
        tags: Comma-separated tags
        score: Calculated score
        score_dictionary: JSON string of score components
        
    Returns:
        True if inserted (new), False if updated (duplicate)
    """
    # Convert dict to JSON string if needed
    if isinstance(score_dictionary, dict):
        score_dictionary = json.dumps(score_dictionary)
    
    with get_session(database_url) as session:
        # Check if resource already exists
        existing = session.query(LyricSnippet).filter_by(
            source=source,
            source_id=source_id
        ).first()
        
        if existing:
            # Update existing record
            existing.title = title
            existing.content = content
            existing.tags = tags
            existing.score = score or 0.0
            existing.score_dictionary = score_dictionary
            session.commit()
            return False
        else:
            # Insert new record
            new_resource = LyricSnippet(
                source=source,
                source_id=source_id,
                title=title,
                content=content,
                tags=tags,
                score=score or 0.0,
                score_dictionary=score_dictionary,
                processed=False
            )
            session.add(new_resource)
            session.commit()
            return True


def get_all_resources(database_url: str, limit: int = 20, order_by: str = "score") -> List[Dict[str, Any]]:
    """Get all resources from database.
    
    Args:
        database_url: SQLAlchemy database URL
        limit: Maximum number of records to return
        order_by: Column to order by
        
    Returns:
        List of resource dictionaries
    """
    with get_session(database_url) as session:
        order_column = getattr(LyricSnippet, order_by, LyricSnippet.score)
        results = session.query(LyricSnippet).order_by(order_column.desc()).limit(limit).all()
        
        resources = []
        for row in results:
            resources.append({
                'id': row.id,
                'source': row.source,
                'source_id': row.source_id,
                'title': row.title,
                'content': row.content,
                'tags': row.tags,
                'score': row.score,
                'score_dictionary': row.score_dictionary,
                'created_at': row.created_at.isoformat() if row.created_at else None,
                'processed': row.processed
            })
        
        return resources


def count_resources(database_url: str) -> int:
    """Count total resources in database.
    
    Args:
        database_url: SQLAlchemy database URL
        
    Returns:
        Total count
    """
    with get_session(database_url) as session:
        return session.query(func.count(LyricSnippet.id)).scalar()


def count_by_source(database_url: str, source: str) -> int:
    """Count resources by source.
    
    Args:
        database_url: SQLAlchemy database URL
        source: Source platform
        
    Returns:
        Count for source
    """
    with get_session(database_url) as session:
        return session.query(func.count(LyricSnippet.id)).filter_by(source=source).scalar()


def get_unprocessed_records(database_url: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get unprocessed records from database.
    
    Args:
        database_url: SQLAlchemy database URL
        limit: Optional limit on number of records
        
    Returns:
        List of unprocessed resource dictionaries
    """
    with get_session(database_url) as session:
        query = session.query(LyricSnippet).filter_by(processed=False)
        
        if limit:
            query = query.limit(limit)
        
        results = query.all()
        
        resources = []
        for row in results:
            resources.append({
                'id': row.id,
                'source': row.source,
                'source_id': row.source_id,
                'title': row.title,
                'content': row.content,
                'tags': row.tags,
                'score': row.score,
                'score_dictionary': row.score_dictionary,
                'created_at': row.created_at.isoformat() if row.created_at else None,
                'processed': row.processed
            })
        
        return resources


def mark_as_processed(database_url: str, record_id: int):
    """Mark a record as processed.
    
    Args:
        database_url: SQLAlchemy database URL
        record_id: Record ID to mark as processed
    """
    with get_session(database_url) as session:
        record = session.query(LyricSnippet).filter_by(id=record_id).first()
        if record:
            record.processed = True
            session.commit()


class Database:
    """Manages database operations for lyric snippet collection.
    
    This class provides a backward-compatible interface.
    """

    def __init__(self, db_path: str, interactive: bool = True):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
            interactive: Whether to prompt for confirmation before creating database
        """
        self.db_path = db_path
        self._interactive = interactive
        
        # Construct database_url from db_path
        if db_path.startswith("sqlite://"):
            self.database_url = db_path
        else:
            self.database_url = f"sqlite:///{db_path}"
        
        # Check if database already exists
        db_exists = Path(db_path).exists() if not db_path.startswith("sqlite://") else True
        
        # If database doesn't exist and we're in interactive mode, ask for confirmation
        if not db_exists and self._interactive:
            if not self._confirm_database_creation():
                print("Database creation cancelled.")
                sys.exit(0)
        
        # Initialize database schema
        init_database(self.database_url)
    
    def _confirm_database_creation(self) -> bool:
        """Prompt user for confirmation before creating database.
        
        Returns:
            True if user confirms, False otherwise
        """
        try:
            response = input(f"Database '{self.db_path}' does not exist. Create it? (y/n): ").strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return True
    
    def insert_resource(self, source: str, source_id: str, title: str,
                       content: Optional[str] = None, tags: Optional[str] = None,
                       score: Optional[float] = None, score_dictionary: Optional[str] = None) -> bool:
        """Insert or update a resource in the database."""
        return insert_resource(
            self.database_url, source, source_id, title,
            content, tags, score, score_dictionary
        )
    
    def get_all_resources(self, limit: int = 20, order_by: str = "score") -> List[Dict[str, Any]]:
        """Get all resources from database."""
        return get_all_resources(self.database_url, limit, order_by)
    
    def count_resources(self) -> int:
        """Count total resources in database."""
        return count_resources(self.database_url)
    
    def count_by_source(self, source: str) -> int:
        """Count resources by source."""
        return count_by_source(self.database_url, source)
    
    def close(self):
        """Close database connection (no-op for compatibility)."""
        pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
