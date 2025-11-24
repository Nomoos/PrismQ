"""Example usage of Story ExpertReview module.

This example demonstrates how to use the ExpertReview module to perform
expert-level assessment of a complete story (title + script + audience context).
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

from T.Story.ExpertReview import (
    review_story_with_gpt,
    review_story_to_json,
    get_expert_feedback,
    ReviewDecision
)
import json


def example_basic_review():
    """Example: Basic expert review of a story."""
    print("="*70)
    print("Example 1: Basic Expert Review")
    print("="*70 + "\n")
    
    title = "The Midnight Visitor: A Choice That Echoes"
    
    script = """Have you ever wondered if your choices really matter?
    
At exactly midnight, Emma receives a visitor.
It's herself - from ten years in the future.

"I came to warn you," Future Emma says.
"The choice you make tomorrow will change everything."

But there's a problem.
Future Emma can't remember what the choice was.
Time has stolen that memory from her.

Emma has 24 hours to figure out which decision will alter her life.
Every choice suddenly feels critical.
Should she answer that call? Take that job? Say those words?

As midnight approaches again, she realizes the truth:
It's not about making the perfect choice.
It's about living with the ones you make.

Future Emma fades with a smile.
"You'll be okay. We always are."
"""
    
    audience_context = {
        "demographic": "US female 14-29",
        "platform": "YouTube shorts",
        "style": "thought-provoking sci-fi",
        "duration": "60 seconds"
    }
    
    original_idea = "A sci-fi story about meeting your future self and learning about choices"
    
    # Perform expert review
    review = review_story_with_gpt(
        title=title,
        script=script,
        audience_context=audience_context,
        original_idea=original_idea,
        story_id="example-001",
        story_version="v3",
        publish_threshold=95
    )
    
    # Display results
    print(f"Title: {title}\n")
    print(f"Story ID: {review.story_id}")
    print(f"Version: {review.story_version}")
    print(f"Reviewed by: {review.reviewer_id}")
    print(f"\nQuality Score: {review.overall_assessment.quality_score}/100")
    print(f"Confidence: {review.overall_assessment.confidence}%")
    print(f"Ready for Publishing: {review.overall_assessment.ready_for_publishing}")
    print(f"Decision: {review.decision.value.upper()}")
    
    print(f"\n{'='*70}")
    print("Assessment Breakdown:")
    print(f"{'='*70}")
    print(f"Story Coherence: {review.story_coherence.score}/100")
    print(f"  - {review.story_coherence.feedback}")
    print(f"\nAudience Fit: {review.audience_fit.score}/100")
    print(f"  - {review.audience_fit.feedback}")
    print(f"\nProfessional Quality: {review.professional_quality.score}/100")
    print(f"  - {review.professional_quality.feedback}")
    print(f"\nPlatform Optimization: {review.platform_optimization.score}/100")
    print(f"  - {review.platform_optimization.feedback}")
    
    if review.improvement_suggestions:
        print(f"\n{'='*70}")
        print(f"Improvement Suggestions ({len(review.improvement_suggestions)}):")
        print(f"{'='*70}")
        for i, suggestion in enumerate(review.improvement_suggestions, 1):
            print(f"\n{i}. [{suggestion.priority.value.upper()}] {suggestion.component.value.upper()}")
            print(f"   {suggestion.suggestion}")
            print(f"   Impact: {suggestion.impact}")
            print(f"   Effort: {suggestion.estimated_effort.value}")


def example_workflow_integration():
    """Example: Using expert review in the workflow."""
    print("\n" + "="*70)
    print("Example 2: Workflow Integration")
    print("="*70 + "\n")
    
    title = "The Last Library: Where Stories Never Die"
    
    script = """In a world where books are illegal, one library remains.
    
Maya is the last librarian.
She protects thousands of forbidden stories in an underground vault.

The government knows she exists.
They just can't find her.

Each night, Maya reads to those brave enough to visit.
In the darkness, words become weapons of hope.

But tonight is different.
Someone has betrayed her location.

As footsteps echo down the tunnel, Maya makes a choice:
Destroy the books to hide the evidence?
Or let them be found - and let the stories spread?

She opens every book, one by one.
Not to destroy them.
To memorize them.

"They can burn the pages," she whispers.
"But they can't burn what's in our minds."

The stories live on.
"""
    
    audience_context = {
        "demographic": "US female 14-29",
        "platform": "YouTube shorts",
        "style": "dystopian drama"
    }
    
    # Perform review
    review = review_story_with_gpt(
        title=title,
        script=script,
        audience_context=audience_context,
        story_id="workflow-001",
        story_version="v4",
        publish_threshold=95
    )
    
    # Get workflow feedback
    feedback = get_expert_feedback(review)
    
    print(f"Story: {feedback['story_id']}")
    print(f"Quality Score: {feedback['quality_score']}/100")
    print(f"Decision: {feedback['decision'].upper()}")
    print(f"\nNext Action: {feedback['next_action']}")
    
    # Handle workflow decision
    if feedback['decision'] == 'publish':
        print("\n✅ Story is ready for publishing!")
        print("   Proceeding to Stage 23: Publishing.Finalization")
    else:
        print("\n⚠️  Story needs expert polish")
        print("   Proceeding to Stage 22: Story.Polish")
        
        if feedback['high_priority_suggestions']:
            print("\n   High Priority Improvements:")
            for suggestion in feedback['high_priority_suggestions']:
                print(f"   - [{suggestion['component'].upper()}] {suggestion['suggestion']}")
        
        if feedback['small_effort_suggestions']:
            print("\n   Quick Wins (Small Effort):")
            for suggestion in feedback['small_effort_suggestions']:
                print(f"   - {suggestion['suggestion']}")


def example_json_output():
    """Example: Getting JSON output for API integration."""
    print("\n" + "="*70)
    print("Example 3: JSON Output for API Integration")
    print("="*70 + "\n")
    
    title = "The Algorithm Knows: But Should You Listen?"
    script = "A short story about AI and human intuition."
    
    # Get JSON output
    json_result = review_story_to_json(
        title=title,
        script=script,
        audience_context={"platform": "YouTube"},
        story_id="json-001",
        story_version="v2"
    )
    
    print("JSON Output:")
    print(json_result)
    
    # Parse and use
    result_dict = json.loads(json_result)
    print(f"\n\nParsed Results:")
    print(f"Story ID: {result_dict['story_id']}")
    print(f"Decision: {result_dict['decision']}")
    
    if 'overall_assessment' in result_dict:
        print(f"Quality Score: {result_dict['overall_assessment']['quality_score']}")


def example_filtering_suggestions():
    """Example: Filtering and prioritizing improvement suggestions."""
    print("\n" + "="*70)
    print("Example 4: Filtering Improvement Suggestions")
    print("="*70 + "\n")
    
    review = review_story_with_gpt(
        title="Test Story",
        script="Short test script",
        audience_context={},
        story_id="filter-001",
        publish_threshold=98  # High threshold to trigger suggestions
    )
    
    print(f"Total Suggestions: {len(review.improvement_suggestions)}")
    
    # Get high-priority suggestions
    high_priority = review.get_high_priority_suggestions()
    print(f"\nHigh Priority Suggestions: {len(high_priority)}")
    for suggestion in high_priority:
        print(f"  - [{suggestion.component.value}] {suggestion.suggestion}")
    
    # Get small effort suggestions (quick wins)
    small_effort = review.get_small_effort_suggestions()
    print(f"\nSmall Effort Suggestions (Quick Wins): {len(small_effort)}")
    for suggestion in small_effort:
        print(f"  - {suggestion.suggestion}")
    
    # Get suggestions by component
    from T.Story.ExpertReview import ComponentType
    
    title_suggestions = review.get_suggestions_by_component(ComponentType.TITLE)
    print(f"\nTitle Improvements: {len(title_suggestions)}")
    for suggestion in title_suggestions:
        print(f"  - {suggestion.suggestion}")
    
    script_suggestions = review.get_suggestions_by_component(ComponentType.SCRIPT)
    print(f"\nScript Improvements: {len(script_suggestions)}")
    for suggestion in script_suggestions:
        print(f"  - {suggestion.suggestion}")


def example_custom_threshold():
    """Example: Using custom publish threshold."""
    print("\n" + "="*70)
    print("Example 5: Custom Publish Threshold")
    print("="*70 + "\n")
    
    title = "Mystery of the Missing Memories"
    script = "A psychological thriller about selective amnesia."
    
    # Try with different thresholds
    thresholds = [90, 95, 98]
    
    for threshold in thresholds:
        review = review_story_with_gpt(
            title=title,
            script=script,
            audience_context={"platform": "YouTube"},
            story_id=f"threshold-{threshold}",
            publish_threshold=threshold
        )
        
        print(f"\nThreshold: {threshold}")
        print(f"Quality Score: {review.overall_assessment.quality_score}")
        print(f"Decision: {review.decision.value}")
        print(f"Ready: {review.overall_assessment.ready_for_publishing}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PrismQ.T.Story.ExpertReview - Usage Examples")
    print("="*70 + "\n")
    
    # Run examples
    example_basic_review()
    example_workflow_integration()
    example_json_output()
    example_filtering_suggestions()
    example_custom_threshold()
    
    print("\n" + "="*70)
    print("Examples completed successfully!")
    print("="*70 + "\n")
