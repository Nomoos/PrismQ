# Queue System Benchmarks

Performance benchmarks for the PrismQ Client Queue System, implementing **Issue #334**.

## Overview

This directory contains comprehensive performance benchmarks to validate that the queue system meets performance targets and operates efficiently under various load conditions.

## Benchmark Suites

### 1. Throughput Benchmark (`throughput_benchmark.py`)
Measures tasks processed per second with varying worker counts.

**Targets:**
- Single Worker: >50 tasks/second
- 5 Workers: >200 tasks/second
- 10 Workers: >300 tasks/second

**Run:**
```bash
cd _meta/benchmarks/queue
python throughput_benchmark.py
```

### 2. Latency Benchmark (`latency_benchmark.py`)
Measures end-to-end task processing latency.

**Targets:**
- p50: <100ms
- p95: <500ms
- p99: <1000ms

**Run:**
```bash
python latency_benchmark.py
```

### 3. Concurrency Benchmark (`concurrency_benchmark.py`)
Tests scaling behavior with concurrent workers.

**Targets:**
- Max Concurrent Workers: 20+
- No SQLITE_BUSY errors: Under 10 workers
- Task Claim Conflicts: <1%

**Run:**
```bash
python concurrency_benchmark.py
```

### 4. Stress Test (`stress_test.py`)
Tests system behavior under extreme load conditions.

**Validates:**
- System stability
- Error handling
- Resource management
- Recovery behavior

**Run:**
```bash
python stress_test.py
```

### 5. Memory Profile (`memory_profile.py`)
Monitors memory usage patterns.

**Tracks:**
- Memory growth over time
- Peak memory usage
- Potential memory leaks
- Garbage collection effectiveness

**Run:**
```bash
python memory_profile.py
```

## Running All Benchmarks

Use the main benchmark runner to execute all suites:

```bash
cd _meta/benchmarks/queue
python benchmark_runner.py
```

This will:
1. Run all benchmark suites
2. Generate comprehensive results in JSON format
3. Create a markdown report with summary
4. Save all outputs to the `results/` directory

## Results

Benchmark results are saved in the `results/` directory with timestamps:

- `throughput_results_YYYYMMDD_HHMMSS.json`
- `latency_results_YYYYMMDD_HHMMSS.json`
- `concurrency_results_YYYYMMDD_HHMMSS.json`
- `stress_test_results_YYYYMMDD_HHMMSS.json`
- `memory_profile_results_YYYYMMDD_HHMMSS.json`
- `benchmark_results_YYYYMMDD_HHMMSS.json` (combined)
- `benchmark_report_YYYYMMDD_HHMMSS.md` (summary report)

## Dependencies

Benchmarks require:
- Python 3.10+
- psutil (for memory profiling)
- asyncio support
- Backend queue system modules

Install with:
```bash
cd Backend
pip install -e .
pip install psutil
```

## Performance Targets

### Throughput
| Workers | Target TPS | Description |
|---------|-----------|-------------|
| 1       | >50       | Single worker baseline |
| 5       | >200      | Medium concurrency |
| 10      | >300      | High concurrency |

### Latency
| Percentile | Target | Description |
|------------|--------|-------------|
| p50        | <100ms | Median latency |
| p95        | <500ms | 95th percentile |
| p99        | <1000ms| 99th percentile |

### Concurrency
| Metric | Target | Description |
|--------|--------|-------------|
| Max Workers | 20+ | Maximum concurrent workers supported |
| SQLITE_BUSY | 0 | No database lock errors with ≤10 workers |
| Conflicts | <1% | Task claim conflict rate |

## Understanding Results

### Throughput
- **TPS (Tasks Per Second)**: Number of tasks completed per second
- **Efficiency**: Tasks per second per worker (indicates scaling efficiency)
- **Status**: ✅ PASS if target is met, ❌ FAIL otherwise

### Latency
- **p50/p95/p99**: Percentile latencies in milliseconds
- Lower is better
- p99 shows worst-case performance

### Concurrency
- **Throughput vs Workers**: Should scale approximately linearly up to 10 workers
- **Conflict Rate**: Percentage of task claims that failed
- **SQLITE_BUSY Errors**: Database lock errors (should be 0 with ≤10 workers)

### Stress Tests
- **Completion Rate**: Percentage of tasks successfully completed
- **Memory Growth**: Memory increase during test
- **Error Count**: Number of errors encountered

### Memory Profile
- **Growth**: Memory increase over test duration
- **Peak**: Maximum memory usage
- Steady growth may indicate memory leaks

## Baseline Results

Baseline results are established on first run. Compare subsequent runs against the baseline to detect performance regressions.

## Troubleshooting

### Import Errors
Make sure Backend is in Python path:
```bash
export PYTHONPATH=/path/to/Backend:$PYTHONPATH
```

### Database Locked Errors
- Indicates too many concurrent workers for current configuration
- Expected with >20 workers
- Should not occur with ≤10 workers

### Low Throughput
Possible causes:
- System under load from other processes
- Disk I/O bottleneck
- Need to increase worker count

### High Memory Usage
- Check for memory leaks in task handlers
- Review task payload sizes
- Consider implementing task result cleanup

## Related Issues

- **#334**: Performance Benchmarks (this implementation)
- **#337**: Concurrency Research - Framework design
- **#338**: Strategy Analysis - Performance analysis
- **#333**: Testing - Test infrastructure

## Contributing

When adding new benchmarks:
1. Follow the existing pattern (setup, run, report)
2. Include performance targets
3. Generate both JSON and human-readable output
4. Update this README
5. Add results to the benchmark runner

## License

Part of PrismQ Client Backend - Proprietary
