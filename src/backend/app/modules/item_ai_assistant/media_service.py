from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.modules.item_ai_assistant.errors import ItemAIAssistantValidationError

BACKEND_DIR = Path(__file__).resolve().parents[3]
ASSETS_DIR = BACKEND_DIR / "data" / "input" / "item_assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class GenerateMediaInput:
    teacher_id: int
    mode: str
    target: str
    spec: dict


@dataclass(frozen=True)
class GenerateMediaOutput:
    asset: dict
    insert_doc: dict
    meta: dict


def _require_list(spec: dict, key: str) -> list:
    value = spec.get(key)
    if not isinstance(value, list) or not value:
        raise ItemAIAssistantValidationError(f"spec.{key} debe ser una lista no vacia")
    return value


def _validate_common(input_data: GenerateMediaInput) -> None:
    if input_data.mode != "chart_deterministic":
        raise ItemAIAssistantValidationError("mode soportado actualmente: chart_deterministic")
    if input_data.target not in {"statement", "option_a", "option_b", "option_c", "option_d"}:
        raise ItemAIAssistantValidationError("target invalido")


def _render_bar_chart(spec: dict) -> None:
    labels = _require_list(spec, "labels")
    values = _require_list(spec, "values")
    if len(labels) != len(values):
        raise ItemAIAssistantValidationError("spec.labels y spec.values deben tener la misma longitud")

    plt.bar(labels, values, color="#4E79A7", edgecolor="black")
    plt.title(str(spec.get("title", "")))
    plt.xlabel(str(spec.get("x_label", "")))
    plt.ylabel(str(spec.get("y_label", "")))


def _render_pie_chart(spec: dict) -> None:
    labels = _require_list(spec, "labels")
    sizes = _require_list(spec, "sizes")
    if len(labels) != len(sizes):
        raise ItemAIAssistantValidationError("spec.labels y spec.sizes deben tener la misma longitud")

    plt.pie(sizes, labels=labels, autopct="%1.0f%%", startangle=90)
    plt.title(str(spec.get("title", "")))
    plt.axis("equal")


def _build_chart(spec: dict) -> str:
    chart_type = str(spec.get("chart_type", "")).lower()
    if chart_type not in {"bar", "pie"}:
        raise ItemAIAssistantValidationError("chart_type soportado: bar o pie")

    fig_w = float(spec.get("fig_w", 7.0))
    fig_h = float(spec.get("fig_h", 4.5))

    plt.figure(figsize=(fig_w, fig_h))
    if chart_type == "bar":
        _render_bar_chart(spec)
    else:
        _render_pie_chart(spec)

    plt.tight_layout()
    filename = f"{uuid4().hex}.png"
    output_path = ASSETS_DIR / filename
    plt.savefig(output_path, dpi=200)
    plt.close()
    return filename


def generate_media_from_spec(input_data: GenerateMediaInput) -> GenerateMediaOutput:
    _validate_common(input_data)
    filename = _build_chart(input_data.spec)

    relative_url = f"/assets/item_assets/{filename}"
    insert_doc = {
        "type": "doc",
        "content": [
            {
                "type": "image",
                "attrs": {
                    "src": relative_url,
                    "alt": "generated-chart",
                    "title": None,
                },
            }
        ],
    }

    return GenerateMediaOutput(
        asset={
            "filename": filename,
            "url": relative_url,
            "mime_type": "image/png",
        },
        insert_doc=insert_doc,
        meta={
            "mode": input_data.mode,
            "target": input_data.target,
            "chart_type": str(input_data.spec.get("chart_type", "")).lower(),
        },
    )
