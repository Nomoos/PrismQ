#!/usr/bin/env python3
"""
Comprehensive test script to verify the general startup infrastructure works after merge.

Tests both:
1. General startup module (src/startup.py) - reusable across all scripts
2. Step 04 specific ai_config.py - works with Step 04 implementation
"""

import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))

def test_general_startup_module():
    """Test the general startup module (src/startup.py)."""
    print("\n" + "=" * 70)
    print("TEST 1: General Startup Module (src/startup.py)")
    print("=" * 70)
    
    try:
        # Test new pattern (recommended)
        from src.startup import create_startup_config, StartupConfig, AISettings
        print("✓ Imports successful (new pattern)")
        
        # Create config (composition root)
        config = create_startup_config()
        print("✓ Created StartupConfig via factory")
        
        # Test database path
        db_path = config.get_database_path()
        print(f"✓ Database path: {db_path}")
        assert db_path is not None, "Database path should not be None"
        
        # Test AI settings
        ai_settings = config.get_ai_settings()
        print(f"✓ AI Settings: model={ai_settings.model}")
        assert ai_settings.model == "qwen3:32b", f"Expected qwen3:32b, got {ai_settings.model}"
        assert ai_settings.api_base == "http://localhost:11434"
        
        # Test temperature generation
        temp1 = ai_settings.get_random_temperature()
        temp2 = ai_settings.get_random_temperature()
        print(f"✓ Random temperatures: {temp1:.3f}, {temp2:.3f}")
        assert 0.6 <= temp1 <= 0.8, f"Temperature should be between 0.6 and 0.8, got {temp1}"
        assert 0.6 <= temp2 <= 0.8, f"Temperature should be between 0.6 and 0.8, got {temp2}"
        
        # Test complete config
        model, temp, api = config.get_ai_config()
        print(f"✓ Full Config: model={model}, temp={temp:.3f}, api={api}")
        assert model == "qwen3:32b"
        assert 0.6 <= temp <= 0.8
        assert api == "http://localhost:11434"
        
        # Test Ollama availability (explicit, not at import)
        ollama_available = config.check_ollama_available()
        print(f"✓ Ollama check (explicit): {ollama_available} (expected False in CI)")
        assert isinstance(ollama_available, bool), "Should return boolean"
        
        # Test manual instantiation (DI pattern)
        custom_ai = AISettings(model="test-model", api_base="http://test:9999")
        custom_config = StartupConfig(
            database_path="/test/db.s3db",
            ai_settings=custom_ai
        )
        print(f"✓ Custom config (DI): db={custom_config.get_database_path()}, model={custom_config.get_ai_settings().model}")
        
        # Test backward compatibility functions
        from src.startup import (
            get_database_path,
            get_local_ai_model,
            get_local_ai_temperature,
            get_local_ai_config
        )
        print("✓ Backward compatibility imports successful")
        
        db_path_old = get_database_path()
        model_old = get_local_ai_model()
        temp_old = get_local_ai_temperature()
        print(f"✓ Old functions work: db={db_path_old is not None}, model={model_old}, temp={temp_old:.3f}")
        
        print("\n✅ General Startup Module: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ General Startup Module: TEST FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_step04_ai_config():
    """Test Step 04 specific AI config module."""
    print("\n" + "=" * 70)
    print("TEST 2: Step 04 AI Config Module (T/Content/From/Idea/Title/src/ai_config.py)")
    print("=" * 70)
    
    try:
        # Add Step 04 src to path (updated path: Content instead of Script)
        step04_src = REPO_ROOT / "T" / "Content" / "From" / "Idea" / "Title" / "src"
        sys.path.insert(0, str(step04_src))
        
        from ai_config import (
            get_local_ai_model,
            get_local_ai_temperature,
            get_local_ai_api_base,
            get_local_ai_config,
            get_local_ai_timeout
        )
        print("✓ All imports successful")
        
        # Test AI model
        model = get_local_ai_model()
        print(f"✓ AI Model: {model}")
        assert model == "qwen3:32b", f"Expected qwen3:32b, got {model}"
        
        # Test AI temperature
        temp = get_local_ai_temperature()
        print(f"✓ AI Temperature: {temp:.3f}")
        assert 0.6 <= temp <= 0.8, f"Temperature should be between 0.6 and 0.8, got {temp}"
        
        # Test API base
        api_base = get_local_ai_api_base()
        print(f"✓ API Base: {api_base}")
        assert api_base == "http://localhost:11434", f"Expected http://localhost:11434, got {api_base}"
        
        # Test timeout
        timeout = get_local_ai_timeout()
        print(f"✓ Timeout: {timeout}s")
        assert timeout == 120, f"Expected 120, got {timeout}"
        
        # Test complete config (note: different return signature than general module)
        model, api, temp, timeout = get_local_ai_config()
        print(f"✓ Full Config: model={model}, api={api}, temp={temp:.3f}, timeout={timeout}")
        assert model == "qwen3:32b"
        assert 0.6 <= temp <= 0.8
        assert api == "http://localhost:11434"
        assert timeout == 120
        
        # Verify it's using top-level module (check if constants are imported)
        try:
            from ai_config import DEFAULT_AI_MODEL, AISettings
            print(f"✓ Using top-level src.startup module (DEFAULT_AI_MODEL={DEFAULT_AI_MODEL})")
        except ImportError:
            print("⚠ Using fallback implementation (not importing from src.startup)")
        
        print("\n✅ Step 04 AI Config: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Step 04 AI Config: TEST FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_step04_integration():
    """Test Step 04 content_generator integration."""
    print("\n" + "=" * 70)
    print("TEST 3: Step 04 Integration (content_generator, ai_content_generator)")
    print("=" * 70)
    
    try:
        # Add Step 04 src to path (updated path: Content instead of Script)
        step04_src = REPO_ROOT / "T" / "Content" / "From" / "Idea" / "Title" / "src"
        sys.path.insert(0, str(step04_src))
        
        from content_generator import ContentGenerator, ContentGeneratorConfig, ContentV1
        from ai_content_generator import AIContentGenerator, AIContentGeneratorConfig, get_random_seed
        
        print("✓ All imports successful")
        
        # Test ContentGeneratorConfig
        config = ContentGeneratorConfig()
        print(f"✓ ContentGeneratorConfig created")
        print(f"  - target_duration: {config.target_duration_seconds}s")
        print(f"  - max_duration: {config.max_duration_seconds}s")
        print(f"  - audience: {config.audience}")
        
        assert config.target_duration_seconds == 120, "Target duration should be 120s"
        assert config.max_duration_seconds == 175, "Max duration should be 175s"
        assert config.audience["age_range"] == "13-23", "Age range should be 13-23"
        assert config.audience["gender"] == "Female", "Gender should be Female"
        assert config.audience["country"] == "United States", "Country should be United States"
        
        # Test seed variations
        seed = get_random_seed()
        print(f"✓ Random seed: '{seed}'")
        assert isinstance(seed, str), "Seed should be a string"
        assert len(seed) > 0, "Seed should not be empty"
        
        # Test AIContentGeneratorConfig
        ai_config = AIContentGeneratorConfig()
        print(f"✓ AIContentGeneratorConfig created")
        print(f"  - model: {ai_config.model}")
        print(f"  - temperature: {ai_config.temperature}")
        print(f"  - timeout: {ai_config.timeout}")
        
        assert ai_config.model == "qwen3:32b", "Model should be qwen3:32b"
        assert ai_config.temperature == 0.7, "Default temperature should be 0.7"
        assert ai_config.timeout == 120, "Timeout should be 120s"
        
        print("\n✅ Step 04 Integration: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Step 04 Integration: TEST FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE STARTUP INFRASTRUCTURE TEST")
    print("=" * 70)
    print("\nTesting both:")
    print("1. General startup module (src/startup.py) - reusable across all scripts")
    print("2. Step 04 specific implementation (T/Content/From/Idea/Title) - uses top-level module")
    
    results = []
    
    # Run tests
    results.append(("General Startup Module", test_general_startup_module()))
    results.append(("Step 04 AI Config", test_step04_ai_config()))
    results.append(("Step 04 Integration", test_step04_integration()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED - Startup infrastructure works correctly!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Please review errors above")
        return 1


if __name__ == "__main__":
    exit(main())
