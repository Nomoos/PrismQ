"""Database operations for CalendarHolidays source."""

import sqlite3
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class Database:
    """Manages database operations for event collection."""

    def __init__(self, db_path: str, interactive: bool = True):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
            interactive: Whether to prompt for confirmation before creating database
        """
        self.db_path = db_path
        self._interactive = interactive
        
        # Check if database already exists
        db_exists = Path(db_path).exists()
        
        # If database doesn't exist and we're in interactive mode, ask for confirmation
        if not db_exists and self._interactive:
            if not self._confirm_database_creation():
                print("Database creation cancelled.")
                sys.exit(0)
        
        # Initialize database schema
        self._init_db()
    
    def _confirm_database_creation(self) -> bool:
        """Prompt user for confirmation before creating database.
        
        Returns:
            True if user confirms, False otherwise
        """
        try:
            response = input(
                f"Database '{self.db_path}' does not exist. Create it? (y/n): "
            ).strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return True
    
    def _init_db(self):
        """Initialize database schema."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                name TEXT NOT NULL,
                event_type TEXT,
                date TEXT NOT NULL,
                recurring INTEGER DEFAULT 0,
                recurrence_pattern TEXT,
                scope TEXT,
                importance TEXT,
                audience_size_estimate INTEGER,
                pre_event_days INTEGER,
                post_event_days INTEGER,
                peak_day TEXT,
                metadata TEXT,
                universal_metrics TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source, source_id)
            )
        """)
        
        # Create index on date for efficient queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_date ON events(date)
        """)
        
        # Create index on source for efficient filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_source ON events(source)
        """)
        
        conn.commit()
        conn.close()
    
    def insert_event(
        self,
        source: str,
        source_id: str,
        name: str,
        event_type: str,
        date: str,
        recurring: bool = False,
        recurrence_pattern: Optional[str] = None,
        scope: Optional[str] = None,
        importance: Optional[str] = None,
        audience_size_estimate: Optional[int] = None,
        pre_event_days: Optional[int] = None,
        post_event_days: Optional[int] = None,
        peak_day: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        universal_metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Insert or update an event in the database.
        
        Args:
            source: Source platform
            source_id: Unique identifier from source
            name: Event name
            event_type: Type of event (holiday, sports, etc.)
            date: Event date (ISO format)
            recurring: Whether event recurs
            recurrence_pattern: Pattern of recurrence
            scope: Scope of event (global, national, etc.)
            importance: Importance level (major, moderate, minor)
            audience_size_estimate: Estimated audience size
            pre_event_days: Days before event to start coverage
            post_event_days: Days after event to continue coverage
            peak_day: Peak day for the event
            metadata: Additional metadata as dictionary
            universal_metrics: Universal metrics as dictionary
            
        Returns:
            True if inserted (new), False if updated (duplicate)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert metadata to JSON
        metadata_json = json.dumps(metadata) if metadata else None
        metrics_json = json.dumps(universal_metrics) if universal_metrics else None
        
        try:
            cursor.execute("""
                INSERT INTO events (
                    source, source_id, name, event_type, date, recurring,
                    recurrence_pattern, scope, importance, audience_size_estimate,
                    pre_event_days, post_event_days, peak_day, metadata, universal_metrics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source, source_id, name, event_type, date, int(recurring),
                recurrence_pattern, scope, importance, audience_size_estimate,
                pre_event_days, post_event_days, peak_day, metadata_json, metrics_json
            ))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Event already exists, update it
            cursor.execute("""
                UPDATE events SET
                    name = ?, event_type = ?, date = ?, recurring = ?,
                    recurrence_pattern = ?, scope = ?, importance = ?,
                    audience_size_estimate = ?, pre_event_days = ?,
                    post_event_days = ?, peak_day = ?, metadata = ?,
                    universal_metrics = ?
                WHERE source = ? AND source_id = ?
            """, (
                name, event_type, date, int(recurring), recurrence_pattern,
                scope, importance, audience_size_estimate, pre_event_days,
                post_event_days, peak_day, metadata_json, metrics_json,
                source, source_id
            ))
            conn.commit()
            conn.close()
            return False
    
    def get_all_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all events from the database.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM events ORDER BY date DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            event = dict(row)
            # Parse JSON fields
            if event['metadata']:
                event['metadata'] = json.loads(event['metadata'])
            if event['universal_metrics']:
                event['universal_metrics'] = json.loads(event['universal_metrics'])
            events.append(event)
        
        return events
    
    def get_event(self, source: str, source_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific event by source and source_id.
        
        Args:
            source: Source platform
            source_id: Unique identifier from source
            
        Returns:
            Event dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM events WHERE source = ? AND source_id = ?",
            (source, source_id)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            event = dict(row)
            if event['metadata']:
                event['metadata'] = json.loads(event['metadata'])
            if event['universal_metrics']:
                event['universal_metrics'] = json.loads(event['universal_metrics'])
            return event
        return None
