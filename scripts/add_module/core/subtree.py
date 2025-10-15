"""Git subtree hierarchy orchestration for PrismQ modules.

Handles the creation of nested git subtree relationships between
parent and child modules in the hierarchy.

PEP 257: Comprehensive docstrings
PEP 484: Type hints throughout
"""

from pathlib import Path
from typing import List, Tuple, Optional
import logging

from .vcs import GitService, VCSError
from .paths import derive_remote_name

logger = logging.getLogger(__name__)


class SubtreeError(Exception):
    """Raised when subtree operations fail."""
    pass


class SubtreeService:
    """Service for orchestrating git subtree hierarchy."""
    
    def __init__(self, git_service: Optional[GitService] = None):
        """
        Initialize SubtreeService.
        
        Args:
            git_service: GitService instance (defaults to new instance)
        """
        self.git = git_service or GitService()
    
    def setup_nested_hierarchy(
        self,
        repos: List[Tuple[str, str, str]],
        repo_root: Path,
        deepest_module_dir: Path
    ) -> None:
        """
        Set up nested git subtree hierarchy from bottom to top.
        
        Process:
        1. Push deepest module to its repository
        2. For each parent (bottom to top):
           - Initialize/pull parent repo
           - Add child as subtree with --prefix
           - Push parent to its repository
        3. Add top-level module to main PrismQ repository
        
        Args:
            repos: List of (repo_name, url, path) tuples for hierarchy
            repo_root: Root of the main PrismQ repository
            deepest_module_dir: Path to the deepest module directory
            
        Raises:
            SubtreeError: If setup fails
        """
        if not repos:
            return
        
        logger.info("Setting up nested git subtree hierarchy...")
        
        # Step 1: Push deepest module to its repository
        self._push_deepest_module(repos[-1], deepest_module_dir)
        
        # Step 2: Integrate each child into its parent (bottom to top)
        for i in range(len(repos) - 2, -1, -1):
            parent_repo, parent_url, parent_path = repos[i]
            child_repo, child_url, child_path = repos[i + 1]
            
            parent_dir = repo_root / parent_path
            
            self._integrate_child_into_parent(
                parent_repo, parent_url, parent_dir,
                child_repo, child_url, child_path
            )
        
        # Step 3: Integrate top-level module into main PrismQ repository
        self._integrate_into_main_repo(repos[0], repo_root)
        
        logger.info("Nested git subtree hierarchy successfully set up!")
    
    def _push_deepest_module(
        self,
        repo_info: Tuple[str, str, str],
        module_dir: Path
    ) -> None:
        """
        Push the deepest module to its GitHub repository.
        
        Args:
            repo_info: Tuple of (repo_name, url, path)
            module_dir: Path to the module directory
        """
        repo_name, url, _ = repo_info
        logger.info(f"Pushing deepest module to GitHub: {repo_name}")
        
        try:
            self.git.push(module_dir)
        except VCSError as e:
            logger.warning(f"Failed to push {repo_name}: {e}")
    
    def _integrate_child_into_parent(
        self,
        parent_repo: str,
        parent_url: str,
        parent_dir: Path,
        child_repo: str,
        child_url: str,
        child_path: str
    ) -> None:
        """
        Integrate a child repository as a subtree of its parent.
        
        Args:
            parent_repo: Parent repository name
            parent_url: Parent repository URL
            parent_dir: Parent directory path
            child_repo: Child repository name
            child_url: Child repository URL
            child_path: Child relative path
        """
        logger.info(f"Integrating {child_repo} into {parent_repo} as subtree...")
        
        # Derive child directory name (last component of path)
        child_dir_name = Path(child_path).name
        
        if not parent_dir.exists():
            logger.warning(f"Parent directory {parent_dir} not found, skipping")
            return
        
        try:
            # Initialize git repo if needed
            if not (parent_dir / '.git').exists():
                self.git.init_repo(parent_dir)
                self.git.add_remote(parent_dir, 'origin', parent_url)
            else:
                # Ensure remote is correct and pull latest
                self.git.add_remote(parent_dir, 'origin', parent_url)
                try:
                    self.git.pull(parent_dir)
                except VCSError:
                    logger.debug(f"Could not pull from {parent_repo} (might be empty)")
            
            # Add child as subtree
            child_remote_name = derive_remote_name(child_url)
            self.git.add_remote(parent_dir, child_remote_name, child_url)
            
            # Subtree add command
            self._subtree_add(
                parent_dir,
                prefix=f'src/{child_dir_name}',
                remote=child_remote_name,
                branch='main'
            )
            
            # Push parent to its repository
            self.git.push(parent_dir)
            
        except Exception as e:
            logger.error(f"Failed to integrate {child_repo} into {parent_repo}: {e}")
            raise SubtreeError(f"Subtree integration failed: {e}")
    
    def _integrate_into_main_repo(
        self,
        top_repo_info: Tuple[str, str, str],
        repo_root: Path
    ) -> None:
        """
        Integrate top-level module into main PrismQ repository.
        
        Args:
            top_repo_info: Tuple of (repo_name, url, path) for top-level repo
            repo_root: Root of main PrismQ repository
        """
        top_repo, top_url, top_path = top_repo_info
        logger.info(f"Integrating {top_repo} into main PrismQ repository...")
        
        top_level_dir = repo_root / top_path
        
        # If directory exists, pull latest changes
        if top_level_dir.exists() and (top_level_dir / '.git').exists():
            try:
                self.git.add_remote(top_level_dir, 'origin', top_url)
                self.git.pull(top_level_dir)
            except VCSError as e:
                logger.debug(f"Could not pull from {top_repo}: {e}")
        
        try:
            # Add as subtree to main repo
            top_remote_name = derive_remote_name(top_url)
            self.git.add_remote(repo_root, top_remote_name, top_url)
            
            self._subtree_add(
                repo_root,
                prefix=top_path,
                remote=top_remote_name,
                branch='main'
            )
            
        except Exception as e:
            logger.warning(f"Failed to add subtree for {top_repo}: {e}")
            # Fallback: just add files normally
            try:
                self.git.runner.run(['git', 'add', top_path], cwd=repo_root)
                self.git.commit(
                    repo_root,
                    f"Add {top_repo.replace('PrismQ.', '')} module"
                )
            except Exception as commit_error:
                logger.error(f"Failed to commit module: {commit_error}")
    
    def _subtree_add(
        self,
        repo_path: Path,
        prefix: str,
        remote: str,
        branch: str = 'main'
    ) -> None:
        """
        Execute git subtree add command.
        
        Args:
            repo_path: Repository path
            prefix: Prefix path for subtree
            remote: Remote name
            branch: Branch name
            
        Raises:
            SubtreeError: If subtree add fails
        """
        try:
            # First fetch the remote
            self.git.runner.run(
                ['git', 'fetch', remote, branch],
                cwd=repo_path
            )
            
            # Then add as subtree
            self.git.runner.run(
                ['git', 'subtree', 'add', f'--prefix={prefix}', remote, branch, '--squash'],
                cwd=repo_path
            )
            logger.info(f"Added subtree at {prefix} from {remote}/{branch}")
            
        except Exception as e:
            raise SubtreeError(f"Failed to add subtree: {e}")
