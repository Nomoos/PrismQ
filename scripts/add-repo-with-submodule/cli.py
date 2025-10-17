#!/usr/bin/env python3
"""CLI interface for add-repo-with-submodule."""

import sys

try:
    from .add_repo_submodule import main
except ImportError:
    from add_repo_submodule import main


def get_module_input_interactive() -> str:
    """
    Prompt user for module name or URL in interactive mode.
    
    Returns:
        Module name or URL provided by user
    """
    print("\nUsage: python -m add_repo_with_submodule <module_name_or_url>")
    print("\nExamples:")
    print("  python -m add_repo_with_submodule PrismQ.IdeaInspiration.SubModule")
    print("  python -m add_repo_with_submodule https://github.com/Nomoos/PrismQ.NewModule")
    print("\n" + "=" * 50)
    
    while True:
        try:
            module_input = input("\n📝 Enter module name or URL (Ctrl+C to exit): ").strip()
            if module_input:
                return module_input
            else:
                print("⚠️  Input cannot be empty. Please try again.")
        except EOFError:
            print("\n\n❌ No input provided")
            sys.exit(1)


def cli_main():
    """Main entry point for CLI."""
    # Get module input from command line or interactive mode
    if len(sys.argv) >= 2:
        module_input = sys.argv[1]
    else:
        try:
            module_input = get_module_input_interactive()
        except KeyboardInterrupt:
            print("\n\n👋 Terminated by user")
            sys.exit(0)
    
    main(module_input)


if __name__ == "__main__":
    cli_main()
