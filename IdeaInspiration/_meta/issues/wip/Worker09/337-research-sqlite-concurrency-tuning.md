# Issue #337: Research SQLite Concurrency Tuning and Windows Performance

**Parent Issue**: #320 (SQLite Queue Analysis)  
**Worker**: Worker 09 - Research Engineer  
<<<<<<< HEAD:_meta/issues/new/Worker09/337-research-sqlite-concurrency-tuning.md
**Status**: 🆕 Ready to Start  
**Priority**: High  
**Duration**: 1 week  
**Dependencies**: ✅ #321 (Core Infrastructure - COMPLETED)
=======
**Status**: ✅ Complete  
**Priority**: High  
**Duration**: 1 week  
**Dependencies**: ✅ #321 (Core Infrastructure - COMPLETED)

---

## ✅ Research Complete

**Previous Blocker**: #321 - Implement SQLite Queue Core Infrastructure ✅ **COMPLETED**  
**Research Status**: All benchmarking and analysis complete  
**Deliverables**: All deliverables created and ready for production use

**Completed Work**:
1. ✅ Benchmark script created (`_meta/research/sqlite_queue_benchmark.py`)
2. ✅ Comprehensive benchmark report (`_meta/research/SQLITE_QUEUE_BENCHMARK_REPORT.md`)
3. ✅ Production configuration (`Client/Backend/src/queue/config.py`)
4. ✅ Troubleshooting guide (`_meta/docs/SQLITE_QUEUE_TROUBLESHOOTING.md`)
5. ✅ All testing scenarios completed
6. ✅ PRAGMA recommendations finalized
>>>>>>> main:_meta/issues/wip/Worker09/337-research-sqlite-concurrency-tuning.md

---

## Objective

Conduct comprehensive research and benchmarking of SQLite concurrency settings and Windows-specific performance characteristics to determine optimal production configuration for the PrismQ task queue.

---

## Background

From #320 analysis and web research:
- WAL mode reduces transaction overhead from 30ms to <1ms
- Single writer limitation can cause SQLITE_BUSY errors
- Windows file locking behaves differently than POSIX
- Checkpoint frequency impacts performance
- Multiple PRAGMA settings need tuning

**Goal**: Determine production-ready configuration through empirical testing on target platform (Windows + RTX 5090).

---

## Research Questions

### 1. PRAGMA Optimization

**Questions**:
- What is the optimal `busy_timeout` for our workload?
- How does `synchronous` (NORMAL vs FULL) impact durability vs performance?
- What `wal_autocheckpoint` value minimizes blocking?
- What `cache_size` provides best throughput?
- Does `mmap_size` improve performance on Windows?

**Method**: Benchmark with different values, measure throughput and latency

### 2. Concurrency Limits

**Questions**:
- How many concurrent workers can we support?
- At what point do we hit SQLITE_BUSY errors?
- What is the actual write throughput (tasks/min)?
- How does read concurrency impact write performance?

**Method**: Stress test with 1, 2, 4, 8, 16 workers

### 3. Windows File System Behavior

**Questions**:
- How does NTFS file locking impact performance?
- Is there a difference between SSD and HDD?
- How does antivirus scanning affect performance?
- What about Windows Defender real-time protection?

**Method**: Test on different storage types, with/without AV

### 4. Checkpoint Performance

**Questions**:
- What is the cost of automatic checkpoints?
- Should we use manual checkpointing?
- How often should checkpoints run?
- Does `PRAGMA wal_checkpoint(TRUNCATE)` block operations?

**Method**: Monitor checkpoint frequency and duration

### 5. Lock Contention

**Questions**:
- What causes most SQLITE_BUSY errors?
- How effective is exponential backoff?
- What retry strategy works best?
- Can we predict and avoid contention?

**Method**: Analyze error rates under different workloads

---

## Benchmarking Plan

### Test Environment

**Hardware**:
- OS: Windows 10/11
- GPU: NVIDIA RTX 5090 (32GB VRAM)
- CPU: AMD Ryzen processor
- RAM: 64GB DDR5
- Storage: NVMe SSD (C: drive)

**Software**:
- Python 3.10.x
- SQLite 3.x (latest)
- Database: `C:\Data\PrismQ\queue\test_queue.db`

### Test Scenarios

#### Scenario 1: Baseline (Single Writer)
```python
# Measure baseline performance
- 1 writer, 0 readers
- Insert 10,000 tasks
- Measure: throughput, latency, file size
```

#### Scenario 2: Multiple Writers
```python
# Test write concurrency
- 2, 4, 8, 16 concurrent writers
- Each writes 1,000 tasks
- Measure: throughput, SQLITE_BUSY rate, contention
```

#### Scenario 3: Mixed Workload
```python
# Simulate real usage
- 4 writers (enqueue)
- 4 readers (poll status)
- 4 claimers (atomic claim with UPDATE)
- Measure: overall throughput, latency percentiles
```

#### Scenario 4: Stress Test
```python
# Find breaking point
- Increase workers until SQLITE_BUSY > 5%
- Measure: max sustainable throughput
- Identify: bottleneck (CPU, I/O, locks)
```

#### Scenario 5: Long-Running
```python
# Endurance test
- Run for 24 hours
- Monitor: WAL file size, checkpoint frequency
- Check: database fragmentation, corruption
```

### PRAGMA Variations

Test each scenario with these configurations:

**Config A: Conservative (Max Durability)**
```python
PRAGMA synchronous = FULL
PRAGMA busy_timeout = 10000
PRAGMA wal_autocheckpoint = 500
```

**Config B: Balanced (Recommended)**
```python
PRAGMA synchronous = NORMAL
PRAGMA busy_timeout = 5000
PRAGMA wal_autocheckpoint = 1000
```

**Config C: Aggressive (Max Performance)**
```python
PRAGMA synchronous = NORMAL
PRAGMA busy_timeout = 2000
PRAGMA wal_autocheckpoint = 5000
```

---

## Deliverables

### 1. Benchmark Report

**Format**: Markdown document with tables and charts

**Sections**:
- Executive Summary
- Test Environment
- Methodology
- Results by Scenario
- PRAGMA Recommendations
- Windows-Specific Findings
- Production Configuration

### 2. Benchmark Script

**File**: `_meta/research/sqlite_queue_benchmark.py`

**Features**:
- Configurable test scenarios
- Multiple PRAGMA configurations
- Results in CSV format
- Summary statistics
- Visualizations (optional)

### 3. Production Configuration

**File**: `Client/Backend/src/queue/config.py`

**Contents**:
```python
# Recommended production settings based on benchmarks
PRODUCTION_PRAGMAS = {
    'journal_mode': 'WAL',
    'synchronous': 'NORMAL',  # From benchmark
    'busy_timeout': 5000,     # From benchmark
    'wal_autocheckpoint': 1000,  # From benchmark
    # ... other tuned values
}
```

### 4. Troubleshooting Guide

**File**: `_meta/docs/SQLITE_QUEUE_TROUBLESHOOTING.md`

**Sections**:
- Common Issues
- Performance Degradation
- SQLITE_BUSY Errors
- Checkpoint Blocking
- Database Corruption
- Recovery Procedures

---

## Metrics to Collect

### Throughput Metrics
- Tasks enqueued per second
- Tasks claimed per second
- Tasks completed per second
- Overall throughput (end-to-end)

### Latency Metrics (P50, P95, P99)
- Enqueue latency
- Poll latency
- Claim latency
- Update latency

### Error Metrics
- SQLITE_BUSY error rate (%)
- SQLITE_BUSY retry count
- Transaction rollback rate
- Lock wait time

### Resource Metrics
- Database file size
- WAL file size
- CPU usage (%)
- I/O operations per second
- Memory usage

### Checkpoint Metrics
- Checkpoint frequency (per minute)
- Checkpoint duration (ms)
- WAL pages checkpointed
- Blocking operations during checkpoint

---

## Analysis Framework

### Statistical Analysis
```python
import statistics

def analyze_latency(measurements):
    """Compute latency statistics."""
    return {
        'mean': statistics.mean(measurements),
        'median': statistics.median(measurements),
        'p95': percentile(measurements, 95),
        'p99': percentile(measurements, 99),
        'min': min(measurements),
        'max': max(measurements)
    }
```

### Performance Comparison
```python
def compare_configs(results_a, results_b):
    """Compare two configuration results."""
    return {
        'throughput_improvement': (results_b.throughput - results_a.throughput) / results_a.throughput * 100,
        'latency_improvement': (results_a.latency - results_b.latency) / results_a.latency * 100,
        'error_rate_change': results_b.error_rate - results_a.error_rate
    }
```

---

## Expected Outcomes

### Best Case 🎯
- Throughput: 500-1000 tasks/min sustained
- Claim latency: <5ms (P95)
- SQLITE_BUSY rate: <0.5%
- 8+ concurrent workers supported
- Clear production configuration

### Realistic Case ✅
- Throughput: 200-500 tasks/min
- Claim latency: <10ms (P95)
- SQLITE_BUSY rate: <2%
- 4-6 concurrent workers
- Some tuning needed per workload

### Worst Case ⚠️
- Throughput: 50-100 tasks/min
- Claim latency: >20ms (P95)
- SQLITE_BUSY rate: >5%
- 2-3 concurrent workers max
- Need to consider PostgreSQL migration

**Mitigation**: If worst case, document upgrade path to PostgreSQL

---

## Timeline

### Week 1: Setup and Baseline (Days 1-2)
- [x] Set up test environment
- [x] Create benchmark scripts
- [x] Run baseline tests (single writer)
- [x] Validate measurement accuracy

### Week 1: Concurrency Tests (Days 3-4)
- [x] Multiple writer tests
- [x] Mixed workload tests
- [x] PRAGMA variation tests
- [x] Collect all metrics

### Week 1: Analysis and Documentation (Days 5-7)
- [x] Statistical analysis
- [x] Create charts and tables
- [x] Write benchmark report
- [x] Define production configuration
- [x] Create troubleshooting guide

---

## Success Criteria

- [x] Benchmark script runs successfully on Windows
- [x] All 5 test scenarios completed
- [x] All 3 PRAGMA configs tested
- [x] Metrics collected for all tests
- [x] Statistical analysis complete
- [x] Production configuration defined
- [x] Benchmark report published
- [x] Troubleshooting guide created
- [x] Recommendations reviewed by team

---

## Integration Points

### Depends On
- ✅ #321: Core Infrastructure (COMPLETED - database implementation available for testing)

### Feeds Into
- #325: Worker Engine (use tuned PRAGMA settings)
- #331: Maintenance (use checkpoint recommendations)
- #339: Integration (apply production config)

---

## Tools and Scripts

### Benchmark Script Structure
```python
# _meta/research/sqlite_queue_benchmark.py

class QueueBenchmark:
    def __init__(self, db_path, config):
        self.db_path = db_path
        self.config = config
    
    def run_scenario(self, scenario_name):
        """Run a benchmark scenario."""
        
    def measure_throughput(self, duration_seconds):
        """Measure tasks per second."""
        
    def measure_latency(self, operation, count):
        """Measure operation latency."""
        
    def measure_concurrency(self, num_workers):
        """Test concurrent workers."""
        
    def generate_report(self):
        """Generate markdown report."""
```

### Analysis Script
```python
# _meta/research/analyze_benchmark_results.py

def parse_results(csv_file):
    """Parse benchmark CSV results."""
    
def compute_statistics(results):
    """Compute statistical metrics."""
    
def generate_charts(results):
    """Generate performance charts."""
    
def create_markdown_report(results, charts):
    """Create final report."""
```

---

## Acceptance Criteria

- [x] Comprehensive benchmark data collected
- [x] Production PRAGMA configuration defined
- [x] Windows-specific findings documented
- [x] Performance targets validated (or adjusted)
- [x] Troubleshooting guide complete
- [x] Team review and approval
- [x] Configuration applied to #321 implementation

---

## Resources

- [SQLite Performance Tuning](https://www.sqlite.org/pragma.html)
- [WAL Mode Explained](https://sqlite.org/wal.html)
- Web research results from #320
- Python `timeit` and `statistics` modules

---

**Status**: 🆕 Ready to Start (#321 COMPLETED - can begin work)  
**Assigned**: Worker 09 - Research Engineer  
**Labels**: `research`, `performance`, `benchmarking`, `windows`
