#!/usr/bin/env python3
"""
PrismQ Nested Repository Builder & Checker

A CLI tool that validates GitHub CLI authentication and derives the full module 
chain from root to deepest, given a PrismQ dotted name or GitHub URL.

This module is kept for backward compatibility. The implementation has been
split into multiple modules:
- exceptions.py: Custom exception classes
- validation.py: GitHub CLI validation
- parsing.py: URL and module name parsing
- display.py: Output formatting
- repository.py: Repository operations
- cli.py: CLI interface and main entry point

Requirements:
- Input must be either:
  1. Dotted module starting with PrismQ. and at least one more segment
  2. GitHub URL (HTTPS or SSH) pointing to Nomoos/<Repo> where <Repo> starts with PrismQ.
- Module names must have only alphanumeric segments separated by dots
- Chain is returned in order from root to deepest for subtree building

Usage:
    python repo_builder.py <module_name_or_url>
    python repo_builder.py  # Interactive mode - prompts for input
    
Examples:
    python repo_builder.py PrismQ.IdeaInspiration.SubModule
    python repo_builder.py https://github.com/Nomoos/PrismQ.IdeaInspiration
"""

# Re-export all functions and classes from the new modules for backward compatibility
from exceptions import (
    RepoBuilderError,
    GitHubCLIError,
    ModuleParseError,
)
from validation import validate_github_cli
from parsing import parse_github_url, derive_module_chain
from display import display_module_chain
from repository import repository_exists, get_repository_path, create_git_chain
from cli import get_module_input_interactive, run_git_creation, main

# This allows the script to be run directly with: python repo_builder.py
if __name__ == "__main__":
    main()
