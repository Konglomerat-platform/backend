"""Gemini client wrapper for the business assistant.

The assistant must never go dark because of an upstream problem, so every
failure mode here — missing key, network error, timeout, safety block, empty
candidate — is funnelled into a single `None` return. Callers treat `None` as
"fall back to the scripted reply" rather than as an exception to propagate.
"""

from __future__ import annotations

import logging
import threading

from django.conf import settings

logger = logging.getLogger(__name__)

_client = None
_client_lock = threading.Lock()


def is_enabled() -> bool:
    return bool(getattr(settings, "GEMINI_API_KEY", ""))


def _get_client():
    """Build the client once and reuse it across requests.

    google-genai holds an httpx pool internally; constructing a client per
    request would leak connections under load.
    """
    global _client
    if _client is not None:
        return _client
    with _client_lock:
        if _client is None:
            from google import genai

            _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def reset_client() -> None:
    """Drop the cached client. Used by tests that swap settings."""
    global _client
    with _client_lock:
        _client = None


def _timeout_ms() -> int:
    """Request timeout in milliseconds, never unbounded.

    google-genai treats a falsy timeout as "no limit", so a misconfigured 0 or
    a negative value would let a hung upstream request occupy a worker
    indefinitely. The floor of one second keeps the request bounded whatever
    the environment says. The SDK field is typed `int | None`, so a float here
    fails validation — hence the explicit int().
    """
    return max(1, int(settings.GEMINI_TIMEOUT_SECONDS)) * 1000


def generate(system_instruction: str, prompt: str) -> str | None:
    """Return the model's text, or None if the call could not be completed."""
    if not is_enabled():
        return None

    try:
        from google.genai import types

        response = _get_client().models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                # This is a short-answer chat widget; the extra latency and
                # billed thought tokens of the default thinking budget buy
                # nothing here.
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                http_options=types.HttpOptions(timeout=_timeout_ms()),
            ),
        )
    except Exception:
        # Deliberately broad: a chat widget must not surface upstream SDK
        # exceptions, and the caller has a scripted answer ready.
        logger.exception("Gemini request failed")
        return None

    text = (getattr(response, "text", None) or "").strip()
    if not text:
        # Safety blocks and token-limit truncation both yield no usable text.
        logger.warning("Gemini returned no usable text")
        return None
    return text
