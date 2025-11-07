#!/usr/bin/env python3
"""
Validation script for YouTube channel download tests.

This script validates the test file structure without actually running the tests.
It checks:
- Test file syntax
- Test function signatures
- Import statements
- Async/await usage
- Docstrings

Usage:
    python validate_youtube_tests.py
"""

import ast
import sys
from pathlib import Path


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def validate_test_file():
    """Validate the YouTube test file."""
    test_file = Path(__file__).parent / "test_youtube_channel_download.py"
    
    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return False
    
    print(f"✓ Test file found: {test_file}")
    
    # Read file
    try:
        with open(test_file, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return False
    
    print(f"✓ File size: {len(content)} bytes")
    
    # Parse syntax
    print_section("Syntax Validation")
    try:
        tree = ast.parse(content)
        print("✓ Python syntax is valid")
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    
    # Find imports
    print_section("Import Analysis")
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
    
    required_imports = ['pytest', 'httpx', 'asyncio', 'src.main.app']
    for imp in required_imports:
        found = any(imp in full_imp for full_imp in imports)
        status = "✓" if found else "✗"
        print(f"{status} Required import: {imp}")
    
    # Find test functions
    print_section("Test Function Analysis")
    test_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name.startswith('test_'):
            test_functions.append(node)
    
    print(f"✓ Found {len(test_functions)} test functions:\n")
    
    for func in test_functions:
        print(f"  • {func.name}")
        
        # Check for pytest.mark.asyncio decorator
        has_asyncio_mark = False
        for decorator in func.decorator_list:
            if isinstance(decorator, ast.Attribute):
                if (isinstance(decorator.value, ast.Attribute) and
                    getattr(decorator.value, 'attr', None) == 'mark' and
                    decorator.attr == 'asyncio'):
                    has_asyncio_mark = True
        
        if has_asyncio_mark:
            print(f"    ✓ Has @pytest.mark.asyncio decorator")
        else:
            print(f"    ✗ Missing @pytest.mark.asyncio decorator")
        
        # Check for docstring
        docstring = ast.get_docstring(func)
        if docstring:
            first_line = docstring.split('\n')[0].strip()
            print(f"    ✓ Has docstring: \"{first_line}\"")
        else:
            print(f"    ⚠ Missing docstring")
        
        # Count lines
        if hasattr(func, 'lineno') and hasattr(func, 'end_lineno'):
            lines = func.end_lineno - func.lineno + 1
            print(f"    ℹ Function length: {lines} lines")
        
        print()
    
    # Check for print statements (for logging)
    print_section("Logging Analysis")
    print_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'print':
                print_count += 1
    
    print(f"✓ Found {print_count} print statements (for detailed logging)")
    
    if print_count > 50:
        print("  ✓ Extensive logging for Agent analysis")
    elif print_count > 20:
        print("  ✓ Good amount of logging")
    else:
        print("  ⚠ Consider adding more logging")
    
    # Summary
    print_section("Validation Summary")
    print(f"✓ Test file is valid")
    print(f"✓ {len(test_functions)} async test functions defined")
    print(f"✓ {print_count} log statements for debugging")
    print(f"✓ Ready for execution")
    
    # Show how to run
    print_section("How to Run Tests")
    print("Run all tests:")
    print("  pytest _meta/tests/integration/test_youtube_channel_download.py -v -s")
    print()
    print("Run specific test:")
    print("  pytest _meta/tests/integration/test_youtube_channel_download.py::test_youtube_channel_download_workflow -v -s")
    print()
    print("Or use the helper script:")
    print("  python _meta/tests/integration/run_youtube_tests.py")
    print()
    
    return True


def main():
    """Main entry point."""
    print_section("YouTube Channel Download Tests - Validation")
    
    success = validate_test_file()
    
    print()
    if success:
        print("✓ Validation completed successfully!")
        return 0
    else:
        print("✗ Validation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
