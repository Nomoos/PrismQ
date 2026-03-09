"""OpenAI Chat Completions client for direct (non-batch) calls.

Used for testing prompts and one-off requests. Production flow uses
openai_batch_client for cost-effective batch processing.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

_shared_dir = Path(__file__).parent.parent
_repo_root = _shared_dir.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from T._shared.api.api_config import (
    OPENAI_API_KEY, OPENAI_BASE_URL,
    GPT_MODEL, GPT_REASONING_EFFORT,
    MAX_TOKENS_REVIEW, REQUEST_TIMEOUT,
)
from T._shared.api.rest_client import RestClient


class OpenAIClient:
    """Thin wrapper around RestClient for OpenAI Chat Completions API.

    Args:
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var).
        model: Model ID (defaults to GPT_MODEL from api_config).
        reasoning_effort: Reasoning effort level for o-series models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
    ):
        key = api_key or OPENAI_API_KEY
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self._client = RestClient(
            base_url=OPENAI_BASE_URL,
            auth_token=key,
            timeout=REQUEST_TIMEOUT,
        )
        self._model = model or GPT_MODEL
        self._reasoning_effort = reasoning_effort or GPT_REASONING_EFFORT

    def chat(
        self,
        prompt: str,
        max_tokens: int = MAX_TOKENS_REVIEW,
        system: Optional[str] = None,
    ) -> str:
        """Send a chat completion request and return the text response.

        Args:
            prompt: User message content.
            max_tokens: Maximum output tokens.
            system: Optional system message.

        Returns:
            Response text.

        Raises:
            RuntimeError: On API error.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        body: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "max_completion_tokens": max_tokens,
        }
        if self._reasoning_effort:
            body["reasoning_effort"] = self._reasoning_effort

        result = self._client.post("/chat/completions", json=body)

        try:
            return result["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Unexpected OpenAI response format: {result}") from exc
