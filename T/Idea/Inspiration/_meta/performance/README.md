# Performance Profiling and Benchmarking

This directory contains performance profiling tools, benchmark tests, and baseline reports for the PrismQ.T.Idea.Inspiration ecosystem.

## Overview

Phase A of issue #111 focuses on establishing performance baselines by:
1. Profiling current performance of all modules
2. Identifying bottlenecks and optimization opportunities
3. Creating reproducible benchmark tests
4. Documenting baseline performance metrics

## Directory Structure

```
performance/
├── README.md                    # This file
├── requirements.txt             # Profiling dependencies
├── profiling_utils.py           # Reusable profiling utilities
├── benchmarks/                  # Benchmark test suites
│   ├── bench_client_backend.py
│   ├── bench_scoring.py
│   └── bench_classification.py
├── scripts/                     # Profiling execution scripts
│   ├── profile_all.py
│   ├── profile_client.py
│   ├── profile_scoring.py
│   └── profile_classification.py
└── reports/                     # Generated reports (git-ignored)
    ├── baseline/                # Initial baseline reports
    ├── cpu/                     # CPU profiling results
    ├── memory/                  # Memory profiling results
    └── benchmarks/              # Benchmark results
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Benchmarks

```bash
# Run individual module benchmarks
cd benchmarks
python -m pytest bench_scoring.py -v --benchmark-only --benchmark-autosave
python -m pytest bench_classification.py -v --benchmark-only --benchmark-autosave

# Or run all at once (requires fixing import issues first)
python scripts/profile_all.py
```

### 3. View Reports

#### Performance Baseline Report
- **Location**: `reports/PERFORMANCE_BASELINE_REPORT.md`
- **Content**: Comprehensive baseline metrics, performance targets comparison
- **Status**: ✅ Complete

#### Bottleneck Identification
- **Location**: `reports/BOTTLENECK_IDENTIFICATION.md`
- **Content**: Identified bottlenecks with priority and fix recommendations
- **Status**: ✅ Complete

#### Benchmark Data
- **Location**: `benchmarks/.benchmarks/`
- **Format**: JSON files with detailed timing data
- **Latest**: `Linux-CPython-3.12-64bit/0002_*.json`

### 4. Current Status

**Phase A Complete** ✅
- [x] Performance baseline established
- [x] Benchmark tests created and run
- [x] Bottlenecks identified
- [x] Reports generated

**Known Issues** ⚠️:
- **Import structure issues** in Scoring and Client Backend modules prevent some benchmarks from running
- The benchmark tests use `sys.path` manipulation which may not work reliably across all execution contexts
- See `BOTTLENECK_IDENTIFICATION.md` for details and recommended fixes

**Workaround**:
```bash
# Run benchmarks from the benchmarks directory
cd _meta/performance/benchmarks
python -m pytest bench_scoring.py -v --benchmark-only
python -m pytest bench_classification.py -v --benchmark-only
```

## Profiling Tools

### CPU Profiling
- **cProfile**: Built-in Python profiler for function call statistics
- **py-spy**: Sampling profiler with minimal overhead
- **line_profiler**: Line-by-line profiling for specific functions

### Memory Profiling
- **memory_profiler**: Line-by-line memory usage
- **tracemalloc**: Built-in memory tracking
- **objgraph**: Object reference graphs

### Benchmarking
- **pytest-benchmark**: Microbenchmarks integrated with pytest
- Custom timing utilities for end-to-end scenarios

## Performance Targets

### Client Backend (FastAPI)
- API response time: <100ms for GET requests (p95)
- Module launch time: <500ms
- Concurrent runs: Support 10+ without degradation
- Log streaming: >10,000 lines/second
- Memory usage: <500MB for 10 concurrent runs
- CPU usage: <50% average under normal load

### Scoring Module
- Text scoring: <50ms per document
- YouTube score calculation: <10ms
- Universal Content Score: <100ms with full metrics
- Memory usage: <100MB per scoring session

### Classification Module
- Category classification: <100ms per item
- Story detection: <150ms per item
- Batch processing: >100 items/second
- Memory usage: <200MB for typical workloads

## Usage Examples

### Profile a Specific Function

```python
from profiling_utils import profile_function

@profile_function(output_dir="reports/cpu")
def my_slow_function():
    # Your code here
    pass
```

### Memory Profiling

```python
from profiling_utils import profile_memory

@profile_memory(output_dir="reports/memory")
def memory_intensive_function():
    # Your code here
    pass
```

### Run Benchmarks

```bash
# Run all benchmarks
pytest benchmarks/ -v --benchmark-only

# Run specific module benchmarks
pytest benchmarks/bench_scoring.py -v --benchmark-only

# Save benchmark results
pytest benchmarks/ --benchmark-save=baseline
```

## Interpreting Results

### CPU Profiling Reports
- **cumtime**: Cumulative time (including subcalls) - identifies high-level bottlenecks
- **tottime**: Total time (excluding subcalls) - identifies specific slow functions
- **ncalls**: Number of calls - identifies hot paths

### Memory Profiling Reports
- **Line-by-line**: Shows memory allocation per line
- **Peak memory**: Maximum memory usage
- **Memory leaks**: Persistent memory growth

### Benchmark Results
- **Mean**: Average execution time
- **StdDev**: Standard deviation (lower is better for consistency)
- **Min/Max**: Range of execution times
- **Rounds**: Number of iterations

## Best Practices

1. **Baseline First**: Always run profiling on the current code before making changes
2. **Isolate Tests**: Profile one component at a time to avoid interference
3. **Realistic Data**: Use production-like data sizes and patterns
4. **Multiple Runs**: Run benchmarks multiple times to account for variance
5. **Document Changes**: Track performance improvements/regressions over time

## RTX 5090 Optimization Notes

This codebase is optimized for:
- **GPU**: NVIDIA RTX 5090 (Ada Lovelace, 32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

Profiling focuses on:
- GPU utilization monitoring (if applicable)
- Memory bandwidth optimization
- Multi-threading efficiency
- Cache-friendly data structures

## Related Documentation

- [Issue #111: Testing and Performance Optimization](../issues/new/111-testing-optimization.md)
- [SOLID Principles](../docs/SOLID_PRINCIPLES.md)
- [Implementation Timeline](../issues/IMPLEMENTATION_TIMELINE.md)
