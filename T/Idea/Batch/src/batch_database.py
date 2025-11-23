"""Database manager for batch processing operations.

This module provides database schema and utilities for tracking batch
processing jobs and individual item results.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone


class BatchDatabase:
    """Database manager for batch processing tracking."""
    
    def __init__(self, db_path: str = "batch.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._configure_connection()
    
    def _configure_connection(self):
        """Configure connection settings."""
        # Enable foreign key constraints in SQLite
        self.conn.execute("PRAGMA foreign_keys = ON")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Create database schema for batch tracking."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Create batch_jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT UNIQUE NOT NULL,
                total_items INTEGER NOT NULL,
                processed_items INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                config TEXT
            )
        """)
        
        # Create batch_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                idea_id TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                error TEXT,
                processing_time REAL,
                attempts INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batch_jobs(batch_id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_batch_jobs_batch_id 
            ON batch_jobs(batch_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_batch_items_batch_id 
            ON batch_items(batch_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_batch_items_status 
            ON batch_items(status)
        """)
        
        self.conn.commit()
    
    def create_batch_job(
        self,
        batch_id: str,
        total_items: int,
        config: Dict[str, Any]
    ) -> int:
        """Create a new batch job record.
        
        Args:
            batch_id: Unique batch identifier
            total_items: Total number of items to process
            config: Batch configuration dictionary
            
        Returns:
            Database row ID of created job
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO batch_jobs (
                batch_id, total_items, status, started_at, config
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            batch_id,
            total_items,
            'running',
            datetime.now(timezone.utc).isoformat(),
            json.dumps(config)
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def update_batch_job(
        self,
        batch_id: str,
        processed_items: Optional[int] = None,
        success_count: Optional[int] = None,
        failure_count: Optional[int] = None,
        status: Optional[str] = None
    ) -> None:
        """Update batch job record.
        
        Args:
            batch_id: Batch identifier
            processed_items: Number of processed items
            success_count: Number of successful items
            failure_count: Number of failed items
            status: Job status
        """
        if not self.conn:
            self.connect()
        
        updates = []
        values = []
        
        if processed_items is not None:
            updates.append("processed_items = ?")
            values.append(processed_items)
        
        if success_count is not None:
            updates.append("success_count = ?")
            values.append(success_count)
        
        if failure_count is not None:
            updates.append("failure_count = ?")
            values.append(failure_count)
        
        if status is not None:
            updates.append("status = ?")
            values.append(status)
            
            if status in ['completed', 'failed']:
                updates.append("completed_at = ?")
                values.append(datetime.now(timezone.utc).isoformat())
        
        if updates:
            values.append(batch_id)
            query = f"UPDATE batch_jobs SET {', '.join(updates)} WHERE batch_id = ?"
            self.conn.execute(query, values)
            self.conn.commit()
    
    def add_batch_item(
        self,
        batch_id: str,
        idea_id: str,
        status: str,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        processing_time: Optional[float] = None,
        attempts: int = 1
    ) -> int:
        """Add a batch item result.
        
        Args:
            batch_id: Batch identifier
            idea_id: Idea identifier
            status: Item status ('success' | 'failed')
            result: Processing result (will be JSON serialized)
            error: Error message if failed
            processing_time: Processing time in seconds
            attempts: Number of processing attempts
            
        Returns:
            Database row ID of created item
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO batch_items (
                batch_id, idea_id, status, result, error, 
                processing_time, attempts
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            batch_id,
            idea_id,
            status,
            json.dumps(result) if result else None,
            error,
            processing_time,
            attempts
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_batch_job(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get batch job by ID.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Batch job dictionary or None
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM batch_jobs WHERE batch_id = ?",
            (batch_id,)
        )
        
        row = cursor.fetchone()
        if row:
            job = dict(row)
            if job.get('config'):
                job['config'] = json.loads(job['config'])
            return job
        return None
    
    def get_batch_items(
        self,
        batch_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get batch items for a batch job.
        
        Args:
            batch_id: Batch identifier
            status: Optional status filter
            
        Returns:
            List of batch item dictionaries
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT * FROM batch_items WHERE batch_id = ? AND status = ?",
                (batch_id, status)
            )
        else:
            cursor.execute(
                "SELECT * FROM batch_items WHERE batch_id = ?",
                (batch_id,)
            )
        
        items = []
        for row in cursor.fetchall():
            item = dict(row)
            if item.get('result'):
                item['result'] = json.loads(item['result'])
            items.append(item)
        
        return items
    
    def list_batch_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List batch jobs.
        
        Args:
            status: Optional status filter
            limit: Maximum number of jobs to return
            
        Returns:
            List of batch job dictionaries
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT * FROM batch_jobs WHERE status = ? ORDER BY started_at DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM batch_jobs ORDER BY started_at DESC LIMIT ?",
                (limit,)
            )
        
        jobs = []
        for row in cursor.fetchall():
            job = dict(row)
            if job.get('config'):
                job['config'] = json.loads(job['config'])
            jobs.append(job)
        
        return jobs
    
    def delete_batch_job(self, batch_id: str) -> None:
        """Delete a batch job and all its items.
        
        Args:
            batch_id: Batch identifier
        """
        if not self.conn:
            self.connect()
        
        self.conn.execute("DELETE FROM batch_jobs WHERE batch_id = ?", (batch_id,))
        self.conn.commit()


__all__ = ["BatchDatabase"]
