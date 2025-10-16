#!/usr/bin/env python3
"""
PrismQ Nested Repository Builder & Checker

A CLI tool that validates GitHub CLI authentication and derives the full module 
chain from deepest to root, given a PrismQ dotted name or GitHub URL.

Usage:
    python repo_builder.py <module_name_or_url>
    python repo_builder.py  # Interactive mode - prompts for input
    
Examples:
    python repo_builder.py PrismQ.IdeaInspiration.SubModule
    python repo_builder.py https://github.com/Nomoos/PrismQ.IdeaInspiration
"""

import sys
import subprocess
import re
from typing import List, Tuple, Optional
from pathlib import Path


class RepoBuilderError(Exception):
    """Base exception for repository builder errors."""
    pass


class GitHubCLIError(RepoBuilderError):
    """Exception raised when GitHub CLI authentication fails."""
    pass


class ModuleParseError(RepoBuilderError):
    """Exception raised when module name parsing fails."""
    pass


def validate_github_cli() -> bool:
    """
    Validate that GitHub CLI is installed and authenticated.
    
    Returns:
        True if GitHub CLI is authenticated
        
    Raises:
        GitHubCLIError: If GitHub CLI is not installed or not authenticated
    """
    print("🔍 Validating GitHub CLI authentication...")
    
    # Check if gh CLI is installed
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise GitHubCLIError("GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/")
    except FileNotFoundError:
        raise GitHubCLIError("GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/")
    
    # Check if authenticated
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise GitHubCLIError("GitHub CLI is not authenticated. Please run 'gh auth login'")
        
        print("✅ GitHub CLI is authenticated")
        return True
        
    except FileNotFoundError:
        raise GitHubCLIError("GitHub CLI (gh) is not installed")


def parse_github_url(url: str) -> str:
    """
    Extract module name from GitHub URL.
    
    Args:
        url: GitHub URL (e.g., https://github.com/Nomoos/PrismQ.IdeaInspiration)
        
    Returns:
        Module name in dotted notation (e.g., PrismQ.IdeaInspiration)
        
    Raises:
        ModuleParseError: If URL format is invalid
    """
    # Match GitHub URL patterns
    patterns = [
        r'https?://github\.com/[^/]+/([^/\.]+(?:\.[^/\.]+)*)',
        r'git@github\.com:[^/]+/([^/\.]+(?:\.[^/\.]+)*)\.git',
        r'git@github\.com:[^/]+/([^/\.]+(?:\.[^/\.]+)*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            repo_name = match.group(1)
            # Replace any remaining .git suffix
            repo_name = re.sub(r'\.git$', '', repo_name)
            return repo_name
    
    raise ModuleParseError(f"Invalid GitHub URL format: {url}")


def derive_module_chain(module_input: str) -> List[str]:
    """
    Derive the full module chain from deepest to root.
    
    Args:
        module_input: Either a dotted module name (e.g., PrismQ.IdeaInspiration.SubModule)
                     or a GitHub URL
                     
    Returns:
        List of module names from deepest to root
        Example: ['PrismQ.IdeaInspiration.SubModule', 'PrismQ.IdeaInspiration', 'PrismQ']
        
    Raises:
        ModuleParseError: If module name format is invalid
    """
    # Check if input is a URL
    if module_input.startswith('http://') or module_input.startswith('https://') or module_input.startswith('git@'):
        module_name = parse_github_url(module_input)
    else:
        module_name = module_input
    
    # Validate module name format
    if not re.match(r'^[A-Za-z][A-Za-z0-9]*(\.[A-Za-z][A-Za-z0-9]*)*$', module_name):
        raise ModuleParseError(
            f"Invalid module name format: {module_name}\n"
            "Module names should be in dotted notation (e.g., PrismQ.IdeaInspiration)"
        )
    
    # Split into parts
    parts = module_name.split('.')
    
    # Build chain from deepest to root
    chain = []
    for i in range(len(parts), 0, -1):
        chain.append('.'.join(parts[:i]))
    
    return chain


def display_module_chain(chain: List[str]) -> None:
    """
    Display the module chain in a formatted way.
    
    Args:
        chain: List of module names from deepest to root
    """
    print("\n📦 Module Chain (deepest → root):")
    print("=" * 50)
    
    for i, module in enumerate(chain):
        indent = "  " * (len(chain) - i - 1)
        depth = len(module.split('.'))
        
        if i == 0:
            marker = "🎯"  # Target module
        elif i == len(chain) - 1:
            marker = "🏠"  # Root module
        else:
            marker = "📁"  # Intermediate module
        
        print(f"{indent}{marker} {module} (depth: {depth})")
    
    print("=" * 50)


def get_module_input_interactive() -> str:
    """
    Prompt user for module name or URL in interactive mode.
    
    Returns:
        Module name or URL provided by user
        
    Raises:
        KeyboardInterrupt: If user terminates the script with Ctrl+C
    """
    print("\nUsage: python repo_builder.py <module_name_or_url>")
    print("\nExamples:")
    print("  python repo_builder.py PrismQ.IdeaInspiration.SubModule")
    print("  python repo_builder.py https://github.com/Nomoos/PrismQ.IdeaInspiration")
    print("\n" + "=" * 50)
    
    while True:
        try:
            module_input = input("\n📝 Enter module name or URL (Ctrl+C to exit): ").strip()
            if module_input:
                return module_input
            else:
                print("⚠️  Input cannot be empty. Please try again.")
        except EOFError:
            # Handle end of input (e.g., when input is piped)
            print("\n\n❌ No input provided")
            sys.exit(1)


def main():
    """Main entry point for the CLI tool."""
    # Get module input from command line or interactive mode
    if len(sys.argv) >= 2:
        module_input = sys.argv[1]
    else:
        try:
            module_input = get_module_input_interactive()
        except KeyboardInterrupt:
            print("\n\n👋 Terminated by user")
            sys.exit(0)
    
    try:
        print(f"\n🚀 PrismQ Nested Repository Builder & Checker")
        print("=" * 50)
        
        # Step 1: Validate GitHub CLI authentication
        validate_github_cli()
        
        # Step 2: Derive module chain
        print(f"\n🔍 Processing input: {module_input}")
        chain = derive_module_chain(module_input)
        
        # Display results
        display_module_chain(chain)
        
        print("\n✅ Analysis complete!")
        
    except RepoBuilderError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
