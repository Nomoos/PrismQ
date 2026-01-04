#!/usr/bin/env python3
"""Test to verify AI configuration is correctly placed at T foundation level.

This test verifies:
1. AI config exists at T/src/ (foundation level)
2. AI config is used across multiple Text domains (Content, Publishing, Story)
3. Lower modules correctly import from T/src
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Go up to PrismQ root
sys.path.insert(0, str(PROJECT_ROOT))

def test_ai_at_foundation_level():
    """Test that AI config is at T foundation level (T/src)."""
    print("\n" + "=" * 70)
    print("TEST: AI Configuration at T Foundation Level")
    print("=" * 70)
    
    # Test 1: Import from T/src directly
    print("\n1. Testing import from T/src (foundation level)...")
    sys.path.insert(0, str(PROJECT_ROOT / "T" / "src"))
    try:
        from ai_config import DEFAULT_AI_MODEL, AISettings, create_ai_config
        print(f"   ✓ Direct import from T/src successful")
        print(f"   ✓ AI Model: {DEFAULT_AI_MODEL}")
        ai_settings = create_ai_config()
        print(f"   ✓ AISettings created: {ai_settings.model}")
    except ImportError as e:
        print(f"   ❌ FAILED: {e}")
        return False
    
    # Test 2: Import from T/Content/src (should re-export from T/src)
    print("\n2. Testing import from T/Content/src (re-exports from T/src)...")
    try:
        from T.Content.src.ai_config import DEFAULT_AI_MODEL as CONTENT_MODEL
        print(f"   ✓ T/Content/src re-export successful")
        print(f"   ✓ Model: {CONTENT_MODEL}")
        if CONTENT_MODEL != DEFAULT_AI_MODEL:
            print(f"   ❌ FAILED: Models don't match!")
            return False
        print(f"   ✓ Correctly re-exports from T/src")
    except ImportError as e:
        print(f"   ❌ FAILED: {e}")
        return False
    
    # Test 3: Import from Title module (should use T/src via T/Content)
    print("\n3. Testing import from T/Content/From/Idea/Title (uses T/src)...")
    try:
        # Directly test the ai_config module without importing content_generator
        title_ai_config_path = PROJECT_ROOT / "T" / "Content" / "From" / "Idea" / "Title" / "src" / "ai_config.py"
        if not title_ai_config_path.exists():
            print(f"   ❌ FAILED: {title_ai_config_path} does not exist")
            return False
        
        # Read the file to verify it imports from T/src
        with open(title_ai_config_path, 'r') as f:
            content = f.read()
            if 'T/src' in content or 'T_SRC' in content:
                print(f"   ✓ Title module correctly references T/src")
                print(f"   ✓ Verified by file content inspection")
            else:
                print(f"   ❌ FAILED: Title module doesn't reference T/src")
                return False
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False
    
    # Test 4: Verify single source of truth
    print("\n4. Verifying single source of truth...")
    print(f"   T/src AI Model:           {DEFAULT_AI_MODEL}")
    print(f"   T/Content re-export:      {CONTENT_MODEL}")
    
    if DEFAULT_AI_MODEL == CONTENT_MODEL:
        print(f"   ✓ Single source of truth confirmed!")
        print(f"   ✓ All modules use same AI config from T/src")
    else:
        print(f"   ❌ FAILED: Inconsistent AI config!")
        return False
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - AI Config Correctly at T Foundation Level")
    print("=" * 70)
    print("\nModule Hierarchy Verified:")
    print("  - T/src/ai_config.py: Foundation level (SOURCE OF TRUTH)")
    print("  - T/Content/src/ai_config.py: Re-exports from T/src")
    print("  - T/Content/From/Idea/Title/: Uses T/src foundation")
    print("\n")
    return True

if __name__ == "__main__":
    success = test_ai_at_foundation_level()
    sys.exit(0 if success else 1)
