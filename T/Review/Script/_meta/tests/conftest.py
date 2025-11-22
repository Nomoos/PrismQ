"""Test configuration for Review.Script tests.

Sets up sys.path to enable importing from T.Idea.Model.src
"""

import sys
from pathlib import Path

# Add T/Idea/Model to path for src.idea import
_test_dir = Path(__file__).parent
_repo_root = _test_dir.parent.parent.parent.parent.parent
_idea_model_path = _repo_root / "T" / "Idea" / "Model"

if str(_idea_model_path) not in sys.path:
    sys.path.insert(0, str(_idea_model_path))
