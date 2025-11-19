# SQLite Task Queue System - Quick Reference

**Created**: 2025-11-05  
**Status**: Ready for Implementation

---

## What Is This?

Analysis and implementation plan for a **SQLite-based task queue system** for PrismQ.IdeaInspiration, providing:
- ✅ Persistent task storage (survives restarts)
- ✅ Distributed worker support (multiple processes)
- ✅ 4 scheduling strategies (FIFO, LIFO, Priority, Weighted Random)
- ✅ Retry with exponential backoff
- ✅ Windows-optimized configuration
- ✅ Zero infrastructure dependencies

---

## Key Documents

1. **[#320: Analysis and Design](./320-sqlite-queue-analysis-and-design.md)** - Complete analysis with pros/cons
2. **[Queue System Index](./QUEUE-SYSTEM-INDEX.md)** - All issues and timeline
3. **[#321: Core Infrastructure](../Worker01/321-implement-sqlite-queue-core-infrastructure.md)** - Foundation implementation
4. **[#327: Scheduling Strategies](../Worker04/327-implement-queue-scheduling-strategies.md)** - FIFO/LIFO/Priority/Weighted Random

---

## Quick Facts

### Why SQLite?
- ✅ **No infrastructure**: No Redis, RabbitMQ, or external services
- ✅ **Simple**: Single file database on local SSD
- ✅ **Portable**: Easy to backup, migrate to PostgreSQL later
- ✅ **Observable**: SQL-queryable metrics
- ✅ **Windows-friendly**: Native support, well-documented

### Limitations
- ⚠️ Single writer (max ~1000 tasks/min)
- ⚠️ Single host (not truly distributed)
- ⚠️ Requires periodic maintenance (VACUUM)

### Verdict
✅ **RECOMMENDED** for PrismQ because:
- Fits "simple architecture" principle
- Good match for moderate throughput workload
- Single Windows host deployment
- Clear upgrade path later

---

## Implementation Plan

### 10 Workers, 20 Issues, 4 Weeks

#### Week 1: Foundation
- Worker 01: Core Infrastructure
- Worker 09: Research concurrency tuning
- Worker 08: Start documentation

#### Week 2-3: Features
- Worker 02: Client API (enqueue, poll, cancel)
- Worker 03: Worker engine (claiming, retry)
- Worker 04: **Scheduling strategies** (FIFO/LIFO/Priority/Weighted)
- Worker 05: Observability (logs, metrics)
- Worker 06: Maintenance (backup, cleanup)

#### Week 4: Polish
- Worker 07: Testing and benchmarks
- Worker 10: Integration with BackgroundTaskManager
- Worker 08: Complete documentation

**Time Savings**: 60-70% vs sequential (4 weeks vs 10-12 weeks)

---

## Scheduling Strategies

### FIFO (First-In-First-Out)
**Use Case**: Fair processing, background jobs  
**Ordering**: Oldest task first  
**Fairness**: High  
**Starvation**: Low

### LIFO (Last-In-First-Out)
**Use Case**: User actions, latest requests  
**Ordering**: Newest task first  
**Fairness**: Low  
**Starvation**: High (for old tasks)

### Priority Queue
**Use Case**: Time-sensitive operations  
**Ordering**: Lower priority number = higher priority  
**Fairness**: None  
**Starvation**: High (for low priority)

### Weighted Random
**Use Case**: Load balancing, prevent starvation  
**Ordering**: Probabilistic based on priority  
**Fairness**: Medium  
**Starvation**: Low (all tasks have some chance)

---

## Research Topics

### Completed ✅
- [x] Analyze proposal pros/cons
- [x] Research SQLite best practices online
- [x] Research WAL mode performance and bottlenecks
- [x] Identify worker allocation strategy
- [x] Create implementation issues

### Ongoing 📋
- [ ] #337: SQLite concurrency tuning (Worker 09)
- [ ] #338: Scheduling strategy performance (Worker 09)
- [ ] Windows file system behavior testing
- [ ] Lease management optimization
- [ ] Integration patterns with BackgroundTaskManager

---

## Best Practices (from Research)

### Critical ✅
1. **Use WAL mode** - Reduces transaction overhead 30ms → <1ms
2. **Set busy_timeout = 5000** - Handle SQLITE_BUSY gracefully
3. **Use IMMEDIATE transactions** - Atomic task claiming
4. **Batch operations** - Reduce write transaction count
5. **Index properly** - (status, priority, run_after_utc)
6. **Connection pooling** - One connection per process

### Important ⚠️
7. Manual checkpointing for high load
8. Regular VACUUM or incremental auto_vacuum
9. Parameterized queries (prevent SQL injection)
10. Local SSD only (not network shares)

---

## Configuration

### Database Location
```
Windows: C:\Data\PrismQ\queue\queue.db
```

### PRAGMAs (Windows-Optimized)
```sql
PRAGMA journal_mode = WAL;           -- Enable concurrency
PRAGMA synchronous = NORMAL;         -- Balance durability
PRAGMA busy_timeout = 5000;          -- 5s lock retry
PRAGMA wal_autocheckpoint = 1000;    -- Checkpoint every 1000 pages
PRAGMA cache_size = -20000;          -- 20MB cache
```

### Worker Configuration
```python
worker_config = WorkerConfig(
    worker_id="worker-1",
    capabilities={"region": "us"},
    scheduling_strategy=SchedulingStrategy.PRIORITY,
    lease_duration_seconds=60
)
```

---

## Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Throughput | 100-1000 tasks/min | Current workload estimate |
| Claim Latency | <10ms | Fast worker response |
| Enqueue Latency | <5ms | Fast client response |
| SQLITE_BUSY Rate | <1% | Acceptable lock contention |
| Test Coverage | >80% | Quality standard |

---

## Architecture Decisions

### ✅ Integrate with BackgroundTaskManager
- Replace in-memory tracking with SQLite
- Maintain existing API
- Provides persistence + retry

### ✅ Python Implementation
- Use `sqlite3` standard library
- Compatible with Python 3.10.x
- Optional `aiosqlite` for async

### ✅ Support All 4 Strategies
- Workers configure strategy
- Factory pattern for flexibility
- Benchmark and compare

### ✅ Gradual Migration
- Parallel operation initially
- Full migration after validation
- Rollback capability

---

## Success Metrics

### Functional ✅
- [x] Analysis complete
- [ ] All issues created (20 total)
- [ ] Core infrastructure operational
- [ ] All 4 strategies implemented
- [ ] Integration complete

### Non-Functional 📊
- [ ] >80% test coverage
- [ ] Performance targets met
- [ ] Windows compatibility verified
- [ ] Documentation complete

---

## Next Steps

1. ✅ Complete analysis (#320)
2. ✅ Create foundational issues (#321, #327)
3. ⏳ Create remaining issues (#322-#340)
4. ⏳ Assign to workers
5. ⏳ Start Week 1 implementation

---

## Questions & Decisions

### Resolved ✅
- **Q**: SQLite vs Redis/RabbitMQ?
  - **A**: SQLite for simplicity, upgrade path later
- **Q**: Replace or augment BackgroundTaskManager?
  - **A**: Integrate/replace for consistency
- **Q**: Which strategies to support?
  - **A**: All 4 (FIFO, LIFO, Priority, Weighted Random)

### Open ❓
- Default scheduling strategy? (Recommend: PRIORITY)
- Task dependency support in v1? (Recommend: No, future)
- Optimal lease duration? (Research in #337)

---

## Related Files

```
_meta/issues/new/Infrastructure_DevOps/
├── 320-sqlite-queue-analysis-and-design.md     # Main analysis
├── QUEUE-SYSTEM-INDEX.md                       # All issues
└── QUEUE-SYSTEM-QUICK-REFERENCE.md            # This file

_meta/issues/new/Worker01/
└── 321-implement-sqlite-queue-core-infrastructure.md

_meta/issues/new/Worker04/
└── 327-implement-queue-scheduling-strategies.md
```

---

## Resources

- [SQLite WAL Mode](https://sqlite.org/wal.html)
- [litequeue (Python)](https://github.com/litements/litequeue)
- [Python sqlite3 docs](https://docs.python.org/3/library/sqlite3.html)
- Web research results (in #320)

---

**Status**: ✅ Ready for Implementation  
**Last Updated**: 2025-11-05  
**Next Review**: After issue creation
