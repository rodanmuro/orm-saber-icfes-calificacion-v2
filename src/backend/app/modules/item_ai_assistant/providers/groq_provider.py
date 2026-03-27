from __future__ import annotations

import json
import random
import time
from typing import Any

from app.core.config import settings
from app.modules.item_ai_assistant.errors import ItemAIAssistantProviderError


class GroqItemDraftProvider:
    provider_name = "groq"

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        retry_backoff_seconds: float | None = None,
    ):
        self.api_key = api_key or settings.groq_api_key
        self.model_name = model_name or settings.groq_model
        self.timeout_seconds = timeout_seconds or settings.groq_timeout_seconds
        self.max_retries = int(max_retries if max_retries is not None else settings.groq_max_retries)
        self.retry_backoff_seconds = float(
            retry_backoff_seconds
            if retry_backoff_seconds is not None
            else settings.groq_retry_backoff_seconds
        )

    def generate_item_draft(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:
        if not self.api_key:
            raise ItemAIAssistantProviderError("GROQ_API_KEY is not configured")

        try:
            from groq import Groq
        except Exception as exc:  # noqa: BLE001
            raise ItemAIAssistantProviderError(
                "groq dependency is missing. Install package 'groq'."
            ) from exc

        client = Groq(api_key=self.api_key, timeout=self.timeout_seconds)
        response = self._create_with_retries(
            client=client,
            model=self.model_name,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        text = _extract_text_from_response(response).strip()
        if not text:
            raise ItemAIAssistantProviderError("groq output is empty")

        try:
            payload = _parse_json_from_output_text(text)
        except json.JSONDecodeError as exc:
            raise ItemAIAssistantProviderError("groq output is not valid JSON") from exc

        if isinstance(payload, dict):
            payload["__usage"] = _extract_usage(response)
        return payload

    def _create_with_retries(
        self,
        *,
        client: Any,
        model: str,
        system_prompt: str,
        user_prompt: str,
    ) -> Any:
        attempts = max(1, self.max_retries + 1)
        last_exc: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                return client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    response_format=_build_groq_response_format_json_schema(),
                )
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                should_retry, reason = _is_retryable_error(exc)
                if (not should_retry) or attempt >= attempts:
                    raise ItemAIAssistantProviderError(
                        f"groq request failed ({reason}): {exc}"
                    ) from exc

                delay = self.retry_backoff_seconds * (2 ** (attempt - 1))
                jitter = random.uniform(0, 0.25 * max(delay, 0.001))
                time.sleep(delay + jitter)

        raise ItemAIAssistantProviderError("groq request failed") from last_exc


def _extract_text_from_response(response: Any) -> str:
    choices = getattr(response, "choices", None)
    if not isinstance(choices, list) or len(choices) == 0:
        return ""
    first_choice = choices[0]
    message = getattr(first_choice, "message", None)
    if message is None:
        return ""
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    return ""


def _is_retryable_error(exc: Exception) -> tuple[bool, str]:
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


def _extract_usage(response: Any) -> dict[str, int]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {
            "input_tokens": 0,
            "cached_input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
    total_tokens = int(getattr(usage, "total_tokens", 0) or (input_tokens + output_tokens))
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": 0,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def _build_groq_response_format_json_schema() -> dict[str, Any]:
    # Best-effort structured outputs in Groq (strict: false).
    # Backend validators remain the source of truth for contract enforcement.
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "item_ai_draft",
            "strict": False,
            "schema": {
                "type": "object",
                "required": ["statement_doc", "options_doc", "correct_answer"],
                "properties": {
                    "statement_doc": {"type": "object"},
                    "options_doc": {
                        "type": "object",
                        "required": ["A", "B", "C", "D"],
                        "properties": {
                            "A": {"type": "object"},
                            "B": {"type": "object"},
                            "C": {"type": "object"},
                            "D": {"type": "object"},
                        },
                    },
                    "correct_answer": {
                        "type": "string",
                        "enum": ["A", "B", "C", "D", "a", "b", "c", "d"],
                    },
                    "media_spec": {"type": ["object", "null"]},
                    "media_specs": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                },
            },
        },
    }
