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
        from src.startup import (
            get_database_path,
            get_local_ai_model,
            get_local_ai_temperature,
            get_local_ai_api_base,
            get_local_ai_config,
            check_ollama_available,
            initialize_environment
        )
        print("✓ All imports successful")
        
        # Test database path
        db_path = get_database_path()
        print(f"✓ Database path: {db_path}")
        assert db_path is not None, "Database path should not be None"
        
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
        
        # Test complete config
        model, temp, api = get_local_ai_config()
        print(f"✓ Full Config: model={model}, temp={temp:.3f}, api={api}")
        assert model == "qwen3:32b"
        assert 0.6 <= temp <= 0.8
        assert api == "http://localhost:11434"
        
        # Test Ollama availability (will be False in CI)
        ollama_available = check_ollama_available()
        print(f"✓ Ollama check: {ollama_available} (expected False in CI)")
        assert isinstance(ollama_available, bool), "Should return boolean"
        
        # Test environment initialization
        config, ai_available = initialize_environment(check_ai=True, interactive=False)
        print(f"✓ Environment initialized: config type={type(config).__name__}, ai_available={ai_available}")
        assert config is not None, "Config should not be None"
        assert isinstance(ai_available, bool), "AI available should be boolean"
        
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
    print("TEST 2: Step 04 AI Config Module (T/Script/From/Idea/Title/src/ai_config.py)")
    print("=" * 70)
    
    try:
        # Add Step 04 src to path
        step04_src = REPO_ROOT / "T" / "Script" / "From" / "Idea" / "Title" / "src"
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
        
        print("\n✅ Step 04 AI Config: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Step 04 AI Config: TEST FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_step04_integration():
    """Test Step 04 script_generator integration."""
    print("\n" + "=" * 70)
    print("TEST 3: Step 04 Integration (script_generator, ai_script_generator)")
    print("=" * 70)
    
    try:
        # Add Step 04 src to path
        step04_src = REPO_ROOT / "T" / "Script" / "From" / "Idea" / "Title" / "src"
        sys.path.insert(0, str(step04_src))
        
        from script_generator import ScriptGenerator, ScriptGeneratorConfig, ScriptV1
        from ai_script_generator import AIScriptGenerator, AIScriptGeneratorConfig, get_random_seed
        
        print("✓ All imports successful")
        
        # Test ScriptGeneratorConfig
        config = ScriptGeneratorConfig()
        print(f"✓ ScriptGeneratorConfig created")
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
        
        # Test AIScriptGeneratorConfig
        ai_config = AIScriptGeneratorConfig()
        print(f"✓ AIScriptGeneratorConfig created")
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
    print("2. Step 04 specific implementation - works with Step 04")
    
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
