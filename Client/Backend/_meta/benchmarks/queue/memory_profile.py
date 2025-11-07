"""
Memory Profiling for Queue System

Monitors memory usage patterns during queue operations.
Identifies memory leaks and optimization opportunities.
"""

import sys
import time
import json
import tempfile
import asyncio
import psutil
import os
import gc
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


def memory_intensive_handler(task: Task) -> bool:
    """Task handler that uses memory."""
    # Simulate some memory usage
    payload = json.loads(task.payload)
    size = payload.get("size", 100)
    data = [i for i in range(size * 1000)]
    return True


class MemoryProfiler:
    """Tracks memory usage over time."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.snapshots = []
    
    def snapshot(self, label: str = ""):
        """Take a memory snapshot."""
        mem_info = self.process.memory_info()
        self.snapshots.append({
            "timestamp": time.time(),
            "label": label,
            "rss_mb": mem_info.rss / 1024 / 1024,
            "vms_mb": mem_info.vms / 1024 / 1024,
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        if not self.snapshots:
            return {}
        
        rss_values = [s["rss_mb"] for s in self.snapshots]
        
        return {
            "snapshot_count": len(self.snapshots),
            "initial_rss_mb": rss_values[0],
            "final_rss_mb": rss_values[-1],
            "peak_rss_mb": max(rss_values),
            "growth_mb": rss_values[-1] - rss_values[0],
            "snapshots": self.snapshots,
        }


async def profile_worker_lifecycle(db_path: str, num_cycles: int = 5) -> Dict[str, Any]:
    """
    Profile memory usage through worker lifecycle.
    
    Args:
        db_path: Path to database
        num_cycles: Number of start/stop cycles
        
    Returns:
        Memory profiling results
    """
    profiler = MemoryProfiler()
    profiler.snapshot("initial")
    
    # Setup database
    db = QueueDatabase(db_path)
    db.initialize_schema()
    profiler.snapshot("db_initialized")
    
    # Register handler
    registry = get_global_registry()
    registry.register_handler("memory_test", memory_intensive_handler, "Memory test handler")
    profiler.snapshot("handler_registered")
    
    try:
        for cycle in range(num_cycles):
            # Enqueue tasks
            with db.transaction() as conn:
                for i in range(100):
                    conn.execute(
                        """
                        INSERT INTO task_queue (type, payload, priority, status)
                        VALUES (?, ?, ?, ?)
                        """,
                        ("memory_test", json.dumps({"size": 10}), 100, "queued")
                    )
            profiler.snapshot(f"cycle_{cycle}_enqueued")
            
            # Create and run worker
            worker = WorkerEngine(
                db=db,
                worker_id=f"memory-worker-{cycle}",
                poll_interval_seconds=0.01,
                lease_seconds=30,
                handler_registry=registry,
            )
            profiler.snapshot(f"cycle_{cycle}_worker_created")
            
            # Process tasks
            processed = 0
            while processed < 100:
                claimed = await asyncio.to_thread(worker.claim_and_process)
                if claimed:
                    processed += 1
                else:
                    await asyncio.sleep(0.01)
            
            profiler.snapshot(f"cycle_{cycle}_completed")
            
            # Clean up
            del worker
            gc.collect()
            profiler.snapshot(f"cycle_{cycle}_gc")
        
        profiler.snapshot("final")
        
        return profiler.get_stats()
        
    finally:
        reset_global_registry()
        db.close()


async def profile_concurrent_workers(
    db_path: str,
    num_workers: int,
    num_tasks: int
) -> Dict[str, Any]:
    """
    Profile memory usage with concurrent workers.
    
    Args:
        db_path: Path to database
        num_workers: Number of concurrent workers
        num_tasks: Number of tasks to process
        
    Returns:
        Memory profiling results
    """
    profiler = MemoryProfiler()
    profiler.snapshot("initial")
    
    # Setup database
    db = QueueDatabase(db_path)
    db.initialize_schema()
    profiler.snapshot("db_initialized")
    
    # Register handler
    registry = get_global_registry()
    registry.register_handler("memory_test", memory_intensive_handler, "Memory test handler")
    
    try:
        # Enqueue tasks
        with db.transaction() as conn:
            for i in range(num_tasks):
                conn.execute(
                    """
                    INSERT INTO task_queue (type, payload, priority, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("memory_test", json.dumps({"size": 10}), 100, "queued")
                )
        profiler.snapshot("tasks_enqueued")
        
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
        profiler.snapshot("workers_created")
        
        # Process tasks
        async def run_worker(worker):
            while True:
                claimed = await asyncio.to_thread(worker.claim_and_process)
                if not claimed:
                    await asyncio.sleep(0.01)
                    claimed = await asyncio.to_thread(worker.claim_and_process)
                    if not claimed:
                        break
        
        # Take snapshots during processing
        async def monitor():
            for i in range(10):
                await asyncio.sleep(0.5)
                profiler.snapshot(f"processing_{i}")
        
        await asyncio.gather(
            *[run_worker(w) for w in workers],
            monitor()
        )
        
        profiler.snapshot("processing_complete")
        
        # Clean up
        del workers
        gc.collect()
        profiler.snapshot("gc_complete")
        
        return profiler.get_stats()
        
    finally:
        reset_global_registry()
        db.close()


async def run_memory_profiling() -> Dict[str, Any]:
    """
    Run complete memory profiling suite.
    
    Returns:
        Dictionary with all profiling results
    """
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "profiles": []
    }
    
    print("=" * 70)
    print("MEMORY PROFILING")
    print("=" * 70)
    
    # Test 1: Worker lifecycle
    print("\n1. Worker Lifecycle Profile")
    print("   Testing memory usage through 5 worker start/stop cycles...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "profile.db")
        lifecycle_result = await profile_worker_lifecycle(db_path, num_cycles=5)
        lifecycle_result["profile_name"] = "worker_lifecycle"
        results["profiles"].append(lifecycle_result)
        
        print(f"   Initial Memory: {lifecycle_result['initial_rss_mb']:.2f} MB")
        print(f"   Final Memory:   {lifecycle_result['final_rss_mb']:.2f} MB")
        print(f"   Peak Memory:    {lifecycle_result['peak_rss_mb']:.2f} MB")
        print(f"   Growth:         {lifecycle_result['growth_mb']:.2f} MB")
        
        # Check for memory leaks
        growth_per_cycle = lifecycle_result['growth_mb'] / 5
        if growth_per_cycle > 5.0:
            print(f"   ⚠️  Potential memory leak: {growth_per_cycle:.2f} MB per cycle")
        else:
            print(f"   ✅ Memory growth acceptable: {growth_per_cycle:.2f} MB per cycle")
    
    # Test 2: Concurrent workers
    print("\n2. Concurrent Workers Profile")
    print("   Testing memory usage with 10 concurrent workers...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "profile.db")
        concurrent_result = await profile_concurrent_workers(db_path, num_workers=10, num_tasks=500)
        concurrent_result["profile_name"] = "concurrent_workers"
        results["profiles"].append(concurrent_result)
        
        print(f"   Initial Memory: {concurrent_result['initial_rss_mb']:.2f} MB")
        print(f"   Final Memory:   {concurrent_result['final_rss_mb']:.2f} MB")
        print(f"   Peak Memory:    {concurrent_result['peak_rss_mb']:.2f} MB")
        print(f"   Growth:         {concurrent_result['growth_mb']:.2f} MB")
        
        if concurrent_result['growth_mb'] > 50.0:
            print(f"   ⚠️  High memory usage: {concurrent_result['growth_mb']:.2f} MB")
        else:
            print(f"   ✅ Memory usage acceptable")
    
    print("\n" + "=" * 70)
    print("MEMORY PROFILING SUMMARY")
    print("=" * 70)
    
    print("\nMemory Usage by Profile:")
    for profile in results["profiles"]:
        print(f"\n{profile['profile_name']}:")
        print(f"  Initial:  {profile['initial_rss_mb']:.2f} MB")
        print(f"  Peak:     {profile['peak_rss_mb']:.2f} MB")
        print(f"  Final:    {profile['final_rss_mb']:.2f} MB")
        print(f"  Growth:   {profile['growth_mb']:.2f} MB")
    
    return results


if __name__ == "__main__":
    # Run profiling
    results = asyncio.run(run_memory_profiling())
    
    # Save results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"memory_profile_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
