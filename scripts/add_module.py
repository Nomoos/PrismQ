#!/usr/bin/env python3
"""
PrismQ Add Module Script (Python)
This script interactively creates a new PrismQ module with GitHub integration.
"""

import os
import sys
import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List
import click
from github import Github, GithubException
from git import Repo, GitCommandError


class ModuleCreator:
    """Handles PrismQ module creation with nested git subtree hierarchy."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.github_client: Optional[Github] = None

    def _get_github_client(self) -> Github:
        """Get authenticated GitHub client."""
        if self.github_client is None:
            try:
                # Try to get token from gh CLI
                result = subprocess.run(
                    ["gh", "auth", "token"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                token = result.stdout.strip()
                from github import Auth
                auth = Auth.Token(token)
                self.github_client = Github(auth=auth)
            except (subprocess.CalledProcessError, FileNotFoundError):
                click.echo("Warning: GitHub CLI not authenticated. Repository operations may fail.")
                click.echo("Please run: gh auth login")
                self.github_client = Github()  # Unauthenticated client
        return self.github_client

    def parse_github_url(self, github_input: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse GitHub URL to extract owner and repository name.
        
        Supports formats:
        - https://github.com/Owner/RepoName.git
        - https://github.com/Owner/RepoName
        - git@github.com:Owner/RepoName.git
        - Owner/RepoName
        """
        # Remove .git suffix if present
        url = github_input.replace('.git', '')
        
        # Handle different URL formats
        if 'github.com/' in url or 'github.com:' in url:
            # Full URL format
            url = url.replace('https://github.com/', '')
            url = url.replace('http://github.com/', '')
            url = url.replace('git@github.com:', '')
        
        # Extract owner and repo from "Owner/RepoName" format
        parts = url.split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]
        
        return None, None

    def derive_module_path(self, repo_name: str) -> Tuple[str, str]:
        """
        Derive module path from repository name.
        
        Converts repository name like "PrismQ.IdeaInspiration.Sources"
        to module name "IdeaInspiration.Sources" and path "src/IdeaInspiration/src/Sources"
        """
        # Remove "PrismQ." prefix if present
        module_full_name = repo_name.replace('PrismQ.', '', 1)
        
        # Split by dots
        components = module_full_name.split('.')
        
        if len(components) == 1:
            # Single component: src/Component
            return components[0], f"src/{components[0]}"
        else:
            # Multiple components: src/First/src/Second/src/Third...
            path_parts = [f"src/{components[0]}"]
            for component in components[1:]:
                path_parts.append(f"src/{component}")
            module_path = '/'.join(path_parts)
            return module_full_name, module_path

    def derive_remote_name(self, remote_url: str) -> str:
        """
        Derive remote name from repository URL.
        
        Converts URL like "https://github.com/Nomoos/PrismQ.RepositoryTemplate.git"
        to "prismq-repositorytemplate"
        """
        # Extract repo name from URL
        url = remote_url.replace('.git', '')
        repo_name = url.split('/')[-1]
        
        # Convert to lowercase and replace dots/underscores with hyphens
        remote_name = repo_name.lower().replace('.', '-').replace('_', '-')
        
        return remote_name

    def create_module_structure(
        self,
        module_dir: Path,
        module_name: str,
        repo_name: str,
        github_owner: str,
        remote_url: str,
        description: str
    ) -> bool:
        """Create the module directory structure and initial files."""
        
        if module_dir.exists():
            # Check if it's a git repository that we can pull from
            if (module_dir / '.git').exists():
                click.echo(f"Module directory '{module_dir}' already exists as git repository")
                click.echo(f"Pulling latest changes from {repo_name}...")
                
                try:
                    from git import Repo, GitCommandError
                    repo = Repo(module_dir)
                    
                    # Ensure origin remote exists and is set correctly
                    try:
                        origin = repo.remote('origin')
                        # Update remote URL if it differs
                        if origin.url != remote_url:
                            click.echo(f"  Updating origin URL to {remote_url}")
                            repo.delete_remote('origin')
                            repo.create_remote('origin', remote_url)
                    except ValueError:
                        # No origin remote exists, create it
                        click.echo(f"  Adding origin remote: {remote_url}")
                        repo.create_remote('origin', remote_url)
                    
                    # Pull latest changes
                    origin = repo.remote('origin')
                    origin.fetch('main')
                    try:
                        repo.git.pull('origin', 'main', '--no-rebase')
                        click.echo(f"  ✓ Pulled latest changes from {repo_name}")
                    except GitCommandError:
                        click.echo(f"  No existing content to pull from {repo_name}")
                    
                    # Module already exists and is up to date, return success
                    return True
                    
                except Exception as e:
                    click.echo(f"  Warning: Could not pull from {repo_name}: {e}")
                    click.echo(f"  Continuing with existing directory...")
                    return True
            else:
                click.echo(f"Error: Module directory '{module_dir}' already exists but is not a git repository")
                return False
        
        click.echo(f"Creating directory: {module_dir}")
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if RepositoryTemplate exists to use as template
        template_dir = self.repo_root / "src" / "RepositoryTemplate"
        
        if template_dir.exists():
            click.echo("Using RepositoryTemplate as base structure...")
            self._copy_template(template_dir, module_dir)
        else:
            click.echo("RepositoryTemplate not found, creating basic structure...")
            self._create_basic_structure(module_dir)
        
        # Create custom configuration files
        self._create_module_config(module_dir, module_name, repo_name, github_owner, remote_url, description)
        
        return True

    def _copy_template(self, template_dir: Path, module_dir: Path):
        """Copy template structure, excluding git-related files."""
        import shutil
        
        # Check if module_dir is a subdirectory of template_dir
        # This would cause infinite recursion during copy
        try:
            module_dir.resolve().relative_to(template_dir.resolve())
            # If we get here, module_dir is inside template_dir - cannot copy!
            click.echo("Warning: Cannot copy template - target is subdirectory of template")
            click.echo("Creating basic structure instead...")
            self._create_basic_structure(module_dir)
            return
        except ValueError:
            # module_dir is NOT a subdirectory of template_dir, safe to proceed
            pass
        
        def ignore_files(directory, files):
            """Ignore .git directories and module-specific files."""
            ignore = {'.git', 'module.json', 'README.md', 'pyproject.toml'}
            return ignore.intersection(files)
        
        try:
            shutil.copytree(template_dir, module_dir, ignore=ignore_files, dirs_exist_ok=True)
            click.echo("Template structure copied successfully")
        except Exception as e:
            click.echo(f"Warning: Failed to copy template structure: {e}")
            self._create_basic_structure(module_dir)

    def _create_basic_structure(self, module_dir: Path):
        """Create basic module directory structure."""
        # Ensure module_dir exists
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (module_dir / "src").mkdir(exist_ok=True)
        (module_dir / "tests").mkdir(exist_ok=True)
        (module_dir / "docs").mkdir(exist_ok=True)
        (module_dir / "scripts").mkdir(exist_ok=True)
        (module_dir / "issues" / "new").mkdir(parents=True, exist_ok=True)
        (module_dir / "issues" / "wip").mkdir(exist_ok=True)
        (module_dir / "issues" / "done").mkdir(exist_ok=True)
        (module_dir / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True, exist_ok=True)
        
        # Create basic Python structure
        init_file = module_dir / "src" / "__init__.py"
        init_file.write_text(f'"""Module package initialization."""\n\n__version__ = "0.1.0"\n')
        
        # Create .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env

# Build
dist/
build/
*.egg-info/

# Tests
.pytest_cache/
.coverage
htmlcov/
"""
        (module_dir / ".gitignore").write_text(gitignore_content)
        
        # Create requirements.txt
        (module_dir / "requirements.txt").write_text("# Core dependencies\n# Add your dependencies here\n")
        
        # Create LICENSE
        license_content = """MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        (module_dir / "LICENSE").write_text(license_content)

    def _create_module_config(
        self,
        module_dir: Path,
        module_name: str,
        repo_name: str,
        github_owner: str,
        remote_url: str,
        description: str
    ):
        """Create module-specific configuration files."""
        
        # Create module.json
        module_json = f"""{{
  "remote": {{
    "url": "{remote_url}"
  }}
}}
"""
        (module_dir / "module.json").write_text(module_json)
        
        # Create README.md
        readme_content = f"""# {repo_name}

{description}

## Purpose

This module is part of the PrismQ ecosystem for AI-powered content generation.

## Target Platform

- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## Quick Start

### Setup

```bash
# Windows
scripts\\setup.bat

# Linux/macOS (development only)
./scripts/setup.sh
```

### Run

```bash
# Windows
scripts\\quickstart.bat

# Linux/macOS (development only)
./scripts/quickstart.sh
```

## Development

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""
        (module_dir / "README.md").write_text(readme_content)
        
        # Create pyproject.toml
        pyproject_content = f"""[tool.poetry]
name = "{module_name}"
version = "0.1.0"
description = "{description}"
authors = ["PrismQ <noreply@github.com>"]

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.dev-dependencies]
pytest = "^7.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
"""
        (module_dir / "pyproject.toml").write_text(pyproject_content)

    def initialize_git_repo(self, module_dir: Path, remote_url: str, module_name: str) -> bool:
        """Initialize git repository in the module directory."""
        try:
            # Check if git repository already exists
            if (module_dir / '.git').exists():
                click.echo("Git repository already exists, skipping initialization...")
                return True
            
            click.echo("Initializing Git repository...")
            
            repo = Repo.init(module_dir)
            
            # Ensure we're on 'main' branch (not 'master')
            # Check if we have a HEAD (initial repo might not)
            try:
                current_branch = repo.active_branch.name
                if current_branch != 'main':
                    # Rename the current branch to 'main'
                    repo.git.branch('-M', 'main')
            except (TypeError, GitCommandError):
                # No active branch yet (empty repo), will be set on first commit
                pass
            
            click.echo("Setting up Git remote...")
            try:
                repo.create_remote('origin', remote_url)
            except GitCommandError:
                click.echo("Warning: Failed to add git remote")
                click.echo(f"You can add it manually later with:")
                click.echo(f"  cd {module_dir}")
                click.echo(f"  git remote add origin {remote_url}")
            
            # Create initial commit on 'main' branch
            repo.index.add(['*'])
            repo.index.commit(f"Initial commit: Create {module_name} module")
            
            # Ensure we're on 'main' branch after commit
            try:
                if repo.active_branch.name != 'main':
                    repo.git.checkout('-B', 'main')
            except (TypeError, GitCommandError):
                pass
            
            click.echo("Module git repository initialized successfully")
            return True
            
        except Exception as e:
            click.echo(f"Warning: Failed to initialize git repository: {e}")
            return False

    def create_github_repositories(self, repo_name: str, github_owner: str) -> List[Tuple[str, str, str]]:
        """
        Create GitHub repositories for all levels of the module hierarchy.
        
        Returns list of (repo_name, url, path) tuples for each hierarchy level.
        """
        # Remove PrismQ. prefix to get module hierarchy
        hierarchy = repo_name.replace('PrismQ.', '', 1)
        
        # Build array of all hierarchy levels
        levels = []
        components = hierarchy.split('.')
        current_level = ""
        
        for component in components:
            if current_level:
                current_level += f".{component}"
            else:
                current_level = component
            levels.append(current_level)
        
        gh = self._get_github_client()
        created_repos = []
        
        click.echo()
        click.echo("=" * 56)
        click.echo("Creating GitHub repositories and setting up hierarchy...")
        click.echo("=" * 56)
        
        for level in levels:
            current_repo = f"PrismQ.{level}"
            current_url = f"https://github.com/{github_owner}/{current_repo}.git"
            
            # Derive module path for this level
            _, temp_path = self.derive_module_path(current_repo)
            
            # Check if repository exists on GitHub
            click.echo(f"Checking repository: {current_repo}")
            
            try:
                gh.get_user(github_owner).get_repo(current_repo.replace('PrismQ.', 'PrismQ.', 1))
                click.echo(f"Repository already exists: {current_repo}")
            except GithubException as e:
                if e.status == 404:
                    # Repository doesn't exist, create it
                    click.echo(f"Creating GitHub repository: {current_repo}")
                    try:
                        gh.get_user(github_owner).create_repo(
                            name=current_repo,
                            description=f"PrismQ module: {level}",
                            private=False
                        )
                        click.echo(f"Successfully created repository: {current_repo}")
                    except GithubException as create_error:
                        click.echo(f"Warning: Failed to create repository {current_repo}")
                        click.echo(f"Error: {create_error}")
                        click.echo("You may need to authenticate with: gh auth login")
                        click.echo(f"Or create it manually at: https://github.com/{github_owner}/{current_repo}")
                else:
                    click.echo(f"Warning: Error checking repository {current_repo}: {e}")
            
            created_repos.append((current_repo, current_url, temp_path))
        
        return created_repos

    def setup_nested_subtree(
        self,
        repos: List[Tuple[str, str, str]],
        final_module_dir: Path
    ):
        """Set up nested git subtree hierarchy from bottom to top."""
        click.echo()
        click.echo("Setting up nested git subtree hierarchy...")
        
        # Push the final (deepest) module to its GitHub repository
        click.echo(f"Pushing deepest module to GitHub: {repos[-1][0]}")
        try:
            repo = Repo(final_module_dir)
            origin = repo.remote('origin')
            # Push main branch to origin/main explicitly
            origin.push(refspec='refs/heads/main:refs/heads/main')
        except Exception as e:
            click.echo(f"Warning: Failed to push to {repos[-1][0]}: {e}")
        
        # Work backwards through hierarchy, integrating each child into parent
        for i in range(len(repos) - 2, -1, -1):
            parent_repo, parent_url, parent_path = repos[i]
            child_repo, child_url, child_path = repos[i + 1]
            
            # Derive child directory name (last component of path)
            child_dir_name = Path(child_path).name
            
            click.echo(f"Integrating {child_repo} into {parent_repo} as subtree...")
            
            parent_dir = self.repo_root / parent_path
            
            if not parent_dir.exists():
                click.echo(f"Warning: Parent directory {parent_dir} not found")
                continue
            
            try:
                # Initialize git repo if not already initialized
                if not (parent_dir / '.git').exists():
                    repo = Repo.init(parent_dir)
                    # Ensure we're on 'main' branch
                    try:
                        repo.git.branch('-M', 'main')
                    except GitCommandError:
                        pass  # Branch doesn't exist yet
                    repo.create_remote('origin', parent_url)
                else:
                    # Parent directory already has a git repository
                    repo = Repo(parent_dir)
                    
                    # Ensure origin remote exists and is set correctly
                    try:
                        origin = repo.remote('origin')
                        # Update remote URL if it differs
                        if origin.url != parent_url:
                            repo.delete_remote('origin')
                            repo.create_remote('origin', parent_url)
                    except ValueError:
                        # No origin remote exists, create it
                        repo.create_remote('origin', parent_url)
                    
                    # Pull latest changes from GitHub repository if it exists
                    try:
                        click.echo(f"  Pulling latest changes from {parent_repo}...")
                        origin = repo.remote('origin')
                        origin.fetch('main')
                        
                        # Check if remote has a main branch
                        try:
                            # Try to pull changes if there's existing content
                            repo.git.pull('origin', 'main', '--no-rebase')
                            click.echo(f"  ✓ Pulled latest changes from {parent_repo}")
                        except GitCommandError as pull_error:
                            # If pull fails (e.g., no commits yet), that's fine
                            click.echo(f"  No existing content to pull from {parent_repo}")
                    except Exception as pull_error:
                        click.echo(f"  Warning: Could not pull from {parent_repo}: {pull_error}")
                
                # Add child as subtree
                child_remote_name = self.derive_remote_name(child_url)
                
                # Add remote if it doesn't exist
                try:
                    repo.create_remote(child_remote_name, child_url)
                except GitCommandError:
                    pass  # Remote already exists
                
                # Fetch and add subtree from origin/main
                repo.git.fetch(child_remote_name, 'main')
                repo.git.subtree('add', f'--prefix=src/{child_dir_name}', child_remote_name, 'main', '--squash')
                
                # Push parent to its GitHub repository's main branch
                origin = repo.remote('origin')
                origin.push(refspec='refs/heads/main:refs/heads/main')
                
            except Exception as e:
                click.echo(f"Warning: Failed to integrate {child_repo} into {parent_repo}: {e}")
        
        # Finally, integrate top-level module into main PrismQ repository
        if repos:
            top_repo, top_url, top_path = repos[0]
            
            click.echo(f"Integrating {top_repo} into main PrismQ repository...")
            
            # Check if top-level module directory already exists locally
            top_level_dir = self.repo_root / top_path
            if top_level_dir.exists() and (top_level_dir / '.git').exists():
                # Directory exists with git repo, pull latest changes first
                try:
                    click.echo(f"  Existing repository found at {top_path}, pulling latest changes...")
                    top_repo_obj = Repo(top_level_dir)
                    
                    # Ensure origin exists and is correct
                    try:
                        origin = top_repo_obj.remote('origin')
                        if origin.url != top_url:
                            top_repo_obj.delete_remote('origin')
                            top_repo_obj.create_remote('origin', top_url)
                    except ValueError:
                        top_repo_obj.create_remote('origin', top_url)
                    
                    # Pull latest changes
                    origin = top_repo_obj.remote('origin')
                    origin.fetch('main')
                    try:
                        top_repo_obj.git.pull('origin', 'main', '--no-rebase')
                        click.echo(f"  ✓ Pulled latest changes from {top_repo}")
                    except GitCommandError:
                        click.echo(f"  No existing content to pull from {top_repo}")
                        
                except Exception as pull_err:
                    click.echo(f"  Warning: Could not pull from existing {top_repo}: {pull_err}")
            
            try:
                main_repo = Repo(self.repo_root)
                top_remote_name = self.derive_remote_name(top_url)
                
                # Add remote if it doesn't exist
                try:
                    main_repo.create_remote(top_remote_name, top_url)
                except GitCommandError:
                    pass  # Remote already exists
                
                # Fetch and add subtree
                main_repo.git.fetch(top_remote_name, 'main')
                main_repo.git.subtree('add', f'--prefix={top_path}', top_remote_name, 'main', '--squash')
                
            except Exception as e:
                click.echo(f"Warning: Failed to add subtree for {top_repo}: {e}")
                # Fallback: just add files normally
                try:
                    main_repo.index.add([top_path])
                    main_repo.index.commit(f"Add {repos[0][0].replace('PrismQ.', '')} module")
                except Exception as commit_error:
                    click.echo(f"Warning: Failed to commit module: {commit_error}")
        
        click.echo("Nested git subtree hierarchy successfully set up!")


@click.command()
@click.option('--github-url', help='GitHub repository URL or Owner/RepoName format')
@click.option('--description', default='A PrismQ module', help='Module description')
def main(github_url: Optional[str], description: str):
    """PrismQ Module Creation Script - Create a new PrismQ module with GitHub integration."""
    
    click.echo()
    click.echo("=" * 56)
    click.echo("        PrismQ Module Creation Script")
    click.echo("=" * 56)
    click.echo()
    
    # Check if we're in a git repository
    try:
        repo = Repo('.', search_parent_directories=True)
        repo_root = Path(repo.working_dir)
    except Exception:
        click.echo("Error: Not in a git repository")
        click.echo("Please run this script from the root of the PrismQ repository")
        sys.exit(1)
    
    creator = ModuleCreator(repo_root)
    
    # Always use GitHub URL input method
    if github_url:
        # GitHub URL provided via command line
        github_input = github_url
    else:
        # Interactive mode - prompt for GitHub URL
        github_input = click.prompt("Enter the GitHub repository URL (e.g., https://github.com/Nomoos/PrismQ.RepositoryTemplate.git)")
    
    # Parse GitHub URL
    github_owner, repo_name = creator.parse_github_url(github_input)
    
    if not github_owner or not repo_name:
        click.echo("Error: Failed to parse GitHub URL")
        sys.exit(1)
    
    # Derive module name and path from repository name
    module_name_derived, module_dir_path = creator.derive_module_path(repo_name)
    
    click.echo()
    click.echo("Parsed from GitHub URL:")
    click.echo(f"  Owner: {github_owner}")
    click.echo(f"  Repository: {repo_name}")
    click.echo(f"  Module Name: {module_name_derived}")
    click.echo(f"  Module Path: {module_dir_path}")
    click.echo()
    
    if not description or description == 'A PrismQ module':
        description = click.prompt("Please enter a short description for the module (optional)", 
                                  default="A PrismQ module", show_default=False)
    
    remote_url = f"https://github.com/{github_owner}/{repo_name}.git"
    
    # Derive remote name
    remote_name = creator.derive_remote_name(remote_url)
    
    # Display configuration summary
    click.echo()
    click.echo("=" * 56)
    click.echo("Module Configuration Summary")
    click.echo("=" * 56)
    click.echo(f"Module Name:        {module_name_derived}")
    click.echo(f"Module Directory:   {module_dir_path}")
    click.echo(f"Description:        {description}")
    click.echo(f"Repository Name:    {repo_name}")
    click.echo(f"GitHub Owner:       {github_owner}")
    click.echo(f"Remote URL:         {remote_url}")
    click.echo(f"Remote Name:        {remote_name}")
    click.echo("=" * 56)
    click.echo()
    
    # Confirm creation
    if not click.confirm("Create this module?"):
        click.echo("Module creation cancelled")
        sys.exit(0)
    
    click.echo()
    click.echo("Creating module structure...")
    
    # Create module structure
    module_dir = repo_root / module_dir_path
    if not creator.create_module_structure(
        module_dir,
        module_name_derived,
        repo_name,
        github_owner,
        remote_url,
        description
    ):
        sys.exit(1)
    
    # Initialize git repository
    creator.initialize_git_repo(module_dir, remote_url, module_name_derived)
    
    # Create GitHub repositories and set up hierarchy
    repos = creator.create_github_repositories(repo_name, github_owner)
    
    # Set up nested subtree structure
    creator.setup_nested_subtree(repos, module_dir)
    
    click.echo()
    click.echo("=" * 56)
    click.echo("Module created successfully!")
    click.echo("=" * 56)
    click.echo()
    click.echo("Next steps:")
    click.echo(f"  1. Review the generated files in {module_dir}")
    click.echo("  2. The module has been committed to the parent repository")
    click.echo("  3. Push the parent repository changes:")
    click.echo("     git push")
    click.echo("  4. Use scripts/sync_modules.py (or scripts\\sync-modules.bat on Windows) to sync future updates")
    click.echo("     The module is managed as a git subtree hierarchy")
    click.echo()


if __name__ == '__main__':
    main()
