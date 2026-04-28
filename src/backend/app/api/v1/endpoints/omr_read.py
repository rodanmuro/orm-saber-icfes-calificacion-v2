from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import csv
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.core.config import settings
from app.db.models import Exam, ExamItem, ExamVersion, ExamVersionItem, OmrAttempt, OmrAttemptAnswer, Student
from app.db.session import SessionLocal
from app.modules.omr_reader.api_service import (
    DEFAULT_METADATA_PATH,
    persist_auxiliary_ratios_csv,
    persist_question_ratios_csv,
    persist_omr_trace_json,
    persist_uploaded_image_bytes,
    resolve_reader_backend,
    run_omr_read_from_image_bytes,
)
from app.modules.omr_reader.errors import OMRReadInputError
from app.modules.omr_scoring.persistence import persist_omr_attempt, recompute_attempt_summary
from app.modules.omr_scoring.service import (
    build_answer_key_from_exam_items,
    build_answer_key_from_version_items,
    grade_omr_questions,
)
from app.modules.omr_reader.loader import load_read_metadata
from app.modules.omr_reader.api_service import resolve_backend_relative_path

router = APIRouter(prefix="/omr", tags=["omr"])
RUNTIME_THRESHOLDS = {
    "marked": settings.omr_marked_threshold,
    "unmarked": settings.omr_unmarked_threshold,
}


class ManualAnswerUpdate(BaseModel):
    question_number: int = Field(..., ge=1)
    manual_answer: str | None = None
    manual_override: bool | None = None


class ManualAnswerPayload(BaseModel):
    answers: list[ManualAnswerUpdate] = Field(default_factory=list)


class AssignAttemptPayload(BaseModel):
    exam_id: int | None = None
    exam_code: str | None = None
    exam_version_id: int | None = None
    teacher_id: int | None = None
    student_id: int | None = None
    document_number: str | None = None
    document_type: str | None = "CC"


class ThresholdsPayload(BaseModel):
    marked: float
    unmarked: float


def _normalize_exam_code(value: str | None) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.isdigit():
        return str(int(raw))
    return raw


@router.get("/thresholds")
def get_omr_thresholds() -> dict[str, float]:
    return {
        "marked": float(RUNTIME_THRESHOLDS["marked"]),
        "unmarked": float(RUNTIME_THRESHOLDS["unmarked"]),
    }


@router.patch("/thresholds")
def update_omr_thresholds(payload: ThresholdsPayload) -> dict[str, float]:
    marked = float(payload.marked)
    unmarked = float(payload.unmarked)
    if not (0.0 <= unmarked <= marked <= 1.0):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="thresholds must satisfy 0 <= unmarked <= marked <= 1",
        )
    RUNTIME_THRESHOLDS["marked"] = marked
    RUNTIME_THRESHOLDS["unmarked"] = unmarked
    return {
        "marked": marked,
        "unmarked": unmarked,
    }


logger = logging.getLogger("uvicorn.error")


@router.post("/read-photo")
async def read_photo_omr(
    photo: UploadFile = File(...),
    metadata_path: str | None = Form(None),
    px_per_mm: float = Form(10.0),
    robust_mode: bool = Form(False),
    save_debug_artifacts: bool = Form(True),
    teacher_id: int | None = Form(None),
    exam_id: int | None = Form(None),
    exam_version_id: int | None = Form(None),
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
        effective_metadata_path = settings.omr_default_metadata_path
        if metadata_path and metadata_path != effective_metadata_path:
            logger.info(
                "OMR metadata_path recibido desde front fue ignorado | received=%s configured=%s",
                metadata_path,
                effective_metadata_path,
            )
        uploaded_path = persist_uploaded_image_bytes(
            image_bytes=image_bytes,
            original_filename=photo.filename,
        )
        marked_threshold = RUNTIME_THRESHOLDS["marked"]
        unmarked_threshold = RUNTIME_THRESHOLDS["unmarked"]
        result = run_omr_read_from_image_bytes(
            image_bytes=image_bytes,
            metadata_path=effective_metadata_path,
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
        ratios_csv_path = persist_question_ratios_csv(
            uploaded_image_path=uploaded_path,
            result_payload=result,
        )
        auxiliary_ratios_csv_path = persist_auxiliary_ratios_csv(
            uploaded_image_path=uploaded_path,
            result_payload=result,
        )
        result.setdefault("diagnostics", {})
        result["diagnostics"]["uploaded_image_path"] = str(uploaded_path)
        result["diagnostics"]["trace_json_path"] = str(trace_json_path)
        result["diagnostics"]["ratios_csv_path"] = str(ratios_csv_path)
        result["diagnostics"]["auxiliary_ratios_csv_path"] = str(auxiliary_ratios_csv_path)
        result["diagnostics"]["thresholds"] = {
            "marked": marked_threshold,
            "unmarked": unmarked_threshold,
        }
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
        logger.info("OMR ratios csv saved at: %s", ratios_csv_path)
        logger.info("OMR auxiliary ratios csv saved at: %s", auxiliary_ratios_csv_path)
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

        grading_block: dict | None = None
        resolved_exam_id: int | None = None
        resolved_exam_version_id: int | None = None
        resolved_student_id: int | None = None

        def _resolve_student(db) -> int | None:
            doc_type = str(doc_value or "CC").strip()
            doc_number = str(student_value or "").strip()
            if not doc_number:
                return None
            student = db.scalar(
                select(Student).where(
                    Student.document_type == doc_type,
                    Student.document_number == doc_number,
                )
            )
            return student.id if student else None

        if exam_version_id is not None:
            with SessionLocal() as db:
                version = db.get(ExamVersion, exam_version_id)
                if version is None:
                    grading_block = {
                        "status": "resolution_error",
                        "message": f"exam_version_id={exam_version_id} not found",
                    }
                else:
                    exam = db.get(Exam, version.exam_id)
                    if exam is None:
                        grading_block = {
                            "status": "resolution_error",
                            "message": f"exam not found for version_id={exam_version_id}",
                        }
                    elif exam_id is not None and exam.id != exam_id:
                        grading_block = {
                            "status": "resolution_error",
                            "message": "exam_id does not match exam_version_id",
                        }
                    elif teacher_id is not None and exam.teacher_id != teacher_id:
                        grading_block = {
                            "status": "resolution_error",
                            "message": "teacher_id does not match exam owner",
                        }
                    else:
                        resolved_exam_id = exam.id
                        resolved_exam_version_id = version.id
                        version_items = db.scalars(
                            select(ExamVersionItem)
                            .where(ExamVersionItem.exam_version_id == version.id)
                            .order_by(ExamVersionItem.question_number.asc())
                        ).all()
                        answer_key = build_answer_key_from_version_items(version_items)
                        score_payload = grade_omr_questions(
                            answer_key=answer_key,
                            omr_questions=result.get("questions", []),
                        )
                        resolved_student_id = _resolve_student(db)
                        grading_block = {
                            "status": "graded",
                            "teacher_id": exam.teacher_id,
                            "exam_id": exam.id,
                            "exam_code": version.exam_code,
                            "exam_version_id": version.id,
                            "summary": score_payload["summary"],
                            "details": score_payload["details"],
                        }
                        logger.info(
                            "OMR grading summary | teacher_id=%s exam_id=%s version_id=%s summary=%s",
                            exam.teacher_id,
                            exam.id,
                            version.id,
                            json.dumps(score_payload["summary"], ensure_ascii=False),
                        )
        elif teacher_id is not None and exam_value:
            exam_code_raw = str(exam_value).strip()
            exam_code = _normalize_exam_code(exam_code_raw)
            if not exam_code:
                grading_block = {
                    "status": "resolution_error",
                    "message": "exam_identifier detected but empty after normalization",
                }
            else:
                with SessionLocal() as db:
                    version = db.scalar(
                        select(ExamVersion).where(
                            ExamVersion.teacher_id == teacher_id,
                            ExamVersion.exam_code == exam_code,
                        )
                    )
                    if version is None:
                        grading_block = {
                            "status": "resolution_error",
                            "message": (
                                f"exam version not found for teacher_id={teacher_id} "
                                f"and exam_code={exam_code} (raw={exam_code_raw})"
                            ),
                        }
                    else:
                        exam = db.get(Exam, version.exam_id)
                        if exam is None:
                            grading_block = {
                                "status": "resolution_error",
                                "message": f"exam not found for version_id={version.id}",
                            }
                        else:
                            resolved_exam_id = exam.id
                            resolved_exam_version_id = version.id
                            version_items = db.scalars(
                                select(ExamVersionItem)
                                .where(ExamVersionItem.exam_version_id == version.id)
                                .order_by(ExamVersionItem.question_number.asc())
                            ).all()
                            answer_key = build_answer_key_from_version_items(version_items)
                            score_payload = grade_omr_questions(
                                answer_key=answer_key,
                                omr_questions=result.get("questions", []),
                            )
                            resolved_student_id = _resolve_student(db)
                            grading_block = {
                                "status": "graded",
                                "teacher_id": teacher_id,
                                "exam_id": exam.id,
                                "exam_code": version.exam_code,
                                "exam_version_id": version.id,
                                "summary": score_payload["summary"],
                                "details": score_payload["details"],
                            }
                            logger.info(
                                "OMR grading summary | teacher_id=%s exam_id=%s version_id=%s summary=%s",
                                teacher_id,
                                exam.id,
                                version.id,
                                json.dumps(score_payload["summary"], ensure_ascii=False),
                            )
        elif teacher_id is not None and not exam_value and exam_version_id is None:
            grading_block = {
                "status": "resolution_error",
                "message": "exam_identifier not detected in OMR auxiliary block",
            }

        if grading_block is not None:
            result["grading"] = grading_block
            result.setdefault("diagnostics", {})
            result["diagnostics"]["grading_enabled"] = True
        else:
            result.setdefault("diagnostics", {})
            result["diagnostics"]["grading_enabled"] = False

        attempt_id: int | None = None
        with SessionLocal() as db:
            attempt = persist_omr_attempt(
                db=db,
                result_payload=result,
                teacher_id=teacher_id,
                exam_id=resolved_exam_id,
                exam_version_id=resolved_exam_version_id,
                student_id=resolved_student_id,
                exam_code_detected=str(exam_value).strip() if exam_value else None,
                grading_block=grading_block,
            )
            attempt_id = attempt.id
        result.setdefault("diagnostics", {})
        result["diagnostics"]["attempt_id"] = attempt_id

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
                aux_ratio_lines.append(f"{block_id}:")
                aux_ratio_lines.extend(f"  row{row}={value:.4f}" for row, value in pairs)
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
                aux_ratio_lines.append(f"{block_id}[col {col_index}]:")
                aux_ratio_lines.extend(f"  row{row}={value:.4f}" for row, value in pairs)
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


@router.get("/attempts/{attempt_id}")
def get_omr_attempt(attempt_id: int) -> dict:
    with SessionLocal() as db:
        attempt = db.get(OmrAttempt, attempt_id)
        if attempt is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="attempt not found")
        answers = db.scalars(
            select(OmrAttemptAnswer)
            .where(OmrAttemptAnswer.attempt_id == attempt_id)
            .order_by(OmrAttemptAnswer.question_number.asc())
        ).all()
        def _effective_answer(row: OmrAttemptAnswer) -> tuple[str | None, str]:
            if row.manual_override:
                manual_answer = str(row.manual_answer or "").strip().upper()
                if manual_answer == "":
                    return None, "blank"
                if manual_answer == row.correct_answer:
                    return manual_answer, "correct"
                return manual_answer, "incorrect"
            status = str(row.status or "blank")
            if status in {"correct", "incorrect", "blank", "ambiguous"}:
                return row.marked_answer, status
            if status == "detected":
                return row.marked_answer, "incorrect"
            return row.marked_answer, "blank"

        return {
            "attempt_id": attempt.id,
            "teacher_id": attempt.teacher_id,
            "exam_id": attempt.exam_id,
            "exam_version_id": attempt.exam_version_id,
            "exam_code": attempt.exam_version.exam_code if attempt.exam_version else (attempt.exam.exam_code if attempt.exam else None),
            "exam_code_detected": attempt.exam_code_detected,
            "status": attempt.status,
            "summary": {
                "score_percent": attempt.score_percent,
                "total_questions": attempt.total_questions,
                "correct": attempt.correct_count,
                "incorrect": attempt.incorrect_count,
                "blank": attempt.blank_count,
                "ambiguous": attempt.ambiguous_count,
                "manual_review_required": attempt.manual_review_required,
            },
            "artifacts": {
                "uploaded_image_path": attempt.uploaded_image_path,
                "trace_json_path": attempt.trace_json_path,
                "ratios_csv_path": attempt.ratios_csv_path,
                "auxiliary_ratios_csv_path": attempt.auxiliary_ratios_csv_path,
            },
            "student": {
                "id": attempt.student_id,
                "document_number": attempt.student.document_number if attempt.student else None,
                "document_type": attempt.student.document_type if attempt.student else None,
                "first_name": attempt.student.first_name if attempt.student else None,
                "last_name": attempt.student.last_name if attempt.student else None,
                "group_name": attempt.student.group_name if attempt.student else None,
            },
            "answers": [
                {
                    "question_number": row.question_number,
                    "item_id": row.item_id,
                    "correct_answer": row.correct_answer,
                    "marked_answer": row.marked_answer,
                    "status": row.status,
                    "marked_options": row.marked_options_json or [],
                    "manual_answer": row.manual_answer,
                    "manual_override": row.manual_override,
                    "effective_answer": _effective_answer(row)[0],
                    "effective_status": _effective_answer(row)[1],
                }
                for row in answers
            ],
        }


@router.delete("/attempts/{attempt_id}")
def delete_omr_attempt(attempt_id: int) -> dict:
    with SessionLocal() as db:
        attempt = db.get(OmrAttempt, attempt_id)
        if attempt is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="attempt not found")
        db.delete(attempt)
        db.commit()
        return {"deleted": True, "attempt_id": attempt_id}


@router.patch("/attempts/{attempt_id}/answers")
def update_omr_attempt_answers(attempt_id: int, payload: ManualAnswerPayload) -> dict:
    updates = {row.question_number: row for row in payload.answers}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="answers payload is empty")

    with SessionLocal() as db:
        attempt = db.get(OmrAttempt, attempt_id)
        if attempt is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="attempt not found")

        answers = db.scalars(
            select(OmrAttemptAnswer).where(OmrAttemptAnswer.attempt_id == attempt_id)
        ).all()
        for row in answers:
            update = updates.get(row.question_number)
            if update is None:
                continue
            manual_override = update.manual_override
            manual_answer = update.manual_answer

            if manual_override is False:
                row.manual_override = False
                row.manual_answer = None
                continue

            normalized = str(manual_answer or "").strip().upper()
            if normalized == "":
                row.manual_override = True
                row.manual_answer = None
                continue
            if normalized not in {"A", "B", "C", "D"}:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"manual_answer invalido para pregunta {row.question_number}",
                )
            if row.correct_answer is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="no se puede corregir manualmente sin clave de respuestas",
                )
            row.manual_override = True
            row.manual_answer = normalized

        db.commit()
        recompute_attempt_summary(db, attempt)

    return get_omr_attempt(attempt_id)


@router.patch("/attempts/{attempt_id}/assign")
def assign_omr_attempt(attempt_id: int, payload: AssignAttemptPayload) -> dict:
    with SessionLocal() as db:
        attempt = db.get(OmrAttempt, attempt_id)
        if attempt is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="attempt not found")

        teacher_id = payload.teacher_id or attempt.teacher_id

        exam = None
        version = None
        if payload.exam_version_id is not None:
            version = db.get(ExamVersion, payload.exam_version_id)
            if version is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam_version not found")
            exam = db.get(Exam, version.exam_id)
            if exam is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam not found for version")
            if payload.exam_id is not None and payload.exam_id != exam.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="exam_id mismatch")
        else:
            if payload.exam_id is not None:
                exam = db.get(Exam, payload.exam_id)
            elif payload.exam_code:
                if teacher_id is None:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="teacher_id required")
                exam_code = _normalize_exam_code(payload.exam_code)
                if not exam_code:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="exam_code invalid")
                version = db.scalar(
                    select(ExamVersion).where(
                        ExamVersion.teacher_id == teacher_id,
                        ExamVersion.exam_code == exam_code,
                    )
                )
                if version is not None:
                    exam = db.get(Exam, version.exam_id)
            if exam is None and version is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam not found")
            if version is None and exam is not None:
                version = db.scalar(
                    select(ExamVersion)
                    .where(ExamVersion.exam_id == exam.id)
                    .order_by(ExamVersion.id.desc())
                )
            if version is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="exam has no versions")

        student_id = attempt.student_id
        if payload.student_id is not None:
            student = db.get(Student, payload.student_id)
            if student is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="student not found")
            student_id = student.id
        elif payload.document_number:
            doc_type = str(payload.document_type or "CC").strip()
            doc_number = str(payload.document_number).strip()
            student = db.scalar(
                select(Student).where(
                    Student.document_type == doc_type,
                    Student.document_number == doc_number,
                )
            )
            if student is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="student not found")
            student_id = student.id

        answers = db.scalars(
            select(OmrAttemptAnswer).where(OmrAttemptAnswer.attempt_id == attempt_id)
        ).all()
        omr_questions = []
        for row in answers:
            marked_options = row.marked_options_json or ([] if not row.marked_answer else [row.marked_answer])
            omr_questions.append(
                {
                    "question_number": row.question_number,
                    "marked_options": marked_options,
                }
            )

        version_items = db.scalars(
            select(ExamVersionItem)
            .where(ExamVersionItem.exam_version_id == version.id)
            .order_by(ExamVersionItem.question_number.asc())
        ).all()
        answer_key = build_answer_key_from_version_items(version_items)
        score_payload = grade_omr_questions(
            answer_key=answer_key,
            omr_questions=omr_questions,
        )

        attempt.exam_id = exam.id
        attempt.exam_version_id = version.id
        attempt.student_id = student_id
        attempt.status = "needs_review" if score_payload["summary"]["ambiguous"] > 0 else "graded"
        attempt.score_percent = score_payload["summary"]["score_percent"]
        attempt.total_questions = score_payload["summary"]["total_questions"]
        attempt.correct_count = score_payload["summary"]["correct"]
        attempt.incorrect_count = score_payload["summary"]["incorrect"]
        attempt.blank_count = score_payload["summary"]["blank"]
        attempt.ambiguous_count = score_payload["summary"]["ambiguous"]
        attempt.manual_review_required = attempt.ambiguous_count > 0

        details_by_qn = {row["question_number"]: row for row in score_payload["details"]}
        for row in answers:
            detail = details_by_qn.get(row.question_number)
            if not detail:
                continue
            row.correct_answer = detail.get("correct_answer")
            row.item_id = detail.get("item_id")
            row.marked_answer = detail.get("marked_answer")
            row.status = detail.get("status")
            row.marked_options_json = detail.get("marked_options")

        db.commit()
        recompute_attempt_summary(db, attempt)

    return get_omr_attempt(attempt_id)


@router.get("/attempts")
def list_omr_attempts(
    teacher_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    with SessionLocal() as db:
        statement = select(OmrAttempt).order_by(OmrAttempt.id.desc()).limit(limit).offset(offset)
        if teacher_id is not None:
            statement = statement.where(OmrAttempt.teacher_id == teacher_id)
        attempts = db.scalars(statement).all()
        rows = []
        for attempt in attempts:
            rows.append(
                {
                    "attempt_id": attempt.id,
                    "teacher_id": attempt.teacher_id,
                    "exam_id": attempt.exam_id,
                    "exam_code": attempt.exam_version.exam_code if attempt.exam_version else (attempt.exam.exam_code if attempt.exam else None),
                    "exam_title": attempt.exam.title if attempt.exam else None,
                    "exam_version_id": attempt.exam_version_id,
                    "exam_version_code": attempt.exam_version.version_code if attempt.exam_version else None,
                    "student_id": attempt.student_id,
                    "student_name": (
                        f"{attempt.student.first_name} {attempt.student.last_name}" if attempt.student else None
                    ),
                    "student_group": attempt.student.group_name if attempt.student else None,
                    "status": attempt.status,
                    "score_percent": attempt.score_percent,
                    "total_questions": attempt.total_questions,
                    "correct_count": attempt.correct_count,
                    "incorrect_count": attempt.incorrect_count,
                    "blank_count": attempt.blank_count,
                    "manual_review_required": attempt.manual_review_required,
                    "uploaded_image_path": attempt.uploaded_image_path,
                    "created_at": attempt.created_at,
                }
            )
        return rows


def _load_question_ratios(path: str) -> list[dict]:
    rows: dict[int, dict] = {}
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            try:
                qn = int(raw.get("question_number") or 0)
            except ValueError:
                continue
            if qn <= 0:
                continue
            entry = rows.setdefault(
                qn,
                {
                    "question_number": qn,
                    "ratios": {},
                    "top1_label": raw.get("top1_label"),
                    "top1_ratio": raw.get("top1_ratio"),
                    "top2_label": raw.get("top2_label"),
                    "top2_ratio": raw.get("top2_ratio"),
                    "margin": raw.get("margin_top1_top2"),
                    "marked_options": raw.get("marked_options") or "",
                    "ambiguous_options": raw.get("ambiguous_options") or "",
                },
            )
            label = raw.get("option_label")
            ratio = raw.get("fill_ratio")
            if label:
                entry["ratios"][label] = ratio
    return [rows[key] for key in sorted(rows.keys())]


def _load_auxiliary_ratios(path: str) -> list[dict]:
    rows: list[dict] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            rows.append(raw)
    return rows


def _effective_answer_value(row: OmrAttemptAnswer) -> str | None:
    if row.manual_override:
        manual_answer = str(row.manual_answer or "").strip().upper()
        return manual_answer or None
    return row.marked_answer


@router.get("/attempts/{attempt_id}/overlay")
def get_omr_attempt_overlay(attempt_id: int) -> dict:
    with SessionLocal() as db:
        attempt = db.get(OmrAttempt, attempt_id)
        if attempt is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="attempt not found")
        aligned_image_path = None
        px_per_mm = 10.0

        if attempt.trace_json_path:
            trace_path = Path(attempt.trace_json_path)
            if trace_path.exists():
                with trace_path.open("r", encoding="utf-8") as handle:
                    trace_payload = json.load(handle)
                diagnostics = trace_payload.get("diagnostics", {}) if isinstance(trace_payload, dict) else {}
                aligned_image_path = diagnostics.get("aligned_image_path") or aligned_image_path
                try:
                    px_per_mm = float(diagnostics.get("px_per_mm") or px_per_mm)
                except (TypeError, ValueError):
                    px_per_mm = px_per_mm

        if not aligned_image_path and attempt.uploaded_image_path:
            uploaded_path = Path(str(attempt.uploaded_image_path))
            aligned_candidate = uploaded_path.with_suffix(".aligned.jpg")
            if aligned_candidate.exists():
                aligned_image_path = str(aligned_candidate)

        if not aligned_image_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="aligned_image_path not available")

        metadata_file = resolve_backend_relative_path(settings.omr_default_metadata_path)
        metadata = load_read_metadata(metadata_file)
        question_items = metadata.get("question_items", [])
        page = metadata.get("page", {}) if isinstance(metadata, dict) else {}
        page_width_px = None
        page_height_px = None
        try:
            page_width_px = round(float(page.get("width_mm")) * px_per_mm, 2)
            page_height_px = round(float(page.get("height_mm")) * px_per_mm, 2)
        except (TypeError, ValueError):
            page_width_px = None
            page_height_px = None
        if not isinstance(question_items, list):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="invalid metadata")

        answers = db.scalars(
            select(OmrAttemptAnswer).where(OmrAttemptAnswer.attempt_id == attempt_id)
        ).all()
        answer_by_question = {row.question_number: row for row in answers}

        questions = []
        for question in question_items:
            qn = int(question.get("question_number", -1))
            options = []
            answer_row = answer_by_question.get(qn)
            correct_answer = answer_row.correct_answer if answer_row else None
            marked_answer = answer_row.marked_answer if answer_row else None
            effective_answer = _effective_answer_value(answer_row) if answer_row else None

            for option in question.get("options", []) if isinstance(question.get("options"), list) else []:
                label = str(option.get("label", ""))
                cx = float(option.get("center_x_mm", 0.0)) * px_per_mm
                cy = float(option.get("center_y_mm", 0.0)) * px_per_mm
                r = float(option.get("radius_mm", 0.0)) * px_per_mm
                options.append(
                    {
                        "label": label,
                        "cx": round(cx, 2),
                        "cy": round(cy, 2),
                        "r": round(r, 2),
                        "is_correct": label == correct_answer if correct_answer else False,
                        "is_marked": label == marked_answer if marked_answer else False,
                        "is_effective": label == effective_answer if effective_answer else False,
                    }
                )
            questions.append({"question_number": qn, "options": options})

        return {
            "attempt_id": attempt.id,
            "aligned_image_path": aligned_image_path,
            "px_per_mm": px_per_mm,
            "page_width_px": page_width_px,
            "page_height_px": page_height_px,
            "questions": questions,
        }


@router.get("/attempts/{attempt_id}/ratios")
def get_omr_attempt_ratios(attempt_id: int) -> dict:
    with SessionLocal() as db:
        attempt = db.get(OmrAttempt, attempt_id)
        if attempt is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="attempt not found")
        if not attempt.ratios_csv_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ratios_csv_path not found")
        if not attempt.auxiliary_ratios_csv_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="auxiliary_ratios_csv_path not found")

        question_ratios = _load_question_ratios(attempt.ratios_csv_path)
        auxiliary_ratios = _load_auxiliary_ratios(attempt.auxiliary_ratios_csv_path)

        return {
            "attempt_id": attempt.id,
            "ratios_csv_path": attempt.ratios_csv_path,
            "auxiliary_ratios_csv_path": attempt.auxiliary_ratios_csv_path,
            "question_ratios": question_ratios,
            "auxiliary_ratios": auxiliary_ratios,
        }
