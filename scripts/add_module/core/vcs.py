"""Version control system operations for PrismQ modules.

Handles Git and GitHub operations following SOLID principles:
- Single Responsibility: Each class has one clear purpose
- Dependency Inversion: Uses injected CommandRunner for testability

PEP 257: Comprehensive docstrings
PEP 484: Type hints throughout
"""

from pathlib import Path
from typing import List, Tuple, Protocol, Optional
import subprocess
import logging

logger = logging.getLogger(__name__)


class VCSError(Exception):
    """Base exception for VCS operations."""
    pass


class RepoExistsButDirtyError(VCSError):
    """Raised when repository exists but has uncommitted changes."""
    pass


class CommandRunner(Protocol):
    """Protocol for command execution (dependency injection)."""
    
    def run(self, cmd: List[str], cwd: Optional[Path] = None, 
            check: bool = True, capture_output: bool = True) -> subprocess.CompletedProcess:
        """
        Run a command.
        
        Args:
            cmd: Command and arguments as list
            cwd: Working directory
            check: Whether to raise on non-zero exit
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            CompletedProcess instance
        """
        ...


class SubprocessCommandRunner:
    """Default command runner using subprocess."""
    
    def run(self, cmd: List[str], cwd: Optional[Path] = None,
            check: bool = True, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run command using subprocess."""
        logger.debug(f"Running command: {' '.join(cmd)} (cwd={cwd})")
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=True
        )
        logger.debug(f"Command completed with exit code: {result.returncode}")
        return result


class GitService:
    """Service for Git operations."""
    
    def __init__(self, runner: CommandRunner = None):
        """
        Initialize GitService.
        
        Args:
            runner: Command runner (defaults to SubprocessCommandRunner)
        """
        self.runner = runner or SubprocessCommandRunner()
    
    def init_repo(self, path: Path, branch: str = 'main') -> None:
        """
        Initialize a git repository.
        
        Args:
            path: Path where to initialize repository
            branch: Initial branch name (default: 'main')
            
        Raises:
            VCSError: If initialization fails
        """
        try:
            if (path / '.git').exists():
                logger.info(f"Git repository already exists at {path}")
                return
            
            self.runner.run(['git', 'init', '-b', branch], cwd=path)
            logger.info(f"Initialized git repository at {path}")
        except subprocess.CalledProcessError as e:
            raise VCSError(f"Failed to initialize git repository: {e}")
    
    def add_remote(self, path: Path, name: str, url: str) -> None:
        """
        Add a git remote.
        
        Args:
            path: Repository path
            name: Remote name
            url: Remote URL
            
        Raises:
            VCSError: If adding remote fails
        """
        try:
            # Check if remote already exists
            result = self.runner.run(
                ['git', 'remote', 'get-url', name],
                cwd=path,
                check=False
            )
            
            if result.returncode == 0:
                # Remote exists, check if URL matches
                if result.stdout.strip() != url:
                    logger.info(f"Updating remote {name} URL to {url}")
                    self.runner.run(['git', 'remote', 'set-url', name, url], cwd=path)
            else:
                # Remote doesn't exist, create it
                self.runner.run(['git', 'remote', 'add', name, url], cwd=path)
                logger.info(f"Added remote {name}: {url}")
        except subprocess.CalledProcessError as e:
            raise VCSError(f"Failed to add remote: {e}")
    
    def commit(self, path: Path, message: str) -> None:
        """
        Create a git commit.
        
        Args:
            path: Repository path
            message: Commit message
            
        Raises:
            VCSError: If commit fails
        """
        try:
            self.runner.run(['git', 'add', '.'], cwd=path)
            self.runner.run(['git', 'commit', '-m', message], cwd=path)
            logger.info(f"Created commit: {message}")
        except subprocess.CalledProcessError as e:
            raise VCSError(f"Failed to create commit: {e}")
    
    def push(self, path: Path, remote: str = 'origin', branch: str = 'main') -> None:
        """
        Push to remote repository.
        
        Args:
            path: Repository path
            remote: Remote name
            branch: Branch name
            
        Raises:
            VCSError: If push fails
        """
        try:
            self.runner.run(['git', 'push', remote, branch], cwd=path)
            logger.info(f"Pushed {branch} to {remote}")
        except subprocess.CalledProcessError as e:
            raise VCSError(f"Failed to push: {e}")
    
    def pull(self, path: Path, remote: str = 'origin', branch: str = 'main') -> None:
        """
        Pull from remote repository.
        
        Args:
            path: Repository path
            remote: Remote name
            branch: Branch name
            
        Raises:
            VCSError: If pull fails
        """
        try:
            self.runner.run(['git', 'pull', remote, branch, '--no-rebase'], cwd=path)
            logger.info(f"Pulled {branch} from {remote}")
        except subprocess.CalledProcessError as e:
            # Pull might fail if remote is empty, that's okay
            logger.debug(f"Pull from {remote}/{branch} returned error (might be empty): {e}")


class GitHubService:
    """Service for GitHub operations using gh CLI."""
    
    def __init__(self, runner: CommandRunner = None):
        """
        Initialize GitHubService.
        
        Args:
            runner: Command runner (defaults to SubprocessCommandRunner)
        """
        self.runner = runner or SubprocessCommandRunner()
    
    def repo_exists(self, owner: str, repo: str) -> bool:
        """
        Check if a GitHub repository exists.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            True if repository exists, False otherwise
        """
        try:
            self.runner.run(['gh', 'repo', 'view', f'{owner}/{repo}'])
            return True
        except subprocess.CalledProcessError:
            return False
    
    def create_repo(self, owner: str, repo: str, public: bool = True,
                    description: str = '') -> None:
        """
        Create a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            public: Whether repository should be public
            description: Repository description
            
        Raises:
            VCSError: If repository creation fails
        """
        try:
            visibility = '--public' if public else '--private'
            cmd = ['gh', 'repo', 'create', f'{owner}/{repo}', visibility, '--confirm']
            if description:
                cmd.extend(['--description', description])
            
            self.runner.run(cmd)
            logger.info(f"Created GitHub repository: {owner}/{repo}")
        except subprocess.CalledProcessError as e:
            raise VCSError(f"Failed to create repository {owner}/{repo}: {e}")
    
    def ensure_repo_exists(self, owner: str, repo: str, public: bool = True,
                          description: str = '') -> bool:
        """
        Ensure a GitHub repository exists, creating it if necessary.
        
        Args:
            owner: Repository owner
            repo: Repository name
            public: Whether repository should be public
            description: Repository description
            
        Returns:
            True if repository was created, False if it already existed
        """
        if self.repo_exists(owner, repo):
            logger.info(f"Repository {owner}/{repo} already exists")
            return False
        
        self.create_repo(owner, repo, public, description)
        return True
