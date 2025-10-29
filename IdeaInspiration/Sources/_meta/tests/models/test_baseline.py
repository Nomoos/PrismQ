"""Tests for the Baseline model."""

from datetime import datetime
import pytest
from src.models.baseline import Baseline


class TestBaseline:
    """Test cases for Baseline dataclass."""
    
    def test_baseline_should_initialize_with_default_values(self):
        """Test that Baseline initializes with default values."""
        # Arrange & Act
        baseline = Baseline()
        
        # Assert
        assert baseline is not None
        assert baseline.id == ""
        assert baseline.scope_type == ""
        assert baseline.scope_key is None
        assert baseline.metric == ""
        assert baseline.platform is None
        assert baseline.category is None
        assert baseline.region is None
        assert baseline.length_bucket is None
        assert baseline.window == ""
        assert baseline.sample_size is None
        assert baseline.baseline_value == 0.0
        assert baseline.baseline_units == ""
        assert baseline.method is None
        assert baseline.notes is None
        assert baseline.computed_at == datetime.min
    
    def test_baseline_should_allow_property_assignment(self):
        """Test that Baseline allows property assignment."""
        # Arrange
        computed_at = datetime.now()
        
        # Act
        baseline = Baseline(
            id="baseline123",
            scope_type="account",
            scope_key="channel456",
            metric="engagement_rate",
            platform="YouTube",
            category="tech",
            region="US",
            length_bucket="31-60s",
            window="P28D",
            sample_size=150,
            baseline_value=0.045,
            baseline_units="ratio",
            method="median",
            notes="Rolling 28-day median for account",
            computed_at=computed_at
        )
        
        # Assert
        assert baseline.id == "baseline123"
        assert baseline.scope_type == "account"
        assert baseline.scope_key == "channel456"
        assert baseline.metric == "engagement_rate"
        assert baseline.platform == "YouTube"
        assert baseline.category == "tech"
        assert baseline.region == "US"
        assert baseline.length_bucket == "31-60s"
        assert baseline.window == "P28D"
        assert baseline.sample_size == 150
        assert baseline.baseline_value == 0.045
        assert baseline.baseline_units == "ratio"
        assert baseline.method == "median"
        assert baseline.notes == "Rolling 28-day median for account"
        assert baseline.computed_at == computed_at
