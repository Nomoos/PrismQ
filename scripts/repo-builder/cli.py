#!/usr/bin/env python3
"""CLI interface and main entry point functions."""

import sys
from pathlib import Path

try:
    from .exceptions import RepoBuilderError
    from .validation import validate_github_cli
    from .parsing import derive_module_chain
    from .display import display_module_chain
    from .repository import create_git_chain
except ImportError:
    from exceptions import RepoBuilderError
    from validation import validate_github_cli
    from parsing import derive_module_chain
    from display import display_module_chain
    from repository import create_git_chain


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


def run_git_creation(module_input: str) -> None:
    """
    Main workflow for creating git repository chain.
    
    Args:
        module_input: Module name or GitHub URL
    """
    try:
        print(f"\n🚀 PrismQ Nested Repository Builder & Checker")
        print("=" * 50)

        # Step 1: Validate GitHub CLI authentication
        validate_github_cli()

        # Step 2: Identify working directory it runs from nearest PrismQ root so you do .. if needed
        workspace = Path.cwd()
        while workspace.name != "PrismQ" and workspace != workspace.parent:
            workspace = workspace.parent
        print(f"📂 Working directory: {workspace}")

        # Step 3: Derive module chain
        print(f"\n🔍 Processing input: {module_input}")
        chain = derive_module_chain(module_input)

        # Display results
        display_module_chain(chain)

        create_git_chain(chain, workspace)

        print("\n✅ Analysis complete!")

    except RepoBuilderError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
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

    run_git_creation(module_input)
