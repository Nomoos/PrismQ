"""
SQLite Queue Configuration

Production-ready configuration for SQLite-based task queue based on
comprehensive benchmarking and performance research (Issue #337).

This configuration provides optimal balance between performance, durability,
and concurrency for the PrismQ task queue system on Windows with RTX 5090.
"""

from pathlib import Path
from typing import Dict, Any


# ==============================================================================
# PRAGMA Settings - Tuned for Production
# ==============================================================================

PRODUCTION_PRAGMAS: Dict[str, Any] = {
    # Essential for concurrency - allows concurrent readers with writers
    'journal_mode': 'WAL',
    
    # Balanced durability and performance
    # NORMAL = fsync at checkpoints (survives app crash)
    # FULL = fsync every commit (survives OS crash, but slower)
    'synchronous': 'NORMAL',
    
    # Handle lock contention gracefully - 5 second timeout
    # Allows retries before raising SQLITE_BUSY error
    'busy_timeout': 5000,
    
    # Checkpoint every 1000 pages (~4MB WAL file)
    # Balances WAL file size with checkpoint frequency
    'wal_autocheckpoint': 1000,
    
    # 20MB cache for better query performance
    # Negative value means KiB (kibibytes)
    # Adjust based on available RAM: -50000 for 50MB on high-memory systems
    'cache_size': -20000,
    
    # Store temporary tables in memory for better performance
    'temp_store': 'MEMORY',
    
    # Enable foreign key constraints
    'foreign_keys': 'ON',
    
    # Page size - 4096 bytes matches typical filesystem block size
    # Must be set before database is created
    'page_size': 4096,
    
    # Memory-mapped I/O - improves performance on Linux
    # WARNING: Test on Windows before enabling - may cause file locking issues
    # Uncomment if testing shows improvement on your Windows environment
    # 'mmap_size': 134217728,  # 128MB
}


# ==============================================================================
# Application Settings
# ==============================================================================

# Maximum concurrent workers for optimal performance
# Based on benchmark: 4-6 workers provides best throughput/error balance
# Beyond 6 workers: error rates increase significantly
MAX_CONCURRENT_WORKERS = 4

# Task claim retry configuration
TASK_CLAIM_RETRY_COUNT = 3
TASK_CLAIM_RETRY_BACKOFF_MS = 100  # Start with 100ms, use exponential backoff

# Error rate threshold for monitoring alerts
ERROR_RATE_ALERT_THRESHOLD = 0.05  # 5%

# Performance monitoring thresholds
LATENCY_P95_ALERT_THRESHOLD_MS = 20.0  # Alert if P95 latency > 20ms
WAL_FILE_SIZE_ALERT_THRESHOLD_MB = 50   # Alert if WAL file > 50MB


# ==============================================================================
# Database Configuration
# ==============================================================================

# Windows production database location
# IMPORTANT: Use local SSD, never network shares or cloud-synced folders
WINDOWS_DB_PATH = r"C:\Data\PrismQ\queue\queue.db"

# Linux/macOS development location
UNIX_DB_PATH = "/var/lib/prismq/queue/queue.db"


def get_default_db_path() -> str:
    """
    Get platform-appropriate database path.
    
    Returns:
        Default database path for the current platform
    """
    import platform
    
    if platform.system() == 'Windows':
        return WINDOWS_DB_PATH
    else:
        return UNIX_DB_PATH


def ensure_db_directory(db_path: str) -> None:
    """
    Ensure database directory exists.
    
    Args:
        db_path: Path to database file
    """
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# Connection Helper
# ==============================================================================

def apply_pragmas(connection) -> None:
    """
    Apply production PRAGMA settings to a database connection.
    
    Args:
        connection: sqlite3.Connection object
        
    Example:
        conn = sqlite3.connect(db_path)
        apply_pragmas(conn)
    """
    for pragma, value in PRODUCTION_PRAGMAS.items():
        if isinstance(value, str):
            connection.execute(f"PRAGMA {pragma}='{value}'")
        else:
            connection.execute(f"PRAGMA {pragma}={value}")


# ==============================================================================
# Performance Expectations
# ==============================================================================

# Based on benchmark results (Issue #337)
PERFORMANCE_TARGETS = {
    'best_case': {
        'throughput_tasks_per_minute': (300, 400),
        'claim_latency_p95_ms': 5.0,
        'error_rate_percent': 1.5,
        'concurrent_workers': (4, 6),
    },
    'realistic': {
        'throughput_tasks_per_minute': (200, 300),
        'claim_latency_p95_ms': 8.0,
        'error_rate_percent': 2.5,
        'concurrent_workers': 4,
    },
    'conservative': {
        'throughput_tasks_per_minute': (150, 200),
        'claim_latency_p95_ms': 10.0,
        'error_rate_percent': 3.0,
        'concurrent_workers': (2, 3),
    },
}


# ==============================================================================
# Windows-Specific Recommendations
# ==============================================================================

WINDOWS_SETUP_NOTES = """
Windows-Specific Setup Recommendations:

1. Database Location:
   - Use local SSD (C: drive recommended)
   - NEVER use network shares (UNC paths)
   - NEVER use cloud-synced folders (OneDrive, Dropbox, etc.)
   
2. Antivirus Exclusions:
   - Add database file to Windows Defender exclusions
   - Add entire database directory to antivirus exclusions
   - This prevents file scanning during database operations
   
3. Storage:
   - NVMe SSD: Best performance
   - SATA SSD: Good performance
   - HDD: Not recommended (significant slowdown)
   
4. Expected Performance (vs Linux):
   - Throughput: ~10-15% slower due to NTFS overhead
   - Latency: ~0.5-1.0ms higher due to file locking
   - Error rate: ~0.3-0.5% higher due to lock contention
   
5. Firewall:
   - No configuration needed (local file access only)
"""


# ==============================================================================
# Migration Path
# ==============================================================================

POSTGRESQL_MIGRATION_TRIGGERS = """
Consider migrating to PostgreSQL if:

1. Concurrent workers needed: > 10
2. Sustained throughput required: > 500 tasks/minute
3. Error rates consistently: > 5%
4. Multiple application servers needed (distributed queue)
5. Advanced features required: LISTEN/NOTIFY, table partitioning

SQLite is sufficient for current PrismQ requirements.
"""


# ==============================================================================
# Configuration Validation
# ==============================================================================

def validate_config() -> bool:
    """
    Validate configuration settings.
    
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate worker count
    if MAX_CONCURRENT_WORKERS < 1:
        raise ValueError("MAX_CONCURRENT_WORKERS must be >= 1")
    
    if MAX_CONCURRENT_WORKERS > 8:
        raise ValueError(
            f"MAX_CONCURRENT_WORKERS={MAX_CONCURRENT_WORKERS} is too high. "
            "SQLite performs poorly with >8 concurrent writers. "
            "Recommended: 4-6 workers."
        )
    
    # Validate retry settings
    if TASK_CLAIM_RETRY_COUNT < 1:
        raise ValueError("TASK_CLAIM_RETRY_COUNT must be >= 1")
    
    if TASK_CLAIM_RETRY_BACKOFF_MS < 10:
        raise ValueError("TASK_CLAIM_RETRY_BACKOFF_MS should be >= 10ms")
    
    # Validate PRAGMA settings
    if PRODUCTION_PRAGMAS.get('journal_mode') != 'WAL':
        raise ValueError("journal_mode must be WAL for concurrency")
    
    if PRODUCTION_PRAGMAS.get('synchronous') not in ('NORMAL', 'FULL'):
        raise ValueError("synchronous must be NORMAL or FULL")
    
    return True


# ==============================================================================
# Usage Example
# ==============================================================================

"""
Example usage in your application:

```python
import sqlite3
from Client.Backend.src.queue.config import (
    get_default_db_path,
    ensure_db_directory,
    apply_pragmas,
    MAX_CONCURRENT_WORKERS,
)

# Get database path
db_path = get_default_db_path()
ensure_db_directory(db_path)

# Create connection with production settings
conn = sqlite3.connect(db_path)
apply_pragmas(conn)

# Now use the connection
cursor = conn.execute("SELECT * FROM task_queue WHERE status = 'queued'")
# ...

conn.close()
```

For context managers:

```python
from contextlib import contextmanager

@contextmanager
def get_queue_connection():
    conn = sqlite3.connect(get_default_db_path())
    apply_pragmas(conn)
    try:
        yield conn
    finally:
        conn.close()

# Usage
with get_queue_connection() as conn:
    # Perform operations
    pass
```
"""

# Validate configuration on import
validate_config()
