"""Git operations for module management."""

from pathlib import Path
from typing import List, Tuple
import click
from git import Repo, GitCommandError
from github import GithubException

from .path_utils import derive_module_path, derive_remote_name


def initialize_git_repo(module_dir: Path, remote_url: str, module_name: str) -> bool:
    """
    Initialize git repository in the module directory.
    
    Args:
        module_dir: Directory to initialize as git repository
        remote_url: Remote repository URL
        module_name: Name of the module
        
    Returns:
        True if successful, False otherwise
    """
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


def create_github_repositories(repo_name: str, github_owner: str, github_client) -> List[Tuple[str, str, str]]:
    """
    Create GitHub repositories for all levels of the module hierarchy.
    
    Args:
        repo_name: Repository name
        github_owner: GitHub owner/organization
        github_client: Authenticated GitHub client
        
    Returns:
        List of (repo_name, url, path) tuples for each hierarchy level
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
    
    created_repos = []
    
    click.echo()
    click.echo("=" * 56)
    click.echo("Creating GitHub repositories and setting up hierarchy...")
    click.echo("=" * 56)
    
    for level in levels:
        current_repo = f"PrismQ.{level}"
        current_url = f"https://github.com/{github_owner}/{current_repo}.git"
        
        # Derive module path for this level
        _, temp_path = derive_module_path(current_repo)
        
        # Check if repository exists on GitHub
        click.echo(f"Checking repository: {current_repo}")
        
        try:
            github_client.get_user(github_owner).get_repo(current_repo.replace('PrismQ.', 'PrismQ.', 1))
            click.echo(f"Repository already exists: {current_repo}")
        except GithubException as e:
            if e.status == 404:
                # Repository doesn't exist, create it
                click.echo(f"Creating GitHub repository: {current_repo}")
                try:
                    github_client.get_user(github_owner).create_repo(
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
    repos: List[Tuple[str, str, str]],
    final_module_dir: Path,
    repo_root: Path
):
    """
    Set up nested git subtree hierarchy from bottom to top.
    
    Args:
        repos: List of (repo_name, url, path) tuples for hierarchy
        final_module_dir: Path to the deepest module
        repo_root: Root of the main repository
    """
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
        
        parent_dir = repo_root / parent_path
        
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
            child_remote_name = derive_remote_name(child_url)
            
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
        top_level_dir = repo_root / top_path
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
            main_repo = Repo(repo_root)
            top_remote_name = derive_remote_name(top_url)
            
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
