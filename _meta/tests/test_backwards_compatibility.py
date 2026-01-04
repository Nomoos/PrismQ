#!/usr/bin/env python3
"""Test backwards compatibility of AI configuration imports.

This test validates that all existing import patterns continue to work
after fixing the circular import issues in the ai_config wrapper modules.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Go up to PrismQ root
sys.path.insert(0, str(PROJECT_ROOT))


def test_all_import_patterns():
    """Test all possible import patterns for AI configuration."""
    print("\n" + "=" * 70)
    print("BACKWARDS COMPATIBILITY TEST - AI Configuration Imports")
    print("=" * 70)
    
    all_passed = True
    
    # Test 1: Direct import from T.src (foundation level)
    print("\n1. Testing direct import from T.src.ai_config...")
    try:
        from T.src.ai_config import AISettings, create_ai_config, DEFAULT_AI_MODEL
        print(f"   ✓ Import successful")
        print(f"   ✓ DEFAULT_AI_MODEL: {DEFAULT_AI_MODEL}")
        ai = create_ai_config()
        print(f"   ✓ AISettings: {ai}")
        temp = ai.get_random_temperature()
        print(f"   ✓ Random temperature: {temp:.4f}")
        assert 0.6 <= temp <= 0.8, f"Temperature should be between 0.6 and 0.8"
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        all_passed = False
    
    # Test 2: Import from T/Content/src wrapper
    print("\n2. Testing import from T.Content.src.ai_config wrapper...")
    try:
        from T.Content.src.ai_config import AISettings as ContentAISettings
        from T.Content.src.ai_config import create_ai_config as content_create_ai_config
        from T.Content.src.ai_config import DEFAULT_AI_MODEL as CONTENT_MODEL
        print(f"   ✓ Import successful")
        print(f"   ✓ DEFAULT_AI_MODEL: {CONTENT_MODEL}")
        ai = content_create_ai_config()
        print(f"   ✓ AISettings: {ai}")
        temp = ai.get_random_temperature()
        print(f"   ✓ Random temperature: {temp:.4f}")
        assert 0.6 <= temp <= 0.8, f"Temperature should be between 0.6 and 0.8"
        assert CONTENT_MODEL == DEFAULT_AI_MODEL, "Content model should match foundation model"
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        all_passed = False
    
    # Test 3: Import from T/Content/From/Idea/Title/src wrapper (legacy functions)
    print("\n3. Testing import from T.Content.From.Idea.Title.src.ai_config...")
    try:
        # Add Title src to path (as content_generator.py does)
        title_src = PROJECT_ROOT / "T" / "Content" / "From" / "Idea" / "Title" / "src"
        if str(title_src) not in sys.path:
            sys.path.insert(0, str(title_src))
        
        from ai_config import get_local_ai_config, get_local_ai_model
        from ai_config import get_local_ai_api_base, get_local_ai_temperature
        print(f"   ✓ Import successful")
        
        model = get_local_ai_model()
        print(f"   ✓ get_local_ai_model(): {model}")
        assert model == "qwen3:32b", f"Expected qwen3:32b, got {model}"
        
        api = get_local_ai_api_base()
        print(f"   ✓ get_local_ai_api_base(): {api}")
        assert api == "http://localhost:11434", f"Expected http://localhost:11434, got {api}"
        
        temp = get_local_ai_temperature()
        print(f"   ✓ get_local_ai_temperature(): {temp:.4f}")
        assert 0.6 <= temp <= 0.8, f"Temperature should be between 0.6 and 0.8"
        
        ai_model, ai_api_base, ai_temperature, ai_timeout = get_local_ai_config()
        print(f"   ✓ get_local_ai_config(): ({ai_model}, {ai_api_base}, {ai_temperature:.4f}, {ai_timeout})")
        assert ai_model == "qwen3:32b"
        assert ai_api_base == "http://localhost:11434"
        assert 0.6 <= ai_temperature <= 0.8
        assert ai_timeout == 120
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # Test 4: Test that content_generator.py pattern works
    print("\n4. Testing content_generator.py usage pattern...")
    try:
        # Simulate content_generator.py import pattern
        title_src = PROJECT_ROOT / "T" / "Content" / "From" / "Idea" / "Title" / "src"
        if str(title_src) not in sys.path:
            sys.path.insert(0, str(title_src))
        
        # This is the exact pattern used in content_generator.py line 218
        from ai_config import get_local_ai_config
        ai_model, ai_api_base, ai_temperature, ai_timeout = get_local_ai_config()
        
        print(f"   ✓ Import pattern successful")
        print(f"   ✓ ai_model: {ai_model}")
        print(f"   ✓ ai_api_base: {ai_api_base}")
        print(f"   ✓ ai_temperature: {ai_temperature:.4f}")
        print(f"   ✓ ai_timeout: {ai_timeout}")
        
        # Validate values
        assert ai_model == "qwen3:32b"
        assert ai_api_base == "http://localhost:11434"
        assert 0.6 <= ai_temperature <= 0.8
        assert ai_timeout == 120
        print(f"   ✓ All values validated correctly")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL BACKWARDS COMPATIBILITY TESTS PASSED")
        print("=" * 70)
        print("\nAll import patterns work correctly:")
        print("  ✓ Direct import from T.src.ai_config")
        print("  ✓ Import from T.Content.src.ai_config wrapper")
        print("  ✓ Import from T.Content.From.Idea.Title.src.ai_config wrapper")
        print("  ✓ content_generator.py usage pattern")
        print("\nCircular import issues have been successfully fixed!")
    else:
        print("❌ SOME BACKWARDS COMPATIBILITY TESTS FAILED")
        print("=" * 70)
    print()
    
    return all_passed


if __name__ == "__main__":
    success = test_all_import_patterns()
    sys.exit(0 if success else 1)
