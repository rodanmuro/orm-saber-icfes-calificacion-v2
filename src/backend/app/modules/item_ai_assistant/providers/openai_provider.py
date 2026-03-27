from __future__ import annotations

import json
import random
import time
from typing import Any

from app.core.config import settings
from app.modules.item_ai_assistant.errors import ItemAIAssistantProviderError



class OpenAIItemDraftProvider:
    provider_name = "openai"

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        retry_backoff_seconds: float | None = None,
    ):
        self.api_key = api_key or settings.openai_api_key
        self.model_name = model_name or settings.openai_model
        self.timeout_seconds = timeout_seconds or settings.openai_timeout_seconds
        self.max_retries = int(max_retries if max_retries is not None else settings.openai_max_retries)
        self.retry_backoff_seconds = float(
            retry_backoff_seconds
            if retry_backoff_seconds is not None
            else settings.openai_retry_backoff_seconds
        )

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

        response = self._responses_create_with_retries(
            client=client,
            model=self.model_name,
            input_payload=[
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
            ],
        )

        text = (getattr(response, "output_text", None) or "").strip()
        if not text:
            raise ItemAIAssistantProviderError("openai output is empty")

        try:
            payload = _parse_json_from_output_text(text)
        except json.JSONDecodeError as exc:
            raise ItemAIAssistantProviderError("openai output is not valid JSON") from exc

        if isinstance(payload, dict):
            payload["__usage"] = _extract_openai_usage(response)
        return payload

    def _responses_create_with_retries(self, *, client: Any, model: str, input_payload: list[dict]) -> Any:
        attempts = max(1, self.max_retries + 1)
        last_exc: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                return client.responses.create(
                    model=model,
                    input=input_payload,
                    text={"format": {"type": "json_object"}},
                )
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                should_retry, reason = _is_retryable_openai_error(exc)
                if (not should_retry) or attempt >= attempts:
                    msg = f"openai request failed ({reason}): {exc}"
                    raise ItemAIAssistantProviderError(msg) from exc

                delay = self.retry_backoff_seconds * (2 ** (attempt - 1))
                jitter = random.uniform(0, 0.25 * max(delay, 0.001))
                time.sleep(delay + jitter)

        raise ItemAIAssistantProviderError("openai request failed") from last_exc


def _is_retryable_openai_error(exc: Exception) -> tuple[bool, str]:
    text = str(exc).lower()

    transient_hints = (
        "timeout",
        "timed out",
        "rate limit",
        "429",
        "503",
        "502",
        "500",
        "connection",
        "temporary",
        "overloaded",
        "incomplete",
    )
    if any(hint in text for hint in transient_hints):
        return True, "transient"

    if "invalid api key" in text or "authentication" in text or "401" in text:
        return False, "auth"

    return False, "non_retryable"


def _strip_markdown_fence(text: str) -> str:
    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
    return raw


def _extract_first_json_object(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escape = False

    for idx in range(start, len(text)):
        ch = text[idx]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            depth += 1
            continue
        if ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]

    return None


def _parse_json_from_output_text(text: str) -> dict[str, Any]:
    raw = _strip_markdown_fence(text)
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass

    candidate = _extract_first_json_object(raw)
    if not candidate:
        raise json.JSONDecodeError("No JSON object found", raw, 0)

    payload = json.loads(candidate)
    if not isinstance(payload, dict):
        raise json.JSONDecodeError("JSON payload is not an object", candidate, 0)
    return payload


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
