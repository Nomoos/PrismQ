# ISSUE-332: Cleanup - Old Tasks and Dead Letter Queue

## Status
✅ **COMPLETE** (2025-11-05)

## Worker Assignment
**Worker 06**: DevOps Engineer (SQLite, Backup, Windows Ops)

## Phase
Phase 2 (Week 2-3) - Implementation

## Component
Backend/src/queue/cleanup.py

## Type
Feature - Queue Cleanup

## Priority
Medium - Prevents database growth

## Description
Implement cleanup utilities for removing old completed tasks and managing the dead letter queue.

## Problem Statement
Queue database grows over time:
- Completed tasks accumulate
- Failed tasks need review
- Database size increases
- Query performance degrades

## Solution
Cleanup system with:
1. Completed task cleanup (age-based)
2. Dead letter queue management
3. Configurable retention periods
4. Statistics tracking
5. Scheduled cleanup jobs

## Implementation Details

### Cleanup Operations
```python
class QueueCleanup:
    async def cleanup_completed_tasks(self, older_than_hours=24):
        """Remove completed tasks older than threshold"""
        cutoff = utc_now() - timedelta(hours=older_than_hours)
        
        result = await db.execute("""
            DELETE FROM task_queue
            WHERE status = 'completed'
            AND completed_at_utc < ?
        """, [cutoff])
        
        return {
            "deleted_count": result.rowcount,
            "older_than_hours": older_than_hours,
            "timestamp": utc_now()
        }
    
    async def cleanup_dead_letter_queue(self, older_than_days=30):
        """Archive or delete old DLQ entries"""
        cutoff = utc_now() - timedelta(days=older_than_days)
        
        # Archive before deleting
        await self.archive_dlq(cutoff)
        
        result = await db.execute("""
            DELETE FROM task_queue
            WHERE status = 'failed'
            AND attempts >= max_attempts
            AND completed_at_utc < ?
        """, [cutoff])
        
        return {
            "deleted_count": result.rowcount,
            "older_than_days": older_than_days
        }
    
    async def get_cleanup_stats(self):
        """Get statistics for cleanup planning"""
        stats = await db.query("""
            SELECT 
                status,
                COUNT(*) as count,
                MIN(created_at_utc) as oldest,
                MAX(created_at_utc) as newest
            FROM task_queue
            GROUP BY status
        """)
        
        return stats
```

### Dead Letter Queue Management
```python
async def review_dead_letter_queue():
    """Get failed tasks for manual review"""
    failed = await db.query("""
        SELECT * FROM task_queue
        WHERE status = 'failed'
        AND attempts >= max_attempts
        ORDER BY completed_at_utc DESC
    """)
    
    return failed

async def retry_from_dlq(task_id):
    """Manually retry a failed task"""
    await db.update("""
        UPDATE task_queue
        SET status = 'queued',
            attempts = 0,
            claimed_by = NULL,
            last_error = NULL
        WHERE id = ?
    """, [task_id])
```

## Acceptance Criteria
- [x] Completed task cleanup working
- [x] Dead letter queue management
- [x] Configurable retention periods
- [x] Statistics tracking
- [x] Archive before delete
- [x] Manual DLQ retry support
- [x] Tests passing
- [x] Part of 52 test suite

## Test Results
- **Integration**: Part of #331 test suite (52 tests)
- **Coverage**: Included in 82-88% coverage
- **Reliability**: Cleanup runs safely

## Dependencies
**Requires**: 
- #321 Core Infrastructure (Worker 01) ✅ COMPLETE
- #331 Maintenance (Worker 06) ✅ COMPLETE

## Enables
- Controlled database size
- DLQ management
- Performance optimization
- Storage efficiency

## Related Issues
- #331: Maintenance (same worker)
- #326: Retry Logic (Worker 03) - Creates DLQ entries

## Files Modified
- Backend/src/queue/cleanup.py (new)
- Backend/src/queue/maintenance.py (integrated)
- tests/queue/test_cleanup.py (included in test_maintenance.py)

## Commits
Week 2-3 implementation commits

## Notes
- Archive before delete prevents data loss
- Configurable retention allows flexibility
- Statistics help plan cleanup schedules
- DLQ review enables manual intervention
- Part of maintenance test suite (52 tests)
- No conflicts with other workers

## Cleanup Schedule Examples

### Daily Cleanup
```python
# Remove completed tasks older than 24 hours
cleanup = QueueCleanup()
result = await cleanup.cleanup_completed_tasks(older_than_hours=24)
logger.info("cleanup_completed", **result)
```

### Weekly DLQ Cleanup
```python
# Archive and remove DLQ entries older than 30 days
result = await cleanup.cleanup_dead_letter_queue(older_than_days=30)
logger.info("dlq_cleanup", **result)
```

### Pre-Cleanup Statistics
```python
# Get stats before cleanup
stats = await cleanup.get_cleanup_stats()

# Example output:
# [
#   {"status": "completed", "count": 1523, "oldest": "2025-10-15", "newest": "2025-11-05"},
#   {"status": "failed", "count": 23, "oldest": "2025-10-20", "newest": "2025-11-04"}
# ]
```

### Manual DLQ Review
```python
# Review failed tasks
failed = await review_dead_letter_queue()

# Retry specific task
await retry_from_dlq(task_id="failed-task-123")
```

## Cleanup Configuration

### Recommended Retention
- **Completed Tasks**: 24 hours (configurable)
- **Failed Tasks (DLQ)**: 30 days (for review)
- **Queued Tasks**: No automatic cleanup
- **Claimed Tasks**: Reclaimed on worker failure

### Storage Estimates
- Average task size: ~1KB
- 1000 tasks/day: ~365MB/year without cleanup
- With 24h cleanup: ~1MB stable size

---

**Created**: Week 2 (2025-11-05)  
**Completed**: Week 2-3 (2025-11-05)  
**Duration**: Part of Week 2-3  
**Success**: ✅ Complete, integrated with maintenance
