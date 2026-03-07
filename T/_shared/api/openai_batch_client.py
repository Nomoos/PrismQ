"""OpenAI Batch API client for cost-efficient bulk processing.

Workflow:
  1. build_request()   – build one JSONL line per story
  2. submit_batch()    – upload JSONL file, create batch, return openai_batch_id
  3. get_status()      – poll batch status (queued / in_progress / completed / failed)
  4. retrieve_results()– download and parse output JSONL into {custom_id: content} dict

Batch pricing: 50 % off standard rates. Completion window: 24 h.

References:
  https://platform.openai.com/docs/guides/batch
"""

import io
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_shared_dir = Path(__file__).parent.parent
_repo_root = _shared_dir.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from T._shared.api.api_config import (
    OPENAI_API_KEY, OPENAI_BASE_URL,
    GPT_MODEL, GPT_REASONING_EFFORT,
    BATCH_COMPLETION_WINDOW, BATCH_ENDPOINT,
    REQUEST_TIMEOUT,
)
from T._shared.api.rest_client import RestClient

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


# Batch statuses that mean "still running"
_ACTIVE_STATUSES = {"validating", "in_progress", "finalizing", "queued"}
# Batch statuses that mean "done successfully"
_DONE_STATUSES = {"completed"}
# Batch statuses that mean "failed"
_FAILED_STATUSES = {"failed", "expired", "cancelled", "cancelling"}


class OpenAIBatchClient:
    """Manages the full lifecycle of an OpenAI Batch API job.

    Args:
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var).
        model: Model ID (defaults to GPT_MODEL from api_config).
        reasoning_effort: Effort level for reasoning models.
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
        self._api_key = key

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
        """Build one JSONL entry for the batch request file.

        Args:
            custom_id: Unique identifier for this request (e.g. "story-123-review").
            prompt: User message text.
            max_tokens: Maximum output tokens.
            system: Optional system message.

        Returns:
            Dict representing one line in the JSONL input file.
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

        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": BATCH_ENDPOINT,
            "body": body,
        }

    def submit_batch(self, requests: List[Dict[str, Any]]) -> str:
        """Upload JSONL and create a batch job.

        Args:
            requests: List of dicts built by build_request().

        Returns:
            OpenAI batch job ID (e.g. "batch_abc123").

        Raises:
            RuntimeError: On upload or batch creation failure.
        """
        if not requests:
            raise ValueError("requests list is empty")

        # Encode JSONL
        jsonl_bytes = "\n".join(json.dumps(r) for r in requests).encode("utf-8")

        # Upload file using multipart/form-data (requests library)
        if not _REQUESTS_AVAILABLE:
            raise RuntimeError("requests library not available; run: pip install requests")

        upload_resp = _requests.post(
            f"{OPENAI_BASE_URL}/files",
            headers={"Authorization": f"Bearer {self._api_key}"},
            files={"file": ("batch_input.jsonl", io.BytesIO(jsonl_bytes), "application/jsonl")},
            data={"purpose": "batch"},
            timeout=REQUEST_TIMEOUT,
        )
        upload_resp.raise_for_status()
        file_id = upload_resp.json()["id"]

        # Create batch
        batch = self._client.post(
            "/batches",
            json={
                "input_file_id": file_id,
                "endpoint": BATCH_ENDPOINT,
                "completion_window": BATCH_COMPLETION_WINDOW,
            },
        )
        return batch["id"]

    def get_status(self, batch_id: str) -> Dict[str, Any]:
        """Poll batch status.

        Returns:
            Full batch object from OpenAI API. Key fields:
              - status: "queued" | "in_progress" | "completed" | "failed" | ...
              - request_counts: {total, completed, failed}
              - output_file_id: present when status == "completed"
              - error_file_id: present when some requests failed
        """
        return self._client.get(f"/batches/{batch_id}")

    def is_active(self, status: str) -> bool:
        """Return True if batch is still running."""
        return status in _ACTIVE_STATUSES

    def is_done(self, status: str) -> bool:
        """Return True if batch completed successfully."""
        return status in _DONE_STATUSES

    def is_failed(self, status: str) -> bool:
        """Return True if batch failed/expired/cancelled."""
        return status in _FAILED_STATUSES

    def retrieve_results(self, output_file_id: str) -> Dict[str, Optional[str]]:
        """Download output JSONL and parse into {custom_id: response_text}.

        Returns:
            Dict mapping custom_id → response text (or None if that request failed).
        """
        raw = self._client.get_raw(f"/files/{output_file_id}/content")
        results: Dict[str, Optional[str]] = {}
        for line in raw.decode("utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                cid = obj.get("custom_id")
                response = obj.get("response", {})
                status_code = response.get("status_code", 0)
                if status_code == 200:
                    body = response.get("body", {})
                    text = body["choices"][0]["message"]["content"].strip()
                    results[cid] = text
                else:
                    results[cid] = None   # request-level error
            except Exception:
                continue
        return results
