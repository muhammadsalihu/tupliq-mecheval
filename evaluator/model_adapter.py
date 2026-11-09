"""
MechEval Model Adapters.
Provides unified interface for live API inference and deterministic offline replay of real frontier model trials.
"""

import json
import re
import time
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import requests


class ModelResponse(BaseModel):
    model_name: str
    raw_text: str
    parsed_json: Optional[Dict[str, Any]] = None
    parse_success: bool = False
    latency_seconds: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0
    error: Optional[str] = None


def extract_json_from_response(text: str) -> Optional[Dict[str, Any]]:
    """
    Robustly extracts and parses JSON dictionary from LLM freeform response text.
    Handles ```json ... ``` markdown codeblocks, trailing commas, and raw json objects.
    """
    if not text:
        return None

    # Try 1: Markdown code block
    match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try cleaning trailing commas
            cleaned = re.sub(r",\s*([\}\]])", r"\1", json_str)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass

    # Try 2: First standalone outer curly braces {...}
    match = re.search(r"(\{[\s\S]*\})", text)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            cleaned = re.sub(r",\s*([\}\]])", r"\1", json_str)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass

    return None


class ModelUnavailableError(RuntimeError):
    """The provider rejected the configured model slug: stop the run, never score it as a failure."""


class BaseModelAdapter:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str, temperature: float = 0.2, timeout: int = 60) -> ModelResponse:
        raise NotImplementedError


class LiveAPIModelAdapter(BaseModelAdapter):
    """
    Calls an OpenAI-compatible ChatCompletions endpoint (OpenRouter, the Nous portal, ...).
    """
    #: Fallback price per 1M tokens for an endpoint that publishes no pricing for the model.
    DEFAULT_PRICING_PER_M = (2.50, 10.00)

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        pricing: Optional[Dict[str, tuple]] = None,
    ):
        super().__init__(model_name)
        self.api_key = api_key or os.getenv("MECHEVAL_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("MECHEVAL_BASE_URL", os.getenv("OPENAI_BASE_URL", base_url)).rstrip("/")
        # model id -> (prompt $/token, completion $/token), from the endpoint's own catalogue.
        self.pricing = dict(pricing or {})

    def generate(self, prompt: str, temperature: float = 0.2, timeout: Optional[int] = None) -> ModelResponse:
        # Reasoning-class models routinely need >60 s for a 5-part JSON deliverable; the read
        # timeout is generous by default and overridable per run (MECHEVAL_TIMEOUT).
        if timeout is None:
            timeout = int(os.getenv("MECHEVAL_TIMEOUT", "300"))
        if not self.api_key:
            return ModelResponse(
                model_name=self.model_name,
                raw_text="",
                error="No API key provided. Set OPENAI_API_KEY or OPENROUTER_API_KEY in .env.",
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        start_time = time.time()
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=(15, timeout),
            )
            elapsed = time.time() - start_time
            if resp.status_code != 200:
                body = resp.text
                # A rejected slug must stop the run: scoring it as "the model failed every task"
                # is silently wrong results, not an error the caller can see.
                if resp.status_code in (400, 404) and "model" in body.lower():
                    raise ModelUnavailableError(
                        f"OpenRouter rejected model '{self.model_name}' "
                        f"(HTTP {resp.status_code}): {body[:300]}"
                    )
                return ModelResponse(
                    model_name=self.model_name,
                    raw_text=body,
                    latency_seconds=elapsed,
                    error=f"API Error {resp.status_code}: {body}",
                )

            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

            # Real price for this model at the endpoint actually called; the fallback is only a
            # placeholder for endpoints that publish no pricing (the report must say which it is).
            p_in, p_out = self.pricing.get(
                self.model_name,
                tuple(rate / 1e6 for rate in self.DEFAULT_PRICING_PER_M),
            )
            cost = prompt_tokens * p_in + completion_tokens * p_out

            parsed = extract_json_from_response(content)

            return ModelResponse(
                model_name=self.model_name,
                raw_text=content,
                parsed_json=parsed,
                parse_success=(parsed is not None),
                latency_seconds=elapsed,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                estimated_cost_usd=cost,
            )
        except ModelUnavailableError:
            raise
        except Exception as e:
            return ModelResponse(
                model_name=self.model_name,
                raw_text="",
                latency_seconds=time.time() - start_time,
                error=f"Exception during API call: {str(e)}",
            )



