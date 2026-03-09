"""Generic REST client with auth, retry, and timeout.

Uses `requests` (already a dep in the pipeline). All methods raise
RuntimeError on unrecoverable failure so callers can log and skip.
"""

import time
from typing import Any, Dict, Optional

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


class RestClient:
    """Lightweight authenticated HTTP client with retry logic.

    Args:
        base_url: Base URL, e.g. "https://api.openai.com/v1"
        auth_token: Bearer token for Authorization header.
        timeout: Seconds per request (default 60).
        max_retries: Number of retries on 429 / 5xx (default 3).
        retry_delay: Initial back-off in seconds, doubled each retry (default 2).
    """

    def __init__(
        self,
        base_url: str,
        auth_token: str,
        timeout: int = 60,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        if not _REQUESTS_AVAILABLE:
            raise RuntimeError("requests library not available; run: pip install requests")
        if not auth_token:
            raise RuntimeError("auth_token is required (set OPENAI_API_KEY env var)")
        self._base = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay

    def _url(self, path: str) -> str:
        return f"{self._base}/{path.lstrip('/')}"

    def _should_retry(self, status_code: int) -> bool:
        return status_code in (429, 500, 502, 503, 504)

    def get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request, returns parsed JSON."""
        delay = self._retry_delay
        for attempt in range(self._max_retries + 1):
            try:
                resp = _requests.get(
                    self._url(path),
                    headers=self._headers,
                    params=params,
                    timeout=self._timeout,
                )
                if self._should_retry(resp.status_code) and attempt < self._max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                resp.raise_for_status()
                return resp.json()
            except _requests.exceptions.RequestException as exc:
                if attempt < self._max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise RuntimeError(f"GET {path} failed: {exc}") from exc
        raise RuntimeError(f"GET {path} failed after {self._max_retries} retries")

    def post(self, path: str, json: Optional[Dict] = None, data: Optional[bytes] = None,
             extra_headers: Optional[Dict] = None) -> Dict[str, Any]:
        """POST request, returns parsed JSON."""
        headers = dict(self._headers)
        if extra_headers:
            headers.update(extra_headers)
        if data is not None:
            headers.pop("Content-Type", None)   # let requests set multipart boundary

        delay = self._retry_delay
        for attempt in range(self._max_retries + 1):
            try:
                if data is not None:
                    resp = _requests.post(
                        self._url(path), headers=headers, data=data, timeout=self._timeout
                    )
                else:
                    resp = _requests.post(
                        self._url(path), headers=headers, json=json, timeout=self._timeout
                    )
                if self._should_retry(resp.status_code) and attempt < self._max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                resp.raise_for_status()
                return resp.json()
            except _requests.exceptions.RequestException as exc:
                if attempt < self._max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise RuntimeError(f"POST {path} failed: {exc}") from exc
        raise RuntimeError(f"POST {path} failed after {self._max_retries} retries")

    def get_raw(self, path: str) -> bytes:
        """GET request, returns raw bytes (for file downloads)."""
        delay = self._retry_delay
        for attempt in range(self._max_retries + 1):
            try:
                resp = _requests.get(
                    self._url(path), headers=self._headers, timeout=self._timeout
                )
                if self._should_retry(resp.status_code) and attempt < self._max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                resp.raise_for_status()
                return resp.content
            except _requests.exceptions.RequestException as exc:
                if attempt < self._max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise RuntimeError(f"GET {path} (raw) failed: {exc}") from exc
        raise RuntimeError(f"GET {path} (raw) failed after {self._max_retries} retries")
