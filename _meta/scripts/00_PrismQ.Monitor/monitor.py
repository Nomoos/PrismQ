#!/usr/bin/env python3
"""PrismQ Pipeline Monitor — prints story state distribution every 30 seconds."""

import sqlite3
import sys
import time
import os
from datetime import datetime
from pathlib import Path

# Force UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DB_PATH = "C:/PrismQ/db.s3db"
REFRESH_SECONDS = 30

# ANSI colors
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
GRAY   = "\033[90m"
WHITE  = "\033[97m"

# Map state fragments → module number
_STATE_MAP = {
    "Idea.From.User":                   "01",
    "Story.From.Idea":                  "02",
    "Title.From.Idea":                  "03",
    "Content.From.Idea.Title":          "04",
    "Review.Title.From.Content.Idea":   "05",
    "Review.Content.From.Title.Idea":   "06",
    "Review.Title.From.Content":        "07",
    "Title.From.Title.Review.Content":  "08",
    "Content.From.Content.Review.Title":"09",
    "Review.Content.From.Title":        "10",
    "Review.Content.Grammar":           "11",
    "Review.Content.Tone":              "12",
    "Review.Content.Content":           "13",
    "Review.Content.Consistency":       "14",
    "Review.Content.Editing":           "15",
    "Review.Title.Readability":         "16",
    "Review.Content.Readability":       "17",
    "Story.Review":                     "18",
    "Story.Polish":                     "19",
    "Publishing":                       "20",
}


def _module_num(state: str) -> str:
    for fragment, num in _STATE_MAP.items():
        if fragment in state:
            return num
    return "??"


def _bar(count: int, max_count: int, width: int = 20) -> str:
    if max_count == 0:
        return " " * width
    filled = round(count / max_count * width)
    return "█" * filled + "░" * (width - filled)


def _clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_table(rows: list, elapsed: float):
    _clear()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    max_count = max((cnt for _, cnt in rows), default=1)
    total = sum(cnt for _, cnt in rows)

    print(f"{BOLD}{CYAN}{'═' * 72}{RESET}")
    print(f"{BOLD}{CYAN}  PrismQ Pipeline Monitor   {GRAY}{now}   next refresh in {REFRESH_SECONDS:.0f}s{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 72}{RESET}")
    print(f"{GRAY}  {'##':>2}  {'Count':>7}  {'Bar':<22}  State{RESET}")
    print(f"{GRAY}  {'──':>2}  {'───────':>7}  {'──────────────────────':<22}  {'─' * 40}{RESET}")

    for state, cnt in rows:
        num = _module_num(state)
        bar = _bar(cnt, max_count)
        color = GREEN if cnt > 0 else GRAY
        short_state = state.replace("PrismQ.T.", "").replace("PrismQ.", "")
        print(f"  {YELLOW}{num:>2}{RESET}  {color}{cnt:>7,}{RESET}  {CYAN}{bar}{RESET}  {WHITE}{short_state}{RESET}")

    print(f"{GRAY}  {'──':>2}  {'───────':>7}  {'──────────────────────':<22}  {'─' * 40}{RESET}")
    print(f"  {'':>2}  {BOLD}{WHITE}{total:>7,}{RESET}  {'total stories':}")
    print(f"{BOLD}{CYAN}{'═' * 72}{RESET}")


def query(conn: sqlite3.Connection) -> list:
    return conn.execute(
        "SELECT state, COUNT(*) AS cnt FROM Story GROUP BY state ORDER BY cnt DESC"
    ).fetchall()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="PrismQ Pipeline Monitor")
    parser.add_argument("--once", action="store_true", help="Print once and exit (no loop)")
    parser.add_argument("--no-clear", action="store_true", help="Skip screen clear (useful for piped output)")
    args = parser.parse_args()

    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"ERROR: Cannot connect to database: {e}")
        return 1

    if args.once:
        rows = query(conn)
        conn.close()
        if args.no_clear:
            # Plain output without cls
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            max_count = max((cnt for _, cnt in rows), default=1)
            total = sum(cnt for _, cnt in rows)
            print(f"\n{BOLD}{CYAN}  PrismQ State Monitor — {now}{RESET}")
            print(f"{GRAY}  {'##':>2}  {'Count':>7}  {'Bar':<22}  State{RESET}")
            print(f"{GRAY}  {'──':>2}  {'───────':>7}  {'──────────────────────':<22}  {'─' * 42}{RESET}")
            for state, cnt in rows:
                num = _module_num(state)
                bar = _bar(cnt, max_count)
                color = GREEN if cnt > 0 else GRAY
                short_state = state.replace("PrismQ.T.", "").replace("PrismQ.", "")
                print(f"  {YELLOW}{num:>2}{RESET}  {color}{cnt:>7,}{RESET}  {CYAN}{bar}{RESET}  {WHITE}{short_state}{RESET}")
            print(f"{GRAY}  {'':>2}  {'───────':>7}{RESET}")
            print(f"  {'':>2}  {BOLD}{WHITE}{total:>7,}{RESET}  total\n")
        else:
            print_table(rows, 0)
        return 0

    print(f"{GREEN}Refreshing every {REFRESH_SECONDS}s — press Ctrl+C to stop.{RESET}")
    time.sleep(1)

    try:
        while True:
            rows = query(conn)
            print_table(rows, 0)
            time.sleep(REFRESH_SECONDS)

    except KeyboardInterrupt:
        _clear()
        print(f"\n{YELLOW}Monitor stopped.{RESET}\n")

    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
