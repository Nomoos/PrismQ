"""Prompt template loading for title generation.

This module handles loading and managing prompt templates from the _meta/prompts directory.
Follows Single Responsibility Principle - only responsible for prompt file I/O.
"""

from pathlib import Path
from typing import Optional


class PromptLoader:
    """Load prompt templates from the prompts directory.
    
    This class is responsible for reading prompt template files and providing
    them to title generation components. It encapsulates all file I/O operations
    related to prompts.
    """
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        """Initialize the prompt loader.
        
        Args:
            prompts_dir: Directory containing prompt files. If None, uses default
                        location (_meta/prompts relative to this file's parent).
        """
        if prompts_dir is None:
            current_file = Path(__file__)
            self._prompts_dir = current_file.parent.parent / "_meta" / "prompts"
        else:
            self._prompts_dir = prompts_dir
    
    def load(self, filename: str) -> str:
        """Load a prompt template from file.
        
        Args:
            filename: Name of the prompt file (e.g., 'title_generation.txt')
            
        Returns:
            The prompt text content
            
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
        """
        prompt_path = self._prompts_dir / filename
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8")
    
    def get_title_generation_prompt(self) -> str:
        """Load the literary-focused title generation prompt.
        
        This is the canonical prompt for generating titles from Ideas.
        It emphasizes emotional essence, symbolism, and book-style titles.
        
        Returns:
            The title generation prompt template with {IDEA} placeholder
        """
        return self.load("title_generation.txt")
