from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.db.models import OmrAttempt, OmrAttemptAnswer


def _derive_attempt_status(grading_block: dict | None, manual_review_required: bool) -> str:
    if grading_block is None:
        return 'read_only'

    grading_status = str(grading_block.get('status', 'read_only'))
    if grading_status == 'resolution_error':
        return 'resolution_error'
    if manual_review_required:
        return 'needs_review'
    return 'graded'


def _build_answers_for_read_only(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for question in questions:
        marked_options = question.get('marked_options', [])
        status = 'blank'
        marked_answer = None
        if len(marked_options) == 1:
            marked_answer = str(marked_options[0])
            status = 'detected'
        elif len(marked_options) > 1:
            status = 'ambiguous'
        rows.append(
            {
                'question_number': int(question.get('question_number', 0)),
                'item_id': None,
                'correct_answer': None,
                'marked_answer': marked_answer,
                'status': status,
                'marked_options': marked_options,
            }
        )
    return rows


def persist_omr_attempt(
    db: Session,
    result_payload: dict[str, Any],
    teacher_id: int | None,
    exam_id: int | None,
    exam_version_id: int | None,
    student_id: int | None,
    exam_code_detected: str | None,
    grading_block: dict | None,
) -> OmrAttempt:
    diagnostics = result_payload.get('diagnostics', {}) if isinstance(result_payload, dict) else {}
    manual_review_required = bool(diagnostics.get('manual_review_required', False))
    attempt_status = _derive_attempt_status(grading_block=grading_block, manual_review_required=manual_review_required)

    summary = {}
    details = []
    if grading_block and grading_block.get('status') == 'graded':
        summary = grading_block.get('summary', {})
        details = grading_block.get('details', [])
    else:
        details = _build_answers_for_read_only(result_payload.get('questions', []))
        summary = {
            'total_questions': len(details),
            'correct': 0,
            'incorrect': 0,
            'blank': sum(1 for row in details if row.get('status') == 'blank'),
            'ambiguous': sum(1 for row in details if row.get('status') == 'ambiguous'),
            'score_percent': None,
        }

    attempt = OmrAttempt(
        teacher_id=teacher_id,
        exam_id=exam_id,
        exam_version_id=exam_version_id,
        student_id=student_id,
        exam_code_detected=exam_code_detected,
        status=attempt_status,
        score_percent=summary.get('score_percent'),
        total_questions=int(summary.get('total_questions', 0) or 0),
        correct_count=int(summary.get('correct', 0) or 0),
        incorrect_count=int(summary.get('incorrect', 0) or 0),
        blank_count=int(summary.get('blank', 0) or 0),
        ambiguous_count=int(summary.get('ambiguous', 0) or 0),
        manual_review_required=manual_review_required,
        uploaded_image_path=diagnostics.get('uploaded_image_path'),
        trace_json_path=diagnostics.get('trace_json_path'),
        ratios_csv_path=diagnostics.get('ratios_csv_path'),
        auxiliary_ratios_csv_path=diagnostics.get('auxiliary_ratios_csv_path'),
    )
    db.add(attempt)
    db.flush()

    for row in details:
        answer = OmrAttemptAnswer(
            attempt_id=attempt.id,
            question_number=int(row.get('question_number', 0)),
            item_id=row.get('item_id'),
            correct_answer=row.get('correct_answer'),
            marked_answer=row.get('marked_answer'),
            status=str(row.get('status', 'blank')),
            marked_options_json=row.get('marked_options', []),
        )
        db.add(answer)

    db.commit()
    db.refresh(attempt)
    return attempt
