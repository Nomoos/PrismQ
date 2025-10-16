"""Module structure creation utilities."""

import shutil
from pathlib import Path
import click
from git import Repo, GitCommandError


def create_module_structure(
    module_dir: Path,
    module_name: str,
    repo_name: str,
    github_owner: str,
    remote_url: str,
    description: str,
    repo_root: Path
) -> bool:
    """
    Create the module directory structure and initial files.
    
    Args:
        module_dir: Path where the module will be created
        module_name: Name of the module
        repo_name: Repository name
        github_owner: GitHub owner/organization
        remote_url: Remote repository URL
        description: Module description
        repo_root: Root of the main repository
        
    Returns:
        True if successful, False otherwise
    """
    if module_dir.exists():
        # Check if it's a git repository that we can pull from
        if (module_dir / '.git').exists():
            click.echo(f"Module directory '{module_dir}' already exists as git repository")
            click.echo(f"Pulling latest changes from {repo_name}...")
            
            try:
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
    template_dir = repo_root / "src" / "RepositoryTemplate"
    
    if template_dir.exists():
        click.echo("Using RepositoryTemplate as base structure...")
        _copy_template(template_dir, module_dir)
    else:
        click.echo("RepositoryTemplate not found, creating basic structure...")
        _create_basic_structure(module_dir)
    
    # Create custom configuration files
    _create_module_config(module_dir, module_name, repo_name, github_owner, remote_url, description)
    
    return True


def _copy_template(template_dir: Path, module_dir: Path):
    """Copy template structure, excluding git-related files."""
    # Check if module_dir is a subdirectory of template_dir
    # This would cause infinite recursion during copy
    try:
        module_dir.resolve().relative_to(template_dir.resolve())
        # If we get here, module_dir is inside template_dir - cannot copy!
        click.echo("Warning: Cannot copy template - target is subdirectory of template")
        click.echo("Creating basic structure instead...")
        _create_basic_structure(module_dir)
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
        _create_basic_structure(module_dir)


def _create_basic_structure(module_dir: Path):
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
../scripts/setup.sh
```

### Run

```bash
# Windows
scripts\\quickstart.bat

# Linux/macOS (development only)
../scripts/quickstart.sh
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
