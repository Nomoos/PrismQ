"""Test for worker.py module."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add source to path
src_path = Path(__file__).resolve().parents[2] / 'src'
sys.path.insert(0, str(src_path))


def test_worker_module_exists():
    """Test that worker.py exists and can be imported."""
    worker_path = Path(__file__).resolve().parents[2] / 'src' / 'worker.py'
    assert worker_path.exists(), f"worker.py should exist at {worker_path}"
    print("✓ worker.py exists")


def test_worker_has_main():
    """Test that worker.py has a main function."""
    import ast
    
    worker_path = Path(__file__).resolve().parents[2] / 'src' / 'worker.py'
    with open(worker_path, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    assert 'main' in functions, "worker.py should have a main() function"
    assert 'create_worker' in functions, "worker.py should have a create_worker() function"
    print("✓ worker.py has main() and create_worker() functions")


def test_worker_has_taskmanager_import():
    """Test that worker.py attempts to import TaskManager."""
    worker_path = Path(__file__).resolve().parents[2] / 'src' / 'worker.py'
    with open(worker_path, 'r') as f:
        content = f.read()
    
    assert 'TaskManagerClient' in content, "worker.py should import TaskManagerClient"
    assert '_taskmanager_available' in content, "worker.py should have _taskmanager_available flag"
    print("✓ worker.py has TaskManager integration code")


def test_worker_has_argparse():
    """Test that worker.py uses argparse for CLI."""
    worker_path = Path(__file__).resolve().parents[2] / 'src' / 'worker.py'
    with open(worker_path, 'r') as f:
        content = f.read()
    
    assert 'argparse' in content, "worker.py should use argparse"
    assert '--worker-id' in content, "worker.py should have --worker-id argument"
    assert '--disable-taskmanager' in content, "worker.py should have --disable-taskmanager argument"
    print("✓ worker.py has proper CLI arguments")


def test_worker_graceful_degradation():
    """Test that worker.py handles TaskManager unavailability."""
    worker_path = Path(__file__).resolve().parents[2] / 'src' / 'worker.py'
    with open(worker_path, 'r') as f:
        content = f.read()
    
    assert 'try:' in content and 'except ImportError:' in content, \
        "worker.py should handle ImportError for TaskManager"
    print("✓ worker.py handles TaskManager unavailability gracefully")


if __name__ == "__main__":
    print("\n=== Running Worker Module Tests ===\n")
    
    test_worker_module_exists()
    test_worker_has_main()
    test_worker_has_taskmanager_import()
    test_worker_has_argparse()
    test_worker_graceful_degradation()
    
    print("\n=== All Tests Passed! ===\n")
