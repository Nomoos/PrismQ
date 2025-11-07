"""
Throughput Benchmark for Queue System

Tests tasks per second with varying worker counts.
Validates against performance targets from Issue #334.

Targets:
- Single Worker: >50 tasks/second
- 5 Workers: >200 tasks/second
- 10 Workers: >300 tasks/second
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
    return True


async def benchmark_throughput(
    db_path: str,
    num_workers: int,
    num_tasks: int
) -> Dict[str, Any]:
    """
    Benchmark throughput with given worker count.
    
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
    
    try:
        # Enqueue tasks
        enqueue_start = time.time()
        with db.transaction() as conn:
            for i in range(num_tasks):
                conn.execute(
                    """
                    INSERT INTO task_queue (type, payload, priority, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("noop", "{}", 100, "queued")
                )
        enqueue_duration = time.time() - enqueue_start
        
        # Create workers
        workers = [
            WorkerEngine(
                db=db,
                worker_id=f"bench-worker-{i}",
                poll_interval_seconds=0.01,  # Fast polling for benchmarking
                lease_seconds=30,
                handler_registry=registry,
            )
            for i in range(num_workers)
        ]
        
        # Process tasks
        process_start = time.time()
        
        # Run workers until queue is empty
        async def run_worker(worker):
            while True:
                # Attempt to claim and process a task
                claimed = await asyncio.to_thread(worker.claim_and_process)
                if not claimed:
                    # No task available, check one more time
                    await asyncio.sleep(0.01)
                    claimed = await asyncio.to_thread(worker.claim_and_process)
                    if not claimed:
                        break
        
        await asyncio.gather(*[run_worker(w) for w in workers])
        
        process_duration = time.time() - process_start
        
        # Verify all tasks completed
        with db.transaction() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM task_queue WHERE status = 'completed'"
            )
            completed = cursor.fetchone()[0]
        
        total_duration = enqueue_duration + process_duration
        
        return {
            "workers": num_workers,
            "tasks": num_tasks,
            "completed": completed,
            "enqueue_duration": enqueue_duration,
            "enqueue_tps": num_tasks / enqueue_duration if enqueue_duration > 0 else 0,
            "process_duration": process_duration,
            "process_tps": completed / process_duration if process_duration > 0 else 0,
            "total_duration": total_duration,
            "overall_tps": completed / total_duration if total_duration > 0 else 0,
            "efficiency": (completed / process_duration / num_workers) if (process_duration > 0 and num_workers > 0) else 0,
        }
    finally:
        reset_global_registry()
        db.close()


async def run_throughput_benchmarks() -> Dict[str, Any]:
    """
    Run complete throughput benchmark suite.
    
    Returns:
        Dictionary with all benchmark results
    """
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmarks": [],
        "targets": {
            "single_worker": 50,
            "five_workers": 200,
            "ten_workers": 300,
        }
    }
    
    # Test configurations
    configs = [
        (1, 1000),    # 1 worker, 1000 tasks
        (5, 1000),    # 5 workers, 1000 tasks
        (10, 1000),   # 10 workers, 1000 tasks
    ]
    
    print("=" * 70)
    print("THROUGHPUT BENCHMARK")
    print("=" * 70)
    
    for num_workers, num_tasks in configs:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "benchmark.db")
            
            print(f"\nRunning: {num_workers} worker(s), {num_tasks} tasks...")
            
            result = await benchmark_throughput(db_path, num_workers, num_tasks)
            results["benchmarks"].append(result)
            
            # Display results
            print(f"  Enqueue TPS:  {result['enqueue_tps']:.2f} tasks/sec")
            print(f"  Process TPS:  {result['process_tps']:.2f} tasks/sec")
            print(f"  Overall TPS:  {result['overall_tps']:.2f} tasks/sec")
            print(f"  Efficiency:   {result['efficiency']:.2f} tasks/sec/worker")
            print(f"  Completed:    {result['completed']}/{result['tasks']}")
            
            # Check against targets
            target = None
            if num_workers == 1:
                target = results["targets"]["single_worker"]
            elif num_workers == 5:
                target = results["targets"]["five_workers"]
            elif num_workers == 10:
                target = results["targets"]["ten_workers"]
            
            if target:
                status = "✅ PASS" if result['process_tps'] >= target else "❌ FAIL"
                print(f"  Target:       {target} tasks/sec {status}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for bench in results["benchmarks"]:
        workers = bench["workers"]
        tps = bench["process_tps"]
        
        if workers == 1:
            target = results["targets"]["single_worker"]
            status = "✅" if tps >= target else "❌"
            print(f"{status} {workers} worker(s):  {tps:.2f} TPS (target: {target})")
        elif workers == 5:
            target = results["targets"]["five_workers"]
            status = "✅" if tps >= target else "❌"
            print(f"{status} {workers} worker(s): {tps:.2f} TPS (target: {target})")
        elif workers == 10:
            target = results["targets"]["ten_workers"]
            status = "✅" if tps >= target else "❌"
            print(f"{status} {workers} worker(s): {tps:.2f} TPS (target: {target})")
    
    return results


if __name__ == "__main__":
    # Run benchmarks
    results = asyncio.run(run_throughput_benchmarks())
    
    # Save results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"throughput_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
