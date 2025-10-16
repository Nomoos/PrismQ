#!/usr/bin/env python3
"""
PrismQ Nested Repository Builder & Checker

A CLI tool that validates GitHub CLI authentication and derives the full module 
chain from root to deepest, given a PrismQ dotted name or GitHub URL.

Requirements:
- Input must be either:
  1. Dotted module starting with PrismQ. and at least one more segment
  2. GitHub URL (HTTPS or SSH) pointing to Nomoos/<Repo> where <Repo> starts with PrismQ.
- Module names must have only alphanumeric segments separated by dots
- Chain is returned in order from root to deepest for subtree building

Usage:
    python -m repo_builder <module_name_or_url>
    python -m repo_builder  # Interactive mode - prompts for input
    
Examples:
    python -m repo_builder PrismQ.IdeaInspiration.SubModule
    python -m repo_builder https://github.com/Nomoos/PrismQ.IdeaInspiration
"""

try:
    from .cli import main
except ImportError:
    from cli import main

if __name__ == "__main__":
    main()
