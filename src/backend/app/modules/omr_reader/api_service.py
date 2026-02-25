from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import cv2
import numpy as np

from app.core.config import settings
from app.modules.omr_reader.alignment import align_image_to_template
from app.modules.omr_reader.auxiliary_blocks import read_auxiliary_blocks
from app.modules.omr_reader.bubble_classifier import classify_bubbles
from app.modules.omr_reader.errors import (
    GeminiReadError,
    InvalidImageError,
    InvalidMetadataError,
    OpenAIReadError,
    UnsupportedReaderBackendError,
)
from app.modules.omr_reader.gemini_reader import run_gemini_omr_read
from app.modules.omr_reader.loader import load_read_metadata
from app.modules.omr_reader.llm_preprocess import prepare_llm_image_bytes
from app.modules.omr_reader.reader_strategy import (
    BACKEND_CLASSIC,
    BACKEND_GEMINI,
    BACKEND_OPENAI,
    OMRReadEngine,
    OMRReadRequest,
    SUPPORTED_OMR_BACKENDS,
    normalize_reader_backend,
)
from app.modules.omr_reader.result_builder import build_omr_read_result
from app.modules.omr_reader.openai_reader import run_openai_omr_read

DEFAULT_METADATA_PATH = settings.omr_default_metadata_path
DEFAULT_UPLOADS_DIR = "data/input/mobile_uploads"
DEFAULT_DEBUG_OUTPUT_DIR = "data/output/debug_preprocess"


def run_omr_read_from_image_bytes(
    *,
    image_bytes: bytes,
    metadata_path: str = DEFAULT_METADATA_PATH,
    px_per_mm: float = 10.0,
    marked_threshold: float = settings.omr_marked_threshold,
    unmarked_threshold: float = settings.omr_unmarked_threshold,
    robust_mode: bool = False,
    save_debug_artifacts: bool = False,
    debug_base_name: str | None = None,
    debug_output_dir: str = DEFAULT_DEBUG_OUTPUT_DIR,
    reader_backend: str | None = None,
) -> dict[str, Any]:
    backend = resolve_reader_backend(reader_backend)
    request = OMRReadRequest(
        image_bytes=image_bytes,
        metadata_path=metadata_path,
        px_per_mm=px_per_mm,
        marked_threshold=marked_threshold,
        unmarked_threshold=unmarked_threshold,
        robust_mode=robust_mode,
        save_debug_artifacts=save_debug_artifacts,
        debug_base_name=debug_base_name,
        debug_output_dir=debug_output_dir,
    )
    engine = get_omr_reader_engine(backend)
    result = engine.read(request)
    result.setdefault("diagnostics", {})
    result["diagnostics"]["reader_backend"] = backend
    return result


class ClassicOMRReadEngine:
    def read(self, request: OMRReadRequest) -> dict[str, Any]:
        return _run_classic_omr_read_from_image_bytes(request=request)


class GeminiOMRReadEngine:
    def read(self, request: OMRReadRequest) -> dict[str, Any]:
        if not settings.gemini_api_key:
            raise GeminiReadError("GEMINI_API_KEY is not configured")
        metadata_file = resolve_backend_relative_path(request.metadata_path)
        metadata = load_read_metadata(metadata_file)
        image = decode_image_bytes(image_bytes=request.image_bytes)
        prepared = prepare_llm_image_bytes(
            image=image,
            metadata=metadata,
            px_per_mm=request.px_per_mm,
        )
        return run_gemini_omr_read(
            image_bytes=prepared["image_bytes"],
            metadata=metadata,
            metadata_file=metadata_file,
            preprocess_diagnostics=prepared["diagnostics"],
        )


class OpenAIOMRReadEngine:
    def read(self, request: OMRReadRequest) -> dict[str, Any]:
        if not settings.openai_api_key:
            raise OpenAIReadError("OPENAI_API_KEY is not configured")
        metadata_file = resolve_backend_relative_path(request.metadata_path)
        metadata = load_read_metadata(metadata_file)
        image = decode_image_bytes(image_bytes=request.image_bytes)
        prepared = prepare_llm_image_bytes(
            image=image,
            metadata=metadata,
            px_per_mm=request.px_per_mm,
        )
        return run_openai_omr_read(
            image_bytes=prepared["image_bytes"],
            metadata=metadata,
            metadata_file=metadata_file,
            preprocess_diagnostics=prepared["diagnostics"],
        )


def resolve_reader_backend(reader_backend: str | None) -> str:
    backend = normalize_reader_backend(reader_backend or settings.omr_reader_backend)
    if backend not in SUPPORTED_OMR_BACKENDS:
        raise UnsupportedReaderBackendError(
            f"reader backend '{backend}' is not supported; valid values: {sorted(SUPPORTED_OMR_BACKENDS)}"
        )
    return backend


def get_omr_reader_engine(backend: str) -> OMRReadEngine:
    if backend == BACKEND_CLASSIC:
        return ClassicOMRReadEngine()
    if backend == BACKEND_GEMINI:
        return GeminiOMRReadEngine()
    if backend == BACKEND_OPENAI:
        return OpenAIOMRReadEngine()
    raise UnsupportedReaderBackendError(
        f"reader backend '{backend}' is not supported; valid values: {sorted(SUPPORTED_OMR_BACKENDS)}"
    )


def _run_classic_omr_read_from_image_bytes(*, request: OMRReadRequest) -> dict[str, Any]:
    metadata_file = resolve_backend_relative_path(request.metadata_path)
    metadata = load_read_metadata(metadata_file)
    image = decode_image_bytes(image_bytes=request.image_bytes)

    aligned = align_image_to_template(
        image=image,
        metadata=metadata,
        px_per_mm=request.px_per_mm,
    )
    debug_artifacts: dict[str, np.ndarray] | None = {} if request.save_debug_artifacts else None
    bubbles = classify_bubbles(
        aligned_image=aligned.aligned_image,
        metadata=metadata,
        px_per_mm=request.px_per_mm,
        marked_threshold=request.marked_threshold,
        unmarked_threshold=request.unmarked_threshold,
        robust_mode=request.robust_mode,
        debug_artifacts=debug_artifacts,
    )
    result = build_omr_read_result(metadata=metadata, bubble_results=bubbles)
    auxiliary = read_auxiliary_blocks(
        aligned_image=aligned.aligned_image,
        metadata=metadata,
        px_per_mm=request.px_per_mm,
        marked_threshold=request.marked_threshold,
        unmarked_threshold=request.unmarked_threshold,
        robust_mode=request.robust_mode,
    )
    result["auxiliary"] = auxiliary
    result["thresholds"] = {
        "marked": request.marked_threshold,
        "unmarked": request.unmarked_threshold,
    }
    result["diagnostics"] = {
        "metadata_path": str(metadata_file),
        "detected_marker_ids": aligned.detected_marker_ids,
        "robust_mode": request.robust_mode,
        "auxiliary_summary": auxiliary.get("summary", {}),
    }
    if request.save_debug_artifacts:
        debug_paths = persist_debug_artifacts(
            aligned_image=aligned.aligned_image,
            binary_inv=debug_artifacts["binary_inv"] if debug_artifacts else None,
            debug_base_name=request.debug_base_name,
            output_dir=request.debug_output_dir,
        )
        result["diagnostics"]["debug_artifacts"] = {k: str(v) for k, v in debug_paths.items()}
    return result


def decode_image_bytes(*, image_bytes: bytes) -> np.ndarray:
    if not image_bytes:
        raise InvalidImageError("uploaded image is empty")

    np_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidImageError("uploaded file is not a valid image (jpg/png)")
    return image


def persist_uploaded_image_bytes(
    *,
    image_bytes: bytes,
    original_filename: str | None = None,
    uploads_dir: str = DEFAULT_UPLOADS_DIR,
) -> Path:
    uploads_path = resolve_backend_relative_path(uploads_dir)
    uploads_path.mkdir(parents=True, exist_ok=True)

    ext = ".jpg"
    if original_filename:
        candidate = Path(original_filename).suffix.lower()
        if candidate in {".jpg", ".jpeg", ".png", ".webp"}:
            ext = candidate

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"mobile_{stamp}_{uuid4().hex[:8]}{ext}"
    out_path = uploads_path / file_name
    out_path.write_bytes(image_bytes)
    return out_path


def persist_omr_trace_json(
    *,
    uploaded_image_path: Path,
    result_payload: dict[str, Any],
) -> Path:
    trace_path = uploaded_image_path.with_suffix(".result.json")

    answers_by_question: list[dict[str, Any]] = []
    for question in result_payload.get("questions", []):
        marked = list(question.get("marked_options", []))
        ambiguous = list(question.get("ambiguous_options", []))
        answers_by_question.append(
            {
                "question_number": question.get("question_number"),
                "marked_options": marked,
                "ambiguous_options": ambiguous,
                "status": (
                    "marked_with_ambiguity"
                    if marked and ambiguous
                    else "marked"
                    if marked
                    else "ambiguous"
                    if ambiguous
                    else "blank"
                ),
                "manual_review_required": bool(ambiguous),
            }
        )

    trace_payload = {
        "template_id": result_payload.get("template_id"),
        "version": result_payload.get("version"),
        "timestamp": result_payload.get("timestamp"),
        "uploaded_image_path": str(uploaded_image_path),
        "quality_summary": result_payload.get("quality_summary", {}),
        "answers_by_question": answers_by_question,
        "auxiliary": result_payload.get("auxiliary", {}),
    }
    trace_path.write_text(
        json.dumps(trace_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return trace_path


def persist_question_ratios_csv(
    *,
    uploaded_image_path: Path,
    result_payload: dict[str, Any],
) -> Path:
    csv_path = uploaded_image_path.with_suffix(".ratios.csv")
    questions = result_payload.get("questions", [])

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "question_number",
                "marked_options",
                "ambiguous_options",
                "option_label",
                "option_state",
                "fill_ratio",
                "rank",
                "top1_label",
                "top1_ratio",
                "top2_label",
                "top2_ratio",
                "margin_top1_top2",
            ]
        )
        for question in questions if isinstance(questions, list) else []:
            qn = question.get("question_number")
            marked = "|".join(question.get("marked_options", []))
            ambiguous = "|".join(question.get("ambiguous_options", []))
            options = question.get("options", [])
            ranked = sorted(
                [
                    (
                        str(option.get("label", "")),
                        str(option.get("state", "")),
                        float(option.get("fill_ratio", 0.0)),
                    )
                    for option in options
                    if isinstance(option, dict)
                ],
                key=lambda item: item[2],
                reverse=True,
            )
            top1_label, _, top1_ratio = ranked[0] if ranked else ("", "", 0.0)
            top2_label, _, top2_ratio = ranked[1] if len(ranked) > 1 else ("", "", 0.0)
            margin = top1_ratio - top2_ratio
            for rank, (label, state, ratio) in enumerate(ranked, start=1):
                writer.writerow(
                    [
                        qn,
                        marked,
                        ambiguous,
                        label,
                        state,
                        round(ratio, 6),
                        rank,
                        top1_label,
                        round(top1_ratio, 6),
                        top2_label,
                        round(top2_ratio, 6),
                        round(margin, 6),
                    ]
                )
    return csv_path


def persist_auxiliary_ratios_csv(
    *,
    uploaded_image_path: Path,
    result_payload: dict[str, Any],
) -> Path:
    csv_path = uploaded_image_path.with_suffix(".auxiliary.ratios.csv")
    auxiliary = result_payload.get("auxiliary", {})
    blocks = auxiliary.get("blocks", []) if isinstance(auxiliary, dict) else []

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "block_id",
                "selection_mode",
                "column_index",
                "status",
                "value",
                "row_index",
                "marked_rows",
                "ambiguous_rows",
                "row",
                "fill_ratio",
                "rank",
                "top1_row",
                "top1_ratio",
                "top2_row",
                "top2_ratio",
                "margin_top1_top2",
            ]
        )

        for block in blocks if isinstance(blocks, list) else []:
            if not isinstance(block, dict):
                continue
            block_id = str(block.get("block_id", ""))
            selection_mode = str(block.get("selection_mode", ""))
            if selection_mode == "single_choice":
                selected = block.get("selected", {})
                ratios_by_row = selected.get("ratios_by_row", {}) if isinstance(selected, dict) else {}
                ranked = sorted(
                    [(int(row), float(ratio)) for row, ratio in ratios_by_row.items()],
                    key=lambda item: item[1],
                    reverse=True,
                )
                top1_row, top1_ratio = ranked[0] if ranked else ("", 0.0)
                top2_row, top2_ratio = ranked[1] if len(ranked) > 1 else ("", 0.0)
                margin = top1_ratio - top2_ratio
                for rank, (row, ratio) in enumerate(ranked, start=1):
                    writer.writerow(
                        [
                            block_id,
                            selection_mode,
                            "",
                            selected.get("status", ""),
                            selected.get("value", ""),
                            selected.get("row_index", ""),
                            "|".join(str(x) for x in selected.get("marked_rows", [])),
                            "|".join(str(x) for x in selected.get("ambiguous_rows", [])),
                            row,
                            round(ratio, 6),
                            rank,
                            top1_row,
                            round(top1_ratio, 6),
                            top2_row,
                            round(top2_ratio, 6),
                            round(margin, 6),
                        ]
                    )
                continue

            for col in block.get("columns", []) if isinstance(block.get("columns"), list) else []:
                if not isinstance(col, dict):
                    continue
                ratios_by_row = col.get("ratios_by_row", {})
                ranked = sorted(
                    [(int(row), float(ratio)) for row, ratio in ratios_by_row.items()],
                    key=lambda item: item[1],
                    reverse=True,
                )
                top1_row, top1_ratio = ranked[0] if ranked else ("", 0.0)
                top2_row, top2_ratio = ranked[1] if len(ranked) > 1 else ("", 0.0)
                margin = top1_ratio - top2_ratio
                for rank, (row, ratio) in enumerate(ranked, start=1):
                    writer.writerow(
                        [
                            block_id,
                            selection_mode,
                            col.get("column_index", ""),
                            col.get("status", ""),
                            col.get("value", ""),
                            col.get("row_index", ""),
                            "|".join(str(x) for x in col.get("marked_rows", [])),
                            "|".join(str(x) for x in col.get("ambiguous_rows", [])),
                            row,
                            round(ratio, 6),
                            rank,
                            top1_row,
                            round(top1_ratio, 6),
                            top2_row,
                            round(top2_ratio, 6),
                            round(margin, 6),
                        ]
                    )
    return csv_path


def persist_debug_artifacts(
    *,
    aligned_image: np.ndarray,
    binary_inv: np.ndarray | None,
    debug_base_name: str | None,
    output_dir: str = DEFAULT_DEBUG_OUTPUT_DIR,
) -> dict[str, Path]:
    out_dir = resolve_backend_relative_path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = debug_base_name or f"omr_{stamp}_{uuid4().hex[:8]}"

    aligned_path = out_dir / f"{prefix}.aligned.jpg"
    cv2.imwrite(str(aligned_path), aligned_image)

    output: dict[str, Path] = {"aligned": aligned_path}
    if binary_inv is not None:
        binary_path = out_dir / f"{prefix}.binary_inv.png"
        cv2.imwrite(str(binary_path), binary_inv)
        output["binary_inv"] = binary_path
    return output


def resolve_backend_relative_path(path_value: str) -> Path:
    backend_root = Path(__file__).resolve().parents[3]
    candidate = Path(path_value)

    resolved = (backend_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    if not str(resolved).startswith(str(backend_root.resolve())):
        raise InvalidMetadataError("metadata_path must stay inside backend directory")
    return resolved
