#!/usr/bin/env python3
"""
PrismQ Add Module - CLI Entry Point

Automates PrismQ module setup end-to-end:
1. Automatic nested module path derivation
2. Hierarchical repository creation with GitHub CLI
3. Full nested git subtree hierarchy
4. Smart sync if repository already exists

PEP 257: Module-level docstring
PEP 484: Type hints throughout
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from .core.paths import (
    derive_module_path,
    parse_module_hierarchy,
    PathDerivationError
)
from .core.vcs import GitService, GitHubService, VCSError
from .core.template import TemplateService, TemplateSyncError
from .core.subtree import SubtreeService, SubtreeError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class AddModuleError(Exception):
    """Base exception for add_module operations."""
    pass


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for add_module CLI.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description='Automate PrismQ module creation with nested git subtree hierarchy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a simple module
  python -m scripts.add_module.add_module PrismQ.NewModule
  
  # Create a nested module with custom owner
  python -m scripts.add_module.add_module \\
    PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource \\
    --owner Nomoos --public
  
  # Create a private module with custom remote prefix
  python -m scripts.add_module.add_module \\
    PrismQ.Internal.PrivateModule \\
    --private --remote-origin-prefix https://github.com
        """
    )
    
    parser.add_argument(
        'module',
        help='PrismQ module name in dot-notation (e.g., PrismQ.IdeaInspiration.Sources)'
    )
    
    parser.add_argument(
        '--owner',
        default='Nomoos',
        help='GitHub repository owner/organization (default: Nomoos)'
    )
    
    parser.add_argument(
        '--branch',
        default='main',
        help='Git branch name (default: main)'
    )
    
    visibility_group = parser.add_mutually_exclusive_group()
    visibility_group.add_argument(
        '--public',
        action='store_true',
        default=True,
        help='Create public repositories (default)'
    )
    visibility_group.add_argument(
        '--private',
        action='store_true',
        help='Create private repositories'
    )
    
    parser.add_argument(
        '--remote-origin-prefix',
        default='https://github.com',
        help='Remote origin URL prefix (default: https://github.com)'
    )
    
    parser.add_argument(
        '--description',
        help='Module description'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser


def validate_module_name(module_name: str) -> None:
    """
    Validate module name format.
    
    Args:
        module_name: Module name to validate
        
    Raises:
        AddModuleError: If module name is invalid
    """
    if not module_name:
        raise AddModuleError("Module name cannot be empty")
    
    if not module_name.startswith('PrismQ.'):
        raise AddModuleError("Module name must start with 'PrismQ.'")
    
    # Check for invalid characters
    parts = module_name.split('.')
    for part in parts:
        if not part:
            raise AddModuleError(f"Invalid module name: empty component in '{module_name}'")
        if not part.replace('_', '').replace('-', '').isalnum():
            raise AddModuleError(
                f"Invalid module name: component '{part}' contains invalid characters"
            )


def get_repo_root() -> Path:
    """
    Get the repository root directory.
    
    Returns:
        Path to repository root
        
    Raises:
        AddModuleError: If not in a git repository
    """
    try:
        from git import Repo
        repo = Repo('.', search_parent_directories=True)
        return Path(repo.working_dir)
    except Exception:
        raise AddModuleError(
            "Not in a git repository. Please run from PrismQ repository root."
        )


def create_hierarchy_repositories(
    module_name: str,
    owner: str,
    public: bool,
    remote_prefix: str,
    github_service: GitHubService
) -> list:
    """
    Create GitHub repositories for all levels in the hierarchy.
    
    Args:
        module_name: Full module name (e.g., PrismQ.IdeaInspiration.Sources)
        owner: GitHub owner
        public: Whether repositories should be public
        remote_prefix: Remote URL prefix
        github_service: GitHubService instance
        
    Returns:
        List of (repo_name, url, path) tuples
    """
    hierarchy = parse_module_hierarchy(module_name)
    repos = []
    
    logger.info("Creating GitHub repository hierarchy...")
    logger.info("=" * 60)
    
    for level in hierarchy:
        url = f"{remote_prefix}/{owner}/{level}.git"
        _, path = derive_module_path(level)
        
        logger.info(f"Checking: {level}")
        
        # Ensure repository exists
        created = github_service.ensure_repo_exists(
            owner,
            level,
            public,
            f"PrismQ module: {level.replace('PrismQ.', '')}"
        )
        
        if created:
            logger.info(f"  ✓ Created repository: {level}")
        else:
            logger.info(f"  ✓ Repository exists: {level}")
        
        repos.append((level, url, path))
    
    logger.info("=" * 60)
    return repos


def setup_module_structure(
    module_path: str,
    repo_root: Path,
    template_service: TemplateService,
    git_service: GitService,
    remote_url: str
) -> Path:
    """
    Set up module directory structure.
    
    Args:
        module_path: Derived module path
        repo_root: Repository root
        template_service: TemplateService instance
        git_service: GitService instance
        remote_url: Remote repository URL
        
    Returns:
        Path to created module directory
    """
    module_dir = repo_root / module_path
    
    logger.info(f"Setting up module structure at: {module_path}")
    
    if module_dir.exists():
        if (module_dir / '.git').exists():
            # Existing git repository - sync with template
            logger.info("Module directory exists, syncing with template...")
            
            # Pull latest changes
            git_service.add_remote(module_dir, 'origin', remote_url)
            try:
                git_service.pull(module_dir)
                logger.info("  ✓ Pulled latest changes")
            except VCSError:
                logger.debug("No existing content to pull")
            
            # Sync missing template files
            try:
                added = template_service.sync_missing_files(module_dir)
                if added:
                    logger.info(f"  ✓ Added {len(added)} missing files from template")
                    # Commit and push changes
                    git_service.commit(module_dir, "Sync: add missing template files/folders")
                    git_service.push(module_dir)
                    logger.info("  ✓ Pushed template sync changes")
            except TemplateSyncError as e:
                logger.warning(f"Could not sync template: {e}")
            
            return module_dir
        else:
            raise AddModuleError(
                f"Directory {module_dir} exists but is not a git repository"
            )
    
    # Create new module
    logger.info("Creating new module directory...")
    module_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy template or create basic structure
    template_dir = repo_root / "src" / "RepositoryTemplate"
    if template_dir.exists():
        logger.info("Using RepositoryTemplate as base...")
        template_service.copy_template_structure(module_dir)
    else:
        logger.info("Creating basic structure...")
        template_service.create_basic_structure(module_dir)
    
    # Initialize git
    git_service.init_repo(module_dir)
    git_service.add_remote(module_dir, 'origin', remote_url)
    
    # Initial commit
    module_name_short = module_path.split('/')[-1]
    git_service.commit(module_dir, f"Initial commit: Create {module_name_short} module")
    
    logger.info("  ✓ Module structure created")
    
    return module_dir


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for add_module CLI.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Print header
        print()
        print("=" * 60)
        print("        PrismQ Module Creation Script")
        print("=" * 60)
        print()
        
        # Validate inputs
        validate_module_name(args.module)
        
        # Get repository root
        repo_root = get_repo_root()
        
        # Derive module path
        module_name, module_path = derive_module_path(args.module)
        
        # Display configuration
        print("Configuration:")
        print(f"  Module Name:     {module_name}")
        print(f"  Module Path:     {module_path}")
        print(f"  Owner:           {args.owner}")
        print(f"  Visibility:      {'Public' if not args.private else 'Private'}")
        print(f"  Branch:          {args.branch}")
        print()
        
        # Initialize services
        git_service = GitService()
        github_service = GitHubService()
        template_dir = repo_root / "src" / "RepositoryTemplate"
        template_service = TemplateService(template_dir)
        subtree_service = SubtreeService(git_service)
        
        # Create repository hierarchy
        is_public = not args.private
        repos = create_hierarchy_repositories(
            args.module,
            args.owner,
            is_public,
            args.remote_origin_prefix,
            github_service
        )
        
        # Get the deepest module info
        final_repo_name, final_remote_url, final_module_path = repos[-1]
        
        # Set up module structure
        module_dir = setup_module_structure(
            final_module_path,
            repo_root,
            template_service,
            git_service,
            final_remote_url
        )
        
        # Set up nested subtree hierarchy
        print()
        logger.info("Setting up nested git subtree hierarchy...")
        subtree_service.setup_nested_hierarchy(repos, repo_root, module_dir)
        
        # Success message
        print()
        print("=" * 60)
        print("Module created successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print(f"  1. Review the generated files in {module_dir}")
        print("  2. The module has been integrated into the parent repository")
        print("  3. Push changes to the main repository:")
        print("     git push")
        print()
        
        return 0
        
    except PathDerivationError as e:
        logger.error(f"Path derivation error: {e}")
        return 1
    except VCSError as e:
        logger.error(f"VCS error: {e}")
        return 1
    except TemplateSyncError as e:
        logger.error(f"Template error: {e}")
        return 1
    except SubtreeError as e:
        logger.error(f"Subtree error: {e}")
        return 1
    except AddModuleError as e:
        logger.error(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())
