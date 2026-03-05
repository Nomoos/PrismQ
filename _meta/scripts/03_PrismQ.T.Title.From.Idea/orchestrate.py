"""Orchestrator for PrismQ.T.Title.From.Idea (step 03).

Reads worker_count from workflow.json and launches that many parallel
worker windows, each processing a disjoint shard of stories (by id modulo).
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent  # _meta/scripts/03_.../ -> _meta/scripts/ -> _meta/ -> repo root
WORKER_SCRIPT = REPO_ROOT / "T" / "Title" / "From" / "Idea" / "src" / "title_from_idea_interactive.py"


def main():
    config_path = SCRIPT_DIR / "workflow.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        worker_count = max(1, int(config.get("worker_count", 1)))
    except Exception as e:
        print(f"[WARN] Could not read workflow.json ({e}), using 1 worker")
        worker_count = 1

    python = sys.executable
    print(f"[INFO] Launching {worker_count} worker window(s)...")
    print(f"[INFO] Script: {WORKER_SCRIPT}")
    print()

    procs = []
    for i in range(worker_count):
        title = f"PrismQ 03 - Worker {i}/{worker_count}"
        cmd = f'"{python}" "{WORKER_SCRIPT}" --worker-id {i}'
        p = subprocess.Popen(
            ["cmd", "/k", cmd],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            cwd=str(SCRIPT_DIR),
        )
        procs.append(p)
        print(f"[INFO] Worker {i} started (PID {p.pid})")

    print()
    print(f"[INFO] All {worker_count} worker(s) running in separate windows.")
    print("[INFO] Close worker windows or press Ctrl+C here to stop orchestrator.")
    print("[INFO] Workers will continue running independently until closed.")

    try:
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        print()
        print("[INFO] Orchestrator stopped. Worker windows continue independently.")


if __name__ == "__main__":
    main()
