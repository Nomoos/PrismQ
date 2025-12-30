"""Ollama API client for local AI text generation.

This module handles communication with the Ollama API service.
It provides a general-purpose interface for interacting with local AI models.
Follows Single Responsibility Principle - only responsible for API communication.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class OllamaConfig:
    """Configuration for Ollama API client.
    
    Attributes:
        model: Name of the Ollama model to use
        api_base: Base URL for Ollama API
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
    """
    
    model: str = "qwen3:32b"  # Qwen3:30b for RTX 5090
    api_base: str = "http://localhost:11434"
    max_tokens: int = 2000
    timeout: int = 60


class OllamaClient:
    """Client for communicating with Ollama API.
    
    This class encapsulates all HTTP communication with the Ollama service,
    providing a clean interface for generating text completions from local AI models.
    Can be used for any text generation task (titles, content, summaries, etc.).
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """Initialize the Ollama client.
        
        Args:
            config: Ollama configuration. Uses defaults if not provided.
        """
        self.config = config or OllamaConfig()
        self._available: Optional[bool] = None
    
    def is_available(self) -> bool:
        """Check if Ollama service is available.
        
        Returns:
            True if Ollama is running and accessible, False otherwise
        """
        if self._available is not None:
            return self._available
        
        try:
            response = requests.get(
                f"{self.config.api_base}/api/tags",
                timeout=5
            )
            self._available = response.status_code == 200
            return self._available
        except Exception as e:
            logger.debug(f"Ollama availability check failed: {e}")
            self._available = False
            return False
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text completion using Ollama.
        
        Args:
            prompt: The input prompt for generation
            temperature: Sampling temperature (0.0-2.0)
            
        Returns:
            Generated text response
            
        Raises:
            RuntimeError: If API call fails or Ollama is unavailable
        """
        if not self.is_available():
            raise RuntimeError(
                f"Ollama not available at {self.config.api_base}. "
                "Ensure Ollama is running before generating text."
            )
        
        logger.debug(f"Sending prompt to Ollama (temperature={temperature})")
        
        try:
            response = requests.post(
                f"{self.config.api_base}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": self.config.max_tokens,
                    },
                },
                timeout=self.config.timeout,
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {e}")
            raise RuntimeError(f"Failed to generate text: {e}") from e
