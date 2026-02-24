from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from app.modules.omr_reader.api_service import (
    decode_image_bytes,
    get_omr_reader_engine,
    resolve_backend_relative_path,
    resolve_reader_backend,
    run_omr_read_from_image_bytes,
)
from app.modules.omr_reader.errors import (
    GeminiReadError,
    InvalidImageError,
    InvalidMetadataError,
    OpenAIReadError,
    UnsupportedReaderBackendError,
)


def test_decode_image_bytes_fails_on_empty() -> None:
    with pytest.raises(InvalidImageError, match="uploaded image is empty"):
        decode_image_bytes(image_bytes=b"")


def test_resolve_backend_relative_path_blocks_escape() -> None:
    with pytest.raises(InvalidMetadataError, match="must stay inside backend directory"):
        resolve_backend_relative_path("../../etc/passwd")


def test_run_omr_read_from_image_bytes_orchestrates_pipeline(monkeypatch) -> None:
    fake_metadata = {"template_id": "template_test", "version": "v1"}
    fake_image = np.zeros((10, 10, 3), dtype=np.uint8)
    fake_aligned = SimpleNamespace(aligned_image=fake_image, detected_marker_ids=[0, 1, 2, 3])
    fake_bubbles = [SimpleNamespace(bubble_id="B1", state="marcada", fill_ratio=0.9)]

    monkeypatch.setattr(
        "app.modules.omr_reader.api_service.resolve_backend_relative_path",
        lambda path_value: path_value,
    )
    monkeypatch.setattr(
        "app.modules.omr_reader.api_service.load_read_metadata",
        lambda metadata_file: fake_metadata,
    )
    monkeypatch.setattr(
        "app.modules.omr_reader.api_service.decode_image_bytes",
        lambda image_bytes: fake_image,
    )
    monkeypatch.setattr(
        "app.modules.omr_reader.api_service.align_image_to_template",
        lambda **kwargs: fake_aligned,
    )
    monkeypatch.setattr(
        "app.modules.omr_reader.api_service.classify_bubbles",
        lambda **kwargs: fake_bubbles,
    )
    monkeypatch.setattr(
        "app.modules.omr_reader.api_service.build_omr_read_result",
        lambda **kwargs: {
            "template_id": "template_test",
            "version": "v1",
            "questions": [],
            "quality_summary": {"total_questions": 0},
        },
    )

    payload = run_omr_read_from_image_bytes(
        image_bytes=b"fake-bytes",
        metadata_path="data/output/template_basica_omr_v1.json",
        px_per_mm=10.0,
        marked_threshold=0.33,
        unmarked_threshold=0.18,
    )

    assert payload["template_id"] == "template_test"
    assert payload["version"] == "v1"
    assert payload["diagnostics"]["detected_marker_ids"] == [0, 1, 2, 3]
    assert payload["diagnostics"]["robust_mode"] is False
    assert payload["diagnostics"]["reader_backend"] == "classic"
    assert payload["thresholds"]["marked"] == 0.33
    assert payload["thresholds"]["unmarked"] == 0.18


def test_resolve_reader_backend_rejects_unknown() -> None:
    with pytest.raises(UnsupportedReaderBackendError, match="is not supported"):
        resolve_reader_backend("otro")


def test_get_omr_reader_engine_gemini_requires_api_key(monkeypatch) -> None:
    engine = get_omr_reader_engine("gemini")
    monkeypatch.setattr("app.modules.omr_reader.gemini_reader.settings.gemini_api_key", None)
    with pytest.raises(GeminiReadError, match="GEMINI_API_KEY is not configured"):
        engine.read(
            request=SimpleNamespace(
                image_bytes=b"fake-image-bytes",
                metadata_path="data/output/template_basica_omr_v1.json",
                px_per_mm=10.0,
                marked_threshold=0.12,
                unmarked_threshold=0.18,
                robust_mode=False,
                save_debug_artifacts=False,
                debug_base_name=None,
                debug_output_dir="",
            )
        )


def test_get_omr_reader_engine_openai_requires_api_key(monkeypatch) -> None:
    engine = get_omr_reader_engine("openai")
    monkeypatch.setattr("app.modules.omr_reader.openai_reader.settings.openai_api_key", None)
    with pytest.raises(OpenAIReadError, match="OPENAI_API_KEY is not configured"):
        engine.read(
            request=SimpleNamespace(
                image_bytes=b"fake-image-bytes",
                metadata_path="data/output/template_basica_omr_v1.json",
                px_per_mm=10.0,
                marked_threshold=0.12,
                unmarked_threshold=0.18,
                robust_mode=False,
                save_debug_artifacts=False,
                debug_base_name=None,
                debug_output_dir="",
            )
        )
