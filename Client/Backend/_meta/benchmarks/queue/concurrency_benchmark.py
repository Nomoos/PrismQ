"""
Concurrency Benchmark for Queue System

Tests scaling behavior with varying numbers of concurrent workers.
Validates against performance targets from Issue #334.

Targets:
- Max Concurrent Workers: 20+
- No SQLITE_BUSY errors: Under 10 workers
- Task Claim Conflicts: <1%
"""

import sys
import time
import json
import tempfile
import asyncio
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
    time.sleep(0.002)  # Small delay to simulate work
    return True


async def benchmark_concurrency(
    db_path: str,
    num_workers: int,
    num_tasks: int
) -> Dict[str, Any]:
    """
    Benchmark concurrency with given worker count.
    
    Args:
        db_path: Path to database
        num_workers: Number of concurrent workers
        num_tasks: Number of tasks to process
        
    Returns:
        Dictionary with benchmark results
    """
    # Setup database
    db = QueueDatabase(db_path)
    db.initialize_schema()
    
    # Register task handler
    registry = get_global_registry()
    registry.register_handler("noop", noop_handler, "No-op task for benchmarking")
    
    # Track claim conflicts
    claims_attempted = 0
    claims_successful = 0
    sqlite_busy_errors = 0
    
    try:
        # Enqueue tasks
        with db.transaction() as conn:
            for i in range(num_tasks):
                conn.execute(
                    """
                    INSERT INTO task_queue (type, payload, priority, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("noop", "{}", 100, "queued")
                )
        
        # Create workers
        workers = [
            WorkerEngine(
                db=db,
                worker_id=f"concurrent-worker-{i}",
                poll_interval_seconds=0.01,
                lease_seconds=30,
                handler_registry=registry,
            )
            for i in range(num_workers)
        ]
        
        # Track worker statistics
        worker_stats = {i: {"tasks": 0, "busy_errors": 0} for i in range(num_workers)}
        
        # Process tasks
        start = time.time()
        
        async def run_worker(worker_idx, worker):
            nonlocal claims_attempted, claims_successful, sqlite_busy_errors
            
            while True:
                try:
                    claims_attempted += 1
                    claimed = await asyncio.to_thread(worker.claim_and_process)
                    
                    if not claimed:
                        # Check if queue is truly empty
                        await asyncio.sleep(0.01)
                        claimed = await asyncio.to_thread(worker.claim_and_process)
                        claims_attempted += 1
                        if not claimed:
                            break
                    
                    claims_successful += 1
                    worker_stats[worker_idx]["tasks"] += 1
                    
                except Exception as e:
                    if "SQLITE_BUSY" in str(e) or "database is locked" in str(e):
                        sqlite_busy_errors += 1
                        worker_stats[worker_idx]["busy_errors"] += 1
                        await asyncio.sleep(0.01)  # Back off
                    else:
                        raise
        
        await asyncio.gather(*[run_worker(i, w) for i, w in enumerate(workers)])
        
        duration = time.time() - start
        
        # Verify all tasks completed
        with db.transaction() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM task_queue WHERE status = 'completed'"
            )
            completed = cursor.fetchone()[0]
        
        # Calculate conflict rate
        conflict_rate = 0
        if claims_attempted > 0:
            conflict_rate = ((claims_attempted - claims_successful) / claims_attempted) * 100
        
        # Calculate efficiency
        throughput = completed / duration if duration > 0 else 0
        efficiency = throughput / num_workers if num_workers > 0 else 0
        
        return {
            "workers": num_workers,
            "tasks": num_tasks,
            "completed": completed,
            "duration": duration,
            "throughput": throughput,
            "efficiency": efficiency,
            "claims_attempted": claims_attempted,
            "claims_successful": claims_successful,
            "conflict_rate": conflict_rate,
            "sqlite_busy_errors": sqlite_busy_errors,
            "worker_stats": worker_stats,
        }
    finally:
        reset_global_registry()
        db.close()


async def run_concurrency_benchmarks() -> Dict[str, Any]:
    """
    Run complete concurrency benchmark suite.
    
    Returns:
        Dictionary with all benchmark results
    """
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmarks": [],
        "targets": {
            "max_workers": 20,
            "conflict_rate_threshold": 1.0,  # percent
            "busy_errors_under_10_workers": 0,
        }
    }
    
    print("=" * 70)
    print("CONCURRENCY BENCHMARK")
    print("=" * 70)
    
    # Test configurations - increasing worker counts
    worker_counts = [1, 2, 5, 10, 15, 20]
    tasks_per_test = 500
    
    for num_workers in worker_counts:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "benchmark.db")
            
            print(f"\nTesting with {num_workers} workers, {tasks_per_test} tasks...")
            
            result = await benchmark_concurrency(db_path, num_workers, tasks_per_test)
            results["benchmarks"].append(result)
            
            # Display results
            print(f"  Throughput:   {result['throughput']:.2f} tasks/sec")
            print(f"  Efficiency:   {result['efficiency']:.2f} tasks/sec/worker")
            print(f"  Duration:     {result['duration']:.2f} sec")
            print(f"  Completed:    {result['completed']}/{result['tasks']}")
            print(f"  Conflict Rate: {result['conflict_rate']:.2f}%")
            print(f"  SQLITE_BUSY:  {result['sqlite_busy_errors']} errors")
            
            # Check against targets
            if num_workers <= 10:
                busy_status = "✅ PASS" if result['sqlite_busy_errors'] == 0 else "❌ FAIL"
                print(f"  SQLITE_BUSY Target (<10 workers): {busy_status}")
            
            conflict_status = "✅ PASS" if result['conflict_rate'] < results["targets"]["conflict_rate_threshold"] else "❌ FAIL"
            print(f"  Conflict Rate Target (<1%): {conflict_status}")
    
    print("\n" + "=" * 70)
    print("SCALING ANALYSIS")
    print("=" * 70)
    
    # Calculate scaling efficiency
    baseline = results["benchmarks"][0]["throughput"]
    
    print(f"\n{'Workers':<10} {'TPS':<15} {'Speedup':<15} {'Efficiency':<15}")
    print(f"{'-'*10} {'-'*15} {'-'*15} {'-'*15}")
    
    for bench in results["benchmarks"]:
        workers = bench["workers"]
        tps = bench["throughput"]
        speedup = tps / baseline if baseline > 0 else 0
        ideal_speedup = workers
        scaling_efficiency = (speedup / ideal_speedup * 100) if ideal_speedup > 0 else 0
        
        print(f"{workers:<10} {tps:<15.2f} {speedup:<15.2f}x {scaling_efficiency:<15.1f}%")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    # Check overall targets
    max_workers_tested = max(b["workers"] for b in results["benchmarks"])
    max_workers_status = "✅ PASS" if max_workers_tested >= 20 else "❌ FAIL"
    print(f"\n✓ Max Workers Tested: {max_workers_tested} (target: ≥20) {max_workers_status}")
    
    # Check SQLITE_BUSY errors for <= 10 workers
    busy_errors_under_10 = sum(
        b["sqlite_busy_errors"] for b in results["benchmarks"] 
        if b["workers"] <= 10
    )
    busy_status = "✅ PASS" if busy_errors_under_10 == 0 else "❌ FAIL"
    print(f"✓ SQLITE_BUSY errors (≤10 workers): {busy_errors_under_10} (target: 0) {busy_status}")
    
    # Check conflict rates
    max_conflict_rate = max(b["conflict_rate"] for b in results["benchmarks"])
    conflict_status = "✅ PASS" if max_conflict_rate < 1.0 else "❌ FAIL"
    print(f"✓ Max Conflict Rate: {max_conflict_rate:.2f}% (target: <1%) {conflict_status}")
    
    return results


if __name__ == "__main__":
    # Run benchmarks
    results = asyncio.run(run_concurrency_benchmarks())
    
    # Save results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"concurrency_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
