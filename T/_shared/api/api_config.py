"""OpenAI API configuration for PrismQ cloud steps (18-21).

Override any value via environment variable.
"""

import os

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
# gpt-5.2 — Lechmazur writing benchmark rank #3 (score 8.511), medium reasoning.
# Supports reasoning_effort in Chat Completions API.
# Override to "gpt-5.2-pro" (higher quality) or "o4-mini" (lower cost).
GPT_MODEL = os.getenv("PRISMQ_GPT_MODEL", "gpt-5.2")
GPT_REASONING_EFFORT = os.getenv("PRISMQ_GPT_REASONING_EFFORT", "medium")

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = "https://api.openai.com/v1"

# ---------------------------------------------------------------------------
# Token limits
# ---------------------------------------------------------------------------
MAX_TOKENS_REVIEW = 800     # Score + feedback only
MAX_TOKENS_POLISH = 2500    # Full improved title + content

# ---------------------------------------------------------------------------
# Content truncation
# ---------------------------------------------------------------------------
MAX_CONTENT_LENGTH = 4000   # Characters sent to GPT for review/polish

# ---------------------------------------------------------------------------
# Batch API
# ---------------------------------------------------------------------------
BATCH_COMPLETION_WINDOW = "24h"
BATCH_ENDPOINT = "/v1/chat/completions"

# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
REQUEST_TIMEOUT = 60        # Seconds for direct (non-batch) API calls
