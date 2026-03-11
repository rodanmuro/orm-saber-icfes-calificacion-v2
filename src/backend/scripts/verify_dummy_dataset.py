from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import engine


EXPECTED = {
    "teacher_email": "docente.dummy40@omr.local",
    "exam_code": "1234",
    "questions": 40,
    "version_code": "V001",
}


def main() -> int:
    print(f"[dummy-check] DATABASE_URL={settings.database_url}")
    try:
        with engine.connect() as conn:
            teacher_count = conn.execute(
                text("SELECT COUNT(*) FROM teacher WHERE email = :email"),
                {"email": EXPECTED["teacher_email"]},
            ).scalar_one()

            exam_count = conn.execute(
                text("SELECT COUNT(*) FROM exam WHERE exam_code = :code"),
                {"code": EXPECTED["exam_code"]},
            ).scalar_one()

            q_count = conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM exam_item ei
                    JOIN exam e ON e.id = ei.exam_id
                    WHERE e.exam_code = :code
                    """
                ),
                {"code": EXPECTED["exam_code"]},
            ).scalar_one()

            v_count = conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM exam_version ev
                    JOIN exam e ON e.id = ev.exam_id
                    WHERE e.exam_code = :code AND ev.version_code = :version
                    """
                ),
                {"code": EXPECTED["exam_code"], "version": EXPECTED["version_code"]},
            ).scalar_one()

            vv_count = conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM exam_version_item evi
                    JOIN exam_version ev ON ev.id = evi.exam_version_id
                    JOIN exam e ON e.id = ev.exam_id
                    WHERE e.exam_code = :code AND ev.version_code = :version
                    """
                ),
                {"code": EXPECTED["exam_code"], "version": EXPECTED["version_code"]},
            ).scalar_one()

    except SQLAlchemyError as exc:
        print(f"[dummy-check] ERROR: {exc}")
        return 1

    errors: list[str] = []
    if teacher_count < 1:
        errors.append("No existe docente dummy")
    if exam_count < 1:
        errors.append("No existe examen dummy")
    if q_count != EXPECTED["questions"]:
        errors.append(f"Cantidad de preguntas invalida: {q_count} != {EXPECTED['questions']}")
    if v_count != 1:
        errors.append(f"Version esperada no valida: {v_count}")
    if vv_count != EXPECTED["questions"]:
        errors.append(f"Cantidad en exam_version_item invalida: {vv_count}")

    if errors:
        print("[dummy-check] FAIL")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("[dummy-check] OK - dataset dummy validado")
    print(
        f"[dummy-check] teacher={teacher_count} exam={exam_count} exam_item={q_count} "
        f"version={v_count} version_item={vv_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
