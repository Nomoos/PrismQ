"""Orchestrator for PrismQ.T.Title.From.Idea (step 03).

Default mode: single process with internal ThreadPoolExecutor (matches OLLAMA_NUM_PARALLEL=4).
No multiple windows needed — parallelism is handled inside the script.

Legacy multi-window sharding:
    Set worker_count > 1 in workflow.json AND pass --worker-id N to each bat window manually.
    In that case each window runs with --worker-id 0, 1, 2, ... and shards by story.id % N.
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent  # _meta/scripts/03_.../ -> repo root
WORKER_SCRIPT = REPO_ROOT / "T" / "Title" / "From" / "Idea" / "src" / "title_from_idea_interactive.py"


def main():
    python = sys.executable
    print(f"[INFO] Starting step 03 with internal threading (PARALLEL_WORKERS=4)")
    print(f"[INFO] Script: {WORKER_SCRIPT}")
    print()

    # Run single process — threading is handled inside the script (--worker-id defaults to -1)
    result = subprocess.run(
        [python, str(WORKER_SCRIPT)],
        cwd=str(SCRIPT_DIR),
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
