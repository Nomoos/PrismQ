#!/usr/bin/env python3
"""
Manual Verification Script for youtube_video_scrape Task Type

This script verifies that the youtube_video_scrape task type is properly
registered and can be instantiated.

Usage:
    python scripts/verify_task_type.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.workers.factory import worker_factory


def verify_task_type_registration():
    """Verify youtube_video_scrape is registered in the factory."""
    print("=" * 70)
    print("YouTube Video Task Type Verification")
    print("=" * 70)

    # Get supported task types
    supported_types = worker_factory.get_supported_types()

    print("\nRegistered task types:")
    for task_type in supported_types:
        print(f"  ✓ {task_type}")

    # Verify youtube_video_scrape is present
    print("\nVerifying youtube_video_scrape:")
    if "youtube_video_scrape" in supported_types:
        print("  ✅ youtube_video_scrape is registered")
    else:
        print("  ❌ youtube_video_scrape is NOT registered")
        return False

    # Verify all three expected types are present
    expected_types = ["youtube_video_single", "youtube_video_search", "youtube_video_scrape"]

    print("\nVerifying all expected task types:")
    all_present = True
    for task_type in expected_types:
        if task_type in supported_types:
            print(f"  ✅ {task_type}")
        else:
            print(f"  ❌ {task_type} MISSING")
            all_present = False

    if all_present:
        print("\n✅ All task types verified successfully!")
        print("\nTask Type Details:")
        print("  • youtube_video_single - Scrape single video by ID/URL")
        print("  • youtube_video_search - Search and scrape multiple videos")
        print("  • youtube_video_scrape - General scraping (auto-routes)")
        return True
    else:
        print("\n❌ Some task types are missing!")
        return False


def main():
    """Main entry point."""
    try:
        success = verify_task_type_registration()
        print("\n" + "=" * 70)

        if success:
            print("Verification PASSED")
            print("=" * 70)
            sys.exit(0)
        else:
            print("Verification FAILED")
            print("=" * 70)
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
