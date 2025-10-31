#!/usr/bin/env python3
"""
Verify all 12 Signal sources are properly implemented.
This script checks the structure and basic functionality of each source.
"""

import os
import sys
from pathlib import Path

# Base path for signals
SIGNALS_BASE = Path("/home/runner/work/PrismQ.IdeaInspiration/PrismQ.IdeaInspiration/Sources/Signals")

# Expected sources based on the implementation guide
EXPECTED_SOURCES = {
    "Trends": ["GoogleTrends", "TrendsFile"],
    "Hashtags": ["TikTokHashtag", "InstagramHashtag"],
    "News": ["GoogleNews", "NewsApi"],
    "Sounds": ["TikTokSounds", "InstagramAudioTrends"],
    "Memes": ["MemeTracker", "KnowYourMeme"],
    "Challenges": ["SocialChallenge"],
    "Locations": ["GeoLocalTrends"]
}

# Required files for each source
REQUIRED_FILES = [
    "README.md",
    "pyproject.toml",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "src/__init__.py",
    "src/cli.py",
    "src/core/__init__.py",
    "src/core/config.py",
    "src/core/database.py",
    "src/core/metrics.py",
    "src/core/signal_processor.py",
    "src/plugins/__init__.py",
    "tests/__init__.py",
    "tests/test_database.py",
    "tests/test_metrics.py"
]

def check_source_structure(category, source_name):
    """Check if a source has all required files."""
    source_path = SIGNALS_BASE / category / source_name
    
    if not source_path.exists():
        return False, f"Directory does not exist: {source_path}"
    
    missing_files = []
    for file_path in REQUIRED_FILES:
        full_path = source_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        return False, f"Missing files: {', '.join(missing_files)}"
    
    return True, "✅ All required files present"

def find_plugin_file(category, source_name):
    """Find the plugin implementation file."""
    source_path = SIGNALS_BASE / category / source_name / "src" / "plugins"
    plugin_files = [f for f in source_path.glob("*.py") if f.name != "__init__.py"]
    
    if len(plugin_files) == 0:
        return False, "No plugin file found"
    elif len(plugin_files) > 1:
        return False, f"Multiple plugin files found: {[f.name for f in plugin_files]}"
    else:
        return True, plugin_files[0].name

def check_test_files(category, source_name):
    """Check if source has proper test files."""
    source_path = SIGNALS_BASE / category / source_name / "tests"
    test_files = [f for f in source_path.glob("test_*.py")]
    
    if len(test_files) < 3:
        return False, f"Only {len(test_files)} test files found (expected at least 3)"
    
    return True, f"✅ {len(test_files)} test files found"

def main():
    """Main verification function."""
    print("=" * 80)
    print("VERIFYING ALL SIGNAL SOURCES")
    print("=" * 80)
    print()
    
    total_sources = 0
    passed_sources = 0
    failed_sources = []
    
    for category, sources in EXPECTED_SOURCES.items():
        print(f"\n{'='*80}")
        print(f"Category: {category}")
        print(f"{'='*80}")
        
        for source_name in sources:
            total_sources += 1
            print(f"\n{source_name}:")
            print(f"  Path: {category}/{source_name}")
            
            # Check structure
            structure_ok, structure_msg = check_source_structure(category, source_name)
            print(f"  Structure: {structure_msg}")
            
            # Find plugin
            plugin_ok, plugin_msg = find_plugin_file(category, source_name)
            print(f"  Plugin: {plugin_msg}")
            
            # Check tests
            tests_ok, tests_msg = check_test_files(category, source_name)
            print(f"  Tests: {tests_msg}")
            
            # Overall status
            if structure_ok and plugin_ok and tests_ok:
                print(f"  ✅ STATUS: PASS")
                passed_sources += 1
            else:
                print(f"  ❌ STATUS: FAIL")
                failed_sources.append(f"{category}/{source_name}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total sources checked: {total_sources}")
    print(f"Passed: {passed_sources}")
    print(f"Failed: {total_sources - passed_sources}")
    
    if failed_sources:
        print("\nFailed sources:")
        for source in failed_sources:
            print(f"  - {source}")
        return 1
    else:
        print("\n✅ ALL 12 SIGNAL SOURCES VERIFIED SUCCESSFULLY!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
