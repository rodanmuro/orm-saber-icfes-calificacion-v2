from __future__ import annotations

import io
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from sqlalchemy import select

from app.core.config import settings
from app.db.models import OmrAttempt, OmrAttemptAnswer, Student
from app.db.session import SessionLocal
from app.modules.omr_reader.api_service import resolve_backend_relative_path
from app.modules.omr_reader.loader import load_read_metadata

router = APIRouter(prefix="/student-portal", tags=["student-portal"])


class StudentPortalAuthPayload(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    document_number: str = Field(min_length=3, max_length=32)


def _normalize_email(value: str) -> str:
    return str(value or "").strip().lower()


def _normalize_doc(value: str) -> str:
    return str(value or "").strip()


def _effective_answer(row: OmrAttemptAnswer) -> tuple[str | None, str]:
    if row.manual_override:
        manual_answer = str(row.manual_answer or "").strip().upper() or None
        if manual_answer:
            if row.correct_answer and manual_answer == row.correct_answer:
                return manual_answer, "correct"
            return manual_answer, "incorrect"
        return None, "blank"

    marked_answer = row.marked_answer
    status = str(row.status or "").lower()
    if status in {"blank", "missing"}:
        return None, "blank"
    if status == "ambiguous":
        return marked_answer, "ambiguous"
    if row.correct_answer and marked_answer == row.correct_answer:
        return marked_answer, "correct"
    if marked_answer:
        return marked_answer, "incorrect"
    return None, "blank"


def _build_overlay_payload(attempt: OmrAttempt) -> dict:
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
                px_per_mm = 10.0

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
        pass

    if not isinstance(question_items, list):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="invalid metadata")

    answer_by_question = {row.question_number: row for row in attempt.answers}
    questions = []
    for question in question_items:
        qn = int(question.get("question_number", -1))
        options = []
        answer_row = answer_by_question.get(qn)
        correct_answer = answer_row.correct_answer if answer_row else None
        marked_answer = answer_row.marked_answer if answer_row else None
        effective_answer, effective_status = _effective_answer(answer_row) if answer_row else (None, "blank")
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
                    "effective_status": effective_status,
                }
            )
        questions.append({"question_number": qn, "options": options})

    return {
        "aligned_image_path": str(aligned_image_path),
        "page_width_px": page_width_px,
        "page_height_px": page_height_px,
        "questions": questions,
    }


def _render_attempt_pdf(attempt: OmrAttempt, overlay_payload: dict) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 36
    y = height - margin

    exam_title = attempt.exam.title if attempt.exam else "Examen"
    version_code = attempt.exam_version.version_code if attempt.exam_version else "-"
    student_name = f"{attempt.student.first_name} {attempt.student.last_name}" if attempt.student else "-"
    student_group = attempt.student.group_name if attempt.student else "-"
    student_doc = attempt.student.document_number if attempt.student else "-"

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Resultado individual")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Examen: {exam_title}")
    y -= 14
    c.drawString(margin, y, f"Version: {version_code}")
    y -= 14
    c.drawString(margin, y, f"Estudiante: {student_name} | Grupo: {student_group} | Documento: {student_doc}")
    y -= 14
    c.drawString(
        margin,
        y,
        f"Puntaje: {attempt.score_percent if attempt.score_percent is not None else '-'} | "
        f"Correctas: {attempt.correct_count} | Incorrectas: {attempt.incorrect_count} | "
        f"No marcadas: {attempt.blank_count}",
    )
    y -= 22

    aligned_image_path = overlay_payload["aligned_image_path"]
    img = ImageReader(aligned_image_path)
    iw, ih = img.getSize()
    max_w = width - (margin * 2)
    max_h = min(290, y - 120)
    scale = min(max_w / iw, max_h / ih)
    draw_w = iw * scale
    draw_h = ih * scale
    img_x = margin
    img_y = y - draw_h

    c.drawImage(img, img_x, img_y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask="auto")

    sx = draw_w / float(overlay_payload.get("page_width_px") or iw)
    sy = draw_h / float(overlay_payload.get("page_height_px") or ih)
    c.setLineWidth(1.6)
    for question in overlay_payload["questions"]:
        for option in question["options"]:
            if not option.get("is_effective"):
                continue
            ox = img_x + (option["cx"] * sx)
            oy = img_y + draw_h - (option["cy"] * sy)
            rr = max(4, option["r"] * ((sx + sy) / 2))
            if option.get("is_correct"):
                c.setStrokeColorRGB(0.0, 0.6, 0.0)
            else:
                c.setStrokeColorRGB(0.85, 0.0, 0.0)
            c.circle(ox, oy, rr, stroke=1, fill=0)

    y = img_y - 18
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Respuestas (correcta vs marcada)")
    y -= 14
    c.setFont("Helvetica", 9)
    for row in sorted(attempt.answers, key=lambda x: x.question_number):
        effective_answer, effective_status = _effective_answer(row)
        line = (
            f"P{row.question_number:02d}: correcta={row.correct_answer or '-'} | "
            f"marcada={effective_answer or '-'} | estado={effective_status}"
        )
        c.drawString(margin, y, line[:140])
        y -= 12
        if y < 40:
            c.showPage()
            y = height - margin
            c.setFont("Helvetica", 9)

    c.showPage()
    c.save()
    return buffer.getvalue()


def _get_student_by_credentials(db, email: str, document_number: str) -> Student:
    normalized_email = _normalize_email(email)
    normalized_doc = _normalize_doc(document_number)
    student = db.scalar(
        select(Student).where(
            Student.email == normalized_email,
            Student.document_number == normalized_doc,
        )
    )
    if student is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="credenciales invalidas")
    return student


@router.post("/authenticate")
def authenticate_student_portal(payload: StudentPortalAuthPayload) -> dict:
    with SessionLocal() as db:
        student = _get_student_by_credentials(db, payload.email, payload.document_number)
        attempts = db.scalars(
            select(OmrAttempt)
            .where(OmrAttempt.student_id == student.id)
            .order_by(OmrAttempt.created_at.desc())
        ).all()
        return {
            "student": {
                "id": student.id,
                "email": student.email,
                "document_number": student.document_number,
                "name": f"{student.first_name} {student.last_name}",
                "group_name": student.group_name,
            },
            "attempts": [
                {
                    "attempt_id": row.id,
                    "exam_id": row.exam_id,
                    "exam_title": row.exam.title if row.exam else None,
                    "exam_code": row.exam_version.exam_code if row.exam_version else (row.exam.exam_code if row.exam else None),
                    "version_code": row.exam_version.version_code if row.exam_version else None,
                    "status": row.status,
                    "score_percent": row.score_percent,
                    "correct_count": row.correct_count,
                    "incorrect_count": row.incorrect_count,
                    "blank_count": row.blank_count,
                    "created_at": row.created_at,
                }
                for row in attempts
            ],
        }


@router.get("/attempts/{attempt_id}/export/pdf")
def export_student_attempt_pdf(
    attempt_id: int,
    email: str = Query(..., min_length=3, max_length=255),
    document_number: str = Query(..., min_length=3, max_length=32),
) -> Response:
    with SessionLocal() as db:
        student = _get_student_by_credentials(db, email, document_number)
        attempt = db.scalar(
            select(OmrAttempt)
            .where(OmrAttempt.id == attempt_id, OmrAttempt.student_id == student.id)
        )
        if attempt is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="attempt not found")
        _ = attempt.answers  # force relationship load
        overlay_payload = _build_overlay_payload(attempt)
        pdf_bytes = _render_attempt_pdf(attempt, overlay_payload)
        filename = f"resultado_{student.document_number}_{attempt.id}.pdf"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
