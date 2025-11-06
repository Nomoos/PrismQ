"""
Unit Tests for Fairness Metrics Module

This module provides comprehensive unit tests for all fairness metric functions.
These tests validate the statistical analysis tools that will be used for
benchmarking scheduling strategies.

Part of Issue #338: Research Scheduling Strategy Performance
Worker: Worker 09 - Research Engineer
"""

import unittest
from typing import List, Dict
import sys
import os

# Add parent directory to path to import fairness_metrics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fairness_metrics import (
    calculate_gini_coefficient,
    calculate_jains_fairness_index,
    calculate_percentiles,
    calculate_wait_time_statistics,
    analyze_starvation_risk,
    calculate_probability_distribution,
    calculate_expected_weighted_random_probability,
    compare_distributions,
)


class TestGiniCoefficient(unittest.TestCase):
    """Test Gini coefficient calculations."""
    
    def test_perfect_equality(self):
        """Test that equal wait times give Gini = 0."""
        wait_times = [10.0] * 10
        gini = calculate_gini_coefficient(wait_times)
        self.assertAlmostEqual(gini, 0.0, places=4)
    
    def test_high_inequality(self):
        """Test that unequal wait times give higher Gini."""
        wait_times = [1.0, 1.0, 1.0, 100.0]
        gini = calculate_gini_coefficient(wait_times)
        self.assertGreater(gini, 0.5)
        self.assertLess(gini, 1.0)
    
    def test_single_value(self):
        """Test that single value gives Gini = 0."""
        wait_times = [10.0]
        gini = calculate_gini_coefficient(wait_times)
        self.assertEqual(gini, 0.0)
    
    def test_all_zeros(self):
        """Test that all zero wait times give Gini = 0."""
        wait_times = [0.0] * 5
        gini = calculate_gini_coefficient(wait_times)
        self.assertEqual(gini, 0.0)
    
    def test_empty_list_raises_error(self):
        """Test that empty list raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_gini_coefficient([])


class TestJainsFairnessIndex(unittest.TestCase):
    """Test Jain's Fairness Index calculations."""
    
    def test_perfect_fairness(self):
        """Test that equal wait times give Jain's index = 1."""
        wait_times = [10.0] * 10
        jain = calculate_jains_fairness_index(wait_times)
        self.assertAlmostEqual(jain, 1.0, places=4)
    
    def test_poor_fairness(self):
        """Test that unequal wait times give lower Jain's index."""
        wait_times = [1.0, 1.0, 1.0, 100.0]
        jain = calculate_jains_fairness_index(wait_times)
        self.assertLess(jain, 0.5)
        self.assertGreater(jain, 0.0)
    
    def test_single_value(self):
        """Test that single value gives Jain's index = 1."""
        wait_times = [10.0]
        jain = calculate_jains_fairness_index(wait_times)
        self.assertEqual(jain, 1.0)
    
    def test_all_zeros(self):
        """Test that all zero wait times give Jain's index = 1."""
        wait_times = [0.0] * 5
        jain = calculate_jains_fairness_index(wait_times)
        self.assertEqual(jain, 1.0)
    
    def test_empty_list_raises_error(self):
        """Test that empty list raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_jains_fairness_index([])


class TestPercentiles(unittest.TestCase):
    """Test percentile calculations."""
    
    def test_median(self):
        """Test 50th percentile (median)."""
        values = list(range(1, 101))  # 1 to 100
        result = calculate_percentiles(values, [50])
        self.assertAlmostEqual(result['P50'], 50.5, places=1)
    
    def test_multiple_percentiles(self):
        """Test multiple percentiles at once."""
        values = list(range(1, 101))
        result = calculate_percentiles(values, [50, 95, 99])
        self.assertIn('P50', result)
        self.assertIn('P95', result)
        self.assertIn('P99', result)
        self.assertLess(result['P50'], result['P95'])
        self.assertLess(result['P95'], result['P99'])
    
    def test_extreme_percentiles(self):
        """Test 0th and 100th percentiles."""
        values = [1, 2, 3, 4, 5]
        result = calculate_percentiles(values, [0, 100])
        self.assertEqual(result['P0'], 1)
        self.assertEqual(result['P100'], 5)
    
    def test_invalid_percentile_raises_error(self):
        """Test that invalid percentile raises ValueError."""
        values = [1, 2, 3]
        with self.assertRaises(ValueError):
            calculate_percentiles(values, [150])
        with self.assertRaises(ValueError):
            calculate_percentiles(values, [-10])
    
    def test_empty_list_raises_error(self):
        """Test that empty list raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_percentiles([], [50])


class TestWaitTimeStatistics(unittest.TestCase):
    """Test comprehensive wait time statistics."""
    
    def test_all_metrics_present(self):
        """Test that all expected metrics are calculated."""
        wait_times = [5, 10, 15, 20, 100]
        stats = calculate_wait_time_statistics(wait_times)
        
        expected_keys = ['mean', 'median', 'std_dev', 'min', 'max', 
                        'P50', 'P95', 'P99', 'gini', 'jain']
        for key in expected_keys:
            self.assertIn(key, stats)
    
    def test_values_make_sense(self):
        """Test that calculated values are reasonable."""
        wait_times = [5, 10, 15, 20, 100]
        stats = calculate_wait_time_statistics(wait_times)
        
        self.assertEqual(stats['min'], 5)
        self.assertEqual(stats['max'], 100)
        self.assertGreater(stats['mean'], stats['min'])
        self.assertLess(stats['mean'], stats['max'])
        self.assertGreaterEqual(stats['gini'], 0.0)
        self.assertLessEqual(stats['gini'], 1.0)
        self.assertGreaterEqual(stats['jain'], 0.0)
        self.assertLessEqual(stats['jain'], 1.0)


class TestStarvationRiskAnalysis(unittest.TestCase):
    """Test starvation risk analysis."""
    
    def test_no_starvation(self):
        """Test scenario with no starved tasks."""
        wait_times_by_priority = {
            1: [1, 2, 3, 4],      # High priority - quick
            100: [5, 6, 7, 8]     # Low priority - also quick
        }
        stats = analyze_starvation_risk(wait_times_by_priority, starvation_threshold_seconds=100)
        
        self.assertEqual(stats[1]['pct_starved'], 0.0)
        self.assertEqual(stats[100]['pct_starved'], 0.0)
    
    def test_with_starvation(self):
        """Test scenario with starved tasks."""
        wait_times_by_priority = {
            1: [1, 2, 3, 4],           # High priority - quick
            100: [300, 400, 500, 600]  # Low priority - starved
        }
        stats = analyze_starvation_risk(wait_times_by_priority, starvation_threshold_seconds=100)
        
        self.assertEqual(stats[1]['pct_starved'], 0.0)
        self.assertEqual(stats[100]['pct_starved'], 100.0)
        self.assertEqual(stats[100]['count_starved'], 4)
    
    def test_partial_starvation(self):
        """Test scenario with some starved tasks."""
        wait_times_by_priority = {
            100: [50, 150, 250, 75]  # Mixed
        }
        stats = analyze_starvation_risk(wait_times_by_priority, starvation_threshold_seconds=100)
        
        self.assertEqual(stats[100]['pct_starved'], 50.0)
        self.assertEqual(stats[100]['count_starved'], 2)


class TestProbabilityDistribution(unittest.TestCase):
    """Test probability distribution calculations."""
    
    def test_equal_distribution(self):
        """Test equal selection counts."""
        selections = {1: 50, 10: 50}
        probs = calculate_probability_distribution(selections)
        
        self.assertAlmostEqual(probs[1], 0.5)
        self.assertAlmostEqual(probs[10], 0.5)
    
    def test_unequal_distribution(self):
        """Test unequal selection counts."""
        selections = {1: 80, 10: 15, 100: 5}
        probs = calculate_probability_distribution(selections)
        
        self.assertAlmostEqual(probs[1], 0.8)
        self.assertAlmostEqual(probs[10], 0.15)
        self.assertAlmostEqual(probs[100], 0.05)
    
    def test_probabilities_sum_to_one(self):
        """Test that probabilities sum to 1.0."""
        selections = {1: 30, 10: 45, 100: 25}
        probs = calculate_probability_distribution(selections)
        
        total = sum(probs.values())
        self.assertAlmostEqual(total, 1.0)
    
    def test_zero_selections_raises_error(self):
        """Test that zero total selections raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_probability_distribution({1: 0, 10: 0})


class TestWeightedRandomProbability(unittest.TestCase):
    """Test expected weighted random probability calculations."""
    
    def test_higher_priority_higher_probability(self):
        """Test that higher priority (lower number) has higher probability."""
        priorities = [1, 10, 100]
        probs = calculate_expected_weighted_random_probability(priorities)
        
        self.assertGreater(probs[1], probs[10])
        self.assertGreater(probs[10], probs[100])
    
    def test_probabilities_sum_to_one(self):
        """Test that probabilities sum to 1.0."""
        priorities = [1, 1, 10, 10, 100, 100]
        probs = calculate_expected_weighted_random_probability(priorities)
        
        total = sum(probs.values())
        self.assertAlmostEqual(total, 1.0, places=6)
    
    def test_same_priority_same_probability(self):
        """Test that same priority levels get same probability."""
        priorities = [10, 10, 10]
        probs = calculate_expected_weighted_random_probability(priorities)
        
        # Only one priority level, should get 100%
        self.assertAlmostEqual(probs[10], 1.0)


class TestDistributionComparison(unittest.TestCase):
    """Test distribution comparison."""
    
    def test_perfect_match(self):
        """Test comparison when actual matches expected."""
        actual = {1: 0.5, 10: 0.3, 100: 0.2}
        expected = {1: 0.5, 10: 0.3, 100: 0.2}
        comparison = compare_distributions(actual, expected)
        
        for priority in [1, 10, 100]:
            self.assertAlmostEqual(comparison[priority]['deviation_pct'], 0.0)
            self.assertAlmostEqual(comparison[priority]['absolute_error'], 0.0)
    
    def test_deviation_calculation(self):
        """Test deviation percentage calculation."""
        actual = {1: 0.5}
        expected = {1: 0.6}
        comparison = compare_distributions(actual, expected)
        
        # 0.5 is 16.67% less than 0.6
        self.assertAlmostEqual(comparison[1]['deviation_pct'], -16.666, places=2)
    
    def test_missing_priorities(self):
        """Test handling of missing priorities in one distribution."""
        actual = {1: 0.6, 10: 0.4}
        expected = {1: 0.5, 10: 0.3, 100: 0.2}
        comparison = compare_distributions(actual, expected)
        
        self.assertIn(100, comparison)
        self.assertEqual(comparison[100]['actual'], 0.0)
        self.assertEqual(comparison[100]['expected'], 0.2)


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
