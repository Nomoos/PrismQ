"""Database management for CSV Import source."""

import sqlite3
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class Database:
    """Manages database operations for CSV import idea collection."""

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
        print(f"\nDatabase does not exist: {self.db_path}")
        print("A new database will be created.")
        response = input("Continue? (y/n): ").strip().lower()
        return response in ('y', 'yes')
    
    def _init_db(self):
        """Initialize database schema."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create ideas table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                notes TEXT,
                category TEXT,
                priority TEXT,
                status TEXT,
                created_by TEXT,
                assigned_to TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                used_at TEXT,
                age_days INTEGER,
                priority_score REAL,
                actionability REAL,
                raw_data TEXT,
                import_batch TEXT,
                import_timestamp TEXT
            )
        ''')
        
        # Create index on source_id for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_source_id ON ideas(source_id)
        ''')
        
        # Create index on status for filtering
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_status ON ideas(status)
        ''')
        
        # Create index on category for filtering
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category ON ideas(category)
        ''')
        
        # Create index on import_batch for batch operations
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_import_batch ON ideas(import_batch)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_ideas(self, ideas: List[Dict[str, Any]]) -> int:
        """Save ideas to database.
        
        Args:
            ideas: List of idea dictionaries
            
        Returns:
            Number of ideas saved
        """
        if not ideas:
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        saved_count = 0
        
        for idea in ideas:
            try:
                # Extract fields from idea dictionary
                source_id = idea.get('source_id', '')
                source = idea.get('source', 'csv_import')
                
                idea_data = idea.get('idea', {})
                title = idea_data.get('title', '')
                description = idea_data.get('description', '')
                notes = idea_data.get('notes', '')
                category = idea_data.get('category', 'general')
                priority = idea_data.get('priority', 'medium')
                
                metadata = idea.get('metadata', {})
                status = metadata.get('status', 'new')
                created_by = metadata.get('created_by', '')
                assigned_to = metadata.get('assigned_to', '')
                tags = ','.join(metadata.get('tags', []))
                
                tracking = idea.get('tracking', {})
                created_at = tracking.get('created_at', datetime.now().isoformat())
                modified_at = tracking.get('modified_at', datetime.now().isoformat())
                used_at = tracking.get('used_at')
                age_days = tracking.get('age_days', 0)
                
                universal_metrics = idea.get('universal_metrics', {})
                priority_score = universal_metrics.get('priority_score', 5.0)
                actionability = universal_metrics.get('actionability', 5.0)
                
                import_batch = idea.get('import_batch', '')
                import_timestamp = idea.get('import_timestamp', datetime.now().isoformat())
                
                # Store raw data as JSON
                raw_data = json.dumps(idea)
                
                # Insert or replace idea
                cursor.execute('''
                    INSERT OR REPLACE INTO ideas (
                        source_id, source, title, description, notes,
                        category, priority, status, created_by, assigned_to,
                        tags, created_at, modified_at, used_at, age_days,
                        priority_score, actionability, raw_data,
                        import_batch, import_timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    source_id, source, title, description, notes,
                    category, priority, status, created_by, assigned_to,
                    tags, created_at, modified_at, used_at, age_days,
                    priority_score, actionability, raw_data,
                    import_batch, import_timestamp
                ))
                
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving idea '{idea.get('source_id', 'unknown')}': {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return saved_count
    
    def get_ideas(self, status: Optional[str] = None, 
                  category: Optional[str] = None,
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve ideas from database.
        
        Args:
            status: Filter by status (optional)
            category: Filter by category (optional)
            limit: Maximum number of ideas to retrieve (optional)
            
        Returns:
            List of idea dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM ideas WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        ideas = []
        for row in rows:
            # Parse raw_data JSON if available
            try:
                idea = json.loads(row['raw_data'])
            except:
                # Fallback to constructing from columns
                idea = {
                    'source_id': row['source_id'],
                    'source': row['source'],
                    'idea': {
                        'title': row['title'],
                        'description': row['description'],
                        'notes': row['notes'],
                        'category': row['category'],
                        'priority': row['priority']
                    },
                    'metadata': {
                        'status': row['status'],
                        'created_by': row['created_by'],
                        'assigned_to': row['assigned_to'],
                        'tags': row['tags'].split(',') if row['tags'] else []
                    },
                    'tracking': {
                        'created_at': row['created_at'],
                        'modified_at': row['modified_at'],
                        'used_at': row['used_at'],
                        'age_days': row['age_days']
                    },
                    'universal_metrics': {
                        'priority_score': row['priority_score'],
                        'actionability': row['actionability']
                    }
                }
            ideas.append(idea)
        
        conn.close()
        return ideas
    
    def check_duplicate(self, source_id: str) -> bool:
        """Check if idea with given source_id already exists.
        
        Args:
            source_id: Unique identifier from source
            
        Returns:
            True if duplicate exists, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ideas WHERE source_id = ?", (source_id,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total ideas
        cursor.execute("SELECT COUNT(*) FROM ideas")
        total = cursor.fetchone()[0]
        
        # Ideas by status
        cursor.execute("SELECT status, COUNT(*) FROM ideas GROUP BY status")
        by_status = dict(cursor.fetchall())
        
        # Ideas by category
        cursor.execute("SELECT category, COUNT(*) FROM ideas GROUP BY category")
        by_category = dict(cursor.fetchall())
        
        # Ideas by priority
        cursor.execute("SELECT priority, COUNT(*) FROM ideas GROUP BY priority")
        by_priority = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total': total,
            'by_status': by_status,
            'by_category': by_category,
            'by_priority': by_priority
        }
