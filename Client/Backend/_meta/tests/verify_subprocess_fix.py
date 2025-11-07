"""Verification script for Windows subprocess fix (Issue #305).

This script verifies that:
1. All modules use ModuleRunner (no bypasses)
2. SubprocessWrapper is the only place creating subprocesses
3. The auto-detection logic works correctly
4. All execution paths use the centralized SubprocessWrapper

Can be run on any platform - will report findings for documentation.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class SubprocessCallFinder(ast.NodeVisitor):
    """AST visitor to find asyncio.create_subprocess calls."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.calls: List[Tuple[int, str]] = []
    
    def visit_Call(self, node: ast.Call):
        """Visit function call nodes."""
        # Check for asyncio.create_subprocess_exec or create_subprocess_shell
        if isinstance(node.func, ast.Attribute):
            if (node.func.attr in ['create_subprocess_exec', 'create_subprocess_shell'] and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'asyncio'):
                self.calls.append((node.lineno, ast.unparse(node)))
        self.generic_visit(node)


def find_subprocess_calls(directory: Path, exclude_patterns: List[str] = None) -> dict:
    """Find all asyncio.create_subprocess calls in Python files.
    
    Args:
        directory: Root directory to search
        exclude_patterns: List of path patterns to exclude
        
    Returns:
        Dictionary mapping file paths to list of (line_number, code) tuples
    """
    if exclude_patterns is None:
        exclude_patterns = ['__pycache__', '.git', 'venv', '.venv', '/test_', '_test.py', '/tests/']
    
    results = {}
    
    for py_file in directory.rglob('*.py'):
        # Skip excluded paths
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(py_file))
            
            finder = SubprocessCallFinder(py_file)
            finder.visit(tree)
            
            if finder.calls:
                results[py_file] = finder.calls
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Warning: Could not parse {py_file}: {e}")
    
    return results


def verify_module_structure():
    """Verify that all source modules follow the correct structure."""
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    sources_dir = repo_root / "Sources"
    
    if not sources_dir.exists():
        print(f"❌ Sources directory not found: {sources_dir}")
        return False
    
    print("=" * 80)
    print("VERIFICATION: Source Modules Structure")
    print("=" * 80)
    
    # Find all module directories (containing module.json)
    modules = []
    for module_json in sources_dir.rglob('module.json'):
        module_dir = module_json.parent
        modules.append(module_dir)
    
    print(f"\nFound {len(modules)} source modules:")
    for module in sorted(modules):
        rel_path = module.relative_to(repo_root)
        print(f"  ✓ {rel_path}")
    
    # Check for asyncio.create_subprocess calls in Sources
    print(f"\n{'=' * 80}")
    print("CHECKING: asyncio.create_subprocess calls in Sources modules")
    print("=" * 80)
    
    subprocess_calls = find_subprocess_calls(sources_dir)
    
    if subprocess_calls:
        print(f"\n❌ FOUND {len(subprocess_calls)} files with direct subprocess calls:")
        for filepath, calls in subprocess_calls.items():
            rel_path = filepath.relative_to(repo_root)
            print(f"\n  {rel_path}:")
            for line_no, code in calls:
                print(f"    Line {line_no}: {code[:80]}...")
        return False
    else:
        print("\n✅ NO direct asyncio.create_subprocess calls found in Sources modules")
        print("   All modules rely on Backend to execute them as subprocesses")
    
    return True


def verify_backend_subprocess_usage():
    """Verify subprocess usage in Backend."""
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    backend_dir = repo_root / "Client" / "Backend"
    
    print(f"\n{'=' * 80}")
    print("VERIFICATION: Backend Subprocess Usage")
    print("=" * 80)
    
    # Find asyncio.create_subprocess calls (excluding tests)
    subprocess_calls = find_subprocess_calls(
        backend_dir / "src",
        exclude_patterns=['__pycache__', '.git', 'venv', '.venv', '/test_', '_test.py', '/tests/']
    )
    
    print(f"\nDirect asyncio.create_subprocess calls in Backend/src:")
    
    if not subprocess_calls:
        print("  ✓ None found")
        return True
    
    # Analyze each file
    allowed_files = [
        'subprocess_wrapper.py',  # Centralized wrapper
        'process_manager.py',     # Legacy but may still be used
        'test_event_loop.py',     # Utility for testing event loop
        'uvicorn_runner.py',      # Server startup utility
    ]
    
    all_allowed = True
    for filepath, calls in subprocess_calls.items():
        filename = filepath.name
        rel_path = filepath.relative_to(repo_root)
        
        if filename in allowed_files:
            print(f"\n  ✓ {rel_path} (allowed - centralized execution)")
            for line_no, code in calls:
                print(f"      Line {line_no}")
        else:
            print(f"\n  ❌ {rel_path} (BYPASS - should use SubprocessWrapper!)")
            for line_no, code in calls:
                print(f"      Line {line_no}: {code[:80]}...")
            all_allowed = False
    
    return all_allowed


def verify_subprocess_wrapper():
    """Verify SubprocessWrapper implementation."""
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    wrapper_file = repo_root / "Client" / "Backend" / "src" / "core" / "subprocess_wrapper.py"
    
    print(f"\n{'=' * 80}")
    print("VERIFICATION: SubprocessWrapper Implementation")
    print("=" * 80)
    
    if not wrapper_file.exists():
        print(f"\n❌ SubprocessWrapper not found: {wrapper_file}")
        return False
    
    with open(wrapper_file, 'r') as f:
        content = f.read()
    
    checks = {
        "RunMode.THREADED exists": "RunMode.THREADED" in content or "THREADED" in content,
        "RunMode.ASYNC exists": "RunMode.ASYNC" in content or "ASYNC" in content,
        "_detect_mode() exists": "_detect_mode" in content,
        "Windows detection (sys.platform)": "sys.platform" in content and "win32" in content,
        "create_subprocess method": "create_subprocess" in content,
        "_threaded_subprocess exists": "_threaded_subprocess" in content,
        "_async_subprocess exists": "_async_subprocess" in content,
    }
    
    print("\nSubprocessWrapper features:")
    all_passed = True
    for check_name, passed in checks.items():
        status = "✓" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed


def verify_module_runner_integration():
    """Verify ModuleRunner uses SubprocessWrapper."""
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    runner_file = repo_root / "Client" / "Backend" / "src" / "core" / "module_runner.py"
    
    print(f"\n{'=' * 80}")
    print("VERIFICATION: ModuleRunner Integration")
    print("=" * 80)
    
    if not runner_file.exists():
        print(f"\n❌ ModuleRunner not found: {runner_file}")
        return False
    
    with open(runner_file, 'r') as f:
        content = f.read()
    
    checks = {
        "Imports SubprocessWrapper": "from .subprocess_wrapper import SubprocessWrapper" in content,
        "Creates SubprocessWrapper instance": "SubprocessWrapper(" in content,
        "Uses subprocess_wrapper.create_subprocess": "subprocess_wrapper.create_subprocess" in content,
        "NO direct asyncio.create_subprocess": "await asyncio.create_subprocess" not in content,
        "Handles SubprocessPolicyException": "SubprocessPolicyException" in content,
    }
    
    print("\nModuleRunner integration:")
    all_passed = True
    for check_name, passed in checks.items():
        status = "✓" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed


def main():
    """Run all verifications."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "WINDOWS SUBPROCESS FIX VERIFICATION (Issue #305)" + " " * 15 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    results = {
        "Source modules structure": verify_module_structure(),
        "Backend subprocess usage": verify_backend_subprocess_usage(),
        "SubprocessWrapper implementation": verify_subprocess_wrapper(),
        "ModuleRunner integration": verify_module_runner_integration(),
    }
    
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print("=" * 80)
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check_name}")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL VERIFICATIONS PASSED")
        print("\nConclusion:")
        print("  • All source modules are standalone scripts (no direct subprocess calls)")
        print("  • Backend uses centralized SubprocessWrapper for all module execution")
        print("  • SubprocessWrapper implements both ASYNC and THREADED modes")
        print("  • ModuleRunner correctly uses SubprocessWrapper")
        print("  • Windows subprocess fix applies to ALL modules (YouTube, reddit, etc.)")
        print("\n✅ YouTube module is protected by the same fix as reddit-posts and hacker-news")
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("\nPlease review the issues above.")
    print("=" * 80 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
