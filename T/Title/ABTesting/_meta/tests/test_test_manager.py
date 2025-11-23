"""Tests for A/B Test Manager module."""

import sys
import os
import pytest
from datetime import datetime, timedelta

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from test_manager import (
    ABTest,
    TitleVariant,
    ABTestManager,
    TestStatus
)


class TestTitleVariant:
    """Tests for TitleVariant class."""
    
    def test_create_valid_variant(self):
        """Test creating a valid variant."""
        variant = TitleVariant(
            variant_id="A",
            title="Test Title",
            traffic_percent=50.0
        )
        
        assert variant.variant_id == "A"
        assert variant.title == "Test Title"
        assert variant.traffic_percent == 50.0
    
    def test_variant_id_validation(self):
        """Test variant_id cannot be empty."""
        with pytest.raises(ValueError, match="variant_id cannot be empty"):
            TitleVariant(variant_id="", title="Test", traffic_percent=50)
    
    def test_title_validation(self):
        """Test title cannot be empty."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            TitleVariant(variant_id="A", title="", traffic_percent=50)
    
    def test_traffic_percent_validation(self):
        """Test traffic_percent must be between 0 and 100."""
        with pytest.raises(ValueError, match="traffic_percent must be between 0 and 100"):
            TitleVariant(variant_id="A", title="Test", traffic_percent=150)
        
        with pytest.raises(ValueError, match="traffic_percent must be between 0 and 100"):
            TitleVariant(variant_id="A", title="Test", traffic_percent=-10)


class TestABTest:
    """Tests for ABTest class."""
    
    def test_create_valid_test(self):
        """Test creating a valid A/B test."""
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        test = ABTest(
            test_id="test-001",
            content_id="content-123",
            variants=variants,
            start_date=start,
            end_date=end
        )
        
        assert test.test_id == "test-001"
        assert test.content_id == "content-123"
        assert len(test.variants) == 2
        assert test.status == TestStatus.DRAFT
        assert test.min_sample_size == 1000
        assert test.success_metric == "ctr"
    
    def test_minimum_variants_validation(self):
        """Test at least 2 variants are required."""
        variants = [TitleVariant("A", "Title A", 100)]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        with pytest.raises(ValueError, match="At least 2 variants required"):
            ABTest(
                test_id="test-001",
                content_id="content-123",
                variants=variants,
                start_date=start,
                end_date=end
            )
    
    def test_maximum_variants_validation(self):
        """Test maximum 5 variants allowed."""
        variants = [
            TitleVariant("A", "Title A", 16.67),
            TitleVariant("B", "Title B", 16.67),
            TitleVariant("C", "Title C", 16.67),
            TitleVariant("D", "Title D", 16.67),
            TitleVariant("E", "Title E", 16.67),
            TitleVariant("F", "Title F", 16.65),
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        with pytest.raises(ValueError, match="Maximum 5 variants supported"):
            ABTest(
                test_id="test-001",
                content_id="content-123",
                variants=variants,
                start_date=start,
                end_date=end
            )
    
    def test_traffic_distribution_validation(self):
        """Test traffic percentages must sum to 100."""
        variants = [
            TitleVariant("A", "Title A", 40),
            TitleVariant("B", "Title B", 40)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        with pytest.raises(ValueError, match="Traffic percentages must sum to 100"):
            ABTest(
                test_id="test-001",
                content_id="content-123",
                variants=variants,
                start_date=start,
                end_date=end
            )
    
    def test_date_order_validation(self):
        """Test start_date must be before end_date."""
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start - timedelta(days=7)  # End before start
        
        with pytest.raises(ValueError, match="start_date must be before end_date"):
            ABTest(
                test_id="test-001",
                content_id="content-123",
                variants=variants,
                start_date=start,
                end_date=end
            )
    
    def test_min_sample_size_validation(self):
        """Test min_sample_size must be at least 100."""
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        with pytest.raises(ValueError, match="min_sample_size must be at least 100"):
            ABTest(
                test_id="test-001",
                content_id="content-123",
                variants=variants,
                start_date=start,
                end_date=end,
                min_sample_size=50
            )
    
    def test_success_metric_validation(self):
        """Test success_metric must be valid."""
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        with pytest.raises(ValueError, match="success_metric must be"):
            ABTest(
                test_id="test-001",
                content_id="content-123",
                variants=variants,
                start_date=start,
                end_date=end,
                success_metric="invalid"
            )


class TestABTestManager:
    """Tests for ABTestManager class."""
    
    def test_create_test(self):
        """Test creating a test through manager."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        test = manager.create_test(
            test_id="test-001",
            content_id="content-123",
            variants=variants,
            start_date=start,
            end_date=end
        )
        
        assert test.test_id == "test-001"
        assert test.status == TestStatus.DRAFT
    
    def test_create_duplicate_test(self):
        """Test cannot create test with duplicate ID."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        manager.create_test(
            test_id="test-001",
            content_id="content-123",
            variants=variants,
            start_date=start,
            end_date=end
        )
        
        with pytest.raises(ValueError, match="already exists"):
            manager.create_test(
                test_id="test-001",
                content_id="content-456",
                variants=variants,
                start_date=start,
                end_date=end
            )
    
    def test_get_test(self):
        """Test retrieving a test by ID."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        created_test = manager.create_test(
            test_id="test-001",
            content_id="content-123",
            variants=variants,
            start_date=start,
            end_date=end
        )
        
        retrieved_test = manager.get_test("test-001")
        assert retrieved_test == created_test
        
        # Test non-existent test
        assert manager.get_test("test-999") is None
    
    def test_start_test(self):
        """Test starting a test."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        test = manager.create_test(
            test_id="test-001",
            content_id="content-123",
            variants=variants,
            start_date=start,
            end_date=end
        )
        
        assert test.status == TestStatus.DRAFT
        
        started_test = manager.start_test("test-001")
        assert started_test.status == TestStatus.ACTIVE
    
    def test_pause_test(self):
        """Test pausing an active test."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        manager.create_test(
            test_id="test-001",
            content_id="content-123",
            variants=variants,
            start_date=start,
            end_date=end
        )
        
        manager.start_test("test-001")
        paused_test = manager.pause_test("test-001")
        
        assert paused_test.status == TestStatus.PAUSED
    
    def test_complete_test(self):
        """Test completing a test."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        manager.create_test(
            test_id="test-001",
            content_id="content-123",
            variants=variants,
            start_date=start,
            end_date=end
        )
        
        manager.start_test("test-001")
        completed_test = manager.complete_test("test-001")
        
        assert completed_test.status == TestStatus.COMPLETED
    
    def test_cancel_test(self):
        """Test cancelling a test."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        manager.create_test(
            test_id="test-001",
            content_id="content-123",
            variants=variants,
            start_date=start,
            end_date=end
        )
        
        cancelled_test = manager.cancel_test("test-001")
        assert cancelled_test.status == TestStatus.CANCELLED
    
    def test_list_tests(self):
        """Test listing tests with filtering."""
        manager = ABTestManager()
        
        variants = [
            TitleVariant("A", "Title A", 50),
            TitleVariant("B", "Title B", 50)
        ]
        
        start = datetime.now()
        end = start + timedelta(days=7)
        
        # Create multiple tests
        manager.create_test(
            test_id="test-001",
            content_id="content-123",
            variants=variants,
            start_date=start,
            end_date=end
        )
        
        manager.create_test(
            test_id="test-002",
            content_id="content-123",
            variants=variants,
            start_date=start,
            end_date=end
        )
        
        manager.create_test(
            test_id="test-003",
            content_id="content-456",
            variants=variants,
            start_date=start,
            end_date=end
        )
        
        manager.start_test("test-001")
        
        # List all tests
        all_tests = manager.list_tests()
        assert len(all_tests) == 3
        
        # Filter by status
        active_tests = manager.list_tests(status=TestStatus.ACTIVE)
        assert len(active_tests) == 1
        assert active_tests[0].test_id == "test-001"
        
        # Filter by content_id
        content_tests = manager.list_tests(content_id="content-123")
        assert len(content_tests) == 2
