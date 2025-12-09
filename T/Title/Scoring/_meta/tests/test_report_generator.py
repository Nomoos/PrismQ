"""Tests for Report Generator module."""

import os
import sys
from datetime import datetime, timedelta

import pytest

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from statistics import VariantMetrics

from report_generator import (
    ReportGenerator,
    TestAnalysis,
    TestReport,
    VariantPerformance,
    generate_report,
)
from test_manager import ABTest, TestStatus, TitleVariant


class TestVariantPerformance:
    """Tests for VariantPerformance dataclass."""

    def test_create_variant_performance(self):
        """Test creating variant performance object."""
        perf = VariantPerformance(
            variant_id="A",
            title="Test Title A",
            views=1000,
            clicks=100,
            ctr=10.0,
            engagement_score=0.75,
        )

        assert perf.variant_id == "A"
        assert perf.title == "Test Title A"
        assert perf.views == 1000
        assert perf.clicks == 100
        assert perf.ctr == 10.0
        assert perf.engagement_score == 0.75


class TestTestAnalysis:
    """Tests for TestAnalysis dataclass."""

    def test_create_test_analysis(self):
        """Test creating test analysis object."""
        analysis = TestAnalysis(
            winning_variant="B",
            confidence=97.5,
            p_value=0.025,
            is_significant=True,
            improvement=15.5,
        )

        assert analysis.winning_variant == "B"
        assert analysis.confidence == 97.5
        assert analysis.p_value == 0.025
        assert analysis.is_significant
        assert analysis.improvement == 15.5


class TestTestReport:
    """Tests for TestReport dataclass."""

    def test_create_test_report(self):
        """Test creating test report."""
        variants = [
            VariantPerformance("A", "Title A", 1000, 100, 10.0, 0.7),
            VariantPerformance("B", "Title B", 1000, 120, 12.0, 0.75),
        ]

        analysis = TestAnalysis("B", 95.0, 0.05, True, 20.0)

        report = TestReport(
            test_id="test-001",
            content_id="content-123",
            status="completed",
            duration_days=7,
            total_views=2000,
            success_metric="ctr",
            variants=variants,
            analysis=analysis,
            recommendation="Deploy variant B",
            created_at=datetime.now(),
        )

        assert report.test_id == "test-001"
        assert report.content_id == "content-123"
        assert len(report.variants) == 2

    def test_to_dict(self):
        """Test converting report to dictionary."""
        variants = [
            VariantPerformance("A", "Title A", 1000, 100, 10.0, 0.7),
            VariantPerformance("B", "Title B", 1000, 120, 12.0, 0.75),
        ]

        analysis = TestAnalysis("B", 95.0, 0.05, True, 20.0)

        report = TestReport(
            test_id="test-001",
            content_id="content-123",
            status="completed",
            duration_days=7,
            total_views=2000,
            success_metric="ctr",
            variants=variants,
            analysis=analysis,
            recommendation="Deploy variant B",
            created_at=datetime.now(),
        )

        report_dict = report.to_dict()

        assert report_dict["test_id"] == "test-001"
        assert report_dict["content_id"] == "content-123"
        assert report_dict["status"] == "completed"
        assert report_dict["duration_days"] == 7
        assert report_dict["total_views"] == 2000
        assert len(report_dict["variants"]) == 2
        assert report_dict["analysis"]["winning_variant"] == "B"
        assert report_dict["analysis"]["is_significant"]
        assert report_dict["analysis"]["improvement"] == "+20.0%"


class TestReportGenerator:
    """Tests for ReportGenerator class."""

    def test_generate_ab_test_report(self):
        """Test generating report for simple A/B test."""
        # Create test
        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        start = datetime.now() - timedelta(days=7)
        end = datetime.now()

        test = ABTest(
            test_id="test-001",
            content_id="content-123",
            variants=variants,
            start_date=start,
            end_date=end,
            status=TestStatus.COMPLETED,
            min_sample_size=1000,
            success_metric="ctr",
        )

        # Create metrics
        metrics_data = {
            "A": VariantMetrics("A", 2000, 200, 0.7),  # 10% CTR
            "B": VariantMetrics("B", 2000, 300, 0.8),  # 15% CTR
        }

        # Generate report
        generator = ReportGenerator()
        report = generator.generate_report(test, metrics_data)

        assert report.test_id == "test-001"
        assert report.content_id == "content-123"
        assert report.duration_days == 7
        assert report.total_views == 4000
        assert len(report.variants) == 2
        assert report.analysis.winning_variant == "B"
        assert report.analysis.is_significant
        assert "Deploy variant B" in report.recommendation

    def test_generate_multivariate_test_report(self):
        """Test generating report for multivariate test."""
        # Create test with 3 variants
        variants = [
            TitleVariant("A", "Title A", 33.33),
            TitleVariant("B", "Title B", 33.33),
            TitleVariant("C", "Title C", 33.34),
        ]

        start = datetime.now() - timedelta(days=10)
        end = datetime.now()

        test = ABTest(
            test_id="test-002",
            content_id="content-456",
            variants=variants,
            start_date=start,
            end_date=end,
            status=TestStatus.COMPLETED,
            min_sample_size=1000,
            success_metric="ctr",
        )

        # Create metrics with clear winner
        metrics_data = {
            "A": VariantMetrics("A", 1500, 120, 0.6),  # 8% CTR
            "B": VariantMetrics("B", 1500, 180, 0.75),  # 12% CTR
            "C": VariantMetrics("C", 1500, 135, 0.65),  # 9% CTR
        }

        # Generate report
        generator = ReportGenerator()
        report = generator.generate_report(test, metrics_data)

        assert report.test_id == "test-002"
        assert report.duration_days == 10
        assert report.total_views == 4500
        assert len(report.variants) == 3
        assert report.analysis.winning_variant == "B"

    def test_generate_report_insufficient_data(self):
        """Test report with insufficient data."""
        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        start = datetime.now() - timedelta(days=2)
        end = datetime.now()

        test = ABTest(
            test_id="test-003",
            content_id="content-789",
            variants=variants,
            start_date=start,
            end_date=end,
            status=TestStatus.ACTIVE,
            min_sample_size=1000,
            success_metric="ctr",
        )

        # Insufficient views
        metrics_data = {
            "A": VariantMetrics("A", 300, 30, 0.6),
            "B": VariantMetrics("B", 400, 40, 0.7),
        }

        generator = ReportGenerator()
        report = generator.generate_report(test, metrics_data)

        assert "Insufficient data" in report.recommendation
        assert "Continue test" in report.recommendation

    def test_generate_report_no_significance(self):
        """Test report when no significant difference found."""
        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        start = datetime.now() - timedelta(days=14)
        end = datetime.now()

        test = ABTest(
            test_id="test-004",
            content_id="content-999",
            variants=variants,
            start_date=start,
            end_date=end,
            status=TestStatus.COMPLETED,
            min_sample_size=1000,
            success_metric="ctr",
        )

        # Very similar performance
        metrics_data = {
            "A": VariantMetrics("A", 2000, 200, 0.7),
            "B": VariantMetrics("B", 2000, 202, 0.71),
        }

        generator = ReportGenerator()
        report = generator.generate_report(test, metrics_data)

        assert not report.analysis.is_significant
        assert "No statistically significant difference" in report.recommendation
        assert "perform similarly" in report.recommendation

    def test_missing_metrics_error(self):
        """Test error when metrics missing for variant."""
        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        start = datetime.now() - timedelta(days=7)
        end = datetime.now()

        test = ABTest(
            test_id="test-005",
            content_id="content-111",
            variants=variants,
            start_date=start,
            end_date=end,
            status=TestStatus.COMPLETED,
        )

        # Missing metrics for variant B
        metrics_data = {"A": VariantMetrics("A", 1000, 100, 0.7)}

        generator = ReportGenerator()

        with pytest.raises(ValueError, match="Missing metrics for variant B"):
            generator.generate_report(test, metrics_data)


class TestGenerateReportFunction:
    """Tests for generate_report convenience function."""

    def test_generate_report_function(self):
        """Test the generate_report convenience function."""
        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        start = datetime.now() - timedelta(days=7)
        end = datetime.now()

        test = ABTest(
            test_id="test-006",
            content_id="content-222",
            variants=variants,
            start_date=start,
            end_date=end,
            status=TestStatus.COMPLETED,
        )

        metrics_data = {
            "A": VariantMetrics("A", 1500, 150, 0.7),
            "B": VariantMetrics("B", 1500, 195, 0.75),
        }

        report = generate_report(test, metrics_data)

        assert isinstance(report, TestReport)
        assert report.test_id == "test-006"
        assert len(report.variants) == 2


class TestRecommendations:
    """Tests for recommendation generation logic."""

    def test_recommendation_clear_winner(self):
        """Test recommendation with clear winner."""
        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        start = datetime.now() - timedelta(days=10)
        end = datetime.now()

        test = ABTest(
            test_id="test-007",
            content_id="content-333",
            variants=variants,
            start_date=start,
            end_date=end,
            status=TestStatus.COMPLETED,
            min_sample_size=1000,
        )

        # Clear winner with large sample
        metrics_data = {
            "A": VariantMetrics("A", 3000, 300, 0.7),
            "B": VariantMetrics("B", 3000, 450, 0.8),
        }

        report = generate_report(test, metrics_data)

        assert report.analysis.is_significant
        assert "Deploy variant B" in report.recommendation
        assert "statistically significant" in report.recommendation

    def test_recommendation_continue_test(self):
        """Test recommendation to continue test."""
        variants = [TitleVariant("A", "Title A", 50), TitleVariant("B", "Title B", 50)]

        start = datetime.now() - timedelta(days=3)
        end = datetime.now()

        test = ABTest(
            test_id="test-008",
            content_id="content-444",
            variants=variants,
            start_date=start,
            end_date=end,
            status=TestStatus.ACTIVE,
            min_sample_size=1000,
        )

        # Some difference but short duration
        metrics_data = {
            "A": VariantMetrics("A", 800, 80, 0.7),
            "B": VariantMetrics("B", 800, 96, 0.75),
        }

        report = generate_report(test, metrics_data)

        if not report.analysis.is_significant:
            assert "Continue test" in report.recommendation
