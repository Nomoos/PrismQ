"""Tests for Statistical Analysis module."""

import os
import sys

import pytest

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from statistics import (
    SignificanceResult,
    VariantMetrics,
    calculate_significance,
    compare_all_variants,
    find_overall_winner,
)


class TestVariantMetrics:
    """Tests for VariantMetrics class."""

    def test_create_valid_metrics(self):
        """Test creating valid metrics."""
        metrics = VariantMetrics(variant_id="A", views=1000, clicks=100, engagement_score=0.75)

        assert metrics.variant_id == "A"
        assert metrics.views == 1000
        assert metrics.clicks == 100
        assert metrics.engagement_score == 0.75
        assert metrics.ctr == 10.0  # (100/1000) * 100

    def test_ctr_calculation(self):
        """Test CTR calculation."""
        metrics = VariantMetrics(variant_id="A", views=2000, clicks=250, engagement_score=0.8)

        assert metrics.ctr == 12.5

    def test_ctr_zero_views(self):
        """Test CTR with zero views."""
        metrics = VariantMetrics(variant_id="A", views=0, clicks=0, engagement_score=0.0)

        assert metrics.ctr == 0.0

    def test_negative_views_validation(self):
        """Test views cannot be negative."""
        with pytest.raises(ValueError, match="views cannot be negative"):
            VariantMetrics(variant_id="A", views=-100, clicks=10, engagement_score=0.5)

    def test_negative_clicks_validation(self):
        """Test clicks cannot be negative."""
        with pytest.raises(ValueError, match="clicks cannot be negative"):
            VariantMetrics(variant_id="A", views=100, clicks=-10, engagement_score=0.5)

    def test_clicks_exceed_views_validation(self):
        """Test clicks cannot exceed views."""
        with pytest.raises(ValueError, match="clicks cannot exceed views"):
            VariantMetrics(variant_id="A", views=100, clicks=150, engagement_score=0.5)

    def test_engagement_score_validation(self):
        """Test engagement_score must be between 0 and 1."""
        with pytest.raises(ValueError, match="engagement_score must be between 0 and 1"):
            VariantMetrics(variant_id="A", views=100, clicks=10, engagement_score=1.5)


class TestCalculateSignificance:
    """Tests for calculate_significance function."""

    def test_ctr_significance_clear_winner(self):
        """Test CTR significance with clear winner."""
        variant_a = VariantMetrics(
            variant_id="A", views=2000, clicks=200, engagement_score=0.7  # 10% CTR
        )

        variant_b = VariantMetrics(
            variant_id="B", views=2000, clicks=300, engagement_score=0.75  # 15% CTR
        )

        result = calculate_significance(variant_a, variant_b, "ctr")

        assert isinstance(result, SignificanceResult)
        assert result.winning_variant == "B"
        assert result.is_significant  # Should be significant with this difference
        assert 0 <= result.p_value <= 1
        assert 0 <= result.confidence <= 100

    def test_ctr_significance_no_difference(self):
        """Test CTR significance with no difference."""
        variant_a = VariantMetrics(variant_id="A", views=1000, clicks=100, engagement_score=0.7)

        variant_b = VariantMetrics(variant_id="B", views=1000, clicks=100, engagement_score=0.7)

        result = calculate_significance(variant_a, variant_b, "ctr")

        assert isinstance(result, SignificanceResult)
        assert not result.is_significant
        assert result.p_value > 0.05

    def test_insufficient_sample_size(self):
        """Test error with insufficient sample size."""
        variant_a = VariantMetrics(variant_id="A", views=50, clicks=5, engagement_score=0.5)

        variant_b = VariantMetrics(variant_id="B", views=50, clicks=10, engagement_score=0.6)

        with pytest.raises(ValueError, match="at least 100 views"):
            calculate_significance(variant_a, variant_b, "ctr")

    def test_engagement_significance(self):
        """Test engagement significance calculation."""
        variant_a = VariantMetrics(variant_id="A", views=1500, clicks=150, engagement_score=0.6)

        variant_b = VariantMetrics(variant_id="B", views=1500, clicks=160, engagement_score=0.8)

        result = calculate_significance(variant_a, variant_b, "engagement")

        assert isinstance(result, SignificanceResult)
        assert result.winning_variant == "B"
        assert 0 <= result.p_value <= 1
        assert 0 <= result.confidence <= 100

    def test_views_significance(self):
        """Test views significance calculation."""
        variant_a = VariantMetrics(variant_id="A", views=1200, clicks=120, engagement_score=0.7)

        variant_b = VariantMetrics(variant_id="B", views=800, clicks=80, engagement_score=0.7)

        result = calculate_significance(variant_a, variant_b, "views")

        assert isinstance(result, SignificanceResult)
        assert result.winning_variant == "A"
        assert 0 <= result.p_value <= 1

    def test_invalid_metric(self):
        """Test error with invalid metric."""
        variant_a = VariantMetrics(variant_id="A", views=1000, clicks=100, engagement_score=0.7)

        variant_b = VariantMetrics(variant_id="B", views=1000, clicks=120, engagement_score=0.75)

        with pytest.raises(ValueError, match="Unsupported metric"):
            calculate_significance(variant_a, variant_b, "invalid_metric")


class TestCompareAllVariants:
    """Tests for compare_all_variants function."""

    def test_compare_three_variants(self):
        """Test pairwise comparison of three variants."""
        variants = [
            VariantMetrics("A", 1000, 80, 0.6),
            VariantMetrics("B", 1000, 100, 0.7),
            VariantMetrics("C", 1000, 120, 0.8),
        ]

        results = compare_all_variants(variants, "ctr")

        # Should have 3 pairwise comparisons: A-B, A-C, B-C
        assert len(results) == 3

        # Check structure
        for v1_id, v2_id, sig_result in results:
            assert v1_id in ["A", "B", "C"]
            assert v2_id in ["A", "B", "C"]
            assert isinstance(sig_result, SignificanceResult)

    def test_compare_two_variants(self):
        """Test comparison with two variants (single pair)."""
        variants = [VariantMetrics("A", 1000, 100, 0.7), VariantMetrics("B", 1000, 120, 0.75)]

        results = compare_all_variants(variants, "ctr")

        # Should have 1 comparison
        assert len(results) == 1
        assert results[0][0] == "A"
        assert results[0][1] == "B"


class TestFindOverallWinner:
    """Tests for find_overall_winner function."""

    def test_clear_winner_three_variants(self):
        """Test finding clear winner among three variants."""
        variants = [
            VariantMetrics("A", 2000, 150, 0.6),  # 7.5% CTR
            VariantMetrics("B", 2000, 250, 0.75),  # 12.5% CTR
            VariantMetrics("C", 2000, 180, 0.65),  # 9% CTR
        ]

        result = find_overall_winner(variants, "ctr")

        assert result is not None
        winner_id, wins = result
        assert winner_id == "B"  # B has highest CTR
        assert wins > 0

    def test_no_clear_winner_similar_performance(self):
        """Test when variants perform similarly."""
        variants = [
            VariantMetrics("A", 500, 50, 0.7),
            VariantMetrics("B", 500, 51, 0.71),
            VariantMetrics("C", 500, 52, 0.72),
        ]

        result = find_overall_winner(variants, "ctr")

        # With small differences and moderate sample size,
        # may or may not find significant winner
        # Just verify it returns valid result or None
        if result:
            winner_id, wins = result
            assert winner_id in ["A", "B", "C"]
            assert wins >= 0

    def test_single_variant(self):
        """Test with single variant (no comparison possible)."""
        variants = [VariantMetrics("A", 1000, 100, 0.7)]

        result = find_overall_winner(variants, "ctr")

        assert result is None

    def test_two_variants(self):
        """Test with two variants."""
        variants = [VariantMetrics("A", 2000, 200, 0.7), VariantMetrics("B", 2000, 300, 0.8)]

        result = find_overall_winner(variants, "ctr")

        assert result is not None
        winner_id, wins = result
        assert winner_id == "B"
        assert wins == 1


class TestStatisticalAccuracy:
    """Tests for statistical calculation accuracy."""

    def test_known_significant_difference(self):
        """Test with known statistically significant difference."""
        # Large sample with clear difference should be significant
        variant_a = VariantMetrics(
            variant_id="A", views=5000, clicks=500, engagement_score=0.7  # 10% CTR
        )

        variant_b = VariantMetrics(
            variant_id="B", views=5000, clicks=750, engagement_score=0.8  # 15% CTR
        )

        result = calculate_significance(variant_a, variant_b, "ctr")

        assert result.is_significant
        assert result.p_value < 0.05
        assert result.winning_variant == "B"

    def test_known_not_significant(self):
        """Test with known non-significant difference."""
        # Small difference with moderate sample should not be significant
        variant_a = VariantMetrics(
            variant_id="A", views=200, clicks=20, engagement_score=0.7  # 10% CTR
        )

        variant_b = VariantMetrics(
            variant_id="B", views=200, clicks=21, engagement_score=0.71  # 10.5% CTR
        )

        result = calculate_significance(variant_a, variant_b, "ctr")

        # Very small difference should not be significant
        assert not result.is_significant
        assert result.p_value > 0.05
