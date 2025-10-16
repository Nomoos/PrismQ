"""Tests for VCS operations (Git and GitHub).

Tests use mocks to avoid real network/filesystem operations.
"""

import pytest
from unittest.mock import Mock, MagicMock, call
from pathlib import Path
import subprocess

from ..core.vcs import (
    GitService,
    GitHubService,
    SubprocessCommandRunner,
    VCSError
)


class TestGitService:
    """Test suite for GitService."""
    
    @pytest.fixture
    def mock_runner(self):
        """Create a mock command runner."""
        runner = Mock()
        runner.run = Mock(return_value=Mock(returncode=0, stdout='', stderr=''))
        return runner
    
    @pytest.fixture
    def git_service(self, mock_runner):
        """Create GitService with mocked runner."""
        return GitService(runner=mock_runner)
    
    def test_init_repo_creates_new_repo(self, git_service, mock_runner, tmp_path):
        """Test initializing a new git repository."""
        git_service.init_repo(tmp_path)
        
        mock_runner.run.assert_called_once_with(
            ['git', 'init', '-b', 'main'],
            cwd=tmp_path
        )
    
    def test_init_repo_skips_if_exists(self, git_service, mock_runner, tmp_path):
        """Test that init skips if .git already exists."""
        (tmp_path / '.git').mkdir()
        
        git_service.init_repo(tmp_path)
        
        # Should not call git init
        mock_runner.run.assert_not_called()
    
    def test_init_repo_custom_branch(self, git_service, mock_runner, tmp_path):
        """Test initializing repo with custom branch name."""
        git_service.init_repo(tmp_path, branch='develop')
        
        mock_runner.run.assert_called_once_with(
            ['git', 'init', '-b', 'develop'],
            cwd=tmp_path
        )
    
    def test_add_remote_new(self, git_service, mock_runner, tmp_path):
        """Test adding a new remote."""
        # Mock get-url to fail (remote doesn't exist)
        mock_runner.run.side_effect = [
            Mock(returncode=1),  # get-url fails
            Mock(returncode=0)   # add succeeds
        ]
        
        git_service.add_remote(tmp_path, 'origin', 'https://github.com/test/repo.git')
        
        assert mock_runner.run.call_count == 2
        # Should try get-url first, then add
        calls = mock_runner.run.call_args_list
        assert calls[0][0][0] == ['git', 'remote', 'get-url', 'origin']
        assert calls[1][0][0] == ['git', 'remote', 'add', 'origin', 'https://github.com/test/repo.git']
    
    def test_add_remote_update_existing(self, git_service, mock_runner, tmp_path):
        """Test updating existing remote with different URL."""
        # Mock get-url to return different URL
        mock_runner.run.side_effect = [
            Mock(returncode=0, stdout='https://github.com/old/repo.git\n'),
            Mock(returncode=0)  # set-url succeeds
        ]
        
        git_service.add_remote(tmp_path, 'origin', 'https://github.com/new/repo.git')
        
        # Should call set-url to update
        calls = mock_runner.run.call_args_list
        assert calls[1][0][0] == ['git', 'remote', 'set-url', 'origin', 'https://github.com/new/repo.git']
    
    def test_commit(self, git_service, mock_runner, tmp_path):
        """Test creating a commit."""
        git_service.commit(tmp_path, "Test commit")
        
        # Should call git add and git commit
        assert mock_runner.run.call_count == 2
        calls = mock_runner.run.call_args_list
        assert calls[0][0][0] == ['git', 'add', '.']
        assert calls[1][0][0] == ['git', 'commit', '-m', 'Test commit']
    
    def test_push(self, git_service, mock_runner, tmp_path):
        """Test pushing to remote."""
        git_service.push(tmp_path, 'origin', 'main')
        
        mock_runner.run.assert_called_once_with(
            ['git', 'push', 'origin', 'main'],
            cwd=tmp_path
        )
    
    def test_pull(self, git_service, mock_runner, tmp_path):
        """Test pulling from remote."""
        git_service.pull(tmp_path, 'origin', 'main')
        
        mock_runner.run.assert_called_once_with(
            ['git', 'pull', 'origin', 'main', '--no-rebase'],
            cwd=tmp_path
        )
    
    def test_pull_handles_errors_gracefully(self, git_service, mock_runner, tmp_path):
        """Test that pull doesn't raise on errors (empty remote is ok)."""
        mock_runner.run.side_effect = subprocess.CalledProcessError(1, 'git')
        
        # Should not raise
        git_service.pull(tmp_path)


class TestGitHubService:
    """Test suite for GitHubService."""
    
    @pytest.fixture
    def mock_runner(self):
        """Create a mock command runner."""
        runner = Mock()
        runner.run = Mock(return_value=Mock(returncode=0, stdout='', stderr=''))
        return runner
    
    @pytest.fixture
    def github_service(self, mock_runner):
        """Create GitHubService with mocked runner."""
        return GitHubService(runner=mock_runner)
    
    def test_repo_exists_true(self, github_service, mock_runner):
        """Test checking if repository exists (it does)."""
        mock_runner.run.return_value = Mock(returncode=0)
        
        result = github_service.repo_exists('Nomoos', 'PrismQ.Test')
        
        assert result is True
        mock_runner.run.assert_called_once_with(
            ['gh', 'repo', 'view', 'Nomoos/PrismQ.Test']
        )
    
    def test_repo_exists_false(self, github_service, mock_runner):
        """Test checking if repository exists (it doesn't)."""
        mock_runner.run.side_effect = subprocess.CalledProcessError(1, 'gh')
        
        result = github_service.repo_exists('Nomoos', 'PrismQ.Test')
        
        assert result is False
    
    def test_create_repo_public(self, github_service, mock_runner):
        """Test creating a public repository."""
        github_service.create_repo('Nomoos', 'PrismQ.Test', public=True, description='Test repo')
        
        mock_runner.run.assert_called_once()
        cmd = mock_runner.run.call_args[0][0]
        assert cmd[:4] == ['gh', 'repo', 'create', 'Nomoos/PrismQ.Test']
        assert '--public' in cmd
        assert '--confirm' in cmd
        assert '--description' in cmd
        assert 'Test repo' in cmd
    
    def test_create_repo_private(self, github_service, mock_runner):
        """Test creating a private repository."""
        github_service.create_repo('Nomoos', 'PrismQ.Test', public=False)
        
        cmd = mock_runner.run.call_args[0][0]
        assert '--private' in cmd
    
    def test_ensure_repo_exists_creates_new(self, github_service, mock_runner):
        """Test ensure_repo_exists when repo doesn't exist."""
        # First call (check exists) fails, second call (create) succeeds
        mock_runner.run.side_effect = [
            subprocess.CalledProcessError(1, 'gh'),  # repo_exists check
            Mock(returncode=0)  # create_repo
        ]
        
        created = github_service.ensure_repo_exists('Nomoos', 'PrismQ.Test')
        
        assert created is True
        assert mock_runner.run.call_count == 2
    
    def test_ensure_repo_exists_already_exists(self, github_service, mock_runner):
        """Test ensure_repo_exists when repo already exists."""
        mock_runner.run.return_value = Mock(returncode=0)
        
        created = github_service.ensure_repo_exists('Nomoos', 'PrismQ.Test')
        
        assert created is False
        # Only one call (repo_exists check)
        assert mock_runner.run.call_count == 1


class TestSubprocessCommandRunner:
    """Test suite for SubprocessCommandRunner."""
    
    def test_run_command_success(self, tmp_path):
        """Test running a successful command."""
        runner = SubprocessCommandRunner()
        result = runner.run(['echo', 'test'], cwd=tmp_path)
        
        assert result.returncode == 0
        assert 'test' in result.stdout
    
    def test_run_command_failure_raises(self, tmp_path):
        """Test that failed command raises when check=True."""
        runner = SubprocessCommandRunner()
        
        with pytest.raises(subprocess.CalledProcessError):
            runner.run(['false'], cwd=tmp_path, check=True)
    
    def test_run_command_failure_no_raise(self, tmp_path):
        """Test that failed command doesn't raise when check=False."""
        runner = SubprocessCommandRunner()
        result = runner.run(['false'], cwd=tmp_path, check=False)
        
        assert result.returncode != 0
