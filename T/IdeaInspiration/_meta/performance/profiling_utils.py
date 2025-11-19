"""Profiling utilities for PrismQ.IdeaInspiration performance analysis.

This module provides reusable decorators and utilities for profiling CPU usage,
memory consumption, and execution time of Python functions.

Follows SOLID principles:
- Single Responsibility: Each profiler handles one aspect (CPU/memory/time)
- Open/Closed: Easy to extend with new profiler types
- Dependency Inversion: Uses protocols for extensibility
"""

import cProfile
import functools
import io
import pstats
import time
import tracemalloc
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, Any
import psutil


@dataclass
class ProfilingResult:
    """Results from a profiling run."""
    
    function_name: str
    execution_time: float
    cpu_time: Optional[float] = None
    memory_peak: Optional[float] = None
    memory_increase: Optional[float] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class CPUProfiler:
    """CPU profiling using cProfile.
    
    This profiler uses cProfile to collect detailed function call statistics
    including number of calls, time per call, and cumulative time.
    """
    
    def __init__(self, output_dir: str = "reports/cpu"):
        """Initialize CPU profiler.
        
        Args:
            output_dir: Directory to save profiling reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def profile(self, func: Callable, *args, **kwargs) -> tuple[Any, str]:
        """Profile a function call.
        
        Args:
            func: Function to profile
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Tuple of (function result, report path)
        """
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        
        # Generate report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"{func.__name__}_{timestamp}.txt"
        
        with open(report_path, "w") as f:
            stats = pstats.Stats(profiler, stream=f)
            stats.strip_dirs()
            stats.sort_stats("cumulative")
            
            f.write(f"CPU Profile for {func.__name__}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write("=" * 80 + "\n\n")
            
            # Top 50 functions by cumulative time
            f.write("Top 50 functions by cumulative time:\n")
            f.write("-" * 80 + "\n")
            stats.print_stats(50)
            
            f.write("\n\n")
            f.write("Top 30 functions by total time:\n")
            f.write("-" * 80 + "\n")
            stats.sort_stats("tottime")
            stats.print_stats(30)
        
        return result, str(report_path)


class MemoryProfiler:
    """Memory profiling using tracemalloc.
    
    This profiler tracks memory allocation and provides information about
    memory usage, peak consumption, and allocation patterns.
    """
    
    def __init__(self, output_dir: str = "reports/memory"):
        """Initialize memory profiler.
        
        Args:
            output_dir: Directory to save profiling reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def profile(self, func: Callable, *args, **kwargs) -> tuple[Any, str, float, float]:
        """Profile memory usage of a function call.
        
        Args:
            func: Function to profile
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Tuple of:
                - function result (Any)
                - report path (str)
                - peak memory in MB (float)
                - memory increase in MB (float)
        """
        # Get baseline memory
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
        
        # Start tracemalloc
        tracemalloc.start()
        
        result = func(*args, **kwargs)
        
        # Get memory statistics
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - baseline_memory
        
        # Convert bytes to MB
        peak_mb = peak / 1024 / 1024
        
        # Generate report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"{func.__name__}_{timestamp}.txt"
        
        with open(report_path, "w") as f:
            f.write(f"Memory Profile for {func.__name__}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Baseline Memory: {baseline_memory:.2f} MB\n")
            f.write(f"Final Memory: {final_memory:.2f} MB\n")
            f.write(f"Memory Increase: {memory_increase:.2f} MB\n")
            f.write(f"Peak Traced Memory: {peak_mb:.2f} MB\n")
            f.write(f"Current Traced Memory: {current / 1024 / 1024:.2f} MB\n")
        
        return result, str(report_path), peak_mb, memory_increase


class TimeProfiler:
    """Simple execution time profiler.
    
    Measures wall-clock time for function execution.
    """
    
    def __init__(self, output_dir: str = "reports/baseline"):
        """Initialize time profiler.
        
        Args:
            output_dir: Directory to save profiling reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def profile(self, func: Callable, *args, **kwargs) -> tuple[Any, float]:
        """Profile execution time of a function call.
        
        Args:
            func: Function to profile
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Tuple of (function result, execution time in seconds)
        """
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        
        return result, execution_time


def profile_function(
    output_dir: str = "reports/cpu",
    include_memory: bool = False
) -> Callable:
    """Decorator to profile a function's CPU usage.
    
    Args:
        output_dir: Directory to save profiling reports
        include_memory: Whether to also profile memory usage
        
    Returns:
        Decorated function
        
    Example:
        @profile_function(output_dir="reports/cpu")
        def my_function():
            # Your code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cpu_profiler = CPUProfiler(output_dir)
            
            if include_memory:
                mem_profiler = MemoryProfiler(output_dir.replace("cpu", "memory"))
                result, cpu_report = cpu_profiler.profile(func, *args, **kwargs)
                _, mem_report, peak_mb, increase_mb = mem_profiler.profile(func, *args, **kwargs)
                
                print(f"✓ CPU profile saved to: {cpu_report}")
                print(f"✓ Memory profile saved to: {mem_report}")
                print(f"  Peak memory: {peak_mb:.2f} MB")
                print(f"  Memory increase: {increase_mb:.2f} MB")
            else:
                result, cpu_report = cpu_profiler.profile(func, *args, **kwargs)
                print(f"✓ CPU profile saved to: {cpu_report}")
            
            return result
        
        return wrapper
    return decorator


def profile_memory(output_dir: str = "reports/memory") -> Callable:
    """Decorator to profile a function's memory usage.
    
    Args:
        output_dir: Directory to save profiling reports
        
    Returns:
        Decorated function
        
    Example:
        @profile_memory(output_dir="reports/memory")
        def my_function():
            # Your code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler = MemoryProfiler(output_dir)
            result, report_path, peak_mb, increase_mb = profiler.profile(func, *args, **kwargs)
            
            print(f"✓ Memory profile saved to: {report_path}")
            print(f"  Peak memory: {peak_mb:.2f} MB")
            print(f"  Memory increase: {increase_mb:.2f} MB")
            
            return result
        
        return wrapper
    return decorator


def time_function(func: Callable) -> Callable:
    """Decorator to measure function execution time.
    
    Args:
        func: Function to time
        
    Returns:
        Decorated function
        
    Example:
        @time_function
        def my_function():
            # Your code here
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        print(f"⏱️  {func.__name__} took {execution_time:.4f} seconds")
        
        return result
    
    return wrapper
