"""Statistical Analysis - Calculate significance and confidence for A/B tests."""

from dataclasses import dataclass
from typing import Optional, List, Tuple
from scipy.stats import chi2_contingency
import math


@dataclass
class VariantMetrics:
    """Performance metrics for a variant.
    
    Attributes:
        variant_id: Variant identifier (A, B, C, etc.)
        views: Total views/impressions
        clicks: Total clicks
        engagement_score: Normalized engagement metric (0.0 to 1.0).
            Represents user engagement level where 0 = no engagement,
            1 = maximum engagement. Can be calculated from time-on-page,
            scroll depth, interactions, or other engagement signals.
    """
    variant_id: str
    views: int
    clicks: int
    engagement_score: float = 0.0
    
    @property
    def ctr(self) -> float:
        """Calculate Click-Through Rate as percentage."""
        if self.views == 0:
            return 0.0
        return (self.clicks / self.views) * 100
    
    def __post_init__(self):
        """Validate metrics."""
        if self.views < 0:
            raise ValueError("views cannot be negative")
        if self.clicks < 0:
            raise ValueError("clicks cannot be negative")
        if self.clicks > self.views:
            raise ValueError("clicks cannot exceed views")
        if not 0 <= self.engagement_score <= 1:
            raise ValueError("engagement_score must be between 0 and 1")


@dataclass
class SignificanceResult:
    """Result of statistical significance test.
    
    Attributes:
        p_value: P-value from statistical test (lower = more significant)
        confidence: Confidence level as percentage (0-100)
        is_significant: Whether result is statistically significant (p < 0.05)
        winning_variant: ID of the better performing variant
        improvement: Percentage improvement of winner over others
    """
    p_value: float
    confidence: float
    is_significant: bool
    winning_variant: Optional[str] = None
    improvement: Optional[float] = None


def calculate_significance(
    variant_a: VariantMetrics,
    variant_b: VariantMetrics,
    metric: str = "ctr"
) -> SignificanceResult:
    """Calculate statistical significance between two variants using chi-square test.
    
    For CTR comparison, uses chi-square test on the contingency table of
    clicks/non-clicks vs variants. For other metrics, uses the appropriate
    statistical test.
    
    Args:
        variant_a: First variant metrics
        variant_b: Second variant metrics
        metric: Metric to compare ('ctr', 'engagement', 'views')
        
    Returns:
        SignificanceResult with p-value, confidence, and winner
        
    Raises:
        ValueError: If insufficient data or invalid metric
    """
    # Validate minimum sample size
    if variant_a.views < 100 or variant_b.views < 100:
        raise ValueError("Each variant needs at least 100 views for significance testing")
    
    if metric == "ctr":
        return _calculate_ctr_significance(variant_a, variant_b)
    elif metric == "engagement":
        return _calculate_engagement_significance(variant_a, variant_b)
    elif metric == "views":
        return _calculate_views_significance(variant_a, variant_b)
    else:
        raise ValueError(f"Unsupported metric: {metric}")


def _calculate_ctr_significance(
    variant_a: VariantMetrics,
    variant_b: VariantMetrics
) -> SignificanceResult:
    """Calculate CTR significance using chi-square test.
    
    Creates a 2x2 contingency table:
                Clicks    Non-clicks
    Variant A   clicks_a  (views_a - clicks_a)
    Variant B   clicks_b  (views_b - clicks_b)
    
    Args:
        variant_a: First variant metrics
        variant_b: Second variant metrics
        
    Returns:
        SignificanceResult with statistical analysis
    """
    # Create contingency table
    data = [
        [variant_a.clicks, variant_a.views - variant_a.clicks],
        [variant_b.clicks, variant_b.views - variant_b.clicks]
    ]
    
    # Perform chi-square test
    try:
        chi2, p_value, dof, expected = chi2_contingency(data)
    except ValueError as e:
        # Handle cases where chi-square test is invalid (e.g., zeros)
        raise ValueError(f"Cannot calculate significance: {e}")
    
    # Calculate confidence level
    confidence = (1 - p_value) * 100
    is_significant = p_value < 0.05  # 95% confidence threshold
    
    # Determine winner and improvement
    ctr_a = variant_a.ctr
    ctr_b = variant_b.ctr
    
    if ctr_a > ctr_b:
        winning_variant = variant_a.variant_id
        if ctr_b > 0:
            improvement = ((ctr_a - ctr_b) / ctr_b) * 100
        else:
            improvement = float('inf') if ctr_a > 0 else 0.0
    else:
        winning_variant = variant_b.variant_id
        if ctr_a > 0:
            improvement = ((ctr_b - ctr_a) / ctr_a) * 100
        else:
            improvement = float('inf') if ctr_b > 0 else 0.0
    
    return SignificanceResult(
        p_value=p_value,
        confidence=confidence,
        is_significant=is_significant,
        winning_variant=winning_variant,
        improvement=improvement
    )


def _calculate_engagement_significance(
    variant_a: VariantMetrics,
    variant_b: VariantMetrics
) -> SignificanceResult:
    """Calculate engagement significance (simplified approximation).
    
    NOTE: This is a SIMPLIFIED APPROXIMATION for MVP purposes.
    The hardcoded p-values (0.03, 0.15, 0.5) are placeholder estimates
    based on rough z-score thresholds and should not be interpreted as
    precise statistical calculations.
    
    Future versions should implement proper t-test or z-test with actual
    engagement data distributions using scipy.stats.ttest_ind or similar.
    
    Args:
        variant_a: First variant metrics
        variant_b: Second variant metrics
        
    Returns:
        SignificanceResult with analysis
    """
    # Calculate difference in engagement scores
    diff = abs(variant_a.engagement_score - variant_b.engagement_score)
    
    # Simple significance estimation based on sample size and difference
    # This is a simplified approach; proper implementation would use t-test
    combined_n = variant_a.views + variant_b.views
    
    # Rough approximation: larger difference and more samples = more significant
    # Z-score approximation
    se = math.sqrt(2 / combined_n)  # Simplified standard error
    z_score = diff / se if se > 0 else 0
    
    # Convert z-score to p-value (PLACEHOLDER APPROXIMATION)
    # These hardcoded values are rough estimates, not precise calculations
    # For z > 1.96, p < 0.05
    if z_score > 1.96:
        p_value = 0.03  # Placeholder for significant result
        is_significant = True
    elif z_score > 1.0:
        p_value = 0.15  # Placeholder for marginally significant
        is_significant = False
    else:
        p_value = 0.5  # Placeholder for not significant
        is_significant = False
    
    confidence = (1 - p_value) * 100
    
    # Determine winner
    if variant_a.engagement_score > variant_b.engagement_score:
        winning_variant = variant_a.variant_id
        if variant_b.engagement_score > 0:
            improvement = ((variant_a.engagement_score - variant_b.engagement_score) 
                          / variant_b.engagement_score) * 100
        else:
            improvement = float('inf')
    else:
        winning_variant = variant_b.variant_id
        if variant_a.engagement_score > 0:
            improvement = ((variant_b.engagement_score - variant_a.engagement_score) 
                          / variant_a.engagement_score) * 100
        else:
            improvement = float('inf')
    
    return SignificanceResult(
        p_value=p_value,
        confidence=confidence,
        is_significant=is_significant,
        winning_variant=winning_variant,
        improvement=improvement
    )


def _calculate_views_significance(
    variant_a: VariantMetrics,
    variant_b: VariantMetrics
) -> SignificanceResult:
    """Calculate views significance (chi-square test for counts).
    
    Compares view counts between variants to determine if the difference
    is statistically significant. Uses manual chi-square calculation which
    is mathematically equivalent to scipy.stats methods for this simple case.
    
    Args:
        variant_a: First variant metrics
        variant_b: Second variant metrics
        
    Returns:
        SignificanceResult with analysis
    """
    # Create simple contingency for view counts
    total_views = variant_a.views + variant_b.views
    expected_a = total_views / 2
    expected_b = total_views / 2
    
    # Chi-square calculation for observed vs expected
    # This is mathematically equivalent to scipy.stats.chisquare
    chi2 = (
        ((variant_a.views - expected_a) ** 2 / expected_a) +
        ((variant_b.views - expected_b) ** 2 / expected_b)
    )
    
    # For df=1, chi2 > 3.841 means p < 0.05
    is_significant = chi2 > 3.841
    
    # Convert chi2 to p-value using standard thresholds (df=1)
    if chi2 > 10.83:  # p < 0.001
        p_value = 0.001
    elif chi2 > 6.635:  # p < 0.01
        p_value = 0.01
    elif chi2 > 3.841:  # p < 0.05
        p_value = 0.04
    else:
        p_value = 0.5  # Not significant
    
    confidence = (1 - p_value) * 100
    
    # Determine winner
    if variant_a.views > variant_b.views:
        winning_variant = variant_a.variant_id
        if variant_b.views > 0:
            improvement = ((variant_a.views - variant_b.views) / variant_b.views) * 100
        else:
            improvement = float('inf')
    else:
        winning_variant = variant_b.variant_id
        if variant_a.views > 0:
            improvement = ((variant_b.views - variant_a.views) / variant_a.views) * 100
        else:
            improvement = float('inf')
    
    return SignificanceResult(
        p_value=p_value,
        confidence=confidence,
        is_significant=is_significant,
        winning_variant=winning_variant,
        improvement=improvement
    )


def compare_all_variants(
    variants: List[VariantMetrics],
    metric: str = "ctr"
) -> List[Tuple[str, str, SignificanceResult]]:
    """Compare all pairs of variants and return pairwise results.
    
    For multivariate tests (A/B/C/D), performs pairwise comparison:
    - A vs B
    - A vs C
    - A vs D
    - B vs C
    - B vs D
    - C vs D
    
    Args:
        variants: List of variant metrics
        metric: Metric to compare
        
    Returns:
        List of tuples (variant_id_1, variant_id_2, SignificanceResult)
    """
    results = []
    
    for i in range(len(variants)):
        for j in range(i + 1, len(variants)):
            try:
                result = calculate_significance(variants[i], variants[j], metric)
                results.append((variants[i].variant_id, variants[j].variant_id, result))
            except ValueError:
                # Skip pairs with insufficient data
                continue
    
    return results


def find_overall_winner(
    variants: List[VariantMetrics],
    metric: str = "ctr"
) -> Optional[Tuple[str, int]]:
    """Find the overall winning variant from multivariate test.
    
    Determines the variant that wins the most pairwise comparisons
    with statistical significance.
    
    Args:
        variants: List of variant metrics
        metric: Metric to compare
        
    Returns:
        Tuple of (winning_variant_id, number_of_wins) or None if no clear winner
    """
    if len(variants) < 2:
        return None
    
    # Count wins for each variant
    wins = {v.variant_id: 0 for v in variants}
    
    # Perform pairwise comparisons
    comparisons = compare_all_variants(variants, metric)
    
    for v1_id, v2_id, result in comparisons:
        if result.is_significant and result.winning_variant:
            wins[result.winning_variant] += 1
    
    # Find variant with most wins
    if not wins:
        return None
    
    max_wins = max(wins.values())
    if max_wins == 0:
        return None
    
    winner_id = max(wins.items(), key=lambda x: x[1])[0]
    return (winner_id, max_wins)
