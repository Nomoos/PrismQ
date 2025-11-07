#!/usr/bin/env python3
"""Test script to verify Windows event loop policy is correctly set."""

import asyncio
import sys


def test_event_loop_policy():
    """Test that the event loop policy is appropriate for the platform."""
    print(f"Platform: {sys.platform}")
    
    # Get the current event loop policy
    policy = asyncio.get_event_loop_policy()
    print(f"Event loop policy: {type(policy).__name__}")
    
    if sys.platform == 'win32':
        # On Windows, we expect WindowsProactorEventLoopPolicy for subprocess support
        expected_policy = "WindowsProactorEventLoopPolicy"
        actual_policy = type(policy).__name__
        
        if actual_policy == expected_policy:
            print(f"✅ PASS: Windows event loop policy is correctly set to {expected_policy}")
            return True
        else:
            print(f"❌ FAIL: Expected {expected_policy}, got {actual_policy}")
            return False
    else:
        # On Unix-like systems, the default policy should work fine
        print(f"✅ PASS: Non-Windows platform using {type(policy).__name__}")
        return True


async def test_subprocess_creation():
    """Test that subprocess creation works."""
    print("\nTesting subprocess creation...")
    
    try:
        # Try to create a simple subprocess
        process = await asyncio.create_subprocess_exec(
            sys.executable, "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print(f"✅ PASS: Subprocess created successfully")
            print(f"   Python version: {stdout.decode().strip()}")
            return True
        else:
            print(f"❌ FAIL: Subprocess exited with code {process.returncode}")
            return False
            
    except NotImplementedError as e:
        print(f"❌ FAIL: NotImplementedError - {e}")
        print("   This indicates the event loop policy doesn't support subprocesses")
        return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error - {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Event Loop Policy Test")
    print("=" * 60)
    
    # Test 1: Check event loop policy
    policy_ok = test_event_loop_policy()
    
    # Test 2: Try to create a subprocess
    subprocess_ok = await test_subprocess_creation()
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    print(f"Event Loop Policy: {'✅ PASS' if policy_ok else '❌ FAIL'}")
    print(f"Subprocess Creation: {'✅ PASS' if subprocess_ok else '❌ FAIL'}")
    
    if policy_ok and subprocess_ok:
        print("\n🎉 All tests passed! The event loop is properly configured.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    # Set Windows event loop policy if needed (like uvicorn_runner does)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
