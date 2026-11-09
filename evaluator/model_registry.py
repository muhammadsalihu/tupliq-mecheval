"""
Canonical MechEval model roster + endpoint resolution.

Short display names resolve to fully-qualified, provider-prefixed model ids. A bare name like
``gpt-6-luna`` is a README display name, not an API model id, and is rejected with HTTP 400 — so
every name must resolve here before a run starts, and :func:`validate_roster` checks the ids
against the endpoint's own catalogue.

The endpoint is configurable (``MECHEVAL_BASE_URL``, else ``OPENAI_BASE_URL``); the catalogue URL
derives from it unless ``MECHEVAL_MODELS_URL`` overrides it. Pricing for the cost column is read
from that same catalogue, so a reported cost is the endpoint's price for the model actually called.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Dict, Iterable, List, Optional, Tuple

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


class UnknownModelError(ValueError):
    """A requested model is neither a roster short name nor a provider-prefixed id."""


#: short name -> (model id, human label, note)
ROSTER = {
    "gpt-6-luna": ("openai/gpt-6-luna", "GPT-6 Luna", "frontier OpenAI, flash-class"),
    "deepseek-4.1-flash": ("deepseek/deepseek-v4.1-flash", "DeepSeek 4.1 Flash", "cheapest reasoning-class"),
    "glm-5.3-flash": ("z-ai/glm-5.3-flash", "GLM 5.3 Flash", "Z.ai flash-class"),
    "haiku-5.5": ("anthropic/claude-haiku-5.5", "Haiku 5.5", "cheapest Claude-class at evaluation time"),
}


def base_url() -> str:
    """Chat-completions endpoint actually used for a run (no trailing slash)."""
    return (os.getenv("MECHEVAL_BASE_URL") or os.getenv("OPENAI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")


def models_url() -> str:
    """Catalogue endpoint: explicit override, else derived from :func:`base_url`."""
    explicit = os.getenv("MECHEVAL_MODELS_URL")
    if explicit:
        return explicit
    base = base_url()
    if base.endswith("/v1"):
        return f"{base}/models"
    return f"{base}/v1/models" if "/api" in base else f"{base}/models"


def api_key() -> Optional[str]:
    """Credential for the endpoint, in the order a run resolves it."""
    return os.getenv("MECHEVAL_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")


def slugs() -> List[str]:
    """Every roster model id, in declaration order (the default run order)."""
    return [entry[0] for entry in ROSTER.values()]


def label_for(model: str) -> str:
    """Human label for a roster model id, else the id itself."""
    for name, (slug, label, _note) in ROSTER.items():
        if model in (slug, name):
            return label
    return model


def resolve(model: str) -> str:
    """``'gpt-6-luna'`` or ``'openai/gpt-6-luna'`` -> ``'openai/gpt-6-luna'``.

    Raises :class:`UnknownModelError` for anything else, so a typo aborts the run instead of
    being scored as a model failure.
    """
    name = (model or "").strip()
    if name in ROSTER:
        return ROSTER[name][0]
    if "/" in name:
        return name  # already provider-prefixed: pass through
    raise UnknownModelError(
        f"Unknown model '{model}'. Roster short names: {', '.join(ROSTER)} "
        f"— or pass a provider-prefixed model id (e.g. 'deepseek/deepseek-v4.1-flash')."
    )


def resolve_all(models: Iterable[str]) -> List[str]:
    return [resolve(m) for m in models]


def fetch_catalogue(url: Optional[str] = None, timeout: int = 30) -> List[dict]:
    """Catalogue entries from the active endpoint (the ``data`` list of its /models payload)."""
    target = url or models_url()
    headers = {"User-Agent": "mecheval/1.0", "Accept": "application/json"}
    key = api_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(target, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (URL comes from config)
        payload = json.loads(resp.read().decode("utf-8"))
    return payload.get("data", [])


def catalogue_ids(entries: Optional[List[dict]] = None) -> List[str]:
    """Every model id the endpoint advertises (fetches the catalogue when not supplied)."""
    return [m.get("id", "") for m in (entries if entries is not None else fetch_catalogue())]


def pricing_map(entries: Optional[List[dict]] = None) -> Dict[str, Tuple[float, float]]:
    """``{model_id: (prompt_usd_per_token, completion_usd_per_token)}`` from the catalogue."""
    out: Dict[str, Tuple[float, float]] = {}
    for entry in (entries if entries is not None else fetch_catalogue()):
        mid, pricing = entry.get("id"), entry.get("pricing") or {}
        if not mid or not isinstance(pricing, dict):
            continue
        try:
            out[mid] = (float(pricing.get("prompt", 0) or 0), float(pricing.get("completion", 0) or 0))
        except (TypeError, ValueError):
            continue
    return out


def validate_roster(models: Iterable[str], catalogue: Optional[List[dict]] = None) -> List[str]:
    """Subset of *models* which the endpoint does not advertise (empty list == all good)."""
    known = set(catalogue_ids(catalogue))
    return [m for m in models if m not in known]
