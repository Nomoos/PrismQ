"""Example: Using parse_input_text from the Creation module."""

import sys
from pathlib import Path

# Add Creation src to path
_SRC = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(_SRC))

from idea_creation_interactive import parse_input_text  # noqa: E402

# Example 1: Short plain text
title, desc, meta = parse_input_text("A ghost story")
print(f"Title: {title}")  # "A ghost story"
print(f"Desc:  {desc!r}")   # ""
print(f"Meta:  {meta}")     # {}

# Example 2: JSON input
import json  # noqa: E402

data = json.dumps({"story_title": "The Door", "tone": "eerie", "theme": "secrets"})
title2, desc2, meta2 = parse_input_text(data)
print(f"\nTitle: {title2}")   # "The Door"
print(f"Desc:  {desc2}")      # "Tone: eerie. Theme: secrets"
