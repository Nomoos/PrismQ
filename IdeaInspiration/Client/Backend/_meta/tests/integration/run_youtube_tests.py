#!/usr/bin/env python3
"""
Quick test runner for YouTube channel download integration tests.

This script helps run the YouTube integration tests and displays
the comprehensive logs for Agent analysis.

Usage:
    python run_youtube_tests.py [test_name]

Examples:
    python run_youtube_tests.py                          # Run all tests
    python run_youtube_tests.py workflow                 # Run workflow test only
    python run_youtube_tests.py error                    # Run error handling test
"""

import sys
import subprocess
from pathlib import Path


def print_banner(text):
    """Print a formatted banner."""
    width = 80
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width + "\n")


def run_test(test_name=None):
    """Run YouTube integration tests."""
    # Change to Backend directory
    backend_dir = Path(__file__).parent.parent.parent.parent
    
    # Build pytest command
    test_file = "_meta/tests/integration/test_youtube_channel_download.py"
    
    if test_name:
        # Map short names to full test names
        test_map = {
            "workflow": "test_youtube_channel_download_workflow",
            "error": "test_youtube_channel_download_error_handling",
            "streaming": "test_youtube_channel_log_streaming",
            "config": "test_youtube_channel_configuration_persistence",
        }
        
        full_test_name = test_map.get(test_name, test_name)
        test_path = f"{test_file}::{full_test_name}"
        print_banner(f"Running test: {full_test_name}")
    else:
        test_path = test_file
        print_banner("Running all YouTube integration tests")
    
    # Run pytest with verbose output and show prints
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",           # Verbose
        "-s",           # Show print statements
        "--tb=short",   # Short traceback
        "--color=yes"   # Colored output
    ]
    
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=backend_dir,
            check=False
        )
        
        if result.returncode == 0:
            print_banner("✓ All tests passed!")
        else:
            print_banner(f"⚠ Tests completed with exit code: {result.returncode}")
            print("\nNote: Some tests may fail if yt-dlp is not installed.")
            print("This is expected behavior and the tests should still verify the workflow.\n")
        
        return result.returncode
    
    except FileNotFoundError:
        print("Error: pytest not found. Please install it with:")
        print("  pip install pytest pytest-asyncio httpx")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def main():
    """Main entry point."""
    print_banner("YouTube Channel Download - Integration Test Runner")
    
    # Parse command line arguments
    test_name = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Show available tests
    if test_name == "help" or test_name == "--help" or test_name == "-h":
        print("Available tests:")
        print("  workflow    - Complete download workflow (comprehensive)")
        print("  error       - Error handling scenarios")
        print("  streaming   - Log streaming/polling")
        print("  config      - Configuration persistence")
        print("\nOr run all tests by not specifying a test name.\n")
        return 0
    
    # Check dependencies
    print("Checking dependencies...")
    missing_deps = []
    
    try:
        import pytest
        print("  ✓ pytest installed")
    except ImportError:
        print("  ✗ pytest not installed")
        missing_deps.append("pytest")
    
    try:
        import httpx
        print("  ✓ httpx installed")
    except ImportError:
        print("  ✗ httpx not installed")
        missing_deps.append("httpx")
    
    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        return 1
    
    print()
    
    # Run tests
    return run_test(test_name)


if __name__ == "__main__":
    sys.exit(main())
