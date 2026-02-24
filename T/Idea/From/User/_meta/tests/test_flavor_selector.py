"""Tests for FlavorSelector – recursive multi-flavor combination and no-flavor logic."""

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from idea_variants import (
    FlavorSelector,
    pick_flavor_combination,
    pick_multiple_weighted_flavors,
    DEFAULT_IDEA_COUNT,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestFlavorSelectorConstants:
    """FlavorSelector exposes the tuning constants as class attributes."""

    def test_multi_flavor_chance_is_0_3(self):
        assert FlavorSelector.MULTI_FLAVOR_CHANCE == 0.3

    def test_default_count_is_10(self):
        assert FlavorSelector.DEFAULT_COUNT == 10

    def test_default_idea_count_matches(self):
        """Module-level DEFAULT_IDEA_COUNT must stay in sync."""
        assert DEFAULT_IDEA_COUNT == FlavorSelector.DEFAULT_COUNT


# ---------------------------------------------------------------------------
# select_flavor_combination – basic contract
# ---------------------------------------------------------------------------

class TestSelectFlavorCombinationBasic:
    """Basic contract tests for select_flavor_combination."""

    def setup_method(self):
        self.selector = FlavorSelector()

    def test_returns_list(self):
        result = self.selector.select_flavor_combination(seed=0)
        assert isinstance(result, list)

    def test_returns_at_least_one_flavor_by_default(self):
        for seed in range(50):
            combo = self.selector.select_flavor_combination(seed=seed)
            assert len(combo) >= 1, f"Expected ≥1 flavor, got {combo} at seed={seed}"

    def test_all_items_are_known_flavors(self):
        known = set(self.selector.loader.list_flavor_names())
        for seed in range(30):
            for flavor in self.selector.select_flavor_combination(seed=seed):
                assert flavor in known, f"Unknown flavor '{flavor}' at seed={seed}"

    def test_no_duplicates_within_combination(self):
        for seed in range(50):
            combo = self.selector.select_flavor_combination(seed=seed)
            assert len(combo) == len(set(combo)), f"Duplicate flavors in combo at seed={seed}"

    def test_deterministic_with_same_seed(self):
        combo_a = self.selector.select_flavor_combination(seed=42)
        combo_b = self.selector.select_flavor_combination(seed=42)
        assert combo_a == combo_b

    def test_different_seeds_may_differ(self):
        results = [
            tuple(self.selector.select_flavor_combination(seed=i)) for i in range(20)
        ]
        assert len(set(results)) > 1, "All seeds produced identical results"


# ---------------------------------------------------------------------------
# select_flavor_combination – primary_flavor parameter
# ---------------------------------------------------------------------------

class TestSelectFlavorCombinationPrimaryFlavor:
    """primary_flavor is always the first element of the returned list."""

    def setup_method(self):
        self.selector = FlavorSelector()

    def test_primary_flavor_is_first_element(self):
        primary = "Emotional Drama + Growth"
        for seed in range(20):
            combo = self.selector.select_flavor_combination(
                primary_flavor=primary, seed=seed
            )
            assert combo[0] == primary, (
                f"Expected first element to be primary flavor, got {combo}"
            )

    def test_primary_flavor_not_duplicated(self):
        primary = "Emotional Drama + Growth"
        for seed in range(20):
            combo = self.selector.select_flavor_combination(
                primary_flavor=primary, seed=seed
            )
            assert combo.count(primary) == 1


# ---------------------------------------------------------------------------
# select_flavor_combination – no-flavor case
# ---------------------------------------------------------------------------

class TestNoFlavorCase:
    """no_flavor_chance=0 never returns empty; >0 does so proportionally."""

    def setup_method(self):
        self.selector = FlavorSelector()

    def test_no_flavor_chance_zero_never_empty(self):
        for seed in range(100):
            combo = self.selector.select_flavor_combination(
                seed=seed, no_flavor_chance=0.0
            )
            assert combo != [], f"Got empty combination at seed={seed}"

    def test_no_flavor_chance_one_always_empty(self):
        for seed in range(20):
            combo = self.selector.select_flavor_combination(
                seed=seed, no_flavor_chance=1.0
            )
            assert combo == [], f"Expected empty combination at seed={seed}"

    def test_no_flavor_chance_statistical(self):
        """Actual empty-rate should be within 3 standard deviations of target."""
        samples = 2000
        target = 0.15
        empty_count = sum(
            1
            for i in range(samples)
            if self.selector.select_flavor_combination(
                seed=i, no_flavor_chance=target
            ) == []
        )
        rate = empty_count / samples
        # 3-sigma tolerance for a binomial distribution
        sigma = (target * (1 - target) / samples) ** 0.5
        assert abs(rate - target) <= 3 * sigma, (
            f"No-flavor rate {rate:.3f} too far from target {target:.3f}"
        )

    def test_empty_list_is_valid_result(self):
        combo = self.selector.select_flavor_combination(
            seed=0, no_flavor_chance=1.0
        )
        assert combo == []
        assert isinstance(combo, list)


# ---------------------------------------------------------------------------
# select_flavor_combination – recursive probability distribution
# ---------------------------------------------------------------------------

class TestRecursiveProbabilityDistribution:
    """Statistical tests for the recursive 30% probability chain."""

    def setup_method(self):
        self.selector = FlavorSelector()
        self.samples = 5000

    def _distribution(self, multi_chance=0.3):
        counts = {}
        for i in range(self.samples):
            n = len(self.selector.select_flavor_combination(
                seed=i, multi_chance=multi_chance
            ))
            counts[n] = counts.get(n, 0) + 1
        return counts

    def test_single_flavor_most_common(self):
        counts = self._distribution()
        assert counts.get(1, 0) > counts.get(2, 0)

    def test_second_flavor_rate_approx_30_pct(self):
        """P(≥2 flavors) should be ~30%."""
        counts = self._distribution()
        multi = sum(v for k, v in counts.items() if k >= 2)
        rate = multi / self.samples
        assert 0.22 <= rate <= 0.38, f"P(≥2 flavors) = {rate:.3f}, expected ~0.30"

    def test_third_flavor_rate_approx_9_pct(self):
        """P(≥3 flavors) should be ~9% (0.3²)."""
        counts = self._distribution()
        triple = sum(v for k, v in counts.items() if k >= 3)
        rate = triple / self.samples
        assert 0.05 <= rate <= 0.14, f"P(≥3 flavors) = {rate:.3f}, expected ~0.09"

    def test_fourth_flavor_rate_approx_2_7_pct(self):
        """P(≥4 flavors) should be ~2.7% (0.3³)."""
        counts = self._distribution()
        quad = sum(v for k, v in counts.items() if k >= 4)
        rate = quad / self.samples
        assert 0.005 <= rate <= 0.06, f"P(≥4 flavors) = {rate:.3f}, expected ~0.027"

    def test_fifth_flavor_rate_approx_0_81_pct(self):
        """P(≥5 flavors) should be ~0.81% (0.3⁴)."""
        counts = self._distribution()
        quint = sum(v for k, v in counts.items() if k >= 5)
        rate = quint / self.samples
        assert rate <= 0.03, f"P(≥5 flavors) = {rate:.3f}, expected ~0.0081"

    def test_custom_multi_chance(self):
        """Passing a custom multi_chance shifts the distribution accordingly."""
        counts_50 = self._distribution(multi_chance=0.5)
        counts_10 = self._distribution(multi_chance=0.1)
        multi_50 = sum(v for k, v in counts_50.items() if k >= 2) / self.samples
        multi_10 = sum(v for k, v in counts_10.items() if k >= 2) / self.samples
        assert multi_50 > multi_10, (
            "Higher multi_chance should produce more multi-flavor combos"
        )


# ---------------------------------------------------------------------------
# select_multiple – default count
# ---------------------------------------------------------------------------

class TestSelectMultipleDefaultCount:
    """select_multiple uses DEFAULT_COUNT = 10 when no count is given."""

    def setup_method(self):
        self.selector = FlavorSelector()

    def test_default_count_returns_10(self):
        result = self.selector.select_multiple(seed=0)
        assert len(result) == 10

    def test_explicit_count_respected(self):
        assert len(self.selector.select_multiple(count=5, seed=0)) == 5
        assert len(self.selector.select_multiple(count=3, seed=0)) == 3


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

class TestConvenienceFunctions:
    """pick_flavor_combination and pick_multiple_weighted_flavors wrappers."""

    def test_pick_flavor_combination_returns_list(self):
        result = pick_flavor_combination(seed=0)
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_pick_flavor_combination_no_flavor(self):
        result = pick_flavor_combination(seed=0, no_flavor_chance=1.0)
        assert result == []

    def test_pick_flavor_combination_primary_flavor(self):
        primary = "Mystery/Curiosity Gap"
        result = pick_flavor_combination(primary_flavor=primary, seed=0)
        assert result[0] == primary

    def test_pick_multiple_weighted_flavors_default_10(self):
        result = pick_multiple_weighted_flavors(seed=0)
        assert len(result) == 10
