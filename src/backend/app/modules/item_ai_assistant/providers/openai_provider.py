from __future__ import annotations

import json
from typing import Any

from app.core.config import settings
from app.modules.item_ai_assistant.errors import ItemAIAssistantProviderError


class OpenAIItemDraftProvider:
    def __init__(self, api_key: str | None = None, model_name: str | None = None, timeout_seconds: float | None = None):
        self.api_key = api_key or settings.openai_api_key
        self.model_name = model_name or settings.openai_model
        self.timeout_seconds = timeout_seconds or settings.openai_timeout_seconds

    def generate_item_draft(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:
        if not self.api_key:
            raise ItemAIAssistantProviderError("OPENAI_API_KEY is not configured")

        try:
            from openai import OpenAI
        except Exception as exc:  # noqa: BLE001
            raise ItemAIAssistantProviderError(
                "openai dependency is missing. Install package 'openai'."
            ) from exc

        client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
        try:
            response = client.responses.create(
                model=self.model_name,
                input=[
                    {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                    {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
                ],
            )
        except Exception as exc:  # noqa: BLE001
            raise ItemAIAssistantProviderError("openai request failed") from exc

        text = (getattr(response, "output_text", None) or "").strip()
        if not text:
            raise ItemAIAssistantProviderError("openai output is empty")

        raw = _strip_markdown_fence(text)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ItemAIAssistantProviderError("openai output is not valid JSON") from exc

        if isinstance(payload, dict):
            payload["__usage"] = _extract_openai_usage(response)
        return payload


def _strip_markdown_fence(text: str) -> str:
    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
    return raw


def _extract_openai_usage(response: Any) -> dict[str, int]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {
            "input_tokens": 0,
            "cached_input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
    total_tokens = int(getattr(usage, "total_tokens", 0) or 0)

    cached_input_tokens = 0
    input_details = getattr(usage, "input_tokens_details", None)
    if input_details is not None:
        cached_input_tokens = int(getattr(input_details, "cached_tokens", 0) or 0)

    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }
