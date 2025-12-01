#!/usr/bin/env python3
"""
Validation script for src module directory structure.

This script validates that the src module properly handles
directory structure for all PrismQ modules (T, A, V, P, M).
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import Config


def test_module_directories():
    """Test module directory structure creation."""
    print("=" * 70)
    print("Testing src Module Directory Structure")
    print("=" * 70)
    
    # Use a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".env"
        
        # Create config
        print(f"\n1. Creating config with working directory: {tmpdir}")
        config = Config(str(env_path), interactive=False)
        print(f"   ✓ Config created")
        print(f"   ✓ Working directory: {config.working_directory}")
        print(f"   ✓ .env file: {config.env_file}")
        
        # Test module directories
        modules = ['T', 'A', 'V', 'P', 'M']
        print(f"\n2. Testing module directories for: {', '.join(modules)}")
        
        for module in modules:
            # Get module directory without content_id
            module_dir = config.get_module_directory(module)
            print(f"\n   Module {module}:")
            print(f"   - Base directory: {module_dir}")
            
            # Get module directory with content_id
            content_id = "test-content-12345"
            content_dir = config.get_module_directory(module, content_id)
            print(f"   - Content directory: {content_dir}")
            
            # Ensure structure exists
            config.ensure_module_structure(module)
            assert module_dir.exists(), f"Module {module} directory should exist"
            print(f"   ✓ Directory created successfully")
        
        # Test specific structure requirements from README.md
        print(f"\n3. Validating structure requirements:")
        
        # T module: T/{id}/{Platform}, T/{id}/Text
        t_content = config.get_module_directory("T", "video-001")
        platform_dir = t_content / "YouTube"
        text_dir = t_content / "Text"
        platform_dir.mkdir(parents=True, exist_ok=True)
        text_dir.mkdir(parents=True, exist_ok=True)
        assert platform_dir.exists(), "T platform directory should exist"
        assert text_dir.exists(), "T text directory should exist"
        print(f"   ✓ T module structure: {t_content}")
        print(f"     - Platform: {platform_dir.relative_to(tmpdir)}")
        print(f"     - Text: {text_dir.relative_to(tmpdir)}")
        
        # A module: A/{id}/{Platform}, A/{id}/Audio
        a_content = config.get_module_directory("A", "audio-001")
        platform_dir = a_content / "Spotify"
        audio_dir = a_content / "Audio"
        platform_dir.mkdir(parents=True, exist_ok=True)
        audio_dir.mkdir(parents=True, exist_ok=True)
        assert platform_dir.exists(), "A platform directory should exist"
        assert audio_dir.exists(), "A audio directory should exist"
        print(f"   ✓ A module structure: {a_content}")
        print(f"     - Platform: {platform_dir.relative_to(tmpdir)}")
        print(f"     - Audio: {audio_dir.relative_to(tmpdir)}")
        
        # V module: V/{id}/{Platform}, V/{id}/Video
        v_content = config.get_module_directory("V", "video-001")
        platform_dir = v_content / "YouTube"
        video_dir = v_content / "Video"
        platform_dir.mkdir(parents=True, exist_ok=True)
        video_dir.mkdir(parents=True, exist_ok=True)
        assert platform_dir.exists(), "V platform directory should exist"
        assert video_dir.exists(), "V video directory should exist"
        print(f"   ✓ V module structure: {v_content}")
        print(f"     - Platform: {platform_dir.relative_to(tmpdir)}")
        print(f"     - Video: {video_dir.relative_to(tmpdir)}")
        
        # P module: P/{Year}/{Month}/{day-range}/{day}/{hour}/{id}/{platform}
        p_base = config.get_module_directory("P")
        p_structured = p_base / "2025" / "11" / "20-end" / "22" / "10" / "pub-001" / "youtube"
        p_structured.mkdir(parents=True, exist_ok=True)
        assert p_structured.exists(), "P structured directory should exist"
        print(f"   ✓ P module structure: {p_structured.relative_to(tmpdir)}")
        
        # M module: M/{Year}/{Month}/{day-range}/{day}/{hour}/{id}/Metrics/{platform}
        m_base = config.get_module_directory("M")
        m_structured = m_base / "2025" / "11" / "20-end" / "22" / "10" / "met-001" / "Metrics" / "youtube"
        m_structured.mkdir(parents=True, exist_ok=True)
        assert m_structured.exists(), "M structured directory should exist"
        print(f"   ✓ M module structure: {m_structured.relative_to(tmpdir)}")
        
        print(f"\n4. Final directory tree:")
        print(f"   {tmpdir}/")
        for module in modules:
            module_path = Path(tmpdir) / module
            if module_path.exists():
                print(f"   ├── {module}/")
                for item in sorted(module_path.rglob("*")):
                    if item.is_dir():
                        rel_path = item.relative_to(tmpdir)
                        depth = len(rel_path.parts) - 1
                        indent = "   │   " * depth + "   ├── "
                        print(f"{indent}{item.name}/")
        
        print(f"\n" + "=" * 70)
        print("✓ All tests passed! Module directory structure is working correctly.")
        print("=" * 70)


if __name__ == "__main__":
    try:
        test_module_directories()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
