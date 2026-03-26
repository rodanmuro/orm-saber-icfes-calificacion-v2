from __future__ import annotations

import pytest

from app.modules.item_ai_assistant.domain import GenerateItemDraftInput
from app.modules.item_ai_assistant.errors import ItemAIAssistantValidationError
from app.modules.item_ai_assistant.service import generate_item_draft


class _FakeProvider:
    model_name = "fake-model"

    def __init__(self, payload: dict):
        self.payload = payload

    def generate_item_draft(self, *, system_prompt: str, user_prompt: str) -> dict:
        assert "JSON" in system_prompt or "json" in system_prompt.lower()
        assert "standard_name" in user_prompt
        return self.payload


class _SequentialProvider:
    model_name = "fake-model"

    def __init__(self, payloads: list[dict]):
        self.payloads = payloads
        self.calls = 0

    def generate_item_draft(self, *, system_prompt: str, user_prompt: str) -> dict:
        idx = min(self.calls, len(self.payloads) - 1)
        self.calls += 1
        return self.payloads[idx]


def _doc_text(text: str) -> dict:
    return {
        "type": "doc",
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
    }


def _doc_math(text_prefix: str, latex: str) -> dict:
    return {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": text_prefix},
                    {"type": "mathInline", "attrs": {"latex": latex}},
                ],
            }
        ],
    }


def test_generate_item_draft_structured_docs_normalizes_to_a_and_reports_cost() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_math("Calcula: ", "\\frac{1}{2}+\\frac{1}{2}"),
            "options_doc": {
                "A": _doc_text("0"),
                "B": _doc_text("1"),
                "C": _doc_text("2"),
                "D": _doc_text("3"),
            },
            "correct_answer": "b",
            "__usage": {
                "input_tokens": 1000,
                "cached_input_tokens": 200,
                "output_tokens": 300,
                "total_tokens": 1300,
            },
        }
    )
    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea una pregunta sobre fracciones",
            standard_name="Fracciones",
            competency_name="Opera fracciones",
            subject="matematicas",
            difficulty="media",
        ),
        provider=provider,
    )

    assert result.correct_answer == "A"
    assert result.options_doc["A"] == _doc_text("1")
    assert result.options_doc["B"] == _doc_text("0")
    assert result.metadata["ai_generated"] is True
    assert result.metadata["ai_model"] == "fake-model"
    assert isinstance(result.metadata["ai_prompt_version"], str)

    assert result.usage is not None
    assert result.usage["input_tokens"] == 1000
    assert result.usage["cached_input_tokens"] == 200
    assert result.usage["non_cached_input_tokens"] == 800
    assert result.usage["output_tokens"] == 300
    assert result.usage["total_tokens"] == 1300
    assert result.usage["input_cost_usd"] == pytest.approx(0.001)
    assert result.usage["cached_input_cost_usd"] == pytest.approx(0.000025)
    assert result.usage["output_cost_usd"] == pytest.approx(0.003)
    assert result.usage["total_cost_usd"] == pytest.approx(0.004025)


def test_generate_item_draft_rejects_invalid_options() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Pregunta de prueba"),
            "options_doc": {
                "A": _doc_text("1"),
                "B": _doc_text("2"),
                "C": _doc_text("3"),
            },
            "correct_answer": "A",
        }
    )

    with pytest.raises(ItemAIAssistantValidationError, match="exactly A, B, C and D"):
        generate_item_draft(
            GenerateItemDraftInput(
                user_prompt="Crea una pregunta",
                standard_name="S",
                competency_name="C",
            ),
            provider=provider,
        )


def test_generate_item_draft_accepts_valid_media_spec() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Interpreta el grafico"),
            "options_doc": {
                "A": _doc_text("Respuesta correcta"),
                "B": _doc_text("Distractor 1"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "A",
            "media_spec": {
                "mode": "chart_deterministic",
                "target": "statement",
                "spec": {
                    "chart_type": "bar",
                    "title": "Ventas",
                    "labels": ["T1", "T2"],
                    "values": [10, 12],
                },
            },
        }
    )

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea pregunta con grafico de barras",
            standard_name="Datos",
            competency_name="Interpreta graficos",
        ),
        provider=provider,
    )

    assert result.media_spec is not None
    assert result.media_spec["mode"] == "chart_deterministic"
    assert result.media_spec["spec"]["chart_type"] == "bar"


def test_generate_item_draft_repair_attempt_when_first_output_is_invalid() -> None:
    invalid_first = {
        "statement_doc": _doc_text("Interpreta el grafico"),
        "options_doc": {
            "A": _doc_text("1"),
            "B": _doc_text("2"),
            "C": _doc_text("3"),
            "D": _doc_text("4"),
        },
        "correct_answer": "A",
        "media_spec": {
            "mode": "chart_deterministic",
            "target": "statement",
            "spec": {
                "chart_type": "bar",
                "labels": [],
                "values": ["abc", 20],
            },
        },
        "__usage": {
            "input_tokens": 100,
            "cached_input_tokens": 0,
            "output_tokens": 100,
            "total_tokens": 200,
        },
    }

    repaired_second = {
        "statement_doc": _doc_text("Interpreta el grafico"),
        "options_doc": {
            "A": _doc_text("1"),
            "B": _doc_text("2"),
            "C": _doc_text("3"),
            "D": _doc_text("4"),
        },
        "correct_answer": "A",
        "media_spec": {
            "mode": "chart_deterministic",
            "target": "statement",
            "spec": {
                "chart_type": "bar",
                "labels": ["T1", "T2"],
                "values": [10, 20],
            },
        },
        "__usage": {
            "input_tokens": 200,
            "cached_input_tokens": 0,
            "output_tokens": 300,
            "total_tokens": 500,
        },
    }

    provider = _SequentialProvider([invalid_first, repaired_second])

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea pregunta con grafico",
            standard_name="Datos",
            competency_name="Interpreta",
        ),
        provider=provider,
    )

    assert provider.calls == 2
    assert result.metadata["ai_repaired"] is True
    assert result.media_spec is not None
    assert result.usage["total_tokens"] == 700


def test_generate_item_draft_retries_when_provider_returns_non_json_then_recovers() -> None:
    from app.modules.item_ai_assistant.errors import ItemAIAssistantProviderError

    class _ProviderWithProviderFailureThenSuccess:
        model_name = "fake-model"

        def __init__(self) -> None:
            self.calls = 0

        def generate_item_draft(self, *, system_prompt: str, user_prompt: str) -> dict:
            self.calls += 1
            if self.calls == 1:
                raise ItemAIAssistantProviderError("openai output is not valid JSON")
            return {
                "statement_doc": _doc_text("Pregunta recuperada"),
                "options_doc": {
                    "A": _doc_text("Correcta"),
                    "B": _doc_text("Distractor 1"),
                    "C": _doc_text("Distractor 2"),
                    "D": _doc_text("Distractor 3"),
                },
                "correct_answer": "A",
                "__usage": {
                    "input_tokens": 50,
                    "cached_input_tokens": 0,
                    "output_tokens": 80,
                    "total_tokens": 130,
                },
            }

    provider = _ProviderWithProviderFailureThenSuccess()

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea una pregunta de prueba",
            standard_name="S",
            competency_name="C",
        ),
        provider=provider,
    )

    assert provider.calls == 2
    assert result.correct_answer == "A"
    assert result.metadata["ai_repaired"] is True
    assert result.usage is not None
    assert result.usage["total_tokens"] == 130


def test_generate_item_draft_accepts_media_spec_data_pairs_for_pie() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Interpreta la grafica"),
            "options_doc": {
                "A": _doc_text("Respuesta correcta"),
                "B": _doc_text("Distractor 1"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "A",
            "media_spec": {
                "mode": "chart_deterministic",
                "target": "statement",
                "spec": {
                    "chart_type": "pie",
                    "title": "Distribucion",
                    "data": [
                        {"label": "A", "value": 30},
                        {"label": "B", "value": 20},
                        {"label": "C", "value": 50},
                    ],
                },
            },
        }
    )

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea pregunta con grafico circular",
            standard_name="Datos",
            competency_name="Interpreta",
        ),
        provider=provider,
    )

    assert result.media_spec is not None
    assert result.media_spec["spec"]["chart_type"] == "pie"
    assert result.media_spec["spec"]["labels"] == ["A", "B", "C"]
    assert result.media_spec["spec"]["sizes"] == [30.0, 20.0, 50.0]


def test_generate_item_draft_accepts_pie_with_values_field() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Interpreta la grafica"),
            "options_doc": {
                "A": _doc_text("Respuesta correcta"),
                "B": _doc_text("Distractor 1"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "A",
            "media_spec": {
                "mode": "chart_deterministic",
                "target": "statement",
                "spec": {
                    "chart_type": "pie",
                    "labels": ["X", "Y", "Z"],
                    "values": [10, 20, 70],
                },
            },
        }
    )

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea pregunta con pie",
            standard_name="Datos",
            competency_name="Interpreta",
        ),
        provider=provider,
    )

    assert result.media_spec is not None
    assert result.media_spec["spec"]["sizes"] == [10.0, 20.0, 70.0]


def test_generate_item_draft_accepts_bar_values_with_percent_strings() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Interpreta la grafica"),
            "options_doc": {
                "A": _doc_text("Respuesta correcta"),
                "B": _doc_text("Distractor 1"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "A",
            "media_spec": {
                "mode": "chart_deterministic",
                "target": "statement",
                "spec": {
                    "chart_type": "bar",
                    "labels": ["Vivienda", "Alimentacion", "Transporte", "Educacion"],
                    "values": ["40%", "30 %", "20%", "10%"],
                },
            },
        }
    )

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea pregunta con barras y porcentajes",
            standard_name="Datos",
            competency_name="Interpreta",
        ),
        provider=provider,
    )

    assert result.media_spec is not None
    assert result.media_spec["spec"]["chart_type"] == "bar"
    assert result.media_spec["spec"]["values"] == [40.0, 30.0, 20.0, 10.0]


def test_generate_item_draft_accepts_bar_values_with_localized_numbers() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Interpreta la grafica"),
            "options_doc": {
                "A": _doc_text("Respuesta correcta"),
                "B": _doc_text("Distractor 1"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "A",
            "media_spec": {
                "mode": "chart_deterministic",
                "target": "statement",
                "spec": {
                    "chart_type": "bar",
                    "labels": ["Enero", "Febrero", "Marzo"],
                    "values": ["1.200", "1,5", "$2.000"],
                },
            },
        }
    )

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea pregunta con barras",
            standard_name="Datos",
            competency_name="Interpreta",
        ),
        provider=provider,
    )

    assert result.media_spec is not None
    assert result.media_spec["spec"]["chart_type"] == "bar"
    assert result.media_spec["spec"]["values"] == [1200.0, 1.5, 2000.0]


def test_generate_item_draft_rejects_bar_without_labels() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Interpreta la grafica"),
            "options_doc": {
                "A": _doc_text("Respuesta correcta"),
                "B": _doc_text("Distractor 1"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "A",
            "media_spec": {
                "mode": "chart_deterministic",
                "target": "statement",
                "spec": {
                    "chart_type": "bar",
                    "values": [10, 20, 30],
                },
            },
        }
    )

    with pytest.raises(ItemAIAssistantValidationError, match="labels requerido para bar"):
        generate_item_draft(
            GenerateItemDraftInput(
                user_prompt="Crea pregunta con barras",
                standard_name="Datos",
                competency_name="Interpreta",
            ),
            provider=provider,
        )


def test_generate_item_draft_accepts_multiple_media_specs_distinct_targets() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Observa las graficas"),
            "options_doc": {
                "A": _doc_text("Correcta"),
                "B": _doc_text("Distractor 1"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "A",
            "media_specs": [
                {
                    "mode": "chart_deterministic",
                    "target": "statement",
                    "spec": {
                        "chart_type": "bar",
                        "labels": ["Bus", "Bici"],
                        "values": [12, 8],
                    },
                },
                {
                    "mode": "chart_deterministic",
                    "target": "option_b",
                    "spec": {
                        "chart_type": "pie",
                        "labels": ["A", "B"],
                        "sizes": [60, 40],
                    },
                },
            ],
        }
    )

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea pregunta con dos graficos",
            standard_name="Datos",
            competency_name="Interpreta",
        ),
        provider=provider,
    )

    assert result.media_specs is not None
    assert len(result.media_specs) == 2
    assert result.media_specs[0]["target"] == "statement"
    assert result.media_specs[1]["target"] == "option_b"


def test_generate_item_draft_rejects_media_specs_with_duplicate_targets() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Observa las graficas"),
            "options_doc": {
                "A": _doc_text("Correcta"),
                "B": _doc_text("Distractor 1"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "A",
            "media_specs": [
                {
                    "mode": "chart_deterministic",
                    "target": "statement",
                    "spec": {"chart_type": "bar", "labels": ["A"], "values": [1]},
                },
                {
                    "mode": "chart_deterministic",
                    "target": "statement",
                    "spec": {"chart_type": "pie", "labels": ["A"], "sizes": [100]},
                },
            ],
        }
    )

    with pytest.raises(ItemAIAssistantValidationError, match="targets duplicados"):
        generate_item_draft(
            GenerateItemDraftInput(
                user_prompt="Crea pregunta con dos graficos",
                standard_name="Datos",
                competency_name="Interpreta",
            ),
            provider=provider,
        )


def _doc_table_simple() -> dict:
    return {
        "type": "doc",
        "content": [
            {
                "type": "table",
                "content": [
                    {
                        "type": "tableRow",
                        "content": [
                            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Categoria"}]}]},
                            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Valor"}]}]},
                        ],
                    },
                    {
                        "type": "tableRow",
                        "content": [
                            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "A"}]}]},
                            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "10"}]}]},
                        ],
                    },
                ],
            }
        ],
    }


def test_generate_item_draft_repair_when_table_requested_but_missing() -> None:
    first_payload = {
        "statement_doc": _doc_text("Tabla en texto plano: A=10, B=20"),
        "options_doc": {
            "A": _doc_text("Correcta"),
            "B": _doc_text("Distractor 1"),
            "C": _doc_text("Distractor 2"),
            "D": _doc_text("Distractor 3"),
        },
        "correct_answer": "A",
    }
    second_payload = {
        "statement_doc": _doc_table_simple(),
        "options_doc": {
            "A": _doc_text("Correcta"),
            "B": _doc_text("Distractor 1"),
            "C": _doc_text("Distractor 2"),
            "D": _doc_text("Distractor 3"),
        },
        "correct_answer": "A",
    }

    provider = _SequentialProvider([first_payload, second_payload])

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea una pregunta con tabla y graficas",
            standard_name="Datos",
            competency_name="Interpreta",
        ),
        provider=provider,
    )

    assert provider.calls == 2
    assert result.metadata["ai_repaired"] is True
    assert result.statement_doc["content"][0]["type"] == "table"


def test_generate_item_draft_compacts_option_text_when_option_has_chart() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Observa las opciones"),
            "options_doc": {
                "A": _doc_text("Esta opcion describe toda la grafica circular con mucho texto y valores."),
                "B": _doc_text("Otro texto largo de apoyo"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "A",
            "media_specs": [
                {
                    "mode": "chart_deterministic",
                    "target": "option_a",
                    "spec": {
                        "chart_type": "pie",
                        "labels": ["A", "B"],
                        "sizes": [70, 30],
                    },
                }
            ],
        }
    )

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea pregunta con grafica en opcion A",
            standard_name="Datos",
            competency_name="Interpreta",
        ),
        provider=provider,
    )

    option_a_text = result.options_doc["A"]["content"][0]["content"][0]["text"]
    assert option_a_text == "Observa la grafica."

def test_generate_item_draft_coerces_plain_text_rows_into_table_node() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": {
                "type": "doc",
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "En la tabla se muestran cantidades por categoria:"}]},
                    {"type": "paragraph", "content": [{"type": "text", "text": "• A pie: 12"}]},
                    {"type": "paragraph", "content": [{"type": "text", "text": "• Bicicleta: 8"}]},
                    {"type": "paragraph", "content": [{"type": "text", "text": "• Bus escolar: 20"}]},
                ],
            },
            "options_doc": {
                "A": _doc_text("Correcta"),
                "B": _doc_text("Distractor 1"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "A",
        }
    )

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea una pregunta con tabla sobre transporte escolar",
            standard_name="Datos",
            competency_name="Interpreta",
        ),
        provider=provider,
    )

    content = result.statement_doc.get("content", [])
    assert any(isinstance(n, dict) and n.get("type") == "table" for n in content)


def test_generate_item_draft_swaps_media_target_and_compacts_after_normalizing_to_a() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Observa las opciones"),
            "options_doc": {
                "A": _doc_text("Texto largo A"),
                "B": _doc_text("Texto largo B con descripcion de grafica"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "B",
            "media_specs": [
                {
                    "mode": "chart_deterministic",
                    "target": "option_b",
                    "spec": {
                        "chart_type": "pie",
                        "labels": ["X", "Y"],
                        "sizes": [70, 30],
                    },
                }
            ],
        }
    )

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea pregunta con grafica en opcion correcta",
            standard_name="Datos",
            competency_name="Interpreta",
        ),
        provider=provider,
    )

    assert result.correct_answer == "A"
    assert result.media_specs[0]["target"] == "option_a"
    assert result.options_doc["A"]["content"][0]["content"][0]["text"] == "Observa la grafica."
