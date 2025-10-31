"""Database management for Amazon Bestsellers source."""

import sqlite3
import json
import sys
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime


class Database:
    """Manages database operations for Amazon bestsellers collection."""

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
            response = input(f"Database '{self.db_path}' does not exist. Create it? (y/n): ").strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            # In non-interactive environments, return True
            return True
    
    def _init_db(self):
        """Initialize database schema."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                title TEXT NOT NULL,
                brand TEXT,
                category TEXT,
                price REAL,
                currency TEXT DEFAULT 'USD',
                description TEXT,
                tags TEXT,
                score REAL,
                score_dictionary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source, source_id)
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_id 
            ON products(source, source_id)
        """)
        
        conn.commit()
        conn.close()
    
    def insert_product(self, source: str, source_id: str, title: str,
                      brand: Optional[str] = None, category: Optional[str] = None,
                      price: Optional[float] = None, currency: str = "USD",
                      description: Optional[str] = None, tags: Optional[str] = None,
                      score: Optional[float] = None, score_dictionary: Optional[str] = None) -> bool:
        """Insert or update a product in the database.
        
        Args:
            source: Source platform (e.g., 'amazon_bestsellers')
            source_id: Unique identifier from source (ASIN for Amazon)
            title: Product title
            brand: Product brand
            category: Product category
            price: Product price
            currency: Currency code (default: USD)
            description: Product description
            tags: Comma-separated tags
            score: Calculated score
            score_dictionary: JSON string or dict of score components
            
        Returns:
            True if inserted (new), False if updated (duplicate)
        """
        # Convert dict to JSON string if needed
        if isinstance(score_dictionary, dict):
            score_dictionary = json.dumps(score_dictionary)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if product already exists
        cursor.execute(
            "SELECT id FROM products WHERE source = ? AND source_id = ?",
            (source, source_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing product
            cursor.execute("""
                UPDATE products 
                SET title = ?, brand = ?, category = ?, price = ?, currency = ?,
                    description = ?, tags = ?, score = ?, score_dictionary = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE source = ? AND source_id = ?
            """, (title, brand, category, price, currency, description, tags, 
                  score, score_dictionary, source, source_id))
            conn.commit()
            conn.close()
            return False
        else:
            # Insert new product
            cursor.execute("""
                INSERT INTO products 
                (source, source_id, title, brand, category, price, currency,
                 description, tags, score, score_dictionary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (source, source_id, title, brand, category, price, currency,
                  description, tags, score, score_dictionary))
            conn.commit()
            conn.close()
            return True
    
    def get_product(self, source: str, source_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific product by source and source_id.
        
        Args:
            source: Source platform
            source_id: Unique identifier from source
            
        Returns:
            Product dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM products WHERE source = ? AND source_id = ?",
            (source, source_id)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_products(self, limit: Optional[int] = None, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all products from the database.
        
        Args:
            limit: Maximum number of products to return
            source: Filter by source (optional)
            
        Returns:
            List of product dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if source:
            query = "SELECT * FROM products WHERE source = ? ORDER BY created_at DESC"
            params = (source,)
        else:
            query = "SELECT * FROM products ORDER BY created_at DESC"
            params = ()
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_products_by_category(self, category: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get products by category.
        
        Args:
            category: Category to filter by
            limit: Maximum number of products to return
            
        Returns:
            List of product dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM products WHERE category = ? ORDER BY score DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, (category,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total = cursor.fetchone()[0]
        
        # Products by source
        cursor.execute("SELECT source, COUNT(*) as count FROM products GROUP BY source")
        by_source = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Products by category
        cursor.execute("SELECT category, COUNT(*) as count FROM products GROUP BY category ORDER BY count DESC LIMIT 10")
        by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total': total,
            'by_source': by_source,
            'by_category': by_category
        }
