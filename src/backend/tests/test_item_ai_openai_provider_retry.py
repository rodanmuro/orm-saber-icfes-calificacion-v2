from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.modules.item_ai_assistant.providers.openai_provider import OpenAIItemDraftProvider


@dataclass
class _FakeResponse:
    output_text: str
    usage: object | None = None


class _FakeClient:
    def __init__(self, fail_first: bool = True):
        self.calls = 0
        self.fail_first = fail_first

    class responses:  # noqa: D401
        pass

    def bind(self):
        self.responses.create = self._create
        return self

    def _create(self, *, model, input, **kwargs):  # noqa: ANN001
        self.calls += 1
        if self.fail_first and self.calls == 1:
            raise RuntimeError("429 rate limit transient")
        return _FakeResponse(output_text='{"statement_doc":{"type":"doc","content":[]},"options_doc":{"A":{"type":"doc","content":[]},"B":{"type":"doc","content":[]},"C":{"type":"doc","content":[]},"D":{"type":"doc","content":[]}},"correct_answer":"A"}')


def test_provider_retries_on_transient_error(monkeypatch):
    fake_client = _FakeClient(fail_first=True).bind()

    class _OpenAI:
        def __init__(self, api_key=None, timeout=None):  # noqa: ANN001
            self.api_key = api_key
            self.timeout = timeout

        @property
        def responses(self):
            return fake_client.responses

    monkeypatch.setitem(__import__('sys').modules, 'openai', type('M', (), {'OpenAI': _OpenAI}))

    provider = OpenAIItemDraftProvider(
        api_key='test-key',
        model_name='gpt-5.1',
        timeout_seconds=5,
        max_retries=2,
        retry_backoff_seconds=0.001,
    )

    payload = provider.generate_item_draft(system_prompt='sys', user_prompt='usr')

    assert fake_client.calls == 2
    assert payload['correct_answer'] == 'A'


def test_provider_no_retry_for_non_retryable(monkeypatch):
    fake_client = _FakeClient(fail_first=False).bind()

    def _always_bad(*, model, input, **kwargs):  # noqa: ANN001
        raise RuntimeError("401 authentication failed")

    fake_client.responses.create = _always_bad

    class _OpenAI:
        def __init__(self, api_key=None, timeout=None):  # noqa: ANN001
            self.api_key = api_key
            self.timeout = timeout

        @property
        def responses(self):
            return fake_client.responses

    monkeypatch.setitem(__import__('sys').modules, 'openai', type('M', (), {'OpenAI': _OpenAI}))

    provider = OpenAIItemDraftProvider(
        api_key='test-key',
        model_name='gpt-5.1',
        timeout_seconds=5,
        max_retries=2,
        retry_backoff_seconds=0.001,
    )

    with pytest.raises(Exception):
        provider.generate_item_draft(system_prompt='sys', user_prompt='usr')

    assert fake_client.calls == 0
