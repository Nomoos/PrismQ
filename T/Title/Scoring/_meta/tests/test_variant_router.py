"""Tests for Variant Router module."""

import os
import sys

import pytest

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from test_manager import TitleVariant
from variant_router import VariantRouter, assign_variant


class TestAssignVariant:
    """Tests for assign_variant function."""

    def test_consistent_assignment(self):
        """Test that same user gets same variant consistently."""
        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        user_id = "user123"

        # Assign multiple times
        assignment1 = assign_variant(user_id, variants)
        assignment2 = assign_variant(user_id, variants)
        assignment3 = assign_variant(user_id, variants)

        # Should always get same variant
        assert assignment1.variant_id == assignment2.variant_id
        assert assignment2.variant_id == assignment3.variant_id

    def test_different_users_can_get_different_variants(self):
        """Test that different users can get different variants."""
        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        # Test with multiple users
        assignments = []
        for i in range(100):
            user_id = f"user{i}"
            variant = assign_variant(user_id, variants)
            assignments.append(variant.variant_id)

        # Should have both A and B in results
        assert "A" in assignments
        assert "B" in assignments

    def test_traffic_distribution_accuracy(self):
        """Test that traffic distribution matches percentages within tolerance."""
        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        # Simulate 1000 users
        assignments = {"A": 0, "B": 0}
        for i in range(1000):
            user_id = f"user{i}"
            variant = assign_variant(user_id, variants)
            assignments[variant.variant_id] += 1

        # Check distribution (allow ±5% tolerance)
        a_percent = (assignments["A"] / 1000) * 100
        b_percent = (assignments["B"] / 1000) * 100

        assert 45 <= a_percent <= 55
        assert 45 <= b_percent <= 55

    def test_uneven_traffic_split(self):
        """Test uneven traffic distribution (70/30 split)."""
        variants = [TitleVariant("A", "Title A", 70), TitleVariant("B", "Title B", 30)]

        # Simulate 1000 users
        assignments = {"A": 0, "B": 0}
        for i in range(1000):
            user_id = f"user{i}"
            variant = assign_variant(user_id, variants)
            assignments[variant.variant_id] += 1

        # Check distribution (allow ±5% tolerance)
        a_percent = (assignments["A"] / 1000) * 100
        b_percent = (assignments["B"] / 1000) * 100

        assert 65 <= a_percent <= 75
        assert 25 <= b_percent <= 35

    def test_three_way_split(self):
        """Test three-variant split (33/33/34)."""
        variants = [
            TitleVariant("A", "Title A", 33.33),
            TitleVariant("B", "Title B", 33.33),
            TitleVariant("C", "Title C", 33.34),
        ]

        # Simulate 900 users
        assignments = {"A": 0, "B": 0, "C": 0}
        for i in range(900):
            user_id = f"user{i}"
            variant = assign_variant(user_id, variants)
            assignments[variant.variant_id] += 1

        # Each should get roughly 300 (±5%)
        for variant_id in ["A", "B", "C"]:
            percent = (assignments[variant_id] / 900) * 100
            assert 28 <= percent <= 38

    def test_empty_variants_list(self):
        """Test error with empty variants list."""
        variants = []

        with pytest.raises(ValueError, match="variants list cannot be empty"):
            assign_variant("user123", variants)

    def test_invalid_traffic_distribution(self):
        """Test error with invalid traffic percentages."""
        variants = [TitleVariant("A", "Title A", 40), TitleVariant("B", "Title B", 40)]

        with pytest.raises(ValueError, match="Traffic percentages must sum to 100"):
            assign_variant("user123", variants)


class TestVariantRouter:
    """Tests for VariantRouter class."""

    def test_assign_and_track(self):
        """Test assigning and tracking user assignments."""
        router = VariantRouter()

        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        variant = router.assign("user123", variants)

        assert variant.variant_id in ["A", "B"]
        assert router.get_assignment("user123") == variant.variant_id

    def test_get_assignment_not_found(self):
        """Test getting assignment for user who hasn't been assigned."""
        router = VariantRouter()

        assert router.get_assignment("unknown_user") is None

    def test_verify_consistency(self):
        """Test verifying assignment consistency."""
        router = VariantRouter()

        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        # First assignment
        router.assign("user123", variants)

        # Verify consistency
        assert router.verify_consistency("user123", variants)

    def test_verify_consistency_no_previous_assignment(self):
        """Test verify_consistency with no previous assignment."""
        router = VariantRouter()

        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        # No previous assignment should return True
        assert router.verify_consistency("user999", variants)

    def test_get_distribution_stats(self):
        """Test calculating distribution statistics."""
        router = VariantRouter()

        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        # Assign 100 users
        for i in range(100):
            router.assign(f"user{i}", variants)

        stats = router.get_distribution_stats(variants)

        # Should have stats for both variants
        assert "A" in stats
        assert "B" in stats

        # Percentages should sum to ~100
        total_percent = stats["A"] + stats["B"]
        assert 99 <= total_percent <= 101

        # Each should be close to 50% (±10% tolerance for small sample)
        assert 40 <= stats["A"] <= 60
        assert 40 <= stats["B"] <= 60

    def test_get_distribution_stats_empty(self):
        """Test distribution stats with no assignments."""
        router = VariantRouter()

        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        stats = router.get_distribution_stats(variants)

        assert stats["A"] == 0.0
        assert stats["B"] == 0.0

    def test_clear_assignments(self):
        """Test clearing all assignments."""
        router = VariantRouter()

        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        # Assign some users
        router.assign("user1", variants)
        router.assign("user2", variants)

        assert router.get_assignment("user1") is not None
        assert router.get_assignment("user2") is not None

        # Clear assignments
        router.clear_assignments()

        assert router.get_assignment("user1") is None
        assert router.get_assignment("user2") is None


class TestTrafficSplitting:
    """Tests for traffic splitting accuracy."""

    def test_50_50_split_large_sample(self):
        """Test 50/50 split with large sample."""
        router = VariantRouter()

        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        # Simulate 10,000 users
        for i in range(10000):
            router.assign(f"user{i}", variants)

        stats = router.get_distribution_stats(variants)

        # With large sample, should be within ±2% of target
        assert 48 <= stats["A"] <= 52
        assert 48 <= stats["B"] <= 52

    def test_25_75_split(self):
        """Test 25/75 uneven split."""
        router = VariantRouter()

        variants = [TitleVariant("A", "Title A", 25), TitleVariant("B", "Title B", 75)]

        # Simulate 1000 users
        for i in range(1000):
            router.assign(f"user{i}", variants)

        stats = router.get_distribution_stats(variants)

        # Allow ±4% tolerance
        assert 21 <= stats["A"] <= 29
        assert 71 <= stats["B"] <= 79

    def test_multivariate_equal_split(self):
        """Test equal split among 4 variants."""
        router = VariantRouter()

        variants = [
            TitleVariant("A", "Title A", 25),
            TitleVariant("B", "Title B", 25),
            TitleVariant("C", "Title C", 25),
            TitleVariant("D", "Title D", 25),
        ]

        # Simulate 2000 users
        for i in range(2000):
            router.assign(f"user{i}", variants)

        stats = router.get_distribution_stats(variants)

        # Each should get ~25% (±4% tolerance)
        for variant_id in ["A", "B", "C", "D"]:
            assert 21 <= stats[variant_id] <= 29

    def test_multivariate_uneven_split(self):
        """Test uneven split among 3 variants."""
        router = VariantRouter()

        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 30),
            TitleVariant("C", "Title C", 20),
        ]

        # Simulate 1500 users
        for i in range(1500):
            router.assign(f"user{i}", variants)

        stats = router.get_distribution_stats(variants)

        # Check each within tolerance
        assert 46 <= stats["A"] <= 54  # 50% ±4%
        assert 26 <= stats["B"] <= 34  # 30% ±4%
        assert 16 <= stats["C"] <= 24  # 20% ±4%
