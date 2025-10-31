"""Database operations for UserFeedbackSource."""

import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

Base = declarative_base()


class CommunitySignal(Base):
    """SQLAlchemy model for community signals."""
    __tablename__ = 'community_signals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True)
    source_id = Column(String(255), nullable=False, index=True)
    
    # Content fields
    content_type = Column(String(50))  # comment, question, feedback, prompt
    content_text = Column(Text)
    content_title = Column(String(500))
    content_author = Column(String(255))
    
    # Context fields
    platform = Column(String(50), index=True)
    parent_content = Column(String(255))
    category = Column(String(100))
    timestamp = Column(DateTime)
    
    # Metrics fields
    upvotes = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    reactions = Column(Text)  # JSON
    
    # Analysis fields
    sentiment = Column(String(20))
    sentiment_score = Column(Float)
    topics = Column(Text)  # JSON array
    intent = Column(String(50))
    
    # Universal metrics
    engagement_score = Column(Float)
    relevance_score = Column(Float)
    actionability = Column(Float)
    overall_score = Column(Float)
    
    # Metadata
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Database:
    """Manages database operations for community signals.
    
    Follows Single Responsibility Principle by handling only database operations.
    """

    def __init__(self, database_url: str, interactive: bool = True):
        """Initialize database connection.
        
        Args:
            database_url: Database URL (e.g., sqlite:///user_feedback.s3db)
            interactive: Whether to prompt for confirmation before creating database
        """
        self.database_url = database_url
        self._interactive = interactive
        
        # Check if database exists for SQLite
        if database_url.startswith("sqlite:///"):
            db_path = database_url.replace("sqlite:///", "")
            db_exists = Path(db_path).exists()
            
            if not db_exists and self._interactive:
                if not self._confirm_database_creation(db_path):
                    print("Database creation cancelled.")
                    sys.exit(0)
        
        # Create engine and session
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Initialize schema
        self._init_schema()
    
    def _confirm_database_creation(self, db_path: str) -> bool:
        """Prompt user for confirmation before creating database.
        
        Args:
            db_path: Path to database file
            
        Returns:
            True if user confirms, False otherwise
        """
        try:
            response = input(f"Database '{db_path}' does not exist. Create it? (y/n): ").strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return True
    
    def _init_schema(self):
        """Initialize database schema."""
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def get_session(self):
        """Get a database session context manager.
        
        Yields:
            SQLAlchemy session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def insert_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Insert or update a community signal.
        
        Args:
            signal_data: Community signal dictionary
            
        Returns:
            True if inserted (new), False if updated (duplicate)
        """
        with self.get_session() as session:
            # Check for existing signal
            existing = session.query(CommunitySignal).filter_by(
                source=signal_data['source'],
                source_id=signal_data['source_id']
            ).first()
            
            if existing:
                # Update existing signal
                self._update_signal(existing, signal_data)
                return False
            else:
                # Insert new signal
                signal = self._create_signal(signal_data)
                session.add(signal)
                return True
    
    def _create_signal(self, data: Dict[str, Any]) -> CommunitySignal:
        """Create CommunitySignal object from dictionary.
        
        Args:
            data: Community signal dictionary
            
        Returns:
            CommunitySignal object
        """
        content = data.get('content', {})
        context = data.get('context', {})
        metrics = data.get('metrics', {})
        analysis = data.get('analysis', {})
        universal = data.get('universal_metrics', {})
        
        # Parse timestamp
        timestamp = None
        if context.get('timestamp'):
            try:
                timestamp = datetime.fromisoformat(context['timestamp'])
            except (ValueError, TypeError):
                pass
        
        return CommunitySignal(
            source=data['source'],
            source_id=data['source_id'],
            content_type=content.get('type'),
            content_text=content.get('text'),
            content_title=content.get('title'),
            content_author=content.get('author'),
            platform=context.get('platform'),
            parent_content=context.get('parent_content'),
            category=context.get('category'),
            timestamp=timestamp,
            upvotes=metrics.get('upvotes', 0),
            replies=metrics.get('replies', 0),
            reactions=json.dumps(metrics.get('reactions', {})),
            sentiment=analysis.get('sentiment'),
            sentiment_score=analysis.get('sentiment_score'),
            topics=json.dumps(analysis.get('topics', [])),
            intent=analysis.get('intent'),
            engagement_score=universal.get('engagement_score'),
            relevance_score=universal.get('relevance_score'),
            actionability=universal.get('actionability'),
            overall_score=self._calculate_overall_score(universal, analysis)
        )
    
    def _update_signal(self, signal: CommunitySignal, data: Dict[str, Any]):
        """Update existing signal with new data.
        
        Args:
            signal: Existing CommunitySignal object
            data: New signal data
        """
        content = data.get('content', {})
        context = data.get('context', {})
        metrics = data.get('metrics', {})
        analysis = data.get('analysis', {})
        universal = data.get('universal_metrics', {})
        
        # Update fields
        signal.content_text = content.get('text', signal.content_text)
        signal.upvotes = metrics.get('upvotes', signal.upvotes)
        signal.replies = metrics.get('replies', signal.replies)
        signal.reactions = json.dumps(metrics.get('reactions', {}))
        signal.sentiment = analysis.get('sentiment', signal.sentiment)
        signal.sentiment_score = analysis.get('sentiment_score', signal.sentiment_score)
        signal.topics = json.dumps(analysis.get('topics', []))
        signal.engagement_score = universal.get('engagement_score', signal.engagement_score)
        signal.relevance_score = universal.get('relevance_score', signal.relevance_score)
        signal.actionability = universal.get('actionability', signal.actionability)
        signal.overall_score = self._calculate_overall_score(universal, analysis)
        signal.updated_at = datetime.utcnow()
    
    def _calculate_overall_score(
        self,
        universal: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall score from metrics.
        
        Args:
            universal: Universal metrics
            analysis: Analysis results
            
        Returns:
            Overall score
        """
        engagement = universal.get('engagement_score', 0.0)
        relevance = universal.get('relevance_score', 0.0)
        actionability = universal.get('actionability', 0.0)
        sentiment = analysis.get('sentiment_score', 0.0)
        
        # Normalize sentiment from -1..1 to 0..10
        normalized_sentiment = (sentiment + 1) * 5
        
        # Weighted average
        overall = (
            engagement * 0.25 +
            relevance * 0.25 +
            actionability * 0.35 +
            normalized_sentiment * 0.15
        )
        
        return round(overall, 2)
    
    def get_signal(self, source: str, source_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific signal by source and source_id.
        
        Args:
            source: Source name
            source_id: Source identifier
            
        Returns:
            Signal dictionary or None if not found
        """
        with self.get_session() as session:
            signal = session.query(CommunitySignal).filter_by(
                source=source,
                source_id=source_id
            ).first()
            
            if signal:
                return self._signal_to_dict(signal)
            return None
    
    def get_all_signals(
        self,
        limit: int = 20,
        order_by: str = "overall_score"
    ) -> List[Dict[str, Any]]:
        """Get all signals from database.
        
        Args:
            limit: Maximum number of records to return
            order_by: Column to order by
            
        Returns:
            List of signal dictionaries
        """
        with self.get_session() as session:
            query = session.query(CommunitySignal)
            
            # Apply ordering
            if hasattr(CommunitySignal, order_by):
                query = query.order_by(getattr(CommunitySignal, order_by).desc())
            
            signals = query.limit(limit).all()
            return [self._signal_to_dict(s) for s in signals]
    
    def count_signals(self) -> int:
        """Count total signals in database.
        
        Returns:
            Total count
        """
        with self.get_session() as session:
            return session.query(CommunitySignal).count()
    
    def count_by_source(self, source: str) -> int:
        """Count signals by source.
        
        Args:
            source: Source name
            
        Returns:
            Count for source
        """
        with self.get_session() as session:
            return session.query(CommunitySignal).filter_by(source=source).count()
    
    def _signal_to_dict(self, signal: CommunitySignal) -> Dict[str, Any]:
        """Convert CommunitySignal object to dictionary.
        
        Args:
            signal: CommunitySignal object
            
        Returns:
            Signal dictionary
        """
        return {
            'id': signal.id,
            'source': signal.source,
            'source_id': signal.source_id,
            'content': {
                'type': signal.content_type,
                'text': signal.content_text,
                'title': signal.content_title,
                'author': signal.content_author
            },
            'context': {
                'platform': signal.platform,
                'parent_content': signal.parent_content,
                'category': signal.category,
                'timestamp': signal.timestamp.isoformat() if signal.timestamp else None
            },
            'metrics': {
                'upvotes': signal.upvotes,
                'replies': signal.replies,
                'reactions': json.loads(signal.reactions) if signal.reactions else {}
            },
            'analysis': {
                'sentiment': signal.sentiment,
                'sentiment_score': signal.sentiment_score,
                'topics': json.loads(signal.topics) if signal.topics else [],
                'intent': signal.intent
            },
            'universal_metrics': {
                'engagement_score': signal.engagement_score,
                'relevance_score': signal.relevance_score,
                'actionability': signal.actionability
            },
            'overall_score': signal.overall_score,
            'processed': signal.processed,
            'created_at': signal.created_at.isoformat() if signal.created_at else None,
            'updated_at': signal.updated_at.isoformat() if signal.updated_at else None
        }
