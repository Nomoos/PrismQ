"""
Fairness Metrics Module for Queue Scheduling Strategy Analysis

This module implements statistical fairness metrics used to evaluate
the fairness of different scheduling strategies. These metrics are
independent of the actual scheduling implementation.

Part of Issue #338: Research Scheduling Strategy Performance
Worker: Worker 09 - Research Engineer
"""

from typing import List, Dict, Tuple
import statistics


def calculate_gini_coefficient(wait_times: List[float]) -> float:
    """
    Calculate Gini coefficient for wait time distribution.
    
    The Gini coefficient is a measure of statistical dispersion intended to
    represent the inequality of a distribution. Originally developed to measure
    income inequality, it's used here to measure wait time inequality.
    
    Args:
        wait_times: List of wait times (in seconds) for tasks
        
    Returns:
        float: Gini coefficient where:
            - 0.0 = perfect equality (all tasks wait same time)
            - 1.0 = complete inequality (one task waits infinitely while others don't)
            
    Example:
        >>> wait_times = [10, 10, 10, 10]  # Perfect equality
        >>> calculate_gini_coefficient(wait_times)
        0.0
        
        >>> wait_times = [1, 1, 1, 100]  # High inequality
        >>> gini = calculate_gini_coefficient(wait_times)
        >>> 0.7 < gini < 0.8  # Approximately 0.72
        True
        
    References:
        - https://en.wikipedia.org/wiki/Gini_coefficient
    """
    if not wait_times:
        raise ValueError("wait_times cannot be empty")
    
    if len(wait_times) == 1:
        return 0.0  # Single value = perfect equality
    
    sorted_times = sorted(wait_times)
    n = len(sorted_times)
    cumsum = 0
    
    for i, t in enumerate(sorted_times):
        cumsum += (2 * i - n + 1) * t
    
    total = sum(sorted_times)
    if total == 0:
        return 0.0  # All wait times are 0 = perfect equality
    
    return cumsum / (n * total)


def calculate_jains_fairness_index(wait_times: List[float]) -> float:
    """
    Calculate Jain's Fairness Index for wait time distribution.
    
    Jain's Fairness Index is a measure of fairness commonly used in networking
    and resource allocation. It quantifies how evenly resources are distributed.
    
    Args:
        wait_times: List of wait times (in seconds) for tasks
        
    Returns:
        float: Jain's Fairness Index where:
            - 1.0 = perfectly fair (all tasks wait same time)
            - 1/n = completely unfair (one task gets all the wait time)
            
    Example:
        >>> wait_times = [10, 10, 10, 10]  # Perfect fairness
        >>> calculate_jains_fairness_index(wait_times)
        1.0
        
        >>> wait_times = [1, 1, 1, 100]  # Poor fairness
        >>> jain = calculate_jains_fairness_index(wait_times)
        >>> 0.2 < jain < 0.3  # Approximately 0.27
        True
        
    References:
        - https://en.wikipedia.org/wiki/Fairness_measure#Jain's_fairness_index
        - Jain, R., Chiu, D., & Hawe, W. (1984). A quantitative measure of fairness
    """
    if not wait_times:
        raise ValueError("wait_times cannot be empty")
    
    if len(wait_times) == 1:
        return 1.0  # Single value = perfect fairness
    
    n = len(wait_times)
    sum_times = sum(wait_times)
    sum_squares = sum(t**2 for t in wait_times)
    
    if sum_squares == 0:
        return 1.0  # All wait times are 0 = perfect fairness
    
    return (sum_times ** 2) / (n * sum_squares)


def calculate_percentiles(values: List[float], percentiles: List[int]) -> Dict[str, float]:
    """
    Calculate percentiles for a list of values.
    
    Args:
        values: List of numerical values
        percentiles: List of percentile values to calculate (e.g., [50, 95, 99])
        
    Returns:
        Dict mapping percentile labels to values (e.g., {"P50": 10.5, "P95": 50.2})
        
    Example:
        >>> values = list(range(1, 101))  # 1 to 100
        >>> calculate_percentiles(values, [50, 95, 99])
        {'P50': 50.5, 'P95': 95.05, 'P99': 99.01}
    """
    if not values:
        raise ValueError("values cannot be empty")
    
    if not percentiles:
        raise ValueError("percentiles cannot be empty")
    
    sorted_values = sorted(values)
    result = {}
    
    for p in percentiles:
        if not 0 <= p <= 100:
            raise ValueError(f"Percentile {p} must be between 0 and 100")
        
        # Calculate the index for the percentile
        k = (len(sorted_values) - 1) * (p / 100.0)
        f = int(k)
        c = k - f
        
        if f + 1 < len(sorted_values):
            value = sorted_values[f] + c * (sorted_values[f + 1] - sorted_values[f])
        else:
            value = sorted_values[f]
        
        result[f"P{p}"] = value
    
    return result


def calculate_wait_time_statistics(wait_times: List[float]) -> Dict[str, float]:
    """
    Calculate comprehensive statistics for wait times.
    
    Args:
        wait_times: List of wait times (in seconds)
        
    Returns:
        Dict containing:
            - mean: Average wait time
            - median: Median wait time
            - std_dev: Standard deviation
            - min: Minimum wait time
            - max: Maximum wait time
            - P50, P95, P99: Percentiles
            - gini: Gini coefficient
            - jain: Jain's fairness index
            
    Example:
        >>> wait_times = [5, 10, 15, 20, 100]
        >>> stats = calculate_wait_time_statistics(wait_times)
        >>> 'mean' in stats and 'gini' in stats and 'jain' in stats
        True
    """
    if not wait_times:
        raise ValueError("wait_times cannot be empty")
    
    percentiles = calculate_percentiles(wait_times, [50, 95, 99])
    
    return {
        'mean': statistics.mean(wait_times),
        'median': statistics.median(wait_times),
        'std_dev': statistics.stdev(wait_times) if len(wait_times) > 1 else 0.0,
        'min': min(wait_times),
        'max': max(wait_times),
        **percentiles,
        'gini': calculate_gini_coefficient(wait_times),
        'jain': calculate_jains_fairness_index(wait_times),
    }


def analyze_starvation_risk(
    wait_times_by_priority: Dict[int, List[float]],
    starvation_threshold_seconds: float = 300.0
) -> Dict[int, Dict[str, float]]:
    """
    Analyze starvation risk for different priority levels.
    
    Args:
        wait_times_by_priority: Dict mapping priority level to list of wait times
        starvation_threshold_seconds: Threshold in seconds to consider task starved
        
    Returns:
        Dict mapping priority level to starvation statistics:
            - max_wait: Maximum wait time for this priority
            - pct_starved: Percentage of tasks exceeding threshold
            - avg_starved_wait: Average wait time for starved tasks
            
    Example:
        >>> wait_times = {
        ...     1: [1, 2, 3, 4],      # High priority - quick
        ...     100: [300, 400, 500]  # Low priority - starved
        ... }
        >>> stats = analyze_starvation_risk(wait_times, 100)
        >>> stats[100]['pct_starved'] > 0
        True
    """
    result = {}
    
    for priority, wait_times in wait_times_by_priority.items():
        if not wait_times:
            continue
        
        starved_times = [t for t in wait_times if t > starvation_threshold_seconds]
        
        result[priority] = {
            'max_wait': max(wait_times),
            'pct_starved': (len(starved_times) / len(wait_times)) * 100,
            'avg_starved_wait': statistics.mean(starved_times) if starved_times else 0.0,
            'count_total': len(wait_times),
            'count_starved': len(starved_times),
        }
    
    return result


def calculate_probability_distribution(
    selections_by_priority: Dict[int, int]
) -> Dict[int, float]:
    """
    Calculate actual probability distribution from selection counts.
    
    Args:
        selections_by_priority: Dict mapping priority to number of selections
        
    Returns:
        Dict mapping priority to actual selection probability (0.0 to 1.0)
        
    Example:
        >>> selections = {1: 80, 10: 15, 100: 5}
        >>> probs = calculate_probability_distribution(selections)
        >>> probs[1]
        0.8
        >>> probs[100]
        0.05
    """
    total_selections = sum(selections_by_priority.values())
    
    if total_selections == 0:
        raise ValueError("Total selections cannot be zero")
    
    return {
        priority: count / total_selections
        for priority, count in selections_by_priority.items()
    }


def calculate_expected_weighted_random_probability(
    priorities: List[int]
) -> Dict[int, float]:
    """
    Calculate expected probability for weighted random strategy.
    
    For weighted random strategy with formula: weight = 1.0 / (priority + 1)
    
    Args:
        priorities: List of all priority levels in the queue
        
    Returns:
        Dict mapping priority to expected probability
        
    Example:
        >>> priorities = [1, 1, 10, 10, 100]
        >>> probs = calculate_expected_weighted_random_probability(priorities)
        >>> probs[1] > probs[10] > probs[100]  # Higher priority = higher probability
        True
    """
    if not priorities:
        raise ValueError("priorities cannot be empty")
    
    # Calculate weights for each priority
    weights = {p: 1.0 / (p + 1) for p in set(priorities)}
    
    # Count occurrences of each priority
    priority_counts = {}
    for p in priorities:
        priority_counts[p] = priority_counts.get(p, 0) + 1
    
    # Total weight = sum of (weight * count) for each priority
    total_weight = sum(weights[p] * priority_counts[p] for p in priority_counts)
    
    # Calculate probability for each priority level
    result = {}
    for priority in set(priorities):
        # Probability = (weight * count) / total_weight
        result[priority] = (weights[priority] * priority_counts[priority]) / total_weight
    
    return result


def compare_distributions(
    actual: Dict[int, float],
    expected: Dict[int, float]
) -> Dict[int, Dict[str, float]]:
    """
    Compare actual vs expected probability distributions.
    
    Args:
        actual: Actual probability distribution
        expected: Expected probability distribution
        
    Returns:
        Dict mapping priority to comparison metrics:
            - actual: Actual probability
            - expected: Expected probability
            - deviation_pct: Percentage deviation
            - absolute_error: Absolute error
            
    Example:
        >>> actual = {1: 0.5, 10: 0.3, 100: 0.2}
        >>> expected = {1: 0.6, 10: 0.25, 100: 0.15}
        >>> comparison = compare_distributions(actual, expected)
        >>> -17 < comparison[1]['deviation_pct'] < -16
        True
    """
    result = {}
    
    all_priorities = set(actual.keys()) | set(expected.keys())
    
    for priority in all_priorities:
        actual_prob = actual.get(priority, 0.0)
        expected_prob = expected.get(priority, 0.0)
        
        if expected_prob > 0:
            deviation_pct = ((actual_prob - expected_prob) / expected_prob) * 100
        else:
            deviation_pct = float('inf') if actual_prob > 0 else 0.0
        
        result[priority] = {
            'actual': actual_prob,
            'expected': expected_prob,
            'deviation_pct': deviation_pct,
            'absolute_error': abs(actual_prob - expected_prob),
        }
    
    return result


if __name__ == "__main__":
    # Example usage and validation
    import doctest
    doctest.testmod()
    
    print("Fairness Metrics Module")
    print("=" * 50)
    print("\nExample: Equal wait times (perfect fairness)")
    equal_waits = [10.0] * 10
    print(f"Wait times: {equal_waits}")
    print(f"Gini coefficient: {calculate_gini_coefficient(equal_waits):.4f}")
    print(f"Jain's index: {calculate_jains_fairness_index(equal_waits):.4f}")
    
    print("\nExample: Unequal wait times (poor fairness)")
    unequal_waits = [1.0, 2.0, 3.0, 4.0, 100.0]
    print(f"Wait times: {unequal_waits}")
    print(f"Gini coefficient: {calculate_gini_coefficient(unequal_waits):.4f}")
    print(f"Jain's index: {calculate_jains_fairness_index(unequal_waits):.4f}")
    
    print("\nExample: Comprehensive statistics")
    stats = calculate_wait_time_statistics(unequal_waits)
    for key, value in stats.items():
        print(f"  {key}: {value:.4f}")
