from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import engine

EXPECTED_TABLES = {
    "teacher",
    "student",
    "standard",
    "competency",
    "item",
    "exam",
    "exam_item",
    "exam_version",
    "exam_version_item",
    "omr_attempt",
    "omr_attempt_answer",
}

EXPECTED_UNIQUE_CONSTRAINTS = {
    "student": {"uq_student_document"},
    "competency": {"uq_competency_standard_code"},
    "exam": {"uq_exam_teacher_code"},
    "exam_item": {"uq_exam_item_pair", "uq_exam_item_order"},
    "exam_version": {"uq_exam_version_code"},
    "exam_version_item": {"uq_exam_version_item_qnum", "uq_exam_version_item_source"},
}


def _validate_tables(inspector) -> list[str]:
    errors: list[str] = []
    tables = set(inspector.get_table_names())

    missing = EXPECTED_TABLES - tables
    if missing:
        errors.append(f"Tablas faltantes: {sorted(missing)}")

    return errors


def _validate_unique_constraints(inspector) -> list[str]:
    errors: list[str] = []

    for table, expected_names in EXPECTED_UNIQUE_CONSTRAINTS.items():
        uniques = inspector.get_unique_constraints(table)
        found_names = {u.get("name") for u in uniques if u.get("name")}
        missing = expected_names - found_names
        if missing:
            errors.append(
                f"Unique constraints faltantes en {table}: {sorted(missing)}"
            )

    return errors


def _validate_foreign_keys(inspector) -> list[str]:
    errors: list[str] = []
    tables_without_expected_fk = {"teacher", "student", "standard"}

    for table in EXPECTED_TABLES:
        if table in tables_without_expected_fk:
            continue
        fks = inspector.get_foreign_keys(table)
        if len(fks) == 0:
            errors.append(f"La tabla {table} no tiene foreign keys y se esperaba al menos una")

    return errors


def _validate_basic_queries() -> list[str]:
    errors: list[str] = []
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.execute(text("SELECT COUNT(*) FROM teacher"))
            conn.execute(text("SELECT COUNT(*) FROM exam"))
            conn.execute(text("SELECT COUNT(*) FROM item"))
    except SQLAlchemyError as exc:
        errors.append(f"Error ejecutando consultas basicas: {exc}")

    return errors


def main() -> int:
    print(f"[schema-check] DATABASE_URL={settings.database_url}")

    try:
        inspector = inspect(engine)
    except SQLAlchemyError as exc:
        print(f"[schema-check] ERROR: no fue posible inspeccionar la DB: {exc}")
        return 1

    errors: list[str] = []
    errors.extend(_validate_tables(inspector))
    errors.extend(_validate_unique_constraints(inspector))
    errors.extend(_validate_foreign_keys(inspector))
    errors.extend(_validate_basic_queries())

    if errors:
        print("[schema-check] FAIL")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("[schema-check] OK - esquema y constraints basicos validados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
