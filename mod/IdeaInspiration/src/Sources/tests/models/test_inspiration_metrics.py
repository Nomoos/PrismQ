"""Tests for the InspirationMetrics model."""

from datetime import datetime
import pytest
from src.models.inspiration_metrics import InspirationMetrics


class TestInspirationMetrics:
    """Test cases for InspirationMetrics dataclass."""
    
    def test_inspiration_metrics_should_initialize_with_default_values(self):
        """Test that InspirationMetrics initializes with default values."""
        # Arrange & Act
        metrics = InspirationMetrics()
        
        # Assert
        assert metrics is not None
        assert metrics.id == ""
        assert metrics.inspiration_item_id == ""
        assert metrics.views is None
        assert metrics.likes is None
        assert metrics.comments is None
        assert metrics.shares is None
        assert metrics.saves is None
        assert metrics.avg_watch_time_sec is None
        assert metrics.length_sec is None
        assert metrics.conversions is None
        assert metrics.engagement_rate_pct is None
        assert metrics.watch_through_pct is None
        assert metrics.conversion_rate_pct is None
        assert metrics.rpi_engagement is None
        assert metrics.rpi_watch_through is None
        assert metrics.computed_at == datetime.min
        assert metrics.engagement_baseline_id is None
        assert metrics.watch_through_baseline_id is None
        assert metrics.conversion_baseline_id is None
    
    def test_inspiration_metrics_should_allow_property_assignment(self):
        """Test that InspirationMetrics allows property assignment."""
        # Arrange
        computed_at = datetime.now()
        
        # Act
        metrics = InspirationMetrics(
            id="metrics123",
            inspiration_item_id="item456",
            views=10000,
            likes=500,
            comments=50,
            shares=100,
            saves=75,
            avg_watch_time_sec=45.5,
            length_sec=60.0,
            conversions=25,
            engagement_rate_pct=150,
            watch_through_pct=120,
            conversion_rate_pct=200,
            rpi_engagement=145,
            rpi_watch_through=130,
            computed_at=computed_at,
            engagement_baseline_id="baseline1",
            watch_through_baseline_id="baseline2",
            conversion_baseline_id="baseline3"
        )
        
        # Assert
        assert metrics.id == "metrics123"
        assert metrics.inspiration_item_id == "item456"
        assert metrics.views == 10000
        assert metrics.likes == 500
        assert metrics.comments == 50
        assert metrics.shares == 100
        assert metrics.saves == 75
        assert metrics.avg_watch_time_sec == 45.5
        assert metrics.length_sec == 60.0
        assert metrics.conversions == 25
        assert metrics.engagement_rate_pct == 150
        assert metrics.watch_through_pct == 120
        assert metrics.conversion_rate_pct == 200
        assert metrics.rpi_engagement == 145
        assert metrics.rpi_watch_through == 130
        assert metrics.computed_at == computed_at
        assert metrics.engagement_baseline_id == "baseline1"
        assert metrics.watch_through_baseline_id == "baseline2"
        assert metrics.conversion_baseline_id == "baseline3"
    
    @pytest.mark.parametrize("percent_value", [
        0,      # At zero (minimum valid value)
        50,     # Below baseline
        100,    # At baseline
        150,    # Above baseline
        500,    # Viral content
    ])
    def test_inspiration_metrics_should_accept_valid_percentage_values(self, percent_value):
        """Test that InspirationMetrics accepts valid percentage values."""
        # Arrange & Act
        metrics = InspirationMetrics(
            engagement_rate_pct=percent_value,
            watch_through_pct=percent_value,
            conversion_rate_pct=percent_value,
            rpi_engagement=percent_value,
            rpi_watch_through=percent_value
        )
        
        # Assert
        assert metrics.engagement_rate_pct == percent_value
        assert metrics.watch_through_pct == percent_value
        assert metrics.conversion_rate_pct == percent_value
        assert metrics.rpi_engagement == percent_value
        assert metrics.rpi_watch_through == percent_value
