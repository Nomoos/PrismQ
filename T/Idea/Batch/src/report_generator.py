"""Batch report generator for batch processing results.

This module generates comprehensive reports for batch processing operations,
including success/failure statistics, timing data, and detailed error information.
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class BatchItemReport:
    """Report for a single item in a batch.
    
    Attributes:
        idea_id: ID of the processed idea
        status: Processing status ('success' | 'failed')
        processing_time: Time taken to process in seconds
        attempts: Number of processing attempts
        error: Error message if failed
        result_summary: Brief summary of result
    """
    idea_id: str
    status: str
    processing_time: float
    attempts: int
    error: Optional[str] = None
    result_summary: Optional[str] = None


@dataclass
class BatchReport:
    """Comprehensive batch processing report.
    
    Attributes:
        batch_id: Unique batch identifier
        total_items: Total number of items in batch
        processed_items: Number of items processed
        success_count: Number of successful items
        failure_count: Number of failed items
        total_duration: Total batch processing time in seconds
        avg_processing_time: Average processing time per item in seconds
        started_at: Batch start timestamp
        completed_at: Batch completion timestamp
        failures: List of failed item details
        config: Batch configuration used
    """
    batch_id: str
    total_items: int
    processed_items: int
    success_count: int
    failure_count: int
    total_duration: float
    avg_processing_time: float
    started_at: str
    completed_at: str
    failures: List[Dict[str, Any]]
    config: Dict[str, Any]


class ReportGenerator:
    """Generator for batch processing reports."""
    
    def __init__(self):
        """Initialize report generator."""
        pass
    
    def generate_report(
        self,
        batch_id: str,
        results: List[Dict[str, Any]],
        started_at: datetime,
        completed_at: datetime,
        config: Dict[str, Any]
    ) -> BatchReport:
        """Generate a comprehensive batch report.
        
        Args:
            batch_id: Unique batch identifier
            results: List of batch processing results
            started_at: Batch start time
            completed_at: Batch completion time
            config: Batch configuration
            
        Returns:
            BatchReport instance
        """
        total_items = len(results)
        success_count = sum(1 for r in results if r.get('status') == 'success')
        failure_count = total_items - success_count
        
        total_duration = (completed_at - started_at).total_seconds()
        
        # Calculate average processing time
        processing_times = [
            r.get('duration', 0.0) for r in results 
            if r.get('duration') is not None
        ]
        avg_processing_time = (
            sum(processing_times) / len(processing_times) 
            if processing_times else 0.0
        )
        
        # Extract failure details
        failures = [
            {
                'idea_id': r.get('idea_id', 'unknown'),
                'error': r.get('error', 'Unknown error'),
                'attempts': r.get('attempts', 0)
            }
            for r in results if r.get('status') == 'failed'
        ]
        
        return BatchReport(
            batch_id=batch_id,
            total_items=total_items,
            processed_items=total_items,
            success_count=success_count,
            failure_count=failure_count,
            total_duration=total_duration,
            avg_processing_time=avg_processing_time,
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat(),
            failures=failures,
            config=config
        )
    
    def generate_item_report(
        self,
        idea_id: str,
        status: str,
        processing_time: float,
        attempts: int,
        error: Optional[str] = None,
        result_summary: Optional[str] = None
    ) -> BatchItemReport:
        """Generate a report for a single batch item.
        
        Args:
            idea_id: ID of the processed idea
            status: Processing status
            processing_time: Processing time in seconds
            attempts: Number of attempts
            error: Optional error message
            result_summary: Optional result summary
            
        Returns:
            BatchItemReport instance
        """
        return BatchItemReport(
            idea_id=idea_id,
            status=status,
            processing_time=processing_time,
            attempts=attempts,
            error=error,
            result_summary=result_summary
        )
    
    def to_json(self, report: BatchReport) -> str:
        """Convert batch report to JSON string.
        
        Args:
            report: BatchReport instance
            
        Returns:
            JSON string representation
        """
        return json.dumps(asdict(report), indent=2)
    
    def to_csv(self, report: BatchReport) -> str:
        """Convert batch report to CSV format.
        
        Args:
            report: BatchReport instance
            
        Returns:
            CSV string representation
        """
        lines = []
        
        # Header
        lines.append("Batch ID,Total Items,Success Count,Failure Count,Total Duration (s),Avg Processing Time (s)")
        
        # Summary row
        lines.append(
            f"{report.batch_id},{report.total_items},{report.success_count},"
            f"{report.failure_count},{report.total_duration:.2f},"
            f"{report.avg_processing_time:.2f}"
        )
        
        # Failures section
        if report.failures:
            lines.append("")
            lines.append("Failed Items")
            lines.append("Idea ID,Error,Attempts")
            for failure in report.failures:
                lines.append(
                    f"{failure['idea_id']},\"{failure['error']}\",{failure['attempts']}"
                )
        
        return "\n".join(lines)
    
    def print_summary(self, report: BatchReport) -> None:
        """Print a human-readable summary of the batch report.
        
        Args:
            report: BatchReport instance
        """
        print(f"\n{'='*60}")
        print(f"Batch Processing Report: {report.batch_id}")
        print(f"{'='*60}")
        print(f"Total Items:           {report.total_items}")
        print(f"Successful:            {report.success_count}")
        print(f"Failed:                {report.failure_count}")
        print(f"Success Rate:          {report.success_count/report.total_items*100:.1f}%")
        print(f"Total Duration:        {report.total_duration:.2f}s")
        print(f"Avg Processing Time:   {report.avg_processing_time:.2f}s")
        print(f"Started:               {report.started_at}")
        print(f"Completed:             {report.completed_at}")
        
        if report.failures:
            print(f"\nFailed Items ({len(report.failures)}):")
            for i, failure in enumerate(report.failures[:5], 1):  # Show first 5
                print(f"  {i}. {failure['idea_id']}: {failure['error']}")
            if len(report.failures) > 5:
                print(f"  ... and {len(report.failures) - 5} more")
        
        print(f"{'='*60}\n")


__all__ = ["ReportGenerator", "BatchReport", "BatchItemReport"]
