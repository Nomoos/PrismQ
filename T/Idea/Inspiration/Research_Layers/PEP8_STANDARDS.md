# PEP 8 Standards - Quick Reference with Examples

**Python Enhancement Proposal 8 (PEP 8)** is the official style guide for Python code.

## Quick Summary

✅ **Follow these rules for consistent, readable code**

## 1. Code Layout

### Indentation
```python
# ✅ GOOD: 4 spaces per indentation level
def process_video(video_id: str) -> Video:
    if video_id:
        return fetch_video(video_id)
    return None

# ❌ BAD: Using tabs or 2 spaces
def process_video(video_id: str) -> Video:
  if video_id:  # 2 spaces - wrong!
      return fetch_video(video_id)
```

### Maximum Line Length
```python
# ✅ GOOD: Line length <= 79-88 characters (88 with Black formatter)
def calculate_relevance_score(
    title: str,
    description: str,
    categories: List[str]
) -> float:
    pass

# ❌ BAD: Line too long
def calculate_relevance_score(title: str, description: str, categories: List[str], keywords: List[str], weights: Dict[str, float]) -> float:
    pass
```

### Blank Lines
```python
# ✅ GOOD: 2 blank lines between top-level definitions

import os
import sys


class VideoProcessor:
    """Process videos."""
    pass


class AudioProcessor:
    """Process audio."""
    pass


def main():
    """Main function."""
    pass


# ✅ GOOD: 1 blank line between methods
class IdeaService:
    
    def create_idea(self) -> str:
        pass
    
    def update_idea(self, idea_id: str) -> None:
        pass
```

## 2. Imports

### Import Order
```python
# ✅ GOOD: Standard library, third-party, local
# 1. Standard library imports
import os
import sys
from datetime import datetime
from typing import List, Dict

# 2. Third-party imports
import requests
from pydantic import BaseModel

# 3. Local application imports
from prismq.model import IdeaInspiration
from prismq.classification import CategoryClassifier


# ❌ BAD: Mixed order, multiple imports per line
from prismq.model import IdeaInspiration
import os, sys  # Don't use comma-separated imports!
import requests
from typing import List
```

### Absolute vs Relative Imports
```python
# ✅ GOOD: Absolute imports (preferred)
from prismq.source.youtube import YouTubePlugin
from prismq.model import IdeaInspiration

# ✅ OK: Relative imports within package
from .youtube import YouTubePlugin
from ..model import IdeaInspiration

# ❌ BAD: Wildcard imports
from prismq.model import *  # Don't do this!
```

## 3. Naming Conventions

### General Rules
```python
# ✅ GOOD: Clear naming conventions

# Modules: lowercase with underscores
# idea_processor.py

# Classes: PascalCase
class VideoProcessor:
    pass

class IdeaInspiration:
    pass

# Functions/methods: snake_case
def calculate_score(data: str) -> float:
    pass

def fetch_video_metadata(video_id: str) -> Dict:
    pass

# Variables: snake_case
video_count = 0
max_retries = 3
api_key = "key123"

# Constants: UPPER_CASE
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

# Private attributes: leading underscore
class Service:
    def __init__(self):
        self._private_data = []
        self.__very_private = None  # Name mangling
```

### Naming Style Examples
```python
# ✅ GOOD: Descriptive names
def calculate_relevance_score(title: str, keywords: List[str]) -> float:
    keyword_matches = sum(1 for kw in keywords if kw in title)
    total_keywords = len(keywords)
    return keyword_matches / total_keywords if total_keywords > 0 else 0.0


# ❌ BAD: Unclear abbreviations
def calc_rel_sc(t: str, kw: List[str]) -> float:
    km = sum(1 for k in kw if k in t)
    tk = len(kw)
    return km / tk if tk > 0 else 0.0
```

## 4. Whitespace

### In Expressions
```python
# ✅ GOOD: Whitespace around operators, after commas
result = value1 + value2
my_list = [1, 2, 3, 4]
my_dict = {"key": "value", "count": 42}

def function(arg1, arg2, arg3):
    pass

# ❌ BAD: No whitespace or too much whitespace
result=value1+value2
my_list = [1,2,3,4]
my_dict = { "key" : "value" , "count" : 42 }
def function(arg1,arg2,arg3):
    pass
```

### Function Calls
```python
# ✅ GOOD: No space before parentheses
result = my_function(arg1, arg2)
my_list.append(item)

# ❌ BAD: Space before parentheses
result = my_function (arg1, arg2)
my_list.append (item)
```

### Slicing
```python
# ✅ GOOD: No spaces around colon in slices
my_list[1:5]
my_list[start:end]
my_list[::2]

# ❌ BAD: Spaces around colons
my_list[1 : 5]
my_list[start : end]
```

## 5. Comments

### Block Comments
```python
# ✅ GOOD: Complete sentences, proper formatting
# This function processes video metadata and extracts
# relevant information for classification. It handles
# multiple video formats and validates the data.
def process_video_metadata(metadata: Dict) -> Video:
    pass


# ❌ BAD: Incomplete sentences, poor formatting
#process video metadata
#handles multiple formats
def process_video_metadata(metadata: Dict) -> Video:
    pass
```

### Inline Comments
```python
# ✅ GOOD: Used sparingly for non-obvious logic
x = x + 1  # Compensate for border (if needed)

# ❌ BAD: Stating the obvious
x = x + 1  # Increment x (obvious!)
```

## 6. Documentation Strings (Docstrings)

### Module Docstrings
```python
# ✅ GOOD: Module-level docstring
"""
Video processing module for PrismQ.T.Idea.Inspiration.

This module provides functionality for processing video content
from various sources including YouTube, TikTok, and Vimeo.
"""

import os
from typing import List
```

### Function Docstrings
```python
# ✅ GOOD: Google-style docstring
def calculate_relevance_score(
    title: str,
    description: str,
    keywords: List[str]
) -> float:
    """Calculate relevance score for content.
    
    Analyzes title and description against provided keywords
    to compute a relevance score between 0.0 and 1.0.
    
    Args:
        title: Content title (required, non-empty)
        description: Content description (can be empty)
        keywords: List of keywords to match against
    
    Returns:
        Relevance score between 0.0 (irrelevant) and 1.0 (highly relevant)
    
    Raises:
        ValueError: If title is empty or keywords list is empty
    
    Example:
        >>> calculate_relevance_score(
        ...     "Python Tutorial",
        ...     "Learn Python basics",
        ...     ["python", "programming"]
        ... )
        0.85
    """
    pass
```

### Class Docstrings
```python
# ✅ GOOD: Class docstring with attributes
class VideoProcessor:
    """Process video content for idea extraction.
    
    This class handles video processing from various sources,
    including metadata extraction, validation, and classification.
    
    Attributes:
        api_key: API key for video service
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
    
    Example:
        >>> processor = VideoProcessor(api_key="key123")
        >>> video = processor.process("video_id")
    """
    
    def __init__(self, api_key: str, max_retries: int = 3):
        """Initialize video processor.
        
        Args:
            api_key: API key for authentication
            max_retries: Maximum retry attempts (default: 3)
        """
        self.api_key = api_key
        self.max_retries = max_retries
```

## 7. Type Hints (PEP 484)

```python
# ✅ GOOD: Complete type hints
from typing import List, Dict, Optional, Union

def process_videos(
    video_ids: List[str],
    options: Optional[Dict[str, str]] = None
) -> List[Video]:
    """Process multiple videos."""
    pass

def get_video(video_id: str) -> Optional[Video]:
    """Get video by ID, returns None if not found."""
    pass

def parse_response(response: Union[str, bytes]) -> Dict[str, Any]:
    """Parse response that can be string or bytes."""
    pass


# ❌ BAD: No type hints
def process_videos(video_ids, options=None):
    pass
```

## 8. String Quotes

```python
# ✅ GOOD: Consistent quote style (choose one and stick with it)
# Use double quotes for strings
message = "Hello, world!"
api_key = "abc123"

# Use single quotes for short strings or dict keys
status = 'active'
my_dict = {'key': 'value'}

# Use triple double-quotes for docstrings
"""This is a docstring."""


# ✅ GOOD: Use appropriate quotes to avoid escaping
text = "It's a beautiful day"  # No need to escape
text = 'He said "Hello"'       # No need to escape

# ❌ BAD: Unnecessary escaping
text = 'It\'s a beautiful day'
text = "He said \"Hello\""
```

## 9. Boolean Comparisons

```python
# ✅ GOOD: Simple boolean checks
if is_valid:
    pass

if not is_valid:
    pass

if my_list:  # Check if list is not empty
    pass


# ❌ BAD: Explicit comparison to True/False
if is_valid == True:
    pass

if is_valid is True:
    pass

if len(my_list) > 0:  # Use "if my_list:" instead
    pass
```

## 10. Checking for None

```python
# ✅ GOOD: Use "is" for None comparisons
if value is None:
    pass

if value is not None:
    pass


# ❌ BAD: Using == for None
if value == None:
    pass

if value != None:
    pass
```

## Tools to Enforce PEP 8

### 1. Black (Auto-formatter)
```bash
# Install
pip install black

# Format file
black my_file.py

# Format directory
black src/

# Check without modifying
black --check src/
```

### 2. Flake8 (Linter)
```bash
# Install
pip install flake8

# Check file
flake8 my_file.py

# Configuration in setup.cfg or .flake8
[flake8]
max-line-length = 88
exclude = .git,__pycache__,venv
ignore = E203,W503
```

### 3. isort (Import sorting)
```bash
# Install
pip install isort

# Sort imports
isort my_file.py

# Check without modifying
isort --check-only my_file.py
```

### 4. mypy (Type checking)
```bash
# Install
pip install mypy

# Check types
mypy my_file.py

# Configuration in mypy.ini or setup.cfg
[mypy]
python_version = 3.10
strict = True
```

## Quick Checklist

Before committing code, verify:

- [ ] 4 spaces for indentation (no tabs)
- [ ] Lines <= 88 characters (with Black)
- [ ] Imports properly organized (stdlib, third-party, local)
- [ ] Names follow conventions (snake_case, PascalCase, UPPER_CASE)
- [ ] Proper whitespace around operators and after commas
- [ ] Docstrings for all public modules, classes, and functions
- [ ] Type hints on all function parameters and returns
- [ ] Boolean comparisons use simple checks (not `== True`)
- [ ] None comparisons use `is` / `is not`
- [ ] Ran Black formatter
- [ ] Ran Flake8 linter
- [ ] Ran mypy type checker

## Configuration Files

### setup.cfg (recommended)
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv

[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

[isort]
profile = black
line_length = 88
```

### pyproject.toml (Black configuration)
```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | venv
  | build
  | dist
)/
'''
```

## Summary

✅ **Key Principles**:
1. Consistency is more important than the exact rule
2. Readable code is more important than clever code
3. Use automated tools (Black, Flake8, mypy)
4. Follow the project's existing style
5. Code is read more than written - optimize for reading

---

**References**:
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)
- [Black Code Style](https://black.readthedocs.io/)

**Last Updated**: 2025-11-14
