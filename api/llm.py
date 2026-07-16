"""Centralized LLM access through a configurable gateway.

This module is the single place the app creates OpenAI-compatible clients.
By routing every call through here we can point the whole system at an LLM
gateway (Helicone, OpenRouter, Portkey, LiteLLM, ...) by setting env vars,
without touching agent code. Falls back to talking to OpenAI directly when no
gateway is configured, so the app keeps working out of the box.

Simplest setup (Helicone proxy, reuses your OpenAI key):
    Just set HELICONE_API_KEY. The base URL and the Helicone-Auth header are
    filled in automatically, and OPENAI_API_KEY is used as the upstream key.
    Chat and embeddings both flow through Helicone, so its dashboard shows
    everything (this also covers the "monitoring tool" component).

Env vars
--------
HELICONE_API_KEY       If set, routes chat + embeddings through the Helicone
                       proxy (https://oai.helicone.ai/v1) and adds the required
                       Helicone-Auth header. Upstream key = OPENAI_API_KEY.
LLM_GATEWAY_BASE_URL   Override the gateway base URL (e.g. an OpenRouter or
                       Portkey endpoint). Takes precedence over the Helicone
                       default. If neither is set, calls go directly to OpenAI.
LLM_GATEWAY_API_KEY    API key sent as the Authorization bearer to the gateway.
                       Falls back to OPENAI_API_KEY.
LLM_GATEWAY_HEADERS    Optional extra headers as a JSON object string.
LLM_CHAT_MODEL         Chat model id. Default "gpt-5-nano" (correct for
                       Helicone/OpenAI; OpenRouter would use "openai/gpt-5-nano").
EMBED_MODEL            Embedding model id. Default "text-embedding-3-small".
EMBED_DIM              Embedding dimension. Default 1536.
OPENAI_API_KEY         Upstream key for OpenAI (chat fallback + embeddings).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

from openai import OpenAI  # type: ignore

CHAT_MODEL = os.environ.get("LLM_CHAT_MODEL", "gpt-5-nano")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")
EMBED_DIM = int(os.environ.get("EMBED_DIM", "1536"))

# Reasoning effort for gpt-5-class models. "minimal"/"low" are dramatically
# faster than the default. Set LLM_REASONING_EFFORT="" to disable the param
# (e.g. for models that don't support it).
REASONING_EFFORT = os.environ.get("LLM_REASONING_EFFORT", "minimal")

HELICONE_PROXY_URL = "https://oai.helicone.ai/v1"


def chat_completion(messages, response_format=None, model=None):
    """Single entry point for chat completions.

    Adds reasoning_effort (big latency win on gpt-5 models) and transparently
    retries without it if the model/gateway rejects the parameter, so a model
    that doesn't support reasoning_effort still works.
    """
    client = chat_client()
    kwargs: dict = {"model": model or CHAT_MODEL, "messages": messages}
    if response_format is not None:
        kwargs["response_format"] = response_format

    if REASONING_EFFORT:
        try:
            return client.chat.completions.create(reasoning_effort=REASONING_EFFORT, **kwargs)
        except Exception as exc:  # noqa: BLE001 - only swallow the reasoning-param case
            msg = str(exc).lower()
            if "reasoning" not in msg and "unsupported" not in msg and "unexpected keyword" not in msg:
                raise
            # Fall through and retry without the parameter.
    return client.chat.completions.create(**kwargs)


def _gateway_headers() -> dict | None:
    """Extra headers to send to the gateway (e.g. Helicone auth)."""
    headers: dict[str, str] = {}
    helicone = os.environ.get("HELICONE_API_KEY")
    if helicone:
        headers["Helicone-Auth"] = f"Bearer {helicone}"
    extra = os.environ.get("LLM_GATEWAY_HEADERS")
    if extra:
        try:
            headers.update(json.loads(extra))
        except (json.JSONDecodeError, TypeError):
            pass
    return headers or None


def _resolve_base_url() -> str | None:
    """Explicit gateway URL wins; else default to Helicone proxy if keyed."""
    explicit = os.environ.get("LLM_GATEWAY_BASE_URL")
    if explicit:
        return explicit
    if os.environ.get("HELICONE_API_KEY"):
        return HELICONE_PROXY_URL
    return None


def _upstream_key() -> str | None:
    return os.environ.get("LLM_GATEWAY_API_KEY") or os.environ.get("OPENAI_API_KEY")


@lru_cache(maxsize=1)
def chat_client() -> OpenAI:
    """OpenAI-compatible client for chat completions, via the gateway if set."""
    base_url = _resolve_base_url()
    if base_url:
        return OpenAI(base_url=base_url, api_key=_upstream_key(), default_headers=_gateway_headers())
    # No gateway configured -> talk to OpenAI directly.
    return OpenAI()


@lru_cache(maxsize=1)
def embed_client() -> OpenAI:
    """Client used for embeddings.

    Routed through the same gateway when one is configured (Helicone proxies the
    embeddings route too). Set EMBED_GATEWAY_BASE_URL to override, or it falls
    back to calling OpenAI directly.
    """
    base_url = os.environ.get("EMBED_GATEWAY_BASE_URL") or _resolve_base_url()
    if base_url:
        return OpenAI(base_url=base_url, api_key=_upstream_key(), default_headers=_gateway_headers())
    return OpenAI()


def gateway_active() -> bool:
    """True when traffic is routed through a gateway (for logging/health)."""
    return bool(_resolve_base_url())
