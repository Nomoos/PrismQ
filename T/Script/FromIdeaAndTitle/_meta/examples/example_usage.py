"""Example usage of Script Generator.

This example demonstrates how to use the ScriptGenerator to create
initial script drafts (v1) from ideas and titles.
"""

import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../Model/src'))

from script_generator import (
    ScriptGenerator,
    ScriptGeneratorConfig,
    ScriptStructure,
    PlatformTarget,
    ScriptTone
)

try:
    from idea import Idea, ContentGenre, IdeaStatus
except ImportError:
    print("Note: Running without full Idea model import")
    # Create a simple mock for demonstration
    from dataclasses import dataclass
    from typing import List
    from enum import Enum
    
    class ContentGenre(Enum):
        MYSTERY = "mystery"
        HORROR = "horror"
        EDUCATIONAL = "educational"
    
    @dataclass
    class Idea:
        id: str = "example-001"
        title: str = "Example Idea"
        concept: str = "An example concept"
        premise: str = "Example premise"
        hook: str = "Example hook"
        synopsis: str = "Example synopsis"
        keywords: List[str] = None
        themes: List[str] = None
        genre: ContentGenre = ContentGenre.MYSTERY
        
        def __post_init__(self):
            if self.keywords is None:
                self.keywords = ["mystery", "suspense"]
            if self.themes is None:
                self.themes = ["investigation", "discovery"]


def example_basic_usage():
    """Basic usage example."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Script Generation")
    print("=" * 70)
    
    # Create an idea
    idea = Idea(
        id="mystery-001",
        title="The Abandoned Lighthouse Mystery",
        concept="A lighthouse keeper disappeared 50 years ago, but his light still turns on every night",
        premise="Every night at 9 PM, the abandoned lighthouse illuminates the coast, despite being without power for decades",
        hook="What if the keeper never really left?",
        synopsis="This is a deep dive into one of the coast's most enduring mysteries. "
                 "The lighthouse has been abandoned since 1974, yet locals report seeing its beam "
                 "sweep across the water every single night. We investigate the disappearance, "
                 "the strange phenomena, and what might really be happening.",
        keywords=["lighthouse", "mystery", "paranormal", "disappearance"],
        themes=["mystery", "investigation", "supernatural"],
        genre=ContentGenre.MYSTERY
    )
    
    # Create title
    title = "The Mystery of the Abandoned Lighthouse"
    
    # Generate script
    generator = ScriptGenerator()
    script = generator.generate_script_v1(idea, title)
    
    print(f"\nScript ID: {script.script_id}")
    print(f"Title: {script.title}")
    print(f"Version: {script.version}")
    print(f"Structure: {script.structure_type.value}")
    print(f"Platform: {script.platform_target.value}")
    print(f"Duration: {script.total_duration_seconds} seconds")
    print(f"\nSections ({len(script.sections)}):")
    for section in script.sections:
        print(f"  - {section.section_type}: {section.estimated_duration_seconds}s - {section.purpose}")
    
    print(f"\nFull Script Preview (first 200 chars):")
    print(script.full_text[:200] + "...")
    
    return script


def example_youtube_short():
    """Example for YouTube short format."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: YouTube Short (60 seconds)")
    print("=" * 70)
    
    # Create idea
    idea = Idea(
        id="horror-002",
        title="The 3 AM Challenge",
        concept="What happens when you call your own phone at 3 AM?",
        premise="Urban legend says if you call your own number at 3 AM, someone will answer",
        hook="I tried the 3 AM phone challenge, and someone answered...",
        synopsis="Testing one of the internet's creepiest urban legends about calling your own phone at 3 AM",
        keywords=["horror", "3am", "urban-legend", "paranormal"],
        themes=["horror", "suspense", "investigation"],
        genre=ContentGenre.HORROR
    )
    
    title = "I Called My Own Phone at 3 AM"
    
    # Configure for YouTube short
    config = ScriptGeneratorConfig(
        platform_target=PlatformTarget.YOUTUBE_SHORT,
        target_duration_seconds=60,
        structure_type=ScriptStructure.HOOK_DELIVER_CTA,
        tone=ScriptTone.DRAMATIC
    )
    
    generator = ScriptGenerator(config)
    script = generator.generate_script_v1(idea, title)
    
    print(f"\nScript ID: {script.script_id}")
    print(f"Duration: {script.total_duration_seconds} seconds")
    print(f"Tone: {config.tone}")
    
    print(f"\nSection Breakdown:")
    for section in script.sections:
        print(f"\n[{section.section_type.upper()}] ({section.estimated_duration_seconds}s)")
        print(f"Purpose: {section.purpose}")
        print(f"Content: {section.content[:100]}...")
    
    return script


def example_educational_content():
    """Example for educational content."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Educational Content (Problem-Solution)")
    print("=" * 70)
    
    idea = Idea(
        id="edu-003",
        title="Understanding Quantum Entanglement",
        concept="Explaining quantum entanglement in simple terms",
        premise="Two particles can be connected in such a way that measuring one instantly affects the other, no matter the distance",
        hook="What Einstein called 'spooky action at a distance' might be the key to the future",
        synopsis="A clear explanation of quantum entanglement, breaking down this complex concept into understandable terms",
        keywords=["quantum", "physics", "science", "entanglement"],
        themes=["education", "science", "physics"],
        genre=ContentGenre.EDUCATIONAL
    )
    
    title = "Quantum Entanglement Explained Simply"
    
    config = ScriptGeneratorConfig(
        platform_target=PlatformTarget.YOUTUBE_MEDIUM,
        target_duration_seconds=120,
        structure_type=ScriptStructure.PROBLEM_SOLUTION,
        tone=ScriptTone.EDUCATIONAL,
        include_cta=True
    )
    
    generator = ScriptGenerator(config)
    script = generator.generate_script_v1(idea, title)
    
    print(f"\nScript Structure: {script.structure_type.value}")
    print(f"Duration: {script.total_duration_seconds} seconds")
    
    print(f"\nGenerated Script:")
    print("-" * 70)
    print(script.full_text)
    print("-" * 70)
    
    return script


def example_custom_configuration():
    """Example with custom configuration."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Custom Configuration")
    print("=" * 70)
    
    idea = Idea(
        id="custom-004",
        title="The Future of AI",
        concept="How artificial intelligence will change our daily lives",
        premise="AI is rapidly evolving and will transform every aspect of how we live and work",
        hook="The future is here, and it's more intelligent than you think",
        synopsis="An exploration of AI's impact on society, work, and daily life",
        keywords=["AI", "technology", "future"],
        themes=["technology", "innovation", "future"]
    )
    
    title = "How AI Will Change Everything"
    
    # Custom configuration with overrides
    generator = ScriptGenerator()
    script = generator.generate_script_v1(
        idea=idea,
        title=title,
        platform_target=PlatformTarget.YOUTUBE_MEDIUM,
        target_duration_seconds=150,
        structure_type=ScriptStructure.THREE_ACT,
        tone=ScriptTone.CONVERSATIONAL,
        include_cta=True,
        script_id="custom-ai-script-v1"
    )
    
    print(f"\nCustom Script ID: {script.script_id}")
    print(f"Structure: {script.structure_type.value}")
    print(f"Duration: {script.total_duration_seconds} seconds")
    
    print(f"\nMetadata:")
    for key, value in script.metadata.items():
        print(f"  {key}: {value}")
    
    # Convert to dictionary
    script_dict = script.to_dict()
    print(f"\nExported as dictionary with {len(script_dict)} keys")
    
    return script


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("SCRIPT GENERATOR EXAMPLES")
    print("=" * 70)
    
    # Run examples
    example_basic_usage()
    example_youtube_short()
    example_educational_content()
    example_custom_configuration()
    
    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
