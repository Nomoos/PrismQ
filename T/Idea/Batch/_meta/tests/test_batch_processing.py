"""Tests for batch processing functionality."""

import asyncio
from datetime import datetime, timezone

import pytest

from T.Idea.Batch import (
    BatchConfig,
    BatchProcessor,
    ProcessingMode,
    QueueConfig,
    QueueManager,
    ReportGenerator,
    RetryConfig,
    RetryHandler,
)


# Test fixtures
@pytest.fixture
def sample_ideas_small():
    """Generate 10 sample ideas for testing."""
    return [{"id": f"idea-{i}", "text": f"Test idea {i}"} for i in range(10)]


@pytest.fixture
def sample_ideas_medium():
    """Generate 50 sample ideas for testing."""
    return [{"id": f"idea-{i}", "text": f"Test idea {i}"} for i in range(50)]


@pytest.fixture
def sample_ideas_large():
    """Generate 100 sample ideas for testing."""
    return [{"id": f"idea-{i}", "text": f"Test idea {i}"} for i in range(100)]


# Mock processing functions
async def mock_process_success(idea):
    """Mock processing function that always succeeds."""
    await asyncio.sleep(0.01)  # Simulate processing time
    return {"processed": True, "idea_id": idea.get("id")}


async def mock_process_failure(idea):
    """Mock processing function that always fails."""
    await asyncio.sleep(0.01)
    raise Exception("Simulated processing error")


async def mock_process_intermittent(idea):
    """Mock processing function that fails on specific IDs."""
    await asyncio.sleep(0.01)
    idea_id = idea.get("id", "")
    # Fail on ideas with IDs ending in 5
    if idea_id.endswith("5"):
        raise Exception("Simulated intermittent failure")
    return {"processed": True, "idea_id": idea_id}


# Test BatchProcessor
class TestBatchProcessor:
    """Tests for BatchProcessor class."""

    @pytest.mark.asyncio
    async def test_process_small_batch_parallel(self, sample_ideas_small):
        """Test processing a small batch (10 ideas) in parallel mode."""
        config = BatchConfig(max_concurrent=5, mode=ProcessingMode.PARALLEL, retry_attempts=1)
        processor = BatchProcessor(config)

        report = await processor.process_batch(
            ideas=sample_ideas_small, process_func=mock_process_success
        )

        assert report.total_items == 10
        assert report.success_count == 10
        assert report.failure_count == 0
        assert report.processed_items == 10

    @pytest.mark.asyncio
    async def test_process_small_batch_sequential(self, sample_ideas_small):
        """Test processing a small batch in sequential mode."""
        config = BatchConfig(max_concurrent=1, mode=ProcessingMode.SEQUENTIAL, retry_attempts=1)
        processor = BatchProcessor(config)

        report = await processor.process_batch(
            ideas=sample_ideas_small, process_func=mock_process_success
        )

        assert report.total_items == 10
        assert report.success_count == 10
        assert report.failure_count == 0

    @pytest.mark.asyncio
    async def test_process_medium_batch(self, sample_ideas_medium):
        """Test processing a medium batch (50 ideas)."""
        config = BatchConfig(max_concurrent=10, mode=ProcessingMode.PARALLEL, retry_attempts=1)
        processor = BatchProcessor(config)

        report = await processor.process_batch(
            ideas=sample_ideas_medium, process_func=mock_process_success
        )

        assert report.total_items == 50
        assert report.success_count == 50
        assert report.failure_count == 0

    @pytest.mark.asyncio
    async def test_batch_with_failures(self, sample_ideas_small):
        """Test batch processing with intermittent failures."""
        config = BatchConfig(max_concurrent=5, mode=ProcessingMode.PARALLEL, retry_attempts=1)
        processor = BatchProcessor(config)

        report = await processor.process_batch(
            ideas=sample_ideas_small, process_func=mock_process_intermittent
        )

        assert report.total_items == 10
        # IDs ending in 5: idea-5
        assert report.failure_count == 1
        assert report.success_count == 9

    @pytest.mark.asyncio
    async def test_batch_with_retry_logic(self):
        """Test that retry logic works correctly."""
        ideas = [{"id": "retry-test", "text": "Test retry"}]

        config = BatchConfig(max_concurrent=1, mode=ProcessingMode.PARALLEL, retry_attempts=3)
        processor = BatchProcessor(config)

        # Should fail even with retries
        report = await processor.process_batch(ideas=ideas, process_func=mock_process_failure)

        assert report.total_items == 1
        assert report.failure_count == 1
        assert len(report.failures) == 1
        assert report.failures[0]["attempts"] == 3

    @pytest.mark.asyncio
    async def test_concurrent_processing_speedup(self, sample_ideas_medium):
        """Test that parallel processing is faster than sequential."""
        import time

        # Sequential processing
        seq_config = BatchConfig(max_concurrent=1, mode=ProcessingMode.SEQUENTIAL, retry_attempts=1)
        seq_processor = BatchProcessor(seq_config)

        start = time.time()
        seq_report = await seq_processor.process_batch(
            ideas=sample_ideas_medium, process_func=mock_process_success
        )
        seq_duration = time.time() - start

        # Parallel processing
        par_config = BatchConfig(max_concurrent=10, mode=ProcessingMode.PARALLEL, retry_attempts=1)
        par_processor = BatchProcessor(par_config)

        start = time.time()
        par_report = await par_processor.process_batch(
            ideas=sample_ideas_medium, process_func=mock_process_success
        )
        par_duration = time.time() - start

        # Parallel should be faster
        assert par_duration < seq_duration
        print(f"\nSpeedup: {seq_duration / par_duration:.2f}x")

    @pytest.mark.asyncio
    async def test_batch_report_generation(self, sample_ideas_small):
        """Test that batch reports are generated correctly."""
        config = BatchConfig(max_concurrent=5)
        processor = BatchProcessor(config)

        report = await processor.process_batch(
            ideas=sample_ideas_small, process_func=mock_process_success
        )

        assert report.batch_id is not None
        assert report.total_items == 10
        assert report.avg_processing_time > 0
        assert report.total_duration > 0
        assert report.started_at is not None
        assert report.completed_at is not None


# Test RetryHandler
class TestRetryHandler:
    """Tests for RetryHandler class."""

    @pytest.mark.asyncio
    async def test_retry_success_on_first_attempt(self):
        """Test successful execution on first attempt."""
        config = RetryConfig(max_attempts=3)
        handler = RetryHandler(config)

        result, attempts, error = await handler.execute_with_retry(
            mock_process_success, {"id": "test"}
        )

        assert result is not None
        assert attempts == 1
        assert error is None

    @pytest.mark.asyncio
    async def test_retry_failure_exhausted(self):
        """Test that all retry attempts are exhausted on failure."""
        config = RetryConfig(max_attempts=3, initial_delay=0.01)
        handler = RetryHandler(config)

        result, attempts, error = await handler.execute_with_retry(
            mock_process_failure, {"id": "test"}
        )

        assert result is None
        assert attempts == 3
        assert error is not None

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(max_attempts=3, backoff_factor=2.0, initial_delay=1.0)
        handler = RetryHandler(config)

        # Test delay calculation
        delay1 = handler._calculate_delay(1)
        delay2 = handler._calculate_delay(2)
        delay3 = handler._calculate_delay(3)

        assert delay1 == 1.0
        assert delay2 == 2.0
        assert delay3 == 4.0


# Test ReportGenerator
class TestReportGenerator:
    """Tests for ReportGenerator class."""

    def test_generate_report(self):
        """Test report generation with sample results."""
        from datetime import datetime

        generator = ReportGenerator()

        results = [
            {"idea_id": "idea-1", "status": "success", "duration": 1.5, "attempts": 1},
            {
                "idea_id": "idea-2",
                "status": "failed",
                "duration": 2.0,
                "attempts": 3,
                "error": "Test error",
            },
        ]

        started_at = datetime.now(timezone.utc)
        completed_at = datetime.now(timezone.utc)

        report = generator.generate_report(
            batch_id="test-batch",
            results=results,
            started_at=started_at,
            completed_at=completed_at,
            config={"max_concurrent": 5},
        )

        assert report.batch_id == "test-batch"
        assert report.total_items == 2
        assert report.success_count == 1
        assert report.failure_count == 1
        assert len(report.failures) == 1
        assert report.failures[0]["idea_id"] == "idea-2"

    def test_report_to_json(self):
        """Test JSON serialization of reports."""
        from datetime import datetime

        generator = ReportGenerator()

        results = [{"idea_id": "idea-1", "status": "success", "duration": 1.0, "attempts": 1}]

        report = generator.generate_report(
            batch_id="test",
            results=results,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            config={},
        )

        json_str = generator.to_json(report)
        assert isinstance(json_str, str)
        assert "test" in json_str

    def test_report_to_csv(self):
        """Test CSV conversion of reports."""
        from datetime import datetime

        generator = ReportGenerator()

        results = [{"idea_id": "idea-1", "status": "success", "duration": 1.0, "attempts": 1}]

        report = generator.generate_report(
            batch_id="test",
            results=results,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            config={},
        )

        csv_str = generator.to_csv(report)
        assert isinstance(csv_str, str)
        assert "Batch ID" in csv_str


# Test QueueManager
class TestQueueManager:
    """Tests for QueueManager class."""

    def test_queue_creation(self):
        """Test queue manager initialization."""
        config = QueueConfig(chunk_size=25)
        manager = QueueManager(config)

        assert manager.config.chunk_size == 25
        assert len(manager.queue) == 0
        assert manager.total_items == 0

    def test_add_items_to_queue(self, sample_ideas_small):
        """Test adding items to queue."""
        manager = QueueManager()

        manager.add_items(sample_ideas_small)

        assert len(manager.queue) == 10
        assert manager.total_items == 10

    def test_get_next_chunk(self, sample_ideas_medium):
        """Test retrieving chunks from queue."""
        config = QueueConfig(chunk_size=10)
        manager = QueueManager(config)

        manager.add_items(sample_ideas_medium)

        chunk = manager.get_next_chunk()
        assert len(chunk) == 10
        assert len(manager.queue) == 40

    def test_queue_progress_tracking(self, sample_ideas_small):
        """Test progress tracking in queue."""
        manager = QueueManager()
        manager.add_items(sample_ideas_small)

        # Get initial progress
        progress = manager.get_progress()
        assert progress["total_items"] == 10
        assert progress["processed_count"] == 0

        # Process a chunk
        chunk = manager.get_next_chunk()
        results = [{"idea_id": item["id"], "status": "success"} for item in chunk]
        manager.mark_chunk_processed(results)

        # Check updated progress
        progress = manager.get_progress()
        assert progress["processed_count"] == len(chunk)

    def test_queue_completion(self, sample_ideas_small):
        """Test queue completion detection."""
        manager = QueueManager()
        manager.add_items(sample_ideas_small)

        assert not manager.is_complete()

        # Process all items
        while not manager.is_complete():
            chunk = manager.get_next_chunk()
            if not chunk:
                break
            results = [{"idea_id": item["id"], "status": "success"} for item in chunk]
            manager.mark_chunk_processed(results)

        assert manager.is_complete()


# Integration tests
class TestBatchProcessingIntegration:
    """Integration tests for batch processing."""

    @pytest.mark.asyncio
    async def test_end_to_end_batch_processing(self, sample_ideas_small):
        """Test complete batch processing workflow."""
        config = BatchConfig(max_concurrent=5, mode=ProcessingMode.PARALLEL, retry_attempts=2)
        processor = BatchProcessor(config)

        report = await processor.process_batch(
            ideas=sample_ideas_small, process_func=mock_process_success, batch_id="integration-test"
        )

        # Verify report
        assert report.batch_id == "integration-test"
        assert report.total_items == 10
        assert report.success_count == 10
        assert report.total_duration > 0

        # Generate additional outputs
        generator = ReportGenerator()
        json_report = generator.to_json(report)
        csv_report = generator.to_csv(report)

        assert len(json_report) > 0
        assert len(csv_report) > 0

    @pytest.mark.asyncio
    async def test_large_batch_with_queue_mode(self, sample_ideas_large):
        """Test processing large batch with queue mode."""
        config = BatchConfig(
            max_concurrent=10, mode=ProcessingMode.QUEUE, chunk_size=25, retry_attempts=1
        )
        processor = BatchProcessor(config)

        report = await processor.process_batch(
            ideas=sample_ideas_large, process_func=mock_process_success
        )

        assert report.total_items == 100
        assert report.success_count == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
