"""Initialize or migrate the queue database.

This script initializes the worker task queue database with the proper schema
and PRAGMA settings optimized for Windows and the RTX 5090 system.

Usage:
    python scripts/init_queue_db.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from workers.queue_database import QueueDatabase


def main():
    """Initialize queue database."""
    # Database path: data/worker_queue.db
    db_path = Path(__file__).parent.parent / "data" / "worker_queue.db"
    
    print(f"Initializing queue database: {db_path}")
    print("=" * 70)
    
    # Create database (this will run schema initialization)
    queue_db = QueueDatabase(str(db_path))
    
    # Show PRAGMA settings
    print("\n📋 PRAGMA Settings:")
    pragma_info = queue_db.get_pragma_info()
    for key, value in pragma_info.items():
        print(f"  {key}: {value}")
    
    # Show database stats
    print("\n📊 Database Statistics:")
    stats = queue_db.get_stats()
    print(f"  Size: {stats['db_size_mb']:.2f} MB")
    print(f"  Active workers: {stats['active_workers']}")
    print(f"  Task counts by status: {stats['status_counts']}")
    
    # Verify tables exist
    print("\n✅ Verifying schema:")
    conn = queue_db.get_connection()
    try:
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  Tables: {', '.join(tables)}")
        
        # Check views
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' 
            ORDER BY name
        """)
        views = [row[0] for row in cursor.fetchall()]
        print(f"  Views: {', '.join(views)}")
        
        # Check indexes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"  Indexes: {', '.join(indexes)}")
        
    finally:
        conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Queue database initialized successfully!")
    print(f"   Location: {db_path}")


if __name__ == "__main__":
    main()
