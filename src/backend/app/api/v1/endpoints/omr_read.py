from __future__ import annotations

import json
import logging
import time

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.config import settings
from app.modules.omr_reader.api_service import (
    DEFAULT_METADATA_PATH,
    persist_omr_trace_json,
    persist_uploaded_image_bytes,
    resolve_reader_backend,
    run_omr_read_from_image_bytes,
)
from app.modules.omr_reader.errors import OMRReadInputError

router = APIRouter(prefix="/omr", tags=["omr"])
logger = logging.getLogger("uvicorn.error")


@router.post("/read-photo")
async def read_photo_omr(
    photo: UploadFile = File(...),
    metadata_path: str = Form(DEFAULT_METADATA_PATH),
    px_per_mm: float = Form(10.0),
    marked_threshold: float = Form(0.12),
    unmarked_threshold: float = Form(0.08),
    robust_mode: bool = Form(False),
    save_debug_artifacts: bool = Form(True),
) -> dict:
    try:
        request_start = time.perf_counter()
        configured_backend = resolve_reader_backend(None)
        if configured_backend == "gemini":
            logger.info("Enviando a Gemini | model=%s", settings.gemini_model)
        elif configured_backend == "openai":
            logger.info("Enviando a OpenAI | model=%s", settings.openai_model)
        else:
            logger.info("Procesando lectura OMR con motor=%s", configured_backend)

        image_bytes = await photo.read()
        uploaded_path = persist_uploaded_image_bytes(
            image_bytes=image_bytes,
            original_filename=photo.filename,
        )
        result = run_omr_read_from_image_bytes(
            image_bytes=image_bytes,
            metadata_path=metadata_path,
            px_per_mm=px_per_mm,
            marked_threshold=marked_threshold,
            unmarked_threshold=unmarked_threshold,
            robust_mode=robust_mode,
            save_debug_artifacts=save_debug_artifacts,
            debug_base_name=uploaded_path.stem,
        )
        trace_json_path = persist_omr_trace_json(
            uploaded_image_path=uploaded_path,
            result_payload=result,
        )
        result.setdefault("diagnostics", {})
        result["diagnostics"]["uploaded_image_path"] = str(uploaded_path)
        result["diagnostics"]["trace_json_path"] = str(trace_json_path)
        result["diagnostics"]["request_total_ms"] = round((time.perf_counter() - request_start) * 1000.0, 2)
        review_questions = sorted(
            int(item.get("question_number"))
            for item in result.get("questions", [])
            if item.get("ambiguous_options")
        )
        result["diagnostics"]["manual_review_questions"] = review_questions
        result["diagnostics"]["manual_review_required"] = bool(review_questions)
        logger.info(
            "OMR read completed | template=%s version=%s summary=%s",
            result.get("template_id"),
            result.get("version"),
            json.dumps(result.get("quality_summary", {}), ensure_ascii=False),
        )
        logger.info("OMR image saved at: %s", uploaded_path)
        logger.info("OMR trace json saved at: %s", trace_json_path)
        diagnostics = result.get("diagnostics", {})
        engine = diagnostics.get("reader_backend", configured_backend)
        usage = diagnostics.get("gemini_usage", {})
        if engine == "openai":
            usage = diagnostics.get("openai_usage", usage)
        report = diagnostics.get("gemini_report", {})
        if engine == "openai":
            report = diagnostics.get("openai_report", report)
        gemini_latency_ms = diagnostics.get("gemini_model_latency_ms")
        if engine == "openai":
            gemini_latency_ms = diagnostics.get("openai_model_latency_ms")
        request_total_ms = diagnostics.get("request_total_ms")
        logger.info(
            "OMR engine=%s usage=%s report=%s gemini_model_latency_ms=%s request_total_ms=%s",
            engine,
            json.dumps(usage, ensure_ascii=False),
            json.dumps(report, ensure_ascii=False),
            gemini_latency_ms,
            request_total_ms,
        )
        auxiliary = result.get("auxiliary", {})
        blocks = auxiliary.get("blocks", []) if isinstance(auxiliary, dict) else []
        by_id = {str(item.get("block_id")): item for item in blocks if isinstance(item, dict)}
        doc_block = by_id.get("document_type", {})
        doc_selected = doc_block.get("selected", {}) if isinstance(doc_block, dict) else {}
        doc_value = doc_selected.get("value")
        doc_status = doc_selected.get("status")
        student_block = by_id.get("student_identity_number", {})
        exam_block = by_id.get("exam_identifier", {})
        student_value = student_block.get("value") if isinstance(student_block, dict) else None
        exam_value = exam_block.get("value") if isinstance(exam_block, dict) else None

        def _problem_columns(block_obj: dict) -> list[int]:
            cols = []
            for col in block_obj.get("columns", []) if isinstance(block_obj, dict) else []:
                if str(col.get("status")) in {"missing", "ambiguous"}:
                    cols.append(int(col.get("column_index", -1)))
            return cols

        student_problem_cols = _problem_columns(student_block if isinstance(student_block, dict) else {})
        exam_problem_cols = _problem_columns(exam_block if isinstance(exam_block, dict) else {})

        aux_summary = auxiliary.get("summary", {}) if isinstance(auxiliary, dict) else {}
        logger.info(
            "OMR auxiliary summary=%s document_type=%s (%s) student_id=%s exam_id=%s",
            json.dumps(aux_summary, ensure_ascii=False),
            doc_value,
            doc_status,
            student_value,
            exam_value,
        )
        if student_problem_cols:
            logger.warning(
                "OMR alerta revision identidad | problematic_columns=%s",
                student_problem_cols,
            )
        if exam_problem_cols:
            logger.warning(
                "OMR alerta revision id_examen | problematic_columns=%s",
                exam_problem_cols,
            )
        if doc_status in {"missing", "ambiguous"}:
            logger.warning(
                "OMR alerta revision tipo_documento | status=%s",
                doc_status,
            )

        if review_questions:
            logger.warning(
                "OMR alerta revisión manual | ambiguous_questions=%s",
                review_questions,
            )
        lines: list[str] = []
        ratio_lines: list[str] = []
        for item in result.get("questions", []):
            question_number = item.get("question_number")
            marked_options = item.get("marked_options", [])
            marked_text = ", ".join(marked_options) if marked_options else "-"
            ambiguous_options = item.get("ambiguous_options", [])
            review_suffix = ""
            if ambiguous_options:
                review_suffix = f" [REVISAR ambigua: {', '.join(ambiguous_options)}]"
            lines.append(f"pregunta {question_number}: {marked_text}{review_suffix}")
            options = item.get("options", [])
            ratios_by_label: dict[str, float] = {}
            for option in options:
                label = str(option.get("label", ""))
                if not label:
                    continue
                ratios_by_label[label] = float(option.get("fill_ratio", 0.0))
            sorted_ratios = sorted(
                ratios_by_label.items(),
                key=lambda pair: pair[1],
                reverse=True,
            )
            margin = 0.0
            if len(sorted_ratios) >= 2:
                margin = sorted_ratios[0][1] - sorted_ratios[1][1]
            ratio_text = ", ".join(f"{label}={value:.4f}" for label, value in sorted_ratios)
            ratio_lines.append(f"pregunta {question_number}: {ratio_text} | margin={margin:.4f}")

        logger.info("OMR respuestas leidas:\n%s", "\n".join(lines))
        logger.info("OMR ratios por pregunta:\n%s", "\n".join(ratio_lines))
        aux_ratio_lines: list[str] = []
        for block in blocks:
            if not isinstance(block, dict):
                continue
            block_id = str(block.get("block_id", "aux"))
            selection_mode = str(block.get("selection_mode", ""))
            if selection_mode == "single_choice":
                selected = block.get("selected", {})
                ratios_by_row = selected.get("ratios_by_row", {}) if isinstance(selected, dict) else {}
                pairs = sorted(
                    ((int(row), float(value)) for row, value in ratios_by_row.items()),
                    key=lambda pair: pair[1],
                    reverse=True,
                )
                ratio_text = ", ".join(f"row{row}={value:.4f}" for row, value in pairs)
                aux_ratio_lines.append(f"{block_id}: {ratio_text}")
                continue

            for col in block.get("columns", []) if isinstance(block.get("columns"), list) else []:
                if not isinstance(col, dict):
                    continue
                col_index = int(col.get("column_index", -1))
                ratios_by_row = col.get("ratios_by_row", {})
                pairs = sorted(
                    ((int(row), float(value)) for row, value in ratios_by_row.items()),
                    key=lambda pair: pair[1],
                    reverse=True,
                )
                ratio_text = ", ".join(f"row{row}={value:.4f}" for row, value in pairs)
                aux_ratio_lines.append(f"{block_id}[col {col_index}]: {ratio_text}")
        if aux_ratio_lines:
            logger.info("OMR ratios auxiliares:\n%s", "\n".join(aux_ratio_lines))
        return result
    except OMRReadInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"unexpected server error: {exc}",
        ) from exc
