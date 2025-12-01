"""Integration test for A/B Testing module.

Tests the complete workflow from test creation to report generation.
"""

import sys
import os
import pytest
from datetime import datetime, timedelta

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from test_manager import ABTestManager, TitleVariant, TestStatus
from variant_router import VariantRouter
from statistics import VariantMetrics
from report_generator import generate_report


class TestABTestingIntegration:
    """Integration tests for complete A/B testing workflow."""
    
    def test_complete_ab_test_workflow(self):
        """Test complete workflow from creation to report generation."""
        # Step 1: Create test manager and variants
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "How AI is Transforming Healthcare", 50),
            TitleVariant("B", "AI Healthcare Revolution 2025", 50)
        ]
        
        # Step 2: Create and start test
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        test = manager.create_test(
            test_id="integration-test-001",
            content_id="content-health-ai",
            variants=variants,
            start_date=start_date,
            end_date=end_date,
            min_sample_size=1000,
            success_metric="ctr"
        )
        
        assert test.status == TestStatus.DRAFT
        
        manager.start_test("integration-test-001")
        assert test.status == TestStatus.ACTIVE
        
        # Step 3: Assign users to variants
        router = VariantRouter()
        assignments = {"A": 0, "B": 0}
        
        for i in range(1000):
            user_id = f"user_{i:05d}"
            variant = router.assign(user_id, test.variants)
            assignments[variant.variant_id] += 1
        
        # Verify distribution is reasonable (45-55% each)
        a_percent = (assignments["A"] / 1000) * 100
        b_percent = (assignments["B"] / 1000) * 100
        
        assert 40 <= a_percent <= 60
        assert 40 <= b_percent <= 60
        
        # Step 4: Simulate metrics collection
        metrics_data = {
            "A": VariantMetrics("A", views=2000, clicks=200, engagement_score=0.70),
            "B": VariantMetrics("B", views=2000, clicks=280, engagement_score=0.78)
        }
        
        # Step 5: Complete test and generate report
        manager.complete_test("integration-test-001")
        assert test.status == TestStatus.COMPLETED
        
        report = generate_report(test, metrics_data)
        
        # Step 6: Verify report
        assert report.test_id == "integration-test-001"
        assert report.content_id == "content-health-ai"
        assert report.status == "completed"
        assert report.total_views == 4000
        assert len(report.variants) == 2
        
        # Verify analysis
        assert report.analysis.winning_variant == "B"  # B has higher CTR
        assert report.analysis.is_significant  # With this difference, should be significant
        assert report.analysis.p_value < 0.05
        assert "Deploy variant B" in report.recommendation
        
        # Verify report export
        report_dict = report.to_dict()
        assert report_dict["test_id"] == "integration-test-001"
        assert report_dict["analysis"]["winning_variant"] == "B"
        assert report_dict["analysis"]["is_significant"]
    
    def test_multivariate_test_workflow(self):
        """Test workflow with 3 variants."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title Variant A", 33.33),
            TitleVariant("B", "Title Variant B", 33.33),
            TitleVariant("C", "Title Variant C", 33.34)
        ]
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=14)
        
        test = manager.create_test(
            test_id="integration-test-002",
            content_id="content-multivariate",
            variants=variants,
            start_date=start_date,
            end_date=end_date,
            min_sample_size=1000,
            success_metric="ctr"
        )
        
        manager.start_test("integration-test-002")
        
        # Assign users
        router = VariantRouter()
        for i in range(3000):
            router.assign(f"user_{i}", test.variants)
        
        # Check distribution
        stats = router.get_distribution_stats(test.variants)
        for variant_id in ["A", "B", "C"]:
            assert 28 <= stats[variant_id] <= 38  # ~33% ±5%
        
        # Generate metrics with clear winner
        metrics_data = {
            "A": VariantMetrics("A", views=1500, clicks=120, engagement_score=0.65),
            "B": VariantMetrics("B", views=1500, clicks=180, engagement_score=0.75),
            "C": VariantMetrics("C", views=1500, clicks=135, engagement_score=0.68)
        }
        
        manager.complete_test("integration-test-002")
        report = generate_report(test, metrics_data)
        
        # B should be the winner
        assert report.analysis.winning_variant == "B"
        assert len(report.variants) == 3
    
    def test_insufficient_data_workflow(self):
        """Test workflow when insufficient data collected."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=3)
        
        test = manager.create_test(
            test_id="integration-test-003",
            content_id="content-insufficient",
            variants=variants,
            start_date=start_date,
            end_date=end_date,
            min_sample_size=1000,
            success_metric="ctr"
        )
        
        manager.start_test("integration-test-003")
        
        # Only small amount of data collected
        metrics_data = {
            "A": VariantMetrics("A", views=200, clicks=20, engagement_score=0.6),
            "B": VariantMetrics("B", views=250, clicks=25, engagement_score=0.65)
        }
        
        # Test is still active (not enough data)
        report = generate_report(test, metrics_data)
        
        # Should recommend continuing test
        assert "Insufficient data" in report.recommendation
        assert "Continue test" in report.recommendation
    
    def test_pause_and_resume_workflow(self):
        """Test pausing and resuming a test."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        test = manager.create_test(
            test_id="integration-test-004",
            content_id="content-pause-resume",
            variants=variants,
            start_date=start_date,
            end_date=end_date
        )
        
        # Start test
        manager.start_test("integration-test-004")
        assert test.status == TestStatus.ACTIVE
        
        # Pause test
        manager.pause_test("integration-test-004")
        assert test.status == TestStatus.PAUSED
        
        # Can complete from paused state
        manager.complete_test("integration-test-004")
        assert test.status == TestStatus.COMPLETED
    
    def test_consistent_assignment_across_sessions(self):
        """Test that same user always gets same variant."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        test = manager.create_test(
            test_id="integration-test-005",
            content_id="content-consistency",
            variants=variants,
            start_date=start_date,
            end_date=end_date
        )
        
        router = VariantRouter()
        
        # Assign same users multiple times
        test_users = ["user_001", "user_002", "user_003", "user_004", "user_005"]
        
        for _ in range(5):
            for user_id in test_users:
                variant = router.assign(user_id, test.variants)
                
                # Verify consistency
                stored_assignment = router.get_assignment(user_id)
                assert stored_assignment == variant.variant_id
                
                # Verify assignment is consistent
                assert router.verify_consistency(user_id, test.variants)


class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    def test_cannot_start_active_test(self):
        """Test that cannot start already active test."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        test = manager.create_test(
            test_id="error-test-001",
            content_id="content-error",
            variants=variants,
            start_date=start_date,
            end_date=end_date
        )
        
        manager.start_test("error-test-001")
        
        with pytest.raises(ValueError, match="Cannot start test"):
            manager.start_test("error-test-001")
    
    def test_cannot_generate_report_with_missing_metrics(self):
        """Test error when generating report with missing metrics."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        test = manager.create_test(
            test_id="error-test-002",
            content_id="content-error",
            variants=variants,
            start_date=start_date,
            end_date=end_date
        )
        
        # Missing metrics for variant B
        metrics_data = {
            "A": VariantMetrics("A", views=1000, clicks=100, engagement_score=0.7)
        }
        
        with pytest.raises(ValueError, match="Missing metrics for variant B"):
            generate_report(test, metrics_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
