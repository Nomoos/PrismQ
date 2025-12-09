"""Integration tests for Scoring and Classification CLI batch processing."""

import json
import subprocess
import sys
from pathlib import Path

# Add Model to path
model_dir = Path(__file__).parent.parent.parent / "Model"
sys.path.insert(0, str(model_dir))

from idea_inspiration import ContentType, IdeaInspiration


def test_scoring_cli_integration():
    """Test Scoring CLI with actual subprocess call."""
    print("Testing Scoring CLI integration...")

    # Create test data
    test_ideas = [
        IdeaInspiration(
            title="Test Article 1",
            description="First test article",
            content="This is test content for the first article.",
            keywords=["test", "article"],
            source_type=ContentType.TEXT,
            score=None,
        ),
        IdeaInspiration(
            title="Test Article 2",
            description="Second test article",
            content="This is test content for the second article.",
            keywords=["test", "article"],
            source_type=ContentType.TEXT,
            score=None,
        ),
    ]

    # Convert to JSON
    input_json = json.dumps([idea.to_dict() for idea in test_ideas])

    # Run CLI
    scoring_cli = Path(__file__).parent.parent.parent / "Scoring" / "src" / "cli.py"
    result = subprocess.run(
        [sys.executable, str(scoring_cli)], input=input_json, capture_output=True, text=True
    )

    assert result.returncode == 0, f"CLI failed with: {result.stderr}"

    # Parse output
    output_lines = [line for line in result.stdout.split("\n") if not line.startswith("2025-")]
    output_json = "\n".join(output_lines)
    output_data = json.loads(output_json)

    assert len(output_data) == 2
    assert all("score" in item and item["score"] is not None for item in output_data)
    assert all(0 <= item["score"] <= 100 for item in output_data)

    print("  ✓ Scoring CLI integration test passed")
    print(f"    - Processed {len(output_data)} items")
    print(f"    - Scores: {[item['score'] for item in output_data]}")


def test_classification_cli_integration():
    """Test Classification CLI with actual subprocess call."""
    print("\nTesting Classification CLI integration...")

    # Create test data
    test_ideas = [
        IdeaInspiration(
            title="My Story",
            description="A personal story",
            content="This happened to me...",
            keywords=["story"],
            source_type=ContentType.TEXT,
            category=None,
        ),
        IdeaInspiration(
            title="Funny Meme",
            description="Hilarious content",
            content="Check this out...",
            keywords=["funny", "meme"],
            source_type=ContentType.VIDEO,
            category=None,
        ),
    ]

    # Convert to JSON
    input_json = json.dumps([idea.to_dict() for idea in test_ideas])

    # Run CLI
    classification_cli = Path(__file__).parent.parent.parent / "Classification" / "src" / "cli.py"
    result = subprocess.run(
        [sys.executable, str(classification_cli)], input=input_json, capture_output=True, text=True
    )

    assert result.returncode == 0, f"CLI failed with: {result.stderr}"

    # Parse output
    output_lines = [line for line in result.stdout.split("\n") if not line.startswith("2025-")]
    output_json = "\n".join(output_lines)
    output_data = json.loads(output_json)

    assert len(output_data) == 2
    assert all("category" in item and item["category"] is not None for item in output_data)

    print("  ✓ Classification CLI integration test passed")
    print(f"    - Processed {len(output_data)} items")
    print(f"    - Categories: {[item['category'] for item in output_data]}")


def test_combined_workflow():
    """Test combined workflow: Classification -> Scoring."""
    print("\nTesting combined workflow (Classification -> Scoring)...")

    # Create test data
    test_ideas = [
        IdeaInspiration(
            title="My Personal AITA Story",
            description="This happened yesterday",
            content="I need to tell you about something that happened...",
            keywords=["aita", "story"],
            source_type=ContentType.TEXT,
            score=None,
            category=None,
        )
    ]

    input_json = json.dumps([idea.to_dict() for idea in test_ideas])

    # Step 1: Classification
    classification_cli = Path(__file__).parent.parent.parent / "Classification" / "src" / "cli.py"
    result1 = subprocess.run(
        [sys.executable, str(classification_cli)], input=input_json, capture_output=True, text=True
    )

    assert result1.returncode == 0

    # Parse classification output
    output_lines1 = [line for line in result1.stdout.split("\n") if not line.startswith("2025-")]
    classified_json = "\n".join(output_lines1)

    # Step 2: Scoring
    scoring_cli = Path(__file__).parent.parent.parent / "Scoring" / "src" / "cli.py"
    result2 = subprocess.run(
        [sys.executable, str(scoring_cli)], input=classified_json, capture_output=True, text=True
    )

    assert result2.returncode == 0

    # Parse final output
    output_lines2 = [line for line in result2.stdout.split("\n") if not line.startswith("2025-")]
    final_json = "\n".join(output_lines2)
    final_data = json.loads(final_json)

    assert len(final_data) == 1
    assert final_data[0]["category"] is not None
    assert final_data[0]["score"] is not None
    assert final_data[0]["category"] == "Storytelling"

    print("  ✓ Combined workflow test passed")
    print(f"    - Category: {final_data[0]['category']}")
    print(f"    - Score: {final_data[0]['score']}")
    print(f"    - Subcategories: {list(final_data[0]['subcategory_relevance'].keys())[:5]}")


if __name__ == "__main__":
    print("Running integration tests for CLI batch processing...\n")

    test_scoring_cli_integration()
    test_classification_cli_integration()
    test_combined_workflow()

    print("\n✓ All integration tests passed!")
