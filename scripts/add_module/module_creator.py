"""Main ModuleCreator class orchestrating module creation."""

from pathlib import Path
from typing import List, Tuple

from .github_client import get_github_client
from .url_parser import parse_github_url
from .path_utils import derive_module_path, derive_remote_name
from .module_structure import create_module_structure
from .git_operations import (
    initialize_git_repo,
    create_github_repositories,
    setup_nested_subtree
)


class ModuleCreator:
    """Handles PrismQ module creation with nested git subtree hierarchy."""

    def __init__(self, repo_root: Path):
        """
        Initialize ModuleCreator.
        
        Args:
            repo_root: Path to the root of the main repository
        """
        self.repo_root = repo_root
        self._github_client = None

    def _get_github_client(self):
        """Get or create GitHub client (lazy initialization)."""
        if self._github_client is None:
            self._github_client = get_github_client()
        return self._github_client

    # Expose utility methods for backward compatibility and testing
    def parse_github_url(self, github_input: str):
        """Parse GitHub URL. Delegates to url_parser module."""
        return parse_github_url(github_input)

    def derive_module_path(self, repo_name: str):
        """Derive module path from repository name. Delegates to path_utils module."""
        return derive_module_path(repo_name)

    def derive_remote_name(self, remote_url: str):
        """Derive remote name from repository URL. Delegates to path_utils module."""
        return derive_remote_name(remote_url)

    def create_module_structure(
        self,
        module_dir: Path,
        module_name: str,
        repo_name: str,
        github_owner: str,
        remote_url: str,
        description: str
    ) -> bool:
        """
        Create the module directory structure and initial files.
        
        Delegates to module_structure module.
        """
        return create_module_structure(
            module_dir,
            module_name,
            repo_name,
            github_owner,
            remote_url,
            description,
            self.repo_root
        )

    def initialize_git_repo(self, module_dir: Path, remote_url: str, module_name: str) -> bool:
        """
        Initialize git repository in the module directory.
        
        Delegates to git_operations module.
        """
        return initialize_git_repo(module_dir, remote_url, module_name)

    def create_github_repositories(self, repo_name: str, github_owner: str) -> List[Tuple[str, str, str]]:
        """
        Create GitHub repositories for all levels of the module hierarchy.
        
        Delegates to git_operations module.
        """
        return create_github_repositories(repo_name, github_owner, self._get_github_client())

    def setup_nested_subtree(
        self,
        repos: List[Tuple[str, str, str]],
        final_module_dir: Path
    ):
        """
        Set up nested git subtree hierarchy from bottom to top.
        
        Delegates to git_operations module.
        """
        setup_nested_subtree(repos, final_module_dir, self.repo_root)
