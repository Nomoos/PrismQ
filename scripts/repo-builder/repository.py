#!/usr/bin/env python3
"""Repository operations for GitHub and local git repositories."""

import subprocess
from pathlib import Path
from typing import List


def repository_exists(repo_name: str) -> bool:
    """
    Check if a GitHub repository exists under the fixed OWNER.

    Args:
        repo_name: Repository name (e.g., 'PrismQ.MyModule')

    Returns:
        True if repository exists, False otherwise.
    """
    full_name = f"Nomoos/{repo_name}"
    try:
        # `gh repo view` exits with 0 if the repo exists, non-zero if not
        result = subprocess.run(
            ["gh", "repo", "view", full_name],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        # GitHub CLI not installed
        raise RuntimeError("GitHub CLI (gh) not installed or not on PATH")


def get_repository_path(repo_name: str, workspace: Path) -> Path:
    """
    Map PrismQ dotted repo name to local workspace path.

    Args:
        repo_name: Repository name (e.g., 'PrismQ.IdeaInspiration')
        workspace: The workspace root path

    Returns:
        Path object representing the repository location

    Rules:
    - 'PrismQ' -> WORKSPACE
    - 'PrismQ.Segment' -> WORKSPACE/src/Segment
    - 'PrismQ.A.B' -> WORKSPACE/src/A/src/B
    - etc.
    """
    if repo_name == "PrismQ":
        return workspace

    parts = repo_name.split(".")
    if parts[0] != "PrismQ":
        raise ValueError(f"Invalid repository name: {repo_name}")

    # start with root = WORKSPACE
    path = workspace
    # for každou část za "PrismQ" přidej src/<Segment>
    for segment in parts[1:]:
        path = path / "src" / segment

    return path


def create_git_chain(chain: List[str], workspace: Path) -> None:
    """
    Create or update a chain of repositories.

    Args:
        chain: List of repository names from root to deepest
        workspace: The workspace root path
    """
    for module in chain:
        repo_name = module
        repo_path = get_repository_path(repo_name, workspace)
        if repository_exists(repo_name):
            print(f"Repository {repo_name} already exists.")
            # exists locally git in repo_path
            if(repo_path / ".git").exists():
                print(f"Repository {repo_name} already cloned locally.")
                # pull changes
                try:
                    subprocess.run(
                        ["git", "-C", str(repo_path), "pull"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print(f"Repository {repo_name} updated successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to update repository {repo_name}. Error: {e.stderr}")
                except FileNotFoundError:
                    raise RuntimeError("Git not installed or not on PATH")

            else:
                print(f"Cloning repository {repo_name}...")
                # ensure parent directory exists
                repo_path.parent.mkdir(parents=True, exist_ok=True)
                # clone repo
                try:
                    subprocess.run(
                        [
                            "gh", "repo", "clone", f"Nomoos/{repo_name}",
                            str(repo_path)
                        ],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print(f"Repository {repo_name} cloned successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to clone repository {repo_name}. Error: {e.stderr}")
                    continue
                except FileNotFoundError:
                    raise RuntimeError("GitHub CLI (gh) not installed or not on PATH")
        else:
            print(f"Creating repository {repo_name} from template...")
            try:
                subprocess.run(
                    [
                        "gh", "repo", "create", f"Nomoos/{repo_name}",
                        "--template", "Nomoos/PrismQ.RepositoryTemplate",
                        "--public",
                        "--confirm"
                    ],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"Repository {repo_name} created successfully from template.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to create repository {repo_name}. Error: {e.stderr}")
                continue
            except FileNotFoundError:
                raise RuntimeError("GitHub CLI (gh) not installed or not on PATH")
