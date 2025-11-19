"""Tests for YouTube API Quota Manager.

This test suite verifies the quota tracking, limit enforcement,
and persistence functionality of the YouTubeQuotaManager.
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta

from src.core.youtube_quota_manager import (
    YouTubeQuotaManager,
    QuotaUsage,
    QuotaExceededException
)


@pytest.fixture
def temp_quota_db():
    """Create temporary quota database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


class TestQuotaManagerInitialization:
    """Test quota manager initialization."""
    
    def test_initialization_with_default_limits(self, temp_quota_db):
        """Test initialization with default quota limits."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db)
        
        assert manager.daily_limit == 10000
        assert manager.get_remaining_quota() == 10000
        assert Path(temp_quota_db).exists()
    
    def test_initialization_with_custom_limit(self, temp_quota_db):
        """Test initialization with custom quota limit."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=5000)
        
        assert manager.daily_limit == 5000
        assert manager.get_remaining_quota() == 5000
    
    def test_initialization_with_custom_quota_costs(self, temp_quota_db):
        """Test initialization with custom quota costs."""
        custom_costs = {
            'search.list': 150,
            'videos.list': 2
        }
        manager = YouTubeQuotaManager(
            db_path=temp_quota_db,
            quota_costs=custom_costs
        )
        
        assert manager.get_operation_cost('search.list') == 150
        assert manager.get_operation_cost('videos.list') == 2
    
    def test_database_schema_creation(self, temp_quota_db):
        """Test that database schema is created correctly."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db)
        
        conn = sqlite3.connect(temp_quota_db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        assert 'quota_usage' in tables
        assert 'quota_config' in tables


class TestQuotaOperations:
    """Test quota tracking and consumption."""
    
    def test_get_operation_cost_default(self, temp_quota_db):
        """Test getting operation cost for known operations."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db)
        
        assert manager.get_operation_cost('search.list') == 100
        assert manager.get_operation_cost('videos.list') == 1
        assert manager.get_operation_cost('channels.list') == 1
        assert manager.get_operation_cost('captions.list') == 50
    
    def test_get_operation_cost_unknown(self, temp_quota_db):
        """Test getting operation cost for unknown operation."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db)
        
        # Unknown operations default to 1 unit
        assert manager.get_operation_cost('unknown.operation') == 1
    
    def test_can_execute_with_sufficient_quota(self, temp_quota_db):
        """Test checking if operation can execute with sufficient quota."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        assert manager.can_execute('search.list') is True
        assert manager.can_execute('videos.list') is True
        assert manager.can_execute('search.list', count=50) is True  # 5000 units
    
    def test_can_execute_with_insufficient_quota(self, temp_quota_db):
        """Test checking if operation can execute with insufficient quota."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=50)
        
        assert manager.can_execute('videos.list') is True  # 1 unit
        assert manager.can_execute('search.list') is False  # 100 units
    
    def test_consume_quota_success(self, temp_quota_db):
        """Test consuming quota successfully."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        initial_remaining = manager.get_remaining_quota()
        
        manager.consume('videos.list')
        
        assert manager.get_remaining_quota() == initial_remaining - 1
    
    def test_consume_quota_multiple_times(self, temp_quota_db):
        """Test consuming quota multiple times."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        manager.consume('videos.list')
        manager.consume('videos.list')
        manager.consume('search.list')
        
        # Should have consumed: 1 + 1 + 100 = 102 units
        assert manager.get_remaining_quota() == 10000 - 102
    
    def test_consume_quota_with_count(self, temp_quota_db):
        """Test consuming quota with count parameter."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        manager.consume('videos.list', count=5)
        
        # Should have consumed: 1 * 5 = 5 units
        assert manager.get_remaining_quota() == 10000 - 5
    
    def test_consume_quota_exceeds_limit(self, temp_quota_db):
        """Test consuming quota that would exceed limit."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=50)
        
        with pytest.raises(QuotaExceededException) as exc_info:
            manager.consume('search.list')  # 100 units
        
        assert exc_info.value.operation == 'search.list'
        assert exc_info.value.cost == 100
        assert exc_info.value.remaining == 50
    
    def test_check_and_consume_success(self, temp_quota_db):
        """Test check_and_consume with sufficient quota."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        result = manager.check_and_consume('search.list')
        
        assert result is True
        assert manager.get_remaining_quota() == 10000 - 100
    
    def test_check_and_consume_failure(self, temp_quota_db):
        """Test check_and_consume with insufficient quota."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=50)
        
        result = manager.check_and_consume('search.list')
        
        assert result is False
        assert manager.get_remaining_quota() == 50  # Unchanged


class TestQuotaUsageTracking:
    """Test quota usage tracking and reporting."""
    
    def test_get_usage_empty(self, temp_quota_db):
        """Test getting usage when no quota consumed."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        usage = manager.get_usage()
        
        assert usage.total_used == 0
        assert usage.remaining == 10000
        assert usage.operations == {}
    
    def test_get_usage_with_consumption(self, temp_quota_db):
        """Test getting usage after consuming quota."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        manager.consume('videos.list')
        manager.consume('search.list')
        manager.consume('videos.list')
        
        usage = manager.get_usage()
        
        assert usage.total_used == 102  # 1 + 100 + 1
        assert usage.remaining == 9898
        assert usage.operations['videos.list'] == 2
        assert usage.operations['search.list'] == 100
    
    def test_get_usage_percentage(self, temp_quota_db):
        """Test getting usage as percentage."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        manager.consume('search.list')  # 100 units
        
        percentage = manager.get_usage_percentage()
        
        assert percentage == 1.0  # 100 / 10000 * 100
    
    def test_get_remaining_quota(self, temp_quota_db):
        """Test getting remaining quota."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        manager.consume('search.list')
        manager.consume('videos.list', count=10)
        
        remaining = manager.get_remaining_quota()
        
        assert remaining == 10000 - 100 - 10
    
    def test_get_usage_report(self, temp_quota_db):
        """Test getting usage report for multiple days."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        manager.consume('videos.list')
        
        report = manager.get_usage_report(days=3)
        
        assert len(report) == 3
        # Today should have usage
        today = list(report.keys())[0]
        assert report[today].total_used > 0


class TestQuotaConfiguration:
    """Test quota configuration and limits."""
    
    def test_set_daily_limit(self, temp_quota_db):
        """Test updating daily quota limit."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        manager.set_daily_limit(5000)
        
        assert manager.daily_limit == 5000
        assert manager.get_remaining_quota() <= 5000
    
    def test_reset_quota(self, temp_quota_db):
        """Test resetting quota for testing purposes."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        manager.consume('search.list')
        manager.consume('videos.list')
        
        assert manager.get_remaining_quota() < 10000
        
        manager.reset_quota()
        
        assert manager.get_remaining_quota() == 10000


class TestQuotaPersistence:
    """Test quota persistence across instances."""
    
    def test_quota_persists_across_instances(self, temp_quota_db):
        """Test that quota usage persists across manager instances."""
        # Create first manager and consume quota
        manager1 = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        manager1.consume('search.list')
        manager1.consume('videos.list', count=5)
        
        remaining1 = manager1.get_remaining_quota()
        
        # Create second manager with same database
        manager2 = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        remaining2 = manager2.get_remaining_quota()
        
        assert remaining1 == remaining2
        assert remaining2 == 10000 - 105  # 100 + 5


class TestQuotaEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_consume_zero_quota(self, temp_quota_db):
        """Test consuming zero quota units."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=10000)
        
        manager.consume('videos.list', count=0)
        
        assert manager.get_remaining_quota() == 10000
    
    def test_consume_at_exact_limit(self, temp_quota_db):
        """Test consuming exactly to the limit."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=100)
        
        manager.consume('search.list')  # 100 units
        
        assert manager.get_remaining_quota() == 0
    
    def test_cannot_consume_after_limit_reached(self, temp_quota_db):
        """Test that consumption fails after limit is reached."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db, daily_limit=100)
        
        manager.consume('search.list')  # 100 units
        
        with pytest.raises(QuotaExceededException):
            manager.consume('videos.list')  # Should fail
    
    def test_cleanup_old_records(self, temp_quota_db):
        """Test that old quota records are cleaned up."""
        manager = YouTubeQuotaManager(db_path=temp_quota_db)
        
        # Insert old record manually
        conn = sqlite3.connect(temp_quota_db)
        old_date = (datetime.now(timezone.utc) - timedelta(days=60)).strftime('%Y-%m-%d')
        conn.execute(
            '''
            INSERT INTO quota_usage (date, operation, cost, timestamp)
            VALUES (?, 'test.operation', 100, ?)
            ''',
            (old_date, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        conn.close()
        
        # Cleanup should remove records older than 30 days
        manager._cleanup_old_records(keep_days=30)
        
        # Verify old record is gone
        conn = sqlite3.connect(temp_quota_db)
        cursor = conn.execute('SELECT COUNT(*) FROM quota_usage WHERE date = ?', (old_date,))
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 0


class TestQuotaUsageDataClass:
    """Test QuotaUsage dataclass functionality."""
    
    def test_quota_usage_creation(self):
        """Test creating QuotaUsage object."""
        usage = QuotaUsage(
            date='2024-11-12',
            total_used=500,
            remaining=9500,
            operations={'search.list': 100, 'videos.list': 400}
        )
        
        assert usage.date == '2024-11-12'
        assert usage.total_used == 500
        assert usage.remaining == 9500
        assert len(usage.operations) == 2
    
    def test_quota_usage_to_dict(self):
        """Test converting QuotaUsage to dictionary."""
        usage = QuotaUsage(
            date='2024-11-12',
            total_used=500,
            remaining=9500,
            operations={'search.list': 100}
        )
        
        data = usage.to_dict()
        
        assert isinstance(data, dict)
        assert data['date'] == '2024-11-12'
        assert data['total_used'] == 500
        assert data['remaining'] == 9500
        assert data['operations'] == {'search.list': 100}


class TestQuotaExceededException:
    """Test QuotaExceededException."""
    
    def test_exception_attributes(self):
        """Test that exception has correct attributes."""
        exc = QuotaExceededException('search.list', 100, 50)
        
        assert exc.operation == 'search.list'
        assert exc.cost == 100
        assert exc.remaining == 50
        assert 'search.list' in str(exc)
        assert '100' in str(exc)
        assert '50' in str(exc)
