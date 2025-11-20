"""Example usage of Story model for story production workflow.

This example demonstrates the complete story production workflow
from Idea to published content, particularly optimized for Reddit stories.
"""

import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../Idea/Model/src'))

from story import Story, StoryState, StoryStatus
from story_db import StoryDatabase
from idea import Idea, ContentGenre


def example_reddit_story_workflow():
    """Complete Reddit story production workflow with quality gates."""
    print("=" * 70)
    print("REDDIT STORY PRODUCTION WORKFLOW WITH QUALITY GATES")
    print("=" * 70)
    
    # Step 1: Create an Idea for a Reddit story
    print("\n1. Creating Idea for Reddit story...")
    idea = Idea(
        title="AITA: Family Won't Support My Career Change to Art",
        concept="Person wants to quit accounting to become tattoo artist, family threatens to disown",
        premise="After 5 years as a CPA, I'm miserable. I've been taking tattoo apprenticeship classes. "
                "I told my parents I'm quitting to pursue tattooing full-time. They exploded.",
        logline="A burned-out accountant must choose between family approval and artistic passion",
        hook="I (25F) told my family I'm quitting accounting to become a tattoo artist and they want to disown me. AITA?",
        skeleton="Hook → Background → Decision Reveal → Family Reaction → Escalation → Current Dilemma → AITA Question",
        target_platforms=["reddit", "tiktok", "youtube_shorts"],
        target_formats=["text", "video"],
        genre=ContentGenre.ENTERTAINMENT,
        keywords=["AITA", "family drama", "career change", "tattoo artist"],
        themes=["personal freedom", "family expectations", "following passion"]
    )
    print(f"   Created Idea: {idea.title}")
    
    # Step 2: Create Story from Idea
    print("\n2. Creating Story from Idea...")
    story = Story.from_idea(idea, created_by="writer_team")
    print(f"   Story created: {story.title}")
    print(f"   Initial state: {story.state.value}")
    print(f"   Status: {story.status.value}")
    
    # Step 3: Idea Review and Development
    print("\n3. Reviewing and developing Idea...")
    
    print("   → IDEA_REVIEW")
    story.transition_to(StoryState.IDEA_REVIEW)
    print(f"     Status: {story.status.value}")
    
    print("   → OUTLINE")
    story.transition_to(StoryState.OUTLINE)
    
    print("   → TITLE_DRAFT")
    story.transition_to(StoryState.TITLE_DRAFT)
    story.script_title = "AITA for choosing my dream career over family approval?"
    print(f"     Initial title: {story.script_title}")
    
    # Step 4: Script Creation
    print("\n4. Creating script...")
    
    print("   → SCRIPT_DRAFT")
    story.transition_to(StoryState.SCRIPT_DRAFT)
    story.script_text = """
I (25F) told my family I'm quitting accounting to become a tattoo artist and they want to disown me. AITA?

I've been a CPA for five years. On paper, I'm successful - good salary, stable career, respect. 
But I'm miserable. Every day feels like slowly dying inside.

For the past year, I've been taking tattoo apprenticeship classes on weekends. I discovered I'm 
actually good at it. Really good. My instructor says I have natural talent and could build a 
successful career.

Last week, I finally told my parents. I showed them my portfolio, explained my plan. They completely 
lost it. My mom started crying. My dad called me ungrateful and said I'm "throwing away their 
investment" in my education. They said tattooing is "low-class" and I'm embarrassing the family.

Now they've uninvited me from family events until I "come to my senses." My sister (the doctor) 
called me selfish. Extended family is messaging me about "wasting my potential."

I love my family, but I can't keep doing work that makes me want to cry every morning. My friends 
say I should follow my passion. But maybe I am being selfish?

AITA for choosing my dream career over family approval?
""".strip()
    print(f"     Script length: {len(story.script_text)} characters")
    print(f"     Status: {story.status.value}")
    
    # Step 5: Quality Review Pipeline
    print("\n5. Going through quality review pipeline...")
    
    print("   → CONTENT_REVIEW")
    story.transition_to(StoryState.CONTENT_REVIEW)
    
    print("   → EDITING")
    story.transition_to(StoryState.EDITING)
    
    print("   → GRAMMAR_REVIEW")
    story.transition_to(StoryState.GRAMMAR_REVIEW)
    print(f"     Status: {story.status.value}")
    
    print("   → CONSISTENCY_CHECK")
    story.transition_to(StoryState.CONSISTENCY_CHECK)
    
    print("   → TONE_CHECK")
    story.transition_to(StoryState.TONE_CHECK)
    
    print("   → READABILITY_REVIEW")
    story.transition_to(StoryState.READABILITY_REVIEW)
    print("     All quality gates passed!")
    
    # Step 6: Finalization
    print("\n6. Finalizing for publication...")
    
    print("   → FINALIZATION")
    story.transition_to(StoryState.FINALIZATION)
    print(f"     Status: {story.status.value}")
    
    print("   → TITLE_OPTIMIZATION")
    story.transition_to(StoryState.TITLE_OPTIMIZATION)
    story.script_title = "AITA for Choosing My Dream Career Over Family Approval? 💔"
    print(f"     Optimized title: {story.script_title}")
    
    # Step 7: Publishing
    print("\n7. Publishing to Reddit...")
    
    print("   → PUBLISHING")
    story.published_text_url = "https://reddit.com/r/AmItheAsshole/comments/abc123/aita_for_choosing_dream_career"
    story.transition_to(StoryState.PUBLISHING)
    print(f"     Published at: {story.published_text_url}")
    print(f"     Status: {story.status.value}")
    
    # Step 8: Archive
    print("\n8. Completing workflow...")
    print("   → ARCHIVED")
    story.transition_to(StoryState.ARCHIVED, notes="Story production complete")
    print(f"     Final status: {story.status.value}")
    
    # Display story summary
    print("\n" + "=" * 70)
    print("STORY SUMMARY")
    print("=" * 70)
    print(f"Title: {story.title}")
    print(f"Idea ID: {story.idea_id}")
    print(f"Final State: {story.state.value}")
    print(f"Final Status: {story.status.value}")
    print(f"\nPublished Content:")
    print(f"  - Text: {story.published_text_url}")
    print(f"\nState Transitions: {len(story.state_history)}")
    
    # Show state history
    print("\nState History:")
    for i, entry in enumerate(story.state_history, 1):
        print(f"  {i}. {entry['state']}")
        if entry.get('notes'):
            print(f"     Note: {entry['notes']}")
    
    return story


def example_with_improvements_loop():
    """Workflow demonstrating improvement loop."""
    print("\n" + "=" * 70)
    print("WORKFLOW WITH IMPROVEMENT LOOP")
    print("=" * 70)
    
    # Create idea
    idea = Idea(
        title="Story Needing Revisions",
        concept="Example showing revision workflow"
    )
    
    # Create and progress story
    story = Story.from_idea(idea)
    
    # Progress to grammar review
    story.transition_to(StoryState.IDEA_REVIEW)
    story.transition_to(StoryState.OUTLINE)
    story.transition_to(StoryState.TITLE_DRAFT)
    story.transition_to(StoryState.SCRIPT_DRAFT)
    story.script_text = "Initial script with issues..."
    story.transition_to(StoryState.CONTENT_REVIEW)
    story.transition_to(StoryState.EDITING)
    story.transition_to(StoryState.GRAMMAR_REVIEW)
    
    print("Found grammar issues - routing to ScriptImprovements...")
    story.transition_to(StoryState.SCRIPT_IMPROVEMENTS, notes="Grammar issues found")
    
    print("Looping back to Editing for fixes...")
    story.transition_to(StoryState.EDITING)
    
    # Continue through pipeline
    story.transition_to(StoryState.GRAMMAR_REVIEW)
    story.transition_to(StoryState.CONSISTENCY_CHECK)
    story.transition_to(StoryState.TONE_CHECK)
    story.transition_to(StoryState.READABILITY_REVIEW)
    story.transition_to(StoryState.FINALIZATION)
    story.transition_to(StoryState.TITLE_OPTIMIZATION)
    story.transition_to(StoryState.PUBLISHING)
    story.transition_to(StoryState.ARCHIVED)
    
    print(f"Story '{story.title}' completed with improvement loop")
    print(f"Total transitions: {len(story.state_history)}")


def example_database_operations():
    """Demonstrate database operations."""
    print("\n" + "=" * 70)
    print("DATABASE OPERATIONS")
    print("=" * 70)
    
    # Create temporary database
    db = StoryDatabase("example_stories.db")
    db.connect()
    print("Database connected")
    
    # Create some stories
    idea1 = Idea(title="Story 1", concept="Concept 1")
    story1 = Story.from_idea(idea1)
    story1.transition_to(StoryState.IDEA_REVIEW)
    
    idea2 = Idea(title="Story 2", concept="Concept 2")
    story2 = Story.from_idea(idea2)
    story2.transition_to(StoryState.IDEA_REVIEW)
    story2.transition_to(StoryState.OUTLINE)
    story2.transition_to(StoryState.TITLE_DRAFT)
    story2.transition_to(StoryState.SCRIPT_DRAFT)
    
    # Insert stories
    id1 = db.insert_story(story1.to_dict())
    id2 = db.insert_story(story2.to_dict())
    print(f"\nInserted story 1 with ID: {id1}")
    print(f"Inserted story 2 with ID: {id2}")
    
    # Query by state
    drafts = db.get_stories_by_state(StoryState.SCRIPT_DRAFT)
    print(f"\nStories in SCRIPT_DRAFT state: {len(drafts)}")
    
    # Query by status
    in_dev = db.get_stories_by_status(StoryStatus.IN_DEVELOPMENT)
    print(f"Stories in IN_DEVELOPMENT status: {len(in_dev)}")
    
    # Update story
    story1.transition_to(StoryState.OUTLINE)
    db.update_story(id1, story1.to_dict())
    print(f"\nUpdated story 1 to state: {story1.state.value}")
    
    # Clean up
    db.close()
    print("\nDatabase closed")


def example_state_transitions():
    """Demonstrate state transition validation."""
    print("\n" + "=" * 70)
    print("STATE TRANSITION VALIDATION")
    print("=" * 70)
    
    story = Story(title="Test Story", idea_id="test_1")
    
    print(f"\nCurrent state: {story.state.value}")
    print(f"Valid transitions: {[s.value for s in story.get_valid_transitions()]}")
    
    # Check if transition is valid
    print(f"\nCan transition to IDEA_REVIEW? {story.can_transition_to(StoryState.IDEA_REVIEW)}")
    print(f"Can transition to PUBLISHING? {story.can_transition_to(StoryState.PUBLISHING)}")
    
    # Try invalid transition
    print("\nAttempting invalid transition...")
    try:
        story.transition_to(StoryState.PUBLISHING)
    except ValueError as e:
        print(f"Error (expected): {e}")
    
    # Valid transition
    print("\nPerforming valid transition...")
    story.transition_to(StoryState.IDEA_REVIEW)
    print(f"New state: {story.state.value}")
    print(f"Valid transitions: {[s.value for s in story.get_valid_transitions()]}")


if __name__ == "__main__":
    # Run all examples
    
    # Main Reddit story workflow
    story = example_reddit_story_workflow()
    
    # Workflow with improvements loop
    example_with_improvements_loop()
    
    # Database operations
    example_database_operations()
    
    # State transitions
    example_state_transitions()
    
    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)
