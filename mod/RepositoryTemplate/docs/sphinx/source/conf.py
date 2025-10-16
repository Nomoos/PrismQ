"""Sphinx configuration for PrismQ module documentation.

This configuration follows PEP 257 (docstring conventions) and provides
minimal setup for API documentation generation.
"""

import os
import sys
from pathlib import Path

# Add project root to path for autodoc
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Project information
project = "PrismQ Module Template"
copyright = "2025, PrismQ"  # noqa: A001
author = "PrismQ"
version = "0.1.0"
release = "0.1.0"

# General configuration
extensions = [
    "sphinx.ext.autodoc",  # Auto-generate documentation from docstrings
    "sphinx.ext.napoleon",  # Support for Google-style docstrings (PEP 257)
    "sphinx.ext.viewcode",  # Add links to highlighted source code
    "sphinx.ext.intersphinx",  # Link to other project documentation
    "sphinx.ext.todo",  # Support for todo items
    "sphinx.ext.coverage",  # Check documentation coverage
]

# Napoleon settings for Google-style docstrings (PEP 257)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Templates path
templates_path = ["_templates"]

# Exclude patterns
exclude_patterns = []

# HTML output options
html_theme = "alabaster"
html_static_path = ["_static"]
html_theme_options = {
    "description": "AI-powered content generation module template",
    "github_user": "Nomoos",
    "github_repo": "PrismQ.RepositoryTemplate",
    "fixed_sidebar": True,
    "show_powered_by": False,
}

# Autodoc options
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Todo extension
todo_include_todos = True
