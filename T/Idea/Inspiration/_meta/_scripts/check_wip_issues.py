#!/usr/bin/env python3
"""
Content to check the state of issues in the wip directory.

This script:
1. Scans all issue files in _meta/issues/wip/
2. Extracts status, priority, and other metadata
3. Verifies if issues should still be in WIP or moved to done/
4. Generates a report with recommendations
"""

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class IssueMetadata:
    """Metadata extracted from an issue file."""

    filename: str
    title: str
    issue_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None

    def __str__(self) -> str:
        return (
            f"Issue: {self.filename}\n"
            f"  Title: {self.title}\n"
            f"  Type: {self.issue_type or 'Unknown'}\n"
            f"  Priority: {self.priority or 'Unknown'}\n"
            f"  Status: {self.status or 'Unknown'}\n"
            f"  Category: {self.category or 'N/A'}"
        )


def extract_issue_metadata(filepath: Path) -> IssueMetadata:
    """Extract metadata from an issue markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract title (first # heading)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else filepath.stem

    # Extract metadata fields
    type_match = re.search(r"\*\*Type\*\*:\s*(.+)$", content, re.MULTILINE | re.IGNORECASE)
    priority_match = re.search(r"\*\*Priority\*\*:\s*(.+)$", content, re.MULTILINE | re.IGNORECASE)
    status_match = re.search(r"\*\*Status\*\*:\s*(.+)$", content, re.MULTILINE | re.IGNORECASE)
    category_match = re.search(r"\*\*Category\*\*:\s*(.+)$", content, re.MULTILINE | re.IGNORECASE)

    return IssueMetadata(
        filename=filepath.name,
        title=title,
        issue_type=type_match.group(1).strip() if type_match else None,
        priority=priority_match.group(1).strip() if priority_match else None,
        status=status_match.group(1).strip() if status_match else None,
        category=category_match.group(1).strip() if category_match else None,
    )


def check_completion_status(filepath: Path) -> Dict[str, any]:
    """Check if an issue appears to be completed based on content analysis."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for completion indicators
    has_completed_checklist = bool(re.search(r"- \[x\].*", content))
    has_incomplete_checklist = bool(re.search(r"- \[ \].*", content))

    # Count completed vs incomplete items
    completed_items = len(re.findall(r"- \[x\]", content))
    incomplete_items = len(re.findall(r"- \[ \]", content))
    total_items = completed_items + incomplete_items

    completion_percentage = (completed_items / total_items * 100) if total_items > 0 else 0

    # Check for "COMPLETE" or "DONE" markers
    has_completion_marker = bool(re.search(r"(✅|COMPLETE|DONE|100%)", content, re.IGNORECASE))

    # Check for "IN PROGRESS" or "WIP" markers
    has_wip_marker = bool(
        re.search(r"(🚧|IN PROGRESS|WIP|\d+%\s+complete)", content, re.IGNORECASE)
    )

    return {
        "has_checklist": total_items > 0,
        "completed_items": completed_items,
        "incomplete_items": incomplete_items,
        "total_items": total_items,
        "completion_percentage": completion_percentage,
        "has_completion_marker": has_completion_marker,
        "has_wip_marker": has_wip_marker,
        "appears_complete": (
            has_completion_marker or (total_items > 0 and completion_percentage == 100)
        ),
    }


def generate_recommendations(metadata: IssueMetadata, completion: Dict) -> List[str]:
    """Generate recommendations based on issue analysis."""
    recommendations = []

    # Check for status mismatch
    if metadata.status and metadata.status.lower() in ["done", "complete", "completed"]:
        recommendations.append(
            "⚠️  Status is 'Done' but issue is in WIP folder - SHOULD MOVE TO done/"
        )
    elif metadata.status and metadata.status.lower() == "new":
        recommendations.append(
            "⚠️  Status is 'New' but issue is in WIP folder - update status or move to new/"
        )

    # Check completion indicators
    if completion["appears_complete"]:
        recommendations.append("✅ Issue appears complete - consider moving to done/")

    if completion["has_checklist"] and completion["completion_percentage"] == 100:
        recommendations.append(
            f"✅ All checklist items completed ({completion['completed_items']}/{completion['total_items']}) - consider moving to done/"
        )
    elif completion["has_checklist"] and completion["completion_percentage"] > 0:
        recommendations.append(
            f"🚧 Checklist progress: {completion['completed_items']}/{completion['total_items']} ({completion['completion_percentage']:.1f}%) - actively in progress"
        )

    if not completion["has_wip_marker"] and not completion["appears_complete"]:
        recommendations.append("⚠️  No clear WIP or completion markers found - verify status")

    return recommendations


def main():
    """Main function to check WIP issues."""
    # Find repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    wip_dir = repo_root / "_meta" / "issues" / "wip"

    if not wip_dir.exists():
        print(f"❌ WIP directory not found: {wip_dir}")
        return

    print("=" * 80)
    print("WIP ISSUES STATUS CHECK")
    print(f"Checking directory: {wip_dir}")
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # Get all markdown files (excluding .gitkeep)
    issue_files = [f for f in wip_dir.glob("*.md") if f.name != ".gitkeep"]

    if not issue_files:
        print("📝 No issue files found in WIP directory")
        return

    print(f"Found {len(issue_files)} issue file(s) in WIP\n")

    issues_to_move = []
    issues_in_progress = []
    issues_need_attention = []

    for issue_file in sorted(issue_files):
        print("-" * 80)
        metadata = extract_issue_metadata(issue_file)
        completion = check_completion_status(issue_file)
        recommendations = generate_recommendations(metadata, completion)

        print(metadata)
        print()

        # Print completion status
        if completion["has_checklist"]:
            print(
                f"  Checklist: {completion['completed_items']}/{completion['total_items']} items completed ({completion['completion_percentage']:.1f}%)"
            )
        if completion["has_completion_marker"]:
            print(f"  ✅ Contains completion markers")
        if completion["has_wip_marker"]:
            print(f"  🚧 Contains WIP markers")

        print()

        # Print recommendations
        if recommendations:
            print("  Recommendations:")
            for rec in recommendations:
                print(f"    {rec}")
        else:
            print("  ✓ Issue state appears appropriate for WIP")

        print()

        # Categorize issues
        if completion["appears_complete"] or (
            metadata.status and metadata.status.lower() in ["done", "complete", "completed"]
        ):
            issues_to_move.append(metadata.filename)
        elif completion["has_wip_marker"] or (
            completion["has_checklist"] and completion["incomplete_items"] > 0
        ):
            issues_in_progress.append(metadata.filename)
        else:
            issues_need_attention.append(metadata.filename)

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    if issues_to_move:
        print(f"✅ Issues that should be moved to done/ ({len(issues_to_move)}):")
        for filename in issues_to_move:
            print(f"   - {filename}")
        print()

    if issues_in_progress:
        print(f"🚧 Issues actively in progress ({len(issues_in_progress)}):")
        for filename in issues_in_progress:
            print(f"   - {filename}")
        print()

    if issues_need_attention:
        print(f"⚠️  Issues needing attention/verification ({len(issues_need_attention)}):")
        for filename in issues_need_attention:
            print(f"   - {filename}")
        print()

    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()

    if issues_to_move:
        print("1. Review issues marked for completion")
        print("2. Move completed issues to _meta/issues/done/:")
        for filename in issues_to_move:
            print(f"   git mv _meta/issues/wip/{filename} _meta/issues/done/")
        print()

    if issues_need_attention:
        print("3. Review and update issues needing attention:")
        for filename in issues_need_attention:
            print(f"   - Update status in {filename}")
        print()

    print("4. Commit changes:")
    print("   git add _meta/issues/")
    print("   git commit -m 'Update issue tracking based on WIP review'")
    print()


if __name__ == "__main__":
    main()
