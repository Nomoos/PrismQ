"""Database management for GoogleTrendsSource."""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class Database:
    """Manages SQLite database operations for Google Trends signals."""

    def __init__(self, database_path: str, interactive: bool = True):
        """Initialize database connection.
        
        Args:
            database_path: Path to SQLite database file
            interactive: Whether to prompt for confirmations (default: True)
        """
        self.database_path = database_path
        self._interactive = interactive
        
        # Ensure database directory exists
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Create signals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                tags TEXT,
                metrics TEXT,
                temporal TEXT,
                universal_metrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source, source_id)
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_signal_type 
            ON signals(source, signal_type)
        """)
        
        conn.commit()
        conn.close()
    
    def insert_signal(
        self,
        source: str,
        source_id: str,
        signal_type: str,
        name: str,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        temporal: Optional[Dict[str, Any]] = None,
        universal_metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Insert a signal into the database.
        
        Args:
            source: Signal source name
            source_id: Unique identifier from source
            signal_type: Type of signal (trend, hashtag, meme, etc.)
            name: Signal name
            description: Signal description
            tags: Comma-separated tags
            metrics: Signal-specific metrics dictionary
            temporal: Temporal data dictionary
            universal_metrics: Universal metrics dictionary
            
        Returns:
            True if inserted successfully, False if duplicate
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO signals (
                    source, source_id, signal_type, name, description, 
                    tags, metrics, temporal, universal_metrics
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source,
                source_id,
                signal_type,
                name,
                description,
                tags,
                json.dumps(metrics) if metrics else None,
                json.dumps(temporal) if temporal else None,
                json.dumps(universal_metrics) if universal_metrics else None
            ))
            
            conn.commit()
            return True
            
        except sqlite3.IntegrityError:
            # Duplicate entry
            return False
        finally:
            conn.close()
    
    def get_all_signals(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all signals from the database.
        
        Args:
            limit: Maximum number of signals to return
            
        Returns:
            List of signal dictionaries
        """
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM signals ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        signals = []
        for row in rows:
            signal = dict(row)
            # Parse JSON fields
            if signal['metrics']:
                signal['metrics'] = json.loads(signal['metrics'])
            if signal['temporal']:
                signal['temporal'] = json.loads(signal['temporal'])
            if signal['universal_metrics']:
                signal['universal_metrics'] = json.loads(signal['universal_metrics'])
            signals.append(signal)
        
        conn.close()
        return signals
    
    def get_signals_by_type(
        self, 
        signal_type: str, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get signals by type.
        
        Args:
            signal_type: Type of signal to filter by
            limit: Maximum number of signals to return
            
        Returns:
            List of signal dictionaries
        """
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM signals WHERE signal_type = ? ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, (signal_type,))
        rows = cursor.fetchall()
        
        signals = []
        for row in rows:
            signal = dict(row)
            # Parse JSON fields
            if signal['metrics']:
                signal['metrics'] = json.loads(signal['metrics'])
            if signal['temporal']:
                signal['temporal'] = json.loads(signal['temporal'])
            if signal['universal_metrics']:
                signal['universal_metrics'] = json.loads(signal['universal_metrics'])
            signals.append(signal)
        
        conn.close()
        return signals
    
    def get_signal_count(self) -> int:
        """Get total count of signals.
        
        Returns:
            Number of signals in database
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM signals")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
