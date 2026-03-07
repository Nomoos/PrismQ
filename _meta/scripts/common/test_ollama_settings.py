"""Ollama settings validation for RTX 5090 pipeline.

Tests:
  1. Ollama reachable, required models registered
  2. KEEP_ALIVE=-1  (expires_at = very far future or null)
  3. NUM_PARALLEL=4 (4 concurrent requests to 14b all served in parallel)

Note: qwen3:32b and qwen3:14b do NOT need to be in VRAM simultaneously.
Pipeline is sequential — Ollama swaps models as needed (KEEP_ALIVE prevents
premature eviction).

Usage:
    python test_ollama_settings.py

Run AFTER restarting Ollama via start_ollama.bat.
"""

import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "http://localhost:11434"


def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=10) as r:
        return json.loads(r.read())


def generate(model, prompt="Reply with one word: OK", num_ctx=None):
    opts = {"num_predict": 5}
    if num_ctx:
        opts["num_ctx"] = num_ctx
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False,
                          "think": False, "options": opts}).encode()
    req = urllib.request.Request(f"{BASE}/api/generate", data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    return resp.get("response", "").strip(), time.time() - t0


def check(label, ok, detail=""):
    mark = "OK" if ok else "!!"
    color = "\033[92m" if ok else "\033[91m"
    end = "\033[0m"
    print(f"  {color}[{mark}]{end} {label}" + (f"  -- {detail}" if detail else ""))
    return ok


def main():
    print("\n" + "=" * 60)
    print("  Ollama Settings Validation -- RTX 5090 Pipeline")
    print("=" * 60)

    # ── Check Ollama is up ──────────────────────────────────────
    print("\n[0] Connectivity")
    try:
        tags = get("/api/tags")
        available = [m["name"] for m in tags.get("models", [])]
        check("Ollama reachable", True, f"{len(available)} models registered")
        for m in ("qwen3:14b", "qwen3:32b"):
            check(f"  {m} registered", m in available)
    except Exception as e:
        check("Ollama reachable", False, str(e))
        print("\n  !! Start Ollama via start_ollama.bat first.")
        return 1

    # ── Warm up 14b (the review model used by parallel test) ───
    print("\n[1] Warming up qwen3:14b (review model)...")
    print("  Loading qwen3:14b ctx=4096...", end="", flush=True)
    try:
        _, t = generate("qwen3:14b", num_ctx=4096)
        print(f" done in {t:.1f}s")
    except Exception as e:
        print(f" FAILED: {e}")
        return 1

    # ── Check KEEP_ALIVE=-1 ─────────────────────────────────────
    print("\n[2] KEEP_ALIVE=-1 (models never expire)")
    ps = get("/api/ps")
    loaded = {m["name"]: m for m in ps.get("models", [])}

    if "qwen3:14b" in loaded:
        expires = loaded["qwen3:14b"].get("expires_at", "")
        # keep_alive=-1 → far future date (Ollama uses ~year 2318 or 9999)
        year = int(expires[:4]) if expires and len(expires) >= 4 else 0
        permanent = not expires or year > 2100
        check("qwen3:14b never expires", permanent, f"expires_at: {expires or 'null'}")
        vram_gb = loaded["qwen3:14b"].get("size_vram", 0) / 1024**3
        check("  VRAM usage", vram_gb < 11.0, f"{vram_gb:.1f} GB (want < 11 GB)")
    else:
        check("qwen3:14b never expires", False, "not in VRAM after warm-up")

    # ── NUM_PARALLEL=4 test ────────────────────────────────────
    print("\n[3] NUM_PARALLEL=4 (4 concurrent requests to qwen3:14b)")
    print("  Sending 4 requests simultaneously...", flush=True)
    times = []
    errors = []

    def req(i):
        try:
            _, t = generate("qwen3:14b", f"Count to {i+1}. Reply with just the number.")
            return t
        except Exception as e:
            return e

    t_start = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = [ex.submit(req, i) for i in range(4)]
        for f in as_completed(futures):
            r = f.result()
            if isinstance(r, Exception):
                errors.append(str(r))
            else:
                times.append(r)
    wall_time = time.time() - t_start

    if errors:
        check("All 4 requests succeeded", False, f"errors: {errors}")
    else:
        avg = sum(times) / len(times)
        parallel_ratio = wall_time / sum(times) if times else 1
        is_parallel = parallel_ratio < 0.6
        check("All 4 requests succeeded", True,
              f"avg {avg:.1f}s each, wall {wall_time:.1f}s")
        check("Requests served in parallel (not serial)",
              is_parallel,
              f"wall/sum ratio = {parallel_ratio:.2f} (< 0.6 = parallel, > 0.9 = serial)")

    # ── Model swap check (optional info) ───────────────────────
    print("\n[4] Model swap info (sequential pipeline — no simultaneous load needed)")
    print("  qwen3:32b @ ctx=4096: ~21 GB VRAM (generation steps 04, 08, 09)")
    print("  qwen3:14b @ ctx=4096:  ~9 GB VRAM (review steps 05-07, 10-17)")
    print("  Ollama swaps on demand — KEEP_ALIVE=-1 minimizes reload frequency")

    print("\n" + "=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
