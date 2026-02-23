from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.modules.omr_reader.api_service import run_omr_read_from_image_bytes

EXPECTED_ANSWERS = [
    "A",
    "B",
    "A",
    "C",
    "A",
    "D",
    "C",
    "B",
    "A",
    "B",
    "C",
    "C",
    "B",
    "B",
    "B",
    "A",
    "A",
    "B",
    "C",
    "C",
    "D",
    "A",
    "A",
    "B",
    "C",
    "D",
    "D",
    "D",
    "C",
    "B",
]


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _resolve_local_image_path() -> Path:
    backend_root = Path(__file__).resolve().parents[1]
    from_env = os.getenv("OMR_INTEGRATION_IMAGE_PATH")
    if from_env:
        candidate = Path(from_env)
        return (backend_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()

    uploads_dir = backend_root / "data" / "input" / "mobile_uploads"
    latest_images = sorted(uploads_dir.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)
    if latest_images:
        return latest_images[0]
    return uploads_dir / "missing.jpg"


def _extract_single_mark(marked_options: list[str]) -> str:
    if len(marked_options) == 1:
        return marked_options[0]
    if len(marked_options) == 0:
        return "-"
    return ",".join(marked_options)


def test_local_image_omr_integration_metrics() -> None:
    image_path = _resolve_local_image_path()
    if not image_path.exists():
        pytest.skip(
            "No local image available. Set OMR_INTEGRATION_IMAGE_PATH or place a .jpg in data/input/mobile_uploads."
        )

    robust_mode = _parse_bool(os.getenv("OMR_INTEGRATION_ROBUST_MODE"), default=True)
    marked_threshold = float(os.getenv("OMR_INTEGRATION_MARKED_THRESHOLD", "0.22"))
    unmarked_threshold = float(os.getenv("OMR_INTEGRATION_UNMARKED_THRESHOLD", "0.08"))

    payload = run_omr_read_from_image_bytes(
        image_bytes=image_path.read_bytes(),
        metadata_path="data/output/template_basica_omr_v1.json",
        px_per_mm=10.0,
        marked_threshold=marked_threshold,
        unmarked_threshold=unmarked_threshold,
        robust_mode=robust_mode,
    )

    questions = payload["questions"]
    obtained = [_extract_single_mark(item.get("marked_options", [])) for item in questions]
    expected = EXPECTED_ANSWERS

    exact_matches = sum(1 for got, exp in zip(obtained, expected) if got == exp)
    blank_count = sum(1 for got in obtained if got == "-")
    multi_mark_count = sum(1 for got in obtained if "," in got)
    total = len(expected)
    accuracy = exact_matches / total if total else 0.0

    min_accuracy_env = os.getenv("OMR_INTEGRATION_MIN_ACCURACY")
    min_accuracy = float(min_accuracy_env) if min_accuracy_env else 0.0

    assert len(questions) == 30, "The OMR result must contain 30 questions."
    assert accuracy >= min_accuracy, (
        f"OMR accuracy {accuracy:.2%} below required {min_accuracy:.2%}. "
        f"image={image_path.name} robust_mode={robust_mode} "
        f"thresholds=({marked_threshold},{unmarked_threshold}) "
        f"exact_matches={exact_matches} blank={blank_count} multi={multi_mark_count}"
    )

    print(
        "\nOMR integration metrics | "
        f"image={image_path.name} robust_mode={robust_mode} "
        f"thresholds=({marked_threshold},{unmarked_threshold}) "
        f"accuracy={accuracy:.2%} exact_matches={exact_matches}/{total} "
        f"blank={blank_count} multi={multi_mark_count}"
    )
