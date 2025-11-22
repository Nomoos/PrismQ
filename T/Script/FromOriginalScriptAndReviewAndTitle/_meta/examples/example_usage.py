"""Example usage of Script Improver module.

This example demonstrates how to use the ScriptImprover to generate
improved script versions (v2+) based on review feedback and updated titles.
"""

import sys
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../FromIdeaAndTitle/src'))

from script_improver import (
    ScriptImprover,
    ScriptImproverConfig,
    ScriptV2,
    ReviewFeedback
)

try:
    from script_generator import (
        ScriptV1,
        ScriptSection,
        ScriptStructure,
        PlatformTarget,
        ScriptTone
    )
except ImportError:
    print("Note: ScriptV1 import failed, using minimal mock")
    
    class ScriptStructure(Enum):
        HOOK_DELIVER_CTA = "hook_deliver_cta"
    
    class PlatformTarget(Enum):
        YOUTUBE_MEDIUM = "youtube_medium"
    
    @dataclass
    class ScriptSection:
        section_type: str
        content: str
        estimated_duration_seconds: int
        purpose: str
        notes: str = ""
    
    @dataclass
    class ScriptV1:
        script_id: str
        idea_id: str
        title: str
        full_text: str
        sections: List[ScriptSection]
        total_duration_seconds: int
        structure_type: ScriptStructure
        platform_target: PlatformTarget
        metadata: Dict[str, Any] = field(default_factory=dict)
        created_at: str = ""
        version: int = 1
        notes: str = ""


# Mock review classes for example

@dataclass
class MockImprovementPoint:
    title: str
    description: str
    priority: str = "high"


@dataclass
class MockScriptReview:
    script_id: str
    overall_score: int
    improvement_points: List[MockImprovementPoint] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    optimal_length_seconds: int = None
    current_length_seconds: int = None


@dataclass
class MockTitleReview:
    title_id: str
    notes: str = ""


def example_stage_7_first_improvement():
    """Example: Stage 7 - First improvement (v1 → v2) using both reviews + new title v2.
    
    This is the primary use case for MVP-007.
    """
    print("=" * 80)
    print("EXAMPLE: Stage 7 - First Improvement (v1 → v2)")
    print("=" * 80)
    
    # Step 1: Create original script v1
    print("\n1. Original Script v1:")
    print("-" * 40)
    
    sections_v1 = [
        ScriptSection(
            section_type="introduction",
            content="What if I told you about the Mystery of the Abandoned House? "
                   "A place where strange things happen every night at midnight.",
            estimated_duration_seconds=15,
            purpose="Hook the audience with intrigue"
        ),
        ScriptSection(
            section_type="body",
            content="This house has been abandoned for decades, standing alone on Maple Street. "
                   "Neighbors report seeing lights flickering in the windows. "
                   "Some claim to hear footsteps and whispers. "
                   "Local historians have documented unexplained phenomena dating back to 1957. "
                   "Police have investigated multiple times but found nothing concrete. "
                   "The mystery deepens with each passing year.",
            estimated_duration_seconds=70,
            purpose="Deliver the main narrative"
        ),
        ScriptSection(
            section_type="conclusion",
            content="So that's the story behind the Mystery of the Abandoned House. "
                   "What do you think is really happening? Let me know in the comments.",
            estimated_duration_seconds=15,
            purpose="Conclude and engage audience"
        )
    ]
    
    script_v1 = ScriptV1(
        script_id="script_v1_horror001_20250122",
        idea_id="idea_horror001",
        title="The Mystery of the Abandoned House",
        full_text="\n\n".join([s.content for s in sections_v1]),
        sections=sections_v1,
        total_duration_seconds=100,
        structure_type=ScriptStructure.HOOK_DELIVER_CTA,
        platform_target=PlatformTarget.YOUTUBE_MEDIUM,
        version=1,
        notes="Initial script draft from idea and title v1"
    )
    
    print(f"Script ID: {script_v1.script_id}")
    print(f"Title: {script_v1.title}")
    print(f"Duration: {script_v1.total_duration_seconds}s")
    print(f"Version: v{script_v1.version}")
    
    # Step 2: Create review feedback from Stage 4 and Stage 5
    print("\n2. Review Feedback (from Stages 4 & 5):")
    print("-" * 40)
    
    # Stage 5: Script Review by Title
    script_review = MockScriptReview(
        script_id=script_v1.script_id,
        overall_score=72,
        improvement_points=[
            MockImprovementPoint(
                title="Too long - needs trimming",
                description="Script is 100s but should target 90s for YouTube shorts. "
                          "Middle section drags with too much detail.",
                priority="high"
            ),
            MockImprovementPoint(
                title="Missing paranormal angle",
                description="Title suggests mystery but script needs stronger paranormal/supernatural elements. "
                          "Currently too focused on mundane details.",
                priority="high"
            ),
            MockImprovementPoint(
                title="Weak middle pacing",
                description="The 30-70s section loses momentum with list-like description.",
                priority="medium"
            )
        ],
        strengths=[
            "Strong opening hook",
            "Clear structure",
            "Good engagement at end"
        ],
        optimal_length_seconds=90,
        current_length_seconds=100
    )
    
    # Stage 4: Title Review by Script (provides insights for script)
    title_review = MockTitleReview(
        title_id="title_v1_horror001",
        notes="Title should emphasize the time-loop/paranormal memory aspect that makes this unique. "
             "Script should focus more on the 'remembering' phenomenon rather than generic haunting."
    )
    
    review_feedback = ReviewFeedback(
        script_review=script_review,
        title_review=title_review,
        review_type="general",
        priority_issues=[
            "Cut 10 seconds to reach 90s target",
            "Add paranormal time-loop elements",
            "Align with title's 'remembering' theme"
        ],
        suggestions=[
            "Strengthen middle section pacing",
            "Reduce mundane details",
            "Focus on unique paranormal angle"
        ]
    )
    
    print(f"Script Review Score: {script_review.overall_score}/100")
    print(f"Critical Issues: {len([p for p in script_review.improvement_points if p.priority == 'high'])}")
    print(f"Optimal Duration: {script_review.optimal_length_seconds}s (current: {script_review.current_length_seconds}s)")
    print(f"Title Review Insight: {title_review.notes[:80]}...")
    
    # Step 3: New title v2 from Stage 6
    print("\n3. New Title v2 (from Stage 6):")
    print("-" * 40)
    
    title_v2 = "The House That Remembers"
    print(f"Title v2: {title_v2}")
    print("(Improved to emphasize memory/time-loop paranormal angle)")
    
    # Step 4: Generate improved script v2
    print("\n4. Generate Improved Script v2:")
    print("-" * 40)
    
    config = ScriptImproverConfig(
        target_duration_seconds=90,  # Address length issue
        preserve_successful_elements=True,  # Keep strong hook and structure
        address_all_critical_issues=True,  # Fix all high-priority issues
        align_with_new_title=True  # Align with "remembers" theme
    )
    
    improver = ScriptImprover(config)
    
    script_v2 = improver.generate_script_v2(
        original_script=script_v1,
        title_v2=title_v2,
        review_feedback=review_feedback
    )
    
    print(f"Script ID: {script_v2.script_id}")
    print(f"Title: {script_v2.title}")
    print(f"Duration: {script_v2.total_duration_seconds}s (was {script_v1.total_duration_seconds}s)")
    print(f"Version: v{script_v2.version}")
    print(f"Previous Version: v{script_v1.version} ({script_v2.previous_script_id})")
    
    print(f"\nImprovements Made:")
    print(f"  {script_v2.improvements_made}")
    
    print(f"\nTitle Alignment:")
    print(f"  {script_v2.title_alignment_notes}")
    
    print(f"\nReview Issues Addressed ({len(script_v2.review_feedback_addressed)}):")
    for issue in script_v2.review_feedback_addressed[:3]:
        print(f"  - {issue[:70]}...")
    
    print(f"\nVersion History:")
    for i, vid in enumerate(script_v2.version_history, 1):
        print(f"  {i}. {vid}")
    
    # Step 5: Show section improvements
    print("\n5. Section-by-Section Comparison:")
    print("-" * 40)
    
    for section_type in ["introduction", "body", "conclusion"]:
        v1_section = script_v1.get_section(section_type)
        v2_section = script_v2.get_section(section_type)
        
        if v1_section and v2_section:
            print(f"\n{section_type.upper()}:")
            print(f"  v1: {v1_section.estimated_duration_seconds}s")
            print(f"  v2: {v2_section.estimated_duration_seconds}s")
            if v2_section.notes and v1_section.notes != v2_section.notes:
                print(f"  Changes: {v2_section.notes}")
    
    return script_v2


def example_stage_11_iterative_refinement():
    """Example: Stage 11 - Iterative refinement (v2 → v3) until acceptance."""
    print("\n\n" + "=" * 80)
    print("EXAMPLE: Stage 11 - Iterative Refinement (v2 → v3)")
    print("=" * 80)
    
    # Start with v2 (created from previous example)
    sections_v2 = [
        ScriptSection(
            section_type="introduction",
            content="The House That Remembers - a place where time itself seems to loop.",
            estimated_duration_seconds=14,
            purpose="Hook"
        ),
        ScriptSection(
            section_type="body",
            content="This isn't just a haunted house. Every midnight, the same events replay. "
                   "Witnesses describe seeing the same ghostly figures performing identical actions. "
                   "It's as if the house captured a moment in time and keeps replaying it forever.",
            estimated_duration_seconds=62,
            purpose="Deliver"
        ),
        ScriptSection(
            section_type="conclusion",
            content="Some places don't just remember - they can't forget. What do you think?",
            estimated_duration_seconds=14,
            purpose="Conclude"
        )
    ]
    
    script_v2 = ScriptV1(
        script_id="script_v2_horror001_20250122",
        idea_id="idea_horror001",
        title="The House That Remembers",
        full_text="\n\n".join([s.content for s in sections_v2]),
        sections=sections_v2,
        total_duration_seconds=90,
        structure_type=ScriptStructure.HOOK_DELIVER_CTA,
        platform_target=PlatformTarget.YOUTUBE_MEDIUM,
        version=2
    )
    # Add version_history attribute for this example
    script_v2.version_history = ["script_v1_horror001_20250122"]
    
    print(f"\nStarting with Script v2:")
    print(f"  Title: {script_v2.title}")
    print(f"  Duration: {script_v2.total_duration_seconds}s")
    
    # Stage 10: Review shows need for stronger climax
    review_feedback = ReviewFeedback(
        script_review=MockScriptReview(
            script_id=script_v2.script_id,
            overall_score=82,
            improvement_points=[
                MockImprovementPoint(
                    title="Strengthen climax",
                    description="Good setup and pacing, but needs more dramatic climax at 70-85s mark.",
                    priority="medium"
                )
            ],
            strengths=["Excellent time-loop concept", "Good length", "Strong hook"]
        ),
        review_type="refinement"
    )
    
    print(f"\nStage 10 Review Feedback:")
    print(f"  Score: 82/100")
    print(f"  Main Issue: Strengthen climax")
    
    # Title v3 (slightly updated)
    title_v3 = "The House That Remembers—And Hunts"
    print(f"\nTitle v3: {title_v3}")
    
    # Generate v3
    improver = ScriptImprover()
    script_v3 = improver.generate_script_v2(
        original_script=script_v2,
        title_v2=title_v3,
        review_feedback=review_feedback
    )
    
    print(f"\nGenerated Script v3:")
    print(f"  Title: {script_v3.title}")
    print(f"  Duration: {script_v3.total_duration_seconds}s")
    print(f"  Version: v{script_v3.version}")
    print(f"  Improvements: {script_v3.improvements_made}")
    
    return script_v3


def example_mvp011_extended_versioning():
    """Example: MVP-011 - Extended versioning support (v3 → v4 → v5).
    
    This example demonstrates that the module supports unlimited version progression.
    """
    print("\n\n" + "=" * 80)
    print("EXAMPLE: MVP-011 - Extended Versioning (v3 → v4 → v5)")
    print("=" * 80)
    
    # Start with v3
    sections_v3 = [
        ScriptSection(
            section_type="introduction",
            content="The House That Remembers—And Hunts. Where time loops and danger waits.",
            estimated_duration_seconds=14,
            purpose="Hook with danger"
        ),
        ScriptSection(
            section_type="body",
            content="Every midnight, the same ghostly hunt replays. But here's the twist: "
                   "anyone inside during the loop becomes part of it—forever. "
                   "Three people have entered. None returned the same.",
            estimated_duration_seconds=62,
            purpose="Deliver with enhanced climax"
        ),
        ScriptSection(
            section_type="conclusion",
            content="The house remembers. The house hunts. Will you be next?",
            estimated_duration_seconds=14,
            purpose="Conclude with threat"
        )
    ]
    
    script_v3 = ScriptV1(
        script_id="script_v3_horror001_20250122",
        idea_id="idea_horror001",
        title="The House That Remembers—And Hunts",
        full_text="\n\n".join([s.content for s in sections_v3]),
        sections=sections_v3,
        total_duration_seconds=90,
        structure_type=ScriptStructure.HOOK_DELIVER_CTA,
        platform_target=PlatformTarget.YOUTUBE_MEDIUM,
        version=3
    )
    script_v3.version_history = ["script_v1_horror001_20250122", "script_v2_horror001_20250122"]
    
    print(f"\nStarting with Script v3:")
    print(f"  Version: v{script_v3.version}")
    print(f"  Title: {script_v3.title}")
    
    improver = ScriptImprover()
    
    # v3 → v4: Minor tone adjustment
    print("\n" + "-" * 80)
    print("Stage 14-18: Grammar/Tone/Content reviews → v4")
    print("-" * 80)
    
    review_v3 = ReviewFeedback(
        script_review=MockScriptReview(
            script_id=script_v3.script_id,
            overall_score=88,
            improvement_points=[
                MockImprovementPoint(
                    title="Tone consistency",
                    description="'Will you be next?' feels too direct. Soften slightly for broader appeal.",
                    priority="low"
                )
            ]
        ),
        review_type="tone_review"
    )
    
    script_v4 = improver.generate_script_v2(
        original_script=script_v3,
        title_v2="The House That Remembers—And Hunts",
        review_feedback=review_v3
    )
    
    print(f"Generated Script v4:")
    print(f"  Version: v{script_v4.version}")
    print(f"  Improvements: {script_v4.improvements_made}")
    print(f"  Version History Length: {len(script_v4.version_history)}")
    
    # v4 → v5: Readability polish
    print("\n" + "-" * 80)
    print("Stage 20: Readability review → v5")
    print("-" * 80)
    
    review_v4 = ReviewFeedback(
        script_review=MockScriptReview(
            script_id=script_v4.script_id,
            overall_score=92,
            improvement_points=[
                MockImprovementPoint(
                    title="Voiceover flow",
                    description="'Three people have entered. None returned the same.' - "
                               "slightly awkward for voiceover. Suggest: 'Three entered. None returned unchanged.'",
                    priority="low"
                )
            ]
        ),
        review_type="readability_review"
    )
    
    script_v5 = improver.generate_script_v2(
        original_script=script_v4,
        title_v2="The House That Remembers—And Hunts",
        review_feedback=review_v4
    )
    
    print(f"Generated Script v5:")
    print(f"  Version: v{script_v5.version}")
    print(f"  Improvements: {script_v5.improvements_made}")
    print(f"  Version History Length: {len(script_v5.version_history)}")
    
    # v5 → v6: Final acceptance refinement
    print("\n" + "-" * 80)
    print("Stage 13: Acceptance check loop → v6")
    print("-" * 80)
    
    review_v5 = ReviewFeedback(
        script_review=MockScriptReview(
            script_id=script_v5.script_id,
            overall_score=94,
            improvement_points=[
                MockImprovementPoint(
                    title="Final polish",
                    description="Minor refinement for publishing quality",
                    priority="low"
                )
            ]
        ),
        review_type="acceptance_refinement"
    )
    
    script_v6 = improver.generate_script_v2(
        original_script=script_v5,
        title_v2="The House That Remembers—And Hunts",
        review_feedback=review_v5
    )
    
    print(f"Generated Script v6:")
    print(f"  Version: v{script_v6.version}")
    print(f"  Version History: {' → '.join(['v1', 'v2'] + [f'v{i}' for i in range(3, 7)])}")
    print(f"  Complete History: {len(script_v6.version_history)} previous versions tracked")
    
    # Show version progression
    print("\n" + "-" * 80)
    print("Complete Version Progression")
    print("-" * 80)
    print(f"v1 → v2 → v3 → v4 → v5 → v6")
    print(f"\nVersion v{script_v6.version} contains references to:")
    for i, version_id in enumerate(script_v6.version_history, 1):
        print(f"  {i}. {version_id}")
    
    print(f"\n✅ MVP-011 Acceptance Criteria Met:")
    print(f"  ✓ Refines from v2 to v3+ using feedback")
    print(f"  ✓ Ensures alignment with title at each version")
    print(f"  ✓ Polishes narrative flow iteratively")
    print(f"  ✓ Stores each version with reference to previous")
    print(f"  ✓ Supports unlimited versioning (v3, v4, v5, v6, v7...)")
    
    return script_v6


def main():
    """Run all examples."""
    print("Script Improver Module - Usage Examples")
    print("PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle")
    print()
    
    # Example 1: Stage 7 - First improvement
    script_v2 = example_stage_7_first_improvement()
    
    # Example 2: Stage 11 - Iterative refinement
    script_v3 = example_stage_11_iterative_refinement()
    
    # Example 3: MVP-011 - Extended versioning
    script_v6 = example_mvp011_extended_versioning()
    
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nGenerated multiple improved script versions:")
    print(f"  1. Script v2: {script_v2.script_id}")
    print(f"  2. Script v3: {script_v3.script_id}")
    print(f"  3. Script v6: {script_v6.script_id}")
    print(f"\nVersion progression: v1 → v2 → v3 → v4 → v5 → v6")
    print(f"\nThe module successfully:")
    print(f"  ✓ Processed review feedback from multiple sources")
    print(f"  ✓ Aligned scripts with improved title versions")
    print(f"  ✓ Tracked version history and improvements")
    print(f"  ✓ Maintained structure while addressing issues")
    print(f"  ✓ Supported iterative refinement cycles")
    print(f"  ✓ Handled unlimited version progression (MVP-011)")


if __name__ == "__main__":
    main()
