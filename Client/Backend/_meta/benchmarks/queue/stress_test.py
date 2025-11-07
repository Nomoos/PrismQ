"""
Stress Test for Queue System

Tests system behavior under extreme load conditions.
Validates stability, error handling, and resource management.
"""

import sys
import time
import json
import tempfile
import asyncio
import psutil
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "Backend"))

from src.queue import (
    QueueDatabase,
    WorkerEngine,
    Task,
    get_global_registry,
    reset_global_registry,
)


def variable_workload_handler(task: Task) -> bool:
    """Task handler with variable workload."""
    payload = json.loads(task.payload)
    work_ms = payload.get("work_ms", 5)
    time.sleep(work_ms / 1000.0)
    return True


async def stress_test_high_volume(
    db_path: str,
    num_workers: int,
    num_tasks: int,
    duration_seconds: int
) -> Dict[str, Any]:
    """
    Stress test with high volume of tasks.
    
    Args:
        db_path: Path to database
        num_workers: Number of concurrent workers
        num_tasks: Number of tasks to enqueue
        duration_seconds: Maximum duration to run
        
    Returns:
        Dictionary with stress test results
    """
    # Setup database
    db = QueueDatabase(db_path)
    db.initialize_schema()
    
    # Register task handler
    registry = get_global_registry()
    registry.register_handler("variable_workload", variable_workload_handler, "Variable workload handler")
    
    # Track metrics
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    errors = []
    completed_count = 0
    failed_count = 0
    
    try:
        # Enqueue tasks in batches
        print(f"  Enqueuing {num_tasks} tasks...")
        enqueue_start = time.time()
        
        batch_size = 100
        for batch_start in range(0, num_tasks, batch_size):
            batch_end = min(batch_start + batch_size, num_tasks)
            with db.transaction() as conn:
                for i in range(batch_start, batch_end):
                    work_ms = 1 + (i % 10)  # Variable workload 1-10ms
                    conn.execute(
                        """
                        INSERT INTO task_queue (type, payload, priority, status)
                        VALUES (?, ?, ?, ?)
                        """,
                        ("variable_workload", json.dumps({"work_ms": work_ms}), 100, "queued")
                    )
        
        enqueue_duration = time.time() - enqueue_start
        print(f"  Enqueued in {enqueue_duration:.2f} sec")
        
        # Create workers
        workers = [
            WorkerEngine(
                db=db,
                worker_id=f"stress-worker-{i}",
                poll_interval_seconds=0.01,
                lease_seconds=60,
                handler_registry=registry,
            )
            for i in range(num_workers)
        ]
        
        # Process tasks with timeout
        start = time.time()
        
        async def run_worker_with_monitoring(worker):
            nonlocal completed_count, failed_count
            
            while (time.time() - start) < duration_seconds:
                try:
                    claimed = await asyncio.to_thread(worker.claim_and_process)
                    if not claimed:
                        await asyncio.sleep(0.01)
                        continue
                    
                    # Track completion (worker handles success/failure internally)
                    completed_count += 1
                        
                except Exception as e:
                    errors.append(str(e))
                    await asyncio.sleep(0.01)
        
        # Run with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*[run_worker_with_monitoring(w) for w in workers]),
                timeout=duration_seconds
            )
        except asyncio.TimeoutError:
            print(f"  Stress test reached {duration_seconds}s timeout")
        
        duration = time.time() - start
        
        # Collect final metrics
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Check remaining tasks
        with db.transaction() as conn:
            cursor = conn.execute(
                """
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'completed') as completed,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed,
                    COUNT(*) FILTER (WHERE status = 'queued') as queued,
                    COUNT(*) FILTER (WHERE status = 'leased') as leased
                FROM task_queue
                """
            )
            row = cursor.fetchone()
            db_completed = row[0] if row else 0
            db_failed = row[1] if row else 0
            db_queued = row[2] if row else 0
            db_leased = row[3] if row else 0
        
        return {
            "workers": num_workers,
            "tasks_enqueued": num_tasks,
            "enqueue_duration": enqueue_duration,
            "test_duration": duration,
            "completed": db_completed,
            "failed": db_failed,
            "queued": db_queued,
            "leased": db_leased,
            "throughput": db_completed / duration if duration > 0 else 0,
            "memory_initial_mb": initial_memory,
            "memory_final_mb": final_memory,
            "memory_increase_mb": memory_increase,
            "errors": errors[:10],  # First 10 errors
            "error_count": len(errors),
        }
    finally:
        reset_global_registry()
        db.close()


async def run_stress_tests() -> Dict[str, Any]:
    """
    Run complete stress test suite.
    
    Returns:
        Dictionary with all stress test results
    """
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": []
    }
    
    print("=" * 70)
    print("STRESS TEST")
    print("=" * 70)
    
    # Test configurations
    configs = [
        {
            "name": "High Volume - 10 Workers",
            "workers": 10,
            "tasks": 5000,
            "duration": 60,
        },
        {
            "name": "High Concurrency - 20 Workers",
            "workers": 20,
            "tasks": 2000,
            "duration": 60,
        },
    ]
    
    for config in configs:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "stress_test.db")
            
            print(f"\n{config['name']}")
            print(f"  Workers: {config['workers']}")
            print(f"  Tasks: {config['tasks']}")
            print(f"  Max Duration: {config['duration']}s")
            
            result = await stress_test_high_volume(
                db_path,
                config['workers'],
                config['tasks'],
                config['duration']
            )
            
            result["test_name"] = config["name"]
            results["tests"].append(result)
            
            # Display results
            print(f"\nResults:")
            print(f"  Duration:     {result['test_duration']:.2f} sec")
            print(f"  Completed:    {result['completed']} ({result['completed']/result['tasks_enqueued']*100:.1f}%)")
            print(f"  Failed:       {result['failed']}")
            print(f"  Queued:       {result['queued']}")
            print(f"  Leased:       {result['leased']}")
            print(f"  Throughput:   {result['throughput']:.2f} tasks/sec")
            print(f"  Memory:       {result['memory_initial_mb']:.1f} MB → {result['memory_final_mb']:.1f} MB (+{result['memory_increase_mb']:.1f} MB)")
            print(f"  Errors:       {result['error_count']}")
            
            if result['error_count'] > 0:
                print(f"\n  Sample Errors:")
                for err in result['errors'][:3]:
                    print(f"    - {err}")
    
    print("\n" + "=" * 70)
    print("STRESS TEST SUMMARY")
    print("=" * 70)
    
    for test in results["tests"]:
        completion_rate = (test['completed'] / test['tasks_enqueued'] * 100) if test['tasks_enqueued'] > 0 else 0
        status = "✅ STABLE" if completion_rate > 95 and test['error_count'] < 10 else "⚠️  ISSUES"
        
        print(f"\n{test['test_name']}: {status}")
        print(f"  Completion Rate: {completion_rate:.1f}%")
        print(f"  Throughput:      {test['throughput']:.2f} tasks/sec")
        print(f"  Memory Growth:   {test['memory_increase_mb']:.1f} MB")
        print(f"  Errors:          {test['error_count']}")
    
    return results


if __name__ == "__main__":
    # Run stress tests
    results = asyncio.run(run_stress_tests())
    
    # Save results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"stress_test_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
