"""Template synchronization for PrismQ modules.

Handles copying template files and syncing missing files/folders
to existing repositories.

PEP 257: Comprehensive docstrings
PEP 484: Type hints throughout
"""

from pathlib import Path
from typing import Set, List
import shutil
import logging

logger = logging.getLogger(__name__)


class TemplateSyncError(Exception):
    """Raised when template sync operations fail."""
    pass


class TemplateService:
    """Service for template operations and synchronization."""
    
    # Files that should not be copied from template
    EXCLUDED_FILES: Set[str] = {
        '.git', 'module.json', 'README.md', 'pyproject.toml',
        '.gitignore'  # Let each module have its own
    }
    
    def __init__(self, template_dir: Path):
        """
        Initialize TemplateService.
        
        Args:
            template_dir: Path to template directory (e.g., src/RepositoryTemplate)
        """
        self.template_dir = template_dir
    
    def copy_template_structure(self, target_dir: Path) -> None:
        """
        Copy template structure to target directory.
        
        Args:
            target_dir: Destination directory
            
        Raises:
            TemplateSyncError: If copy operation fails
        """
        if not self.template_dir.exists():
            raise TemplateSyncError(f"Template directory not found: {self.template_dir}")
        
        # Check for circular reference (target inside template)
        try:
            target_dir.resolve().relative_to(self.template_dir.resolve())
            raise TemplateSyncError(
                "Cannot copy template - target is subdirectory of template"
            )
        except ValueError:
            # Not a subdirectory, safe to proceed
            pass
        
        try:
            shutil.copytree(
                self.template_dir,
                target_dir,
                ignore=self._ignore_patterns,
                dirs_exist_ok=True
            )
            logger.info(f"Copied template structure to {target_dir}")
        except Exception as e:
            raise TemplateSyncError(f"Failed to copy template: {e}")
    
    def sync_missing_files(self, target_dir: Path) -> List[Path]:
        """
        Sync missing files/folders from template to target.
        
        This is the "smart sync" that adds missing template files
        to an existing repository without overwriting existing files.
        
        Args:
            target_dir: Target directory to sync to
            
        Returns:
            List of paths that were added
            
        Raises:
            TemplateSyncError: If sync operation fails
        """
        if not self.template_dir.exists():
            raise TemplateSyncError(f"Template directory not found: {self.template_dir}")
        
        if not target_dir.exists():
            raise TemplateSyncError(f"Target directory not found: {target_dir}")
        
        added_paths: List[Path] = []
        
        try:
            for item in self._walk_template():
                rel_path = item.relative_to(self.template_dir)
                target_path = target_dir / rel_path
                
                if not target_path.exists():
                    # Missing file/folder, copy it
                    if item.is_dir():
                        target_path.mkdir(parents=True, exist_ok=True)
                        logger.debug(f"Created directory: {rel_path}")
                    else:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_path)
                        logger.debug(f"Copied file: {rel_path}")
                    
                    added_paths.append(rel_path)
            
            if added_paths:
                logger.info(f"Synced {len(added_paths)} missing items from template")
            else:
                logger.info("No missing items to sync from template")
            
            return added_paths
            
        except Exception as e:
            raise TemplateSyncError(f"Failed to sync template files: {e}")
    
    def create_basic_structure(self, target_dir: Path) -> None:
        """
        Create basic module structure when template is not available.
        
        Args:
            target_dir: Directory where to create structure
            
        Raises:
            TemplateSyncError: If creation fails
        """
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Create standard directories
            dirs = [
                'src',
                'tests',
                'docs',
                'scripts',
                'issues/new',
                'issues/wip',
                'issues/done',
                '.github/ISSUE_TEMPLATE'
            ]
            
            for dir_path in dirs:
                (target_dir / dir_path).mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py
            init_file = target_dir / 'src' / '__init__.py'
            init_file.write_text('"""Module package initialization."""\n\n__version__ = "0.1.0"\n')
            
            # Create .gitignore
            gitignore = target_dir / '.gitignore'
            gitignore.write_text(self._get_default_gitignore())
            
            logger.info(f"Created basic module structure at {target_dir}")
            
        except Exception as e:
            raise TemplateSyncError(f"Failed to create basic structure: {e}")
    
    def _ignore_patterns(self, directory: str, files: List[str]) -> Set[str]:
        """
        Determine which files to ignore during copy.
        
        Args:
            directory: Directory being processed
            files: List of files in directory
            
        Returns:
            Set of file names to ignore
        """
        return self.EXCLUDED_FILES.intersection(files)
    
    def _walk_template(self) -> List[Path]:
        """
        Walk template directory and return all files/folders.
        
        Returns:
            List of Path objects for all items in template
        """
        items: List[Path] = []
        
        for item in self.template_dir.rglob('*'):
            # Skip excluded items and their contents
            if any(excluded in item.parts for excluded in self.EXCLUDED_FILES):
                continue
            items.append(item)
        
        return items
    
    @staticmethod
    def _get_default_gitignore() -> str:
        """Get default .gitignore content."""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/
dist/
build/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Local env
.env
.env.local
"""
