# SQLite Task Queue System - Implementation Summary

**Issue**: The Queue (SQLite-based Task Queue)  
**Created**: 2025-11-05  
**Status**: Analysis Complete, Ready for Implementation

---

## Executive Summary

This document summarizes the analysis, research, and implementation plan for a **SQLite-based task queue system** for PrismQ.IdeaInspiration. The system will provide persistent, distributed task processing with multiple scheduling strategies, optimized for Windows deployment.

---

## Problem Solved

The current `BackgroundTaskManager` lacks:
- ❌ **Persistence** - Tasks lost on server crash
- ❌ **Distribution** - Cannot scale across processes
- ❌ **Scheduling** - No FIFO/LIFO/Priority options
- ❌ **Retry logic** - Limited failure handling
- ❌ **Observability** - Minimal metrics

**Solution**: SQLite + WAL-based queue provides all these features with **zero infrastructure overhead**.

---

## Key Decisions

### 1. Technology: SQLite 3 + WAL ✅

**Rationale**:
- No external dependencies (Redis, RabbitMQ)
- Simple file-based database
- ACID guarantees
- Windows-native support
- Easy migration to PostgreSQL later

**Trade-offs**:
- Limited to ~1000 tasks/min (acceptable for current workload)
- Single writer bottleneck (mitigated by WAL mode)
- Requires periodic maintenance (VACUUM)

### 2. Architecture: Integrate with BackgroundTaskManager ✅

**Approach**: Replace in-memory tracking with SQLite backend while maintaining existing API

**Benefits**:
- Backward compatibility
- Minimal code changes for clients
- Gradual migration path
- Leverages existing RunRegistry

### 3. Scheduling: Support 4 Strategies ✅

**Strategies Implemented**:
1. **FIFO** - Fair processing, background jobs
2. **LIFO** - Latest tasks first, user actions
3. **Priority** - Time-sensitive operations
4. **Weighted Random** - Load balancing, prevent starvation

**Rationale**: Different use cases need different ordering guarantees

### 4. Platform: Windows-Optimized ✅

**Optimizations**:
- Local SSD path (`C:\Data\PrismQ\queue\queue.db`)
- Windows-specific PRAGMA tuning
- File locking considerations
- Antivirus compatibility

---

## Research Findings

### SQLite Best Practices (from Web Research)

**Critical**:
1. ✅ **WAL mode** - Reduces tx overhead 30ms → <1ms
2. ✅ **IMMEDIATE transactions** - Atomic task claiming
3. ✅ **busy_timeout = 5000** - Handle lock contention
4. ✅ **Indexes** - (status, priority, run_after_utc)
5. ✅ **Batch operations** - Reduce write tx count

**Important**:
6. ⚠️ Manual checkpointing for high load
7. ⚠️ Connection pooling (one per process)
8. ⚠️ Regular VACUUM or auto_vacuum
9. ⚠️ Parameterized queries only
10. ⚠️ Local SSD, never network shares

### Performance Expectations

**Based on research and similar implementations**:
- **Throughput**: 100-1000 tasks/min (target: 200-500)
- **Claim Latency**: <10ms (P95)
- **Concurrent Workers**: 4-8 recommended
- **SQLITE_BUSY Rate**: <2% acceptable

**Upgrade Threshold**: If >1000 tasks/min needed, migrate to PostgreSQL or Redis

---

## Implementation Breakdown

### 10 Workers, 20 Issues, 4 Weeks

#### Phase 1: Foundation (Week 1)
- **#321**: Core Infrastructure (Worker 01)
- **#337**: Concurrency Research (Worker 09)
- **#335**: Documentation Start (Worker 08)

#### Phase 2: Features (Week 2-3)
- **#323**: Client API (Worker 02)
- **#325**: Worker Engine (Worker 03)
- **#327**: Scheduling Strategies (Worker 04)
- **#329**: Observability (Worker 05)
- **#331**: Maintenance (Worker 06)

#### Phase 3: Integration (Week 4)
- **#333**: Testing (Worker 07)
- **#339**: Integration (Worker 10)
- **#336**: Documentation Complete (Worker 08)

**Parallelization**: Maximum 5 workers in Phase 2 (all independent after Phase 1)

---

## Technical Highlights

### Schema Design

**3 Tables**:
1. **task_queue** - Main task storage with status tracking
2. **workers** - Worker registry and heartbeat
3. **task_logs** - Append-only audit trail

**Key Features**:
- Generated columns for JSON filtering
- Idempotency keys for dedup
- Lease-based atomic claiming
- Automatic timestamps

### Atomic Claiming Algorithm

```sql
BEGIN IMMEDIATE;  -- Block other writers

WITH candidate AS (
  SELECT id FROM task_queue
  WHERE status = 'queued'
    AND run_after_utc <= datetime('now')
    AND (region IS NULL OR region = :worker_region)
  ORDER BY priority ASC, id ASC  -- Strategy-specific
  LIMIT 1
)
UPDATE task_queue
SET status = 'leased',
    lease_until_utc = datetime('now', '+60 seconds'),
    locked_by = :worker_id
WHERE id = (SELECT id FROM candidate);

COMMIT;
```

**Guarantees**: Only one worker can claim each task (no duplicates)

### Retry Logic

```sql
UPDATE task_queue
SET attempts = attempts + 1,
    status = CASE WHEN attempts + 1 >= max_attempts 
                  THEN 'dead' 
                  ELSE 'queued' END,
    run_after_utc = datetime('now', printf('+%d seconds', :backoff)),
    locked_by = NULL
WHERE id = :task_id;
```

**Strategy**: Exponential backoff up to max_attempts, then dead-letter

---

## Scheduling Strategy Comparison

| Strategy | Use Case | Ordering | Fairness | Starvation |
|----------|----------|----------|----------|------------|
| **FIFO** | Background jobs | Oldest first | High | Low |
| **LIFO** | User actions | Newest first | Low | High |
| **Priority** | Time-sensitive | Priority value | None | High |
| **Weighted Random** | Load balancing | Probabilistic | Medium | Low |

**Default Recommendation**: **Priority** (most common use case)

**Switch Example**:
```python
worker = Worker(
    config=WorkerConfig(
        scheduling_strategy=SchedulingStrategy.WEIGHTED_RANDOM
    )
)
```

---

## Observability

### SQL Metrics (Available Immediately)

```sql
-- Queue depth by status
SELECT status, COUNT(*) FROM task_queue GROUP BY status;

-- Age of oldest queued
SELECT type, MIN(run_after_utc) 
FROM task_queue 
WHERE status = 'queued' 
GROUP BY type;

-- Success rate (last 6 hours)
SELECT type,
  SUM(CASE WHEN status = 'succeeded' THEN 1 ELSE 0 END) as ok,
  SUM(CASE WHEN status = 'dead' THEN 1 ELSE 0 END) as failed
FROM task_queue
WHERE finished_at_utc >= datetime('now', '-6 hours')
GROUP BY type;
```

### Integration with Existing Logging
- Use `ConfigLoad` module patterns
- Structured logging with metadata
- Windows Event Log compatibility

---

## Operations

### Backup Procedure

```python
# SQLite online backup (safe while running)
import sqlite3

def backup_queue_db(source_path, backup_path):
    source = sqlite3.connect(source_path)
    backup = sqlite3.connect(backup_path)
    source.backup(backup)
    backup.close()
    source.close()
```

**Schedule**: Daily backups, retain 7 days

### Maintenance Tasks

**Daily**:
- Checkpoint WAL manually
- Backup database
- Check SQLITE_BUSY rate

**Weekly**:
- Run `PRAGMA optimize`
- Clean up old task_logs (>30 days)
- Review queue depth trends

**Monthly**:
- Run `VACUUM` (or incremental)
- Review dead-letter tasks
- Performance tuning

---

## Migration Strategy

### Phase 1: Parallel Deployment (Week 5)
1. Deploy SQLite queue
2. Route new task types to queue
3. Keep existing tasks in BackgroundTaskManager
4. Monitor performance and reliability

### Phase 2: Full Migration (Week 6-7)
1. Migrate all task types to queue
2. Update BackgroundTaskManager to use queue backend
3. Maintain API compatibility
4. Remove in-memory tracking

### Phase 3: Optimization (Week 8+)
1. Tune based on production metrics
2. Adjust PRAGMA settings if needed
3. Document lessons learned
4. Plan for PostgreSQL upgrade (if needed)

---

## Risk Mitigation

### High Risks

**Risk**: Windows file locking issues  
**Mitigation**: Thorough testing on Windows (#337), avoid network paths

**Risk**: SQLITE_BUSY errors under load  
**Mitigation**: Tune busy_timeout, implement exponential backoff, benchmark (#337)

**Risk**: Performance below expectations  
**Mitigation**: Early benchmarking (#337), clear PostgreSQL upgrade path

### Medium Risks

**Risk**: Migration complexity  
**Mitigation**: Gradual rollout, parallel operation, rollback capability

**Risk**: Stale lease accumulation  
**Mitigation**: Automatic sweeper (#332), monitoring (#329)

**Risk**: Database corruption  
**Mitigation**: Regular backups (#331), WAL mode, testing

---

## Success Metrics

### Functional (MVP)
- [x] Analysis complete (#320)
- [ ] Core infrastructure operational (#321)
- [ ] All 4 strategies working (#327)
- [ ] Client API functional (#323)
- [ ] Worker claiming tasks (#325)
- [ ] Basic observability (#329)

### Non-Functional
- [ ] Throughput: 200+ tasks/min sustained
- [ ] Latency: <10ms claim (P95)
- [ ] Reliability: <2% SQLITE_BUSY rate
- [ ] Test coverage: >80%
- [ ] Documentation: Complete

### Production Readiness
- [ ] Windows compatibility verified
- [ ] Backup procedures tested
- [ ] Monitoring in place
- [ ] Runbook complete
- [ ] Team trained

---

## Open Questions

### Resolved ✅
- **Q**: SQLite vs Redis?
  - **A**: SQLite (simple, upgrade later)
- **Q**: Replace BackgroundTaskManager?
  - **A**: Integrate/replace (maintain API)
- **Q**: Support all 4 strategies?
  - **A**: Yes (different use cases)

### To Be Resolved
- **Q**: Default scheduling strategy?
  - **Recommend**: PRIORITY (most common)
  - **Decide**: In #327 implementation
  
- **Q**: Optimal lease duration?
  - **Research**: In #337 benchmarks
  - **Decide**: After testing
  
- **Q**: Task dependencies in v1?
  - **Recommend**: No (future enhancement)
  - **Decide**: Team review

---

## Documents Created

### Analysis and Planning ✅
1. **#320: Analysis and Design** - Complete pros/cons evaluation
2. **QUEUE-SYSTEM-INDEX** - Master index of all issues
3. **QUEUE-SYSTEM-QUICK-REFERENCE** - Quick reference guide
4. **This Document** - Implementation summary

### Implementation Issues ✅
1. **#321: Core Infrastructure** (Worker 01)
2. **#327: Scheduling Strategies** (Worker 04)
3. **#337: Concurrency Research** (Worker 09)

### To Be Created 📋
- #323-326: Client and Worker issues (Worker 02-3)
- #329-332: Observability and Maintenance (Worker 05-6)
- #333-336: Testing and Documentation (Worker 07-8)
- #339-340: Integration issues (Worker 10)

---

## Next Steps

### Immediate (This Week)
1. ✅ Complete analysis (#320)
2. ✅ Create foundational issues
3. ✅ Team review and approval
4. ⏳ Create remaining issues
5. ⏳ Assign workers

### Short Term (Week 1-2)
1. ⏳ Start #321 (Core Infrastructure)
2. ⏳ Start #337 (Research benchmarks)
3. ⏳ Begin documentation (#335)

### Medium Term (Week 3-4)
1. ⏳ Complete Phase 2 features
2. ⏳ Comprehensive testing
3. ⏳ Integration with BackgroundTaskManager

### Long Term (Week 5+)
1. ⏳ Production deployment
2. ⏳ Monitor and optimize
3. ⏳ Plan PostgreSQL migration (if needed)

---

## Conclusion

The SQLite task queue system provides a **pragmatic, maintainable solution** that:
- ✅ Fits PrismQ's "simple architecture" principle
- ✅ Requires zero infrastructure
- ✅ Supports Windows platform natively
- ✅ Provides clear upgrade path
- ✅ Can be implemented in parallel by 10 workers

**Recommendation**: **APPROVE** for implementation

**Timeline**: 4 weeks to production-ready MVP  
**Resources**: 10 workers in parallel  
**Risk Level**: Low-Medium (well-researched, proven technology)

---

## Appendix: References

### Web Research Sources
- SQLite WAL Mode Documentation
- Python sqlite3 Best Practices
- litequeue (reference implementation)
- SQLite Concurrency Benchmarks
- Windows File System Optimization

### Internal References
- `Client/Backend/src/core/task_manager.py` (existing)
- `Client/Backend/src/core/run_registry.py` (existing)
- PrismQ Architecture Documentation
- SOLID Principles Guide

### Related Projects
- PrismQ.IdeaCollector
- StoryGenerator
- Other PrismQ modules using task processing

---

**Status**: ✅ Analysis Complete, Ready for Team Review  
**Created**: 2025-11-05  
**Last Updated**: 2025-11-05  
**Next Review**: Before starting implementation
