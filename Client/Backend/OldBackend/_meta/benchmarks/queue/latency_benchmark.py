"""
Latency Benchmark for Queue System

Measures task processing latency (end-to-end time).
Validates against performance targets from Issue #334.

Targets:
- p50: <100ms
- p95: <500ms
- p99: <1000ms
"""

import sys
import time
import json
import tempfile
import asyncio
import statistics
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "Backend"))

from src.queue import (
    QueueDatabase,
    WorkerEngine,
    Task,
    get_global_registry,
    reset_global_registry,
)


def noop_handler(task: Task) -> bool:
    """No-operation task handler for benchmarking."""
    time.sleep(0.001)  # Small delay to simulate minimal work
    return True


def percentile(data: List[float], p: float) -> float:
    """Calculate percentile of data."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[-1]
    d0 = sorted_data[f] * (c - k)
    d1 = sorted_data[c] * (k - f)
    return d0 + d1


async def benchmark_latency(
    db_path: str,
    num_samples: int = 100
) -> Dict[str, Any]:
    """
    Benchmark task processing latency.
    
    Args:
        db_path: Path to database
        num_samples: Number of samples to measure
        
    Returns:
        Dictionary with latency statistics
    """
    # Setup database
    db = QueueDatabase(db_path)
    db.initialize_schema()
    
    # Register task handler
    registry = get_global_registry()
    registry.register_handler("noop", noop_handler, "No-op task for benchmarking")
    
    # Create worker
    worker = WorkerEngine(
        db=db,
        worker_id="latency-worker",
        poll_interval_seconds=0.001,  # Fast polling
        lease_seconds=30,
        handler_registry=registry,
    )
    
    # Start worker in background
    worker_task = None
    
    async def run_worker():
        while True:
            claimed = await asyncio.to_thread(worker.claim_and_process)
            if not claimed:
                await asyncio.sleep(0.001)
    
    try:
        # Start worker
        worker_task = asyncio.create_task(run_worker())
        
        # Measure latencies
        latencies = []
        
        for i in range(num_samples):
            # Enqueue task with timestamp
            start = time.time()
            
            with db.transaction() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO task_queue (type, payload, priority, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("noop", json.dumps({"start": start}), 100, "queued")
                )
                task_id = cursor.lastrowid
            
            # Wait for completion
            while True:
                with db.transaction() as conn:
                    cursor = conn.execute(
                        "SELECT status FROM task_queue WHERE id = ?",
                        (task_id,)
                    )
                    row = cursor.fetchone()
                    if row and row[0] == "completed":
                        break
                
                await asyncio.sleep(0.001)
            
            latency = (time.time() - start) * 1000  # Convert to ms
            latencies.append(latency)
            
            # Small delay between samples
            if i < num_samples - 1:
                await asyncio.sleep(0.01)
        
        # Calculate statistics
        latencies_sorted = sorted(latencies)
        
        return {
            "samples": num_samples,
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "min": min(latencies),
            "max": max(latencies),
            "p50": percentile(latencies, 50),
            "p75": percentile(latencies, 75),
            "p90": percentile(latencies, 90),
            "p95": percentile(latencies, 95),
            "p99": percentile(latencies, 99),
            "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        }
    finally:
        # Stop worker
        if worker_task:
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass
        
        reset_global_registry()
        db.close()


async def run_latency_benchmarks() -> Dict[str, Any]:
    """
    Run complete latency benchmark suite.
    
    Returns:
        Dictionary with all benchmark results
    """
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmarks": [],
        "targets": {
            "p50": 100,   # ms
            "p95": 500,   # ms
            "p99": 1000,  # ms
        }
    }
    
    print("=" * 70)
    print("LATENCY BENCHMARK")
    print("=" * 70)
    
    # Test with different sample sizes
    sample_sizes = [100]
    
    for num_samples in sample_sizes:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "benchmark.db")
            
            print(f"\nMeasuring latency with {num_samples} samples...")
            
            result = await benchmark_latency(db_path, num_samples)
            results["benchmarks"].append(result)
            
            # Display results
            print(f"\nLatency Statistics (ms):")
            print(f"  Mean:    {result['mean']:.2f} ms")
            print(f"  Median:  {result['median']:.2f} ms")
            print(f"  Min:     {result['min']:.2f} ms")
            print(f"  Max:     {result['max']:.2f} ms")
            print(f"  StdDev:  {result['stdev']:.2f} ms")
            print(f"\nPercentiles:")
            print(f"  p50:     {result['p50']:.2f} ms")
            print(f"  p75:     {result['p75']:.2f} ms")
            print(f"  p90:     {result['p90']:.2f} ms")
            print(f"  p95:     {result['p95']:.2f} ms")
            print(f"  p99:     {result['p99']:.2f} ms")
            
            # Check against targets
            targets = results["targets"]
            p50_status = "✅ PASS" if result['p50'] < targets['p50'] else "❌ FAIL"
            p95_status = "✅ PASS" if result['p95'] < targets['p95'] else "❌ FAIL"
            p99_status = "✅ PASS" if result['p99'] < targets['p99'] else "❌ FAIL"
            
            print(f"\nTarget Validation:")
            print(f"  p50 < {targets['p50']}ms:  {p50_status}")
            print(f"  p95 < {targets['p95']}ms:  {p95_status}")
            print(f"  p99 < {targets['p99']}ms: {p99_status}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    bench = results["benchmarks"][0]
    targets = results["targets"]
    
    print(f"{'Metric':<10} {'Actual':<15} {'Target':<15} {'Status'}")
    print(f"{'-'*10} {'-'*15} {'-'*15} {'-'*10}")
    
    p50_status = "✅ PASS" if bench['p50'] < targets['p50'] else "❌ FAIL"
    print(f"{'p50':<10} {bench['p50']:.2f} ms{'':<6} < {targets['p50']} ms{'':<6} {p50_status}")
    
    p95_status = "✅ PASS" if bench['p95'] < targets['p95'] else "❌ FAIL"
    print(f"{'p95':<10} {bench['p95']:.2f} ms{'':<6} < {targets['p95']} ms{'':<6} {p95_status}")
    
    p99_status = "✅ PASS" if bench['p99'] < targets['p99'] else "❌ FAIL"
    print(f"{'p99':<10} {bench['p99']:.2f} ms{'':<6} < {targets['p99']} ms{'':<5} {p99_status}")
    
    return results


if __name__ == "__main__":
    # Run benchmarks
    results = asyncio.run(run_latency_benchmarks())
    
    # Save results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"latency_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
