"""Report Generator - Create test result reports and recommendations."""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# Avoid circular import issues
if TYPE_CHECKING:
    from .statistics import VariantMetrics
    from .test_manager import ABTest, TitleVariant

try:
    from .statistics import VariantMetrics, calculate_significance, find_overall_winner
    from .test_manager import ABTest, TitleVariant
except ImportError:
    # For tests that import directly
    from statistics import VariantMetrics, calculate_significance, find_overall_winner

    from test_manager import ABTest, TitleVariant


@dataclass
class VariantPerformance:
    """Performance data for a variant in a report.

    Attributes:
        variant_id: Variant identifier
        title: Title text
        views: Total views
        clicks: Total clicks
        ctr: Click-through rate as percentage
        engagement_score: Engagement metric (0-1)
    """

    variant_id: str
    title: str
    views: int
    clicks: int
    ctr: float
    engagement_score: float


@dataclass
class TestAnalysis:
    """Statistical analysis results for a test.

    Attributes:
        winning_variant: ID of the best performing variant
        confidence: Confidence level as percentage
        p_value: Statistical p-value
        is_significant: Whether results are statistically significant
        improvement: Percentage improvement of winner
    """

    winning_variant: Optional[str]
    confidence: float
    p_value: float
    is_significant: bool
    improvement: Optional[float]


@dataclass
class TestReport:
    """Complete A/B test report with results and recommendations.

    Attributes:
        test_id: Test identifier
        content_id: Content identifier
        status: Test status
        duration_days: Number of days test ran
        total_views: Total views across all variants
        success_metric: Metric used for optimization
        variants: Performance data for each variant
        analysis: Statistical analysis results
        recommendation: Recommended action based on results
        created_at: Report generation timestamp
    """

    test_id: str
    content_id: str
    status: str
    duration_days: int
    total_views: int
    success_metric: str
    variants: List[VariantPerformance]
    analysis: TestAnalysis
    recommendation: str
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for JSON serialization.

        Returns:
            Dictionary representation of report
        """
        return {
            "test_id": self.test_id,
            "content_id": self.content_id,
            "status": self.status,
            "duration_days": self.duration_days,
            "total_views": self.total_views,
            "success_metric": self.success_metric,
            "variants": [
                {
                    "variant_id": v.variant_id,
                    "title": v.title,
                    "views": v.views,
                    "clicks": v.clicks,
                    "ctr": round(v.ctr, 2),
                    "engagement_score": round(v.engagement_score, 2),
                }
                for v in self.variants
            ],
            "analysis": {
                "winning_variant": self.analysis.winning_variant,
                "confidence": round(self.analysis.confidence, 1),
                "p_value": round(self.analysis.p_value, 4),
                "is_significant": self.analysis.is_significant,
                "improvement": (
                    f"+{round(self.analysis.improvement, 1)}%"
                    if self.analysis.improvement is not None
                    and self.analysis.improvement != float("inf")
                    else None
                ),
            },
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class ReportGenerator:
    """Generates test reports with performance analysis and recommendations."""

    def generate_report(self, test: ABTest, metrics_data: Dict[str, VariantMetrics]) -> TestReport:
        """Generate a complete test report.

        Args:
            test: ABTest configuration
            metrics_data: Dictionary mapping variant_id to VariantMetrics

        Returns:
            Complete TestReport with analysis and recommendations

        Raises:
            ValueError: If insufficient data or invalid test state
        """
        # Validate we have metrics for all variants
        for variant in test.variants:
            if variant.variant_id not in metrics_data:
                raise ValueError(f"Missing metrics for variant {variant.variant_id}")

        # Calculate duration
        duration = (test.end_date - test.start_date).days

        # Calculate total views
        total_views = sum(m.views for m in metrics_data.values())

        # Create variant performance objects
        variant_performances = []
        for variant in test.variants:
            metrics = metrics_data[variant.variant_id]
            variant_performances.append(
                VariantPerformance(
                    variant_id=variant.variant_id,
                    title=variant.title,
                    views=metrics.views,
                    clicks=metrics.clicks,
                    ctr=metrics.ctr,
                    engagement_score=metrics.engagement_score,
                )
            )

        # Perform statistical analysis
        metrics_list = [metrics_data[v.variant_id] for v in test.variants]

        if len(metrics_list) == 2:
            # Simple A/B test
            analysis_result = calculate_significance(
                metrics_list[0], metrics_list[1], test.success_metric
            )

            analysis = TestAnalysis(
                winning_variant=analysis_result.winning_variant,
                confidence=analysis_result.confidence,
                p_value=analysis_result.p_value,
                is_significant=analysis_result.is_significant,
                improvement=analysis_result.improvement,
            )
        else:
            # Multivariate test - find overall winner
            winner_result = find_overall_winner(metrics_list, test.success_metric)

            if winner_result:
                winner_id, wins = winner_result

                # Get significance vs best competitor
                winner_metrics = metrics_data[winner_id]
                other_metrics = [m for m in metrics_list if m.variant_id != winner_id]

                # Compare with best competitor
                best_competitor = max(
                    other_metrics,
                    key=lambda m: m.ctr if test.success_metric == "ctr" else m.engagement_score,
                )

                sig_result = calculate_significance(
                    winner_metrics, best_competitor, test.success_metric
                )

                analysis = TestAnalysis(
                    winning_variant=winner_id,
                    confidence=sig_result.confidence,
                    p_value=sig_result.p_value,
                    is_significant=sig_result.is_significant,
                    improvement=sig_result.improvement,
                )
            else:
                # No clear winner
                analysis = TestAnalysis(
                    winning_variant=None,
                    confidence=0.0,
                    p_value=1.0,
                    is_significant=False,
                    improvement=None,
                )

        # Generate recommendation
        recommendation = self._generate_recommendation(test, analysis, total_views, duration)

        return TestReport(
            test_id=test.test_id,
            content_id=test.content_id,
            status=test.status.value,
            duration_days=duration,
            total_views=total_views,
            success_metric=test.success_metric,
            variants=variant_performances,
            analysis=analysis,
            recommendation=recommendation,
            created_at=datetime.now(),
        )

    def _generate_recommendation(
        self, test: ABTest, analysis: TestAnalysis, total_views: int, duration: int
    ) -> str:
        """Generate recommendation based on test results.

        Args:
            test: Test configuration
            analysis: Statistical analysis
            total_views: Total views across variants
            duration: Test duration in days

        Returns:
            Recommendation string
        """
        # Check minimum sample size
        min_views_needed = test.min_sample_size * len(test.variants)

        if total_views < min_views_needed:
            return (
                f"Insufficient data: Need at least {min_views_needed} total views "
                f"({test.min_sample_size} per variant). "
                f"Continue test to gather more data."
            )

        # Check statistical significance
        if not analysis.is_significant:
            if duration < 7:
                return (
                    "No statistically significant difference detected yet. "
                    "Continue test for longer duration (minimum 7 days recommended)."
                )
            else:
                return (
                    "No statistically significant difference detected. "
                    "Variants perform similarly - use the variant that best "
                    "aligns with brand voice or content strategy."
                )

        # Significant result found
        if analysis.winning_variant:
            improvement_str = ""
            if analysis.improvement and analysis.improvement != float("inf"):
                improvement_str = f" with {analysis.improvement:.1f}% improvement"

            return (
                f"Deploy variant {analysis.winning_variant} as primary title{improvement_str}. "
                f"Result is statistically significant at {analysis.confidence:.1f}% confidence level."
            )

        return "Unable to determine clear winner. Review data and consider extending test."


def generate_report(test: ABTest, metrics_data: Dict[str, VariantMetrics]) -> TestReport:
    """Convenience function to generate a test report.

    Args:
        test: ABTest configuration
        metrics_data: Dictionary mapping variant_id to VariantMetrics

    Returns:
        Complete TestReport
    """
    generator = ReportGenerator()
    return generator.generate_report(test, metrics_data)
