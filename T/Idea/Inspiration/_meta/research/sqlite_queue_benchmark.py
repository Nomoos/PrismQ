#!/usr/bin/env python3
"""
SQLite Queue Benchmark Script

Comprehensive benchmarking of SQLite concurrency settings and performance
for the PrismQ task queue system.

Usage:
    python sqlite_queue_benchmark.py [--config CONFIG_NAME] [--workers NUM]
"""

import argparse
import json
import os
import sqlite3
import statistics
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


class QueueBenchmark:
    """Benchmark SQLite queue performance with different configurations."""

    PRAGMA_CONFIGS = {
        "conservative": {
            "journal_mode": "WAL",
            "synchronous": "FULL",
            "busy_timeout": 10000,
            "wal_autocheckpoint": 500,
            "cache_size": -2000,  # 2MB
            "temp_store": "MEMORY",
        },
        "balanced": {
            "journal_mode": "WAL",
            "synchronous": "NORMAL",
            "busy_timeout": 5000,
            "wal_autocheckpoint": 1000,
            "cache_size": -20000,  # 20MB
            "temp_store": "MEMORY",
        },
        "aggressive": {
            "journal_mode": "WAL",
            "synchronous": "NORMAL",
            "busy_timeout": 2000,
            "wal_autocheckpoint": 5000,
            "cache_size": -20000,  # 20MB
            "temp_store": "MEMORY",
            "mmap_size": 134217728,  # 128MB
        },
    }

    def __init__(self, db_path: str, config_name: str = "balanced"):
        """
        Initialize benchmark.

        Args:
            db_path: Path to test database
            config_name: Name of PRAGMA config to use
        """
        self.db_path = db_path
        self.config_name = config_name
        self.config = self.PRAGMA_CONFIGS[config_name]
        self.results = []

    def _init_db(self) -> None:
        """Initialize database with schema and PRAGMAs."""
        conn = sqlite3.connect(self.db_path)
        try:
            # Apply PRAGMA settings
            for pragma, value in self.config.items():
                conn.execute(f"PRAGMA {pragma}={value}")

            # Create task queue table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS task_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    task_type TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'queued',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT
                )
            """
            )

            # Create index
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_status_priority 
                    ON task_queue(status, priority DESC, created_at ASC)
            """
            )

            conn.commit()
        finally:
            conn.close()

    def _measure_operation(self, operation_func, *args) -> Tuple[float, Any]:
        """
        Measure execution time of an operation.

        Returns:
            Tuple of (duration_ms, result)
        """
        start = time.perf_counter()
        result = operation_func(*args)
        duration = (time.perf_counter() - start) * 1000  # Convert to ms
        return duration, result

    def _insert_task(self, conn: sqlite3.Connection, task_id: str, priority: int = 0) -> None:
        """Insert a single task."""
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO task_queue (task_id, task_type, parameters, priority, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (task_id, "test_task", '{"data": "test"}', priority, now, now),
        )
        conn.commit()

    def _claim_task(self, conn: sqlite3.Connection) -> bool:
        """Atomically claim a task."""
        now = datetime.now(timezone.utc).isoformat()

        # Start immediate transaction
        conn.execute("BEGIN IMMEDIATE")
        try:
            # Find highest priority queued task
            cursor = conn.execute(
                """
                SELECT id FROM task_queue 
                WHERE status = 'queued'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """
            )
            row = cursor.fetchone()

            if row:
                task_id = row[0]
                # Claim the task
                conn.execute(
                    """
                    UPDATE task_queue 
                    SET status = 'processing', started_at = ?, updated_at = ?
                    WHERE id = ?
                """,
                    (now, now, task_id),
                )
                conn.commit()
                return True
            else:
                conn.rollback()
                return False
        except Exception:
            conn.rollback()
            raise

    def benchmark_single_writer(self, num_tasks: int = 1000) -> Dict[str, Any]:
        """
        Benchmark single writer performance.

        Args:
            num_tasks: Number of tasks to insert

        Returns:
            Dictionary with benchmark results
        """
        self._init_db()
        conn = sqlite3.connect(self.db_path)

        try:
            # Apply PRAGMAs
            for pragma, value in self.config.items():
                conn.execute(f"PRAGMA {pragma}={value}")

            # Measure insert throughput
            latencies = []
            start_time = time.perf_counter()

            for i in range(num_tasks):
                duration, _ = self._measure_operation(self._insert_task, conn, f"task_{i}", i % 10)
                latencies.append(duration)

            total_time = time.perf_counter() - start_time
            throughput = num_tasks / total_time

            return {
                "scenario": "single_writer",
                "config": self.config_name,
                "num_tasks": num_tasks,
                "total_time_sec": total_time,
                "throughput_tasks_per_sec": throughput,
                "latency_mean_ms": statistics.mean(latencies),
                "latency_median_ms": statistics.median(latencies),
                "latency_p95_ms": self._percentile(latencies, 95),
                "latency_p99_ms": self._percentile(latencies, 99),
                "latency_min_ms": min(latencies),
                "latency_max_ms": max(latencies),
            }
        finally:
            conn.close()

    def benchmark_concurrent_writers(
        self, num_workers: int = 4, tasks_per_worker: int = 250
    ) -> Dict[str, Any]:
        """
        Benchmark concurrent writer performance.

        Args:
            num_workers: Number of concurrent workers
            tasks_per_worker: Tasks each worker will insert

        Returns:
            Dictionary with benchmark results
        """
        self._init_db()

        def worker_insert(worker_id: int) -> Tuple[List[float], int]:
            """Worker function to insert tasks."""
            conn = sqlite3.connect(self.db_path)
            latencies = []
            errors = 0

            try:
                # Apply PRAGMAs
                for pragma, value in self.config.items():
                    conn.execute(f"PRAGMA {pragma}={value}")

                for i in range(tasks_per_worker):
                    try:
                        duration, _ = self._measure_operation(
                            self._insert_task, conn, f"w{worker_id}_task_{i}", i % 10
                        )
                        latencies.append(duration)
                    except sqlite3.OperationalError as e:
                        if "locked" in str(e).lower() or "busy" in str(e).lower():
                            errors += 1
                        else:
                            raise
            finally:
                conn.close()

            return latencies, errors

        # Run concurrent workers
        all_latencies = []
        total_errors = 0
        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker_insert, i) for i in range(num_workers)]

            for future in as_completed(futures):
                latencies, errors = future.result()
                all_latencies.extend(latencies)
                total_errors += errors

        total_time = time.perf_counter() - start_time
        total_tasks = num_workers * tasks_per_worker
        throughput = total_tasks / total_time
        error_rate = (total_errors / total_tasks) * 100 if total_tasks > 0 else 0

        return {
            "scenario": "concurrent_writers",
            "config": self.config_name,
            "num_workers": num_workers,
            "tasks_per_worker": tasks_per_worker,
            "total_tasks": total_tasks,
            "total_time_sec": total_time,
            "throughput_tasks_per_sec": throughput,
            "latency_mean_ms": statistics.mean(all_latencies) if all_latencies else 0,
            "latency_median_ms": statistics.median(all_latencies) if all_latencies else 0,
            "latency_p95_ms": self._percentile(all_latencies, 95) if all_latencies else 0,
            "latency_p99_ms": self._percentile(all_latencies, 99) if all_latencies else 0,
            "total_errors": total_errors,
            "error_rate_percent": error_rate,
        }

    def benchmark_mixed_workload(
        self, num_writers: int = 2, num_claimers: int = 2, duration_sec: int = 10
    ) -> Dict[str, Any]:
        """
        Benchmark mixed read/write workload.

        Args:
            num_writers: Number of concurrent writers
            num_claimers: Number of concurrent task claimers
            duration_sec: How long to run the test

        Returns:
            Dictionary with benchmark results
        """
        self._init_db()

        # Pre-populate with some tasks
        conn = sqlite3.connect(self.db_path)
        try:
            for pragma, value in self.config.items():
                conn.execute(f"PRAGMA {pragma}={value}")

            for i in range(100):
                self._insert_task(conn, f"initial_task_{i}", i % 10)
        finally:
            conn.close()

        stop_time = time.time() + duration_sec
        stats = {
            "writes": 0,
            "claims": 0,
            "write_errors": 0,
            "claim_errors": 0,
        }

        def writer_worker():
            """Continuously write tasks."""
            conn = sqlite3.connect(self.db_path)
            count = 0
            errors = 0
            try:
                for pragma, value in self.config.items():
                    conn.execute(f"PRAGMA {pragma}={value}")

                while time.time() < stop_time:
                    try:
                        self._insert_task(conn, f"runtime_task_{time.time()}_{count}", count % 10)
                        count += 1
                    except sqlite3.OperationalError:
                        errors += 1
            finally:
                conn.close()
            return count, errors

        def claimer_worker():
            """Continuously claim tasks."""
            conn = sqlite3.connect(self.db_path)
            count = 0
            errors = 0
            try:
                for pragma, value in self.config.items():
                    conn.execute(f"PRAGMA {pragma}={value}")

                while time.time() < stop_time:
                    try:
                        if self._claim_task(conn):
                            count += 1
                    except sqlite3.OperationalError:
                        errors += 1
                    time.sleep(0.01)  # Small delay between claims
            finally:
                conn.close()
            return count, errors

        # Run workers
        with ThreadPoolExecutor(max_workers=num_writers + num_claimers) as executor:
            writer_futures = [executor.submit(writer_worker) for _ in range(num_writers)]
            claimer_futures = [executor.submit(claimer_worker) for _ in range(num_claimers)]

            for future in as_completed(writer_futures):
                writes, errors = future.result()
                stats["writes"] += writes
                stats["write_errors"] += errors

            for future in as_completed(claimer_futures):
                claims, errors = future.result()
                stats["claims"] += claims
                stats["claim_errors"] += errors

        return {
            "scenario": "mixed_workload",
            "config": self.config_name,
            "num_writers": num_writers,
            "num_claimers": num_claimers,
            "duration_sec": duration_sec,
            "total_writes": stats["writes"],
            "total_claims": stats["claims"],
            "write_throughput": stats["writes"] / duration_sec,
            "claim_throughput": stats["claims"] / duration_sec,
            "write_errors": stats["write_errors"],
            "claim_errors": stats["claim_errors"],
            "total_errors": stats["write_errors"] + stats["claim_errors"],
        }

    @staticmethod
    def _percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile of a list."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]

    def run_all_benchmarks(self) -> List[Dict[str, Any]]:
        """Run all benchmark scenarios."""
        results = []

        print(f"\n=== Running benchmarks with {self.config_name} configuration ===\n")

        # Scenario 1: Single writer
        print("Running single writer benchmark...")
        results.append(self.benchmark_single_writer(num_tasks=1000))

        # Scenario 2: Concurrent writers (2, 4, 8 workers)
        for num_workers in [2, 4, 8]:
            print(f"Running concurrent writers benchmark ({num_workers} workers)...")
            results.append(
                self.benchmark_concurrent_writers(num_workers=num_workers, tasks_per_worker=250)
            )

        # Scenario 3: Mixed workload
        print("Running mixed workload benchmark...")
        results.append(
            self.benchmark_mixed_workload(num_writers=2, num_claimers=2, duration_sec=10)
        )

        return results


def main():
    """Main benchmark runner."""
    parser = argparse.ArgumentParser(description="SQLite Queue Benchmark")
    parser.add_argument(
        "--config",
        choices=["conservative", "balanced", "aggressive"],
        default="balanced",
        help="PRAGMA configuration to test",
    )
    parser.add_argument(
        "--output", default="benchmark_results.json", help="Output file for results"
    )
    args = parser.parse_args()

    # Create temporary database for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_queue.db")

        # Run benchmarks
        benchmark = QueueBenchmark(db_path, args.config)
        results = benchmark.run_all_benchmarks()

        # Save results
        output_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config": args.config,
            "pragma_settings": benchmark.config,
            "results": results,
        }

        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\n=== Benchmark Complete ===")
        print(f"Results saved to: {args.output}")
        print(f"\nSummary:")
        for result in results:
            print(f"\n{result['scenario']}:")
            if "throughput_tasks_per_sec" in result:
                print(f"  Throughput: {result['throughput_tasks_per_sec']:.2f} tasks/sec")
            if "latency_median_ms" in result:
                print(f"  Median Latency: {result['latency_median_ms']:.2f} ms")
            if "error_rate_percent" in result:
                print(f"  Error Rate: {result['error_rate_percent']:.2f}%")


if __name__ == "__main__":
    main()
