"""
Canonical MechEval model roster.

Short display names resolve to fully-qualified OpenRouter slugs (provider-prefixed).
OpenRouter rejects a bare name like ``gpt-6-luna`` with a 400, and a rejected slug used to be
scored as *the model failing the task* — so every name must resolve here before a run starts,
and :func:`validate_roster` checks the slugs against OpenRouter's catalogue (no API key needed).
"""

from __future__ import annotations

import json
import urllib.request
from typing import Iterable, List

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


class UnknownModelError(ValueError):
    """A requested model is neither a roster short name nor a provider-prefixed slug."""


#: short name -> (OpenRouter slug, human label, note)
ROSTER = {
    "gpt-6-luna": ("openai/gpt-6-luna", "GPT-6 Luna", "frontier OpenAI, flash-class"),
    "deepseek-4.1-flash": ("deepseek/deepseek-v4.1-flash", "DeepSeek 4.1 Flash", "cheapest reasoning-class"),
    "glm-5.3-flash": ("z-ai/glm-5.3-flash", "GLM 5.3 Flash", "Z.ai flash-class"),
    "haiku-5.5": ("anthropic/claude-haiku-5.5", "Haiku 5.5", "cheapest Claude-class at evaluation time"),
}


def slugs() -> List[str]:
    """Every roster slug, in declaration order (the default run order)."""
    return [entry[0] for entry in ROSTER.values()]


def label_for(slug: str) -> str:
    """Human label for a roster slug, else the slug itself."""
    for name, (entry_slug, label, _note) in ROSTER.items():
        if slug == entry_slug or slug == name:
            return label
    return slug


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
        f"— or pass a provider-prefixed OpenRouter slug (e.g. 'deepseek/deepseek-v4.1-flash')."
    )


def resolve_all(models: Iterable[str]) -> List[str]:
    return [resolve(m) for m in models]


def fetch_catalogue(timeout: int = 25) -> List[str]:
    """Every model id OpenRouter currently serves (public endpoint, no key required)."""
    req = urllib.request.Request(OPENROUTER_MODELS_URL, headers={"User-Agent": "mecheval/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (fixed https URL)
        payload = json.loads(resp.read().decode("utf-8"))
    return [m["id"] for m in payload.get("data", [])]


def validate_roster(models: Iterable[str], catalogue: List[str] | None = None) -> List[str]:
    """Return the subset of *models* that OpenRouter does not advertise (empty list == all good)."""
    ids = catalogue if catalogue is not None else fetch_catalogue()
    known = set(ids)
    return [m for m in models if m not in known]
