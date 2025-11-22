# Issue #320: SQLite Task Queue System - Analysis and Design

**Status**: New  
**Priority**: High  
**Category**: Infrastructure/DevOps  
**Estimated Time**: 2-3 days (Research & Design)  
**Created**: 2025-11-05

---

## Overview

This issue analyzes the proposed SQLite-based task queue system for PrismQ.T.Idea.Inspiration, evaluates its pros and cons, identifies research topics, and creates a comprehensive implementation plan with worker allocation for parallel development.

---

## Problem Statement

The current `BackgroundTaskManager` in `Client/Backend` provides fire-and-forget task execution but lacks:
- **Persistence**: Tasks are lost if the server crashes
- **Distributed work**: Cannot scale across multiple worker processes
- **Priority management**: No support for FIFO/LIFO/Priority/Weighted scheduling
- **Retry logic**: Limited failure handling and exponential backoff
- **Observability**: Minimal metrics and monitoring
- **Atomic claiming**: No protection against duplicate task execution

A SQLite-based queue provides a middle ground between in-memory queues (current) and full message brokers (RabbitMQ, Redis).

---

## Proposed Solution Analysis

### Original Proposal Summary

The issue proposes a **SQLite 3 + WAL** based task queue with:
- **Client/UI/Backend**: Only enqueue tasks and poll status
- **Workers**: Filter by capability, atomically claim (lease), process, and finalize
- **DB Features**: WAL mode, safe leases, retries, dead-letter handling, observability

### Pros ✅

1. **Zero Infrastructure**
   - No external services (Redis, RabbitMQ) required
   - Single file database (`C:\Data\queue\queue.db`)
   - Works on Windows without dependencies
   - Simple backup (SQLite online backup API)

2. **ACID Guarantees**
   - Atomic task claiming via `BEGIN IMMEDIATE`
   - Transactions ensure consistency
   - WAL mode prevents reader blocking

3. **Windows-Friendly**
   - Native Windows support
   - Runs on local SSD (no network shares needed)
   - Well-documented PRAGMA settings for Windows

4. **Observability**
   - SQL-queryable metrics
   - Task logs table for debugging
   - Worker registry for monitoring
   - Simple to inspect with any SQLite tool

5. **Maintainability**
   - Schema is simple and portable
   - Easy to migrate to PostgreSQL later
   - Standard SQL queries
   - Well-understood technology

6. **Feature-Rich**
   - Priority queues
   - Retry with exponential backoff
   - Dead-letter handling (max_attempts)
   - Idempotency keys
   - Lease renewal for long jobs
   - Capability-based worker filtering
   - JSON support via JSON1 extension

### Cons ❌

1. **Single Writer Bottleneck**
   - Only one write transaction at a time
   - Can cause `SQLITE_BUSY` errors under high concurrency
   - Limited to ~1000 tasks/minute write throughput (per research)

2. **Windows File Locking**
   - Windows file locking behaves differently than POSIX
   - Potential contention issues with multiple processes
   - Requires thorough testing on target platform

3. **Checkpointing Overhead**
   - WAL checkpoint can block writers
   - Needs tuning (`wal_autocheckpoint`)
   - "Checkpoint starvation" if not managed

4. **No Native Lock/Skip**
   - SQLite lacks `SELECT FOR UPDATE SKIP LOCKED`
   - Requires custom lease-based claiming
   - More complex than PostgreSQL queues

5. **Scalability Ceiling**
   - Not suitable for very high throughput (10k+ tasks/min)
   - Limited to single host (no true distributed queue)
   - Eventually needs upgrade to Redis/RabbitMQ

6. **Database Fragmentation**
   - Frequent deletes can fragment file
   - Requires periodic `VACUUM` (blocking operation)
   - Or use `auto_vacuum = INCREMENTAL`

### Verdict

**RECOMMENDED** for PrismQ.T.Idea.Inspiration because:
- ✅ Fits "simple architecture" principle (agent instructions)
- ✅ Good match for single Windows host with moderate throughput
- ✅ Zero infrastructure overhead
- ✅ Easy to understand and maintain
- ✅ Provides clear upgrade path to PostgreSQL/Redis later

**Limitations Acceptable** because:
- Current workload: Source module runs, scoring, classification (dozens to hundreds/min)
- Platform: Single Windows host with RTX 5090
- Team: Small team prefers simplicity over complex infrastructure

---

## Best Practices Research Summary

### From Online Research

**Key Findings:**

1. **WAL Mode is Essential**
   - Reduces transaction overhead from 30ms to <1ms
   - Enables concurrent readers while writing
   - Required for any production queue

2. **Atomic Claiming is Critical**
   - Use `isolation_level='IMMEDIATE'` in Python
   - Prevents race conditions between workers
   - Essential for avoiding duplicate processing

3. **Busy Timeout Must Be Tuned**
   - Set `PRAGMA busy_timeout = 5000` (5 seconds)
   - Allows retries on lock contention
   - Reduces `SQLITE_BUSY` errors

4. **Batch Operations Improve Throughput**
   - Batch inserts/updates when possible
   - Reduces transaction count
   - Mitigates single-writer bottleneck

5. **Manual Checkpointing Recommended**
   - Use `PRAGMA wal_checkpoint(TRUNCATE)` strategically
   - Prevents unbounded WAL growth
   - Reduces I/O during high load

6. **Connection Pooling is Important**
   - One connection per process recommended
   - Avoid open/close overhead
   - Limit total connections to avoid file locks

7. **Indexing is Non-Negotiable**
   - Index on (status, priority, run_after_utc)
   - Index on type for filtering
   - Generated columns for JSON filtering

**Source Libraries for Reference:**
- [litequeue](https://github.com/litements/litequeue) - Persistent SQLite queue for Python
- Simple examples on [blog.tomhuibregtse.com](https://blog.tomhuibregtse.com/a-dead-simple-work-queue-using-sqlite)

---

## Architecture Decisions

### Integration with Current System

**Option A: Replace BackgroundTaskManager** (Recommended)
- Migrate current in-memory task tracking to SQLite queue
- Provides persistence and retry capabilities
- Maintains existing API with `RunRegistry`

**Option B: Parallel Implementation**
- Keep `BackgroundTaskManager` for simple tasks
- Use SQLite queue for long-running/critical tasks
- More complexity but gradual migration

**Decision: Option A** - Replace for consistency and simplicity

### Queue Scheduling Strategies

Must support 4 strategies (per issue requirements):

1. **FIFO (First-In-First-Out)**
   - `ORDER BY id ASC`
   - Default for fair processing
   - Use case: Background jobs, imports

2. **LIFO (Last-In-First-Out)**
   - `ORDER BY id DESC`
   - Latest tasks first
   - Use case: User-triggered operations (cancel older)

3. **Priority Queue**
   - `ORDER BY priority ASC, id ASC`
   - Lower number = higher priority
   - Use case: Time-sensitive operations

4. **Weighted Random**
   - Probabilistic selection based on priority weight
   - Prevents starvation of low-priority tasks
   - Use case: Load balancing across priorities
   - Implementation: `ORDER BY RANDOM() * (1.0 / (priority + 1)) DESC`

**Implementation**: Add `scheduling_strategy` field to worker configuration

---

## Component Breakdown

### 1. Core Queue Infrastructure
- SQLite database setup with PRAGMAs
- Schema implementation (task_queue, workers, task_logs)
- Connection management and pooling
- Transaction handling

### 2. Client API
- Enqueue task with parameters
- Query task status
- Cancel task
- Idempotency handling

### 3. Worker Engine
- Task claiming with atomic leases
- Capability-based filtering
- Lease renewal for long jobs
- Retry logic with exponential backoff
- Dead-letter handling

### 4. Scheduling Strategies
- FIFO implementation
- LIFO implementation
- Priority queue implementation
- Weighted random implementation
- Strategy switching mechanism

### 5. Observability
- Task logs appending
- Worker heartbeat tracking
- Queue depth metrics
- Success/failure rates
- Age of oldest queued task

### 6. Maintenance & Operations
- Database backup procedures
- WAL checkpoint management
- Stale lease cleanup (sweeper)
- Database optimization (ANALYZE, VACUUM)

### 7. Testing & Benchmarking
- Unit tests for each component
- Integration tests for worker scenarios
- Concurrency tests (multiple workers)
- Performance benchmarks
- Windows-specific testing

---

## Research Topics Identified

### High Priority

1. **R1: SQLite Concurrency Tuning**
   - Benchmark different PRAGMA settings
   - Test multiple workers on Windows
   - Measure SQLITE_BUSY frequency
   - Optimize busy_timeout

2. **R2: Scheduling Strategy Performance**
   - Compare execution order guarantees
   - Measure weighted random fairness
   - Test priority inversion scenarios
   - Benchmark switching overhead

3. **R3: Lease Management**
   - Determine optimal lease duration
   - Test lease renewal patterns
   - Measure stale lease detection latency
   - Handle worker crash scenarios

### Medium Priority

4. **R4: Integration with BackgroundTaskManager**
   - Define migration path
   - API compatibility layer
   - RunRegistry integration
   - Backward compatibility

5. **R5: Windows File System Behavior**
   - Test file locking on NTFS
   - Measure checkpoint performance
   - Validate backup procedures
   - SSD vs HDD performance

6. **R6: Observability Patterns**
   - Design metrics schema
   - Query performance for dashboards
   - Log retention policies
   - Integration with existing logging

### Lower Priority

7. **R7: Migration to PostgreSQL**
   - Document upgrade path
   - Schema compatibility
   - Query translation
   - Data migration tools

8. **R8: Sharding by Task Type**
   - Multiple DB files per type
   - Worker affinity patterns
   - Cross-shard monitoring
   - Backup complexity

---

## Worker Allocation for Parallel Development

### Worker 01: Core Queue Infrastructure (Backend Engineer)
**Issues**: 
- #321: Implement SQLite Queue Core Infrastructure
- #322: Database Schema and Connection Management

**Duration**: 1-2 weeks  
**Skills**: Python, SQLite, Database design  
**Deliverables**:
- SQLite database setup with Windows-optimized PRAGMAs
- Schema implementation (task_queue, workers, task_logs)
- Connection pool management
- Transaction handling utilities
- Basic enqueue/dequeue operations

### Worker 02: Client API (Full Stack Engineer)
**Issues**:
- #323: Implement Queue Client API ✅ **COMPLETE**
- #324: Task Status and Polling Endpoints ✅ **COMPLETE**

**Duration**: 1 week  
**Skills**: Python, FastAPI, API design  
**Status**: ✅ **COMPLETE**  
**Deliverables**:
- [x] Enqueue task API with validation
- [x] Task status polling
- [x] Task cancellation
- [x] Idempotency key handling
- [x] REST endpoint integration with Backend

### Worker 03: Worker Engine (Backend Engineer)
**Issues**:
- #325: Implement Worker Task Claiming Engine
- #326: Retry Logic and Dead-Letter Handling

**Duration**: 1-2 weeks  
**Skills**: Python, Concurrency, Error handling  
**Deliverables**:
- Atomic lease-based task claiming
- Capability-based filtering
- Worker loop implementation
- Lease renewal mechanism
- Exponential backoff retry
- Dead-letter task handling

### Worker 04: Scheduling Strategies (Algorithm Engineer)
**Issues**:
- #327: Implement Queue Scheduling Strategies
- #328: Worker Strategy Configuration

**Duration**: 1 week  
**Skills**: Algorithms, SQL optimization  
**Deliverables**:
- FIFO scheduling
- LIFO scheduling
- Priority queue scheduling
- Weighted random scheduling
- Strategy switching mechanism
- Benchmarking suite

### Worker 05: Observability (DevOps/Monitoring Engineer)
**Issues**:
- #329: Implement Queue Observability
- #330: Worker Heartbeat and Monitoring

**Duration**: 3-5 days  
**Skills**: SQL, Metrics, Logging  
**Deliverables**:
- Task logs implementation
- Worker registry and heartbeat
- Queue metrics queries
- Dashboard-ready SQL views
- Integration with existing logging system

### Worker 06: Maintenance & Operations (DevOps Engineer)
**Issues**:
- #331: Database Maintenance and Backup
- #332: Stale Lease Cleanup and Optimization

**Duration**: 3-5 days  
**Skills**: SQLite, Backup strategies, Windows ops  
**Deliverables**:
- SQLite online backup implementation
- WAL checkpoint management
- Stale lease sweeper
- VACUUM/ANALYZE scheduling
- Operational runbook

### Worker 07: Testing & Benchmarking (QA Engineer)
**Issues**:
- #333: Comprehensive Queue Testing
- #334: Performance Benchmarking Suite

**Duration**: 1 week  
**Skills**: pytest, Performance testing, Windows testing  
**Deliverables**:
- Unit tests for all components
- Integration tests with multiple workers
- Concurrency test scenarios
- Performance benchmarks
- Windows-specific test coverage

### Worker 08: Documentation (Technical Writer)
**Issues**:
- #335: Queue System Architecture Documentation
- #336: Operational Guide and Runbook

**Duration**: 3-5 days  
**Skills**: Technical writing, Architecture diagrams  
**Deliverables**:
- Architecture documentation
- API reference
- Worker configuration guide
- Operational runbook
- Migration guide from BackgroundTaskManager

### Worker 09: Research Tasks (Research Engineer)
**Issues**:
- #337: Research SQLite Concurrency Tuning
- #338: Research Scheduling Strategy Performance

**Duration**: 1 week  
**Skills**: Benchmarking, Analysis, Research  
**Deliverables**:
- Concurrency tuning report
- Scheduling strategy comparison
- Windows-specific findings
- Recommendations for production settings

### Worker 10: Integration (Senior Engineer)
**Issues**:
- #339: Integrate Queue with BackgroundTaskManager
- #340: Migration Strategy and Backward Compatibility

**Duration**: 1 week  
**Skills**: Python, Architecture, Integration  
**Deliverables**:
- BackgroundTaskManager integration layer
- Migration scripts
- Backward compatibility wrappers
- Integration tests
- Rollback procedures

---

## Parallelization Strategy

### Phase 1: Foundation (Week 1)
**Can work in parallel**:
- Worker 01: Core Infrastructure (#321, #322)
- Worker 09: Research (#337, #338)
- Worker 08: Documentation (start) (#335)

### Phase 2: Implementation (Week 2-3)
**Can work in parallel** (dependencies on Phase 1):
- Worker 02: Client API (#323, #324) - ✅ **COMPLETE**
- Worker 03: Worker Engine (#325, #326) - depends on Worker 1
- Worker 04: Scheduling (#327, #328) - depends on Worker 1
- Worker 05: Observability (#329, #330) - depends on Worker 1
- Worker 06: Maintenance (#331, #332) - depends on Worker 1

### Phase 3: Testing & Integration (Week 4)
**Can work in parallel**:
- Worker 07: Testing (#333, #334) - depends on Phase 2
- Worker 10: Integration (#339, #340) - depends on Phase 2
- Worker 08: Documentation (complete) (#336) - depends on Phase 2

**Total Timeline**: 4 weeks with 10 parallel workers  
**Sequential Timeline**: 10-12 weeks

**Time Savings**: 60-70% reduction

---

## Suggested Changes and Improvements

### Changes to Original Proposal

1. **Add Scheduling Strategy Field**
   - Original: Only priority-based
   - Enhancement: Support FIFO/LIFO/Priority/Weighted Random
   - Implementation: Add `scheduling_strategy` column to workers table

2. **Integration with Existing System**
   - Original: Standalone queue
   - Enhancement: Integrate with `BackgroundTaskManager` and `RunRegistry`
   - Benefit: Maintains existing UI/API contracts

3. **Python-Specific Implementation**
   - Original: .NET/C# examples
   - Change: Use Python with `sqlite3` or `aiosqlite` for async
   - Reason: PrismQ ecosystem is Python-based

4. **Worker Capability Schema**
   - Original: JSON blob
   - Enhancement: Define capability Protocol (SOLID Interface Segregation)
   - Example: `{"regions": ["us", "eu"], "formats": ["video", "audio"], "max_memory_gb": 16}`

5. **Task Type Enum**
   - Original: Freeform text
   - Enhancement: Python Enum for type safety
   - Example: `TaskType.SOURCE_INGEST`, `TaskType.CLASSIFICATION`, `TaskType.SCORING`

6. **Monitoring Integration**
   - Original: SQL-only queries
   - Enhancement: Export metrics to existing logging system
   - Integration: Use `ConfigLoad` module logging patterns

### Additional Features

1. **Task Dependencies**
   - Future enhancement: `depends_on` task IDs
   - Use case: Multi-stage pipelines
   - Implementation: Check dependencies before claiming

2. **Batch Task Support**
   - Future enhancement: Single task with multiple items
   - Use case: Bulk imports
   - Implementation: JSON array in payload

3. **Task Cancellation Callback**
   - Future enhancement: Notify task of cancellation
   - Use case: Cleanup external resources
   - Implementation: Cancellation token in worker

4. **Dead-Letter Analysis**
   - Future enhancement: Pattern detection in failed tasks
   - Use case: Identify systemic issues
   - Implementation: Aggregate error_message patterns

---

## Acceptance Criteria

### Functional Requirements
- [ ] Tasks can be enqueued with priority, payload, and capabilities
- [ ] Workers can claim tasks atomically (no duplicate execution)
- [ ] Supports FIFO, LIFO, Priority, and Weighted Random scheduling
- [ ] Retry with exponential backoff up to max_attempts
- [ ] Dead-letter handling for failed tasks
- [ ] Task cancellation while queued or processing
- [ ] Idempotency keys prevent duplicate enqueues
- [ ] Lease renewal for long-running tasks
- [ ] Stale lease recovery (sweeper)

### Non-Functional Requirements
- [ ] Handles 100-1000 tasks/minute on Windows
- [ ] Multiple workers can run concurrently
- [ ] Database survives server restart (persistence)
- [ ] SQLite_BUSY errors handled gracefully
- [ ] Queue metrics available via SQL queries
- [ ] Backup procedures documented and tested
- [ ] Compatible with existing BackgroundTaskManager API

### Testing Requirements
- [ ] Unit tests for all components (>80% coverage)
- [ ] Integration tests with multiple workers
- [ ] Concurrency tests on Windows
- [ ] Performance benchmarks documented
- [ ] Failure scenario testing (crashes, timeouts)

---

## Implementation Timeline

### Week 1: Foundation
- Set up SQLite database and schema
- Implement connection management
- Research concurrency tuning
- Start documentation

### Week 2-3: Core Features
- Client API implementation
- Worker engine with claiming
- Scheduling strategies
- Observability setup
- Maintenance procedures

### Week 4: Integration & Testing
- Comprehensive testing
- Integration with BackgroundTaskManager
- Performance benchmarking
- Documentation completion

---

## Migration Strategy

### Phase 1: Parallel Operation
1. Deploy SQLite queue alongside BackgroundTaskManager
2. Route new task types to SQLite queue
3. Keep existing tasks in BackgroundTaskManager
4. Monitor performance and reliability

### Phase 2: Full Migration
1. Migrate all task types to SQLite queue
2. Update BackgroundTaskManager to use queue backend
3. Maintain API compatibility
4. Deprecate in-memory task tracking

### Phase 3: Optimization
1. Tune based on production metrics
2. Optimize based on actual workload patterns
3. Document lessons learned

---

## Related Documentation

- Original proposal: Issue description (SQLite + WAL queue)
- Existing: `Client/Backend/src/core/task_manager.py`
- Existing: `Client/Backend/src/core/run_registry.py`
- Research: [litequeue](https://github.com/litements/litequeue)
- Best practices: Web search results (SQLite WAL optimization)

---

## Next Steps

1. **Review this analysis** with team
2. **Approve or modify** architecture decisions
3. **Create worker issues** (#321-#340)
4. **Assign workers** based on skills
5. **Start Phase 1** (Foundation)

---

## Questions for Review

1. Should we replace or augment BackgroundTaskManager?
2. Which scheduling strategy should be default?
3. What is acceptable task throughput target?
4. Should we support task dependencies in v1?
5. Optimal lease duration for typical tasks?

---

**Status**: Ready for Review  
**Assigned**: Infrastructure/DevOps Team  
**Labels**: `infrastructure`, `queue`, `sqlite`, `architecture`, `research`
