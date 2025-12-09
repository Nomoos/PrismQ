"""A/B Test Management - Test lifecycle and configuration management."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TestStatus(Enum):
    """Status of an A/B test."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TitleVariant:
    """Represents a single title variant in an A/B test.

    Attributes:
        variant_id: Unique identifier (A, B, C, etc.)
        title: The title text to test
        traffic_percent: Percentage of traffic assigned (0-100)
    """

    variant_id: str
    title: str
    traffic_percent: float

    def __post_init__(self):
        """Validate variant data."""
        if not self.variant_id:
            raise ValueError("variant_id cannot be empty")
        if not self.title:
            raise ValueError("title cannot be empty")
        if not 0 <= self.traffic_percent <= 100:
            raise ValueError("traffic_percent must be between 0 and 100")


@dataclass
class ABTest:
    """Configuration for an A/B test.

    Attributes:
        test_id: Unique identifier for the test
        content_id: ID of the content being tested
        variants: List of title variants to test
        start_date: When the test starts (or started)
        end_date: When the test ends (or ended)
        status: Current test status
        min_sample_size: Minimum views required per variant
        success_metric: Metric to optimize ('ctr', 'engagement', 'views')
        created_at: Test creation timestamp
        config: Additional configuration options
    """

    test_id: str
    content_id: str
    variants: List[TitleVariant]
    start_date: datetime
    end_date: datetime
    status: TestStatus = TestStatus.DRAFT
    min_sample_size: int = 1000
    success_metric: str = "ctr"
    created_at: datetime = field(default_factory=datetime.now)
    config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate test configuration."""
        if not self.test_id:
            raise ValueError("test_id cannot be empty")
        if not self.content_id:
            raise ValueError("content_id cannot be empty")
        if not self.variants:
            raise ValueError("variants list cannot be empty")
        if len(self.variants) < 2:
            raise ValueError("At least 2 variants required for A/B testing")
        if len(self.variants) > 5:
            raise ValueError("Maximum 5 variants supported")
        if self.min_sample_size < 100:
            raise ValueError("min_sample_size must be at least 100")
        if self.success_metric not in ["ctr", "engagement", "views"]:
            raise ValueError("success_metric must be 'ctr', 'engagement', or 'views'")

        # Validate traffic distribution
        total_traffic = sum(v.traffic_percent for v in self.variants)
        if abs(total_traffic - 100.0) > 0.1:  # Allow small floating point errors
            raise ValueError(f"Traffic percentages must sum to 100, got {total_traffic}")

        # Validate date order
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")


class ABTestManager:
    """Manages A/B test lifecycle operations."""

    def __init__(self):
        """Initialize the test manager."""
        self._tests: Dict[str, ABTest] = {}

    def create_test(
        self,
        test_id: str,
        content_id: str,
        variants: List[TitleVariant],
        start_date: datetime,
        end_date: datetime,
        min_sample_size: int = 1000,
        success_metric: str = "ctr",
        config: Optional[Dict[str, Any]] = None,
    ) -> ABTest:
        """Create a new A/B test.

        Args:
            test_id: Unique test identifier
            content_id: Content being tested
            variants: List of title variants
            start_date: Test start date
            end_date: Test end date
            min_sample_size: Minimum views per variant
            success_metric: Metric to optimize
            config: Additional configuration

        Returns:
            Created ABTest instance

        Raises:
            ValueError: If test_id already exists or validation fails
        """
        if test_id in self._tests:
            raise ValueError(f"Test with id '{test_id}' already exists")

        test = ABTest(
            test_id=test_id,
            content_id=content_id,
            variants=variants,
            start_date=start_date,
            end_date=end_date,
            status=TestStatus.DRAFT,
            min_sample_size=min_sample_size,
            success_metric=success_metric,
            config=config or {},
        )

        self._tests[test_id] = test
        return test

    def get_test(self, test_id: str) -> Optional[ABTest]:
        """Get a test by ID.

        Args:
            test_id: Test identifier

        Returns:
            ABTest instance or None if not found
        """
        return self._tests.get(test_id)

    def start_test(self, test_id: str) -> ABTest:
        """Start a test (move from DRAFT to ACTIVE).

        Args:
            test_id: Test identifier

        Returns:
            Updated ABTest instance

        Raises:
            ValueError: If test not found or already active
        """
        test = self._tests.get(test_id)
        if not test:
            raise ValueError(f"Test '{test_id}' not found")

        if test.status != TestStatus.DRAFT:
            raise ValueError(f"Cannot start test in '{test.status.value}' status")

        test.status = TestStatus.ACTIVE
        return test

    def pause_test(self, test_id: str) -> ABTest:
        """Pause an active test.

        Args:
            test_id: Test identifier

        Returns:
            Updated ABTest instance

        Raises:
            ValueError: If test not found or not active
        """
        test = self._tests.get(test_id)
        if not test:
            raise ValueError(f"Test '{test_id}' not found")

        if test.status != TestStatus.ACTIVE:
            raise ValueError(f"Can only pause ACTIVE tests, current status: '{test.status.value}'")

        test.status = TestStatus.PAUSED
        return test

    def complete_test(self, test_id: str) -> ABTest:
        """Mark a test as completed.

        Args:
            test_id: Test identifier

        Returns:
            Updated ABTest instance

        Raises:
            ValueError: If test not found
        """
        test = self._tests.get(test_id)
        if not test:
            raise ValueError(f"Test '{test_id}' not found")

        if test.status not in [TestStatus.ACTIVE, TestStatus.PAUSED]:
            raise ValueError(
                f"Can only complete ACTIVE or PAUSED tests, current status: '{test.status.value}'"
            )

        test.status = TestStatus.COMPLETED
        return test

    def cancel_test(self, test_id: str) -> ABTest:
        """Cancel a test.

        Args:
            test_id: Test identifier

        Returns:
            Updated ABTest instance

        Raises:
            ValueError: If test not found or already completed
        """
        test = self._tests.get(test_id)
        if not test:
            raise ValueError(f"Test '{test_id}' not found")

        if test.status == TestStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed test")

        test.status = TestStatus.CANCELLED
        return test

    def list_tests(
        self, status: Optional[TestStatus] = None, content_id: Optional[str] = None
    ) -> List[ABTest]:
        """List tests with optional filtering.

        Args:
            status: Filter by status
            content_id: Filter by content ID

        Returns:
            List of matching ABTest instances
        """
        tests = list(self._tests.values())

        if status:
            tests = [t for t in tests if t.status == status]

        if content_id:
            tests = [t for t in tests if t.content_id == content_id]

        return tests
