"""Anthropic Batch API client for cost-efficient bulk processing.

Workflow:
  1. build_request()    – build one batch request dict per story
  2. submit_batch()     – POST /v1/messages/batches → returns batch_id
  3. get_status()       – GET  /v1/messages/batches/{id} → processing_status
  4. retrieve_results() – GET  /v1/messages/batches/{id}/results → {custom_id: text}

Batch pricing: 50 % off standard rates.

References:
  https://docs.anthropic.com/en/docs/build-with-claude/batch-api
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_shared_dir = Path(__file__).parent.parent
_repo_root = _shared_dir.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from T._shared.api.rest_client import RestClient

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_BASE_URL = "https://api.anthropic.com"
ANTHROPIC_VERSION  = "2023-06-01"
ANTHROPIC_BETA     = "message-batches-2024-09-24"

# Default Claude model for review/polish (best reasoning quality)
CLAUDE_MODEL = os.getenv("PRISMQ_CLAUDE_MODEL", "claude-opus-4-6")

# Statuses
_ACTIVE_STATUSES = {"in_progress", "validating"}
_DONE_STATUS     = "ended"
_FAILED_STATUSES = {"errored", "expired", "canceled", "cancelling"}


class ClaudeBatchClient:
    """Manages the full lifecycle of an Anthropic Message Batch.

    Args:
        api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var).
        model: Claude model ID (defaults to CLAUDE_MODEL).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        key = api_key or ANTHROPIC_API_KEY
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self._client = RestClient(
            base_url=ANTHROPIC_BASE_URL,
            auth_token=key,
            timeout=60,
        )
        # Anthropic uses x-api-key instead of Bearer; we override via extra_headers
        self._api_key = key
        self._model = model or CLAUDE_MODEL

    def _headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self._api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "anthropic-beta": ANTHROPIC_BETA,
            "content-type": "application/json",
        }

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def build_request(
        self,
        custom_id: str,
        prompt: str,
        max_tokens: int,
        system: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build one request dict for the batch.

        Args:
            custom_id: Unique identifier (e.g. "story-123-review").
            prompt: User message content.
            max_tokens: Maximum output tokens.
            system: Optional system prompt.

        Returns:
            Dict representing one entry in the batch requests list.
        """
        params: Dict[str, Any] = {
            "model": self._model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            params["system"] = system

        return {
            "custom_id": custom_id,
            "params": params,
        }

    def submit_batch(self, requests: List[Dict[str, Any]]) -> str:
        """Submit a batch of message requests.

        Args:
            requests: List of dicts built by build_request().

        Returns:
            Anthropic batch ID (e.g. "msgbatch_01abc...").

        Raises:
            RuntimeError: On API error.
        """
        if not requests:
            raise ValueError("requests list is empty")

        try:
            import requests as _req
        except ImportError as exc:
            raise RuntimeError("requests library not available; run: pip install requests") from exc

        import json as _json
        resp = _req.post(
            f"{ANTHROPIC_BASE_URL}/v1/messages/batches",
            headers=self._headers(),
            data=_json.dumps({"requests": requests}),
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["id"]

    def get_status(self, batch_id: str) -> Dict[str, Any]:
        """Poll batch status.

        Returns:
            Full batch object. Key fields:
              - processing_status: "in_progress" | "ended" | "errored" | ...
              - request_counts: {processing, succeeded, errored, canceled, expired}
              - results_url: present when processing_status == "ended"
        """
        try:
            import requests as _req
        except ImportError as exc:
            raise RuntimeError("requests library not available") from exc

        resp = _req.get(
            f"{ANTHROPIC_BASE_URL}/v1/messages/batches/{batch_id}",
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def is_active(self, status: str) -> bool:
        return status in _ACTIVE_STATUSES

    def is_done(self, status: str) -> bool:
        return status == _DONE_STATUS

    def is_failed(self, status: str) -> bool:
        return status in _FAILED_STATUSES

    def retrieve_results(self, batch_id: str) -> Dict[str, Optional[str]]:
        """Download batch results and parse into {custom_id: response_text}.

        Streams JSONL results from the results URL.

        Returns:
            Dict mapping custom_id → text (or None if that request failed).
        """
        try:
            import requests as _req
        except ImportError as exc:
            raise RuntimeError("requests library not available") from exc

        resp = _req.get(
            f"{ANTHROPIC_BASE_URL}/v1/messages/batches/{batch_id}/results",
            headers=self._headers(),
            timeout=120,
        )
        resp.raise_for_status()

        results: Dict[str, Optional[str]] = {}
        for line in resp.text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                cid = obj.get("custom_id")
                result_type = obj.get("result", {}).get("type")
                if result_type == "succeeded":
                    message = obj["result"]["message"]
                    text = message["content"][0]["text"].strip()
                    results[cid] = text
                else:
                    results[cid] = None   # errored / canceled
            except Exception:
                continue

        return results
