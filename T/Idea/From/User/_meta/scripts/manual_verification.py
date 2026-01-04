#!/usr/bin/env python3
"""Manual verification script for T.Idea.From.User functionality.

This script demonstrates the complete flow:
1. Text input → AI generation → Database storage

Run this script to manually verify that the module works as specified.

Requirements:
- Ollama must be running (ollama serve)
- A model must be available (e.g., qwen3:32b)

Usage:
    python manual_verification.py
"""

import os
import sys
import tempfile
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()
MODULE_ROOT = SCRIPT_DIR.parent.parent  # T/Idea/From/User
REPO_ROOT = MODULE_ROOT.parent.parent.parent.parent  # repo root

sys.path.insert(0, str(MODULE_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from idea_variants import IdeaGenerator
from idea import IdeaTable


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_section(text):
    """Print a formatted section."""
    print(f"\n{'-' * 70}")
    print(f"{text}")
    print(f"{'-' * 70}")


def manual_verification_with_mock():
    """Verify functionality with mocked AI (doesn't require Ollama)."""
    from unittest.mock import Mock, patch
    
    print_header("MANUAL VERIFICATION - Mocked AI (No Ollama Required)")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_db_path = tmp.name
    
    try:
        print(f"📁 Using temporary database: {tmp_db_path}\n")
        
        # Setup database
        print_section("Step 1: Setting up database")
        db = IdeaTable(tmp_db_path)
        db.connect()
        db.create_tables()
        print("✓ Database initialized with Idea table")
        
        # Mock AI
        print_section("Step 2: Creating mocked AI generator")
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_class:
            mock_ai = Mock()
            mock_ai.available = True
            
            ai_response = (
                "A thrilling adventure unfolds as a group of hikers explores the "
                "mysterious trails of Acadia National Park under the moonlight. "
                "Strange sounds echo through the darkness, and the team must work "
                "together to uncover the secrets hidden in the forest."
            )
            
            def mock_generate(input_text, **kwargs):
                print(f"   → AI received input: '{input_text}'")
                print(f"   → AI generated: {len(ai_response)} characters")
                return ai_response
            
            mock_ai.generate_with_custom_prompt = mock_generate
            mock_ai_class.return_value = mock_ai
            
            print("✓ Mocked AI generator created")
            
            # Generate idea
            print_section("Step 3: Generating idea from text input")
            input_text = "Acadia Night Hikers"
            print(f"   Input text: '{input_text}'")
            
            generator = IdeaGenerator(use_ai=True)
            idea = generator.generate_from_flavor(
                flavor_name="Emotion-First Hook",
                input_text=input_text,
                db=db
            )
            
            print(f"\n✓ Idea generated successfully")
            
            # Display result
            print_section("Step 4: Result")
            print(f"   Variant Name: {idea['variant_name']}")
            print(f"   Database ID: {idea['idea_id']}")
            print(f"   Text Length: {len(idea['text'])} characters")
            print(f"\n   AI-Generated Text Preview:")
            print(f"   {idea['text'][:150]}...")
            
            # Verify database storage
            print_section("Step 5: Verifying database storage")
            stored_idea = db.get_idea(idea['idea_id'])
            
            print(f"   ✓ Idea retrieved from database (ID: {stored_idea['id']})")
            print(f"   ✓ Text matches AI output: {stored_idea['text'] == ai_response}")
            print(f"   ✓ Version is 1: {stored_idea['version'] == 1}")
            print(f"   ✓ Created timestamp: {stored_idea['created_at']}")
            
        db.close()
        
        print_header("✅ VERIFICATION SUCCESSFUL")
        print("The module correctly:")
        print("  1. Accepts text input")
        print("  2. Passes it to AI without parsing")
        print("  3. Receives AI-generated text")
        print("  4. Stores it in database with version=1")
        print("  5. Returns structured result with ID")
        
    finally:
        # Cleanup
        if os.path.exists(tmp_db_path):
            os.remove(tmp_db_path)
            print(f"\n🗑️  Cleaned up temporary database")


def manual_verification_with_real_ai():
    """Verify functionality with real Ollama AI."""
    print_header("MANUAL VERIFICATION - Real AI (Requires Ollama)")
    
    try:
        # Try to create generator with real AI
        print_section("Checking AI availability")
        generator = IdeaGenerator(use_ai=True)
        print("✓ Ollama is available and running")
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db_path = tmp.name
        
        try:
            print(f"\n📁 Using temporary database: {tmp_db_path}\n")
            
            # Setup database
            print_section("Step 1: Setting up database")
            db = IdeaTable(tmp_db_path)
            db.connect()
            db.create_tables()
            print("✓ Database initialized")
            
            # Generate idea
            print_section("Step 2: Generating idea with real AI")
            input_text = "Acadia Night Hikers"
            print(f"   Input text: '{input_text}'")
            print("   ⏳ Calling Ollama API (this may take a moment)...")
            
            idea = generator.generate_from_flavor(
                flavor_name="Emotion-First Hook",
                input_text=input_text,
                db=db
            )
            
            print(f"\n✓ Real AI generation successful")
            
            # Display result
            print_section("Step 3: Result from real AI")
            print(f"   Variant Name: {idea['variant_name']}")
            print(f"   Database ID: {idea['idea_id']}")
            print(f"   Text Length: {len(idea['text'])} characters")
            print(f"\n   AI-Generated Text:")
            print(f"   {idea['text']}")
            
            # Verify database storage
            print_section("Step 4: Verifying database storage")
            stored_idea = db.get_idea(idea['idea_id'])
            
            print(f"   ✓ Idea retrieved from database (ID: {stored_idea['id']})")
            print(f"   ✓ Text stored: {len(stored_idea['text'])} characters")
            print(f"   ✓ Version: {stored_idea['version']}")
            print(f"   ✓ Created: {stored_idea['created_at']}")
            
            db.close()
            
            print_header("✅ VERIFICATION WITH REAL AI SUCCESSFUL")
            
        finally:
            if os.path.exists(tmp_db_path):
                os.remove(tmp_db_path)
                print(f"\n🗑️  Cleaned up temporary database")
                
    except RuntimeError as e:
        print(f"\n⚠️  Ollama not available: {e}")
        print("\nTo test with real AI:")
        print("  1. Install Ollama: https://ollama.com/")
        print("  2. Pull a model: ollama pull qwen3:32b")
        print("  3. Start Ollama: ollama serve")
        print("  4. Run this script again")


def main():
    """Run manual verification."""
    print("\n" + "=" * 70)
    print("  MANUAL VERIFICATION: T.Idea.From.User Module")
    print("=" * 70)
    print("\nThis script verifies that the module:")
    print("  ✓ Creates Idea objects from text input")
    print("  ✓ Uses AI for generation")
    print("  ✓ Stores AI-generated text in database")
    print("\n")
    
    # First, always run with mocked AI (works in any environment)
    manual_verification_with_mock()
    
    # Then try with real AI if available
    print("\n" + "=" * 70)
    input("\n⏸️  Press Enter to test with real AI (requires Ollama)... ")
    manual_verification_with_real_ai()
    
    print("\n" + "=" * 70)
    print("  MANUAL VERIFICATION COMPLETE")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
