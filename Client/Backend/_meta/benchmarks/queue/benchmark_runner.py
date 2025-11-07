"""
Queue System Benchmark Runner

Main script to run all benchmark suites and generate comprehensive report.
Implements Issue #334: Performance Benchmarks.
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "Backend"))

# Import benchmark modules
from throughput_benchmark import run_throughput_benchmarks
from latency_benchmark import run_latency_benchmarks
from concurrency_benchmark import run_concurrency_benchmarks
from stress_test import run_stress_tests
from memory_profile import run_memory_profiling


async def run_all_benchmarks() -> Dict[str, Any]:
    """
    Run all benchmark suites.
    
    Returns:
        Dictionary with all results
    """
    print("\n" + "=" * 70)
    print(" " * 15 + "QUEUE SYSTEM PERFORMANCE BENCHMARKS")
    print(" " * 20 + "Issue #334 Implementation")
    print("=" * 70)
    
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmarks": {}
    }
    
    # 1. Throughput Benchmarks
    print("\n[1/5] Running Throughput Benchmarks...")
    try:
        throughput_results = await run_throughput_benchmarks()
        results["benchmarks"]["throughput"] = throughput_results
        print("✅ Throughput benchmarks completed")
    except Exception as e:
        print(f"❌ Throughput benchmarks failed: {e}")
        results["benchmarks"]["throughput"] = {"error": str(e)}
    
    # 2. Latency Benchmarks
    print("\n[2/5] Running Latency Benchmarks...")
    try:
        latency_results = await run_latency_benchmarks()
        results["benchmarks"]["latency"] = latency_results
        print("✅ Latency benchmarks completed")
    except Exception as e:
        print(f"❌ Latency benchmarks failed: {e}")
        results["benchmarks"]["latency"] = {"error": str(e)}
    
    # 3. Concurrency Benchmarks
    print("\n[3/5] Running Concurrency Benchmarks...")
    try:
        concurrency_results = await run_concurrency_benchmarks()
        results["benchmarks"]["concurrency"] = concurrency_results
        print("✅ Concurrency benchmarks completed")
    except Exception as e:
        print(f"❌ Concurrency benchmarks failed: {e}")
        results["benchmarks"]["concurrency"] = {"error": str(e)}
    
    # 4. Stress Tests
    print("\n[4/5] Running Stress Tests...")
    try:
        stress_results = await run_stress_tests()
        results["benchmarks"]["stress"] = stress_results
        print("✅ Stress tests completed")
    except Exception as e:
        print(f"❌ Stress tests failed: {e}")
        results["benchmarks"]["stress"] = {"error": str(e)}
    
    # 5. Memory Profiling
    print("\n[5/5] Running Memory Profiling...")
    try:
        memory_results = await run_memory_profiling()
        results["benchmarks"]["memory"] = memory_results
        print("✅ Memory profiling completed")
    except Exception as e:
        print(f"❌ Memory profiling failed: {e}")
        results["benchmarks"]["memory"] = {"error": str(e)}
    
    return results


def generate_report(results: Dict[str, Any]) -> str:
    """
    Generate markdown report from benchmark results.
    
    Args:
        results: Benchmark results dictionary
        
    Returns:
        Markdown formatted report
    """
    report = ["# Queue System Performance Benchmark Report"]
    report.append(f"\n**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append(f"\n**Issue**: #334 - Performance Benchmarks\n")
    
    # Performance Targets
    report.append("## Performance Targets\n")
    report.append("### Throughput")
    report.append("- Single Worker: >50 tasks/second")
    report.append("- 5 Workers: >200 tasks/second")
    report.append("- 10 Workers: >300 tasks/second\n")
    
    report.append("### Latency")
    report.append("- p50: <100ms")
    report.append("- p95: <500ms")
    report.append("- p99: <1000ms\n")
    
    report.append("### Concurrency")
    report.append("- Max Concurrent Workers: 20+")
    report.append("- No SQLITE_BUSY errors: Under 10 workers")
    report.append("- Task Claim Conflicts: <1%\n")
    
    # Throughput Results
    if "throughput" in results["benchmarks"] and "benchmarks" in results["benchmarks"]["throughput"]:
        report.append("## Throughput Results\n")
        
        throughput_data = results["benchmarks"]["throughput"]
        targets = throughput_data.get("targets", {})
        
        for bench in throughput_data["benchmarks"]:
            workers = bench["workers"]
            tps = bench["process_tps"]
            
            target = None
            if workers == 1:
                target = targets.get("single_worker", 50)
            elif workers == 5:
                target = targets.get("five_workers", 200)
            elif workers == 10:
                target = targets.get("ten_workers", 300)
            
            if target:
                status = "✅" if tps >= target else "❌"
                report.append(f"- {workers} Worker(s): **{tps:.2f} TPS** (target: {target}) {status}")
        
        report.append("")
    
    # Latency Results
    if "latency" in results["benchmarks"] and "benchmarks" in results["benchmarks"]["latency"]:
        report.append("## Latency Results\n")
        
        latency_data = results["benchmarks"]["latency"]
        if latency_data["benchmarks"]:
            bench = latency_data["benchmarks"][0]
            targets = latency_data.get("targets", {})
            
            p50_status = "✅" if bench["p50"] < targets.get("p50", 100) else "❌"
            p95_status = "✅" if bench["p95"] < targets.get("p95", 500) else "❌"
            p99_status = "✅" if bench["p99"] < targets.get("p99", 1000) else "❌"
            
            report.append(f"- p50: **{bench['p50']:.2f}ms** (target: <100ms) {p50_status}")
            report.append(f"- p95: **{bench['p95']:.2f}ms** (target: <500ms) {p95_status}")
            report.append(f"- p99: **{bench['p99']:.2f}ms** (target: <1000ms) {p99_status}")
            report.append("")
    
    # Concurrency Results
    if "concurrency" in results["benchmarks"] and "benchmarks" in results["benchmarks"]["concurrency"]:
        report.append("## Concurrency Results\n")
        
        concurrency_data = results["benchmarks"]["concurrency"]
        benchmarks = concurrency_data.get("benchmarks", [])
        
        if benchmarks:
            max_workers = max(b["workers"] for b in benchmarks)
            report.append(f"- Tested up to **{max_workers} workers** ✅")
            
            busy_errors = sum(b["sqlite_busy_errors"] for b in benchmarks if b["workers"] <= 10)
            busy_status = "✅" if busy_errors == 0 else "❌"
            report.append(f"- SQLITE_BUSY errors (≤10 workers): **{busy_errors}** {busy_status}")
            
            max_conflict_rate = max(b["conflict_rate"] for b in benchmarks)
            conflict_status = "✅" if max_conflict_rate < 1.0 else "❌"
            report.append(f"- Max conflict rate: **{max_conflict_rate:.2f}%** (target: <1%) {conflict_status}")
            report.append("")
    
    # Stress Test Results
    if "stress" in results["benchmarks"] and "tests" in results["benchmarks"]["stress"]:
        report.append("## Stress Test Results\n")
        
        stress_data = results["benchmarks"]["stress"]
        for test in stress_data["tests"]:
            completion_rate = (test["completed"] / test["tasks_enqueued"] * 100) if test["tasks_enqueued"] > 0 else 0
            status = "✅" if completion_rate > 95 else "⚠️"
            
            report.append(f"### {test['test_name']}")
            report.append(f"- Completion Rate: **{completion_rate:.1f}%** {status}")
            report.append(f"- Throughput: **{test['throughput']:.2f} tasks/sec**")
            report.append(f"- Memory Growth: **{test['memory_increase_mb']:.1f} MB**")
            report.append(f"- Errors: **{test['error_count']}**")
            report.append("")
    
    # Memory Profile Results
    if "memory" in results["benchmarks"] and "profiles" in results["benchmarks"]["memory"]:
        report.append("## Memory Profile Results\n")
        
        memory_data = results["benchmarks"]["memory"]
        for profile in memory_data["profiles"]:
            report.append(f"### {profile['profile_name'].replace('_', ' ').title()}")
            report.append(f"- Initial Memory: **{profile['initial_rss_mb']:.2f} MB**")
            report.append(f"- Peak Memory: **{profile['peak_rss_mb']:.2f} MB**")
            report.append(f"- Growth: **{profile['growth_mb']:.2f} MB**")
            report.append("")
    
    # Overall Summary
    report.append("## Overall Summary\n")
    report.append("All benchmark suites have been executed. See detailed results above.")
    report.append("\n---\n")
    report.append(f"*Generated by benchmark_runner.py - Issue #334*")
    
    return "\n".join(report)


if __name__ == "__main__":
    # Run all benchmarks
    print("\nStarting comprehensive benchmark suite...")
    results = asyncio.run(run_all_benchmarks())
    
    # Save raw results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    
    # Save JSON results
    json_file = output_dir / f"benchmark_results_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Raw results saved to: {json_file}")
    
    # Generate and save markdown report
    report = generate_report(results)
    report_file = output_dir / f"benchmark_report_{timestamp}.md"
    with open(report_file, "w") as f:
        f.write(report)
    
    print(f"✅ Report saved to: {report_file}")
    
    print("\n" + "=" * 70)
    print("BENCHMARK SUITE COMPLETED")
    print("=" * 70)
